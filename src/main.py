# imports
import curses
import os

# basic info
# - integrate curses CLI and integrate existing file_ui method into it
# - screen size: [0,0] to [60,25]
# - FUA: add colors to the screen
#      : implement interactions between elements
#      : implement solid dynamics (gravity), liquid dynamics (gravity and liquid fluidity) and gas dynamics

# cell state represented by a dictionary
cell_data:dict = {
                    "element": "air",
                    "coordinate": [0,0]
                }

# file selector ui
# FUA: - probably need to rework this later using the curses CLI module
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
        print(display.rstrip(),end="")
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
        if len(line.rstrip()) != 60:
            return None
        print(line, end="")
        buffer.append(line.rstrip())
    fhand.close()
    if len(buffer) != 25:
        return None
    return buffer

# parse text files 
# FUA: - implement logic for this
def parse_file() -> [dict]:
    buffer:[str] = file_ui()
    if not buffer:
        os.system("clear")
        print("Incorrect number of rows and columns. Please input a 60 by 25 grid.")
        return None
    coord:[dict] = []
    for y in range(len(buffer)):
        for x in range(len(buffer[y])):
            cell_data:dict = {
                                "element": "air",
                                "coordinate": [0,0]
                            }
            match buffer[y][x]:
                case ".": # air block
                    cell_data["element"] = "air_block"
                    cell_data["coordinate"] = [x,y]
                case "$": # flammable block --> set on fire by fire, dissapears upon combustion leaving soot, doused by water, affected by solid dynamics
                    cell_data["element"] = "flammable_block"
                    cell_data["coordinate"] = [x,y]
                case "*": # oil block --> surface set on fire by water, top layer evaporates and produces effervesence, doused by water, affected by liquid dynamics
                    cell_data["element"] = "oil_block"
                    cell_data["coordinate"] = [x,y]
                case "^": # fire block --> doused by water
                    cell_data["element"] = "fire_block"
                    cell_data["coordinate"] = [x,y]
                case "~": # water block --> affected by liquid dynamics, puts out fire at no cost to itself
                    cell_data["element"] = "water_block"
                    cell_data["coordinate"] = [x,y]
                case "#": # non-flammable block --> not affected by solid dynamics, inert
                    cell_data["element"] = "non-flammable_block"
                    cell_data["coordinate"] = [x,y]
                case "_": # soot block --> affected by solid dynamics
                    cell_data["element"] = "soot_block"
                    cell_data["coordinate"] = [x,y]
                case "%": # effervesence block --> affected by gas dynamics
                    cell_data["element"] = "effervesence_block"
                    cell_data["coordinate"] = [x,y]
                case _: # edge case --> this shouldn't exist
                    os.system("clear")
                    print(f"Unknown character found in line {y + 1} --> [{buffer[y][x]}]")
                    return None
            coord.append(cell_data)

# event loop
parse_file()
