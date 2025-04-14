import math
import numpy as np


def edges_to_coords(edges: np.ndarray) -> np.ndarray:
    return 0.5 * (edges[:-1] + edges[1:])


def coords_to_edges(coords: np.ndarray) -> np.ndarray:
    delta = coords[1] - coords[0]
    return np.hstack([coords - 0.5 * delta, [coords[-1] + 0.5 * delta]])


def get_relativistic_factors(kin_energy: float, mass: float) -> tuple[float, float]:
    gamma = 1.0 + (kin_energy / mass)
    beta = math.sqrt(gamma**2 - 1.0) / gamma
    return (gamma, beta)