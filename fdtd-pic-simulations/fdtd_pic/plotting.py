"""Shared matplotlib helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def save_figure(fig: plt.Figure, path: str | Path, dpi: int = 150) -> Path:
    """Save figure and return resolved path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    return out


def apply_style() -> None:
    """Consistent plot style across notebooks."""
    plt.rcParams.update(
        {
            "figure.figsize": (7, 4.5),
            "axes.grid": True,
            "grid.alpha": 0.3,
            "font.size": 11,
        }
    )
