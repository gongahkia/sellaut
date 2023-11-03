# mypy: ignore-errors
# silence mypy type errors

# imports
import curses
import os

# basic info
# - screen size: [0,0] to [60,25], a 61 by 26 grid
# - implement interactions between elements
# - implement solid dynamics (gravity), liquid dynamics (gravity and liquid fluidity) and gas dynamics
# - functional programming
# - data structures
# - separate the file_ui function and other resuable functions to a lower file directory for other cellular automata projects in this repo

# cell state represented by a dictionary
cell_data:dict = {
                    "element": "air",
                    "coordinate": (0,0)
                }

# file selector ui
def file_ui() -> [str]:
    display:str = "Pick a valid number.\n"
    count:int = 1
    file_name_array:[str] = [file_name.split(".") for file_name in os.listdir() if os.path.isfile(file_name)]
    valid_file_name:[str] = []
    for file_name in file_name_array:
        if file_name[1] == "txt": # checks txt file
            display += f"[{count}] | {file_name[0]}.{file_name[1]}\n"
            valid_file_name.append(f"{file_name[0]}.{file_name[1]}")
    while True:
        print(display)
        user:str = input("File number: ")
        try:
            if int(user) - 1 > 1 or int(user) - 1 < len(file_name_array):
                break
        except:
            continue
    # print(valid_file_name)
    fhand = open(f"{valid_file_name[int(user) - 1]}", "r")
    buffer:list = []
    for line in fhand:
        if len(line.rstrip()) != 61:
            return None
        # print(line, end="")
        buffer.append(line.rstrip())
    fhand.close()
    if len(buffer) != 26:
        return None
    return buffer

# parse text files 
def parse_file() -> [dict]:
    buffer:[str] = file_ui()
    if not buffer:
        os.system("clear")
        print("Incorrect number of rows and columns. Please input a 61 by 26 grid.")
        return None
    coord:[dict] = []
    for y in range(len(buffer)):
        for x in range(len(buffer[y])):
            cell_data:dict = {
                                "element": "",
                                "coordinate": (0,0)
                            }
            match buffer[y][x]:
                case ".": # air block
                    cell_data["element"] = "air_block"
                    cell_data["coordinate"] = (x,y)
                case "$": # flammable block --> set on fire by fire, dissapears upon combustion leaving soot, doused by water, affected by solid dynamics
                    cell_data["element"] = "flammable_block"
                    cell_data["coordinate"] = (x,y)
                case "*": # oil block --> surface set on fire by water, top layer evaporates and produces effervesence, doused by water, affected by liquid dynamics
                    cell_data["element"] = "oil_block"
                    cell_data["coordinate"] = (x,y)
                case "^": # fire block --> doused by water
                    cell_data["element"] = "fire_block"
                    cell_data["coordinate"] = (x,y)
                case "~": # water block --> affected by liquid dynamics, puts out fire at no cost to itself
                    cell_data["element"] = "water_block"
                    cell_data["coordinate"] = (x,y)
                case "#": # non-flammable block --> not affected by solid dynamics, inert
                    cell_data["element"] = "non-flammable_block"
                    cell_data["coordinate"] = (x,y)
                case "_": # soot block --> affected by solid dynamics
                    cell_data["element"] = "soot_block"
                    cell_data["coordinate"] = (x,y)
                case "%": # effervesence block --> affected by gas dynamics
                    cell_data["element"] = "effervesence_block"
                    cell_data["coordinate"] = (x,y)
                case _: # edge case --> this shouldn't exist
                    os.system("clear")
                    print(f"Unknown character found in line {y + 1} --> [{buffer[y][x]}]")
                    return None
            coord.append(cell_data)
            # debug(coord)
    return coord

# prints debug information
def debug(coord:[dict]) -> None:
    fhand = open(".sellaut-log","w")
    final:str = ""
    for cell_info in coord:
        final += f"{str(cell_info)}\n"
    fhand.write(final)
    fhand.close()

