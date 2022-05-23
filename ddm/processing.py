import numpy as np
from numba import jit

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
    r = np.sqrt((x-centre[0])**2 + (y-centre[1])**2)
    r = r.astype(np.int)
    tbin = np.bincount(r.ravel(),data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin/nr
    return radialprofile


@jit(nopython=True, nogil=True)
def radial_profile_jit(data, centre, x, y):
    # x, y = np.indices((data.shape))
    r = np.sqrt((x-centre[0])**2 + (y-centre[1])**2)
    r = r.astype(np.int64)
    tbin = np.bincount(r.ravel(),data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin/nr
    return radialprofile