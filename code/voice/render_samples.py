#!/usr/bin/env python3
"""Render the sample passages in three versions for listening comparison, and write a full trace per passage.
  A  current engine (formant synthesis), declaimed, synagogue
  B  Koine neural voice, evidence layer only (accent, declination, cadences, stress, room)
  C  Koine neural voice, evidence + interpretive delivery layer (speaker, mood, emphasis)
Outputs: audio_model/v2/<passage>_{A_engine,B_evidence,C_full}.mp3 and <passage>_C_full.json (every word: speaker, times,
pitch targets, gain, rule ids) plus measured pitch (F0) of the final audio.
Usage: python3 render_samples.py <sblgnt dir> <voice .onnx>
"""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import koine_voice as K
E = K.E
SBL, MODEL = sys.argv[1:3]; OUT = os.path.join(ROOT, "audio_model", "v2"); os.makedirs(OUT, exist_ok=True)
PASSAGES = {"prologue_1-1-5": [(1, v) for v in range(1, 6)], "lazarus_11-32-36": [(11, v) for v in range(32, 37)],
            "vine_15-1-5": [(15, v) for v in range(1, 6)], "finished_19-28-30": [(19, v) for v in range(28, 31)]}
V = K.assign_speakers(K.load_john(SBL)); voice = K.Voice(MODEL)
def mp3(y, path):
    tmp = path[:-4] + ".wav"; wavfile.write(tmp, E.SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-b:a", "96k", path], check=True); return tmp
index = {}
for name, refs in PASSAGES.items():
    text = " ".join(t["raw"] for r in refs for t in V[r])
    wa = os.path.join(OUT, f"{name}_A_engine.wav"); E.make(text, "greek", "koine", "declaim", "none", wa, space="synagogue")
    sr, ya = wavfile.read(wa); mp3(ya.astype(float) / 32768, os.path.join(OUT, f"{name}_A_engine.mp3")); os.remove(wa); os.remove(wa[:-4] + ".json")
    yb, _ = K.render_passage(voice, V, refs, delivery=False); os.remove(mp3(yb, os.path.join(OUT, f"{name}_B_evidence.mp3")))
    yc, words = K.render_passage(voice, V, refs, delivery=True); wc = mp3(yc, os.path.join(OUT, f"{name}_C_full.mp3"))
    f0 = K.measure_f0(yc, E.SR)
    json.dump(dict(passage=name, refs=[f"{c}:{v}" for c, v in refs], duration_s=round(len(yc) / E.SR, 2), voice=os.path.basename(MODEL), room="synagogue",
                   words=words, f0=f0, rulebook="code/voice/delivery_rules.json"), open(os.path.join(OUT, f"{name}_C_full.json"), "w"), ensure_ascii=False, indent=0)
    os.replace(wc, os.path.join(OUT, f"{name}_C_full.wav"))   # kept for the video renderer (not committed)
    spk = sorted({w["speaker"] for w in words}); rules = sorted({r for w in words for r in w["rules"]})
    index[name] = dict(duration=round(len(yc) / E.SR, 1), speakers=spk, rules=rules)
    print(name, index[name], flush=True)
json.dump(index, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
