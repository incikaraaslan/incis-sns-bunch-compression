"""Plot longitudinal profiles.

Usage:
    python 02_plot_profiles.py --experiment=exp01
"""

import argparse
import math
import os
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate
import xarray as xr
from omegaconf import OmegaConf
from omegaconf import DictConfig
from scipy.constants import speed_of_light

from tools.plotting import set_mpl_style
from tools.utils import coords_to_edges
from tools.utils import edges_to_coords
from tools.utils import get_relativistic_factors


set_mpl_style()


# Setup
# --------------------------------------------------------------------------------------

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--experiment", type=str)
parser.add_argument("--turn-start", type=int, default=100)
parser.add_argument("--turn-step", type=int, default=50)
parser.add_argument("--offset-scale", type=float, default=4.0)
args = parser.parse_args()

# Create output directory
path = pathlib.Path(__file__)
output_dir = os.path.join("outputs", path.stem, args.experiment)
os.makedirs(output_dir, exist_ok=True)

# Load experiment parameters
cfg = OmegaConf.load("config.yml")
print(OmegaConf.to_yaml(cfg))


# Load data
# --------------------------------------------------------------------------------------

filename = os.path.join("outputs/00_proc_ring_bcm", args.experiment, "profiles.nc")
profiles = xr.open_dataarray(filename)


# Plot individual profiles
# --------------------------------------------------------------------------------------

for turn in range(args.turn_start, len(profiles), args.turn_step):
    values = profiles[turn].copy()
    coords = profiles.coords["z"]
    edges = coords_to_edges(coords)

    fig, ax = plt.subplots(figsize=(5.0, 2.5))
    ax.stairs(values, edges, color="black", lw=1.5, fill=True)
    ax.set_xlabel("z [m]")
    ax.set_ylabel("BCM")
    ax.set_xlim(-0.5 * cfg.ring.length, 0.5 * cfg.ring.length)
    ax.set_ylim(0.0, np.max(profiles) * 1.1)
    ax.annotate(f"Turn={turn:04.0f}", xy=(0.02, 0.92), xycoords="axes fraction")

    filename = os.path.join(output_dir, f"fig_profile_{turn:04.0f}")
    print(filename)
    plt.savefig(filename)
    plt.close("all")


# Plot waterfall
# --------------------------------------------------------------------------------------

turns = np.arange(args.turn_start, len(profiles), args.turn_step)
coords = np.copy(profiles.coords["z"])

profiles_sub = np.copy(profiles[turns, :])
for i, values in enumerate(profiles_sub):
    values_sum = np.sum(values)
    if values_sum > 0.0:
        values = values / values_sum
    print(coords)
    values = values / (coords[1] - coords[0])
    profiles_sub[i] = np.copy(values)

fig, ax = plt.subplots(figsize=(2.5, 3.0))
for turn, values in zip(turns, profiles_sub):
    frac = turn / turns[-1]
    offset = frac * np.max(profiles_sub) * args.offset_scale
    ax.plot(coords, values + offset, color="black", alpha=1.0)

"""ax.set_xlim(-124.0, 124.0)
ax.set_yticklabels([])
ax.set_ylabel(r"Time $\rightarrow$")
ax.set_xlabel("z [m]")

filename = os.path.join(output_dir, "fig_profiles_waterfall")
print(filename)
plt.savefig(filename)
plt.close("all")


# Plot waterfall heatmap
# --------------------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(4.0, 3.0))
values = profiles.data.T
coords = [profiles.coords["z"], profiles.coords["turn"]]
m = ax.pcolormesh(coords[0], coords[1], values.T, shading="auto")
fig.colorbar(m)
ax.set_xlabel("z [m]")
ax.set_ylabel("Turn")

filename = os.path.join(output_dir, "fig_profiles_waterfall_pcolor")
print(filename)
plt.savefig(filename)
plt.close("all")"""
