"""Ring resonator analytical and fitting helpers."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit


def analytical_fsr(
    radius: float,
    *,
    n_g: float = 4.2,
    wavelength: float = 1.55,
) -> float:
    """Free spectral range FSR ~ lambda^2 / (n_g * L), L = 2 pi r (µm)."""
    length = 2 * math.pi * radius
    return wavelength**2 / (n_g * length)


def analytical_fsr_hz(
    radius: float,
    *,
    n_g: float = 4.2,
    wavelength: float = 1.55,
) -> float:
    """Convert wavelength-domain FSR (µm) to frequency spacing (Hz)."""
    fsr_um = analytical_fsr(radius, n_g=n_g, wavelength=wavelength)
    lambda_m = wavelength * 1e-6
    dlambda_m = fsr_um * 1e-6
    return 299_792_458.0 * dlambda_m / lambda_m**2


def lorentzian(f: np.ndarray, f0: float, gamma: float, amplitude: float) -> np.ndarray:
    """Lorentzian lineshape (notch or peak depending on sign of data)."""
    half = gamma / 2.0
    return amplitude * half**2 / ((f - f0) ** 2 + half**2)


@dataclass
class ResonanceFit:
    """Fitted resonance parameters."""

    f0: float
    gamma: float
    amplitude: float
    q_factor: float


def fit_resonance(
    freqs: np.ndarray,
    transmission: np.ndarray,
    *,
    f0_guess: float | None = None,
) -> ResonanceFit:
    """Fit a Lorentzian to the deepest dip in the transmission spectrum."""
    freqs = np.asarray(freqs, dtype=float)
    transmission = np.asarray(transmission, dtype=float)

    idx_min = int(np.argmin(transmission))
    if f0_guess is None:
        f0_guess = float(freqs[idx_min])

    depth = float(transmission.max() - transmission.min())
    df = max(float(freqs[1] - freqs[0]) * 5, 1e11)
    p0 = (f0_guess, df, depth)

    # Fit inverted Lorentzian dip: T ~ 1 - Lorentzian
    def dip_model(f, f0, gamma, amp):
        return transmission.max() - lorentzian(f, f0, gamma, amp)

    popt, _ = curve_fit(
        dip_model,
        freqs,
        transmission,
        p0=p0,
        bounds=(
            (float(freqs.min()), 1e9, 0.0),
            (float(freqs.max()), float(np.ptp(freqs)), depth * 2),
        ),
        maxfev=10_000,
    )
    f0, gamma, amplitude = (float(popt[0]), float(popt[1]), float(popt[2]))
    q_factor = f0 / gamma if gamma > 0 else float("nan")
    return ResonanceFit(f0=f0, gamma=gamma, amplitude=amplitude, q_factor=q_factor)


def measured_fsr(freqs: np.ndarray, transmission: np.ndarray) -> float:
    """Estimate FSR from spacing between local minima in transmission."""
    freqs = np.asarray(freqs, dtype=float)
    transmission = np.asarray(transmission, dtype=float)
    # Simple: find two deepest minima
    from scipy.signal import find_peaks

    inverted = transmission.max() - transmission
    peaks, _ = find_peaks(inverted, distance=max(len(freqs) // 20, 3))
    if len(peaks) < 2:
        return float("nan")
    peak_freqs = freqs[peaks]
    order = np.argsort(inverted[peaks])[::-1]
    f_a, f_b = sorted(peak_freqs[order[:2]])
    return abs(f_b - f_a)
