from typing import Tuple

import numpy as np
from sdt.sim import simulate_gauss
from skimage import util
from tifffile import imwrite
from tqdm import tqdm


def generate_images(
    tracks: np.ndarray, window: Tuple[int, int] = (512, 512)
) -> np.ndarray:
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
        frame = util.invert(generate_frame(tracks[:, :, i], window))
        stack.append(frame)
    return np.asarray(stack)


def generate_tracks(
    n_particles: int = 100,
    steps: int = 1000,
    tau: float = 0.01,
    drift: Tuple[float, float] = (0.1, 0.1),
    window: Tuple[int, int] = (512, 512),
    pixel_size: float = 1e-7,
    D: float = None,
) -> np.ndarray:
    """Generate tracks of particles undergoing 2D Brownian motion

    Parameters
    ----------
    n_particles : int, optional
        number of particles, by default 100
    steps : int, optional
        number of time points to be simulated, by default 1000
    tau : float, optional
        time between steps in seconds, by default 0.01
    drift : Tuple[float, float], optional
        drift in x and y direction in fraction of step size, by default (-0.1, -0.1)
    window : Tuple[int, int], optional
        size of the simulated image in pixels, by default (512, 512)
    pixel_size : float, optional
        size of the pixel in meters, by default 1e-7
    D : float
        diffusion coefficient

    Returns
    -------
    np.array
        3D array with particle tracks with shape (n_particles, dimensions, time points)
    """

    k = np.sqrt(2 * D * tau)

    x = k * (np.random.randn(n_particles, steps - 1) + drift[0]) / pixel_size
    y = k * (np.random.randn(n_particles, steps - 1) + drift[1]) / pixel_size
    z = np.array([x, y]).swapaxes(0, 1)

    # Extend window size to create particles outside of the window to account for drift
    window_extended = tuple(np.round(x * 2) for x in window)
    coords = np.array(
        [
            np.random.uniform(-window_extended[0], window_extended[0], n_particles),
            np.random.uniform(-window_extended[0], window_extended[1], n_particles),
        ]
    ).T

    return np.dstack((coords, z)).cumsum(axis=2)


def generate_frame(
    coords: np.ndarray, window: Tuple[int, int] = (512, 512)
) -> np.ndarray:
    """Create microscopy image from tracks at single timepoint

    Parameters
    ----------
    coords : np.array
        coordinates of particles
    window : Tuple[int, int], optional
        size of the simulated image in pixels, by default (512, 512)

    Returns
    -------
    np.array
        2D array of microscope image with particles
    """
    amplitudes = 1000  # amplitude of the PSF
    sigmas = 2  # sigma of the amplitude
    img = simulate_gauss(window, coords, amplitudes, sigmas)
    img_noisy = np.array(np.random.poisson(img), dtype="float16")  # add shot noise
    img_noisy += np.random.normal(200, 20, img_noisy.shape)  # add camera noise
    return img_noisy


def get_diffusion_coefficient(
    particle_size: float = 1e-6, eta: float = 1e-3, T: float = 293
) -> float:
    """Calculate diffusion coefficient

    Parameters
    ----------
    particle_size : float
        size of the particles in meters, defaults to 1e-6
    eta : float
        viscosity of the medium in Pascal-seconds, defaults to 1e-3
    T : float
        temperature in Kelvin, defaults to 293

    Returns
    -------
    float
        diffusion coefficient
    """
    kB = 1.38e-23  # Boltzmann constant
    return kB * T / (3 * np.pi * eta * particle_size)


def save_stack(file_path: str, stack: np.ndarray):
    """Save image stack

    Parameters
    ----------
    stack : np.array
        3D array of simulated microscopy images
    file_path : str, optional
        path to save file"
    """
    imwrite(file_path, stack)


if __name__ == "__main__":
    print("Generating images...")
    D = get_diffusion_coefficient()
    tracks = generate_tracks(n_particles=1000, steps=5000, drift=(0.0, 0.0), D=D)
    stack = generate_images(tracks)
    print("Saving image stack...")
    save_stack("./data/sim_diffusion.tif", stack)
    print("Done!")
