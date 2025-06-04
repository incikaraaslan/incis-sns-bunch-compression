import numpy as np


def load_bcm_waveform(filename: str, samp_step: float) -> np.ndarray:
    f = np.loadtxt(filename)
    t = np.arange(len(f)) * samp_step
    return np.stack([t, f], axis=-1)


def interpolate_bcm_waveform(waveform: np.ndarray, t_start: float, t_step: float) -> np.ndarray:
    t = waveform[:, 0]
    f = waveform[:, 1]

    t_new = np.arange(t_start, t[-1] + t_step, t_step)
    f_new = np.interp(t_new, t, f)

    t_new = t_new - t_new[0]
    
    return np.stack([t_new, f_new], axis=-1)

