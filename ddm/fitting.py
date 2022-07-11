import numpy as np
from scipy.optimize import curve_fit


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


def DDM_Matix(ISF, A, B):
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
