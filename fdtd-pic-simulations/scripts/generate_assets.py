#!/usr/bin/env python3
"""Generate README asset PNGs from local ModeSolver (no cloud)."""

from __future__ import annotations

import matplotlib.pyplot as plt

from fdtd_pic.config import PROFILE_WIDTHS_UM, WIDTH_SWEEP
from fdtd_pic.modes import solve_modes, sweep_widths
from fdtd_pic.plotting import apply_style, save_figure


def main() -> None:
    apply_style()
    assets = __import__("pathlib").Path(__file__).resolve().parent.parent / "assets"

    widths_um, n_eff = sweep_widths(WIDTH_SWEEP)
    fig, ax = plt.subplots()
    ax.plot(widths_um * 1000, n_eff, "o-")
    ax.set_xlabel("Width (nm)")
    ax.set_ylabel(r"$n_{\mathrm{eff}}$ (mode 0)")
    ax.set_title("Effective index vs width — 220 nm SOI @ 1550 nm")
    save_figure(fig, assets / "mode_neff_vs_width.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    for ax, w in zip(axes, PROFILE_WIDTHS_UM):
        result = solve_modes(w)
        result.mode_solver.plot_field(field_name="Ez", val="abs", mode_index=0, ax=ax)
        ax.set_title(f"w = {int(w * 1000)} nm")
    fig.suptitle(r"$|E_z|$ mode profiles (fundamental)")
    fig.tight_layout()
    save_figure(fig, assets / "mode_profiles_3widths.png")
    plt.close(fig)

    print(f"Wrote assets to {assets}")


if __name__ == "__main__":
    main()
