| state | character | interaction |
| :---: | :---: | :---: |
| water | `≈` | stays as water |
| sand | `#` | becomes water if surrounded by 3 or more water cells in vnn, becomes land if 2 or more land cell in vnn |
| land | `.` | becomes village if 20 or more land cells and 1 or more stone cells in en with probability *i*, becomes village if 1 or more village cells in mn with probability *h*, becomes stone with probability *f* if 0 water cells in mn, becomes tree with probability *g* if 1 water cell and 0 stone cells in mn, becomes tree with probability *a* if 8 land cells in mn and 1 or more tree cell in emn, becomes sand if 7 or more sand cells in emn |
| stone | `*` | becomes land with probability *p*, becomes sand with probability *e* if 7 or more sand cells in emn | 
| village | `&` | becomes fire if 1 or more village cells in emn and 0 tree cells in emn |
| tree | `%` | becomes fire if 1 or more fire cells in mn |
| fire | `^` | becomes stone with probability *o*, else becomes land |

> **vnn**: von neumann neighbourhood (4 surrounding cells)
> **mn**: moore neighbourhood (8 surrounding cells)
> **emn** : extended moore neighbourhood (24 surrounding cells)
