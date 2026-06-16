---
kind: proposal
slug: 2026-06-16-snap-fit-enclosure
date: "2026-06-16"
status: proposed
hypothesis: >
  A build123d-writing LLM agent, given a closed verification loop (OCCT
  validity + DFM diagnostics + rendered-PNG review, and a CalculiX strength
  check on the snap arm), can autonomously produce a parametric two-part
  snap-fit enclosure that mates at a target clearance, satisfies FDM DFM
  constraints (min wall, support-free overhangs, no interference), and whose
  snap-fit cantilever flexes to engage without exceeding material yield —
  reaching a passing design in a small number of revise cycles with minimal
  human correction.
rationale: >
  Smallest design that is genuinely multi-part yet prints as two simple
  support-free parts, and that exercises every rung of the recommended stack:
  clearance/tolerance (what FDM fits get wrong), min-wall and overhang DFM, and
  a built-in strength/robustness probe (the cantilever snap must deflect to
  engage without breaking — a clean, small FEA problem). Establishes the
  end-to-end loop (agent → build123d → STEP/STL → checks → FEA → revise) on an
  easy target before scaling part count/complexity.
reads:
  - "literature/posts/2026-06-16-agentic-cad-landscape.md"
expected_metric: >
  Primary: design passes all gates — solid valid/watertight (both parts),
  lid-to-box diametral/edge clearance within 0.15–0.25 mm, min wall ≥ 1.5 mm,
  all overhangs ≤ 45° (support-free), zero box↔lid interference in the assembled
  state, snap engages (interference feature present and reachable by the
  flexing arm). Strength gate: CalculiX peak strain in the snap arm at full
  insertion deflection < material yield strain (PETG), with a margin ≥ 1.5.
  Process metric: number of agent revise cycles to first all-pass (target ≤ 5),
  and count/category of failures caught by the loop vs. left to the human.
design_sketch: >
  Parametric box (L×W×H, wall t, floor t) + lid with a perimeter lip and N
  cantilever snap arms engaging mating undercuts/slots on the box rim. Exposed
  parameters: outer dims, wall t, clearance, lip depth, snap-arm length /
  thickness / hook depth / lead-in angle, fillet radii. build123d source under
  experiments/<date>-snap-fit-enclosure/src/enclosure.py; cad-khana (or
  build123d-mcp) drives build → diagnostics.json → khana draw PNGs → agent
  reads failures → edits parameters/geometry → rebuild. Strength: export snap
  arm (or full lid) to STEP, apply prescribed insertion displacement at the hook
  tip, run CalculiX, read max principal/von Mises strain. All-digital validation
  first; STL archived for a later outsourced PETG print (JLC3DP/PCBWay) as a
  physical confirmation.
risks:
  - "Snap-fit geometry is tolerance-sensitive; agent may oscillate on clearance — cap revise cycles and log the trajectory."
  - "CalculiX setup (mesh + prescribed-displacement BC on a thin cantilever) may be finicky; fall back to closed-form cantilever-beam strain estimate if FEA stalls, and lean on agentic-solid-mechanics tooling."
  - "cad-khana is early / API may churn — pin a commit; have a raw-build123d fallback path that calls OCCT checks directly."
  - "Anisotropy: real FDM snap strength across layer lines differs from isotropic FEA; treat the FEA gate as a screen, flag print-orientation in the result."
related_prior: []
estimated_runtime: "Setup + loop: a few hours of agent wall-time; no GPU training. FEA runs are seconds-to-minutes each."
---

# Trial: parametric two-part snap-fit enclosure

## Argument

This is the project's **first end-to-end loop test** on a deliberately small but
honest target. Per the landscape note
([[2026-06-16-agentic-cad-landscape]]), the verified recommendation is
[[agentic-code-cad]] (build123d) inside a
[[closed-loop-geometric-verification]] loop, with strength brought in via
[[fea-in-the-loop]]. A snap-fit enclosure is the minimal design that forces all
of those at once while staying printable as two support-free parts.

**Why not something simpler (a single bracket)?** A single part wouldn't test
assembly clearance/interference — the thing FDM and agents most reliably get
wrong, and the reason multi-part is the hard regime
([[code-cad-vs-generative]]). **Why not harder (hinged box, 4+ parts)?**
Print-in-place hinges are tolerance-nightmares; better to prove the loop first.

**What we learn regardless of outcome:** where the agent loop catches failures
on its own vs. where a human must intervene, how many revise cycles convergence
takes, and whether the [[fdm-anisotropy-and-dfm]] / FEA gate is practical to wire
up. That failure-characterization is the real deliverable — strict
manufacturable multi-part design is not solved (Hephaestus-CCX: ~0 strict passes
in 400 first attempts), so the value is mapping *where and why* the loop helps.

## Success criteria (HCE-light)

No held-out test set here (this is a tooling/loop trial, not a learned model), so
HCE's `test/` rule is not triggered. Metrics live in `metrics.json`: the boolean
gate-pass set above plus the process metrics (revise-cycle count, failure
taxonomy). A physical PETG print is an optional later confirmation, not part of
the pass criterion.

## Next steps if it passes

- Scale part count (add a gasket channel, cable gland, board standoffs → 3–4
  interacting features).
- Swap the snap for a threaded interface; compare loop difficulty.
- Promote the FEA gate into a reusable check shared with `agentic-solid-mechanics`.
