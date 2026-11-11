#!/usr/bin/env python3
"""Round 58. (A) John 1:1-18 played on the ark instrument (round 57); (B) the construction texts not yet included,
calculated and added.

A. Every syllable of the prologue (SBLGNT, Koine pronunciation) plucks the ark-zither string of its vowel (Nicomachus;
   Koine omega = omicron, so the lowest string is silent), held for its length (short 0.30 s, long 0.60 s), sounding
   through the ark box's own modes. The menorah pipes hold the mese softly throughout; pauses at punctuation (breath);
   at 1:12, the prologue's syllable centre (claim C1), the pipes open to the fourth and fifth; 1:18 closes on the mese.
B. Additions (texts checked on Sefaria this round): 1 Kgs 6:6 side chambers 5/6/7 cubits; Exod 26:28 the centre bar;
   1 Kgs 7:49 ten lampstands; Zech 4:2 seven lamps with seven pipes; 1 Chr 15:20-21 alamoth / sheminith; 1 Chr 25:7
   288 singers; 1 Kgs 10:12 almug-wood lyres; Mishnah Middot 4:6 Herod's 100-cubit house; Rev 21:16-17 the cube city.
Usage: python3 power/round58_prologue_and_additions.py
"""
import itertools, json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import fftconvolve
from scipy.io import wavfile
SR = E.SR; C = 343.0; CU = 0.445; rng = np.random.default_rng(58); out = {}
f_len = lambda cubits, cu=CU: C / (2 * cubits * cu)
def note(f):
    m = 69 + 12 * math.log2(f / 440); n = round(m); N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{N[n % 12]}{n // 12 - 1}{(m - n) * 100:+.0f}c"
R57 = json.load(open(os.path.join(HERE, "round57_results.json")))
STR = {s["vowel"]: s for s in R57["instrument"]["ark_box_zither"]["strings"]}
MESE = STR["ι"]["Hz"]; BOX = R57["instrument"]["ark_box_zither"]["box_modes_below_1kHz"]
# the ark box impulse response from its modes (all modes below 1 kHz)
Lx, Ly, Lz = 2.5 * CU, 1.5 * CU, 1.5 * CU
modes = sorted(C / 2 * math.sqrt((a / Lx) ** 2 + (b / Ly) ** 2 + (c / Lz) ** 2) for a, b, c in itertools.product(range(7), range(4), range(4)) if (a, b, c) != (0, 0, 0))
modes = [m for m in modes if m < 1000]
t_ir = np.arange(int(0.6 * SR)) / SR
IR = sum(np.cos(2 * np.pi * f * t_ir + rng.uniform(0, 6.28)) * np.exp(-t_ir * 6.91 / 0.35) / (1 + f / 400) for f in modes); IR /= np.abs(IR).max()
def gut(f, d):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 22):
        if k * f > 7000: break
        y += np.sin(2 * np.pi * k * f * t * (1 + 0.0003 * k * k)) * abs(math.sin(k * math.pi * 0.17)) / k * np.exp(-t * (0.9 + 0.35 * k))
    return fftconvolve(y, IR)[:n + len(IR) // 2]
def pipe(f, n):
    t = np.arange(n) / SR; return sum(np.sin(2 * np.pi * f * k * t) / k ** 1.3 for k in (1, 3, 5, 7)) + 0.015 * rng.standard_normal(n)
IPA2GK = {"a": "α", "ɛ": "ε", "e": "η", "i": "ι", "o": "ο", "y": "υ", "ɔ": "ο", "u": "ο"}   # Koine: omega sounds as o
V = {}
for l in open(os.path.join(ROOT, "sources/texts/sblgnt/64-Jn-morphgnt.txt"), encoding="utf-8"):
    r = (int(l[2:4]), int(l[4:6]))
    if r[0] == 1 and r[1] <= 18: V.setdefault(r, []).append(l.split()[3])
PAUSE = {".": 0.9, ";": 0.9, "·": 0.6, ",": 0.35}
events, t, verse_t, used = [], 1.0, {}, {}
for r, ws in V.items():
    verse_t[f"1:{r[1]}"] = round(t, 1)
    for w in ws:
        for pw in E.parse_greek(w, "koine"):
            for s in pw:
                if not s.get("nuc"): continue
                g = IPA2GK.get(s["nuc"][0].rstrip("ː"), "α"); L = 0.60 if (s.get("long") or s["nuc"][0].endswith("ː")) else 0.30
                events.append((t, STR[g]["Hz"], L)); used[STR[g]["string"]] = used.get(STR[g]["string"], 0) + 1; t += L
        t += PAUSE.get(w[-1], 0.04)
    t += 0.5
T = t + 4.0; mix = np.zeros(int(T * SR))
cache = {}
for t0, f, L in events:
    key = (f, L)
    if key not in cache: cache[key] = E.norm(gut(f, max(1.2, L * 2.5)))
    E.place(mix, 0.55 * cache[key], t0)
n = len(mix); tt = np.arange(n) / SR
drone = pipe(MESE, n) * np.minimum(1, tt / 3) * np.minimum(1, (T - tt) / 3)
c12, c13 = verse_t["1:12"], verse_t["1:13"]
open_ = np.clip((tt - c12) / 1.5, 0, 1) * np.clip((c13 + 4 - tt) / 2.0, 0, 1)
centre = (pipe(MESE * 4 / 3, n) + pipe(MESE * 3 / 2, n)) * open_
mix += 0.10 * E.norm(drone) + 0.08 * E.norm(centre)
E.MODAL_ROOMS["tabernacle_hoh"] = ((10 * CU,) * 3, 2.0)
y = E.reverb(E.norm(mix), "tabernacle_hoh")
wav = os.path.join(HERE, "audio", "r58_prologue_ark_instrument.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
out["A_prologue"] = dict(file=os.path.relpath(mp3, ROOT), seconds=round(len(y) / SR, 1), syllables=len(events), verse_start_seconds=verse_t,
    strings_played=dict(sorted(used.items(), key=lambda kv: -kv[1])), centre="1:12 (syllable centre of the prologue): the pipes open to the fourth and fifth above the mese")

# ---------------------------------------------------------------- B. additions
def bar(L_m, v): return v / (2 * L_m)
add = {
 "Solomon's side chambers (1 Kgs 6:6): 5, 6, 7 cubits wide, explicit": dict(Hz=[round(f_len(w), 1) for w in (5, 6, 7)], notes=[note(f_len(w)) for w in (5, 6, 7)],
     chord="frequencies 1/5 : 1/6 : 1/7 = 42 : 35 : 30, a minor third (6:5) over a septimal minor third (7:6): a narrow, dark, diminished-type chord"),
 "The centre bar (Exod 26:28): one bar through the boards from end to end, 30 cubits": dict(length_m=round(30 * CU, 2),
     longitudinal_Hz_range=[round(bar(30 * CU, 3500), 0), round(bar(30 * CU, 5000), 0)], note="along-grain sound speed of hardwood 3,500-5,000 m/s: the bar's lowest ring spans 131-187 Hz, the range of the ark zither"),
 "Ten lampstands (1 Kgs 7:49)": dict(lamps=70, mapping="the menorah multiplied: 5 on the right, 5 on the left = ten seven-pipe ranks, 70 pipes"),
 "Seven lamps with seven pipes (Zech 4:2)": dict(mapping="the text itself names 'pipes' (Hebrew mutsaqot, conduits) on a seven-lamp golden stand"),
 "Harps on alamoth, lyres on the sheminith (1 Chr 15:20-21)": dict(reading="widely read as registers: alamoth = high ('maidens'), sheminith = 'the eighth', an octave (K: meaning uncertain)",
     mapping="the ark zither doubled: one rank high, one an octave below", octave_below_Hz=[round(STR[g]["Hz"] / 2, 1) for g in "ωυοιηεα"]),
 "288 trained singers (1 Chr 25:7)": dict(structure="24 courses x 12", note="Josephus' nabla has 12 notes; 24 x 12 = 288"),
 "Almug-wood lyres and harps (1 Kgs 10:12)": dict(note="the only explicit instruction to build instruments for the House"),
 "Herod's temple (Mishnah Middot 4:6)": dict(house="100 x 100 x 100 cubits, a cube", Hz=round(f_len(100), 2), note="the temple Jesus taught in was itself a cube; its Holy of Holies 20 x 20 (Middot 4:7); 15 steps where the Levites sang (Middot 2:5)"),
 "The New Jerusalem (Rev 21:16-17)": dict(city="a cube, 12,000 stadia each way (about 2,220 km)", wall="144 cubits", note="the final Holy of Holies is a cube: the same shape as the tabernacle's and Solomon's inner rooms and Herod's house"),
}
out["B_additions"] = add
out["B_still_missing"] = ["Tabernacle: the boards' tenons and the 5 bars per side (Exod 26:15-29); the entrance screen on 5 pillars; the court's 60 pillars with silver hooks and bands (Exod 27:9-19)",
    "Tabernacle: the laver made from bronze mirrors (Exod 38:8); the anointing oil and incense recipes (Exod 30:22-38)",
    "Priestly garments in full: ephod, onyx shoulder stones with 12 names, sash, tunic, turban, the gold plate 'Holy to the LORD' (Exod 28)",
    "Solomon: ten lavers on wheeled stands, 4 cubits, 40 baths each (1 Kgs 7:27-39); the doors of olive wood with five- and four-sided frames (1 Kgs 6:31-35); windows (6:4)",
    "Ezekiel 40-48 in full: six gates with chambers and porches, 30 chambers on the pavement, the kitchens, the east gate shut (44:1-2)",
    "Other sound objects with instructions: Joshua's seven shofars (Josh 6); Gideon's 300 trumpets and smashed jars (Judg 7:16-20); Miriam's drum (Exod 15:20); David's instruments (1 Chr 23:5)",
    "Herod's temple in full: Mishnah Middot 1-5 and Josephus, War 5.184-237 (the Nicanor gate, the 15 steps, the golden vine over the entrance)"]
json.dump(out, open(os.path.join(HERE, "round58_results.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out["A_prologue"], ensure_ascii=False)); print(json.dumps(add["Solomon's side chambers (1 Kgs 6:6): 5, 6, 7 cubits wide, explicit"], ensure_ascii=False)); print(add["The centre bar (Exod 26:28): one bar through the boards from end to end, 30 cubits"])
