# Installation

Step 1: create a conda environment named "carla37" with python version 3.7.9 and activate it
```
conda create -n carla37 python=3.7.9
conda activate carla37
```

Step 2: clone this repo to your machine and navigate to the root folder in terminal

Step 3: Update the environment with all the necessary packages needed for this repository
```
conda env update -n carla37 --file environment.yml
```
Now you can run the experiments

# Running experiments

## Streaming
You can use the streamer.py file to stream from the spectator in a remote server. Issue this command in the terminal:
```
python streamer.py
```
It will prompt for ip and port.

## Running carla examples
Navigate to the carla examples folder from your carla installation folder. Run any experiment. The streamer should be able to show the simulation.
