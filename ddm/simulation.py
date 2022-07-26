import numpy as np
from tifffile import imwrite
from skimage import util
from sdt.sim import simulate_gauss
from typing import Tuple
from tqdm import tqdm


def generate_stack(tracks: np.array) -> np.array:
    """Create an image stack of simulated microscopy images

    Parameters
    ----------
    tracks : np.array
        3D array with particle tracks with shape (n_particles, 2, time points)

    Returns
    -------
    np.array
        3D array of simulated microscopy images
    """
    stack = []
    for i in tqdm(range(tracks.shape[-1])):
        frame = util.invert(generate_frame(tracks[:, :, i]))
        stack.append(frame)
    return np.asarray(stack)


def generate_tracks(
    n_particles: int = 100,
    steps: int = 1000,
    tau: float = 0.01,
    drift: Tuple[float, float] = (-0.1, -0.1),
    window: Tuple[int, int] = (512, 512),
    pixel_size: float = 1e-7,
) -> np.array:
    """Generate tracks of particles undergoing 2D Brownian motion

    Parameters
    ----------
    n_particles : int, optional
        number of particles, by default 100
    steps : int, optional
        number of time points to be simulated, by default 1000
    tau : float, optional
        time between steps, by default 0.01 [in seconds]
    drift : Tuple[float, float], optional
        drift in x and y direction, by default (-0.1, -0.1) [fraction of step size]
    window : Tuple[int, int], optional
        size of the simulated image, by default (512, 512) [in pixels]
    pixel_size : float, optional
        size of the pixel, by default 1e-7 [in meters]

    Returns
    -------
    np.array
        3D array with particle tracks with shape (n_particles, dimensions, time points)
    """
    D = get_diffusion_coefficient()
    k = np.sqrt(2 * D * tau)

    x = k * (np.random.randn(n_particles, steps - 1) + drift[0]) / pixel_size
    y = k * (np.random.randn(n_particles, steps - 1) + drift[1]) / pixel_size
    z = np.array([x, y]).swapaxes(0, 1)

    # Extend window size to create particles outside of the window to account for drift
    window_extended = tuple(np.round(x * 2) for x in window)
    coords = np.array(
        [
            np.random.uniform(0, window_extended[0], n_particles),
            np.random.uniform(0, window_extended[1], n_particles),
        ]
    ).T

    return np.dstack((coords, z)).cumsum(axis=2)


def generate_frame(coords: np.array, window: Tuple[int, int] = (512, 512)) -> np.array:
    """Create microscopy image from tracks at single timepoint

    Parameters
    ----------
    coords : np.array
        coordinates of particles
    window : Tuple[int, int], optional
        size of the simulated image, by default (512, 512) [in pixels]

    Returns
    -------
    np.array
        2D array of microscope image with particles
    """
    amplitudes = 500
    sigmas = 5
    img = simulate_gauss(window, coords, amplitudes, sigmas)
    img_noisy = np.array(np.random.poisson(img), dtype="float16")  # add shot noise
    img_noisy += np.random.normal(200, 20, img_noisy.shape)  # add camera noise
    return img_noisy


def get_diffusion_coefficient():
    """Calculate diffusion coefficient

    Returns
    -------
    float
        diffusion coefficient
    """
    particle_size = 1e-6  # in meter
    eta = 1e-3  # viscosity (Pascal-seconds)
    kB = 1.38e-23  # Boltzmann constant
    T = 293  # in Kelvin
    D = kB * T / (3 * np.pi * eta * particle_size)  # Diffusion coefficient
    return D


def save_stack(stack: np.array, path: str = "diffusion.tif"):
    """Save image stack

    Parameters
    ----------
    stack : np.array
        3D array of simulated microscopy images
    path : str, optional
        path to save file, by default "diffusion.tif"
    """
    imwrite(path, stack)


if __name__ == "__main__":
    print("Loading simulation settings from ddm/sim_config.yml")

    print("Generating images...")
    tracks = generate_tracks()
    stack = generate_stack(tracks)
    print("Saving image stack...")
    save_stack(stack)
    print("Done!")
