import glob
import os
from subprocess import call

# This script takes care of loading all the py files inside the root directory (the main directory in which 
# this py script resides), and it loads every one of them (excluding this py script) in order to execute them
# Every python script inside the folder must be a "task", that is it should have the structure of the task.py
# template script, which uses the PyRTOS library to run as a RTOS script

# Delete all the .terminate files in this folder, so every task can be started if it was previously shutdown
ter_list = glob.glob("*.terminate")
for ter_item in ter_list:
    os.remove(ter_item)


# Get a list of all python files in the current directory, excluding current python file
pylist = glob.glob("*.py")
this_file = os.path.basename(__file__)
pylist.remove(this_file)


# Execute each python file in the list
for pyscript in pylist:
    call(["python", pyscript])
