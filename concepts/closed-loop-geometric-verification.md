---
kind: concept
name: "Closed-loop geometric verification"
status: growing
added: "2026-06-16"
sources:
  - "literature/posts/2026-06-16-agentic-cad-landscape.md"
related_concepts:
  - agentic-code-cad
  - fea-in-the-loop
related_experiments: []
tags: [cad, verification, occt, feedback-loop, dfm]
---

# Closed-loop geometric verification

## Definition

The agent does not write CAD blind: it **exports geometry, runs programmatic
checks, and feeds failures back** into a revise step. Checks include OCCT kernel
queries (solid validity / watertightness, volume, bbox, center of mass,
face/edge/vertex counts), DFM diagnostics (interference, clearance, wall
thickness, overhang), rendered PNG engineering drawings for visual feedback, and
STEP/STL export. Assertion violations become **hard build failures**.

## Why it matters here

The loop is the whole game. CADSmith: closed-loop refinement raises CadQuery
execution to 100% and cuts mean Chamfer Distance 28.37 → 0.74 (2603.26512).
Tooling: `cad-khana` (`diagnostics.json`, `khana draw` PNGs, `.assert_clearance`
/ `.assert_min_wall` / `.assert_no_interference`); `build123d-mcp` (`measure`,
`analyze_printability`, `render_view`). Design thesis: existing tools assume a
human at a render window; the agent needs explicit non-visual feedback.

**Reality check:** even with the loop, frontier models show a "failure cascade"
(executable → valid geometry → engineering-ready) and rarely pass *strict*
requirements — so this is a human-curated assistant, not autonomous production
(MUSE 2605.28579; Hephaestus-CCX 2605.17448v2). A cheaper verification primitive
is compiler/grammar review (CAD-Judge 2508.04002).

## Connections

- Enables [[agentic-code-cad]]; strength variant is [[fea-in-the-loop]].
- Manufacturability constraints come from [[fdm-anisotropy-and-dfm]].
