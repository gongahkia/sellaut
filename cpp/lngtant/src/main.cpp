#include "util.hpp"

#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

enum class Direction {
    Up = 0,
    Right = 1,
    Down = 2,
    Left = 3,
};

struct Ant {
    int row = 0;
    int column = 0;
    Direction direction = Direction::Up;
};

struct World {
    std::vector<std::string> cells;
    Ant ant;
};

Direction direction_from_char(char value) {
    switch (value) {
        case '^':
            return Direction::Up;
        case '>':
            return Direction::Right;
        case 'v':
            return Direction::Down;
        case '<':
            return Direction::Left;
        default:
            throw std::runtime_error("Unexpected ant direction.");
    }
}

char direction_to_char(Direction direction) {
    switch (direction) {
        case Direction::Up:
            return '^';
        case Direction::Right:
            return '>';
        case Direction::Down:
            return 'v';
        case Direction::Left:
            return '<';
    }
    return '^';
}

Direction turn_right(Direction direction) {
    return static_cast<Direction>((static_cast<int>(direction) + 1) % 4);
}

Direction turn_left(Direction direction) {
    return static_cast<Direction>((static_cast<int>(direction) + 3) % 4);
}

World parse_world(const common::fs::path& path) {
    World world;
    world.cells = common::read_lines(path);
    common::require_rectangular(world.cells, "Langton input");

    bool found_ant = false;
    for (std::size_t row = 0; row < world.cells.size(); ++row) {
        for (std::size_t column = 0; column < world.cells[row].size(); ++column) {
            const char cell = world.cells[row][column];
            if (cell == '.' || cell == '#') {
                continue;
            }

            if (cell == '^' || cell == '>' || cell == 'v' || cell == '<') {
                if (found_ant) {
                    throw std::runtime_error("Langton input must contain exactly one ant.");
                }
                found_ant = true;
                world.ant = {
                    static_cast<int>(row),
                    static_cast<int>(column),
                    direction_from_char(cell),
                };
                world.cells[row][column] = '.';
                continue;
            }

            throw std::runtime_error("Langton input contains an unsupported character.");
        }
    }

    if (!found_ant) {
        throw std::runtime_error("Langton input must contain exactly one ant.");
    }

    return world;
}

void advance(World& world) {
    char& current_cell = world.cells[static_cast<std::size_t>(world.ant.row)][static_cast<std::size_t>(world.ant.column)];
    if (current_cell == '.') {
        world.ant.direction = turn_right(world.ant.direction);
        current_cell = '#';
    } else {
        world.ant.direction = turn_left(world.ant.direction);
        current_cell = '.';
    }

    const int row_count = static_cast<int>(world.cells.size());
    const int column_count = static_cast<int>(world.cells.front().size());

    switch (world.ant.direction) {
        case Direction::Up:
            world.ant.row = (world.ant.row - 1 + row_count) % row_count;
            break;
        case Direction::Right:
            world.ant.column = (world.ant.column + 1) % column_count;
            break;
        case Direction::Down:
            world.ant.row = (world.ant.row + 1) % row_count;
            break;
        case Direction::Left:
            world.ant.column = (world.ant.column - 1 + column_count) % column_count;
            break;
    }
}

void render(const World& world, int current_step, int total_steps, const std::string& source_name) {
    std::cout << common::colorize("Langton's Ant", 96) << " | step " << current_step << "/" << total_steps
              << " | " << source_name << "\n";
    std::cout << "white turns right, black turns left, toroidal wrap\n\n";

    for (std::size_t row = 0; row < world.cells.size(); ++row) {
        for (std::size_t column = 0; column < world.cells[row].size(); ++column) {
            if (world.ant.row == static_cast<int>(row) && world.ant.column == static_cast<int>(column)) {
                std::cout << common::colorize(std::string(1, direction_to_char(world.ant.direction)), 96);
            } else if (world.cells[row][column] == '#') {
                std::cout << common::colorize("#", 33);
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
        const common::Options options = common::parse_options(argc, argv, false);
        const common::fs::path input_path = common::resolve_input_path(options.input, "src", "Pick a Langton sample file.");

        World world = parse_world(input_path);
        const int steps = options.steps ? *options.steps : common::prompt_int("Steps", 80, 0, 5000);
        const int delay_ms = options.delay_ms ? *options.delay_ms : common::prompt_int("Delay in milliseconds", 60, 0, 5000);

        common::CursorGuard cursor_guard;
        for (int step = 0; step <= steps; ++step) {
            common::clear_screen();
            render(world, step, steps, input_path.filename().string());
            std::cout.flush();

            if (step == steps) {
                break;
            }

            common::sleep_ms(delay_ms);
            advance(world);
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << common::colorize("Error: ", 31) << error.what() << "\n";
        return 1;
    }
}