# incorporates curses module
# FUA --> debug why the screen is not showing the changed code in line 173 but instead skips to final iteration, it has something to do with the logic in 184, probably need to make a shallow copy of coord dict and run based off that
def render(coord:[dict]) -> None:

    # curses boilerplate
    screen = curses.initscr()
    curses.cbreak()
    curses.noecho()
    screen.timeout(0)
    curses.curs_set(0)

    if curses.has_colors():
        curses.start_color()
        
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # add check_changes(coord) function here?
        while check_changes(coord):

            screen.erase()

            # add engine function / update_dictionary function here (core part of game engine)
            coord:[dict] = engine(coord)

            for cell in coord:

                x_coord:int = cell["coordinate"][0]
                y_coord:int = cell["coordinate"][1]
                ascii_char:str = ""

                match cell["element"]:
                    case "air_block":
                        ascii_char = "."
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(7))
                    case "flammable_block": 
                        ascii_char = "$"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(2))
                    case "oil_block": 
                        ascii_char = "*"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(4))
                    case "fire_block": 
                        ascii_char = "^"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(1))
                    case "water_block": 
                        ascii_char = "≈"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(6))
                    case "non-flammable_block": 
                        ascii_char = "#"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(3))
                    case "soot_block": 
                        ascii_char = "_"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(5))
                    case "effervesence_block": 
                        ascii_char = "%"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(7))
                    case _: 
                        os.system("clear")
                        print(f"Edge case 001 found.")
                        return None

            # screen.erase() # erases the screen before new cells can be drawn
            screen.refresh() # refreshes the screen once all cells have been added
            curses.napms(2000) # waits few seconds without input

    curses.endwin() # exits curses window

# runs every update loop
# FUA --> implement the 3 engines for different types of objects, solid liquid and gaseous; maybe abstract into different functions?
#     --> implement the checks necessary after I've written the function to restructure data
def engine(coord:[dict]) -> [dict]:

    coord_dict = re_list_dict(coord)
    final_coord_dict:{(int):str} = {}
    # print(coord_dict)

    for pair in coord_dict:
        x_coord:int = pair[0]
        y_coord:int = pair[1]

    # structure of engine change 
        # 1. Effect to be implemented
        # 2. Calculate estimated change in block position
        # 3. New position of existing block
        # 4. New element at existing position
        # * Caveat --> x min;0 max;60
        #          --> y min;0 max;25
        # 5. Need to consider if block already in dictionary, don't alter it

        match coord_dict[(x_coord,y_coord)]:

            case "air_block": # do nothing
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "air_block"
                else:
                    pass

            case "flammable_block": # FUA --> implement further collisions between this and OTHER objects

                if (x_coord,y_coord) not in final_coord_dict:
                    # 1. GRAVITY
                    if y_coord + 1 <= 25: 
                        # 2. Calculate estimated change in block position
                        # 3. New position of existing block
                        final_coord_dict[(x_coord,y_coord+1)] = "flammable_block"
                        # 4. New element at existing position
                        final_coord_dict[(x_coord,y_coord)] = "air_block"

            case "oil_block": # FUA --> implement logic
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "oil_block"

            case "fire_block": # FUA --> implement logic
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "fire_block"

            case "water_block": # FUA --> implement logic
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "water_block"

            case "non-flammable_block": # FUA --> implement logic
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "non-flammable_block"

            case "soot_block": # FUA --> implement logic
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "soot_block"

            case "effervesence_block": # FUA --> implement logic
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "effervesence_block"

            case _: 
                os.system("clear")
                print(f"Edge case 002 found.")
                return None

    return re_dict_list(final_coord_dict)

# restructures coord to coord_dict
def re_list_dict(coord:[dict]) -> {(int):str}:
    coord_dict:dict = {}
    # print(coord)
    for cell in coord:
        # print(tuple(cell["coordinate"]))
        coord_dict[tuple(cell["coordinate"])] = coord_dict.get(tuple(cell["coordinate"]), "") + cell["element"]
    return coord_dict

# restructures coord_dict to coord
def re_dict_list(coord_dict:{(int):str}) -> [dict]:
    coord:list = []
    for pair in coord_dict:
        coordinate:(int) = pair
        element:str = coord_dict[coordinate]
        cell_data:dict = {
                    "element": element,
                    "coordinate": coordinate
        }
        coord.append(cell_data)
    return coord

# runs every update loop
def check_changes(coord:[dict]) -> bool:
    initial_coord:[dict] = coord.copy()
    subsequent_coord:[dict] = engine(initial_coord)
    if initial_coord == subsequent_coord:
        return False
    else:
        return True

# event loop
render(parse_file())
# print(check_changes(re_dict_list(re_list_dict(parse_file()))))