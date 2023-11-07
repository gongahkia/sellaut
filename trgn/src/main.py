# mypy: ignore-errors
# silence mypy type errors

# imports
import curses
import os
import random

# basic info
# - screen size: (0,0) to (60,25), a 61 by 26 grid
# - implement randomised block generator
# - implement rules as in the README.md

cell_data:dict = {
                    "state": "water",
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
                                "state": "water",
                                "coordinate": (0,0)
                            }
            match buffer[y][x]:
                case "~": # water state
                    cell_data["state"] = "water"
                    cell_data["coordinate"] = (x,y)
                case "#": # sand state
                    cell_data["state"] = "sand"
                    cell_data["coordinate"] = (x,y)
                case ".": # land state
                    cell_data["state"] = "land"
                    cell_data["coordinate"] = (x,y)
                case "o": # stone state
                    cell_data["state"] = "stone"
                    cell_data["coordinate"] = (x,y)
                case "&": # village state
                    cell_data["state"] = "village"
                    cell_data["coordinate"] = (x,y)
                case "%": # tree state
                    cell_data["state"] = "tree"
                    cell_data["coordinate"] = (x,y)
                case "^": # fire state
                    cell_data["state"] = "fire"
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
                    case "water":
                        ascii_char = "≈"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(4))
                    case "sand":
                        ascii_char = "#"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(3))
                    case "land":
                        ascii_char = "."
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(7))
                    case "stone":
                        ascii_char = "o"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(7))
                    case "village":
                        ascii_char = "&"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(5))
                    case "tree":
                        ascii_char = "%"
                        screen.addstr(y_coord, x_coord, ascii_char, curses.color_pair(2))
                    case "fire":
                        ascii_char = "^"
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

            case "water": 
                if (x_coord,y_coord) not in final_coord_dict:
                    
                    num_land_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["land"]
                    num_water_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["water"]
                    num_sand_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["sand"]

                    if num_water_emn >= 1 and num_land_mn == 9:
                        final_coord_dict[(x_coord,y_coord)] = "land"
                    elif num_sand_emn >= 5 and num_water_emn >= 1:
                        final_coord_dict[(x_coord,y_coord)] = "sand"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "water"
            
            case "sand": 
                if (x_coord,y_coord) not in final_coord_dict:

                    num_water_vnn:int = von_neumann_neighbourhood_count(coord,x_coord,y_coord)["water"]
                    num_land_vnn:int = von_neumann_neighbourhood_count(coord,x_coord,y_coord)["land"]
                    num_sand_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["sand"]
                    num_water_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["water"]
                    num_land_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["land"]

                    if num_water_vnn >= 3 or num_water_mn >= 5:
                        final_coord_dict[(x_coord,y_coord)] = "water"
                    elif num_water_vnn >= 2 and num_sand_mn >= 2:
                        final_coord_dict[(x_coord,y_coord)] = "water"
                    elif num_land_vnn >= 3 or num_land_emn >= 14:
                        final_coord_dict[(x_coord,y_coord)] = "land"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "sand"

            case "land": 
                if (x_coord,y_coord) not in final_coord_dict:
                    
                    # these weights can be edited
                    probability_z:bool = probability_gen(0.25)
                    probability_c:bool = probability_gen(0.35)
                    probability_b:bool = probability_gen(0.45)
                    probability_i:bool = probability_gen(0.05)
                    probability_h:bool = probability_gen(0.04)
                    probability_f:bool = probability_gen(0.01)
                    probability_g:bool = probability_gen(0.02)
                    probability_a:bool = probability_gen(0.03)
                    
                    num_land_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["land"]
                    num_stone_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["stone"]
                    num_tree_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["tree"]
                    num_sand_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["sand"]
                    num_water_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["water"]
                    num_village_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["village"]
                    num_stone_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["stone"]
                    num_land_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["land"]
                    num_water_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["water"]
                    
                    if num_land_emn >= 20 and num_stone_emn >= 1 and probability_i:
                        final_coord_dict[(x_coord,y_coord)] = "village"
                    elif num_village_mn >= 1 and probability_h:
                        final_coord_dict[(x_coord,y_coord)] = "village"
                    elif num_water_emn == 0 and probability_f:
                        final_coord_dict[(x_coord,y_coord)] = "stone"
                    elif num_water_emn == 1 and num_stone_mn == 0 and probability_g:
                        final_coord_dict[(x_coord,y_coord)] = "tree"
                    elif num_land_mn == 8 and num_tree_emn >= 1 and probability_a:
                        final_coord_dict[(x_coord,y_coord)] = "tree"
                    elif num_sand_emn >= 7:
                        final_coord_dict[(x_coord,y_coord)] = "sand"
                    elif num_water_mn >= 3 and probability_z:
                        final_coord_dict[(x_coord,y_coord)] = "sand"
                    elif num_land_emn >= 6 and num_tree_emn >= 3 and probability_b:
                        final_coord_dict[(x_coord,y_coord)] = "water"
                    elif num_water_mn == 1 and num_tree_emn >= 1 and probability_c:
                        final_coord_dict[(x_coord,y_coord)] = "water"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "land"

            case "stone": 
                if (x_coord,y_coord) not in final_coord_dict:
                    
                    probability_p:bool = probability_gen(0.9)
                    probability_e:bool = probability_gen(0.10)
                    
                    num_sand_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["sand"]
                    
                    if probability_p:
                        final_coord_dict[(x_coord,y_coord)] = "land"
                    elif num_sand_emn >= 7 and probability_e:
                        final_coord_dict[(x_coord,y_coord)] = "sand"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "stone"

            case "village": 
                if (x_coord,y_coord) not in final_coord_dict:

                    num_village_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["village"]
                    num_tree_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["tree"]

                    if num_village_emn >= 1 and num_tree_emn == 0:
                        final_coord_dict[(x_coord,y_coord)] = "fire"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "village"

            case "tree": 
                if (x_coord,y_coord) not in final_coord_dict:
                    
                    probability_s:bool = probability_gen(0.20)

                    num_fire_mn:int = moore_neighbourhood_count(coord,x_coord,y_coord)["fire"]
                    num_tree_emn:int = extended_moore_neighbourhood_count(coord,x_coord,y_coord)["tree"]

                    if num_fire_mn >= 1:
                        final_coord_dict[(x_coord,y_coord)] = "fire"
                    elif num_tree_emn >= 15 and probability_s:
                        final_coord_dict[(x_coord,y_coord)] = "fire"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "tree"

            case "fire": 
                if (x_coord,y_coord) not in final_coord_dict:

                    probability_o:bool = probability_gen(0.10)
                    
                    if probability_o:
                        final_coord_dict[(x_coord,y_coord)] = "stone"
                    else:
                        final_coord_dict[(x_coord,y_coord)] = "land"

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

