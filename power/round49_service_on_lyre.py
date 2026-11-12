#!/usr/bin/env python3
"""Round 49. The daily Temple service (round 48) played on the seven-string lyre with vowel tubes (rounds 41-44).

The trumpets (tekiah-teruah-tekiah, Rosh Hashanah 4:9 ratios) and the single cymbal are kept. Psalm 24 is no longer
sung by voices: each Hebrew syllable plucks the Nicomachus string of its vowel and sounds through that vowel's tube
(round-42 three-section resonators), held for the syllable's length.
Vowel -> string: a Moon (nete), e Venus (trite), ɛ Mercury (paranete), i Sun (mese), o Mars (lichanos),
ɔ (Tiberian qamets) Saturn (hypate). OUR choices: u -> Jupiter (parhypate, the 'u-letter' upsilon), shewa ə -> Mercury,
short. Section breaks 1-2 / 3-6 / 7-10, as in round 48. Reports which strings Hebrew sounds (vs Koine Greek, where the
hypate is silent).
Usage: python3 power/round49_service_on_lyre.py
"""
import json, math, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
SR = E.SR
R41 = json.load(open(os.path.join(HERE, "round41_results.json")))["instrument"]["heptachord_lyre"]
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
STR = {s["vowel"]: s for s in R41}
V2GK = {"a": "α", "ɑ": "α", "e": "η", "ɛ": "ε", "i": "ι", "o": "ο", "ɔ": "ω", "u": "υ", "ə": "ε", "y": "υ"}
V2TUBE = {"a": "a", "ɑ": "a", "e": "e", "ɛ": "ɛ", "i": "i", "o": "o", "ɔ": "ɔ", "u": "o", "ə": "ɛ", "y": "y"}
t = open(os.path.join(ROOT, "sources/texts/morphhb/wlc/Ps.xml"), encoding="utf-8").read()
def verse(v):
    m = re.search(rf'<verse osisID="Ps\.24\.{v}">(.*?)</verse>', t, re.S)
    ws = [re.sub(r"[֑-ֽ֯׀׃/]", "", re.sub(r"<[^>]+>", "", w)) for w in re.findall(r"<w[^>]*>(.*?)</w>", m.group(1))]
    return " ".join(w for w in ws if w)
def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, b in zip(freqs, bws): bb, aa = E.resonator_coeffs(f, b); y += lfilter(bb, aa, x)
    return y
def pluck(f0, n):
    tt = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 30):
        if k * f0 > 8000: break
        y += np.sin(2 * np.pi * k * f0 * tt) * abs(math.sin(k * math.pi * 0.2)) / k * np.exp(-tt * (1.2 + 0.5 * k))
    return y
def lyre_tubes(text, beat=0.36):
    seq, out = [], []
    for w in E.parse_hebrew(text, "tiberian"):
        for s in w:
            if not s.get("nuc"): continue
            v = s["nuc"][0].rstrip("ː"); g = V2GK.get(v, "α"); st = STR[g]
            L = beat * (0.5 if v == "ə" else (2 if (s.get("long") or s["nuc"][0].endswith("ː")) else 1)); n = int(L * SR)
            tone = pluck(st["Hz"], n); sp = resonate(tone, R42[V2TUBE.get(v, "a")]["machine"])
            out.append(0.45 * tone / (np.abs(tone).max() + 1e-9) + 0.55 * sp / (np.abs(sp).max() + 1e-9)); seq.append(st["string"])
        out.append(np.zeros(int(0.1 * SR)))
    return np.concatenate(out), seq
YEV = 0.30; TERUAH = 3 * YEV; TEKIAH = 3 * TERUAH
def blast(d): return E.inst_brass(233.0, 233.0, int(d * SR), bright=1.3)
def teruah(): return np.concatenate([np.concatenate([blast(YEV * 0.8), np.zeros(int(YEV * 0.2 * SR))]) for _ in range(3)])
def gap(s): return np.zeros(int(s * SR))
def nm(y, p=0.9): return E.norm(y, p)
parts = [nm(np.concatenate([blast(TEKIAH), gap(0.25), teruah(), gap(0.25), blast(TEKIAH)])), gap(0.6), nm(E.inst_cymbal(), 0.8), gap(0.8)]
allseq = []
for a, b in [(1, 2), (3, 6), (7, 10)]:
    y, seq = lyre_tubes(" ".join(verse(v) for v in range(a, b + 1))); allseq += seq
    parts += [nm(y), gap(0.5), nm(blast(TEKIAH)), gap(2.0)]
y = E.reverb(nm(np.concatenate(parts)), "temple")
wav = os.path.join(HERE, "audio", "r49_tamid_psalm24_lyre_tubes.wav"); wavfile.write(wav, SR, (nm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
names = [s["string"] for s in R41]
share = {n: round(allseq.count(n) / len(allseq), 3) for n in names}
out = dict(file=os.path.relpath(mp3, ROOT), seconds=round(len(y) / SR, 1), syllables=len(allseq), string_shares=share,
           hypate_sounds=share["hypate"] > 0, most_sounded=max(share, key=share.get),
           note="Hebrew qamets (ɔ) sounds the hypate (Saturn), the string Koine Greek leaves silent (round 45)")
json.dump(out, open(os.path.join(HERE, "round49_results.json"), "w"), ensure_ascii=False, indent=1); print(out)
