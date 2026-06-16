# Log — 2026-06-16-snap-fit-enclosure

Chronological record of the verify-and-revise loop. The harness
(`run.py`) starts from `START_PARAMS` (deliberately defective) and walks
to the all-pass design in `config.yaml`, one fix per cycle. Re-run with
`../../.venv/bin/python run.py` from this folder.

Toolchain notes:
- build123d 0.10.0 (OCP/OCCT) installed via `uv add build123d`.
- `which ccx` / `which freecadcmd` / `which gmsh` all empty on this host
  -> strength gate uses the closed-form cantilever screen (proposal
  fallback), NOT real FEA.

## Run trace (seed 42)

Strength gate: closed-form cantilever (eps = 3*t*delta / 2*L^2); CalculiX absent.

### Cycle 0 — FAIL

- clearance=0.0 mm, min_wall=1.0 mm, overhang=70.0 deg, interference=0.0 mm^3, strain=0.08 (margin 0.5)
- failures: clearance_in_band, min_wall_ok, overhang_ok, strength_ok
- FIX: min-wall fail (wall_t too thin) -> wall_t 1.0->2.0 mm

### Cycle 1 — FAIL

- clearance=0.0 mm, min_wall=1.6 mm, overhang=70.0 deg, interference=0.0 mm^3, strain=0.08 (margin 0.5)
- failures: clearance_in_band, overhang_ok, strength_ok
- FIX: clearance/interference fail -> clearance 0.00->0.20 mm (mid-band)

### Cycle 2 — FAIL

- clearance=0.2 mm, min_wall=1.6 mm, overhang=70.0 deg, interference=0.0 mm^3, strain=0.08 (margin 0.5)
- failures: overhang_ok, strength_ok
- FIX: overhang fail -> hook lead-in 70->45 deg (support-free)

### Cycle 3 — FAIL

- clearance=0.2 mm, min_wall=1.6 mm, overhang=45.0 deg, interference=0.0 mm^3, strain=0.08 (margin 0.5)
- failures: strength_ok
- FIX: strength fail -> arm L 6->12 mm, t 2.4->1.6 mm (cut surface strain)

### Cycle 4 — PASS (all gates)

- clearance=0.2 mm, min_wall=1.6 mm, overhang=45.0 deg, interference=0.0 mm^3, strain=0.013333 (margin 3.0)

**Converged in 4 revise cycles** (budget 5). Failures caught automatically by the loop: 10; left to human: 0.
