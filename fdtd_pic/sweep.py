"""Generic parameter sweep runner for Tidy3D cloud jobs."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import tidy3d as td
import tidy3d.web as web


def sweep_param(
    build_fn: Callable[..., td.Simulation],
    param_name: str,
    values: tuple[float, ...] | list[float],
    task_prefix: str,
    cache_dir: str | Path = ".tidy3d_cache",
    verbose: bool = True,
    **fixed_kwargs: Any,
) -> dict[float, td.SimulationData]:
    """Run ``build_fn(**{param_name: value, **fixed_kwargs})`` for each value.

    Results are cached as JSON metadata + SimulationData hdf5 in ``cache_dir``.
    """
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    results: dict[float, td.SimulationData] = {}

    for value in values:
        key = f"{task_prefix}_{param_name}={value:.4f}"
        cache_file = cache / f"{key}.hdf5"
        meta_file = cache / f"{key}.json"

        if cache_file.exists():
            if verbose:
                print(f"Loading cached: {key}")
            results[float(value)] = td.SimulationData.from_file(str(cache_file))
            continue

        kwargs = {**fixed_kwargs, param_name: value}
        sim = build_fn(**kwargs)
        if verbose:
            print(f"Running: {key}")
        sim_data = web.run(sim, task_name=key, verbose=verbose)
        sim_data.to_file(str(cache_file))
        meta_file.write_text(json.dumps({"param": param_name, "value": value}), encoding="utf-8")
        results[float(value)] = sim_data

    return results
