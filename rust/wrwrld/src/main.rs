// TO IMPLEMENT
    // -- visual interface that allows drawing of conductors etc

// TO DEBUG

// REFERENCES
    // -- reference grid can be found at https://docs.google.com/spreadsheets/d/1IqnQmAzA5Csrg4qfyqQYj8Mq_NAmfO-QuABiW2rEnfM/edit?usp=sharing
    // -- https://xalava.github.io/WireWorld/

// Wireworld rules
    // 1. Empty -> Empty
    // 2. ElectronHead -> ElectronTail
    // 3. ElectronTail -> Conductor
    // 4. Conductor -> ElectronHead if 1 or 2 of the neighbouring cells are ElectronHeads, otherwise remains conductor

// ----------

use std::process::Command;
use std::io;
use std::io::Write;
use std::time::Duration;
use std::thread;
use std::fs;

use colored::*;

#[derive(Copy, Clone)]
#[derive(Debug)]
enum CellState {
    Outofbounds,
    Empty,
    ElectronHead,
    ElectronTail,
    Conductor,
}

#[derive(Copy, Clone)]
#[derive(Debug)]
struct Coordinate {
    x_coord:i32,
    y_coord:i32,
}

fn process_text_file(mut output_grid_display:Vec<Vec<CellState>>) -> Vec<Vec<CellState>> {

    Command::new("clear").status().expect("Failed to run command");
    let mut file_vector:Vec<String> = Vec::new();
    let mut desired_index_i32:i32;
    for file in fs::read_dir("./").expect("Unable to read file directory") {
        let file_name:String = file.expect("Unable to open file").path().display().to_string();
        let file_name_vector:Vec<&str> = file_name.split("./").collect();
        file_vector.push(file_name_vector[1].to_string());
    }
    loop {
        println!("{}\n", "Please select a number corresponding to your desired file.".green());
        let mut index:i32 = 0;
        let mut counter:u8 = 1;
        for entry in file_vector.clone() {
            if entry == String::from("main.rs") || entry == String::from(".main.rs.swp") {
                file_vector.remove(i32_to_usize(index));
                index += 1;
            } else {
                println!("{} {} {}", counter, "|".green(), entry);
                counter += 1;
                index += 1;
            }
        }

        let mut desired_index:String = String::new();
        io::stdin().read_line(&mut desired_index).expect("Failed to read line");
        desired_index = desired_index.trim_end().to_string();
        desired_index_i32 = desired_index.parse::<i32>().expect("Failed to parse number") - 1;
        if desired_index_i32 < 0 || desired_index_i32 > usize_to_i32(file_vector.clone().len()) - 1 {
            Command::new("clear").status().expect("Failed to run command");
            println!("{}\n", "Invalid number detected, please reenter.".red()); 
            continue;
        } else {
            break;
        }
    }

    let file_vector_clone:Vec<String> = file_vector.clone();
    let desired_file_name:&str = file_vector_clone[i32_to_usize(desired_index_i32.clone())].as_str();

    let file_contents:String = fs::read_to_string(desired_file_name.clone()).expect("Failed to read file into string");
    let mut row_vector:Vec<&str> = file_contents.split("\n").collect();
    row_vector.pop();
    
    let mut coordinate_vector_conductor:Vec<Coordinate> = Vec::new();
    let mut coordinate_vector_electronhead:Vec<Coordinate> = Vec::new();
    
    for (index_y, row) in row_vector.into_iter().enumerate() {
        for (index_x, character) in row.chars().enumerate() {
            let i32_index_x:i32 = usize_to_i32(index_x);
            let i32_index_y:i32 = usize_to_i32(index_y);
            let current_coordinate:Coordinate = Coordinate {x_coord:i32_index_x, y_coord:i32_index_y};
            // empty_space represented by the '-' character
            // coordinate_vector_conductor: called for 'x' character
            // coordinate_vector_electronhead: called for 'o' character
            match character {
                '-' => (),
                'o' => {
                    coordinate_vector_electronhead.push(current_coordinate);
                },

                'x' => {
                    coordinate_vector_conductor.push(current_coordinate);
                },
                _ => (),
            }
        }
    }
    
    output_grid_display = array_to_cellstate_conductor(output_grid_display.clone(), coordinate_vector_conductor.clone());
    output_grid_display = array_to_cellstate_electronhead(output_grid_display.clone(), coordinate_vector_electronhead.clone());
    output_grid_display
}

