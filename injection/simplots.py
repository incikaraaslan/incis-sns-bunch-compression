"""Inject particles and visualize longitudinal phase space distribution."""
import argparse
import math
import os
import pathlib

import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange
import scipy.interpolate
import xarray as xr
from omegaconf import OmegaConf
from omegaconf import DictConfig
from scipy.constants import speed_of_light

from orbit.core.bunch import Bunch
from orbit.teapot import TEAPOT_Ring
from orbit.utils.consts import mass_proton
from orbit.lattice import AccNode
from orbit.lattice import AccLattice
from tools.plotting import set_mpl_style
from tools.utils import coords_to_edges
from tools.utils import edges_to_coords
from tools.utils import get_relativistic_factors

# sns-ring-model
from sns_ring_model import SNS_RING

# pyorbit-tools
from orbit_tools.diag import BunchHistogram2D

# local
from injection import make_inj_dist_x_joho
from injection import make_inj_dist_y_joho
from injection import make_inj_dist_z_sns_espread

set_mpl_style()

# Setup
parser = argparse.ArgumentParser()
parser.add_argument("--experiment", type=str, default="exp01")
parser.add_argument("--case", type=str, default="")
parser.add_argument("--macros-per-turn", type=int, default=3000, help="macros per turn")
parser.add_argument("--energy", type=float, default=1.300, help="kinetic energy [GeV]")
parser.add_argument("--rf-voltage1", type=float, default=0.0, help="h=1 rf voltage1 [kV]")
parser.add_argument("--rf-voltage2", type=float, default=0.0, help="h=1 rf voltage2 [kV]")
parser.add_argument("--turns", type=int, default=1000, help="number of turns to track")
parser.add_argument("--turn-step", type=int, default=50, help="number of turns to plot in waterfall")
parser.add_argument("--turn-start", type=int, default=0)
parser.add_argument("--offset", type=float, default=0.000, help = "energy offset due to off-energy injected beam")

# Make the energy spread configurable during runtime #
parser.add_argument("--energy-spread", type=float, default=0.0005, help="Energy spread standard deviation [GeV]")
parser.add_argument("--pulse-width", type=float, default=(36.0 / 64.0), help="Normalized pulse width")
parser.add_argument("--inject-turns", type=int, default=300, help="Number of turns to inject particles")


args = parser.parse_args()

# EXPERIMENT
# --------------------------------------------------------------------------------------
# Create output directory
path = pathlib.Path(__file__)
output_dir = os.path.join("../2025-02-16/analysis/outputs", path.stem, args.experiment)
os.makedirs(output_dir, exist_ok=True)

# Load experiment parameters
cfg = OmegaConf.load("../2025-02-16/analysis/config.yml")
print(OmegaConf.to_yaml(cfg))

# Load data
filename = os.path.join("../2025-02-16/analysis/outputs/00_proc_ring_bcm", args.experiment, args.case, "profiles.nc")
profiles = xr.open_dataarray(filename)

# SIMULATION
# --------------------------------------------------------------------------------------
# Create empty bunch
bunch = Bunch()
bunch.mass(mass_proton)
bunch.getSyncParticle().kinEnergy(args.energy)
bunch.macroSize(1.5e11/args.macros_per_turn)


# Create lattice
model = SNS_RING(
    lattice_file="inputs/sns_ring.lat",
    lattice_file_type="madx",
    lattice_seq="rnginj",
)
model.initialize()
model.set_bunch(bunch)

# Add rf cavity node
model.add_rf_cavity_nodes(
    voltage_1=(args.rf_voltage1 * 1.00e-06),
    voltage_2=(args.rf_voltage2 * 1.00e-06), # If both are turned on, take half of each
    voltage_3=0.0,
    voltage_4=0.0,
    hnum_1=1.0,
    hnum_2=1.0,
    hnum_3=2.0,
    hnum_4=2.0,
)
lattice = model.lattice

# Add injection node
inj_dist_x = make_inj_dist_x_joho()
inj_dist_y = make_inj_dist_y_joho()
inj_dist_z = inj_dist_z = make_inj_dist_z_sns_espread(
    bunch=bunch,
    lattice=lattice,
    esigma=args.energy_spread,
    zlim=args.pulse_width
)
inj_node = model.add_inj_node(
    dist_x=inj_dist_x,
    dist_y=inj_dist_y,
    dist_z=inj_dist_z,
    nparts=args.macros_per_turn
)


