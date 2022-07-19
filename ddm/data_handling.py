import os

import dask.array as da
import nd2
import numpy as np
import pims
import xarray

from .utils import verify_bioformats_jar


def read_file(
    filename: str, xscale: float = None, tscale: float = None, experiment: int = None
) -> xarray.DataArray:
    """A function to read in a generic microscopy series.

    Parameters
    ----------
    filename : string
        the path and name of the file which is to be loaded in
    xscale : float, optional
         the resolution of the image in microns per pixel. Default is None.
    tscale : float, optional
        the time per frame of the image series in milliseconds. Default is None
    experiment : int, optional
        selected experiment in a multi-experiment lif file

    Returns
    -------
    dask array
        array with the image data saved as a dask array. Metadata in the dask array includes the spatial resolution in microns per pixel and the temporal resolution in milliseconds per frame.

    Raises
    ------
    OSError
        file cannot be found
    ValueError
        file extension is not supported
    """
    # Catch potential problems with jar_file from Bioformats
    verify_bioformats_jar()

    # Define supported files
    supported = {".lif": readLIF, ".nd2": readND2, ".tif": readTIF, ".tiff": readTIF}
    extension = os.path.splitext(filename)[-1]

    if extension in supported.keys():
        if not os.path.exists(filename):
            raise OSError(f"The file {filename} does not exist")

        try:
            if extension == ".lif":
                return supported[extension](filename, xscale, tscale, experiment)
            else:
                return supported[extension](filename, xscale, tscale)
        except IndexError as err:
            raise
        except BaseException as err:
            print(f"Error: {err}")

    else:
        raise ValueError(
            f"{extension} is not a supported image format. The currently supported formats are {[name for name in supported.keys()]}."
        )


def readND2(
    filename: str, xscale: float = None, tscale: float = None
) -> xarray.DataArray:
    """A function to read in a .nd2 file taken from a Nikon microscope. Has been shown to work for files from our Minicell in the Koenderink lab.

    Parameters
    ----------
    filename : string
        the path and name of the .nd2 file which is to be loaded in
    xscale : float, optional
        the resolution of the image in microns per pixel
    tscale : float, optional
        the time per frame of the image series in milliseconds

    Returns
    -------
    dask array
        array with the image data saved as a dask array.
        Metadata in the dask array includes the spatial resolution in microns per pixel and the temporal resolution in milliseconds per frame.
    """
    sequence = nd2.imread(filename, xarray=True, dask=True)
    # Find frame time per frame in ms
    frameT = sequence.metadata["experiment"][0].parameters.periodDiff.avg
    # Find scale in microns per pixel
    xscale = float(sequence.X[1]) if xscale is None else xscale
    tscale = frameT if tscale is None else tscale
    sequence["T"] = np.arange(len(sequence["T"])) * tscale
    sequence.attrs = {"xyScale": xscale, "tScale": tscale}
    return sequence


def readLIF(
    filename: str, xscale: float = None, tscale: float = None, experiment: int = None
) -> xarray.DataArray:
    """A function to read in a .lif file taken from a Leica microscope.
    Verified to work for files from our Thunder in the Koenderink lab.

    Parameters
    ----------
    filename : string
        the path and name of the .lif file which is to be loaded in
    xscale : float, optional
        the resolution of the image in microns per pixel
    tscale : float, optional
        the time per frame of the image series in milliseconds
    experiment : int, optional
        selected experiment in a multi-experiment lif file

    Returns
    -------
    xarray.DataArray
        Metadata in the dask array includes the spatial resolution in microns per pixel and the temporal resolution in milliseconds per frame.

    """

    data_sets = []
    lifSeq = pims.Bioformats(filename, read_mode="jpype")

    # Select experiment when multiple experiments are available
    n_experiments = lifSeq.metadata.ImageCount()
    if n_experiments > 1:
        experiment = (
            select_LIF_experiment(lifSeq.metadata) if experiment is None else experiment
        )
    else:
        experiment = 0

    lifSeq.series = experiment
    xscale = lifSeq.metadata.PixelsPhysicalSizeX(0) if xscale is None else xscale
    tscale = lifSeq.metadata.PlaneDeltaT(0, 1) * 1000.0 if tscale is None else tscale
    lifXCoords = np.arange(0.0, lifSeq.shape[1] * xscale, xscale)
    lifYCoords = np.arange(0.0, lifSeq.shape[2] * xscale, xscale)
    lifTCoords = np.arange(0.0, lifSeq.shape[0] * tscale, tscale)
    ds = da.from_array(lifSeq)
    sequence = xarray.DataArray(
        data=ds,
        dims=["T", "Y", "X"],
        coords=(lifTCoords, lifYCoords, lifXCoords),
        attrs=dict(xyScale=xscale, tScale=tscale),
    )
    return sequence


def select_LIF_experiment(metadata: pims.bioformats.MetadataRetrieve) -> int:
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
    experiments = [x for x in range(metadata.ImageCount())]
    print(f"The datafile contains the following experiments:")
    for exp in experiments:
        print(f"{exp} : {metadata.ImageName(exp)}")
    return int(
        input(f"Please select the experiment you want to process {experiments} \n")
    )


def readTIF(
    filename: str, xscale: float = None, tscale: float = None
) -> xarray.DataArray:
    """A function to read in a .tif file taken from a Leica microscope. Has been shown to work for files from our Thunder in the Koenderink lab.

    Parameters
    ----------
    filename : string
        the path and name of the .tif file which is to be loaded in
    xscale : float, optional
        the resolution of the image in microns per pixel
    tscale : float, optional
        the time per frame of the image series in milliseconds

    Returns
    -------
    dask array
        array with the image data saved as a dask array. Metadata in the dask array includes the spatial resolution in microns per pixel and the temporal resolution in milliseconds per frame.
    """
    tifSeq = pims.Bioformats(filename, read_mode="jpype")

    # Parse xscale and tscale
    if xscale == None:
        try:
            xscale = tifSeq.metadata.PixelsPhysicalSizeX(0)
        except:
            xscale = 1.0
    if tscale == None:
        try:
            tscale = tifSeq.metadata.PixelsTimeIncrement(0) * 1000.0
        except:
            tscale = 1.0

    # Create coordinates
    tifXCoords = np.arange(0.0, tifSeq.shape[1] * xscale, xscale)
    tifYCoords = np.arange(0.0, tifSeq.shape[2] * xscale, xscale)
    tifTCoords = np.arange(0.0, tifSeq.shape[0] * tscale, tscale)

    # Build DataFrame
    ds = da.from_array(tifSeq)
    sequence = xarray.DataArray(
        data=ds,
        dims=["T", "Y", "X"],
        coords=(tifTCoords, tifYCoords, tifXCoords),
        attrs=dict(xyScale=xscale, tScale=tscale),
    )
    return sequence
