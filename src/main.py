# imports
import curses
import os

# basic info
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

# parse text files 
# - FUA: add error check for incorrect number of x and y 
def parse_file(file_name:str) -> list | None:
    fhand = open(file_name,"r")
    buffer:list = []
    for line in fhand:
        buffer.append(line.rstrip())
    fhand.close()
    for y in range(len(buffer)):
        for x in range(len(buffer[y])):
            match buffer[y][x]:
                case ".": # air block
                    pass
                case "$": # flammable block --> set on fire by fire, dissapears upon combustion leaving soot, doused by water, affected by solid dynamics
                    pass
                case "*": # oil block --> surface set on fire by water, top layer evaporates and produces effervesence, doused by water, affected by liquid dynamics
                    pass
                case "^": # fire block --> doused by water
                    pass
                case "~": # water block --> affected by liquid dynamics, puts out fire at no cost to itself
                    pass
                case "#": # non-flammable block --> not affected by solid dynamics, inert
                    pass
                case "_": # soot block --> affected by solid dynamics
                    pass
                case "%": # effervesence block --> affected by gas dynamics
                    pass
