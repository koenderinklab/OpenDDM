import matplotlib.pyplot as pl
import numpy as np
from .fitting import singleExp

def plotISF(isf, taus, q = None):
    """_summary_

    Parameters
    ----------
    isf : np.ndarray
        _description_
    taus : np.ndarray
        _description_
    q : int or tuple of ints, optional
        _description_

    Returns
    -------
    _type_
        _description_
    """
    q = len(isf)//2 if q is None else q
    q = [q] if type(q) is int else q
    for x in q:
        pl.plot(taus, isf[x], ls = 'None', marker = 'o', label = str(x))

def plotSingleExpFit(isf, taus, q = None):
    """_summary_

    Parameters
    ----------
    isf : np.ndarray
        _description_
    taus : np.ndarray
        _description_
    q : int or tuple of ints, optional
        _description_

    Returns
    -------
    _type_
        _description_
    """
    q = len(isf)//2 if q is None else q
    q = [q] if type(q) is int else q
    for x in q:
        pExpFit, pExpErrs = ddm.genFit(isf[x], taus, 'singleExp')
        pl.plot(taus, singleExp(taus, *pExpFit))