"""Plot longitudinal profiles.

Usage:
    python 03_plot_ring_llrf.py --experiment=exp01
"""

import argparse
import math
import os
import pathlib
import pickle
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np

from tools.plotting import set_mpl_style


# Setup
# --------------------------------------------------------------------------------------

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--experiment", type=str)
args = parser.parse_args()

# Create output directory
path = pathlib.Path(__file__)
output_dir = os.path.join("outputs", path.stem, args.experiment)
os.makedirs(output_dir, exist_ok=True)

# Plot settings
set_mpl_style()


# Load data
# --------------------------------------------------------------------------------------

filename = os.path.join("outputs/01_proc_ring_llrf", args.experiment, "data.pkl")
print(filename)

file = open(filename, "rb")
data = pickle.load(file)


# Plot
# --------------------------------------------------------------------------------------

fig, axs = plt.subplots(ncols=4, nrows=2, figsize=(10.0, 4.0), constrained_layout=True)

for j, cav_name in enumerate(data):
    signal_amp = data[cav_name]["amp"]
    signal_phi = data[cav_name]["phase"]
    axs[0, j].plot(signal_amp)
    axs[1, j].plot(signal_phi)
    axs[0, j].set_title(cav_name)
    for ax in axs[:, j]:
        ax.set_xlabel("Turn")
axs[0, 0].set_ylabel("Amplitude [kV]")
axs[1, 0].set_ylabel("Phase [deg]")

filename = "fig_ring_llrf.png"
filename = os.path.join(output_dir, filename)
print(filename)

fig.savefig(filename, dpi=300)
plt.close("all")

