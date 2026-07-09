#!/usr/bin/env python3
"""Minimal local ModeSolver smoke test (no cloud credits)."""

from __future__ import annotations

import sys


def main() -> int:
    from fdtd_pic.modes import solve_modes

    result = solve_modes(0.5)
    print(f"Mode solve OK @ width=0.5 um")
    print(f"  n_eff (all modes): {result.n_eff}")
    print(f"  TE00 n_eff: {result.n_eff[0]:.4f}")
    if result.n_eff[0] < 1.5 or result.n_eff[0] > 3.5:
        print("WARN: n_eff outside expected range for Si strip")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
