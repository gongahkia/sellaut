# mypy: ignore-errors
# silence mypy type errors

# imports
import curses
import os

# basic info
# - screen size: (0,0) to (60,25), a 61 by 26 grid

cell_data:dict = {
                    "state": "off",
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
            count += 1
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
                                "state": "off",
                                "coordinate": (0,0)
                            }
            match buffer[y][x]:
                case ".": # off state; ready
                    cell_data["state"] = "off"
                    cell_data["coordinate"] = (x,y)
                case "#": # on state; firing
                    cell_data["state"] = "on"
                    cell_data["coordinate"] = (x,y)
                case "*": # dying state; refractory
                    cell_data["state"] = "dying"
                    cell_data["coordinate"] = (x,y)
                case _: # edge case 
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
def render(coord:[dict]) -> None:

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

        while check_changes(coord):

            screen.erase()

            for cell in coord:

                x_coord:int = cell["coordinate"][0]
                y_coord:int = cell["coordinate"][1]
                ascii_char:str = ""

                match cell["state"]:
                    case "off":
                        ascii_char = "."
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(7))
                    case "on":
                        ascii_char = "#"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(3))
                    case "dying":
                        ascii_char = "*"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(1))
                    case _: 
                        os.system("clear")
                        print("Edge case 001 found.")
                        return None

            coord:[dict] = engine(coord)

            screen.refresh() 
            curses.napms(50) 

    curses.endwin() 

# runs every update loop
def engine(coord:[dict]) -> [dict]:

    coord_dict = re_list_dict(coord)
    final_coord_dict:{(int):str} = {}

    for pair in coord_dict:
        x_coord:int = pair[0]
        y_coord:int = pair[1]

        match coord_dict[(x_coord,y_coord)]:

            case "off": 
                num_on:int = moore_neighborhood_count(coord,x_coord,y_coord)["on"]
                if (x_coord,y_coord) not in final_coord_dict:
                    if num_on == 2:
                        final_coord_dict[(x_coord,y_coord)] = "on"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "off"

            case "on": 
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "dying"

            case "dying": 
                if (x_coord,y_coord) not in final_coord_dict:
                    final_coord_dict[(x_coord,y_coord)] = "off"

            case _: 
                os.system("clear")
                print("Edge case 002 found.")
                return None

    return re_dict_list(final_coord_dict)

# restructures coord to coord_dict
def re_list_dict(coord:[dict]) -> {(int):str}:
    coord_dict:dict = {}
    for cell in coord:
        coord_dict[tuple(cell["coordinate"])] = coord_dict.get(tuple(cell["coordinate"]), "") + cell["state"]
    return coord_dict

# restructures coord_dict to coord
def re_dict_list(coord_dict:{(int):str}) -> [dict]:
    coord:list = []
    for pair in coord_dict:
        coordinate:(int) = pair
        state:str = coord_dict[coordinate]
        cell_data:dict = {
                    "state": state,
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

# checks whether a given coordinate is within the bounds of (0,0) and (60,25)
def check_bounds(coordinate:(int)) -> bool:
    x_coord:int = coordinate[0]
    y_coord:int = coordinate[1]
    if x_coord >= 0 and x_coord <= 60 and y_coord >= 0 and y_coord <= 25:
        return True
    else:
        return False

# moore neighbourhoods count all 8 surrounding cells
def moore_neighborhood_count(coord,x_coord,y_coord) -> {str:int}:
    coord_dict:{(int):str} = re_list_dict(coord)
    count:dict = {}
    count:dict = {
        "off":0,
        "on":0,
        "dying":0
    }

    if check_bounds((x_coord - 1, y_coord - 1)):
        count[coord_dict[(x_coord - 1, y_coord - 1)]] = count.get(coord_dict[(x_coord - 1, y_coord - 1)],0) + 1

    if check_bounds((x_coord, y_coord - 1)):
        count[coord_dict[(x_coord, y_coord - 1)]] = count.get(coord_dict[(x_coord, y_coord - 1)],0) + 1

    if check_bounds((x_coord + 1, y_coord - 1)):
        count[coord_dict[(x_coord + 1, y_coord - 1)]] = count.get(coord_dict[(x_coord + 1, y_coord - 1)],0) + 1

    if check_bounds((x_coord - 1, y_coord)):
        count[coord_dict[(x_coord - 1, y_coord)]] = count.get(coord_dict[(x_coord - 1, y_coord)],0) + 1

    if check_bounds((x_coord + 1, y_coord)):
        count[coord_dict[(x_coord + 1, y_coord)]] = count.get(coord_dict[(x_coord + 1, y_coord)],0) + 1

    if check_bounds((x_coord - 1, y_coord + 1)):
        count[coord_dict[(x_coord - 1, y_coord + 1)]] = count.get(coord_dict[(x_coord - 1, y_coord + 1)],0) + 1

    if check_bounds((x_coord, y_coord + 1)):
        count[coord_dict[(x_coord, y_coord + 1)]] = count.get(coord_dict[(x_coord, y_coord + 1)],0) + 1

    if check_bounds((x_coord + 1, y_coord + 1)):
        count[coord_dict[(x_coord + 1, y_coord + 1)]] = count.get(coord_dict[(x_coord + 1, y_coord + 1)],0) + 1

    return count

# event loop
render(parse_file())