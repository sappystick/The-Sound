#!/usr/bin/env python3
"""Experiments 3 and 4, the parts that can be run by computation.

E3  THE SEVEN VOWELS. Measure, in the rendered chant (power/audio/seven_vowels.mp3), which harmonic of the sung note is
    strongest in the second-formant region (600-2,600 Hz) in each vowel, and compare with the prediction (F2 / f0).
    Also print, for any chosen note, the overtone melody the seven vowels would produce.
E4  ROOMS. Resonant frequencies (room modes) of the rooms described in the texts, treated as rigid rectangular boxes:
    f = (c/2) * sqrt((nx/Lx)^2 + (ny/Ly)^2 + (nz/Lz)^2).
      - the inner sanctuary of the tabernacle: a 10-cubit cube (inferred from Exodus 26)
      - the inner sanctuary of Solomon's temple: 'twenty cubits long, twenty wide, twenty high' (1 Kings 6:20)
      - Solomon's temple hall (house): 60 x 20 x 30 cubits (1 Kings 6:2)
      - the King's Chamber, Great Pyramid: 10.47 x 5.24 x 5.84 m (commonly published survey dimensions)
    with two cubits: 0.445 m (common) and 0.523 m (royal Egyptian). Counted: modes in the male chanting range
    (85-180 Hz), and 'stacked' frequencies where several modes coincide (a cube stacks three at every axial step).
Usage: python3 e3_e4_compute.py   (writes experiments/e3_e4_results.json)
"""
import itertools, json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); out = {}
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
# ---------------------------------------------------------------- E3
print("E3. SEVEN VOWELS: strongest harmonic in the 600-2,600 Hz band, measured vs predicted")
tmp = os.path.join(HERE, "_sv.wav"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(ROOT, "power/audio/seven_vowels.mp3"), "-ac", "1", "-ar", "44100", tmp], check=True)
from scipy.io import wavfile
sr, y = wavfile.read(tmp); os.remove(tmp); y = y.astype(float) / 32768
import parselmouth
snd = parselmouth.Sound(y, sampling_frequency=sr); pitch = snd.to_pitch(time_step=0.01, pitch_floor=60, pitch_ceiling=400)
pt, pf = pitch.xs(), pitch.selected_array["frequency"]; voiced = pf > 0
env = np.array([np.sqrt(np.mean(y[int(t * sr) - 441: int(t * sr) + 441] ** 2)) if int(t * sr) > 441 else 0 for t in pt])
# segment the chant into 7 vowels: voiced frames grouped into the 7 largest runs between intensity dips
idx = np.flatnonzero(voiced & (env > 0.15 * env.max())); runs, cur = [], [idx[0]]
for a, b in zip(idx, idx[1:]):
    if b - a > 3: runs.append(cur); cur = [b]
    else: cur.append(b)
runs.append(cur); runs = sorted(sorted(runs, key=len, reverse=True)[:7], key=lambda r: r[0])
if len(runs) < 7:   # fall back to equal division of the voiced span
    span = np.arange(idx[0], idx[-1] + 1); runs = [list(c) for c in np.array_split(span, 7)]
VOW = [("α", "a"), ("ε", "e"), ("η", "ɛ"), ("ι", "i"), ("ο", "o"), ("υ", "y"), ("ω", "ɔ")]; e3 = []
for (g, ipa), r in zip(VOW, runs):
    mid = r[len(r) // 4: 3 * len(r) // 4] or r; t0, t1 = pt[mid[0]], pt[mid[-1]]; f0 = float(np.median(pf[mid][pf[mid] > 0]))
    seg = y[int(t0 * sr): int(t1 * sr)]; seg = seg * np.hanning(len(seg)); spec = np.abs(np.fft.rfft(seg, 1 << 16)); fr = np.fft.rfftfreq(1 << 16, 1 / sr)
    hs = [h for h in range(1, 60) if 600 <= h * f0 <= 2600]; amp = {h: spec[np.argmin(np.abs(fr - h * f0))] for h in hs}; best = max(amp, key=amp.get)
    pred = round(E.VOWELS[ipa][1] / f0); e3.append(dict(letter=g, ipa=ipa, f0=round(f0, 1), measured_harmonic=best, measured_hz=round(best * f0), predicted_harmonic=pred, match=abs(best - pred) <= 1))
    print(f"   {g} /{ipa}/  sung at {f0:6.1f} Hz: strongest harmonic {best:2d} ({best * f0:5.0f} Hz); predicted {pred:2d}  {'✓' if abs(best - pred) <= 1 else '·'}")
print(f"   {sum(x['match'] for x in e3)} of 7 within one harmonic of the prediction")
out["E3"] = e3
print("   overtone melody for other notes (harmonic numbers brightened, alpha to omega):")
for f0 in (98.0, 110.0, 130.8, 146.8, 196.0): print(f"     {f0:6.1f} Hz: " + " ".join(f"{round(E.VOWELS[i][1] / f0):2d}" for _, i in VOW))
# ---------------------------------------------------------------- E4
print("\nE4. ROOM RESONANCES")
c = 343.0
ROOMS = [("Tabernacle inner sanctuary (10-cubit cube)", (10, 10, 10), "cubit"), ("Solomon's inner sanctuary (20-cubit cube, 1 Kings 6:20)", (20, 20, 20), "cubit"),
         ("Solomon's temple hall (60 x 20 x 30 cubits, 1 Kings 6:2)", (60, 20, 30), "cubit"), ("King's Chamber, Great Pyramid", (10.47, 5.24, 5.84), "m")]
def modes(L, fmax=260):
    res = []
    for n in itertools.product(range(0, 25), repeat=3):
        if n == (0, 0, 0): continue
        f = c / 2 * math.sqrt(sum((k / l) ** 2 for k, l in zip(n, L)))
        if f <= fmax: res.append((round(f, 1), n))
    return sorted(res)
e4 = []
for name, dims, unit in ROOMS:
    for cub in ((0.445, 0.523) if unit == "cubit" else (1.0,)):
        L = tuple(d * cub for d in dims); M = modes(L); band = [m for m in M if 85 <= m[0] <= 180]
        stacks = {}
        for f, n in M: stacks.setdefault(round(f, 0), []).append(n)
        strong = sorted([(f, len(v)) for f, v in stacks.items() if len(v) >= 3 and 85 <= f <= 180])
        lowest = M[0][0]; label = f"{name}" + (f", cubit {cub} m" if unit == "cubit" else "")
        print(f"   {label}: {L[0]:.2f} x {L[1]:.2f} x {L[2]:.2f} m; lowest mode {lowest} Hz; {len(band)} modes in 85-180 Hz; frequencies where 3 or more modes coincide: {', '.join(f'{f:.0f} Hz ×{k}' for f, k in strong) or 'none'}")
        e4.append(dict(room=label, dims_m=[round(x, 2) for x in L], lowest=lowest, modes_85_180=len(band), stacked=strong, axial=[round(c / (2 * L[0]) * k, 1) for k in range(1, 12)]))
out["E4"] = e4
cube = [r for r in e4 if r["room"].startswith("Solomon's inner sanctuary") and "0.445" in r["room"]][0]
print(f"   in a cube the axial modes of all three directions coincide: Solomon's inner sanctuary (common cubit) rings at {', '.join(str(x) for x in cube['axial'][:9])} Hz, each three-fold")
json.dump(out, open(os.path.join(HERE, "e3_e4_results.json"), "w"), ensure_ascii=False, indent=1)
