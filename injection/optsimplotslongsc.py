"""Inject particles and visualize longitudinal phase space distribution."""
import argparse
import math
import os
import pathlib

import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange
import scipy.interpolate
from scipy.optimize import minimize
from scipy.stats import wasserstein_distance
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
parser.add_argument("--turn-step", type=int, default=100, help="number of turns to plot in waterfall")
parser.add_argument("--turn-start", type=int, default=0)

# Make the energy spread configurable during runtime #
parser.add_argument("--pulse-width", type=float, default=(36.0 / 64.0), help="Normalized pulse width")
parser.add_argument("--inject-turns", type=int, default=300, help="Number of turns to inject particles")

# Optimization Parameters
parser.add_argument("--method", type=str, default="l2", help="Optimization Loss Function Method")
parser.add_argument("--energy-spread", type=float, default=0.001, help="Energy spread standard deviation [GeV]")

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

def simulate_z_profile_for_energy_spread(energy_spread=args.energy_spread):
    """
    Run the SNS ring simulation using the given energy spread and return
    longitudinal z-profiles at each selected turn (for comparison).
    
    Returns:
        sim_profiles: turn number -> profile (np.ndarray of shape [64])
    """
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
        n_bins=64,
        position=124.0,  # or whatever longitudinal position you'd like in meters
        impedance=None   # defaults to zero impedance
    )

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
        esigma=energy_spread,
        zlim=args.pulse_width
    )
    inj_node = model.add_inj_node(
        dist_x=inj_dist_x,
        dist_y=inj_dist_y,
        dist_z=inj_dist_z,
        nparts=args.macros_per_turn
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
            # Extract phase space variables
            z_vals = [bunch.z(i) for i in range(bunch.getSize())]
            stored_z_vals.append([z_vals])
    
    return lattice, stored_z_vals

def compute_loss(energy_spread, method=args.method):
    """
    Compute cumulative distance (loss) between experiment and simulation profiles
    across all turns. Supports 'l2' or 'wasserstein' (Earth Mover’s Distance).
    """
    lattice, stored_z_vals = simulate_z_profile_for_energy_spread(energy_spread)
    loss = 0.0
    
    for idx, z_data in enumerate(stored_z_vals):
        turn = idx * 50
        
        # SIMULATION
        # Draw Histogram
        hist, bin_edges = np.histogram(z_data, bins=64, range=(-0.5 * lattice.getLength(), 0.5 * lattice.getLength()))
        coords_sim = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # Bin centers
        hist = hist.astype(np.float64)
        
        # Normalize Simulation Values
        hist_sum = np.sum(hist)
        if hist_sum > 0.0:
            hist = hist / hist_sum  # Normalize total sum to 1
        hist = hist / (coords_sim[1] - coords_sim[0])  # Normalize by bin width
        
        # EXPERIMENT
        exp_values = profiles[turn].copy()
        coords = profiles.coords["z"]

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
        # Interpolate sim_profile onto experiment z-axis
        sim_interp = np.interp(coords, coords_sim_shifted, np.asarray(hist), left=0, right=0)
        
        # Distance metric
        if method == "wasserstein":
            d = wasserstein_distance(coords, coords, sim_interp, exp_values)
        elif method == "l2":
            d = np.sqrt(np.mean((sim_interp - exp_values) ** 2))
        else:
            raise ValueError(f"Unknown distance method: {method}")
        
        loss += d

    return loss



result = minimize(
    lambda x: compute_loss(x[0], method=args.method),  # or "l2"
    x0=[args.energy_spread],
    bounds=[(0.0001, 0.01)],
    method="L-BFGS-B",
)

print("Optimal energy spread:", result)
