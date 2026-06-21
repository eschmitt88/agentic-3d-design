# NOTES

Running log of work sessions. `/wrap` appends a new dated section at the
end of each session with **Did / Findings / Next** subsections. The
SessionEnd hook backstops this if you forget.

<!-- entries go below this line, newest at bottom -->

## 2026-06-16

### Did
- Bootstrapped the project from a deep-research sweep (24 sources → 25
  adversarially-verified claims) on agentic 3D/CAD design.
- Wrote README (project framing), cited landscape note
  (`literature/posts/2026-06-16-agentic-cad-landscape.md`), 5 seed concepts,
  and the first trial proposal (`2026-06-16-snap-fit-enclosure`).
- Set `agency: max`; created public GitHub remote + Pages.

### Findings
- **Agent-driven code-CAD (build123d/CadQuery) beats generative text-to-3D/mesh**
  for multi-part mechanical parts; the **closed verify-revise loop** is the key
  (CADSmith Chamfer 28.37→0.74). Tooling exists: `cad-khana` (Claude Code skill),
  `build123d-mcp`. Strength enters via **CalculiX FEA** (bridges to
  `agentic-solid-mechanics`).
- Not solved: even frontier models rarely pass strict multi-part requirements →
  target a human-curated assistant, characterize where/why it fails.

### Next
- `/implement` the snap-fit-enclosure proposal: stand up build123d + cad-khana
  loop, wire OCCT + DFM checks and a CalculiX snap-arm strain gate.
- Optionally auto-advance: `/fetch-paper` + `/ingest` the load-bearing arXiv
  sources (2603.26512, 2505.19713, 2605.17448v2, 2605.28579, …) — check
  coordinator headroom first (agency: max).

## 2026-06-21

### Did
- Implemented the snap-fit-enclosure trial via `/implement` (opus subagent):
  build123d two-part enclosure, closed verify-revise loop, **all 8 gates pass
  in 4 cycles**. Strength = closed-form cantilever (CalculiX absent — FEA stays
  in agentic-solid-mechanics by decision).
- Built the **human QA pipeline** (ADR `docs/decisions/0001-human-qa-strategy.md`):
  - `docs/qa.html` — three.js STL viewer + gate metrics + dimensions + STEP/STL
    downloads; context-aware (GitHub Pages → raw.githubusercontent; aiserver →
    live working tree). No-slug shows an experiment chooser.
  - `tools/qa_serve.py` + systemd `--user` unit `agentic-3d-qa.service` on
    **port 8091** — live viewer at `http://aiserver2026:8091/` (LAN + Tailscale).
  - `tools/step_to_stl.py` — mesh STEP→STL for the web viewer.
  - `docs/index.html` nav gains a "3D / QA viewer" link.

### Findings
- Desktop `desktop-2020` (Windows) is LAN + Tailscale-direct to `aiserver2026`,
  so live serving + GitHub Pages mirror both work; bandwidth is a non-issue.
- Web QA = visual (STL, no WASM); precise measurement pushed to desktop CAD.

### Next
- On `desktop-2020`: install OrcaSlicer + FreeCAD (winget commands provided) and
  smoke-test the live viewer + a STEP download.
- Fold `step_to_stl.py` into the experiment harness so new designs auto-mesh.
- Consider generalizing `qa.html`'s metrics schema as experiments diverge.
