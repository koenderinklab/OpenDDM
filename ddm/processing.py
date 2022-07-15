import numpy as np
import pyfftw
from dask import delayed
from numba import jit


@delayed
def radial_profile(data: np.ndarray, centre: tuple):
    """_summary_

    Parameters
    ----------
    data : np.ndarray
        _description_
    centre : tuple
        _description_

    Returns
    -------
    _type_
        _description_
    """
    x, y = np.indices((data.shape))
    r = np.sqrt((x - centre[0]) ** 2 + (y - centre[1]) ** 2)
    r = r.astype(np.int)
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    return radialprofile


@delayed
@jit(nopython=True, nogil=True)
def radial_profile_jit(data, centre, x, y):
    # x, y = np.indices((data.shape))
    r = np.sqrt((x - centre[0]) ** 2 + (y - centre[1]) ** 2)
    r = r.astype(np.int64)
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    return radialprofile


def get_diff_images(data: np.ndarray, step: int):
    """Calculate difference between image [n] and [n + shift] for all images

    Parameters
    ----------
    data : ndarray
        array of images
    shift : int
        step between frame number

    Returns
    -------
    ndarray
        
    """
    return data[:-step, :, :] - data[step:, :, :]


def ddm_fftw(data: np.ndarray, tau: int):
    """Calculate gTau with radial profile using pyfftw

    Parameters
    ----------
    data : _type_
        _description_
    tau : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    num_frames, height, width = data.shape

    pyfftw.interfaces.cache.enable()
    imageDiff = pyfftw.empty_aligned((height, width), dtype="complex64")
    fft_object = pyfftw.builders.fft2(
        imageDiff, threads=8, overwrite_input=True, planner_effort="FFTW_ESTIMATE"
    )

    gTau = np.zeros(
        (width, height)
    )  # initialise gTau to hold g(vec(q), tau) which will be radially averaged then saved
    imageDiffFTSquared = np.zeros(
        [width, height]
    )  # initialise zeros to hold the squared of the fourier transformed differences

    for jj in range(
        num_frames - tau
    ):  # j is the initial frame in the difference calculation, usually labelled as t
        imageDiff = (
            data[jj + tau] - data[jj]
        )  # calculate the difference in pixel intensities between images
        imageDiffFTSquared += (
            np.abs(fft_object(imageDiff)) ** 2
        )  # for averaging this, add the square of the fourier transform to itself

    imageDiffFTSquared = np.fft.fftshift(imageDiffFTSquared)
    gTau = imageDiffFTSquared / (num_frames - tau)
    gTauRadial = radial_profile(gTau, (width / 2.0, height / 2.0))
    return gTauRadial


def ddm_numpy(data: np.ndarray, tau: int):
    """Calculate gTau with radial profile using numpy

    Parameters
    ----------
    data : _type_
        _description_
    tau : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    num_frames, height, width = data.shape

    gTau = np.zeros(
        (width, height)
    )  # initialise gTau to hold g(vec(q), tau) which will be radially averaged then saved
    imageDiffFTSquared = np.zeros(
        (width, height)
    )  # initialise zeros to hold the squared of the fourier transformed differences

    for jj in range(
        num_frames - tau
    ):  # j is the initial frame in the difference calculation, usually labelled as t
        imageDiff = (
            data[jj + tau] - data[jj]
        )  # calculate the difference in pixel intensities between images
        imageDiffFT = np.fft.fft2(imageDiff)  # fourier transform the difference
        imageDiffFTSquared += (
            np.abs(imageDiffFT) ** 2
        )  # for averaging this, add the square of the fourier transform to itself

    imageDiffFTSquared = np.fft.fftshift(imageDiffFTSquared)
    gTau = imageDiffFTSquared / (num_frames - tau)
    gTauRadial = radial_profile(gTau, (width / 2.0, height / 2.0))
    return gTauRadial


def ddm(data, tau: int):
    """_summary_

    Parameters
    ----------
    data : _type_
        _description_
    tau : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    num_frames, height, width = data.shape
    fft_shift = calc_fft_pyfftw(data, tau=tau)
    gTau = fft_shift / (num_frames - tau)
    x, y = np.indices((width, height))
    gTau_radial = radial_profile_jit(gTau, (width / 2.0, height / 2.0), x, y)
    return gTau_radial


@delayed
def calc_fft_pyfftw(data, tau: int):
    """_summary_

    Parameters
    ----------
    data : _type_
        _description_
    tau : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    num_frames, height, width = data.shape
    image_fft_squared = np.zeros((width, height))

    pyfftw.interfaces.cache.enable()
    image_diff = pyfftw.empty_aligned((height, width), dtype="complex64")
    fft_object = pyfftw.builders.fft2(
        image_diff, threads=8, overwrite_input=True, planner_effort="FFTW_ESTIMATE"
    )

    for jj in range(num_frames - tau):
        image_diff = data[jj + tau] - data[jj]
        image_fft_squared += np.abs(fft_object(image_diff)) ** 2

    fft_shift = np.fft.fftshift(image_fft_squared)
    return fft_shift


@delayed
def calc_fft(data, tau: int):
    """_summary_

    Parameters
    ----------
    data : _type_
        _description_
    tau : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    num_frames, height, width = data.shape
    image_fft_squared = np.zeros((width, height))
    for jj in range(num_frames - tau):
        image_diff = data[jj + tau] - data[jj]
        image_fft = np.fft.fft2(image_diff)
        image_fft_squared += np.abs(image_fft) ** 2

    fft_shift = np.fft.fftshift(image_fft_squared)
    return fft_shift
