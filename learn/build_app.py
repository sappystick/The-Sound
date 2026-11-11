#!/usr/bin/env python3
"""Assemble learn/index.html: the Akouo engine (template.html) with the built-in course pack (John's Greek)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); L = json.load(open(os.path.join(H, "ladder.json"), encoding="utf-8")); A = json.load(open(os.path.join(H, "ladder_audio.json"), encoding="utf-8"))
steps = []
for s in L["steps"]:
    s = dict(s); s["a"] = A[str(s["n"])]; steps.append(s)
c = L["curve"]
pack = dict(id="john-koine", name="The Gospel of John in first-century Greek", lang="grc", langName="the Greek of John's Gospel", dir="ltr", audio="files", audioBase="audio/step_", refLabel="John ",
            steps=steps, curve=c, distractors=L["distractors"],
            measured=[["Reading John in its own order", f"{L['canon_new']:.2f} new words per clause over the first {len(steps)} clauses"],
                      ["After 600 steps (beyond this course)", f"{round(c[-1]['tokens'] * 100)}% of all words in John"],
                      ["Same algorithm on Hebrew Genesis, 150 steps", "151 words → 70% of all words; 149 of 150 steps add exactly one new word"]])
open(os.path.join(H, "index.html"), "w", encoding="utf-8").write(open(os.path.join(H, "template.html"), encoding="utf-8").read().replace("__DATA__", json.dumps(pack, ensure_ascii=False, separators=(",", ":"))))
json.dump({k: pack[k] for k in pack if k != "steps"} | {"steps": [dict(s, a=None) for s in steps[:3]]}, open(os.path.join(H, "pack_format_example.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("built", round(os.path.getsize(os.path.join(H, "index.html")) / 1e3), "KB;", len(steps), "steps; total audio", round(sum(s["a"]["dur"] for s in steps) / 60, 1), "min")
