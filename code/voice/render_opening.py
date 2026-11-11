#!/usr/bin/env python3
"""Render the opening pages of John (1:1-2:11) with the Koine voice v2, all layers, and annotate every word with:
speaker, probable original language (language_layer.json), Aramaic words kept in the Greek, and how the verse reads in
the four earliest manuscripts (P66, P75, Sinaiticus, Vaticanus: words that differ from SBLGNT, and how many of those
differences sound the same in Koine).
Outputs: audio_model/v2/opening_*_C_full.{mp3,json,wav}, opening_index.json
Usage: python3 render_opening.py <sblgnt dir> <voice .onnx> <cntr class-1 dir>
"""
import difflib, json, os, re, subprocess, sys
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import koine_voice as K
E = K.E; SBL, MODEL, CN = sys.argv[1:4]; OUT = os.path.join(ROOT, "audio_model", "v2")
LL = json.load(open(os.path.join(HERE, "language_layer.json"), encoding="utf-8"))
SECTIONS = [("opening_1_prologue", "The Word (prologue)", [(1, v) for v in range(1, 19)]),
            ("opening_2_baptist", "The voice in the wilderness", [(1, v) for v in range(19, 35)]),
            ("opening_3_disciples", "Come and see", [(1, v) for v in range(35, 52)]),
            ("opening_4_cana", "The wedding at Cana", [(2, v) for v in range(1, 12)])]
NS = {"θσ": "θεοσ", "θυ": "θεου", "θν": "θεον", "θω": "θεω", "ισ": "ιησουσ", "ιυ": "ιησου", "ιν": "ιησουν", "κσ": "κυριοσ", "κυ": "κυριου", "κν": "κυριον", "κε": "κυριε",
      "χσ": "χριστοσ", "χυ": "χριστου", "χν": "χριστον", "πηρ": "πατηρ", "πρσ": "πατροσ", "πρα": "πατερα", "πρι": "πατρι", "περ": "πατερ", "πρ": "πατηρ", "υσ": "υιοσ",
      "υν": "υιον", "υυ": "υιου", "πνα": "πνευμα", "πνσ": "πνευματοσ", "πνι": "πνευματι", "ανοσ": "ανθρωποσ", "ανον": "ανθρωπον", "ανου": "ανθρωπου", "ανοι": "ανθρωποι", "ανων": "ανθρωπων", "ιηλ": "ισραηλ"}
def ms(fn):
    V = {}
    for l in open(os.path.join(CN, fn), encoding="utf-8"):
        if not l.startswith("43"): continue
        t = re.sub(r"x\{[^}]*\}", "", l[9:]).replace("a{", "").replace("{", "").replace("}", ""); ws = []
        for tok in t.split():
            w = K.nrm(re.sub(r"[0-9/]", "", tok))
            if w: ws.append(NS.get(w, w) if "=" in tok else w)
        V[(int(l[2:5]), int(l[5:8]))] = ws
    return V
MSS = {n: ms(f) for n, f in (("P66", "P66.txt"), ("P75", "P75.txt"), ("Sinaiticus", "01.txt"), ("Vaticanus", "03.txt"))}
_k = {}
def sound(w):
    if w not in _k:
        try: _k[w] = "".join(p for s in E.parse_greek(w, "koine-late")[0] for p in s["ph"]).replace("ː", "")
        except Exception: _k[w] = w
    return _k[w]
def ms_line(ref, sbl_words):
    out = []
    for name, V in MSS.items():
        if ref not in V: out.append(f"{name}: not extant"); continue
        a, b = sbl_words, V[ref]; diff = same = 0
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal": continue
            k = max(i2 - i1, j2 - j1); diff += k
            if tag == "replace" and i2 - i1 == j2 - j1: same += sum(sound(x) == sound(y) for x, y in zip(a[i1:i2], b[j1:j2]))
        out.append(f"{name}: same wording" if diff == 0 else (f"{name}: {diff} words differ" if diff > 1 else f"{name}: 1 word differs") + (f" ({same} sound{'s' if same == 1 else ''} the same when read aloud)" if same else ""))
    return out
V = K.assign_speakers(K.load_john(SBL)); voice = K.Voice(MODEL); index = []
for name, label, refs in SECTIONS:
    y, words = K.render_passage(voice, V, refs, delivery=True)
    lem = [t["lem"] for r in refs for t in V[r]]
    for w, l in zip(words, lem):
        ll = LL["speakers"].get(w["speaker"], LL["default"]); w["lang"] = ll["lang"]; w["lang_conf"] = ll["confidence"]
        if l in LL["aramaic_words"]: w["aram"] = LL["aramaic_words"][l]
    mss = {f"{c}:{v}": ms_line((c, v), [t["w"] for t in V[(c, v)]]) for c, v in refs}
    wav = os.path.join(OUT, f"{name}_C_full.wav"); wavfile.write(wav, E.SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", wav[:-4] + ".mp3"], check=True)
    json.dump(dict(passage=name, label=label, refs=[f"{c}:{v}" for c, v in refs], duration_s=round(len(y) / E.SR, 2), voice=os.path.basename(MODEL), room="synagogue",
                   words=words, mss=mss, f0=K.measure_f0(y, E.SR)), open(os.path.join(OUT, f"{name}_C_full.json"), "w"), ensure_ascii=False, indent=0)
    info = dict(name=name, label=label, refs=[f"{refs[0][0]}:{refs[0][1]}", f"{refs[-1][0]}:{refs[-1][1]}"], duration=round(len(y) / E.SR, 1), speakers=sorted({w["speaker"] for w in words}),
                rules=sorted({r for w in words for r in w["rules"]}), aramaic=sorted({w["word"].strip(",.;·") for w in words if w.get("aram")}))
    index.append(info); print(info, flush=True)
json.dump(index, open(os.path.join(OUT, "opening_index.json"), "w"), ensure_ascii=False, indent=1)
