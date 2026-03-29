# [Cyclic Cellular Automaton](https://en.wikipedia.org/wiki/Cyclic_cellular_automaton)

Six-state cyclic automaton on a toroidal grid.

| state | character | interaction |
| :---: | :---: | :--- |
| phase 0 | `0` | advances to `1` if at least 2 neighbors are already `1` |
| phase 1 | `1` | advances to `2` if at least 2 neighbors are already `2` |
| phase 2 | `2` | advances to `3` if at least 2 neighbors are already `3` |
| phase 3 | `3` | advances to `4` if at least 2 neighbors are already `4` |
| phase 4 | `4` | advances to `5` if at least 2 neighbors are already `5` |
| phase 5 | `5` | advances to `0` if at least 2 neighbors are already `0` |

| sample input | meaning |
| :---: | :--- |
| `0` `1` `2` `3` `4` `5` | one of the six cyclic phases |

## To run

```console
$ git clone https://github.com/gongahkia/cppaut
$ cd cppaut/cycaut
$ make
$ ./build/cycaut
$ ./build/cycaut --input src/eg2.txt --steps 100 --delay 25
```
