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
    # Retrieve command-line arguments

    # Cleaning past garbage
    shutil.rmtree(PATH_TO_DEST_FOLDER, ignore_errors=True)
    # Cleaning past garbage

    # Create a garbage directory
    os.mkdir(PATH_TO_DEST_FOLDER)
    # Create a garbage directory

    # Compute some complete paths
    PATH_TO_TRACY_EXE = os.path.join(PATH_TO_TRACY_FOLDER, TRACY_EXE)
    PATH_TO_TRACY_RETRIEVE_CSV_EXE = os.path.join(PATH_TO_TRACY_FOLDER, TRACY_RETRIEVE_CSV_EXE)
    PATH_TO_TRACY_BENCHMARK_CSV_FILE = os.path.join(PATH_TO_DEST_FOLDER, BENCHMARK_CSV_FILE)
    PATH_TO_BENCHMARK_RESULT = os.path.join(PATH_TO_DEST_FOLDER, BENCHMARK_RESULT)
    # Compute some complete paths

    # SETTING UP ENVIROMENT



    # Retrieve the inputs from file and save parameters of simulations in an object
    simulations = []

    f = open(INPUT_FILE, "r")
    for line in f.readlines():
        if line.isspace():
            continue

        values = line.split()

        # DEBUG
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

        # DEBUG
        print(os.getcwd())
        # DEBUG

        # Build and execute command to start tracy-capture(tracy's server) in background(in another thread)
        # we must run in another thread tracy-capture so we can run the simulation in this
        command = PATH_TO_TRACY_EXE + " -f -o " + PATH_TO_RESULT_TRACY_FILE
        # DEBUG
        print(command)
        # DEBUG
        process_tracy_capture = subprocess.Popen(command, shell=True)
        # Build and execute command to start tracy-capture(tracy's server) in background(in another thread)

        # Save the current working directory and chdir to simulation's folder
        current_working_dir = os.getcwd()
        os.chdir(PATH_TO_SIMULATION_FOLDER)
        # Save the current working directory and chdir to simulation's folder

        # Build and execute command to start simulation
        arguments = " -- " + num_threads + " " + num_agents + " " + field_size
        command = "cargo run --release --features \"krabmaga/multithreaded krabmaga/trace_tracy\"" + arguments
        os.system(command)
        # Build and execute command to start simulation

        # Return to the old working directory
        os.chdir(current_working_dir)
        # Return to the old working directory
        
        # Wait till tracy capture isn't ended
        process_tracy_capture.wait()
        # Wait till tracy capture isn't ended

        # Produce csv file from tracy with tracy-csvexport
        command = PATH_TO_TRACY_RETRIEVE_CSV_EXE + " " + PATH_TO_RESULT_TRACY_FILE + " > " + PATH_TO_TRACY_BENCHMARK_CSV_FILE 
        os.system(command)
        # Produce csv file from tracy with tracy-csvexport

        # Extract from csv of the result some data
        # data to extract: 
        #  - mean_elapsed time for update_field's time zone
        #  - mean_elapsed time for flocker's step's time zone 
        #  - elapsed time of the simulation
        zone_names = ["system{name=\"flockers::step_system\"}", "system{name=\"krabmaga::engine::fields::field_2d::update_field\"}"]
        simulation_result = {}

        with open('example.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')

            for row in csvreader:
                zone_name = row['name'] 
                if zone_name in zone_names:
                    mean_ns = float(row['mean_ns'])
                    simulation_result[zone_name] = mean_ns

        print(simulation_result)
        # Extract from csv of the result some data

        # Delete csv # TEMPORARY temporary removed file from directory
        # os.remove(PATH_TO_TRACY_BENCHMARK_CSV_FILE)
        # Delete csv

        # save simulation result in a data structures in central memory
        simulation_results.append(simulation_result)
        # save simulation result in a data structures in central memory

    # Until simulations isn't empty

    # save simulations' data in the file at the end
    # 0 - mean of elapsed time step's zone 
    # 1 - mean of elapsed time update_field's zone
    # 2 - elapsed time of simulation
    benchmark_result = open(PATH_TO_BENCHMARK_RESULT, "w")
    for simulation_result in simulation_results:
        
    # save simulations' data in the file at the end
#----------------------------------------------------------------------------------------------------------------