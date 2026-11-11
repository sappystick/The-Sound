#!/usr/bin/env python3
"""Assemble learn/index.html from ladder.json, ladder_audio.json and template.html."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); L = json.load(open(os.path.join(H, "ladder.json"), encoding="utf-8")); A = json.load(open(os.path.join(H, "ladder_audio.json"), encoding="utf-8"))
D = dict(steps=L["steps"], audio=A, curve=L["curve"], distractors=L["distractors"], canon_new=L["canon_new"], one_new=sum(len(set(s["new"])) == 1 for s in L["steps"]),
         hebrew="151 words → 70% of all words in Genesis; 149 of 150 steps add exactly one new word")
open(os.path.join(H, "index.html"), "w", encoding="utf-8").write(open(os.path.join(H, "template.html"), encoding="utf-8").read().replace("__DATA__", json.dumps(D, ensure_ascii=False, separators=(",", ":"))))
print("built", round(os.path.getsize(os.path.join(H, "index.html")) / 1e3), "KB")
