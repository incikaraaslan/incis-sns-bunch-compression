"""Inject particles and visualize longitudinal phase space distribution."""
import argparse
import os

import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange

from orbit.core.bunch import Bunch
from orbit.teapot import TEAPOT_Ring
from orbit.utils.consts import mass_proton
from orbit.lattice import AccNode
from orbit.lattice import AccLattice

# sns-ring-model
from sns_ring_model import SNS_RING

# pyorbit-tools
from orbit_tools.diag import BunchHistogram2D

# local
from injection import make_inj_dist_x_joho
from injection import make_inj_dist_y_joho
from injection import make_inj_dist_z_sns_espread


# Setup
parser = argparse.ArgumentParser()
parser.add_argument("--macros-per-turn", type=int, default=10, help="macros per turn")
parser.add_argument("--energy", type=float, default=1.300, help="kinetic energy [GeV]")
parser.add_argument("--rf-voltage1", type=float, default=0.0, help="h=1 rf voltage1 [kV]")
parser.add_argument("--rf-voltage2", type=float, default=0.0, help="h=1 rf voltage2 [kV]")
parser.add_argument("--turns", type=int, default=1000, help="number of turns to track")

# Make the energy spread configurable during runtime #
parser.add_argument("--energy-spread", type=float, default=0.0005, help="Energy spread standard deviation [GeV]")
parser.add_argument("--pulse-width", type=float, default=(35.0 / 64.0), help="Normalized pulse width")
parser.add_argument("--inject-turns", type=int, default=1000, help="Number of turns to inject particles")


args = parser.parse_args()

# If turns were not provided as a command-line argument, ask the user
"""if args.turns is None:
    args.turns = int(input("Enter the number of turns to track: "))
if args.rf_voltage is None:
    args.rf_voltage = int(input("h=1 RF on Voltage (in kV): "))
"""
# Create empty bunch
bunch = Bunch()
bunch.mass(mass_proton)
bunch.getSyncParticle().kinEnergy(args.energy)
bunch.macroSize(1.0)


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
for turn in trange(args.turns + 1):       
    lattice.trackBunch(bunch)

    # Stop injection after user-specified number of turns
    if turn == args.inject_turns:
        inj_node.setnParts(0)  # Remove injection node from the lattice
    
    if turn % 100 == 0:
        histo.track(bunch)
        coords = histo.coords
        values = histo.values.copy()
        values = np.ma.masked_less_equal(values, 0.0)
        
        # Extract phase space variables
        z_vals = [bunch.z(i) for i in range(bunch.getSize())]
        stored_z_vals.append([z_vals])  # Append to cumulative storage
        de_vals = [bunch.dE(i) for i in range(bunch.getSize())]
        
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        m = ax[0].pcolormesh(coords[0], coords[1], values.T, cmap="Blues")
        fig.colorbar(m, ax=ax[0])
        
        # Fig 1: Phase Space Plot with Histogram
        ax[0].scatter(z_vals, de_vals, s=1, alpha=0.5)
        ax[0].set_xlabel("z [m]")
        ax[0].set_ylabel("ΔE [GeV]")
        ax[0].set_title(f"Longitudinal Phase Space (Turn {turn})")
        
        ax[1].hist(de_vals, bins=50, alpha=0.7, color='b', edgecolor='black') # Histogram of ΔE
        ax[1].set_xlabel("ΔE [GeV]")
        ax[1].set_ylabel("Count")
        ax[1].set_title(f"Energy Spread Histogram (Turn {turn})")
        
        plt.savefig(f"./outputs/simout/Exp02_3-bunch_{turn:04.0f}.jpg")
        plt.close()
        
        # Fig 0: Individual Profile Plots
        fig, ax = plt.subplots(figsize=(5.0, 2.5))
        ax.hist(z_vals, bins=100, color="black", alpha=0.7, edgecolor='black')
        ax.set_xlabel("z [m]")
        ax.set_ylabel("Particle Count")
        ax.set_xlim(-0.5 * lattice.getLength(), 0.5 * lattice.getLength())
        ax.annotate(f"Turn={turn:04.0f}", xy=(0.02, 0.92), xycoords="axes fraction")
        plt.savefig(f"./outputs/simout/Exp02_3_profile_{turn:04.0f}.png")
        plt.close()

# Fig 2: Waterfall Plot
turn_stride = 100
offset_scale = 6.0
fig, ax = plt.subplots(figsize=(3.0, 5.0))

for idx, z_data in enumerate(stored_z_vals):
    hist, bin_edges = np.histogram(z_data, bins=100, range=(-0.5 * lattice.getLength(), 0.5 * lattice.getLength()))
    """hist = hist / np.max(hist)  # Normalize
    offset = (turn / args.turns) * np.max(hist) * offset_scale"""
    hist_sum = np.sum(hist)
    if hist_sum > 0.0:
        hist = hist / hist_sum  # Normalize total sum to 1
    offset = idx * np.max(hist) * 6.0  
    ax.plot(bin_edges[:-1], hist + offset, color="black", alpha=1.0)

"""ax.set_xlim(-0.5 * lattice.getLength(), 0.5 * lattice.getLength())
ax.set_yticklabels([])
ax.set_ylabel(r"Turn $\rightarrow$")
ax.set_xlabel("z [m]")
plt.savefig("./outputs/simout/Exp02_3_profiles_waterfall.png")
plt.close()
"""
"""# Fig 3: Heatmap Plot
fig, ax = plt.subplots(figsize=(7.0, 5.0))
values_list = []
turn_list = []
z_edges = np.linspace(-0.5 * lattice.getLength(), 0.5 * lattice.getLength(), 100)



hist, _ = np.histogram(z_vals, bins=z_edges)
values_list.append(hist)
turn_list.append(turn)

values_array = np.array(values_list)
m = ax.pcolormesh(z_edges[:-1], turn_list, values_array, shading="auto")
fig.colorbar(m)
ax.set_xlabel("z [m]")
ax.set_ylabel("Turn")
plt.savefig("./outputs/simout/Exp0a2_2_profiles_waterfall_pcolor.png")
plt.close()"""