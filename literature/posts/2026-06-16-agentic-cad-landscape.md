---
kind: post
title: "Agentic 3D/CAD design landscape (mid-2026): code-CAD vs generative"
author: "deep-research sweep (synthesized)"
url: null
source: "raw/research/2026-06-16-deep-research-agentic-cad.json"
added: "2026-06-16"
relevance: 5
related_experiments: []
related_concepts:
  - agentic-code-cad
  - code-cad-vs-generative
  - closed-loop-geometric-verification
  - fea-in-the-loop
  - fdm-anisotropy-and-dfm
tags: [landscape, cad, agentic, dfm, fea, synthesis]
---

# Agentic 3D/CAD design landscape (mid-2026)

Synthesis of an adversarially-verified deep-research sweep (24 sources →
109 claims → 25 verified, 24 confirmed / 1 killed). Raw capture:
`raw/research/2026-06-16-deep-research-agentic-cad.json`. Confidence tags below
mirror the sweep's 3-vote verification; items marked **(unverified)** were
fetched but not among the verified set — treat as reasoned, not evidence-backed.

## TL;DR

For medium-complexity, **multi-part mechanical** parts, the field favors an
**LLM agent writing parametric code-CAD (CadQuery / build123d Python) in a
closed verify-and-revise loop** over generative text-to-3D/mesh models. The loop
— export geometry, run programmatic checks, feed failures back — is what makes it
work; single-pass generation is dramatically worse. But strict manufacturable
multi-part design is **not solved**: even frontier models almost never pass
strict engineering requirements, so the realistic target is a **human-curated
agentic assistant**, not autonomous part production.

## Key points (verified, high-confidence)

- **Code-CAD is the convergent substrate.** Multiple independent 2025–26 papers
  pick CadQuery/build123d Python because LLMs already excel at Python +
  spatial reasoning, the output is parametric and directly validatable, and it
  integrates with existing LLMs — vs. command-sequences (need training from
  scratch) or meshes. (Text-to-CadQuery, arXiv 2505.06507; CAD-Coder, 2505.19713;
  CADSmith, 2603.26512.) *Note: the sweep refuted a stronger claim that
  fine-tuning on Text-to-CadQuery data is "highly effective" (0-3) — keep the
  architectural rationale, not the fine-tuning efficacy claim.*

- **The closed loop substantially beats single-pass.** CADSmith's closed-loop
  refinement raises CadQuery execution to 100% and cuts mean Chamfer Distance
  28.37 → 0.74 (median F1 0.971 → 0.985, IoU 0.809 → 0.963) with a vision
  "judge" (2603.26512). FEA-feedback raises requirement-pass 38.8% → 60.5%
  (2605.17448v2).

- **Agents can self-verify geometry concretely.** OCCT/OpenCASCADE kernel
  queries (validity/watertightness, volume, bbox, center of mass, face/edge/
  vertex counts), interference/clearance/wall-thickness/overhang diagnostics,
  rendered PNG engineering drawings for visual feedback, STEP/STL export — with
  assertion violations forced into hard build failures. Purpose-built tooling
  exists: **`cad-khana`** (CLI + Claude Code skill, "diagnostics-first",
  `diagnostics.json` + `khana draw` PNGs; `.assert_no_interference`,
  `.assert_clearance(min_mm=0.2)`, `.assert_min_wall(min_mm=1.5)`) and
  **`build123d-mcp`** (MCP server: `measure`, `analyze_printability`,
  `render_view`, import/export). Design thesis: existing code-CAD "assumes a
  human at a render window"; "the AI writes blind" and needs explicit
  non-visual feedback. *(cad-khana self-describes as early / API may churn.)*

- **Strength enters the loop via open-source FEA.** Agent writes CadQuery →
  exports STEP (AP242) → Hephaestus-CCX meshes and runs **CalculiX** (free,
  Abaqus-deck-compatible), returning typed failures over von Mises stress,
  displacement, modal, buckling (first-mode factor ≥1.5), contact, clearance
  (2605.17448v2). This is the bridge to the sibling `agentic-solid-mechanics`
  project.

- **Compiler/grammar verification is an emerging cheaper alternative** to
  rendering + VLM review: CAD-Judge's Compiler-as-a-Judge (Chamfer-distance
  reward, no rendering) and Compiler-as-a-Review (2508.04002) — avoids slow
  rendering and VLM reward-hacking.

