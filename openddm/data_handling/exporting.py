import os
from datetime import datetime

import numpy as np
import xarray as xr


def export_data(
    pathname: str,
    data: np.ndarray,
    taus: np.ndarray,
    img_pathname: str,
) -> xr.DataArray:
    """Convert data to xr.dataArray and store as netcdf and csv

    Parameters
    ----------
    pathname : str
        export folder
    data : np.ndarray
        ddmMatrix
    taus : np.ndarray
        array of lag times
    img_pathname : str
        pathname of microscopy source data
    export_type : str, optional
        export protocol, defaults to netcdf.

    Returns
    -------
    xr.dataArray
        data as xarray dataArray
    """

    # Create output folder if it doesn't exist
    if not os.path.isdir(os.path.abspath(pathname)):
        os.mkdir(os.path.abspath(pathname))

    arr = create_data_array(data, taus, os.path.abspath(img_pathname))

    # Create file names
    save_file_base = os.path.splitext(os.path.basename(img_pathname))[0]
    save_file_nc = os.path.join(
        os.path.abspath(pathname), f"{save_file_base}_matrix.nc"
    )
    save_file_csv = os.path.join(
        os.path.abspath(pathname), f"{save_file_base}_matrix.csv"
    )

    if os.path.exists(save_file_nc):
        arr = update_stored_data_array(save_file_nc, arr)

    # Write dataArray to file
    arr.to_netcdf(save_file_nc)
    arr.to_pandas().to_csv(save_file_csv)
    return arr


def create_data_array(
    data: np.ndarray, taus: np.ndarray, img_pathname: str = ""
) -> xr.DataArray:
    """Create xarray dataArray

    Parameters
    ----------
    data : np.ndarray
        _description_
    taus : np.ndarray
        array of lag times
    img_pathfile : str
        pathname of microscopy source data

    Returns
    -------
    xr.dataArray
    """
    return xr.DataArray(
        data=data,
        dims=["tau", "q"],
        coords=dict(tau=taus, q=np.arange(data.shape[1])),
        attrs=dict(
            file=img_pathname, datetime=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        ),
    )


def update_stored_data_array(pathname: str, xr_arr: xr.DataArray) -> xr.DataArray:
    """Update dataArray with new lag times

    Parameters
    ----------
    pathname : str
        file location of stored data array
    xr_arr : xr.dataArray
        _description_

    Returns
    -------
    xr.dataArray
        Combined data arrays
    """
    arr_stored = xr.open_dataarray(pathname)
    assert (
        arr_stored.file == xr_arr.file
    ), "Data arrays have different source data files"

    arr_combined = xr.combine_by_coords([xr_arr, arr_stored], combine_attrs="override")
    arr_stored.close()
    return arr_combined
