#!/usr/bin/env python3
"""Build a course pack for ANY language from a corpus file.

Corpus JSON: {"id": "...", "name": "...", "lang": "es", "langName": "Spanish", "dir": "ltr",
              "units": [{"ref": "1", "meaning": "literal meaning of the clause",
                         "tokens": [{"w": "written form", "lemma": "dictionary form", "gloss": "meaning",
                                     "role": "subject|verb|object|of|to|address|link", "hint": "note on the form"}]}]}
Only "w" is required per token; lemma defaults to the lower-cased form, role to "link".
Output: a pack JSON the Akouo app loads (audio by the page's voice unless recordings are supplied).
Usage: python3 build_course.py corpus.json pack.json [steps]"""
import json, sys
from ladder_core import ladder, curve
c = json.load(open(sys.argv[1], encoding="utf-8")); steps = int(sys.argv[3]) if len(sys.argv) > 3 else 400
for u in c["units"]:
    for t in u["tokens"]: t.setdefault("lemma", t["w"].lower().strip(".,;:!?¡¿\"'()")); t.setdefault("gloss", "?"); t.setdefault("role", "link"); t.setdefault("hint", "")
U = [[t["lemma"] for t in u["tokens"]] for u in c["units"]]; order = ladder(U, steps); cv = curve(U, order)
pack = dict(id=c.get("id", "course"), name=c["name"], lang=c.get("lang", ""), langName=c.get("langName", c["name"]), dir=c.get("dir", "ltr"), audio="tts",
            steps=[dict(n=n, ref=c["units"][i].get("ref", ""), new=new, mean=c["units"][i].get("meaning", " ".join(t["gloss"] for t in c["units"][i]["tokens"])),
                        toks=[dict(w=t["w"], lem=t["lemma"], g=t["gloss"], role=t["role"], hint=t["hint"], new=t["lemma"] in new) for t in c["units"][i]["tokens"]]) for n, (i, new, k) in enumerate(order, 1)],
            curve=cv, distractors=sorted({t["gloss"] for u in c["units"] for t in u["tokens"] if t["gloss"] != "?"})[:400], totals=dict(units=len(U), words=sum(map(len, U)), lemmas=len({x for u in U for x in u})))
json.dump(pack, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False); print(len(pack["steps"]), "steps;", cv[-1] if cv else "")
