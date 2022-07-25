import pytest

from ddm.fitting import genFit

def test_unsupported_function():
    with pytest.raises(ValueError) as exc_info:
        genFit(None, None, "foo")
    assert "fitting function" in str(exc_info.value)