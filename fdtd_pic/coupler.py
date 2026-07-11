"""Directional coupler FDTD simulation assembly."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import tidy3d as td

from fdtd_pic.config import (
    COUPLING_LENGTH,
    DEFAULT_WIDTH,
    FREQ0,
    FWIDTH,
    HEIGHT,
    MIN_STEPS_PER_WVL,
    PML_SPACING,
    RUN_TIME_FACTOR,
    WAVELENGTH,
)
from fdtd_pic.materials import si_medium, sio2_medium
from fdtd_pic.waveguide import make_substrate


@dataclass
class CouplerPortPowers:
    """Power fractions at the four coupler ports."""

    bar_in: float
    bar_through: float
    cross_through: float
    cross_out: float

    @property
    def total_output(self) -> float:
        return self.bar_through + self.cross_out

    @property
    def coupling_ratio(self) -> float:
        """Cross-port power fraction on the output side."""
        out = self.total_output
        if out <= 0:
            return 0.0
        return self.cross_out / out


def make_coupler_structures(
    gap: float,
    coupling_length: float = COUPLING_LENGTH,
    width: float = DEFAULT_WIDTH,
    lead_length: float = 3.0,
) -> list[td.Structure]:
    """Two parallel silicon strips with edge-to-edge gap ``gap`` (µm)."""
    y_lower = -(gap / 2 + width / 2)
    y_upper = gap / 2 + width / 2
    total_length = coupling_length + 2 * lead_length
    x_center = 0.0

    wg_lower = td.Structure(
        geometry=td.Box(
            center=(x_center, y_lower, 0.0),
            size=(total_length, width, HEIGHT),
        ),
        medium=si_medium(),
    )
    wg_upper = td.Structure(
        geometry=td.Box(
            center=(x_center, y_upper, 0.0),
            size=(total_length, width, HEIGHT),
        ),
        medium=si_medium(),
    )
    return [make_substrate(), wg_lower, wg_upper]


def build_coupler_simulation(
    gap: float,
    coupling_length: float = COUPLING_LENGTH,
    width: float = DEFAULT_WIDTH,
    lead_length: float = 3.0,
) -> td.Simulation:
    """Assemble a 3D FDTD simulation for the directional coupler."""
    structures = make_coupler_structures(gap, coupling_length, width, lead_length)
    y_lower = -(gap / 2 + width / 2)
    y_upper = gap / 2 + width / 2

    total_length = coupling_length + 2 * lead_length
    sim_x = total_length + 2 * PML_SPACING + WAVELENGTH
    sim_y = abs(y_upper - y_lower) + width + 2 * PML_SPACING + WAVELENGTH
    sim_z = HEIGHT + 2 * PML_SPACING

    x_in = -total_length / 2 + lead_length / 2
    x_out = total_length / 2 - lead_length / 2

    mode_spec = td.ModeSpec(num_modes=2)
    source_time = td.GaussianPulse(freq0=FREQ0, fwidth=FWIDTH)

    source = td.ModeSource(
        center=(x_in, y_lower, 0.0),
        size=(0, width, sim_z),
        source_time=source_time,
        direction="+",
        mode_spec=mode_spec,
        name="source",
    )

    monitor_bar_out = td.ModeMonitor(
        center=(x_out, y_lower, 0.0),
        size=(0, width, sim_z),
        freqs=[FREQ0],
        mode_spec=mode_spec,
        name="bar_out",
    )
    monitor_cross_out = td.ModeMonitor(
        center=(x_out, y_upper, 0.0),
        size=(0, width, sim_z),
        freqs=[FREQ0],
        mode_spec=mode_spec,
        name="cross_out",
    )
    field_monitor = td.FieldMonitor(
        center=(0, 0, 0),
        size=(td.inf, td.inf, 0),
        freqs=[FREQ0],
        name="field_xy",
    )

    return td.Simulation(
        size=(sim_x, sim_y, sim_z),
        center=(0, 0, 0),
        grid_spec=td.GridSpec.auto(
            min_steps_per_wvl=MIN_STEPS_PER_WVL,
            wavelength=WAVELENGTH,
        ),
        structures=structures,
        sources=[source],
        monitors=[monitor_bar_out, monitor_cross_out, field_monitor],
        run_time=RUN_TIME_FACTOR / FWIDTH,
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        medium=sio2_medium(),
    )


def _mode_power(sim_data: td.SimulationData, monitor_name: str, direction: str = "-") -> float:
    amps = sim_data[monitor_name].amps
    amp = amps.sel(direction=direction, f=FREQ0, mode_index=0)
    return float(np.abs(amp.values) ** 2)


def extract_port_powers(sim_data: td.SimulationData) -> CouplerPortPowers:
    """Extract normalized mode powers at bar and cross output ports."""
    bar_through = _mode_power(sim_data, "bar_out")
    cross_out = _mode_power(sim_data, "cross_out")
    return CouplerPortPowers(
        bar_in=1.0,
        bar_through=bar_through,
        cross_through=0.0,
        cross_out=cross_out,
    )


def coupling_ratio(sim_data: td.SimulationData) -> float:
    """Cross-port output power fraction."""
    return extract_port_powers(sim_data).coupling_ratio
