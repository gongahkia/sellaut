# [Elementary Cellular Automata](https://mathworld.wolfram.com/ElementaryCellularAutomaton.html)

One-dimensional elementary rules rendered downward over time from a single seed row.

| rule | effect |
| :---: | :--- |
| `30` | chaotic triangular growth |
| `90` | Sierpinski-like structure |
| `110` | complex long-lived interactions |
| `0-255` | custom Wolfram rule number |

| sample input | meaning |
| :---: | :--- |
| `.` | off cell |
| `#` | on cell |

## To run

```console
$ git clone https://github.com/gongahkia/cppaut
$ cd cppaut/elmrule
$ make
$ ./build/elmrule
$ ./build/elmrule --input src/eg1.txt --rule 110 --steps 40 --delay 20
```