fn coordinate_to_cellstate(grid_display:Vec<Vec<CellState>>, c_struct:Coordinate) -> CellState {
    if c_struct.y_coord.clone() < 0 || c_struct.x_coord.clone() < 0 || c_struct.y_coord.clone() > 20 || c_struct.x_coord.clone() > 50 {
        CellState::Outofbounds
        // the overflow error is handled by the coordinate_to_cellstate() function here, not within required bounds, a check is not necessary as coordinate is not included within the count
    } else {
        grid_display[i32_to_usize(c_struct.y_coord.clone())][i32_to_usize(c_struct.x_coord.clone())]
    }
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

    let mut electronhead_neighbour_count:u32 = 0;

    match coordinate_to_cellstate(grid_display.clone(), c1.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }
    
    match coordinate_to_cellstate(grid_display.clone(), c2.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }

    match coordinate_to_cellstate(grid_display.clone(), c3.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }

    match coordinate_to_cellstate(grid_display.clone(), c4.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }

    match coordinate_to_cellstate(grid_display.clone(), c6.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }

    match coordinate_to_cellstate(grid_display.clone(), c7.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }

    match coordinate_to_cellstate(grid_display.clone(), c8.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }

    match coordinate_to_cellstate(grid_display.clone(), c9.clone()) {
        CellState::Empty => (),
        CellState::ElectronTail => (),
        CellState::Conductor => (),
        CellState::Outofbounds => (),
        CellState::ElectronHead => {
            electronhead_neighbour_count += 1;
        },
    }
    electronhead_neighbour_count
}

fn update_grid(grid_display:Vec<Vec<CellState>>) -> Vec<Vec<CellState>> {

// Wireworld rules
    // 1. Empty -> Empty
    // 2. ElectronHead -> ElectronTail
    // 3. ElectronTail -> Conductor
    // 4. Conductor -> ElectronHead if 1 or 2 of the neighbouring 
    // cells are ElectronHeads, otherwise remains conductor

    let mut final_output_grid:Vec<Vec<CellState>> = Vec::new();
    for y in 0..21 {
        let mut x_output_grid:Vec<CellState> = Vec::new();
        for x in 0..51 {
            let c5:Coordinate = Coordinate {x_coord:x, y_coord:y};
            let electronhead_neighbour_count:u32 = num_live_neighbours(grid_display.clone(), c5.clone());
            match coordinate_to_cellstate(grid_display.clone(), c5.clone()) {
                CellState::Outofbounds => {
                },
                CellState::Empty => {
                    x_output_grid.push(CellState::Empty); 
                },
                CellState::ElectronHead => {
                    x_output_grid.push(CellState::ElectronTail); 
                },
                CellState::ElectronTail => {
                    x_output_grid.push(CellState::Conductor); 
                },
                CellState::Conductor => {
                    if electronhead_neighbour_count == 1 || electronhead_neighbour_count == 2 {
                        x_output_grid.push(CellState::ElectronHead);
                    } else {
                        x_output_grid.push(CellState::Conductor);
                    }
                },
            }
        }
        final_output_grid.push(x_output_grid.clone());
    }
    final_output_grid
}

fn array_to_cellstate_conductor(mut grid_display:Vec<Vec<CellState>>, coordinate_vector:Vec<Coordinate>) -> Vec<Vec<CellState>> {
    for coordinate in coordinate_vector {
        // println!("{:?}", coordinate);
        grid_display[i32_to_usize(coordinate.y_coord.clone())][i32_to_usize(coordinate.x_coord.clone())] = CellState::Conductor;
    }
    grid_display
}

fn array_to_cellstate_electronhead(mut grid_display:Vec<Vec<CellState>>, coordinate_vector:Vec<Coordinate>) -> Vec<Vec<CellState>> {
    for coordinate in coordinate_vector {
        // println!("{:?}", coordinate);
        grid_display[i32_to_usize(coordinate.y_coord.clone())][i32_to_usize(coordinate.x_coord.clone())] = CellState::ElectronHead;
    }
    grid_display
}

// since Rust slices can only be indexed by usize
fn i32_to_usize(number_i32:i32) -> usize {
    let number_usize:usize = usize::try_from(number_i32).expect("Failed to parse large number");
    number_usize
}

// try_from() is a sick function
fn usize_to_i32(number_usize:usize) -> i32 {
    let number_i32:i32 = i32::try_from(number_usize).expect("Failed to parse large number");
    number_i32
}

fn display_grid(grid_display:Vec<Vec<CellState>>) {
    for y in 0..21 {
        for x in 0..51 {
            match grid_display[y][x] {
                CellState::Empty => {
                    print!(" ");
                    io::stdout().flush().expect("Failed to flush buffer");
                },
                CellState::ElectronHead => {
                    print!("{}", "X".blue());
                    io::stdout().flush().expect("Failed to flush buffer");
                },
                CellState::ElectronTail => {
                    print!("{}", "X".red());
                    io::stdout().flush().expect("Failed to flush buffer");
                },
                CellState::Conductor => {
                    print!("{}", "X".yellow());
                    io::stdout().flush().expect("Failed to flush buffer");
                },
                CellState::Outofbounds => (),
            }
        }
        print!("\n");
        io::stdout().flush().expect("Failed to flush buffer");
    }
}

fn main() {
    Command::new("clear").status().expect("Failed to run command");
    let mut grid_display:Vec<Vec<CellState>> = vec![vec![CellState::Empty; 51]; 21];
    grid_display = process_text_file(grid_display);

    loop {
        // println!("ass");
        Command::new("clear").status().expect("Failed to run command");
        println!("{}\n", "Wireworld".cyan());
        display_grid(grid_display.clone());
        grid_display = update_grid(grid_display.clone());
        thread::sleep(Duration::from_millis(300));
    }
}
