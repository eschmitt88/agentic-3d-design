---
kind: concept
name: "FDM anisotropy and DFM"
status: seedling
added: "2026-06-16"
sources:
  - "literature/posts/2026-06-16-agentic-cad-landscape.md"
related_concepts:
  - fea-in-the-loop
  - closed-loop-geometric-verification
related_experiments: []
tags: [fdm, materials, dfm, anisotropy, strength]
---

# FDM anisotropy and DFM

## Definition

The material/manufacturability constraints an agent must respect for
fused-deposition (FDM) printing: parts are **strongly anisotropic** (weak across
layer lines, strong along them), and design parameters trade off — notably
infill % gives the largest ultimate-tensile-strength gain (PLA +37.3%, PETG
+24.4%) but *lowers* mass-normalized "specific" strength (−30.4% PLA, −37.7%
PETG), so strength-optimal ≠ strength-to-weight-optimal (PMC9230522,
peer-reviewed). Other DFM levers: wall/perimeter count, min wall thickness,
overhang angle (support-free ≤ ~45°), clearance/tolerance for mating parts
(~0.2 mm typical for FDM fits).

## Why it matters here

These are the rules the agent's [[closed-loop-geometric-verification]] and
[[fea-in-the-loop]] checks enforce. Material choice (PLA stiff/brittle, PETG
tougher, ABS/ASA heat- and impact-resistant, nylon/CF for load) sets the
strength limits the FEA gate compares against. Orientation matters: route load
*along* layers, not across.

## Connections

- Enforced by [[closed-loop-geometric-verification]]; quantified by
  [[fea-in-the-loop]].
- First probe of these tradeoffs: the snap-fit cantilever in
  [[2026-06-16-snap-fit-enclosure]].
