# Project: agentic-3d-design

Short orientation only. User-level `~/.claude/CLAUDE.md` holds the durable
principles; this file refines them for this project.

## What this project is about

Can an LLM agent design medium-complexity, multi-part **mechanical** objects
that are actually manufacturable — by writing parametric **code-CAD**
(build123d / CadQuery, Python/OCCT) in a **closed verify-and-revise loop**?
The loop exports geometry and self-checks: OCCT validity → DFM diagnostics
(clearance, min-wall, overhang, interference) → rendered-PNG review →
**CalculiX FEA** strength gate. Generative text-to-3D/mesh is on the bench
(ideation only) — the verified mid-2026 evidence favors agent code-CAD for
engineering parts. Strength/manufacturability are first-class. The FEA gate
bridges to the sibling project `agentic-solid-mechanics`. `agency: max`.
Orientation: `README.md`; landscape evidence:
`literature/posts/2026-06-16-agentic-cad-landscape.md`.

## Layout (see user CLAUDE.md for the full rationale)

- `raw/` — immutable source material. Read only.
- `literature/` — processed notes on papers, repos, posts.
- `concepts/` — atomic ideas. Promote to `mocs/` when ≥5 cluster.
- `experiments/YYYY-MM-DD-<slug>/` — self-contained runs.
- `docs/decisions/` — lightweight ADRs.
- `journal/` — daily session files (hook-written).
- `_meta/` — index, log, templates.

## Scoped rules

Detailed conventions live in `.claude/rules/` and are auto-loaded when you
touch matching paths:

@.claude/rules/experiments.md
@.claude/rules/notebooks.md
@.claude/rules/data.md

## Budget & compute

Autonomous runs read `budget.yaml` at this project's root for hard
ceilings (wall time, tokens, disk) and model roles (ideator vs
implementer). Before proposing anything with non-trivial resource
demands — multi-hour training, large downloads, many seeds — read
`budget.yaml` and make sure the ask fits under the remaining headroom.
If it doesn't fit, say so in the proposal's `risks:` and either scope
down or explicitly flag the need to raise a ceiling.

@budget.yaml

## Project-specific facts

- Primary language: (fill in)
- Environment: managed by `uv`; run `make env` to sync.
- Data: tracked by DVC. Large artifacts on SN850X via `~/projects/`.

## Housekeeping

- End sessions with `/wrap`. The SessionEnd hook backstops this.
- Use `/new-experiment <slug>` — don't hand-roll experiment folders.
- Run `/lint` weekly.
