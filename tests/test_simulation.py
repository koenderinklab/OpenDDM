import numpy as np
import pytest

from ddm.simulation import get_diffusion_coefficient, generate_tracks, generate_images


def test_default_diffusion_coefficient():
    D = get_diffusion_coefficient(particle_size=1e-6, eta=1e-3, T=293)
    assert D == pytest.approx(4.29e-13, 1e-15)


def test_generate_tracks():
    D = get_diffusion_coefficient()
    tracks = generate_tracks(
        n_particles=10,
        steps=100,
        tau=0.01,
        drift=(0.1, 0.1),
        window=(512, 512),
        pixel_size=1e-7,
        D=D,
    )
    assert isinstance(tracks, np.ndarray)
    assert tracks.shape == (10, 2, 100)

def test_generate_images():
    D = get_diffusion_coefficient()
    tracks = generate_tracks(
        n_particles=10,
        steps=2,
        window=(512, 512),
        D=D,
    )
    images = generate_images(tracks)
    assert isinstance(images, np.ndarray)
    assert images.shape == (2, 512, 512)    