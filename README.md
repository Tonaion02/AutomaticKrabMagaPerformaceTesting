<center> <h1>Automatic performance testing for KrABMaga</h1> </center>

This repository contains all the necessary to execute performance testing with Tracy profiler for a simulation written with KrABMaga.

<h2>Project structure</h2>

The principal files of this project are:
- **main.py**: where there is code source
- **input.txt**: where there are parameters for each simulation

<h2>How to use</h2>

To run performance test simulation:

```
python main.py 
```

The results of the simulation is written in the file benchmark_result.csv in the folder under PATH_TO_DEST_FOLDER.

There are some some optional parameters for this program:
- **PATH_TO_DEST_FOLDER**: path to the folder in which we save the benchmarks and other files
- **PATH_TO_SIMULATION_FOLDER**: path to simulation's folder where is the simulation code that we want to test
- **PATH_TO_TRACY_FOLDER**: path to tracy's folder(the capture, not the profiler with gui)
- **NUM_STEPS**: number of steps for simulation
- **NUM_RUN**: number of run for each simulation

**NOTE**: The order in which the optional parameters are defined is not important.

Example:

```
python main.py PATH_TO_DEST_FOLDER=C:/Dest NUM_STEPS=200 NUM_RUN=10
```

<h3>How to set other parameters</h3>
There are also other parameters that we can set for this tester. For example, we can set the zones' name for which we want to extract and save information.
Unfortunately for now we can only set these parameters from the code.