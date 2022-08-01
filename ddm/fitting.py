#!/usr/bin/env python
# coding: utf-8

import numpy as np
from scipy.optimize import curve_fit
import dask.array as da
import dask
from typing import Tuple
from .processing import radial_profile


def findMeanSqFFT(dData: dask.array):
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
    sqFFT = 2 * da.abs(da.fft.fft2(dData)) * da.abs(da.fft.fft2(dData))
    sqFFT = da.fft.fftshift(sqFFT)
    sqFFTmean = da.mean(sqFFT, axis=0)
    return sqFFTmean


def computeAB(sqFFTmean: np.array) -> Tuple[np.array, float]:
    """
    Function to calculate the parameters A and B

    Parameters
    ----------
    sqFFTmean : numpy array
        the result of findMeanSqFFT, the mean over all frames of the square of the fourier transform

    Returns
    -------
    a : numpy array
        array containing A(q), the pre-factor of the image structure function which contains info on the imaging conditions
    b : float
        the magnitude of the noise of the image data
    """
    sqFFTrad = radial_profile(
        sqFFTmean, (np.shape(sqFFTmean)[1] / 2, np.shape(sqFFTmean)[2] / 2)
    )
    b = np.mean(sqFFTrad[-100:-50])  # change depending on size of array
    a = sqFFTrad - b
    return a, b


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


def doubleExp(t, tau1, tau2, n, B, S1, S2):
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
    
    if fitFunc in supported.keys():
        popt, pcov = curve_fit(supported[fitFunc], taus, isf)
        errs = np.sqrt(np.diag(pcov))
        return popt, errs
    else:
        raise ValueError(
            f"{fitFunc} is not a supported fitting function. The currently supported functions are {[name for name in supported.keys()]}.")

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
