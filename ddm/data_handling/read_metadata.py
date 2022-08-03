import os
import pims
import nd2
from typing import Dict


def read_metadata(filename: str) -> Dict:
    """Wrapper for reading metadata

    Parameters
    ----------
    filename : str
        name of data file

    Returns
    -------
    dict
        metadata

    Raises
    ------
    ValueError
        file extension is not supported
    """

    extension = os.path.splitext(filename)[-1]
    formats_metadata = {
        ".lif": read_metadata_lif,
        ".nd2": read_metadata_nd2,
        ".tif": read_metadata_tif,
        ".tiff": read_metadata_tif,
    }

    if extension in formats_metadata.keys():
        return formats_metadata[extension](filename)
    else:
        raise ValueError(
            f"No metadata reader is available for {extension}. The currently supported formats are {[name for name in formats_metadata.keys()]}."
        )


def read_metadata_nd2(filename: str) -> Dict:
    """Read metadata from nd2 file

    Parameters
    ----------
    filename : str
        file to read

    Returns
    -------
    Dict
        image metadata
    """
    metadata = {}

    with nd2.ND2File(filename) as imgs:
        metadata["tscale"] = imgs.experiment[0].parameters.periodDiff.avg
        metadata["xscale"] = imgs.voxel_size().x
    return metadata


def read_metadata_lif(filename: str) -> Dict:
    """Read metadata from lif file

    Parameters
    ----------
    filename : str
        file to read

    Returns
    -------
    Dict
        image metadata
    """
    metadata = {}
    with pims.Bioformats(filename) as imgs:
        metadata["xscale"] = imgs.metadata.PixelsPhysicalSizeX(0)
        metadata["tscale"] = imgs.metadata.PlaneDeltaT(0, 1) * 1000.0
        metadata["n_experiments"] = imgs.metadata.ImageCount()
        metadata["experiment_names"] = [
            imgs.metadata.ImageName(x) for x in range(imgs.metadata.ImageCount())
        ]
    return metadata


def read_metadata_tif(filename: str) -> Dict:
    """Read metadata from tif file

    Parameters
    ----------
    filename : str
        file to read

    Returns
    -------
    Dict
        image metadata
    """
    metadata = {}
    with pims.Bioformats(filename) as imgs:
        try:
            metadata["xscale"] = imgs.metadata.PixelsPhysicalSizeX(0)
        except AttributeError:
            metadata["xscale"] = 1.0
        try:
            metadata["tscale"] = imgs.metadata.PixelsTimeIncrement(0) * 1000.0
        except AttributeError:
            metadata["tscale"] = 1.0
    return metadata
