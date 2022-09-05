from pathlib import Path

import pytest
import xarray
import dask
import numpy

from ddm.data_handling.read_file import read_file
from ddm.utils import verify_bioformats_jar

THIS_DIR = Path(__file__).parent

# Catch problem with jar library
verify_bioformats_jar


def test_unsupported_filetype():
    with pytest.raises(ValueError) as exc_info:
        read_file("test.abc")
    assert "image format" in str(exc_info.value)


def test_load_unknown_file():
    with pytest.raises(OSError):
        read_file("test.tif")  # non-existing file


def test_import_lif_type():
    data_path = THIS_DIR / "data/testData1series.lif"
    data = read_file(data_path)
    assert isinstance(data, xarray.DataArray)


def test_import_lif_multi_experiment():
    data_path = THIS_DIR / "data/testData3series.lif"
    data = read_file(data_path, experiment=1)
    assert isinstance(data, xarray.DataArray)


def test_lif_invalid_index_experiment(monkeypatch):
    data_path = THIS_DIR / "data/testData3series.lif"
    monkeypatch.setattr("builtins.input", lambda _: 4)
    with pytest.raises(IndexError) as exc_info:
        read_file(data_path)
    assert "out of bounds" in str(exc_info.value)


def test_lif_invalid_type_experiment(monkeypatch):
    data_path = THIS_DIR / "data/testData3series.lif"
    monkeypatch.setattr("builtins.input", lambda _: "a")
    with pytest.raises(TypeError) as exc_info:
        read_file(data_path)
    assert "value should be an integer" in str(exc_info.value)


def test_import_nd2_type():
    data_path = THIS_DIR / "data/testData10frames.nd2"
    data = read_file(data_path)
    assert isinstance(data, xarray.DataArray)


def test_import_tif_type():
    data_path = THIS_DIR / "data/21-03-31_ddm_fb_2mg-mll_sample.tif"
    data = read_file(data_path, delayed=False)
    assert isinstance(data, xarray.DataArray)
    assert isinstance(data.data, numpy.ndarray)


def test_import_tif_img_selection():
    data_path = THIS_DIR / "data/21-03-31_ddm_fb_2mg-mll_sample.tif"
    data = read_file(data_path, delayed=False, img_selection=slice(0, 5, 1))
    assert data.shape[0] == 5


def test_import_tif_type_delayed():
    data_path = THIS_DIR / "data/21-03-31_ddm_fb_2mg-mll_sample.tif"
    data = read_file(data_path, delayed=True)
    assert isinstance(data, xarray.DataArray)
    assert isinstance(data.data, dask.array.core.Array)


def test_custom_scales_tif():
    data_path = THIS_DIR / "data/21-03-31_ddm_fb_2mg-mll_sample.tif"
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
