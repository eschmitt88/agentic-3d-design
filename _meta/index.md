---
name: index
description: Entry-point index for this project's knowledge graph.
---

# Index

Orientation for the project knowledge graph. Updated by `/wrap`, `/ingest`,
and `/new-experiment`.

## Maps of Content

(promote a cluster of ≥5 related concepts into `mocs/<theme>.md`)

## Concepts

- [[agentic-code-cad]] — agent writes parametric Python CAD (build123d/CadQuery)
- [[code-cad-vs-generative]] — the central tooling adjudication (code-CAD wins)
- [[closed-loop-geometric-verification]] — export → check → revise; the core loop
- [[fea-in-the-loop]] — CalculiX strength gate; bridge to agentic-solid-mechanics
- [[fdm-anisotropy-and-dfm]] — materials/DFM constraints the loop enforces

## Literature

- [[2026-06-16-agentic-cad-landscape]] — mid-2026 sweep, cited (relevance 5)

## Proposals

- `experiments/_proposals/2026-06-16-snap-fit-enclosure.md` — first trial loop

## Active experiments

(none yet — snap-fit-enclosure proposal awaiting `/implement`)

## Open questions

- Commercial-cloud CAD API tractability (Onshape/Fusion) for an LLM loop vs code-CAD.
- Full callable DFM/material toolchain beyond OCCT + CalculiX; generalizing
  infill/anisotropy strength estimates beyond one study.
- Slicer-in-the-loop (PrusaSlicer CLI) integration.
