"""Process LLRF data.

Usage:
    python 01_proc_ring_llrf --experiment=exp01
"""
import argparse
import numpy as np
import os
import pathlib
import pickle
from pprint import pprint


# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--experiment", type=str)
parser.add_argument("--tstart", type=float, default=0)
parser.add_argument("--tstop", type=float, default=1300)
args = parser.parse_args()

# Create output directory
path = pathlib.Path(__file__)
experiment = args.experiment
output_dir = os.path.join("outputs", path.stem, experiment)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Collect filenames
def get_filename(cav_name: str, signal_name: str) -> np.ndarray:
    filename = f"Ring_LLRFuTCA:{cav_name}:Field_Wfs.{signal_name}.dat"
    return filename

input_dir = "../data"
input_dir = os.path.join(input_dir, args.experiment)
input_dir = os.path.join(input_dir, "ring-llrf")
filenames = os.listdir(input_dir)

# Save pickled
data = {}
for cav_name in ["Cav1", "Cav2", "Cav3", "Cav4"]:
    data[cav_name] = {}
    for key, signal_name in zip(["amp", "phase"], ["VALA", "VALB"]):
        filename = get_filename(cav_name, signal_name)
        filename = os.path.join(input_dir, filename)
        print(filename)
        
        signal = np.loadtxt(filename)
        signal = signal[args.tstart: args.tstop + 1]
        data[cav_name][key] = signal
        
filename = os.path.join(output_dir, "data.pkl")
file = open(filename, "wb")
pickle.dump(data, file)
file.close()

print(filename)




