from pathlib import Path
from ddm.data_handling import read_file
import pims
import pytest
import xarray
from urllib.error import HTTPError

THIS_DIR = Path(__file__).parent

# Catch problem with jar library
try:
    pims.bioformats._find_jar()
except HTTPError:
    pims.bioformats.download_jar(version="6.5")


def test_unsupported_filetype():
    with pytest.raises(ValueError) as exc_info:
        read_file("test.abc")
    assert "image format" in str(exc_info.value)


def test_load_unknown_file():
    with pytest.raises(OSError):
        read_file("test.tif")  # file does not exist


def test_import_lif_type():
    data_path = THIS_DIR / "data/testData1series.lif"
    data = read_file(data_path)
    assert isinstance(data, xarray.DataArray)


def test_import_nd2_type():
    data_path = THIS_DIR / "data/testData10frames.nd2"
    data = read_file(data_path)
    assert isinstance(data, xarray.DataArray)


def test_import_tif_type():
    data_path = THIS_DIR / "data/21-03-31_ddm_fb_2mg-mll_sample.tif"
    data = read_file(data_path)
    assert isinstance(data, xarray.DataArray)


def test_custom_scales_tif():
    data_path = THIS_DIR / "data/testData10frames.nd2"
    expected_result = 5
    data = read_file(data_path, xscale=expected_result, tscale=expected_result)
    assert data.attrs["xyScale"] == expected_result
    assert data.attrs["tScale"] == expected_result


def test_custom_scales_lif():
    data_path = THIS_DIR / "data/testData1series.lif"
    expected_result = 10
    data = read_file(data_path, xscale=expected_result, tscale=expected_result)
    assert data.attrs["xyScale"] == expected_result
    assert data.attrs["tScale"] == expected_result


def test_metadata_lif():
    pytest.fail()


def test_metadata_tif():
    pytest.fail()


def test_metadata_nd2():
    pytest.fail()
