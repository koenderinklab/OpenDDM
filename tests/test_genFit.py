import pytest

import numpy as np

from ddm.fitting import genFit

def test_unsupported_function():
    with pytest.raises(ValueError) as exc_info:
        genFit(None, None, "foo")
    assert "fitting function" in str(exc_info.value)

def test_fitting_dummy_singleExp():
    a = 1000.
    b = 2.
    tData = np.linspace(0.,2.*a,1000)
    isfData = np.exp(-1.*(tData/a)**b) 
    isfData += np.random.normal(0.0, isfData/100., 1000)
    popt, pcov = genFit(isfData, tData, 'singleExp')
    assert (np.abs(popt - [a,b]) < [a/100.,b/100.]).all()
    
def test_fitting_dummy_doubleExp():
    tau1 = 10.
    tau2 = 200.
    frac = 0.3
    s1 = 1.2
    s2 = 1.1
    tData = np.linspace(0., 10.*np.max([tau1, tau2]), 1000)
    isfData = frac*np.exp(-1.*(tData/tau1)**s1) + (1. - frac)*np.exp(-1.*(tData/tau2)**s2)
    isfData += np.random.normal(0.0, isfData/1000., 1000)
    popt, pcov = genFit(isfData, tData, 'doubleExp')
    assert (np.abs(popt - [tau1, tau2, frac, s1, s2]) < [tau1/100., tau2/100., frac/100., s1/100., s2/100.]).all() or (np.abs(popt - [tau2, tau1, 1.-frac, s2, s1]) < [tau2/100., tau1/100., (1-frac)/100., s2/100., s1/100.]).all()
    
def test_fitting_linear():
    tau = 0.1
    b = 1.
    tData = np.linspace(0.,tau/10., 1000)
    isfData = np.exp(-1.*(tData/tau)**b)
    with pytest.raises(ValueError) as exc_info:
        genFit(isfData, tData, 'singleExp')
    assert "very little decorrelation" in str(exc_info.value)
