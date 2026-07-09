"""Tidy3D medium definitions for the SOI stack."""

from __future__ import annotations

import tidy3d as td

from fdtd_pic.config import N_SI, N_SIO2


def si_medium() -> td.Medium:
    """Silicon core at 1550 nm (lossless, n = 3.48)."""
    return td.Medium(permittivity=N_SI**2)


def sio2_medium() -> td.Medium:
    """Silicon dioxide cladding / substrate (n = 1.44)."""
    return td.Medium(permittivity=N_SIO2**2)
