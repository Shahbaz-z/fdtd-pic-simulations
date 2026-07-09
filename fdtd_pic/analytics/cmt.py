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
