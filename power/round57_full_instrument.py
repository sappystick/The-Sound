#!/usr/bin/env python3
"""Round 57. Ezekiel's temple and Noah's ark added to the instrument; then the realistic, buildable instrument.

Part 1 (architecture, life size): calculated resonances of Ezekiel's temple (long cubit 0.52 m: 'a cubit and a
handbreadth', Ezek 40:5) and Noah's ark (common cubit 0.445 m), and the harmonic frame of all four structures.
Part 2 (a real instrument): the furniture is already instrument-sized. The ark becomes a box zither with seven gut
strings over its lid, the menorah seven stopped pipes on a wind chest (the incense altar as bellows box), the table a
monochord, the cherubim a horn, plus 72 bells and two silver trumpets. Strings, pipes and the ark's box modes are
calculated; the piece is synthesised with those values.
Usage: python3 power/round57_full_instrument.py
"""
import itertools, json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter, fftconvolve
from scipy.io import wavfile
SR = E.SR; C = 343.0; CU = 0.445; LCU = 0.52; rng = np.random.default_rng(57); out = {}
f_len = lambda cubits, cu=CU: C / (2 * cubits * cu)
def note(f):
    m = 69 + 12 * math.log2(f / 440); n = round(m); N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{N[n % 12]}{n // 12 - 1}{(m - n) * 100:+.0f}c"

# ---------------------------------------------------------------- Part 1: Ezekiel and Noah
V_noah = (300 * CU) * (50 * CU) * (30 * CU)
def helmholtz(A, L, V): return C / (2 * math.pi) * math.sqrt(A / (V * L))
win_sq = (1 * CU) ** 2; win_strip = (1 * CU) * (300 * CU)
out["noah"] = dict(text="Gen 6:14-16: 300 x 50 x 30 cubits; gopher wood; pitch inside and out; an opening finished within a cubit of the top; a door in the side; three decks",
    axial_Hz=[round(f_len(300), 3), round(f_len(50), 2), round(f_len(30), 2)], as_harmonics=[1, 6, 10],
    deck_height_cubits=10, deck_axial_Hz=round(f_len(10), 1), deck_note="the same 38.5 Hz as the tabernacle's Holy of Holies",
    volume_m3=round(V_noah), helmholtz_Hz=dict(one_cubit_square_opening=round(helmholtz(win_sq, 0.3 + 1.7 * math.sqrt(win_sq / math.pi), V_noah), 3),
                                               one_cubit_strip_along_the_length=round(helmholtz(win_strip, 1.0, V_noah), 2)),
    period_s=dict(square=round(1 / helmholtz(win_sq, 0.3 + 1.7 * math.sqrt(win_sq / math.pi), V_noah), 1), strip=round(1 / helmholtz(win_strip, 1.0, V_noah), 2)),
    mapping="the sealed hull with one opening is a Helmholtz resonator (the 'body' of the instrument at the largest scale); its breathing period is a sea swell")
ez = {"outer wall square (42:16-20)": 500, "temple depth and width (41:13-14)": 100, "gate (40:15)": 50, "gate width (40:21)": 25, "nave length (41:2)": 40,
      "nave width / inner room (41:2,4)": 20, "altar hearth (43:16)": 12, "altar upper ledge (43:17)": 14, "wall (41:5)": 6, "side chamber, ground level (41:5)": 4}
out["ezekiel"] = dict(cubit_m=LCU, parts={k: dict(cubits=v, Hz=round(f_len(v, LCU), 2), note=note(f_len(v, LCU)) if f_len(v, LCU) > 16 else "below hearing") for k, v in ez.items()},
    side_chambers=dict(text="41:5-7: 4 cubits wide at ground level, wider at each of three levels (5 and 6 inferred by commentators)",
                       Hz=[round(f_len(w, LCU), 2) for w in (4, 5, 6)], notes=[note(f_len(w, LCU)) for w in (4, 5, 6)],
                       chord="widths 4:5:6 resonate as frequencies 15:12:10, a just MINOR triad: E2, C2, A1 (A minor)"),
    altar_steps=dict(text="43:14-15: 2, 4, 4 cubits", ratios="2:4 octave, 4:4 unison"),
    river=dict(text="47:3-5: depth ankle, knee, waist, swimming, at 1,000-cubit steps", mapping="a four-step crescendo"),
    voice=dict(text="43:2: the Presence comes 'with a roar like the roar of mighty waters'", calc="round 42: 10-30 voices = rushing water"))
# the frame: every stated length (common-cubit structures) as a divisor of Noah's 300
lengths = [300, 50, 30, 10, 100, 50, 5, 20, 10, 2.5, 1.5, 2, 1, 5, 3, 1, 2, 28, 4, 30, 60, 20, 30, 40, 20, 18, 12, 10, 4, 3]
divides = [l for l in lengths if abs(300 / l - round(300 / l)) < 1e-9]
out["frame"] = dict(base="Noah's ark length, 300 cubits = 1.285 Hz", lengths=len(lengths), dividing_300=len(divides),
    not_dividing=sorted({l for l in lengths if l not in divides}),
    caveat="300 = 2^2 x 3 x 5^2 is highly composite: most small numbers divide it, so this is weak evidence of a common design")

# ---------------------------------------------------------------- Part 2: the buildable instrument
MESE = f_len(2.5)                         # the ark's long axis, 154.2 Hz
HEPTA = [("hypate", "ω", 3 / 4), ("parhypate", "υ", 3 / 4 * 256 / 243), ("lichanos", "ο", 8 / 9), ("mese", "ι", 1), ("trite", "η", 256 / 243), ("paranete", "ε", 32 / 27), ("nete", "α", 4 / 3)]
L_str = 1.0; rho_gut = 1300
strings = []
for name, v, r in HEPTA:
    f = MESE * r
    for d in (1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8):
        mu = rho_gut * math.pi * (d / 2000) ** 2; T = (2 * L_str * f) ** 2 * mu
        if T <= 110: break
    strings.append(dict(string=name, vowel=v, Hz=round(f, 1), note=note(f), length_m=L_str, gut_diameter_mm=d, tension_N=round(T, 1)))
pipes = []
for name, v, r in HEPTA:
    f = MESE * r; rad = 0.015; L = C / (4 * f) - 0.6 * rad
    pipes.append(dict(branch=name, Hz=round(f, 1), stopped_pipe_length_m=round(L, 3), bore_mm=30))
box = []
Lx, Ly, Lz = 2.5 * CU, 1.5 * CU, 1.5 * CU
for nx, ny, nz in itertools.product(range(7), range(4), range(4)):
    if (nx, ny, nz) == (0, 0, 0): continue
    f = C / 2 * math.sqrt((nx / Lx) ** 2 + (ny / Ly) ** 2 + (nz / Lz) ** 2)
    if f < 1000: box.append(round(f, 1))
box = sorted(box)
out["instrument"] = dict(
    ark_box_zither=dict(body_m=[round(Lx, 3), round(Ly, 3), round(Lz, 3)], material="acacia, gold-lined inside and out (stiff, reflective)", box_modes_below_1kHz=box[:24], modes_count=len(box),
                        strings=strings, note="seven gut strings over the lid (the mercy seat), plucked or bowed; the box rings at its modes"),
    menorah_pipes=dict(height_handbreadths=18, height_m="1.3-1.6 (Menachot 28b)", pipes=pipes, wind="the incense altar (1 x 1 x 2 cubits) as the bellows box / wind chest"),
    table_monochord=dict(length_m=round(2 * CU, 3), stops={"1/2 (octave)": round(MESE * 2, 1), "2/3 (fifth)": round(MESE * 1.5, 1), "3/4 (fourth)": round(MESE * 4 / 3, 1)}, open_Hz=round(MESE, 1)),
    cherubim_horn=dict(mouth_m=round(2.5 * CU, 2), lowest_efficient_Hz=round(C / (math.pi * 2.5 * CU))),
    bells=dict(count=72, Hz="2,000-5,000"), trumpets=dict(count=2, length_m=0.42, partials_Hz=[408, 612, 817, 1021]),
    ezekiel_chambers_drone=dict(Hz=[55.0, 66.0, 82.5], notes=["A1", "C2", "E2"], audible_octaves=[110.0, 132.0, 165.0]))

# ---------------------------------------------------------------- the sound
def box_ir(rt=0.35, n=int(0.6 * SR)):
    t = np.arange(n) / SR; y = np.zeros(n)
    for f in box: y += np.cos(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t * 6.91 / rt) * (1 / (1 + f / 400))
    return y / np.abs(y).max()
IR = box_ir()
def gut(f, d=2.4):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 25):
        if k * f > 7000: break
        y += np.sin(2 * np.pi * k * f * t * (1 + 0.0003 * k * k)) * abs(math.sin(k * math.pi * 0.17)) / k * np.exp(-t * (0.9 + 0.35 * k))
    return fftconvolve(y, IR)[:n + len(IR)]
