"""Ring resonator FDTD simulation assembly."""

# problem at 3 oclock, fixing defection.


from __future__ import annotations

import numpy as np
import tidy3d as td

from fdtd_pic.config import (
    DEFAULT_WIDTH,
    FREQ0,
    FWIDTH,
    HEIGHT,
    MIN_STEPS_PER_WVL,
    PML_SPACING,
    RING_GAP,
    RING_RADIUS,
    RUN_TIME_FACTOR,
    WAVELENGTH,
)
from fdtd_pic.materials import si_medium, sio2_medium
from fdtd_pic.waveguide import make_substrate


Ring_run_time_factor = RUN_TIME_FACTOR * 2.0  # ring resonators take longer to converge

def _ring_vertices(
    radius: float,
    width: float,
    center: tuple[float, float],
    num_points: int = 72,
) -> list[tuple[float, float]]:
    """Closed polygon for a ring waveguide cross-section."""
    cx, cy = center
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    r_outer = radius + width / 2
    r_inner = max(radius - width / 2, width * 0.25)
    outer = [(cx + r_outer * np.cos(a), cy + r_outer * np.sin(a)) for a in angles]
    inner = [(cx + r_inner * np.cos(a), cy + r_inner * np.sin(a)) for a in angles[::-1]]
    return outer + inner


def make_ring_structures(
    radius: float = RING_RADIUS,
    gap: float = RING_GAP,
    width: float = DEFAULT_WIDTH,
    bus_length: float = 30.0,
) -> list[td.Structure]:
    """Bus waveguide + ring cavity."""
    ring_center_y = radius + gap + width

    bus = td.Structure(
        geometry=td.Box(
            center=(0.0, 0.0, 0.0),
            size=(bus_length, width, HEIGHT),
        ),
        medium=si_medium(),
    )
    ring_center = (0.0, ring_center_y, 0.0)
    r_outer = radius + width / 2
    r_inner = max(radius - width / 2, width * 0.25)

    outer = td.Cylinder(
        center=ring_center,
        axis=2,
        radius=r_outer,
        length=HEIGHT,
    )
    inner = td.Cylinder(
        center=ring_center,
        axis=2,
        radius=r_inner,
        length=HEIGHT,
    )
    ring = td.Structure(
        geometry=outer - inner,
        medium=si_medium(),
    )

    return [make_substrate(), bus, ring]


def build_ring_simulation(
    radius: float = RING_RADIUS,
    gap: float = RING_GAP,
    width: float = DEFAULT_WIDTH,
    bus_length: float = 30.0,
    num_freqs: int = 101,
) -> td.Simulation:
    """Broadband FDTD simulation of a single-bus ring resonator."""
    structures = make_ring_structures(radius, gap, width, bus_length)
    ring_center_y = radius + gap + width

    r_outer = radius + width / 2

    # Extents of bus + ring
    y_min = min(-width / 2, ring_center_y - r_outer)
    y_max = max(width / 2, ring_center_y + r_outer)
    x_min = min(-bus_length / 2, -r_outer)
    x_max = max(bus_length / 2, r_outer)

    buffer = WAVELENGTH
    sim_x = (x_max - x_min) + 2 * PML_SPACING + buffer
    sim_y = (y_max - y_min) + 2 * PML_SPACING + buffer
    sim_z = HEIGHT + 2 * PML_SPACING

    sim_center = (
        (x_max + x_min) / 2,
        (y_max + y_min) / 2,
        0.0,
    )

    x_src = -bus_length / 2 + PML_SPACING + 0.5
    x_mon = bus_length / 2 - PML_SPACING - 0.5

    freqs = np.linspace(FREQ0 - FWIDTH, FREQ0 + FWIDTH, num_freqs)
    source_time = td.GaussianPulse(freq0=FREQ0, fwidth=FWIDTH)

    source = td.ModeSource(
        center=(x_src, 0.0, 0.0),
        size=(0, width + 2 * PML_SPACING, sim_z),
        source_time=source_time,
        direction="+",
        mode_spec=td.ModeSpec(num_modes=1),
        name="source",
    )
    flux_in = td.FluxMonitor(
        center=(x_src + 0.5, 0.0, 0.0),
        size=(0, width + 2 * PML_SPACING, sim_z),
        freqs=freqs.tolist(),
        name="flux_in",
    )
    flux_out = td.FluxMonitor(
        center=(x_mon, 0.0, 0.0),
        size=(0, width + 2 * PML_SPACING, sim_z),
        freqs=freqs.tolist(),
        name="flux_out",
    )
    field_monitor = td.FieldMonitor(
        center=(0, ring_center_y / 2, 0),
        size=(td.inf, td.inf, 0),
        freqs=[FREQ0],
        name="field_xy",
    )

    return td.Simulation(
        size=(sim_x, sim_y, sim_z),
        center=sim_center,
        grid_spec=td.GridSpec.auto(
            min_steps_per_wvl=MIN_STEPS_PER_WVL,
            wavelength=WAVELENGTH,
        ),
        structures=structures,
        sources=[source],
        monitors=[flux_in, flux_out, field_monitor],
        run_time=5e-10, # need ns runtime for ring energy to decay...
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        medium=sio2_medium(),
    )


def extract_transmission_spectrum(sim_data: td.SimulationData) -> tuple[np.ndarray, np.ndarray]:
    """Return (frequencies_Hz, normalized_through_flux)."""
    flux_in = np.abs(sim_data["flux_in"].flux.values)
    flux_out = np.abs(sim_data["flux_out"].flux.values)
    freqs = np.array(sim_data["flux_out"].flux.f)
    with np.errstate(divide="ignore", invalid="ignore"):
        transmission = np.where(flux_in > 0, flux_out / flux_in, 0.0)
    return freqs, transmission
