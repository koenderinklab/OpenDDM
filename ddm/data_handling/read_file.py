import os
import warnings

import dask
import numpy as np
import xarray
from typing import Dict

from .read_metadata import read_metadata
from .dask_image import read_data_into_dask
from ..utils import verify_bioformats_jar


SUPPORTED_FORMATS = [".lif", ".nd2", ".tif", ".tiff"]


def read_file(
    filename: str,
    nframes: int = 1,
    xscale: float = None,
    tscale: float = None,
    experiment: int = None,
) -> xarray.DataArray:
    """A function to read in a generic microscopy series.

    Parameters
    ----------
    filename : string
        the path and name of the file which is to be loaded in
    nframes : int
        Number of the frames to include in each dask chunk. Default is 1.
    xscale : float, optional
        the resolution of the image in microns per pixel. Default is None.
    tscale : float, optional
        the time per frame of the image series in milliseconds. Default is None
    experiment : int, optional
        selected experiment in a multi-experiment lif file

    Returns
    -------
    dask array
        array with the image data saved as a dask array. Metadata in the dask array
        includes the spatial resolution in microns per pixel and the temporal resolution
        in milliseconds per frame.

    Raises
    ------
    OSError
        file cannot be found
    ValueError
        file extension is not supported
    TypeError
        user input is of wrong type
    """
    # Catch potential problems with jar_file from Bioformats
    verify_bioformats_jar()

    # Define supported files
    extension = os.path.splitext(filename)[-1]

    if extension in SUPPORTED_FORMATS:
        if not os.path.exists(filename):
            raise OSError(f"The file {filename} does not exist")

        try:
            return load_data(filename, nframes, xscale, tscale, experiment)
        except IndexError:
            raise
        except TypeError:
            raise
        except BaseException as err:
            print(f"Unknown error: {err}")

    else:
        raise ValueError(
            f"{extension} is not a supported image format. The currently supported formats are {[name for name in SUPPORTED_FORMATS]}."
        )


def load_data(
    filename: str,
    nframes: int = 1,
    xscale: float = None,
    tscale: float = None,
    experiment: int = None,
):
    """Read image data

    Parameters
    ----------
    filename : string
        the path and name of the file which is to be loaded in
    nframes : int
        Number of the frames to include in each dask chunk. Default is 1.
    xscale : float, optional
        the resolution of the image in microns per pixel. Default is None.
    tscale : float, optional
        the time per frame of the image series in milliseconds. Default is None
    experiment : int, optional
        selected experiment in a multi-experiment lif file

    Returns
    -------
    xarray.DataArray
        A xarray containing metadata and a Dask Array with the contents of all image files.
    """

    # Set xscale and tscale
    metadata = read_metadata(filename)
    xscale = metadata["xscale"] if xscale is None else xscale
    tscale = metadata["tscale"] if tscale is None else tscale

    # Handle multiple experiments for lif files
    extension = os.path.splitext(filename)[-1]
    if extension == ".lif":
        experiment = select_experiment(metadata, experiment)
    else:
        experiment = 0

    # Load delayed data
    arr = read_data_into_dask(filename, nframes, experiment=experiment)

    # Return xarray
    return create_xarray(arr, xscale, tscale)


def select_experiment(metadata: Dict, experiment: int = None) -> int:
    """Prompt user to select single experiment from .lif file

    Parameters
    ----------
    metadata : pims.bioformats.MetadataRetrieve
        .lif image metadata

    Returns
    -------
    int
        selected experiment
    """

    if (metadata["n_experiments"] > 1) and (experiment is None):

        experiments = [x for x in range(metadata["n_experiments"])]
        print(f"The datafile contains the following experiments:")
        for i, name in enumerate(metadata["experiment_names"]):
            print(f"{i} : {name}")
        experiment = input(
            f"Please select the experiment you want to process {experiments} \n"
        )
    elif experiment is not None:
        experiment = experiment
    else:
        experiment = 0

    # Check value of experiment
    if type(experiment) is not int:
        raise TypeError(
            f"Experiment value should be an integer, not {type(experiment)=}"
        )
    elif experiment >= metadata["n_experiments"]:
        raise IndexError(f"Index {experiment} is out of bounds.")
    return experiment


def create_xarray(
    arr: dask.array.core.Array, xscale: float, tscale: float
) -> xarray.DataArray:
    """Create xarray DataFrame with delayed dataset

    Parameters
    ----------
    arr : dask.array.core.Array
        dataset of images
    xscale : float
        size of a pixel in the image in micron
    tscale : float
        frametime in ms

    Returns
    -------
    xarray.DataArray

    """
    # Create coordinates
    t_coords = np.arange(0.0, arr.shape[0] * tscale, tscale)
    x_coords = np.arange(0.0, arr.shape[1] * xscale, xscale)
    y_coords = np.arange(0.0, arr.shape[2] * xscale, xscale)

    # Create data array
    x_arr = xarray.DataArray(
        data=arr,
        dims=["T", "Y", "X"],
        coords=(t_coords, y_coords, x_coords),
        attrs=dict(xyScale=xscale, tScale=tscale),
    )
    return x_arr
