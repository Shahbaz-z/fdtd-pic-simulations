"""Shared SOI stack and simulation defaults (aligned with PIC-component-Library)."""

from __future__ import annotations

import tidy3d as td

# --- Material indices at 1550 nm ---
N_SI = 3.48
N_SIO2 = 1.44

# --- Geometry (µm) ---
WAVELENGTH = 1.55
HEIGHT = 0.22
DEFAULT_WIDTH = 0.5
COUPLING_LENGTH = 10.0
RING_RADIUS = 10.0
RING_GAP = 0.2

# --- Frequency helpers ---
FREQ0 = td.C_0 / WAVELENGTH
FWIDTH = FREQ0 / 10

# --- Mode solver domain (µm) ---
MODE_PLANE_SIZE = (8.0, 8.0)
MODE_SOLVER_NUM_MODES = 4

# --- FDTD grid / runtime ---
MIN_STEPS_PER_WVL = 15
RUN_TIME_FACTOR = 10  # run_time = RUN_TIME_FACTOR / fwidth
PML_SPACING = 2.0 * WAVELENGTH

# --- Sweeps ---
import numpy as np

WIDTH_SWEEP = tuple(float(w) for w in np.linspace(0.3, 0.8, 100)) # want smooth graphs so have 100 points between 300 and 800 nm
PROFILE_WIDTHS_UM = (0.3, 0.5, 0.7)
GAP_SWEEP = (0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4)

# --- Ring analytics ---
N_GROUP = 4.2
