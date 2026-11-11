#!/usr/bin/env python3
"""Record every ladder step with the Koine voice v2 (evidence rules only, slower learner's pace, small room) and store
word timings, IPA and a plain respelling. Output: learn/audio/step_NNN.mp3, learn/ladder_audio.json
Usage: python3 render_audio.py <voice .onnx>"""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "code", "voice"))
import koine_voice as K
E = K.E; K.VC["base_length_scale"] = 1.32; OUT = os.path.join(HERE, "audio"); os.makedirs(OUT, exist_ok=True)
RESP = {"a": "ah", "e": "eh", "ɛ": "e", "i": "ee", "o": "o", "u": "oo", "y": "ü", "ɣ": "gh", "ð": "dh", "θ": "th", "x": "kh", "ŋ": "ng", "pʰ": "p", "tʰ": "t", "kʰ": "k", "j": "y", "ʝ": "y", "ç": "h"}
def respell(sylls):
    out = []
    for s in sylls:
        t = "".join(RESP.get(p.replace("ː", ""), p.replace("ː", "")) for p in s["ph"]); out.append(t.upper() if s.get("accent") and s["accent"] != "grave" else t)
    return "-".join(out)
L = json.load(open(os.path.join(HERE, "ladder.json"), encoding="utf-8")); voice = K.Voice(sys.argv[1]); meta = {}
for st in L["steps"]:
    toks = [dict(raw=t["w"], w=K.nrm(t["w"]), lem=K.nrm(t["lem"]), pos="", parse="--------", spk="narrator") for t in st["toks"]]
    y, words = K.render_passage(voice, {(st["n"], 1): toks}, [(st["n"], 1)], delivery=False, space="house_church", verse_gap=0.3)
    wav = os.path.join(OUT, f"step_{st['n']:03d}.wav"); wavfile.write(wav, E.SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-b:a", "64k", wav[:-4] + ".mp3"], check=True); os.remove(wav)
    meta[st["n"]] = dict(dur=round(len(y) / E.SR, 2), words=[dict(s=w["start"], e=w["end"], ipa=w["ipa"], say=respell(K.word_ipa(w["word"]))) for w in words])
    if st["n"] % 25 == 0: print(st["n"], flush=True)
json.dump(meta, open(os.path.join(HERE, "ladder_audio.json"), "w"), ensure_ascii=False)
print("total", round(sum(m["dur"] for m in meta.values()) / 60, 1), "min")