# Create histogram diagnostic. This diagnostic computes the histogram along 
    # a 2D axis using built-in binning routines (C++, fast). There is some
    # smoothing applied so it's not an exact histogram.
histo = BunchHistogram2D(
    axis=(4, 5),
    shape=(100, 100),
    limits=[
        (-0.5 * lattice.getLength(), 0.5 * lattice.getLength()),
        (-0.015, 0.015),
    ],
)

stored_z_vals = []

# Track bunch
for turn in trange(args.turns + 1):       # args.turns + 1
    lattice.trackBunch(bunch)

    # Stop injection after user-specified number of turns
    if turn == args.inject_turns:
        inj_node.setnParts(0)  # Remove injection node from the lattice
    
    if turn % args.turn_step == 0:
        # SIMULATION
        histo.track(bunch)
        coords = histo.coords
        values = histo.values.copy()
        values = np.ma.masked_less_equal(values, 0.0)
        
        # Extract phase space variables
        z_vals = [bunch.z(i) for i in range(bunch.getSize())]
        stored_z_vals.append([z_vals])  # Append to cumulative storage

# Turn by Turn Plot
for idx, z_data in enumerate(stored_z_vals):
    fig, ax = plt.subplots(figsize=(3.0, 5.0))
    turn = idx * 50

    # SIMULATION
    hist, bin_edges = np.histogram(z_data, bins=70, range=(-0.5 * lattice.getLength(), 0.5 * lattice.getLength()))
    coords_sim = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # Bin centers

    # Normalize Simulation Values
    hist_sum = np.sum(hist)
    if hist_sum > 0.0:
        hist = hist / hist_sum  # Normalize total sum to 1
    hist = hist / (coords_sim[1] - coords_sim[0])  # Normalize by bin width
    
    """ax.plot(bin_edges[:-1], hist, color="red", linestyle='dashed', alpha=1.0)
    ax.set_xlim(-0.5 * lattice.getLength(), 0.5 * lattice.getLength())
    ax.set_yticklabels([])
    ax.annotate(f"Turn={turn}", xy=(0.02, 0.92), xycoords="axes fraction")
    ax.set_ylabel(r"Turn $\rightarrow$")
    ax.set_xlabel("z [m]")
    """
    # EXPERIMENT
    # --------------------------------------------------------------------------------------
    exp_values = profiles[turn].copy()
    coords = profiles.coords["z"]
    edges = coords_to_edges(coords)
    
    # Normalize Experimental Values
    exp_values_sum = np.sum(exp_values)
    if exp_values_sum > 0.0:
        exp_values = exp_values / exp_values_sum
    exp_values = exp_values / (coords[1] - coords[0])
    
    # === CENTER ALIGNMENT ===
    def find_center(z, intensity):
        return np.sum(z * intensity) / np.sum(intensity)

    center_exp = find_center(np.asarray(coords), np.asarray(exp_values))
    center_sim = find_center(np.asarray(coords_sim), np.asarray(hist))
    shift = center_exp - center_sim
    coords_sim_shifted = coords_sim + shift

    # === PLOT ===
    ax.plot(coords_sim_shifted, hist, color="red", linestyle='dashed', alpha=1.0, label="Simulation (aligned)")
    ax.plot(coords, exp_values, color="black", alpha=1.0, label="Experiment")

    ax.set_xlim(-0.5 * lattice.getLength(), 0.5 * lattice.getLength())
    ax.set_yticklabels([])
    ax.annotate(f"Turn={turn}", xy=(0.02, 0.92), xycoords="axes fraction")
    ax.set_ylabel("Probability Density (arbitrary units)")
    ax.set_xlabel("z [m]")
    ax.legend(loc="upper right", fontsize="x-small")
    
    """ax.plot(coords, exp_values, color="black", alpha=1.0)"""
    plt.savefig(f"./outputs/simout/aligned_fig_{args.experiment}_{args.case}_turn_profile_{turn}_macros_{args.macros_per_turn}_energy_{args.energy}_bins_70.png")
    print(f"Done {turn:04.0f}")
    plt.close()