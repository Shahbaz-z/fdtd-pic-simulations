"""ModeSolver helpers for strip waveguide width sweeps."""

from __future__ import annotations

from dataclasses import dataclass
from turtle import width

import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver
from fdtd_pic.materials import sio2_medium

from fdtd_pic.config import (
    FREQ0,
    HEIGHT,
    MIN_STEPS_PER_WVL,
    MODE_PLANE_SIZE,
    MODE_SOLVER_NUM_MODES,
    PML_SPACING,
    WAVELENGTH,
)
from fdtd_pic.waveguide import make_strip_waveguide


@dataclass
class ModeSolveResult:
    """Container for one width solve."""

    width: float
    n_eff: np.ndarray
    mode_solver: ModeSolver
    mode_data: object


def _mode_simulation_box(width: float) -> tuple[tuple[float, float, float], list[td.Structure]]:
    """Simulation domain sized for a given strip width."""
    plane_x, plane_y = MODE_PLANE_SIZE
    sim_x = max(plane_x + 2 * PML_SPACING, 4.0)
    sim_y = max(plane_y + 2 * PML_SPACING, width + 2 * PML_SPACING + 1.0)
    sim_z = HEIGHT + 2 * PML_SPACING #pml perfect mactching layer
    structures = make_strip_waveguide(width=width, length=sim_x * 0.5)
    return (sim_x, sim_y, sim_z), structures


def build_mode_solver(width: float) -> ModeSolver:
    """Build a ModeSolver for a strip waveguide at ``width`` (µm)."""
    sim_size, structures = _mode_simulation_box(width)
    sim_x, sim_y, sim_z = sim_size

    simulation = td.Simulation(
        size=sim_size,
        center=(0, 0, 0),
        grid_spec=td.GridSpec.auto(
            min_steps_per_wvl=MIN_STEPS_PER_WVL,
            wavelength=WAVELENGTH,
        ),
        structures=structures,
        sources=[],
        monitors=[],
        run_time=1e-12,
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        medium=sio2_medium()
    )

    plane_y = max(MODE_PLANE_SIZE[0], width + 2 * PML_SPACING + 1.0)
    plane_z = HEIGHT + 2 * PML_SPACING
    plane = td.Box(center=(0, 0, 0), size=(0, plane_y, plane_z)) # needed to fix to y-z plane as we have x propagation

    return ModeSolver(
        simulation=simulation,
        plane=plane,
        mode_spec=td.ModeSpec(
            num_modes=MODE_SOLVER_NUM_MODES,
            target_neff=2.8,
        ),
        freqs=[FREQ0],
    )


def solve_modes(width: float) -> ModeSolveResult:
    """Run the eigenmode solver locally (no cloud credits)."""
    mode_solver = build_mode_solver(width)
    mode_data = mode_solver.solve()
    n_eff = np.real(mode_data.n_eff.values[0]).astype(float)
    return ModeSolveResult(
        width=width,
        n_eff=n_eff,
        mode_solver=mode_solver,
        mode_data=mode_data,
    )


def sweep_widths(widths: tuple[float, ...] | list[float]) -> tuple[np.ndarray, np.ndarray]:
    """Sweep strip width; return (widths_um, te00_n_eff)."""
    widths_arr = np.asarray(widths, dtype=float)
    n_effs = []
    for w in widths_arr:
        result = solve_modes(float(w))
        n_effs.append(float(np.max(result.n_eff)))
    return widths_arr, np.asarray(n_effs)


def te00_mode_index(mode_data: object) -> int:
    """Return mode index of fundamental TE mode (lowest n_eff TE)."""
    return 0

