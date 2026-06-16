---
kind: experiment
slug: "2026-06-16-snap-fit-enclosure"
date: "2026-06-16"
status: done
hypothesis: >
  A build123d-writing agent in a closed verify-and-revise loop (OCCT
  validity + DFM diagnostics + rendered-PNG review + a CalculiX-or-
  closed-form strength check on the snap arm) can produce a parametric
  two-part snap-fit enclosure that mates at target clearance, satisfies
  FDM DFM constraints, and whose cantilever snap flexes to engage without
  exceeding material yield — reaching a passing design in <=5 revise cycles.
result: >
  All 8 gates pass after 4 revise cycles (budget 5). Final design:
  clearance 0.20 mm, min wall 1.6 mm, all overhangs <=45 deg, zero
  box-lid interference, snap peak strain 0.0133 vs PETG yield 0.04
  (margin 3.0). Strength via closed-form cantilever (no CalculiX on host).
related_concepts: []
related_literature:
  - "literature/posts/2026-06-16-agentic-cad-landscape.md"
tags: [code-cad, build123d, snap-fit, dfm, verify-revise-loop, fea-fallback]
---

# 2026-06-16-snap-fit-enclosure

## Hypothesis

A build123d-writing agent, given a closed verification loop (OCCT
validity + DFM diagnostics + rendered-PNG review, and a strength check on
the snap arm), can produce a parametric two-part snap-fit enclosure that
mates at a target clearance, satisfies FDM DFM constraints (min wall,
support-free overhangs, no interference), and whose cantilever snap flexes
to engage without exceeding material yield — reaching a passing design in
a small number of revise cycles (target <=5).

## Setup

- Config: `config.yaml` — all design parameters, PETG material constants,
  gate thresholds, `seed: 42`.
- Code:
  - `src/enclosure.py` — `build(params) -> (box, lid, diagnostics)`. A
    parametric box (L x W x H, walls, floor) with through-window mating
    slots in the long walls + a lid with a perimeter lip skirt and N
    cantilever snap arms ending in hooks that catch the windows.
  - `run.py` — the verify-and-revise harness. Starts from a deliberately
    wrong parameter set (`START_PARAMS`), runs all 8 gate checks each
    cycle, applies one targeted fix per cycle, and converges; then exports
    STEP/STL, renders a 3-view PNG, and writes `metrics.json` + `log.md`.
- Toolchain: build123d 0.10.0 (OCP/OCCT kernel) in the project `uv` venv.
  CalculiX / FreeCAD / gmsh are **absent** on this host, so the strength
  gate uses the proposal-permitted closed-form cantilever screen.
- Data: none (deterministic geometry; no learned model, no split).

## Result

All 8 gates pass (`metrics.json:all_gates_pass` = true) after **4 revise
cycles** (`metrics.json:cycles_to_first_all_pass`), inside the budget of 5.

Final converged numbers (`metrics.json:final_numbers`):

| gate | value | threshold | pass |
|---|---|---|---|
| lid-box clearance | 0.20 mm | 0.15-0.25 mm | yes |
| min wall | 1.6 mm | >=1.5 mm | yes |
| max overhang | 45.0 deg | <=45 deg | yes |
| box<->lid interference | 0.0 mm^3 | ~0 | yes |
| snap peak strain | 0.0133 | < yield 0.04 | yes |
| strain margin | 3.0 | >=1.5 | yes |
| OCCT solid validity (box, lid) | valid | valid | yes |
| snap reachable | true | true | yes |

The verify-revise trace (`log.md`) shows the loop catching, in order:
min-wall (cycle 0), clearance (cycle 1), overhang (cycle 2), and snap-arm
strength (cycle 3), reaching all-pass at cycle 4. Ten gate failures were
caught automatically by the loop across the four revise cycles; zero were
left to a human (`metrics.json:process`).

Artifacts in `results/`: `box.step/stl`, `lid.step/stl`,
`assembled_closed.step`, `assembled_exploded.step`, and `three_view.png`
(box, lid, exploded assembly). All exports are well under 10 MB and are
git-committed.

## Interpretation

The closed loop did exactly the job the project hypothesis ascribes to it:
each automatically-computed diagnostic (OCCT validity, a boolean-
intersection interference test, a geometric min-wall/overhang measure, and
a cantilever-strain screen) pinned a specific manufacturability defect and
drove a single parameter fix, converging deterministically. The one design
insight surfaced by the loop: a **blind** snap pocket leaves only
`wall_t - hook_depth` of residual wall (1.2 mm on a 2 mm wall, below the
1.5 mm min-wall floor), so the slot was changed to a **through-window** —
the standard snap-fit detail — which removes the thin residual entirely.
This is the kind of DFM fix the verify loop is supposed to force early.

The strength gate is a closed-form screen, not real FEA, because no solver
is installed on the host. The cantilever estimate
`eps = 3 * t_arm * delta / (2 * L_arm^2)` gives 0.0133 (margin 3.0); a real
CalculiX run would refine the stress concentration at the arm root and is
the obvious next step (see next_candidates).

## Diagnostics

Unless noted, numbers reference `metrics.json` (the only metrics file;
this project does not opt into HCE — no `test/`, no `splits.yaml`).

- intended_effect_confirmed: yes — all 8 gates pass in 4 revise cycles
  (`metrics.json:all_gates_pass`, `metrics.json:cycles_to_first_all_pass`);
  the loop caught min-wall, clearance, overhang and strength defects in
  sequence (`log.md:6-32`) and each was fixed by a single parameter edit
  (`run.py:apply_fix`).
- leakage_check: n/a (no learned model / no holdout split) — geometry is
  computed deterministically from `config.yaml`; there is nothing to leak
  and no `test/` exists (`config.yaml` has no split spec).
- overfitting_signal: n/a (deterministic geometry, no train/val learning)
  — gates are fixed physical/DFM thresholds (`config.yaml:gates`), not a
  fitted objective, so there is no train-vs-val gap to report.
- delta_from_prior: n/a (first experiment) — no prior experiment in this
  project to diff against (`experiments/` held only `_proposals/`).
- unexpected_findings: A blind snap pocket silently violated the min-wall
  floor (1.2 mm residual behind the hook on a 2 mm wall); switching to a
  through-window — the canonical snap-fit detail — both fixed min-wall and
  simplified the interference check (`src/enclosure.py:173-191`,
  `metrics.json:final_numbers.min_wall_mm`).
- seeds_run: 1 (single run)
- metric_aggregation: single-run
- next_candidates:
  - Replace the closed-form strength screen with a real CalculiX (or
    gmsh+ccx) prescribed-displacement run on the snap arm, meshing the
    exported STEP, to capture the root stress concentration the beam
    formula misses and validate the 3.0 margin.
  - Stress-test the loop's generality: randomize the starting parameters
    (and target dims) across many seeds and measure cycles-to-pass and
    failure-taxonomy distribution, to show the verify-revise loop is
    robust rather than tuned to one hand-picked defect set.
  - Add a real radial-clearance probe (minimum face-to-face distance via
    OCCT distance query) instead of trusting the `clearance` parameter, so
    the clearance gate measures the as-built gap rather than the nominal.

## Follow-up

- Wire a CalculiX stage into `dvc.yaml` once a solver is installed on the
  host (bridges to the sibling `agentic-solid-mechanics` project).
