---
kind: concept
name: "FEA in the loop"
status: seedling
added: "2026-06-16"
sources:
  - "literature/posts/2026-06-16-agentic-cad-landscape.md"
related_concepts:
  - closed-loop-geometric-verification
  - fdm-anisotropy-and-dfm
related_experiments: []
tags: [fea, calculix, strength, simulation, cross-project]
---

# FEA in the loop

## Definition

Bring **structural strength/robustness** into the agentic design loop by running
finite-element analysis on the agent's exported geometry: CadQuery/build123d →
STEP (AP242) → mesh → **CalculiX** (free, open-source, Abaqus-deck-compatible) →
typed failures over von Mises stress, displacement, modal frequencies, buckling
(first-mode factor ≥ 1.5), contact, clearance.

## Why it matters here

This is how "strength/robustness/reliability" becomes a checkable signal rather
than a hope. Demonstrated by Self-Improving CAD Generation Agents with FEA as
feedback / Hephaestus-CCX (2605.17448v2): iterative FEA feedback raises mean
requirement pass 38.8% → 60.5%. **Direct bridge to the sibling project**
[`agentic-solid-mechanics`](https://github.com/eschmitt88/agentic-solid-mechanics),
which studies the agent-as-FEM-operator loop in depth — this project can reuse
that machinery for the strength gate.

## Connections

- Specialized form of [[closed-loop-geometric-verification]].
- Constrained by material anisotropy — see [[fdm-anisotropy-and-dfm]].
- Cross-project: agentic-solid-mechanics (FEM operator + inverse design).
