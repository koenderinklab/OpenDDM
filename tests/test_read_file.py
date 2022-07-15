from pathlib import Path

import pytest
import xarray

from ddm.data_handling import read_file
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


def test_lif_invalid_user_input_experiment(monkeypatch):
    data_path = THIS_DIR / "data/testData3series.lif"
    monkeypatch.setattr("builtins.input", lambda _: 4)
    with pytest.raises(IndexError) as exc_info:
        read_file(data_path)
    assert "index out of bounds" in str(exc_info.value)


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
