"""Coupled-mode theory helpers for directional coupler comparison."""

from __future__ import annotations

import math


def cross_power_fraction(
    coupling_length: float,
    gap: float,
    *,
    kappa_scale: float = 3.0,
    gap_decay_um: float = 0.1,
) -> float:
    """Qualitative CMT estimate: |sin(kappa * L)|^2 with kappa ~ exp(-gap/decay).

  Matches the phenomenological model in PIC-component-Library
  ``directional_coupler.cross_power_fraction`` for overlay plots.
    """
    kappa = kappa_scale * math.exp(-gap / gap_decay_um)
    return math.sin(kappa * coupling_length) ** 2


def cross_power_curve(
    gaps: tuple[float, ...] | list[float],
    coupling_length: float,
    **kwargs: float,
) -> list[float]:
    """Evaluate cross_power_fraction over a list of gaps."""
    return [cross_power_fraction(coupling_length, g, **kwargs) for g in gaps]


def kappa_from_cross_fraction(cross_fraction: float, coupling_length: float) -> float:
    """Infer effective κ (µm⁻¹) from output split η ≈ sin²(κL)."""
    eta = max(0.0, min(1.0, cross_fraction))
    return math.asin(math.sqrt(eta)) / coupling_length


def kappa_curve_from_ratios(
    gaps: tuple[float, ...] | list[float],
    ratios: tuple[float, ...] | list[float],
    coupling_length: float,
) -> list[float]:
    """κ(g) extracted from FDTD coupling ratios."""
    return [kappa_from_cross_fraction(r, coupling_length) for r in ratios]


def fit_kappa_exponential(
    gaps: tuple[float, ...] | list[float],
    kappas: tuple[float, ...] | list[float],
) -> tuple[float, float]:
    """Fit κ(g) = κ₀ exp(−g / g₀). Returns (kappa_0, gap_decay_um)."""
    import numpy as np
    from scipy.optimize import curve_fit

    def model(g, k0, decay):
        return k0 * np.exp(-np.asarray(g) / decay)

    p0 = (float(kappas[0]), 0.12)
    k0, decay = curve_fit(model, gaps, kappas, p0=p0, maxfev=10_000)[0]
    return float(k0), float(decay)


def cross_power_curve_fitted(
    gaps: tuple[float, ...] | list[float],
    coupling_length: float,
    kappa_0: float,
    gap_decay_um: float,
) -> list[float]:
    """sin²(κ(g)L) using κ fitted from FDTD."""
    return [
        math.sin(kappa_0 * math.exp(-g / gap_decay_um) * coupling_length) ** 2
        for g in gaps
    ]