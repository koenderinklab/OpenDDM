from typing import Union
import numpy as np
import dask
from dask.diagnostics import ProgressBar
import dask.array as da
from tqdm import tqdm

from .utils import is_gpu_available

try:
    import cupy as cp
except ImportError:
    pass


def ddm(
    data: Union[dask.array.core.Array, np.ndarray], taus: np.ndarray = np.arange(0)
) -> np.ndarray:
    """_summary_

    Parameters
    ----------
    data : Union[dask.array.core.Array, np.ndarray]
    taus : np.ndarray, optional
        array of lag times (in frames), by default half of number of frames

    Returns
    -------
    np.ndarray

    Raises
    ------
    TypeError
        Data type is not supported. Supported types are np.ndarray and dask.array.core.Array.
    """
    # Check lag time range
    taus = np.arange(1, len(data) // 2) if taus.size == 0 else taus
    if taus[0] == 0:
        raise ValueError("Cannot calculate 0 lag time, please start range at 1")

    data_type = data.data
    if isinstance(data_type, np.ndarray):
        return ddm_numpy(data, taus)
    elif isinstance(data_type, dask.array.core.Array):
        if is_gpu_available:
            try:
                import cupy as cp

                print("Running analysis on GPU")
                return ddm_dask_gpu(data, taus)
            except ImportError:
                print("ImportError CuPy, running analysis on CPU")
                return ddm_dask_cpu(data, taus)
        else:
            print("Running analysis on CPU")
            return ddm_dask_cpu(data, taus)
    else:
        raise (TypeError, f"Data of type {data_type} is not supported")


def ddm_numpy(data, taus: np.ndarray):
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
    num_frames, height, width = data.shape
    results = []

    img_fft = np.fft.fft2(data).astype(np.complex64)

    for tau in taus:
        result = dask.delayed(calc_matrix)(img_fft, tau, num_frames, height, width)
        results.append(result)

    with ProgressBar():
        out = dask.compute(*results)
    return np.asarray(out)


def ddm_dask_cpu(data, taus: np.ndarray):
    """_summary_

    Parameters
    ----------
    data : _type_
        _description_
    taus : _type_, optional
        _description_, by default np.arange(0)

    Returns
    -------
    _type_
        _description_
    """
    num_frames, _, _ = data.shape
    results = []

    fft_data = da.fft.fft2(data.data)

    for tau in taus:
        result = calc_matrix_dask(fft_data, tau)
        results.append(result)

    with ProgressBar():
        fft_shift = dask.compute(*results)

    out = []
    for row, tau in zip(fft_shift, taus):
        out.append(calc_radial(row, num_frames, tau))
    return np.asarray(out)


def ddm_dask_gpu(data, taus: np.ndarray = np.arange(0)):
    """_summary_

    Parameters
    ----------
    data : _type_
        _description_
    taus : _type_, optional
        _description_, by default np.arange(0)

    Returns
    -------
    _type_
        _description_
    """
    taus = np.arange(1, len(data) // 2) if taus.size == 0 else taus
    num_frames, width, height = data.shape
    results = []

    chunk_size = (data.chunks[0][0], width, height)

    data_gpu = da.from_array(cp.asarray(data.data), chunks=chunk_size, asarray=False)
    fft_data = da.fft.fft2(data_gpu).astype(cp.complex64)
    del data_gpu

    for tau in tqdm(taus):
        result = calc_matrix_dask(fft_data, tau)
        out = dask.compute(result, scheduler="single-threaded")
        results.append(cp.asnumpy(out[0]))
        del result, out
        cp._default_memory_pool.free_all_blocks()

    del fft_data
    cp._default_memory_pool.free_all_blocks()

    out = []
    for data, tau in zip(results, taus):
        out.append(calc_radial(data, num_frames, tau))
    return np.asarray(out)


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


def calc_radial(fft_shift: np.ndarray, num_frames, tau):
    """_summary_

    Parameters
    ----------
    fft_shift : _type_
        _description_
    num_frames : _type_
        _description_
    tau : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    width, height = fft_shift.shape
    gTau = fft_shift / (num_frames - tau)
    gTauRadial = radial_profile(gTau, (width / 2.0, height / 2.0))
    return gTauRadial


def calc_radial_gpu(fft_shift: np.ndarray, num_frames, tau):
    """_summary_

    Parameters
    ----------
    fft_shift : _type_
        _description_
    num_frames : _type_
        _description_
    tau : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    width, height = fft_shift.shape
    gTau = fft_shift / (num_frames - tau)
    gTauRadial = radial_profile_gpu(gTau, (width / 2.0, height / 2.0))
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


def radial_profile_gpu(data: np.ndarray, centre: tuple):
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
    x, y = cp.indices((data.shape))
    r = cp.sqrt((x - centre[0]) ** 2 + (y - centre[1]) ** 2)
    r = r.astype(cp.int)
    tbin = cp.bincount(r.ravel(), data.ravel())
    nr = cp.bincount(r.ravel())
    radialprofile = tbin / nr
    return radialprofile
