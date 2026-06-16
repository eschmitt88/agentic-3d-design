# agentic-3d-design

**Can an LLM agent design medium-complexity, multi-part mechanical objects that
are actually manufacturable — by writing parametric code-CAD in a closed
verify-and-revise loop?**

📂 **[Browse this repo →](https://eschmitt88.github.io/agentic-3d-design/)** —
interactive, always-live view of experiments, concepts, literature, and maps of
content. Served via GitHub Pages from `docs/index.html`; reads the live file
tree, no build step.

## What this is

The *generative/design* counterpart to its sibling project
[`agentic-solid-mechanics`](https://github.com/eschmitt88/agentic-solid-mechanics)
(can an agent operate FEM solvers?). Here the agent **produces** geometry; there
it **analyzes** it. The two meet at the FEA-in-the-loop strength check.

The question: drive an LLM agent to design real multi-part parts — enclosures,
brackets, fixtures — that respect **materials, manufacturability (DFM), and
strength/robustness/reliability**, then validate them digitally (and eventually
on a 3D print). Success = the agent reaches a manufacturable, requirement-passing
design with minimal human correction, and we can characterize where and why it
fails.

The mid-2026 literature sweep (`literature/posts/2026-06-16-agentic-cad-landscape.md`)
adjudicated the central tooling question: **agent-driven code-CAD beats
generative text-to-3D/mesh for engineering parts.** The stack is therefore:

- **CAD engine:** [`build123d`](https://github.com/gumyr/build123d) (Python,
  OCCT kernel) — parametric, deterministic, diffable, git-friendly.
- **Agent loop:** diagnostics-first feedback via
  [`cad-khana`](https://github.com/cyberchitta/cad-khana) (a Claude Code skill)
  and/or [`build123d-mcp`](https://github.com/pzfreo/build123d-mcp) — the loop
  is what makes it work (single-pass generation is far worse).
- **Verification ladder:** OCCT validity/measure → printability
  (overhang/thin-wall/clearance) → rendered-PNG review → **CalculiX FEA** for
  load-bearing parts.
- **Generative models:** kept on the bench as an optional ideation front-end,
  not the production path.

No printer yet — designs are validated **digitally first** (all free/local), and
only ordered from an outsourced print service once they pass.

## Status

Bootstrapped 2026-06-16 from a deep-research sweep. First trial proposed:
a **parametric two-part snap-fit enclosure** (`experiments/_proposals/`) — a
small design that exercises clearance/tolerance, min-wall DFM, and a
cantilever-snap strength check.

## How it's organized

Plain Markdown + flat YAML frontmatter, cross-linked with `[[wikilinks]]`:

- `concepts/` / `mocs/` — atomic ideas; promoted to a map of content when ≥5 cluster.
- `literature/` — processed notes on papers, repos, posts (0–5 relevance scored).
- `experiments/YYYY-MM-DD-<slug>/` — self-contained runs (hypothesis → result, config, metrics, log).
- `raw/` — immutable source captures · `docs/decisions/` — ADRs · `_meta/` — index, log, templates.

## Local use

```sh
make env    # uv sync
make lint   # knowledge-graph / experiment health check
```

Part of a personal research framework
([claude-system](https://github.com/eschmitt88/claude-system)). See `CLAUDE.md`
for the agent-facing orientation and `~/.claude/CLAUDE.md` for the framework's
durable principles.
