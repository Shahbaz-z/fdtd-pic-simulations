"""Geometry unit tests (structure placement, no cloud)."""

from __future__ import annotations

from fdtd_pic.config import COUPLING_LENGTH, DEFAULT_WIDTH, HEIGHT
from fdtd_pic.coupler import make_coupler_structures
from fdtd_pic.waveguide import make_strip_waveguide


def test_strip_waveguide_has_two_structures():
    structs = make_strip_waveguide(0.5)
    assert len(structs) == 2


def test_coupler_gap_centers():
    gap = 0.2
    structs = make_coupler_structures(gap, COUPLING_LENGTH, DEFAULT_WIDTH)
    # substrate + lower + upper
    assert len(structs) == 3
    lower = structs[1].geometry
    upper = structs[2].geometry
    y_sep = upper.center[1] - lower.center[1]
    expected = gap + DEFAULT_WIDTH
    assert abs(y_sep - expected) < 1e-9


def test_strip_height_matches_soi():
    structs = make_strip_waveguide(0.5)
    core = structs[1].geometry
    assert abs(core.size[2] - HEIGHT) < 1e-9
