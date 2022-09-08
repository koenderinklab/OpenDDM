import numpy as np
from scipy.optimize import curve_fit
import xarray as xr
import dask.array as da
import dask
from typing import Tuple
from .processing import radial_profile


def compute_AB(dData: xr.DataArray) -> Tuple[np.ndarray, float]:
    """
    Function to calculate the parameters A and B

    Parameters
    ----------
    dData : xarray.DataArray
        xarray containing the raw image data

    Returns
    -------
    A : np.ndarray
        array containing A(q), the pre-factor of the image structure function which contains info on the imaging conditions
    B : float
        the magnitude of the noise of the image data
    """

    if isinstance(dData.data, np.ndarray):
        sqFFTmean = findMeanSqFFT_numpy(dData)
    elif isinstance(dData.data, dask.array.core.Array):
        sqFFTmean = findMeanSqFFT(dData)
    else:
        raise TypeError(f"Type {type(dData)} is not supported")

    sqFFTrad = radial_profile(
        sqFFTmean, (np.shape(sqFFTmean)[0] / 2, np.shape(sqFFTmean)[1] / 2)
    )
    b = np.mean(sqFFTrad[-100:-50])  # change depending on size of array
    a = sqFFTrad - b
    return a, b


def findMeanSqFFT(dData: dask.array) -> np.ndarray:
    """
    Function to calculate the mean of the square of the FFT over all frames

    Parameters
    ----------
    dData : dask.array
        dask array containing the raw image data

    Returns
    -------
    sqFFTmean : the mean over all frames of the square of the fourier transform
    """

    sqFFT = 2 * da.abs(da.fft.fft2(dData.data).astype(np.complex64)) ** 2
    sqFFT = da.fft.fftshift(sqFFT)
    sqFFTmean = da.mean(sqFFT, axis=0).compute()
    return sqFFTmean


def findMeanSqFFT_numpy(dData: np.array) -> np.ndarray:
    """
    Function to calculate the mean of the square of the FFT over all frames

    Parameters
    ----------
    dData : dask.array
        dask array containing the raw image data

    Returns
    -------
    sqFFTmean : the mean over all frames of the square of the fourier transform
    """
    sqFFT = 2 * np.abs(np.fft.fft2(dData).astype(np.complex64)) ** 2
    sqFFT = np.fft.fftshift(sqFFT)
    sqFFTmean = np.mean(sqFFT, axis=0)
    return sqFFTmean


def singleExp(t, tau, S):
    """
    Function for single exponential DDM fits

    Parameters
    ----------
    t : array_like
        array of the lag times
    tau : float
        decay time
    S: float
        stretching exponent

    Returns
    -------
    theoretical single exponential ISF for given parameters
    """
    return np.exp(-1 * (t / tau) ** S)


def doubleExp(t, tau1, tau2, n, S1, S2):
    """
    Function for single exponential DDM fits

    Parameters
    ----------
    t : array_like
        array of the lag times
    tau1 : float
        decay time for first exponential
    tau2 : float
        decay time for second exponential
    n: float
        fraction of dynamics for first exponential
    S1: float
        stretching exponent for first exponential
    S2: float
        stretching exponent for second exponential

    Returns
    -------
    theoretical double exponential ISF for given parameters
    """
    return n * np.exp(-1 * (t / tau1) ** S1) + (1 - n) * np.exp(-1 * (t / tau2) ** S2)


def schultz(lagtime, tau1, tau2, n, S, Z):
    """
    Function for the so called Schultz model for fitting to DDM data containing
    both diffusive and actively directed motion

    Parameters
    ----------
    lagtime : array_like
        array of the lag times
    tau1 : float
        decay time for the exponential part of ISF
    tau2 : floar
        decay time for directed motion part of ISF
    n : float
        fraction of dynamics undergoing ballistic motion
    S: float
        stretching exponent
    Z : float
        Schultz distribution number

    Returns
    -------
    theoretical ISF for schultz distribution for given values
    """

    theta = (lagtime / tau2) / (Z + 1.0)
    VDist = (
        ((Z + 1.0) / ((Z * lagtime) / tau2))
        * np.sin(Z * np.arctan(theta))
        / ((1.0 + theta**2.0) ** (Z / 2.0))
    )
    return np.exp(-1.0 * (lagtime / tau1) ** S) * ((1.0 - n) + n * VDist)


def test_linear(isf, taus):
    """ """
    linGrad = (isf[-1] - isf[0]) / (taus[-1] - taus[0])
    linInter = 1.0
    residual = np.sqrt(np.sum((isf - (linGrad * taus + linInter)) ** 2))
    if residual < 0.1:
        return True
    else:
        return False


def genFit(isf, taus, fitFunc):
    """
    Generalised fitting function to fit the ISF

    Parameters
    ----------
    isf : array_like
        array of the lag times
    taus : np.ndarray
        decay time
    fitFunc: string
        stretching exponent

    Returns
    -------

    """
    supported = {"singleExp": singleExp, "doubleExp": doubleExp, "schultz": schultz}

    if fitFunc not in supported.keys():
        raise ValueError(
            f"{fitFunc} is not a supported fitting function. The currently supported functions are {[name for name in supported.keys()]}."
        )
    else:
        if test_linear(isf, taus):
            raise ValueError(
                f"The data fits well to a linear function, implying very little decorrelation which cannot be fitted to a model based on exponential decorellation."
            )
        else:
            if fitFunc == "doubleExp":
                popt, pcov = curve_fit(
                    supported[fitFunc],
                    taus,
                    isf,
                    bounds=([0.0, 0.0, 0.0, 1.0, 1.0], [np.inf, np.inf, 1.0, 2.0, 2.0]),
                )
            else:
                popt, pcov = curve_fit(supported[fitFunc], taus, isf)
            errs = np.sqrt(np.diag(pcov))
            return popt, errs


def DDM_Matrix(ISF, A, B):
    """
    Function to calculate the DDM matrix from a given ISF

    Parameters
    ----------
    ISF : array_like
        array containing the ISF
    A : float
        scaling amplitude factor
    B : float
        background term

    Returns
    -------
    theoretical DDM matrix for given ISF
    """

    return A * (1 - ISF) + B


def compute_ISF(ddmMatrix: np.ndarray, A: np.ndarray, B: float) -> np.ndarray:
    """Calculate ISF

    Parameters
    ----------
    ddmMatrix : np.ndarray
        theoretical DDM matrix for given ISF
    A : float
        scaling amplitude factor
    B : float
        background term

    Returns
    -------
    np.ndarray
        ISF
    """

    isf = 1.0 - (ddmMatrix - B) / A
    return np.transpose(isf)
