# 0001 — Human QA strategy for 3D designs

- Status: accepted
- Date: 2026-06-21
- Deciders: eschmitt + agent

## Context

Designs are produced on the headless aiserver (`aiserver2026`, Linux). The
human reviewer works on a Windows daily driver (`desktop-2020`) that is on the
same LAN (192.168.50.0/24) **and** the Tailscale mesh (direct connection). We
need the reviewer to open and validate multi-part 3D files (STEP/STL) easily,
with as little manual effort as possible. FEA-based strength validation is
explicitly **out of scope here** — it lives in the sibling `agentic-solid-mechanics`
project. QA here is geometric/visual/printability review by a human.

## Decision

A three-layer QA pipeline, agent-does-the-work first:

1. **Agent-generated QA sheet (default, lowest effort).** Per design, an
   interactive page (`docs/qa.html?slug=<experiment>`) shows: a three.js STL
   viewer (rotate/zoom/pan, switch box/lid/assembled/exploded), the gate
   pass/fail table, key dimensions, loop stats, the strength-method caveat, the
   reference render, and STEP/STL download links.

2. **Browser viewer, zero install.** `docs/qa.html` is context-aware:
   - On GitHub Pages it loads models from `raw.githubusercontent.com` (works
     anywhere with internet; committed designs only).
   - Served by the aiserver it loads from the live working tree (shows
     in-progress, uncommitted iterations).
   Interactive web view uses **STL** (no WASM dependency); STEP is offered as a
   download for desktop CAD.

3. **Two free desktop tools on `desktop-2020`, for deep QA.**
   - **OrcaSlicer** — printability view (orientation, overhangs, supports,
     time/material), matches the print-outsourcing goal.
   - **FreeCAD** — precise measurement (clearances, walls), section/exploded.

### Hosting — both paths

- **Live:** `tools/qa_serve.py` (stdlib HTTP, port **8091**) run by a systemd
  `--user` unit `agentic-3d-qa.service`. Reachable at `http://aiserver2026:8091/`
  (Tailscale MagicDNS — fast on-LAN, still works remote) and `http://192.168.50.46:8091/`.
  Bound to the LAN/tailnet only; **not** port-forwarded to the public internet.
- **Durable/remote:** the same `docs/qa.html` on GitHub Pages
  (`https://eschmitt88.github.io/agentic-3d-design/qa.html`), reading committed
  files. Survives the aiserver being off; works from anywhere.

## Why STL for web, STEP for desktop

STL meshes render in-browser with no WASM/OCCT importer (simpler, reliable).
STEP carries exact B-rep + assembly transforms — what FreeCAD/OrcaSlicer want
for measuring and slicing. `tools/step_to_stl.py` meshes STEP→STL for the
viewer; the agent runs it after each design.

## three.js is vendored, not CDN-loaded

The aiserver could not reliably reach `cdn.jsdelivr.net` (likely the AdGuard/edge
DNS in the home-netsec setup), so the viewer's three.js (core + STLLoader +
OrbitControls) is **vendored under `docs/vendor/three/`** and loaded via an
import map (`"three"` → the local build). No CDN dependency — works on-LAN,
offline, and on Pages. A `window.error` handler surfaces any missing-lib failure
instead of rendering a blank screen.

## Network rationale

Desktop is LAN + Tailscale-direct, so bandwidth is a non-issue and a stable
MagicDNS hostname (`aiserver2026`) works on-LAN and remote transparently. The
GitHub Pages mirror covers the desktop-is-offline-from-aiserver case (needs
only internet).

## Consequences

- New designs need `step_to_stl.py` run on their `results/*.step` so the viewer
  has meshes (fold into the experiment harness going forward).
- `qa.html` currently assumes the snap-fit experiment's metrics schema
  (`gate_results`, `final_numbers`, `process`); generalize as schemas diverge.
- Web view is visual only — precise measurement is deliberately pushed to the
  desktop tools, not reimplemented in-browser.
