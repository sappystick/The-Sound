#!/usr/bin/env python3
"""Build the Resonance web app: template.html + the engine's data (datapoints, presets, verification report) -> index.html.
The samples/*.mp3 files are published beside it."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(HERE)
dp = json.load(open(os.path.join(R, "datapoints.json"), encoding="utf-8"))
dp["rooms"] = {k: {x: v[x] for x in ("name", "dims_m", "modes_voice", "evidence", "note", "reported_hz") if x in v} for k, v in dp["rooms"].items()}
pre = json.load(open(os.path.join(R, "presets.json"), encoding="utf-8"))["presets"]
rep = json.load(open(os.path.join(R, "verify_report.json"), encoding="utf-8"))
rep = [dict(name=r["name"], passed=r["passed"], checks=[dict(c=x["check"], want=str(x["expected"]), got=str(x["measured"]), ok=x["passed"]) for x in r["checks"]]) for r in rep]
DATA = json.dumps(dict(dp=dp, presets=pre, report=rep), ensure_ascii=False).replace("</", "<\\/")
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("/*__DATA__*/null", DATA)
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html); print("index.html", len(html) // 1024, "KB")
