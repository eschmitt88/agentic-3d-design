#!/usr/bin/env python
"""Live QA server for agentic-3d-design.

Serves the project working tree over HTTP so the Windows daily-driver
(desktop-2020) can review designs in a browser — including in-progress,
uncommitted iterations the GitHub Pages mirror can't see yet.

  - `/`                      -> landing page listing experiments + QA links
  - `/docs/qa.html?slug=...` -> the interactive QA sheet (three.js viewer)
  - `/experiments/<slug>/results/*.stl|*.step|metrics.json` -> raw files

Binds 0.0.0.0 so it's reachable on the LAN (192.168.50.46) and over the
Tailscale mesh (http://aiserver2026:8101). Private tailnet + LAN only — do
not port-forward to the public internet (not needed; repo is on GitHub Pages
for remote/durable access).

Stdlib only — no venv required:  python3 tools/qa_serve.py [--port 8101]
"""
from __future__ import annotations

import argparse
import html
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP_DIR = ROOT / "experiments"
SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-.+")


def experiments() -> list[dict]:
    out = []
    if not EXP_DIR.is_dir():
        return out
    for d in sorted(EXP_DIR.iterdir(), reverse=True):
        if not d.is_dir() or not SLUG_RE.match(d.name):
            continue
        info = {"slug": d.name, "pass": None, "cycles": None, "strength": None}
        mj = d / "metrics.json"
        if mj.is_file():
            try:
                m = json.loads(mj.read_text())
                info["pass"] = m.get("all_gates_pass")
                proc = m.get("process") or {}
                info["cycles"] = proc.get("n_revise_cycles", m.get("cycles_to_first_all_pass"))
                info["strength"] = m.get("strength_method")
            except (json.JSONDecodeError, OSError):
                pass
        out.append(info)
    return out


def landing() -> bytes:
    cards = []
    for e in experiments():
        if e["pass"] is True:
            badge = '<span style="color:#3fb950">● all gates pass</span>'
        elif e["pass"] is False:
            badge = '<span style="color:#f85149">● gates failing</span>'
        else:
            badge = '<span style="color:#9aa3b2">○ no metrics</span>'
        meta = []
        if e["cycles"] is not None:
            meta.append(f'{e["cycles"]} revise cycles')
        if e["strength"] and e["strength"] != "fea":
            meta.append(f'strength: {html.escape(e["strength"])}')
        slug = html.escape(e["slug"])
        cards.append(
            f'<a class="card" href="/docs/qa.html?slug={slug}">'
            f'<div class="t">{slug}</div>'
            f'<div class="b">{badge}</div>'
            f'<div class="m">{" · ".join(meta)}</div></a>'
        )
    body = "\n".join(cards) or '<p style="color:#9aa3b2">No experiments yet.</p>'
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QA · agentic-3d-design</title><style>
  body {{ margin:0; font:14px/1.5 system-ui,sans-serif; background:#0f1115; color:#e6e9ef; }}
  header {{ padding:16px 22px; border-bottom:1px solid #262b36; }}
  header h1 {{ margin:0; font-size:17px; }}
  header p {{ margin:4px 0 0; color:#9aa3b2; font-size:13px; }}
  .wrap {{ padding:18px 22px; display:grid; gap:12px; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); }}
  a.card {{ display:block; padding:14px 16px; background:#171a21; border:1px solid #262b36; border-radius:9px; text-decoration:none; color:inherit; }}
  a.card:hover {{ border-color:#58a6ff; }}
  .t {{ font-family:ui-monospace,monospace; font-weight:600; }}
  .b {{ margin-top:6px; font-size:13px; }}
  .m {{ margin-top:4px; color:#9aa3b2; font-size:12px; }}
</style></head><body>
<header><h1>agentic-3d-design · QA</h1>
<p>Live working tree on aiserver2026. Click a design to review it. Open STEP files in FreeCAD / OrcaSlicer for measurement.</p></header>
<div class="wrap">{body}</div></body></html>""".encode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            payload = landing()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def end_headers(self):
        # working-tree files change between iterations; never cache.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):  # quieter logs
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8101)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()
    handler = partial(Handler, directory=str(ROOT))
    srv = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"agentic-3d-design QA server → http://aiserver2026:{args.port}/  (root={ROOT})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
