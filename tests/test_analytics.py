"""Unit tests for analytical helpers (no Tidy3D cloud)."""

from __future__ import annotations

import numpy as np

from fdtd_pic.analytics.cmt import cross_power_fraction, cross_power_curve
from fdtd_pic.analytics.ring import analytical_fsr, fit_resonance, lorentzian


def test_cross_power_bounded():
    eta = cross_power_fraction(10.0, 0.2)
    assert 0.0 <= eta <= 1.0


def test_cross_power_curve_length():
    gaps = (0.1, 0.2, 0.3)
    curve = cross_power_curve(gaps, coupling_length=10.0)
    assert len(curve) == 3


def test_analytical_fsr_positive():
    fsr = analytical_fsr(10.0)
    assert fsr > 0


def test_lorentzian_peak():
    f = np.linspace(190e12, 200e12, 500)
    f0 = 195e12
    gamma = 0.5e12
    y = lorentzian(f, f0, gamma, 1.0)
    assert abs(y.max() - 1.0) < 0.01


def test_fit_resonance_synthetic_dip():
    f = np.linspace(190e12, 200e12, 400)
    f0 = 195e12
    gamma = 0.3e12
    baseline = 0.95
    dip = baseline - lorentzian(f, f0, gamma, 0.4)
    fit = fit_resonance(f, dip, f0_guess=194e12)
    assert abs(fit.f0 - f0) / f0 < 0.02
    assert fit.q_factor > 100
