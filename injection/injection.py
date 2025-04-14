import math
from typing import Any
from typing import Callable

import numpy as np

from orbit.core.bunch import Bunch
from orbit.injection import TeapotInjectionNode
from orbit.injection import JohoTransverse
from orbit.injection import JohoLongitudinal
from orbit.injection import SNSESpreadDist
from orbit.lattice import AccNode
from orbit.lattice import AccLattice
from orbit.utils.consts import speed_of_light


def make_inj_dist_x_joho(
    order: float = 9.0,
    alpha: float = 0.064,
    beta: float = 10.056,
    eps: float = 0.221 * 1.0e-6,
    centerpos: float = 0.0486,
    centermom: float = 0.0,
) -> JohoTransverse:
    emitlim = eps * 2.0 * (order + 1.0)
    dist = JohoTransverse(order, alpha, beta, emitlim, centerpos, centermom)
    return dist
    

def make_inj_dist_y_joho(
    order: float = 9.0,
    alpha: float = 0.063,
    beta: float = 10.815,
    eps: float = 0.221 * 1.0e-6,
    centerpos: float = 0.046,
    centermom: float = 0.0,
) -> JohoTransverse:
    emitlim = eps * 2.0 * (order + 1.0)
    dist = JohoTransverse(order, alpha, beta, emitlim, centerpos, centermom)
    return dist


def make_inj_dist_z_sns_espread(
    bunch: Bunch,
    lattice: AccLattice,
    zlim: float = (35.0 / 64.0),
    tailfraction: float = 0.0,

    esigma: float = 0.0005,
    etrunc: float = 1.0,
    emin: float = -0.0025,
    emax: float = +0.0025,

    ecmean: float = 0.0,
    ecsigma: float = 0.000000001,
    ectrunc: float = 1.0,
    ecmin: float = -0.0035,
    ecmax: float = +0.0035,
    ecdrifti: float = 0.0,
    ecdriftf: float = 0.0,
    
    esnu: float = 100.0,
    esphase: float = 0.0,
    esmax: float = 0.0, 
) -> SNSESpreadDist:

    zlim = np.multiply(zlim, 0.5 * lattice.getLength())
    zmin = -zlim
    zmax = +zlim

    sync_part = bunch.getSyncParticle()
    emean = sync_part.kinEnergy()
    emin += sync_part.kinEnergy()
    emax += sync_part.kinEnergy()

    tturn = lattice.getLength() / (sync_part.beta() * speed_of_light)

    drifttime = 1000.0 * (1000) * tturn
    ecparams = (ecmean, ecsigma, ectrunc, ecmin, ecmax, ecdrifti, ecdriftf, drifttime)
    nulltime = 0.0
    esparams = (esnu, esphase, esmax, nulltime)

    dist = SNSESpreadDist(
        lattice.getLength(),
        zmin,
        zmax,
        tailfraction,
        sync_part,
        emean,
        esigma,
        etrunc,
        emin,
        emax,
        ecparams,
        esparams,
    )
    return dist


def make_inj_node(
    bunch: Bunch,
    dist_x: Any,
    dist_y: Any,
    dist_z: Any,
    nparts: int,
    x: float = 0.0486,
    y: float = 0.0460,
    xp: float = 0.000,
    yp: float = 0.000,
) -> AccNode:    
    xmin = x - 0.005
    xmax = x + 0.014722
    ymin = y - 0.005
    ymax = y + 0.020
    limits = (xmin, xmax, ymin, ymax)

    lostbunch = Bunch()
    
    inj_node = TeapotInjectionNode(nparts, bunch, lostbunch, limits, dist_x, dist_y, dist_z)
    return inj_node