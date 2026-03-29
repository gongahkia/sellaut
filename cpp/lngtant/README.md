# [Langton's Ant](https://en.wikipedia.org/wiki/Langton%27s_ant)

Toroidal Langton's Ant on a rectangular ASCII grid.

| current cell | ant action |
| :---: | :--- |
| `.` | turn right, flip the cell to `#`, move forward |
| `#` | turn left, flip the cell to `.`, move forward |

| sample input | meaning |
| :---: | :--- |
| `.` | white cell |
| `#` | black cell |
| `^` `>` `v` `<` | exactly one ant start position and facing |

## To run

```console
$ git clone https://github.com/gongahkia/cppaut
$ cd cppaut/lngtant
$ make
$ ./build/lngtant
$ ./build/lngtant --input src/eg2.txt --steps 120 --delay 30
```
