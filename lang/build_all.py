#!/usr/bin/env python3
"""Build everything spoken for Sala: sample recordings for the language page, and the Akouo course (ladder + audio).
Usage: python3 build_all.py <voice .onnx>"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "learn"))
import sala as S, voice as VO, texts as T
from ladder_core import ladder, curve
import koine_voice as K
v = K.Voice(sys.argv[1]); PAGE = os.path.join(HERE, "page", "audio"); CRS = os.path.join(HERE, "course", "audio"); os.makedirs(PAGE, exist_ok=True); os.makedirs(CRS, exist_ok=True)
def sent_text(toks): return " ".join(("ha" if False else (S.number_word(x) if k == "num" else x)) for k, x in toks)
# ---- samples for the page
samples = {}
for name in ("john", "dialogue", "machine"):
    rows = []
    for i, (notation, eng) in enumerate(T.SETS[name]):
        text = S.render(notation); info = VO.speak(v, text, os.path.join(PAGE, f"{name}_{i + 1:02d}.mp3")); p = S.parse(text)
        rows.append(dict(sala=text, english=eng, literal=" ".join(S.english(s) for s in p), call=[S.to_call(s) for s in p], stance=[s["stance"] for s in p], hex=S.to_bytes(text).hex(), file=f"{name}_{i + 1:02d}.mp3", dur=info["dur"]))
    samples[name] = rows; print(name, len(rows), "recorded", flush=True)
json.dump(samples, open(os.path.join(HERE, "samples.json"), "w"), ensure_ascii=False, indent=1)
# ---- course units: every distinct sentence of every set
units, seen = [], set()
for name in ("starter", "dialogue", "machine", "john"):
    for notation, eng in T.SETS[name]:
        text = S.render(notation); sents = S.sentences(text)
        for toks, ann in zip(sents, S.annotate(text)):
            st = sent_text(toks)
            if st in seen: continue
            seen.add(st); units.append(dict(text=st, tokens=ann["tokens"], meaning=eng if len(sents) == 1 else ann["meaning"], literal=ann["meaning"]))
U = [[t["lemma"] for t in u["tokens"]] for u in units]; order = ladder(U, 400, min_len=1, max_len=14); cv = curve(U, order); steps = []
for n, (i, new, k) in enumerate(order, 1):
    u = units[i]; info = VO.speak(v, u["text"], os.path.join(CRS, f"step_{n:03d}.mp3"))
    toks = [dict(w=t["w"], lem=t["lemma"], g=t["gloss"], role=t["role"], hint=t["hint"], new=t["lemma"] in new) for t in u["tokens"]]
    hooks = {l: S.ROOT[l]["source"] for l in new if l in S.ROOT}
    steps.append(dict(n=n, ref="", new=new, mean=re.sub(r"^[AB]: ", "", u["meaning"]), toks=toks, hooks=hooks, a=dict(dur=info["dur"], words=[dict(s=w["s"], e=w["e"], say=t["w"], ipa=t["w"].lower().replace("y", "j")) for w, t in zip(info["words"], u["tokens"])])))
    if n % 20 == 0: print("course step", n, flush=True)
pack = dict(id="sala", name="Sala: first steps", lang="", langName="Sala", dir="ltr", audio="files", audioBase="audio/step_", refLabel="", steps=steps, curve=cv,
            distractors=sorted({t["gloss"] for u in units for t in u["tokens"]}),
            measured=[["Sentences in this starter text", str(len(units))], ["Different words in it", f"{len({x for u in U for x in u})} ({len({x for u in U for x in u if x in S.ROOT})} roots, the rest grammar words)"],
                      ["Sound system", "10 consonants and 5 vowels, each found in 56-97% of 3,020 languages surveyed (PHOIBLE)"], ["Sentence structure", "every sentence has exactly one parse; the same text is a function call for a machine"]])
tpl = open(os.path.join(ROOT, "learn", "template.html"), encoding="utf-8").read().replace("<title>Akouo</title>", "<title>Learn Sala</title>").replace("ἀκούω · I hear · the Echo Ladder", "sala · peace · the Echo Ladder").replace("<h1>Akouo</h1>", "<h1>Learn Sala</h1>").replace('"akouo2"', '"sala-course"')
open(os.path.join(HERE, "course", "index.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(pack, ensure_ascii=False, separators=(",", ":"))))
json.dump(dict(steps=len(steps), units=len(units), one_new=sum(len(set(s["new"])) == 1 for s in steps), curve_end=cv[-1], minutes=round(sum(s["a"]["dur"] for s in steps) / 60, 1)), open(os.path.join(HERE, "course_stats.json"), "w"), indent=1)
print("course:", len(steps), "steps of", len(units), "sentences;", sum(len(set(s["new"])) == 1 for s in steps), "add exactly one new word; end of ladder:", cv[-1], "; audio", round(sum(s["a"]["dur"] for s in steps) / 60, 1), "min")
print([(" ".join(t["w"] for t in s["toks"]), s["new"]) for s in steps[:8]])