def pipe(f, d=1.6):
    n = int(d * SR); t = np.arange(n) / SR; env = np.minimum(1, t / 0.06) * np.minimum(1, (d - t) / 0.12)
    y = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.3 for k in (1, 3, 5, 7)) + 0.02 * rng.standard_normal(n)
    return y * env
def bell(f, d=0.6):
    n = int(d * SR); t = np.arange(n) / SR; return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * (3 + r)) for r, a in ((1, 1), (2.76, .5), (5.4, .3)))
T = 78.0; mix = np.zeros(int(T * SR)); P = lambda y, t0, g: E.place(mix, g * E.norm(y), t0)
t0 = 0.5                                   # 1. the table: tuning by the canon (open string, octave, fifth, fourth)
for f in (MESE, MESE * 2, MESE * 1.5, MESE * 4 / 3): P(gut(f, 1.8), t0, 0.6); t0 += 1.3
t0 = 7.0                                   # 2. the ark zither: the seven strings, Moon to Saturn
for _, _, r in reversed(HEPTA): P(gut(MESE * r), t0, 0.6); t0 += 0.85
t0 = 14.0                                  # 3. menorah pipes enter, holding the mese; the strings play 'I am' (e-go-i-mi: Mercury, Mars, Sun, Sun)
P(pipe(MESE, 9.0), t0, 0.25); P(pipe(MESE * 3 / 4, 9.0), t0 + 0.5, 0.18); P(pipe(MESE * 4 / 3, 9.0), t0 + 1.0, 0.18)
for k, (r, L) in enumerate([(32 / 27, 1), (8 / 9, 1), (1, 2), (1, 1)] * 2):
    P(gut(MESE * r, 1.6 * L), t0 + 1.5 + k * 0.9, 0.55)