- **Generative text-to-3D/CAD is single-part-biased.** It degrades sharply on
  complex topology and multi-part assemblies (spatial misalignment →
  "dislocations"). Text2CAD-Bench: L3 invalidity ~68–70%, IoU ~0.23–0.25; L4
  real-world 61–81% invalid (2605.18430). CAD-Coder itself notes multi-component
  assemblies suffer visible dislocations (2505.19713). MUSE was built precisely
  because prior text-to-CAD targets single parts (2605.28579). This is a
  current-gen limitation actively being mitigated, not a permanent ceiling.

- **Reality check — not solved.** On multi-part/engineering benchmarks even
  frontier models show a "failure cascade" (executable code → valid geometry →
  engineering-ready) and almost never pass strict requirements. MUSE: GPT-5.5
  ~54.7% functionality / ~53.8% manufacturability. Hephaestus-CCX: 400 first
  attempts produce *zero* strict-passing artifacts; one FEA round adds one strict
  pass across 400 revisions; first-attempt mean requirement pass ~20–33%
  single-part, ~6.6–15% multi-part (2605.28579; 2605.17448v2).

- **FDM strength is quantifiable for the loop.** Infill % gives the largest UTS
  gain (PLA +37.3%, PETG +24.4%) but *lowers* specific (mass-normalized)
  strength (−30.4% PLA, −37.7% PETG) — so strength-optimal ≠
  strength-to-weight-optimal (PMC9230522, peer-reviewed). FDM is strongly
  anisotropic (weak across layer lines) — a first-class DFM constraint:
  orient parts so load runs along, not across, layers.

## Recommended stack (synthesis)

| Layer | Choice | Why |
|---|---|---|
| CAD engine | **build123d** (or CadQuery) | parametric, deterministic, diffable, OCCT kernel, git-friendly |
| Agent loop | **cad-khana** (Claude Code skill) + **build123d-mcp** | diagnostics-first feedback is the verified differentiator |
| Geometry checks | OCCT validity/measure, printability | watertight, clearance, min-wall, overhang |
| Visual feedback | rendered PNG engineering drawings | the agent's "eyes" |
| Strength | **CalculiX** FEA (+ FreeCAD FEM) | von Mises, displacement, buckling — ties to agentic-solid-mechanics |
| Generative | on the bench (Hunyuan3D/TRELLIS/Text2CAD) | optional ideation front-end only |

## Practical notes (unverified — fetched but not 3-vote-verified)

- **Hobbyist CAD:** build123d / CadQuery / OpenSCAD / FreeCAD all free & open;
  FreeCAD bundles CalculiX FEM. Onshape (free hobby tier, has API) and Fusion 360
  (personal) add cloud/licensing friction without helping the agent loop. For the
  agentic path, **code-CAD wins** — full local control, no API latency.
- **No printer → outsource:** validate digitally first (free), then order from
  **JLC3DP / PCBWay** (cheap FDM/MJF) or a **Craftcloud** aggregator. If buying
  later, the consensus entry for functional multi-part prototypes is the
  **Bambu Lab A1 / P1S** class.

## Open questions (not yet researched here)

- Commercial-cloud CAD API tractability (Onshape FeatureScript/API, Fusion 360
  Python API) for an LLM loop vs. code-CAD — no verified evidence gathered.
- Full callable DFM/material-selection toolchain beyond OCCT + CalculiX; how well
  infill/wall/anisotropy strength estimates generalize beyond the single PMC study.
- Best slicer-in-the-loop integration (PrusaSlicer CLI was fetched as a DFM
  signal source).

## Follow-up

- Fetch + ingest the load-bearing primary sources as individual notes:
  CADSmith (2603.26512), CAD-Coder (2505.19713), Text-to-CadQuery (2505.06507),
  Self-Improving-FEA / Hephaestus-CCX (2605.17448v2), MUSE (2605.28579),
  Text2CAD-Bench (2605.18430), CAD-Judge (2508.04002); repos cad-khana,
  build123d-mcp.
- Stand up the build123d + cad-khana loop and run the first trial
  (`[[2026-06-16-snap-fit-enclosure]]`).
