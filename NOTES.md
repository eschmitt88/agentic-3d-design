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
