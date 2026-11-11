#!/usr/bin/env python3
"""E3 stimulus: the seven vowels on one exactly held note (source-filter synthesis, engine primitives), 1.6 s each with
smooth 0.25 s glides between vowels, then measurement of the strongest harmonic in each vowel's second-formant band.
Also the cube-vs-ordinary-room control for E4. Writes experiments/audio/e3_seven_vowels_110hz.mp3 and e3_e4_results.json (adds keys)."""
import itertools, json, math, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True); SR = E.SR
VOW = [("α", "a"), ("ε", "e"), ("η", "ɛ"), ("ι", "i"), ("ο", "o"), ("υ", "y"), ("ω", "ɔ")]
VOWELS = dict(E.VOWELS); VOWELS["y"] = (270, 1700, 2150)     # front rounded: F2 lower than [i] and [e] (rounding lowers F2)
F0, HOLD, GLIDE = 110.0, 1.6, 0.25
tracks = [[], [], []]
for k, (g, ipa) in enumerate(VOW):
    F = VOWELS[ipa]; nxt = VOWELS[VOW[k + 1][1]] if k + 1 < len(VOW) else F
    for j in range(3):
        tracks[j] += [F[j]] * int(HOLD * SR) + list(np.linspace(F[j], nxt[j], int(GLIDE * SR)))
n = len(tracks[0]); f0 = np.full(n, F0)
src = E.glottal_source(f0, vib=0.0, jitter=0.0); y = E.formant_filter(src, *[np.array(t) for t in tracks])
y = y / np.abs(y).max() * 0.8; fade = int(0.05 * SR); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
dry = y.copy(); wet = E.reverb(y, "temple")
for name, sig in (("e3_seven_vowels_110hz_dry", dry), ("e3_seven_vowels_110hz_temple", wet)):
    w = os.path.join(HERE, "audio", name + ".wav"); wavfile.write(w, SR, (sig / np.abs(sig).max() * 0.9 * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-b:a", "160k", w[:-4] + ".mp3"], check=True); os.remove(w)
res = []
for k, (g, ipa) in enumerate(VOW):
    a = int((k * (HOLD + GLIDE) + 0.3) * SR); b = a + int((HOLD - 0.6) * SR); seg = dry[a:b] * np.hanning(b - a)
    spec = np.abs(np.fft.rfft(seg, 1 << 17)); fr = np.fft.rfftfreq(1 << 17, 1 / SR)
    hs = range(1, 40); amp = {h: spec[np.argmin(np.abs(fr - h * F0))] for h in hs}
    band = {h: v for h, v in amp.items() if 500 <= h * F0 <= 2700 and abs(h * F0 - VOWELS[ipa][0]) > 150}   # F2 region, away from F1
    best = max(band, key=band.get); pred = round(VOWELS[ipa][1] / F0); res.append(dict(letter=g, ipa=ipa, measured=best, predicted=pred))
    print(f"   {g} /{ipa}/: strongest upper harmonic {best:2d} ({best * F0:.0f} Hz), predicted {pred:2d}")
print("   overtone melody heard above the 110 Hz drone (harmonic numbers):", " ".join(str(r["measured"]) for r in res))
# E4 control: a cube against an ordinary room of the same volume (proportions 1 : 1.28 : 1.54, a common 'good' studio ratio)
c = 343.0
def modes(L, fmax=180):
    return sorted(round(c / 2 * math.sqrt(sum((k / l) ** 2 for k, l in zip(nn, L))), 0) for nn in itertools.product(range(0, 25), repeat=3) if nn != (0, 0, 0) and c / 2 * math.sqrt(sum((k / l) ** 2 for k, l in zip(nn, L))) <= fmax)
ctrl = {}
for side in (4.45, 8.90):
    V = side ** 3; r = (V / (1.28 * 1.54)) ** (1 / 3); other = (r, 1.28 * r, 1.54 * r)
    for name, L in ((f"cube {side} m", (side,) * 3), (f"ordinary room, same volume ({other[0]:.2f} x {other[1]:.2f} x {other[2]:.2f} m)", other)):
        M = [m for m in modes(L) if 85 <= m <= 180]; from collections import Counter; cnt = Counter(M)
        distinct = len(cnt); maxstack = max(cnt.values()); stacked3 = sum(1 for v in cnt.values() if v >= 3)
        ctrl[name] = dict(modes=len(M), distinct_frequencies=distinct, max_coincident=maxstack, frequencies_with_3plus=stacked3)
        print(f"   {name}: {len(M)} modes in 85-180 Hz at {distinct} distinct frequencies; up to {maxstack} coincide; {stacked3} frequencies carry 3 or more")
R = json.load(open(os.path.join(HERE, "e3_e4_results.json"))); R["E3_held_note"] = dict(f0=F0, vowels=res); R["E4_control"] = ctrl
json.dump(R, open(os.path.join(HERE, "e3_e4_results.json"), "w"), ensure_ascii=False, indent=1)
