---
kind: concept
name: "Agentic code-CAD"
status: growing
added: "2026-06-16"
sources:
  - "literature/posts/2026-06-16-agentic-cad-landscape.md"
related_concepts:
  - code-cad-vs-generative
  - closed-loop-geometric-verification
related_experiments: []
tags: [cad, agentic, build123d, cadquery]
---

# Agentic code-CAD

## Definition

An LLM agent designs geometry by writing **parametric CAD as code** (Python:
CadQuery / build123d, built on the OCCT kernel), rather than emitting meshes,
B-rep command sequences, or driving a GUI. Code is the design artifact: it is
deterministic, parametric, diffable, and git-trackable.

## Why it matters here

This is the project's chosen substrate. The mid-2026 literature converges on it
because LLMs already excel at Python + spatial reasoning, the output validates
directly, and it integrates cleanly with agent loops and version control
(Text-to-CadQuery 2505.06507; CAD-Coder 2505.19713; CADSmith 2603.26512). It is
the alternative to [[code-cad-vs-generative|generative mesh/text-to-CAD]], which
fails on multi-part assemblies.

## Connections

- Needs [[closed-loop-geometric-verification]] to be effective (single-pass is
  far worse).
- Tooling: `cad-khana` (Claude Code skill), `build123d-mcp` (MCP server).
- Contrast: [[code-cad-vs-generative]].
