#!/usr/bin/env python
import subprocess
import os
import shutil
from pathlib import Path
import sys
import csv





#----------------------------------------------------------------------------------------------------------------
#================================================================================================================ 
# ENVIROMENT-VARIABLES
#================================================================================================================
PATH_TO_TRACY_FOLDER = "C:/utils/trace_0.11.0"
PATH_TO_SIMULATION_FOLDER = "C:/source/rust/KrABMagaTirocinio_provisory/examples/flockers"
PATH_TO_DEST_FOLDER = "garbage"

TRACY_EXE = "tracy-capture.exe"
TRACY_RETRIEVE_CSV_EXE = "tracy-csvexport.exe"

BENCHMARK_CSV_FILE = "benchmark_extracted.csv"
BENCHMARK_RESULT = "benchmark_result.csv"
INPUT_FILE = "input.txt"

TRASH_TRACY_DEBUG_FILE = "simulation_tracy.txt"
TRASH_SIMULATION_DEBUG_FILE = "simulation_debug.txt"

NUM_STEPS = 200 # number of steps for simulation
NUM_RUN = 5 # number of repetition of the same simulation 
#----------------------------------------------------------------------------------------------------------------





#----------------------------------------------------------------------------------------------------------------
#================================================================================================================
# MAIN
#================================================================================================================
if __name__ == "__main__":

    # SETTING UP ENVIROMENT

    # Retrieve command-line arguments
    argv = sys.argv[1:]
    print(argv)
    for arg in argv:
        # Split name and value of parameters
        line_splitted = arg.split('=')
        name, value = line_splitted[0], line_splitted[1]
        # Split name and value of parameters

        # DEBUG
        print("name: " + name)
        print("value: " + value)
        # DEBUG

        if name.lower() == PATH_TO_DEST_FOLDER:
            PATH_TO_DEST_FOLDER = value
        elif name.lower() == PATH_TO_SIMULATION_FOLDER:
            PATH_TO_SIMULATION_FOLDER = value
        elif name.lower() == PATH_TO_TRACY_FOLDER:
            PATH_TO_TRACY_FOLDER = value
        elif name.lower() == NUM_STEPS:
            NUM_STEPS = value
        elif name.lower() == NUM_RUN:
            NUM_RUN = value
    # Retrieve command-line arguments

    # Cleaning past garbage's directory
    shutil.rmtree(PATH_TO_DEST_FOLDER, ignore_errors=True)
    # Cleaning past garbage's directory

    # Create a garbage's directory
    os.mkdir(PATH_TO_DEST_FOLDER)
    # Create a garbage's directory

    # Compute some complete paths
    PATH_TO_TRACY_EXE = os.path.join(PATH_TO_TRACY_FOLDER, TRACY_EXE)
    PATH_TO_TRACY_RETRIEVE_CSV_EXE = os.path.join(PATH_TO_TRACY_FOLDER, TRACY_RETRIEVE_CSV_EXE)
    PATH_TO_TRACY_BENCHMARK_CSV_FILE = os.path.join(PATH_TO_DEST_FOLDER, BENCHMARK_CSV_FILE)
    PATH_TO_BENCHMARK_RESULT = os.path.join(PATH_TO_DEST_FOLDER, BENCHMARK_RESULT)
    PATH_TO_TRASH_TRACY_DEBUG_FILE = os.path.join(PATH_TO_DEST_FOLDER, TRASH_TRACY_DEBUG_FILE)
    # Compute some complete paths

    # Define a list that describe the fields to extract and save
    # data to extract and save: 
    #  0 mean_elapsed time for flocker's step's time zone 
    #  1 mean_elapsed time for update_field's time zone
    #  2 elapsed time of the simulation
    # ATTENTION: fields' list describe the order in which data are written in row of csv file
    zone_names = ["system{name=\"flockers::step_system\"}", "system{name=\"krabmaga::engine::fields::field_2d::update_field\"}"]

    fields = []
    for zone_name in zone_names:
        fields.append(zone_name)
    fields.append("elapsed_time")
    # Define a list that describe the fields to extract and save

    # SETTING UP ENVIROMENT




    # Retrieve the inputs from file and save parameters of simulations in an object
    # The format expected is the sequent:
    # 0 number of threads
    # 1 number of agents
    # 2 size of field
    simulations = []

    f = open(INPUT_FILE, "r")
    for line in f.readlines():
        if line.isspace(): # skip if line is only formed by white-spaces
            continue

        values = line.split() # split on space line

        # DEBUG
        print("VALUES RETRIEVED FROM INPUT.TXT:")
        print(values[0])
        print(values[1])
        print(values[2])
        # DEBUG

        simulation = (values[0], values[1], values[2])
        simulations.append(simulation)
    # Retrieve the inputs from file and save parameters of simulations in an object



    current_test = 0
    simulation_results = []

    # Until simulations isn't empty
    while simulations:
        simulation = simulations.pop(0)

        current_test = current_test + 1

        num_threads = simulation[0]
        num_agents = simulation[1]
        field_size = simulation[2]

        # Compute name and path of tracy's benchmark 
        benchmark_tracy_values = ("benchmark", str(current_test), str(num_threads), str(num_agents), str(field_size), ".tracy")
        benchmark_tracy_name = "_".join(benchmark_tracy_values)
        PATH_TO_RESULT_TRACY_FILE = os.path.join(PATH_TO_DEST_FOLDER, benchmark_tracy_name)
        # Compute name and path of tracy's benchmark



        # Initialize simulation_result
        # Initialize all the fields to zero because we need to do a mean of the results on all the runs
        simulation_result = {"elapsed_time": float(0)}
        for zone_name in zone_names:
            simulation_result[zone_name] = float(0)
        # Initialize simulation_result



        # Repeat this operation for NUM_RUN
        for _ in range(NUM_RUN):
            # DEBUG
            print("CURRENT WORKING DIRECTORY: " + os.getcwd())
            # DEBUG
    
            # Build and execute command to start tracy-capture(tracy's server) in background(in another thread)
            # we must run in another thread tracy-capture so we can run the simulation in this thread
            command = PATH_TO_TRACY_EXE + " -f -o " + PATH_TO_RESULT_TRACY_FILE + " > " + PATH_TO_TRASH_TRACY_DEBUG_FILE
            # DEBUG
            print("TRACY-CAPTURE: " + command)
            # DEBUG
            process_tracy_capture = subprocess.Popen(command, shell=True)
            # Build and execute command to start tracy-capture(tracy's server) in background(in another thread)
    
            # Save the current working directory and chdir to simulation's folder
            current_working_dir = os.getcwd()
            os.chdir(PATH_TO_SIMULATION_FOLDER)
            # Save the current working directory and chdir to simulation's folder
    
            # Set properly RUSTFLAGS
            # This is necessary to hide all the warnings generated by cargo, to not display that during this phase
            os.putenv("RUSTFLAGS", "-Awarnings")
            # Set properly RUSTFLAGS

            # Build and execute command to start simulation
            arguments = " -- " + num_threads + " " + num_agents + " " + field_size
            command = "cargo run --release --features \"krabmaga/multithreaded krabmaga/trace_tracy\"" + arguments
            os.system(command)
            # Build and execute command to start simulation

            # Reset default RUSTFLAGS
            os.putenv("RUSTFLAGS", "")
            # Reset default RUSTFLAGS
    
            # Return to the old working directory
            os.chdir(current_working_dir)
            # Return to the old working directory
            
            # Wait till tracy-capture isn't ended
            process_tracy_capture.wait()
            # Wait till tracy-capture isn't ended
    
            # Produce csv file with profiling's information from .tracy with tracy-csvexport
            command = PATH_TO_TRACY_RETRIEVE_CSV_EXE + " " + PATH_TO_RESULT_TRACY_FILE + " > " + PATH_TO_TRACY_BENCHMARK_CSV_FILE 
            os.system(command)
            # Produce csv file with profiling's information from .tracy with tracy-csvexport
    
            # Extract from csv of the result some data    
            with open(PATH_TO_TRACY_BENCHMARK_CSV_FILE, newline='') as csvfile:
                csvreader = csv.DictReader(csvfile, delimiter=',')
    
                for row in csvreader:
                    zone_name = row['name'] 
                    if zone_name in zone_names:
                        mean_ns = float(row['mean_ns'])
                        simulation_result[zone_name] += mean_ns
            # Extract from csv of the result some data
    
        # Delete csv
        os.remove(PATH_TO_TRACY_BENCHMARK_CSV_FILE)
        # Delete csv
    
        # save simulation result in a data structures in central memory
        # TODO make simulation_result parameters the mean on NUM_RUN
        # DEBUG
        print("BEFORE: " + str(simulation_result["system{name=\"flockers::step_system\"}"]))
        # DEBUG
        for key, value in simulation_result.items():
            simulation_result[key] = value / NUM_RUN
        # DEBUG
        print("AFTER: " + str(simulation_result["system{name=\"flockers::step_system\"}"]))
        # DEBUG
        simulation_results.append(simulation_result)
        # save simulation result in a data structures in central memory
        
        # Repeat this operation for NUM_RUN

    # DEBUG
    print("SIMULATION_RESULTS:")
    print(simulation_results[0]["system{name=\"flockers::step_system\"}"])
    print(simulation_results[0]["system{name=\"krabmaga::engine::fields::field_2d::update_field\"}"])
    print(simulation_results[0]["elapsed_time"])
    # DEBUG



    # save simulations' data in the file at the end
    with open(PATH_TO_BENCHMARK_RESULT, "w", newline='') as csvfile:
        benchmark_result = csv.DictWriter(csvfile, fieldnames=fields, delimiter='\t')

        benchmark_result.writeheader()
        for simulation_result in simulation_results:
            benchmark_result.writerow(simulation_result)
    # save simulations' data in the file at the end
#----------------------------------------------------------------------------------------------------------------