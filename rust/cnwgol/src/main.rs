// imports from the standard library
use std::process::Command;
use std::thread;
use std::io;
use std::time::Duration;
use std::convert::TryFrom;

// external imports
use colored::*;

#[derive(Copy, Clone)]
#[derive(Debug)]
enum CellState {
    On,
    Off,
}

#[derive(Copy, Clone)]
#[derive(Debug)]
struct Coordinate {
    x_coord:i32,
    y_coord:i32,
}

fn input_to_coordinate_vector() -> Vec<Coordinate> {
    let mut output_vec:Vec<Coordinate> = Vec::new();
    loop {
        Command::new("clear").status().expect("Failed to run command");
        let mut coordinate_x:String = String::new();
        let mut coordinate_y:String = String::new();

        println!("{} {} {}", "Input an".green(), "X-coordinate".yellow(), "between 0 and 50:".green());
        io::stdin().read_line(&mut coordinate_x).expect("Failed to read line");

        println!("{} {} {}", "Input a".green(), "Y-coordinate".yellow(), "between 0 and 20:".green());
        io::stdin().read_line(&mut coordinate_y).expect("Failed to read line");

        let int_coordinate_x:i32 = coordinate_x.trim_end().parse().expect("Failed to parse to integer");
        let int_coordinate_y:i32 = coordinate_y.trim_end().parse().expect("Failed to parse to integer");

        if int_coordinate_x < 0 || int_coordinate_x > 50 || int_coordinate_y < 0 || int_coordinate_y > 20 {
            println!("{}", "Invalid input detected!".red());
            thread::sleep(Duration::from_secs(2));
            continue
        }

        let coordinate = Coordinate {x_coord: int_coordinate_x, y_coord: int_coordinate_y};
        output_vec.push(coordinate);

        println!("{}", "Input received\n".green());
        println!("{} {} {} {} {}", "Input".green(), "[E]".yellow(), "to exit, or".green(), "[Enter]".yellow(), "to continue:".green());
        let mut exit_condition:String = String::new();
        io::stdin().read_line(&mut exit_condition).expect("Failed to read line");
        if exit_condition.trim_end().to_lowercase() == String::from("e") {
            break
        }
    }
    output_vec
}

fn array_to_cellstate_on(mut grid_display:Vec<Vec<CellState>>, coordinate_vector:Vec<Coordinate>) -> Vec<Vec<CellState>> {
    for coordinate in coordinate_vector {
        println!("{:?}", coordinate);
        grid_display[i32_to_usize(coordinate.y_coord.clone())][i32_to_usize(coordinate.x_coord.clone())] = CellState::On;
    }
    grid_display
}

// since Rust slices can only be indexed by usize
fn i32_to_usize(number_i32:i32) -> usize {
    let number_usize:usize = usize::try_from(number_i32).expect("Failed to parse large number");
    number_usize
}

fn coordinate_to_cellstate(grid_display:Vec<Vec<CellState>>, c_struct:Coordinate) -> bool {
    if c_struct.y_coord.clone() < 0 || c_struct.x_coord.clone() < 0 || c_struct.y_coord.clone() > 20 || c_struct.x_coord.clone() > 50 {
        false
        // the overflow error is handled by the coordinate_to_cellstate() function here:
            // not within required bounds, a check is not necessary as coordinate is not included within the count
    } else {
        let coordinate_cellstate:CellState = grid_display[i32_to_usize(c_struct.y_coord.clone())][i32_to_usize(c_struct.x_coord.clone())];
        match coordinate_cellstate {
            CellState::On => true,
            CellState::Off => false
        }
    }
}

fn display_grid(grid_display:Vec<Vec<CellState>>) -> String {
    let mut final_grid:String = String::new();
    for y in 0..21 {
        for x in 0..51 {
            match grid_display[y][x] {
                CellState::On => {
                    final_grid.push_str("X");
                },
                CellState::Off => {
                    final_grid.push_str(" ");
                },
            }
        }
        final_grid.push_str("\n");
    }
    final_grid
}

fn update_grid(grid_display:Vec<Vec<CellState>>) -> Vec<Vec<CellState>> {
    let mut final_output_grid:Vec<Vec<CellState>> = Vec::new();
    for y in 0..21 {
        let mut x_output_grid:Vec<CellState> = Vec::new();
        for x in 0..51 {
            let c5:Coordinate = Coordinate {x_coord:x, y_coord:y};
            let c5_live_neighbours:u32 = num_live_neighbours(grid_display.clone(), c5.clone());
            match c5_live_neighbours {
            // implement the relevant rules for Conway's game of life within this match statement
                // RULES
                // 1. Any live cell with two or three live neighbours survives.
                // 2. Any dead cell with three live neighbours becomes a live cell.
                // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                0 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },
                
                1 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },

                2 => {
                    // to adhere to rule:
                    // 1. Any live cell with two or three live neighbours survives.
                    if coordinate_to_cellstate(grid_display.clone(), c5.clone()) {
                        x_output_grid.push(CellState::On);
                    } else {
                        x_output_grid.push(CellState::Off);
                    }
                },

                3 => {
                    // to adhere to rules:
                    // 1. Any live cell with two or three live neighbours survives.
                    // 2. Any dead cell with three live neighbours becomes a live cell.
                    // tldr: either way any cell with three live neighbours survives the next
                    // iteration
                    x_output_grid.push(CellState::On);
                }, 

                4 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },

                5 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },

                6 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },

                7 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },
                
                8 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },

                9 => {
                    // to adhere to rule:
                    // 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    x_output_grid.push(CellState::Off);
                },

                // edge cases diam diam, this technically should be impossible anyway
                _ => ()
            }
        }
        final_output_grid.push(x_output_grid.clone());
    }
    final_output_grid
}
            
