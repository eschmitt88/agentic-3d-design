#!/usr/bin/env python
"""Mesh one or more STEP files to STL (for the browser QA viewer).

STEP carries exact B-rep + assembly transforms; the web viewer (Online3DViewer)
wants a triangulated mesh. This converts in place: foo.step -> foo.stl.

Usage:
    python tools/step_to_stl.py <file.step> [<file2.step> ...]
    python tools/step_to_stl.py experiments/<slug>/results/*.step

Run with the project venv: `.venv/bin/python tools/step_to_stl.py ...`
"""
from __future__ import annotations

import sys
from pathlib import Path

from build123d import import_step, export_stl


def convert(step_path: Path) -> Path:
    shape = import_step(str(step_path))
    stl_path = step_path.with_suffix(".stl")
    # tolerance/angular_tolerance: fine enough for visual QA, small files.
    export_stl(shape, str(stl_path), tolerance=0.05, angular_tolerance=0.2)
    return stl_path


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    rc = 0
    for arg in argv:
        p = Path(arg)
        if not p.exists() or p.suffix.lower() not in {".step", ".stp"}:
            print(f"skip (not a STEP file): {p}")
            rc = 1
            continue
        out = convert(p)
        print(f"{p} -> {out} ({out.stat().st_size} bytes)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
