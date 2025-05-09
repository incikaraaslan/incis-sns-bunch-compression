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
from orbit.rf_cavities import Harmonic_RFNode
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

# Make the energy spread configurable during runtime #
parser.add_argument("--energy-spread", type=float, default=0.001, help="Energy spread standard deviation [GeV]")
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

# Add Longitudinal space-charge node
model.add_longitudinal_spacecharge_node(
    b_over_a=(10.0 / 3.0),
    n_macros_min=1000,
    n_bins=70,
    position=124.0,  # or whatever longitudinal position you'd like in meters
    impedance=None   # defaults to zero impedance
)

# Add rf cavity node
rf_nodes = model.add_rf_cavity_nodes(
    voltage_1=(args.rf_voltage1 * 1.00e-06),
    voltage_2=(args.rf_voltage2 * 1.00e-06), # If both are turned on, take half of each
    voltage_3=0.0,
    voltage_4=0.0,
    hnum_1=1.0,
    hnum_2=1.0,
    hnum_3=2.0,
    hnum_4=2.0,
    phase_1=0.0,
    phase_2=math.pi,
    phase_3=0.0,
    phase_4=0.0,

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

def remove_rf_node(lattice, node_name):
    # Get the list of all nodes in the lattice
    nodes = lattice.getNodes()

    # Find and remove RF2 node if it exists
    new_nodes = [node for node in nodes if node.getName() != node_name]

    # Update the lattice with the new list of nodes (without RF2)
    lattice.setNodes(new_nodes)

    print("RF2 node removed from lattice.")


stored_z_vals = []
stored_de_vals = []

# Track bunch
for turn in trange(args.turns + 1):       # args.turns + 1
    lattice.trackBunch(bunch)

    # Stop injection after user-specified number of turns
    if turn == args.inject_turns:
        inj_node.setnParts(0)  # Remove injection node from the lattice
        """remove_rf_node(lattice, "RF2")"""

    
    if turn % args.turn_step == 0:
        # SIMULATION
        histo.track(bunch)
        coords = histo.coords
        values = histo.values.copy()
        values = np.ma.masked_less_equal(values, 0.0)
        
        # Extract phase space variables
        z_vals = [bunch.z(i) for i in range(bunch.getSize())]
        stored_z_vals.append([z_vals])  # Append to cumulative storage
        de_vals = [bunch.dE(i) for i in range(bunch.getSize())]
        stored_de_vals.append([de_vals])

# Turn by Turn Plot

for idx, z_data in enumerate(stored_z_vals):
    fig, ax = plt.subplots(figsize=(3.0, 5.0))
    turn = idx * 50
    # SIMULATION
    hist, bin_edges = np.histogram(z_data, bins=64, range=(-0.5 * lattice.getLength(), 0.5 * lattice.getLength()))
    coords_sim = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # Bin centers

    # Normalize Simulation Values
    hist_sum = np.sum(hist)
    if hist_sum > 0.0:
        hist = hist / hist_sum  # Normalize total sum to 1
    hist = hist / (coords_sim[1] - coords_sim[0])  # Normalize by bin width
    
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
    
    # Subtract negative offsets that weren't removed
    exp_values = np.clip(exp_values, a_min=0.0, a_max=None)
    
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
    ax.annotate(f"Turn={turn}", xy=(0.02, 0.92), xycoords="axes fraction")
    ax.set_ylabel("Probability Density [1/m]")
    ax.set_xlabel("z [m]")
    ax.legend(loc="upper right", fontsize="x-small")
    
    plt.savefig(f"./outputs/scsimsout/nosubfig_{args.experiment}_{args.case}_turn_profile_{turn:04.0f}_macros_{args.macros_per_turn}_energy_{args.energy}_spread_{args.energy_spread}_bins_64.png")
    print(f"Done {turn:04.0f}")
    plt.close()

# Turn by Turn Plot 2
"""for idx, de_data in enumerate(stored_de_vals):
    fig, ax = plt.subplots(1,2, figsize=(12.0, 5.0))
    turn = idx * 50
    z_data = stored_z_vals[idx]
    
    # SIMULATION
    # --------------------------------------------------------------------------------------
    ax[0].scatter(z_data, de_data, s=2, alpha=0.5)
    ax[0].set_xlabel("z [m]")
    ax[0].set_ylabel("ΔE [GeV]")
    ax[0].set_title(f"Simulation Longitudinal Phase Space (Turn {turn})")
    
    ax[1].hist(de_vals, bins=64, alpha=0.7, color='b', edgecolor='black') # Histogram of ΔE
    ax[1].set_xlabel("ΔE [GeV]")
    ax[1].set_ylabel("Count")
    ax[1].set_title(f"Simulation Energy Spread Histogram (Turn {turn})")
    
    plt.savefig(f"./outputs/phasesp/fig_{args.experiment}_{args.case}_turn_phase_{turn:04.0f}_macros_{args.macros_per_turn}_energy_{args.energy}_spread_{args.energy_spread}_bins_64.png")
    print(f"Done {turn:04.0f}")
    plt.close()
"""