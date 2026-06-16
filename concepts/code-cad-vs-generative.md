---
kind: concept
name: "Code-CAD vs generative 3D"
status: growing
added: "2026-06-16"
sources:
  - "literature/posts/2026-06-16-agentic-cad-landscape.md"
related_concepts:
  - agentic-code-cad
  - closed-loop-geometric-verification
related_experiments: []
tags: [cad, generative, text-to-cad, mesh, adjudication]
---

# Code-CAD vs generative 3D

## Definition

The central tooling adjudication: **agent-written code-CAD** (parametric Python)
vs. **generative models** (text-to-CAD, text/image-to-mesh: Text2CAD,
Hunyuan3D, TRELLIS, B-rep/SDF generators) for producing engineering parts.

## Why it matters here

For medium-complexity **multi-part mechanical** designs, the mid-2026 evidence
favors code-CAD. Generative models are single-part-biased and degrade sharply on
complex topology and assemblies — spatial misalignment produces visible
"dislocations" (Text2CAD-Bench 2605.18430: L3 invalidity ~68–70%; CAD-Coder
2505.19713 Appendix F; MUSE 2605.28579, built because prior work targets single
parts). Generative stays an **optional ideation front-end** (rough mesh →
reverse to parametric), not the production path. Caveat: this is a current-gen
limitation being actively mitigated, not a permanent ceiling.

## Connections

- Production path: [[agentic-code-cad]].
- Both still fail strict multi-part engineering requirements — see the "failure
  cascade" in [[closed-loop-geometric-verification]].