# von neumann neighbourhood
def von_neumann_neighbourhood_count(coord,x_coord,y_coord) -> {str:int}:
    coord_dict:{(int):str} = re_list_dict(coord)
    count:dict = {}
    count:dict = {
        "water":0,
        "sand":0,
        "land":0,
        "stone":0,
        "village":0,
        "tree":0,
        "fire":0
    }

    if check_bounds((x_coord, y_coord - 1)):
        count[coord_dict[(x_coord, y_coord - 1)]] = count.get(coord_dict[(x_coord, y_coord - 1)],0) + 1

    if check_bounds((x_coord, y_coord + 1)):
        count[coord_dict[(x_coord, y_coord + 1)]] = count.get(coord_dict[(x_coord, y_coord + 1)],0) + 1

    if check_bounds((x_coord - 1, y_coord)):
        count[coord_dict[(x_coord - 1, y_coord)]] = count.get(coord_dict[(x_coord - 1, y_coord)],0) + 1

    if check_bounds((x_coord + 1, y_coord)):
        count[coord_dict[(x_coord + 1, y_coord)]] = count.get(coord_dict[(x_coord + 1, y_coord)],0) + 1

    return count

# moore neighbourhood
def moore_neighbourhood_count(coord,x_coord,y_coord) -> {str:int}:
    coord_dict:{(int):str} = re_list_dict(coord)
    count:dict = {}
    count:dict = {
        "water":0,
        "sand":0,
        "land":0,
        "stone":0,
        "village":0,
        "tree":0,
        "fire":0
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

# extended moore neighbourhood
def extended_moore_neighbourhood_count(coord,x_coord,y_coord) -> {str:int}:
    coord_dict:{(int):str} = re_list_dict(coord)
    count:dict = {}
    count:dict = {
        "water":0,
        "sand":0,
        "land":0,
        "stone":0,
        "village":0,
        "tree":0,
        "fire":0
    }

    if check_bounds((x_coord - 2, y_coord - 2)):
        count[coord_dict[(x_coord - 2, y_coord - 2)]] = count.get(coord_dict[(x_coord - 2, y_coord - 2)],0) + 1

    if check_bounds((x_coord - 1, y_coord - 2)):
        count[coord_dict[(x_coord - 1, y_coord - 2)]] = count.get(coord_dict[(x_coord - 1, y_coord - 2)],0) + 1

    if check_bounds((x_coord, y_coord - 2)):
        count[coord_dict[(x_coord, y_coord - 2)]] = count.get(coord_dict[(x_coord, y_coord - 2)],0) + 1

    if check_bounds((x_coord + 1, y_coord - 2)):
        count[coord_dict[(x_coord + 1, y_coord - 2)]] = count.get(coord_dict[(x_coord + 1, y_coord - 2)],0) + 1

    if check_bounds((x_coord + 2, y_coord - 2)):
        count[coord_dict[(x_coord + 2, y_coord - 2)]] = count.get(coord_dict[(x_coord + 2, y_coord - 2)],0) + 1

    if check_bounds((x_coord - 2, y_coord - 1)):
        count[coord_dict[(x_coord - 2, y_coord - 1)]] = count.get(coord_dict[(x_coord - 2, y_coord - 1)],0) + 1

    if check_bounds((x_coord - 1, y_coord - 1)):
        count[coord_dict[(x_coord - 1, y_coord - 1)]] = count.get(coord_dict[(x_coord - 1, y_coord - 1)],0) + 1

    if check_bounds((x_coord, y_coord - 1)):
        count[coord_dict[(x_coord, y_coord - 1)]] = count.get(coord_dict[(x_coord, y_coord - 1)],0) + 1

    if check_bounds((x_coord + 1, y_coord - 1)):
        count[coord_dict[(x_coord + 1, y_coord - 1)]] = count.get(coord_dict[(x_coord + 1, y_coord - 1)],0) + 1

    if check_bounds((x_coord + 2, y_coord - 1)):
        count[coord_dict[(x_coord + 2, y_coord - 1)]] = count.get(coord_dict[(x_coord + 2, y_coord - 1)],0) + 1

    if check_bounds((x_coord - 2, y_coord)):
        count[coord_dict[(x_coord - 2, y_coord)]] = count.get(coord_dict[(x_coord - 2, y_coord)],0) + 1

    if check_bounds((x_coord - 1, y_coord)):
        count[coord_dict[(x_coord - 1, y_coord)]] = count.get(coord_dict[(x_coord - 1, y_coord)],0) + 1

    if check_bounds((x_coord + 1, y_coord)):
        count[coord_dict[(x_coord + 1, y_coord)]] = count.get(coord_dict[(x_coord + 1, y_coord)],0) + 1

    if check_bounds((x_coord + 2, y_coord)):
        count[coord_dict[(x_coord + 2, y_coord)]] = count.get(coord_dict[(x_coord + 2, y_coord)],0) + 1

    if check_bounds((x_coord - 2, y_coord + 1)):
        count[coord_dict[(x_coord - 2, y_coord + 1)]] = count.get(coord_dict[(x_coord - 2, y_coord + 1)],0) + 1

    if check_bounds((x_coord - 1, y_coord + 1)):
        count[coord_dict[(x_coord - 1, y_coord + 1)]] = count.get(coord_dict[(x_coord - 1, y_coord + 1)],0) + 1

    if check_bounds((x_coord, y_coord + 1)):
        count[coord_dict[(x_coord, y_coord + 1)]] = count.get(coord_dict[(x_coord, y_coord + 1)],0) + 1

    if check_bounds((x_coord + 1, y_coord + 1)):
        count[coord_dict[(x_coord + 1, y_coord + 1)]] = count.get(coord_dict[(x_coord + 1, y_coord + 1)],0) + 1

    if check_bounds((x_coord + 2, y_coord + 1)):
        count[coord_dict[(x_coord + 2, y_coord + 1)]] = count.get(coord_dict[(x_coord + 2, y_coord + 1)],0) + 1

    if check_bounds((x_coord - 2, y_coord + 2)):
        count[coord_dict[(x_coord - 2, y_coord + 2)]] = count.get(coord_dict[(x_coord - 2, y_coord + 2)],0) + 1

    if check_bounds((x_coord - 1, y_coord + 2)):
        count[coord_dict[(x_coord - 1, y_coord + 2)]] = count.get(coord_dict[(x_coord - 1, y_coord + 2)],0) + 1

    if check_bounds((x_coord, y_coord + 2)):
        count[coord_dict[(x_coord, y_coord + 2)]] = count.get(coord_dict[(x_coord, y_coord + 2)],0) + 1

    if check_bounds((x_coord + 1, y_coord + 2)):
        count[coord_dict[(x_coord + 1, y_coord + 2)]] = count.get(coord_dict[(x_coord + 1, y_coord + 2)],0) + 1

    if check_bounds((x_coord + 2, y_coord + 2)):
        count[coord_dict[(x_coord + 2, y_coord + 2)]] = count.get(coord_dict[(x_coord + 2, y_coord + 2)],0) + 1
        
    return count

# by default, probability is 50 50
def probability_gen(weight:float = 0.0) -> bool:
    return random.randint(1,100) < ((1 + weight) * 5)

# event loop
render(parse_file())