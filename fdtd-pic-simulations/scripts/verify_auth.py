#!/usr/bin/env python3
"""Verify Tidy3D installation and API authentication."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        import tidy3d as td
        import tidy3d.web as web
    except ImportError as exc:
        print(f"FAIL: tidy3d not installed — pip install -e '.[dev]'\n  {exc}")
        return 1

    print(f"Tidy3D version: {td.__version__}")

    try:
        account = web.account(verbose=False)
        credit = getattr(account, "credit", None) or getattr(account, "flex_credit", None)
        if credit is not None:
            print(f"Authentication OK. Account credit: {credit}")
        else:
            print(f"Authentication OK. Account: {account}")
    except Exception as exc:
        print("FAIL: Tidy3D not authenticated.")
        print("  Run: tidy3d configure")
        print(f"  ({exc})")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
