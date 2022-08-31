import numpy as np
import pyfftw

import dask
from dask.diagnostics import ProgressBar
import dask.array as da


def ddm_numpy(data):
    """_summary_

    Parameters
    ----------
    data : np.array
        image stack

    Returns
    -------
    np.array
        ddm matrix
    """
    taus = np.arange(1, len(data) // 2)
    num_frames, height, width = data.shape
    results = []

    img_fft = np.fft.fft2(data).astype("complex64")

    for tau in taus:
        result = dask.delayed(calc_matrix)(img_fft, tau, num_frames, height, width)
        results.append(result)

    with ProgressBar():
        out = dask.compute(*results)
    return np.asarray(out)


def ddm_dask(data, temp_folder: str):
    taus = da.arange(1, len(data) // 2)
    num_frames, height, width = data.shape
    results = []

    fft_data = store_img_fft_temp(data, temp_folder)

    for tau in taus:
        result = calc_matrix_dask(fft_data, tau)
        results.append(result)

    with ProgressBar():
        out = dask.compute(*results)
    fft_shift = np.asarray(out)

    out = []
    for row in fft_shift:
        out.append(calc_radial(fft_shift, num_frames, tau, width, height))


def store_img_fft_temp(data, temp_folder: str = "../data/_temp"):
    img_fft = da.fft.fft2(data.data).astype("complex64")
    da.to_npy_stack(temp_folder, img_fft)
    return da.from_npy_stack(temp_folder)


def calc_matrix(img_fft, tau, num_frames, height, width):
    """_summary_

    Parameters
    ----------
    img_fft : np.array
        _description_
    tau : _type_
        _description_
    num_frames : _type_
        _description_
    height : _type_
        _description_
    width : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    img_diff = img_fft[:-tau, :, :] - img_fft[tau:, :, :]
    img_fft_sq = np.abs(img_diff) ** 2
    img_sum = np.sum(img_fft_sq, axis=0)
    fft_shift = np.fft.fftshift(img_sum)
    gTau = fft_shift / (num_frames - tau)
    gTauRadial = radial_profile(gTau, (width / 2.0, height / 2.0))
    return gTauRadial


def calc_matrix_dask(img_fft, tau):
    """_summary_

    Parameters
    ----------
    img_fft : np.array
        _description_
    tau : _type_
        _description_
    num_frames : _type_
        _description_
    height : _type_
        _description_
    width : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    img_diff = img_fft[:-tau, :, :] - img_fft[tau:, :, :]
    img_fft_sq = da.abs(img_diff) ** 2
    img_sum = da.sum(img_fft_sq, axis=0)
    fft_shift = da.fft.fftshift(img_sum)
    return fft_shift


def calc_radial(fft_shift, num_frames, tau, width, height):
    gTau = fft_shift / (num_frames - tau)
    gTauRadial = radial_profile(gTau, (width / 2.0, height / 2.0))
    return gTauRadial


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


# def ddm_numpy(data: np.ndarray, tau: int):
#     """Calculate gTau with radial profile using numpy

#     Parameters
#     ----------
#     data : _type_
#         _description_
#     tau : _type_
#         _description_

#     Returns
#     -------
#     _type_
#         _description_
#     """
#     num_frames, height, width = data.shape

#     gTau = np.zeros(
#         (width, height)
#     )  # initialise gTau to hold g(vec(q), tau) which will be radially averaged then saved
#     imageDiffFTSquared = np.zeros(
#         (width, height)
#     )  # initialise zeros to hold the squared of the fourier transformed differences

#     for jj in range(
#         num_frames - tau
#     ):  # j is the initial frame in the difference calculation, usually labelled as t
#         imageDiff = (
#             data[jj + tau] - data[jj]
#         )  # calculate the difference in pixel intensities between images
#         imageDiffFT = np.fft.fft2(imageDiff)  # fourier transform the difference
#         imageDiffFTSquared += (
#             np.abs(imageDiffFT) ** 2
#         )  # for averaging this, add the square of the fourier transform to itself

#     imageDiffFTSquared = np.fft.fftshift(imageDiffFTSquared)
#     gTau = imageDiffFTSquared / (num_frames - tau)
#     gTauRadial = radial_profile(gTau, (width / 2.0, height / 2.0))
#     return gTauRadial


# def ddm(data, tau: int):
#     """_summary_

#     Parameters
#     ----------
#     data : _type_
#         _description_
#     tau : _type_
#         _description_

#     Returns
#     -------
#     _type_
#         _description_
#     """
#     num_frames, height, width = data.shape
#     fft_shift = calc_fft_pyfftw(data, tau=tau)
#     gTau = fft_shift / (num_frames - tau)
#     x, y = np.indices((width, height))
#     gTau_radial = radial_profile(gTau, (width / 2.0, height / 2.0), x, y)
#     return gTau_radial


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
