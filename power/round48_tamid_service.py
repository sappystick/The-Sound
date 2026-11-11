#!/usr/bin/env python3
"""Round 48. The daily Temple service as a score (Mishnah Tamid 7:3), with the ensemble specified in the sources.

Score, step by step from the text:
  1. Two priests with silver trumpets sound tekiah - teruah - tekiah (Tamid 7:3). Lengths from Rosh Hashanah 4:9:
     a tekiah = 3 teruot, a teruah = 3 'whimpers' (yevavot). One whimper = 0.30 s (assumed), so teruah 0.9 s
     (three short blasts), tekiah 2.7 s.
  2. Ben Arza strikes the cymbal (one cymbal only: Arakhin 2:5).
  3. The Levites (12 voices: Arakhin 2:6) sing the psalm of the day, with lyres (kinnor: 10 strings, plectrum;
     nabla: 12 notes, fingers - Josephus, Ant. 7.306) and the engine's Temple ensemble.
  4. The psalm is in three sections; at each break the trumpets sound a tekiah and the people bow (Tamid 7:3).
     Sunday's psalm is Psalm 24 (Tamid 7:4). The division into 1-2 / 3-6 / 7-10 is OUR choice (the Mishnah does
     not say where the breaks fall); it follows the psalm's own turns (creation / who may ascend / lift up your heads).
Pronunciation: the engine's Tiberian-type Hebrew (a reconstruction; Second Temple Hebrew was older).
Space: the Temple court, modelled with the engine's 'temple' reverberation (the Levites stood on the platform
outside the house).
Usage: python3 power/round48_tamid_service.py   -> power/audio/r48_tamid_service_psalm24.mp3, power/round48_results.json
"""
import json, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.io import wavfile
SR = E.SR
t = open(os.path.join(ROOT, "sources/texts/morphhb/wlc/Ps.xml"), encoding="utf-8").read()
def verse(v):
    m = re.search(rf'<verse osisID="Ps\.24\.{v}">(.*?)</verse>', t, re.S)
    ws = [re.sub(r"[֑-ֽ֯׀׃/]", "", re.sub(r"<[^>]+>", "", w)) for w in re.findall(r"<w[^>]*>(.*?)</w>", m.group(1))]
    return " ".join(w for w in ws if w)
SECTIONS = [(1, 2), (3, 6), (7, 10)]
YEV = 0.30; TERUAH = 3 * YEV; TEKIAH = 3 * TERUAH
F_TRUMPET = 233.0
def blast(d):
    n = int(d * SR); return E.inst_brass(F_TRUMPET, F_TRUMPET, n, bright=1.3)
def teruah():   # three short blasts filling one teruah
    seg = []
    for _ in range(3):
        n = int(YEV * 0.8 * SR); seg += [blast(YEV * 0.8), np.zeros(int(YEV * 0.2 * SR))]
    return np.concatenate(seg)
def two_trumpets(y):  # two priests, slightly detuned
    n = len(y); t_ = np.arange(n) / SR
    return y + 0.9 * np.interp(t_ * 1.004, t_, y, right=0)
def cymbal():
    return E.inst_cymbal()
def gap(s): return np.zeros(int(s * SR))
def norm(y, p=0.9): return E.norm(y, p)
parts, log = [], []
call = np.concatenate([blast(TEKIAH), gap(0.25), teruah(), gap(0.25), blast(TEKIAH)])
parts += [norm(two_trumpets(call)), gap(0.6), norm(cymbal(), 0.8), gap(0.8)]
log += [dict(t="tekiah-teruah-tekiah", seconds=round(len(call) / SR, 1)), dict(t="cymbal (Ben Arza)")]
for i, (a, b) in enumerate(SECTIONS):
    text = " ".join(verse(v) for v in range(a, b + 1))
    words = E.parse_hebrew(text, "tiberian")
    y, segs, notes, total = E.render(words, "hebrew", "tiberian", "chant", "temple", "temple", 110.0, None, True, 12)
    parts += [norm(y), gap(0.5)]
    log.append(dict(t=f"Levites: Psalm 24:{a}-{b}", seconds=round(len(y) / SR, 1), text=text))
    parts += [norm(two_trumpets(blast(TEKIAH))), gap(2.0)]
    log += [dict(t="tekiah (break)"), dict(t="the people bow: silence 2 s")]
y = np.concatenate(parts); y = E.reverb(norm(y), "temple")
wav = os.path.join(HERE, "audio", "r48_tamid_service_psalm24.wav"); wavfile.write(wav, SR, (norm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
out = dict(score=log, total_seconds=round(len(y) / SR, 1), file=os.path.relpath(mp3, ROOT),
           rhythm=dict(yevava_s=YEV, teruah_s=TERUAH, tekiah_s=TEKIAH, rule="Rosh Hashanah 4:9: tekiah = 3 teruot; teruah = 3 yevavot"),
           ensemble=dict(trumpets=2, cymbal=1, voices=12, lyres="engine Temple ensemble (kinnor, nevel, halil)", sources=["Tamid 7:3-4", "Arakhin 2:3-6", "Josephus Ant. 7.306"]),
           choices=["whimper length 0.30 s", "section breaks 1-2/3-6/7-10", "trumpet pitch 233 Hz", "Tiberian-type pronunciation", "court reverberation"])
json.dump(out, open(os.path.join(HERE, "round48_results.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "score"}, ensure_ascii=False)); print([s["t"] for s in log])
