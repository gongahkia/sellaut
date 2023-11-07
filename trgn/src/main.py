# mypy: ignore-errors
# silence mypy type errors

# imports
import curses
import os

# basic info
# - screen size: (0,0) to (60,25), a 61 by 26 grid
# - implement randomised block generator
# - implement rules as in the README.md

cell_data:dict = {
                    "state": "water",
                    "coordinate": (0,0)
                }
