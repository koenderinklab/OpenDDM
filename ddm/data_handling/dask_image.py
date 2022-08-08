# Copyright (c) 2017-2018, dask-image Developers (see AUTHORS.rst for details)
# All rights reserved.

import glob
import threading
import numbers
import warnings

from typing import Any

import dask.array as da
import numpy as np
import pims
from tifffile import natural_sorted


def read_data_into_dask(fname, nframes: int = 1, *, experiment: int = 0):
    """
    Read image data into a Dask Array.
    Provides a simple, fast mechanism to ingest image data into a
    Dask Array.
    Parameters
    ----------
    fname : str or pathlib.Path
        A glob like string that may match one or multiple filenames.
        Where multiple filenames match, they are sorted using
        natural (as opposed to alphabetical) sort.
    nframes : int, optional
        Number of the frames to include in each chunk (default: 1).
    experiment : int, optional
        select experiment if image stack contains multiple measurement series (default: 0)

    Returns
    -------
    array : dask.array.Array
        A Dask Array representing the contents of all image files.
    """

    sfname = str(fname)
    if not isinstance(nframes, numbers.Integral):
        raise ValueError("`nframes` must be an integer.")
    if (nframes != -1) and not (nframes > 0):
        raise ValueError("`nframes` must be greater than zero.")

    arrayfunc = np.asanyarray

    with pims.open(sfname) as imgs:
        shape = (len(imgs),) + imgs.frame_shape
        dtype = np.dtype(imgs.pixel_type)

    if nframes == -1:
        nframes = shape[0]

    if nframes > shape[0]:
        warnings.warn(
            "`nframes` larger than number of frames in file."
            " Will truncate to number of frames in file.",
            RuntimeWarning,
        )
    elif shape[0] % nframes != 0:
        warnings.warn(
            "`nframes` does not nicely divide number of frames in file."
            " Last chunk will contain the remainder.",
            RuntimeWarning,
        )

    # Check experiment selection

    # place source filenames into dask array after sorting
    filenames = natural_sorted(glob.glob(sfname))
    if len(filenames) > 1:
        ar = da.from_array(filenames, chunks=(nframes,))
        multiple_files = True
    else:
        ar = da.from_array(filenames * shape[0], chunks=(nframes,))
        multiple_files = False

    # read in data using encoded filenames
    dask_arr = ar.map_blocks(
        _map_read_frame,
        chunks=da.core.normalize_chunks((nframes,) + shape[1:], shape),
        multiple_files=multiple_files,
        new_axis=list(range(1, len(shape))),
        experiment=experiment,
        arrayfunc=arrayfunc,
        meta=arrayfunc([]).astype(dtype),  # meta overwrites `dtype` argument
    )
    return dask_arr


def _map_read_frame(x, multiple_files, block_info=None, **kwargs):

    fn = x[0]  # get filename from input chunk

    if multiple_files:
        i, j = 0, 1
    else:
        i, j = block_info[None]["array-location"][0]

    with threading.RLock():
        return _read_frame(fn=fn, i=slice(i, j), **kwargs)


def _read_frame(fn, i, *, arrayfunc=np.asanyarray, experiment=0):
    # with pims.Bioformats(fn, series=experiment, read_mode="jpype") as imgs:
    # with pims.Bioformats(fn) as imgs:
    with pims.open(fn) as imgs:
        data = arrayfunc(imgs[i])
        data = data.copy()
        return data