fn num_live_neighbours(grid_display:Vec<Vec<CellState>>, c_struct:Coordinate) -> u32 {
    // cell 5 is current coordinate cell!
    // naming convention for the neighbour coordinates            
    // [1][2][3]
    // [4][5][6]
    // [7][8][9]

    let x:i32 = c_struct.x_coord;
    let y:i32 = c_struct.y_coord;

    let c1:Coordinate = Coordinate {x_coord:x-1, y_coord:y-1};
    let c2:Coordinate = Coordinate {x_coord:x, y_coord:y-1};
    let c3:Coordinate = Coordinate {x_coord:x+1, y_coord:y-1};
    let c4:Coordinate = Coordinate {x_coord:x-1, y_coord:y};
    let c6:Coordinate = Coordinate {x_coord:x+1, y_coord:y};
    let c7:Coordinate = Coordinate {x_coord:x-1, y_coord:y+1};
    let c8:Coordinate = Coordinate {x_coord:x, y_coord:y+1};
    let c9:Coordinate = Coordinate {x_coord:x+1, y_coord:y+1};

    // --- COUNTING NEIGHBOURS

    let mut live_neighbour_count:u32 = 0;
    
    if coordinate_to_cellstate(grid_display.clone(), c1.clone()) {
        // for debugging
        live_neighbour_count += 1;
        /* println!("it 1");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c1); */
    }
    if coordinate_to_cellstate(grid_display.clone(), c2.clone()) {
        // for debugging
        live_neighbour_count += 1;
        /* println!("it 2");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c2); */
    }
    if coordinate_to_cellstate(grid_display.clone(), c3.clone()) {
        // for debugging
        live_neighbour_count += 1;
        /* println!("it 3");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c3); 8 */
    }
    if coordinate_to_cellstate(grid_display.clone(), c4.clone()) {
        // for debugging
        live_neighbour_count += 1;
        /* println!("it 4");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c4); */
    }
    if coordinate_to_cellstate(grid_display.clone(), c6.clone()) {
        // for debugging
        live_neighbour_count += 1;
        /* println!("it 6");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c6); */
    }
    if coordinate_to_cellstate(grid_display.clone(), c7.clone()) {
        // for debugging
        /* live_neighbour_count += 1;
        println!("it 7");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c7); */
    }
    if coordinate_to_cellstate(grid_display.clone(), c8.clone()) {
        // for debugging
        live_neighbour_count += 1;
        /* println!("it 8");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c8); */
    }
    if coordinate_to_cellstate(grid_display.clone(), c9.clone()) {
        // for debugging
        /* live_neighbour_count += 1;
        println!("it 9");
        println!("neighbour count: {}", live_neighbour_count);
        println!("{:?}", c9); */
    }
    live_neighbour_count
}

fn main() {
    // -- always .clone() in Rust to avoid memory errors first, learn about borrowing later
    let mut grid_display:Vec<Vec<CellState>> = vec![vec![CellState::Off; 51]; 21];

    // ~~~ TESTING STARTS HERE ~~~

    /* 

    // i'm not cloning these values in the function call below because i know they won't be reused later!
    let _c1:Coordinate = Coordinate {x_coord:0, y_coord:0};
    let c2:Coordinate = Coordinate {x_coord:1, y_coord:0};
    let c3:Coordinate = Coordinate {x_coord:0, y_coord:1};
    let c4:Coordinate = Coordinate {x_coord:1, y_coord:1};
    let c5:Coordinate = Coordinate {x_coord:49, y_coord:19};
    let c6:Coordinate = Coordinate {x_coord:50, y_coord:19};
    let c7:Coordinate = Coordinate {x_coord:49, y_coord:20};
    let cEmptyControl:Coordinate = Coordinate {x_coord:25, y_coord:10};
    let _c50:Coordinate = Coordinate {x_coord:50, y_coord:20};

    // checking the num_live_neighbours count function works
    println!("neighbour count for coordinate 1,0 --> {}", num_live_neighbours(grid_display.clone(), c2));
    println!("neighbour count for coordinate 0,1 --> {}", num_live_neighbours(grid_display.clone(), c3));
    println!("neighbour count for coordinate 1,1 --> {}", num_live_neighbours(grid_display.clone(), c4));
    println!("{}", "-------------".yellow());
    println!("neighbour count for coordinate 49,19 --> {}", num_live_neighbours(grid_display.clone(), c5));
    println!("neighbour count for coordinate 50,19 --> {}", num_live_neighbours(grid_display.clone(), c6));
    println!("neighbour count for coordinate 49,20 --> {}", num_live_neighbours(grid_display.clone(), c7));
    println!("neighbour count for coordinate 25,10 --> {}", num_live_neighbours(grid_display.clone(), cEmptyControl)); 

    */

    // ~~~ TESTING ENDS HERE ~~~

    let coordinate_vector:Vec<Coordinate> = input_to_coordinate_vector();
    grid_display = array_to_cellstate_on(grid_display.clone(), coordinate_vector.clone());

    // main event loop
    loop {
        // required boilerplate
        Command::new("clear").status().expect("Failed to run command");
        println!("{}\n", "Conway's game of life".bright_green());
        
        // debugging
        // println!("{:?}", grid_display);
        println!("{}", display_grid(grid_display.clone()));

        // reassigning the return value of update_grid() function, allowing me to easily clone it!
        grid_display = update_grid(grid_display.clone());
        thread::sleep(Duration::from_secs(1));
    }
}
