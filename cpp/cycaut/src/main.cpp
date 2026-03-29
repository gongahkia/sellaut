#include "util.hpp"

#include <array>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using Grid = std::vector<std::string>;

Grid parse_grid(const common::fs::path& path) {
    Grid grid = common::read_lines(path);
    common::require_rectangular(grid, "Cyclic automaton input");

    for (const std::string& row : grid) {
        for (char cell : row) {
            if (cell < '0' || cell > '5') {
                throw std::runtime_error("Cyclic automaton input accepts only digits 0 through 5.");
            }
        }
    }

    return grid;
}

Grid advance(const Grid& grid) {
    Grid next = grid;
    const int row_count = static_cast<int>(grid.size());
    const int column_count = static_cast<int>(grid.front().size());

    for (int row = 0; row < row_count; ++row) {
        for (int column = 0; column < column_count; ++column) {
            const int state = grid[static_cast<std::size_t>(row)][static_cast<std::size_t>(column)] - '0';
            const int target = (state + 1) % 6;

            int matching_neighbors = 0;
            for (int delta_row = -1; delta_row <= 1; ++delta_row) {
                for (int delta_column = -1; delta_column <= 1; ++delta_column) {
                    if (delta_row == 0 && delta_column == 0) {
                        continue;
                    }

                    const int neighbor_row = (row + delta_row + row_count) % row_count;
                    const int neighbor_column = (column + delta_column + column_count) % column_count;
                    if (grid[static_cast<std::size_t>(neighbor_row)][static_cast<std::size_t>(neighbor_column)] - '0' == target) {
                        ++matching_neighbors;
                    }
                }
            }

            if (matching_neighbors >= 2) {
                next[static_cast<std::size_t>(row)][static_cast<std::size_t>(column)] =
                    static_cast<char>('0' + target);
            }
        }
    }

    return next;
}

std::string colored_cell(char cell) {
    static const std::array<std::string, 6> colors = {"37", "91", "93", "92", "96", "95"};
    return common::colorize(std::string(1, cell), colors[static_cast<std::size_t>(cell - '0')]);
}

void render(const Grid& grid, int current_step, int total_steps, const std::string& source_name) {
    std::cout << common::colorize("Cyclic Cellular Automaton", 95) << " | step " << current_step
              << "/" << total_steps << " | " << source_name << "\n";
    std::cout << "each state advances when at least 2 neighbors are already its successor\n\n";

    for (const std::string& row : grid) {
        for (char cell : row) {
            std::cout << colored_cell(cell);
        }
        std::cout << "\n";
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const common::Options options = common::parse_options(argc, argv, false);
        const common::fs::path input_path = common::resolve_input_path(options.input, "src", "Pick a cyclic automaton sample file.");
        Grid grid = parse_grid(input_path);

        const int steps = options.steps ? *options.steps : common::prompt_int("Steps", 80, 0, 5000);
        const int delay_ms = options.delay_ms ? *options.delay_ms : common::prompt_int("Delay in milliseconds", 50, 0, 5000);

        common::CursorGuard cursor_guard;
        for (int step = 0; step <= steps; ++step) {
            common::clear_screen();
            render(grid, step, steps, input_path.filename().string());
            std::cout.flush();

            if (step == steps) {
                break;
            }

            common::sleep_ms(delay_ms);
            grid = advance(grid);
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << common::colorize("Error: ", 31) << error.what() << "\n";
        return 1;
    }
}
