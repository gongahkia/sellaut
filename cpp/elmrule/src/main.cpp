#include "util.hpp"

#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

std::string parse_seed(const common::fs::path& path) {
    const std::vector<std::string> lines = common::read_lines(path);
    if (lines.size() != 1) {
        throw std::runtime_error("Elementary rule input must contain exactly one seed row.");
    }

    for (char value : lines.front()) {
        if (value != '.' && value != '#') {
            throw std::runtime_error("Elementary rule input accepts only '.' and '#'.");
        }
    }

    return lines.front();
}

int prompt_rule() {
    while (true) {
        std::cout << "Rule [30, 90, 110, or 0-255] [30]: ";
        std::string raw_input;
        std::getline(std::cin, raw_input);
        raw_input = common::trim_copy(raw_input);

        if (raw_input.empty()) {
            return 30;
        }

        try {
            const int rule = common::parse_int(raw_input);
            if (rule >= 0 && rule <= 255) {
                return rule;
            }
        } catch (const std::exception&) {
        }

        std::cout << "Expected a rule number between 0 and 255.\n";
    }
}

std::string next_row(const std::string& current, int rule) {
    std::string next = current;
    for (std::size_t index = 0; index < current.size(); ++index) {
        const bool left = (index > 0 && current[index - 1] == '#');
        const bool center = (current[index] == '#');
        const bool right = (index + 1 < current.size() && current[index + 1] == '#');
        const int pattern = (static_cast<int>(left) << 2) | (static_cast<int>(center) << 1) | static_cast<int>(right);
        next[index] = ((rule >> pattern) & 1) == 1 ? '#' : '.';
    }
    return next;
}

void render(const std::vector<std::string>& history, int rule, int current_step, int total_steps, const std::string& source_name) {
    std::cout << common::colorize("Elementary Cellular Automata", 92) << " | rule " << rule
              << " | step " << current_step << "/" << total_steps << " | " << source_name << "\n";
    std::cout << "rows grow downward from a single seed\n\n";

    for (const std::string& row : history) {
        for (char cell : row) {
            if (cell == '#') {
                std::cout << common::colorize("#", 92);
            } else {
                std::cout << common::colorize(".", 37);
            }
        }
        std::cout << "\n";
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const common::Options options = common::parse_options(argc, argv, true);
        const common::fs::path input_path = common::resolve_input_path(options.input, "src", "Pick an elementary rule seed file.");
        const std::string seed = parse_seed(input_path);

        const int rule = options.rule ? *options.rule : prompt_rule();
        if (rule < 0 || rule > 255) {
            throw std::runtime_error("Rule must be between 0 and 255.");
        }

        const int steps = options.steps ? *options.steps : common::prompt_int("Rows to generate", 32, 0, 5000);
        const int delay_ms = options.delay_ms ? *options.delay_ms : common::prompt_int("Delay in milliseconds", 40, 0, 5000);

        std::vector<std::string> history;
        history.push_back(seed);

        common::CursorGuard cursor_guard;
        for (int step = 0; step <= steps; ++step) {
            common::clear_screen();
            render(history, rule, step, steps, input_path.filename().string());
            std::cout.flush();

            if (step == steps) {
                break;
            }

            common::sleep_ms(delay_ms);
            history.push_back(next_row(history.back(), rule));
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << common::colorize("Error: ", 31) << error.what() << "\n";
        return 1;
    }
}
