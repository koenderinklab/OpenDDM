from pathlib import Path

import pytest

from openddm.data_handling.read_metadata import read_metadata
from openddm.utils import verify_bioformats_jar

THIS_DIR = Path(__file__).parent

# Catch problem with jar library
verify_bioformats_jar


def test_unsupported_data_type():
    with pytest.raises(ValueError) as exc_info:
        read_metadata("test.abc")
    assert "metadata reader" in str(exc_info.value)


def test_read_metadata_nd2():
    data_path = THIS_DIR / "data/testData10frames.nd2"
    metadata = read_metadata(data_path)
    assert isinstance(metadata, dict)
    assert type(metadata["xscale"]) is float
    assert type(metadata["tscale"]) is float


def test_read_metadata_tif():
    data_path = THIS_DIR / "data/21-03-31_ddm_water_control_sample.tif"
    metadata = read_metadata(data_path)
    assert isinstance(metadata, dict)
    assert type(metadata["xscale"]) is float
    assert type(metadata["tscale"]) is float


def test_read_metadata_lif():
    data_path = THIS_DIR / "data/testData1series.lif"
    metadata = read_metadata(data_path)
    assert isinstance(metadata, dict)
    assert type(metadata["xscale"]) is float
    assert type(metadata["tscale"]) is float
    assert metadata["n_experiments"] == 1


def test_read_metadata_multi_lif():
    data_path = THIS_DIR / "data/testData3series.lif"
    metadata = read_metadata(data_path)
    assert metadata["n_experiments"] == 3
