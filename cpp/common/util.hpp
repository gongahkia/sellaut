#pragma once

#include <algorithm>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace common {

namespace fs = std::filesystem;

struct Options {
    std::optional<std::string> input;
    std::optional<int> steps;
    std::optional<int> delay_ms;
    std::optional<int> rule;
};

inline std::string trim_copy(std::string value) {
    auto is_space = [](unsigned char ch) {
        return std::isspace(ch) != 0;
    };

    value.erase(value.begin(), std::find_if(value.begin(), value.end(), [&](unsigned char ch) {
        return !is_space(ch);
    }));
    value.erase(std::find_if(value.rbegin(), value.rend(), [&](unsigned char ch) {
        return !is_space(ch);
    }).base(), value.end());
    return value;
}

inline int parse_int(const std::string& text) {
    std::size_t index = 0;
    const int value = std::stoi(text, &index);
    if (index != text.size()) {
        throw std::runtime_error("Expected an integer, received \"" + text + "\".");
    }
    return value;
}

inline Options parse_options(int argc, char** argv, bool allow_rule) {
    Options options;

    for (int index = 1; index < argc; ++index) {
        const std::string arg = argv[index];
        auto read_value = [&](const std::string& flag) -> std::string {
            if (index + 1 >= argc) {
                throw std::runtime_error("Missing value for " + flag + ".");
            }
            ++index;
            return argv[index];
        };

        if (arg == "--input") {
            options.input = read_value(arg);
        } else if (arg == "--steps") {
            options.steps = parse_int(read_value(arg));
        } else if (arg == "--delay") {
            options.delay_ms = parse_int(read_value(arg));
        } else if (arg == "--rule") {
            if (!allow_rule) {
                throw std::runtime_error("--rule is not supported by this example.");
            }
            options.rule = parse_int(read_value(arg));
        } else {
            throw std::runtime_error("Unknown option: " + arg);
        }
    }

    if (options.steps && *options.steps < 0) {
        throw std::runtime_error("Steps must be zero or greater.");
    }
    if (options.delay_ms && *options.delay_ms < 0) {
        throw std::runtime_error("Delay must be zero or greater.");
    }

    return options;
}

inline std::vector<fs::path> list_text_files(const fs::path& directory) {
    std::vector<fs::path> files;
    if (!fs::exists(directory)) {
        throw std::runtime_error("Directory not found: " + directory.string());
    }

    for (const auto& entry : fs::directory_iterator(directory)) {
        if (entry.is_regular_file() && entry.path().extension() == ".txt") {
            files.push_back(entry.path());
        }
    }

    std::sort(files.begin(), files.end(), [](const fs::path& lhs, const fs::path& rhs) {
        return lhs.filename().string() < rhs.filename().string();
    });

    if (files.empty()) {
        throw std::runtime_error("No .txt files found in " + directory.string() + ".");
    }

    return files;
}

inline fs::path prompt_file_choice(const std::vector<fs::path>& files, const std::string& prompt) {
    while (true) {
        std::cout << prompt << "\n\n";
        for (std::size_t index = 0; index < files.size(); ++index) {
            std::cout << "[" << index + 1 << "] " << files[index].filename().string() << "\n";
        }
        std::cout << "\nFile number [1]: ";

        std::string raw_input;
        std::getline(std::cin, raw_input);
        raw_input = trim_copy(raw_input);

        if (raw_input.empty()) {
            return files.front();
        }

        try {
            const int selection = parse_int(raw_input);
            if (selection >= 1 && static_cast<std::size_t>(selection) <= files.size()) {
                return files[static_cast<std::size_t>(selection - 1)];
            }
        } catch (const std::exception&) {
        }

        std::cout << "Invalid selection. Try again.\n\n";
    }
}

inline fs::path resolve_input_path(const std::optional<std::string>& input, const fs::path& directory, const std::string& prompt) {
    if (input) {
        return fs::path(*input);
    }
    return prompt_file_choice(list_text_files(directory), prompt);
}

inline std::vector<std::string> read_lines(const fs::path& path) {
    std::ifstream input(path);
    if (!input.is_open()) {
        throw std::runtime_error("Unable to open file: " + path.string());
    }

    std::vector<std::string> lines;
    std::string line;
    while (std::getline(input, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        lines.push_back(line);
    }

    if (lines.empty()) {
        throw std::runtime_error("Input file is empty: " + path.string());
    }

    return lines;
}

inline void require_rectangular(const std::vector<std::string>& lines, const std::string& label) {
    if (lines.empty() || lines.front().empty()) {
        throw std::runtime_error(label + " must not be empty.");
    }

    const std::size_t expected_width = lines.front().size();
    for (std::size_t row = 0; row < lines.size(); ++row) {
        if (lines[row].size() != expected_width) {
            throw std::runtime_error(label + " must be rectangular. Row " + std::to_string(row + 1) + " differs in length.");
        }
    }
}

inline int prompt_int(const std::string& label, int default_value, int minimum, int maximum) {
    while (true) {
        std::cout << label << " [" << default_value << "]: ";
        std::string raw_input;
        std::getline(std::cin, raw_input);
        raw_input = trim_copy(raw_input);

        if (raw_input.empty()) {
            return default_value;
        }

        try {
            const int value = parse_int(raw_input);
            if (value >= minimum && value <= maximum) {
                return value;
            }
        } catch (const std::exception&) {
        }

        std::cout << "Expected a number between " << minimum << " and " << maximum << ".\n";
    }
}

inline std::string colorize(const std::string& text, const std::string& code) {
    return "\033[" + code + "m" + text + "\033[0m";
}

inline std::string colorize(const std::string& text, int code) {
    return colorize(text, std::to_string(code));
}

inline void clear_screen() {
    std::cout << "\033[2J\033[H";
}

inline void sleep_ms(int delay_ms) {
    if (delay_ms > 0) {
        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
    }
}

class CursorGuard {
  public:
    CursorGuard() {
        std::cout << "\033[?25l";
        std::cout.flush();
    }

    ~CursorGuard() {
        std::cout << "\033[0m\033[?25h" << std::flush;
    }
};

}  // namespace common