t0 = 25.0                                  # 4. Ezekiel's chambers: the A-minor drone (sounded an octave up so it can be heard), the river rising in 4 steps
n = int(20 * SR); tt = np.arange(n) / SR
drone = sum(np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) for f in (110.0, 132.0, 165.0))
steps = np.clip(np.floor(tt / 5) + 1, 1, 4) / 4
P(drone * steps * np.minimum(1, (20 - tt) / 2), t0, 0.35)
t0 = 46.0                                  # 5. 'a roar like mighty waters' (Ezek 43:2): many voices through the vowel tubes, breathing with Noah's ark (0.48 Hz strip opening shown as the swell)
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
n = int(18 * SR); tt = np.arange(n) / SR; crowd = np.zeros(n)
for i in range(60):
    f0 = rng.uniform(90, 240); v = rng.choice(list(R42)); src = np.exp(-((f0 * tt) % 1.0) * 9) - 0.11
    for F, bw in zip(R42[v]["machine"], (80, 100, 140)):
        bb, aa = E.resonator_coeffs(F, bw); crowd += lfilter(bb, aa, src) * rng.uniform(0.2, 1) / 60
swell = 0.6 + 0.4 * np.sin(2 * np.pi * out["noah"]["helmholtz_Hz"]["one_cubit_strip_along_the_length"] / 4 * tt)
P(crowd * swell * np.minimum(1, tt / 4) * np.minimum(1, (18 - tt) / 3), t0, 0.5)
for i in range(72): P(bell(rng.uniform(2200, 4200)), 50 + i * 0.14 + rng.uniform(0, 0.04), 0.06)   # 6. the 72 bells
for tk in (66.0, 69.5): P(E.inst_brass(408.0, 408.0, int(2.7 * SR), bright=1.4), tk, 0.45)     # 7. two silver trumpets close
E.MODAL_ROOMS["tabernacle_hoh"] = ((10 * CU,) * 3, 2.0)
y = E.reverb(E.norm(mix), "tabernacle_hoh")
wav = os.path.join(HERE, "audio", "r57_ark_instrument.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
out["render"] = dict(file=os.path.relpath(mp3, ROOT), sequence=["0.5 s table monochord: open, octave, fifth, fourth", "7 s ark zither: seven strings, Moon to Saturn",
    "14 s menorah pipes hold mese, fourth below and above; strings play 'I am' twice", "25 s Ezekiel's chambers: A-minor drone (octave up), rising in four river steps",
    "46 s 'a roar like mighty waters': 60 machine voices, swelling with Noah's ark", "50 s the 72 bells", "66 s two silver trumpets"])
json.dump(out, open(os.path.join(HERE, "round57_results.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("noah", "frame")}, ensure_ascii=False, indent=1)[:2500])
print(json.dumps(out["ezekiel"]["side_chambers"], ensure_ascii=False)); print({k: v["Hz"] for k, v in out["ezekiel"]["parts"].items()})
for s in strings: print(s)
for p in pipes: print(p)
print("box modes", box[:16]); print(out["render"]["file"])
