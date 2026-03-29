| state | character | interaction |
| :---: | :---: | :---: |
| empty | `.` | has a chance every iteration of becoming a tree at probability *p* |
| tree | `%` | becomes a fire cell if 1 or more neighbours is fire OR if 2 neighbours, ignites with probability *f* |
| fire | `^` | becomes empty cell |

> Rules available [here](https://dev.to/triplebyte/how-fire-spreads-mathematical-models-and-simulators-395c).