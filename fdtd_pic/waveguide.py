"""Strip waveguide geometry helpers."""

from __future__ import annotations

import tidy3d as td

from fdtd_pic.config import HEIGHT
from fdtd_pic.materials import si_medium, sio2_medium


def make_substrate(z_top: float = -HEIGHT / 2) -> td.Structure:
    """Semi-infinite SiO2 substrate below the silicon slab."""
    return td.Structure(
        geometry=td.Box(
            center=(0, 0, z_top - 5.0),
            size=(td.inf, td.inf, 10.0),
        ),
        medium=sio2_medium(),
    )


def make_strip_core(
    width: float,
    length: float = 2.0,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> td.Structure:
    """Single silicon strip (propagation along x)."""
    cx, cy, cz = center
    return td.Structure(
        geometry=td.Box(
            center=(cx, cy, cz),
            size=(length, width, HEIGHT),
        ),
        medium=si_medium(),
    )


def make_strip_waveguide(
    width: float,
    length: float = 2.0,
) -> list[td.Structure]:
    """Si strip on SiO2 substrate (mode-solver / compact FDTD building block)."""
    return [
        make_substrate(),
        make_strip_core(width=width, length=length, center=(0.0, 0.0, 0.0)),
    ]
