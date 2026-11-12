#!/usr/bin/env python3
"""Round 56. Thought experiment, taken as true: the tabernacle and temple instructions are one design for one instrument.
Every part is listed with (1) what the text says (dimensions, material), (2) the role it is given in the instrument
(MAPPING: speculative), and (3) its physics calculated from the stated dimensions (CALC).
Cubit 0.445 m (common); c = 343 m/s. Outputs: power/round56_results.json, power/round56_design.svg,
power/audio/r56_tabernacle_instrument.mp3.
Usage: python3 power/round56_tabernacle_instrument.py
"""
import json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
SR = E.SR; CU = 0.445; C = 343.0; rng = np.random.default_rng(56)
f_len = lambda cubits: C / (2 * cubits * CU)          # axial resonance of a length (open-open or closed-closed air)
COURT = f_len(100)                                  # 3.854 Hz: the court's long axis
MESE = f_len(2.5)                                   # the ark's long axis, 154.2 Hz
def harm(f): return round(f / COURT, 2)
parts = []
def add(name, ref, text, role, calc): parts.append(dict(part=name, ref=ref, text=text, mapping=role, calc=calc))
add("Court", "Exod 27:9-18", "100 x 50 cubits, linen hangings 5 cubits high", "the outer baffle and listening space",
    dict(axial_Hz=[round(f_len(100), 2), round(f_len(50), 2)], note="the base of the whole harmonic frame: every dimension that divides 100 cubits is a harmonic of 3.85 Hz"))
add("Tabernacle tent (Holy Place)", "Exod 26 (20 x 10 x 10 cubits, inferred from the boards)", "48 acacia boards 10 x 1.5 cubits, gold-overlaid, on 96 silver sockets",
    "the tuning chamber: the outer resonator", dict(axial_Hz=[round(f_len(20), 2), round(f_len(10), 2), round(f_len(10), 2)], harmonics_of_court=[harm(f_len(20)), harm(f_len(10))]))
add("Silver sockets", "Exod 26:19-25; 38:27", "96 + 4 sockets from 100 talents of silver", "the feet: isolation of the resonator from the ground (like a bridge's feet)", dict())
add("Coverings", "Exod 26:1-14", "4 layers: twined linen (10 curtains 28 x 4), goat hair (11 curtains 30 x 4), rams' skins, tachash skins", "the skin: damping and sealing layers that set how long the chamber rings", dict())
add("Veil", "Exod 26:31-33", "woven linen, blue, purple, scarlet, cherubim; 10 x 10 cubits", "the diaphragm between the two chambers: couples and filters them", dict())
add("Holy of Holies", "Exod 26 (10-cubit cube, inferred); 1 Kgs 6:20 (20-cubit cube)", "a cube", "the inner resonator",
    dict(tabernacle_axial_Hz=[round(f_len(10), 2)] * 3, solomon_axial_Hz=[round(f_len(20), 2)] * 3, note="one note on all three axes; modes stack (round 38)"))
add("Ark", "Exod 25:10-16", "acacia box 2.5 x 1.5 x 1.5 cubits, gold inside and out", "the soundbox at the centre",
    dict(axial_Hz=[round(f_len(2.5), 1), round(f_len(1.5), 1), round(f_len(1.5), 1)], long_axis_as_harmonic_of_room=dict(tabernacle=round(f_len(2.5) / f_len(10), 3), solomon=round(f_len(2.5) / f_len(20), 3)),
         note="2.5 cubits is 1/4 of the tabernacle's 10 and 1/8 of Solomon's 20: the ark's tone is 2 and 3 octaves above its room"))
add("Mercy seat and two cherubim", "Exod 25:17-22; Num 7:89", "gold slab 2.5 x 1.5; two cherubim of beaten gold, wings spread over it, faces toward each other; 'from between the two cherubim I will speak with you'",
    "the mouth: two wings forming a horn over the soundbox, the point the voice comes from", dict(horn_mouth_m=round(2.5 * CU, 2), lowest_efficient_Hz=round(C / (math.pi * 2.5 * CU), 0)))
add("Menorah", "Exod 25:31-40; 37:17-24", "beaten gold, one shaft, six branches (3 each side), seven lamps; cups, knobs, flowers",
    "the seven voices: a heptachord with the central shaft as the mese (Philo: the middle lamp is the Sun)",
    dict(strings_Hz={k: round(MESE * r, 1) for k, r in [("hypate", 3 / 4), ("parhypate", 3 / 4 * 256 / 243), ("lichanos", 8 / 9), ("mese", 1), ("trite", 256 / 243), ("paranete", 32 / 27), ("nete", 4 / 3)]},
         note="mese tuned to the ark's note, 154.2 Hz"))
add("Table of showbread", "Exod 25:23-30", "acacia 2 x 1 x 1.5 cubits, gold; 12 loaves", "the tuning standard (monochord): octave 2:1, fifth 3:2, fourth 4:3 in one object; 12 loaves = 12 notes (Josephus' 12-note nabla)",
    dict(ratios=["2:1", "4:3", "3:2"], twelve_notes_Hz=[round(MESE * (3 / 2) ** k / 2 ** math.floor(math.log2((3 / 2) ** k)), 1) for k in range(12)]))
add("Altar of incense", "Exod 30:1-10", "acacia 1 x 1 x 2 cubits, gold; incense morning and evening", "the breath: the air supply (smoke = moving air)", dict(axial_Hz=[round(f_len(1), 1), round(f_len(2), 1)]))
add("Altar of burnt offering", "Exod 27:1-8", "acacia 5 x 5 x 3 cubits, bronze-overlaid, 'hollow with boards', a bronze grating halfway down", "the drum: a large hollow bronze body",
    dict(axial_Hz=[round(f_len(5), 1), round(f_len(5), 1), round(f_len(3), 1)], singing_tube_check="a heated hollow with a grating is a Rijke tube, but a grating at mid-height sits where the fundamental is not driven: it would not sing (N)"))
add("Laver / bronze sea", "Exod 30:18; 1 Kgs 7:23-26", "Solomon's sea: 10 cubits across, 5 high, a handbreadth thick, on 12 bronze oxen", "the gong",
    dict(lowest_mode_Hz_rough=round(440 * (0.074 / 0.07) / (10 * CU) ** 2, 1), note="bell scaling f ~ t/D^2 from a 1 m, 7 cm bell at 440 Hz: an order-of-magnitude estimate only"))
add("Pillars Jachin and Boaz", "1 Kgs 7:15-22; Jer 52:21", "bronze, 18 cubits high, 12 in circumference, hollow, four fingers thick; capitals with lily-work and 200 pomegranates",
    "the bass: two hollow bronze tubes flanking the entrance",
    dict(air_column_open_Hz=round(f_len(18), 1), struck_free_free_Hz=round(22.4 / (2 * math.pi * (18 * CU) ** 2) * math.sqrt(110e9 / 8800) * (12 * CU / (2 * math.pi)) / math.sqrt(2), 1),
         standing_cantilever_Hz=round(3.52 / (2 * math.pi * (18 * CU) ** 2) * math.sqrt(110e9 / 8800) * (12 * CU / (2 * math.pi)) / math.sqrt(2), 1),
         ring_mode_Hz=round(math.sqrt(110e9 / 8800) / (2 * math.pi * 12 * CU / (2 * math.pi)), 0)))
add("Silver trumpets", "Num 10:1-10; Josephus, Ant. 3.291", "two, beaten silver; 'a little less than a cubit long, a narrow tube a little thicker than an aulos, ending in a bell'", "the signal voices",
    dict(length_m=0.42, closed_pipe_fundamental_Hz=round(C / (4 * 0.42), 0), playable_partials_Hz=[round(C / (4 * 0.42) * k, 0) for k in (2, 3, 4, 5, 6)]))
add("Robe of the ephod", "Exod 28:31-35; Bavli Zevachim 88b", "blue robe; golden bells and pomegranates alternating on the hem (72 bells, 72 clappers); 'its sound shall be heard when he goes into the holy place'",
    "the shaker: percussion sounded by the player's own movement", dict(bells=72, typical_small_bell_Hz="2,000-5,000"))
add("Breastpiece with Urim and Thummim", "Exod 28:15-30", "12 stones in 4 rows of 3, names of the 12 tribes; Urim and Thummim inside", "the display: 12 outputs, one for each of the 12 notes", dict())
out = dict(parts=parts, frame=dict(court_base_Hz=round(COURT, 3), mese_Hz=round(MESE, 1),
    note="Every length that divides 100 cubits (100, 50, 20, 10, 5, 2.5, 2, 1) is a harmonic of the court's 3.85 Hz: the ark is harmonic 40, the Holy of Holies 10, the Holy Place 5. Lengths of 1.5, 3, 28 and 30 cubits are not."))

# ---------------------------------------------------------------- schematic (SVG)
W, H = 1000, 680
def rect(x, y, w, h, fill, stroke, label, sub="", lx=None, ly=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2" rx="4"/>'
    s += f'<text x="{lx or x + 8}" y="{ly or y + 20}" font-size="15" font-family="sans-serif" fill="#1d1d1f" font-weight="600">{label}</text>'
    if sub: s += f'<text x="{lx or x + 8}" y="{(ly or y + 20) + 18}" font-size="12.5" font-family="sans-serif" fill="#444">{sub}</text>'
    return s
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#fbfaf7"/>',
       '<text x="20" y="32" font-size="20" font-family="sans-serif" font-weight="700" fill="#1d1d1f">The tabernacle read as one instrument (thought experiment)</text>',
       '<text x="20" y="54" font-size="13" font-family="sans-serif" fill="#555">Dimensions from Exodus 25-30 and 1 Kings 6-7 (cubit 0.445 m). Frequencies calculated; roles are speculative.</text>',
       rect(20, 75, 960, 470, "#f2efe6", "#b8ae90", "Court 100 x 50 cubits: the baffle", "base of the harmonic frame: 3.85 Hz; every length dividing 100 cubits is one of its harmonics"),
       rect(330, 150, 620, 300, "#e9e3d2", "#8c7f5a", "Holy Place 20 x 10 x 10: tuning chamber", "axes 19.3 / 38.5 / 38.5 Hz (harmonics 5, 10, 10)"),
       rect(700, 200, 230, 200, "#ddd3b8", "#6b5c33", "Holy of Holies 10-cube", "38.5 Hz on all 3 axes"),
       '<line x1="700" y1="200" x2="700" y2="400" stroke="#7a3b3b" stroke-width="5"/><text x="706" y="420" font-size="12.5" font-family="sans-serif" fill="#7a3b3b">veil (red line): the diaphragm</text>',
       rect(760, 300, 110, 60, "#d8b84a", "#7a5c00", "Ark", "box: 154.2 Hz", 768, 322),
       '<path d="M 760 300 Q 815 245 870 300" fill="none" stroke="#7a5c00" stroke-width="3"/><text x="712" y="376" font-size="12" font-family="sans-serif" fill="#7a5c00">arc = cherubim: the horn / mouth</text>',
       '<text x="712" y="392" font-size="12" font-family="sans-serif" fill="#7a5c00">"from between them I will speak"</text>']
mx, my = 420, 330
for i in range(7):
    x = mx + i * 22; h = 70 - abs(3 - i) * 12
    svg.append(f'<line x1="{x}" y1="{my}" x2="{x}" y2="{my - h}" stroke="#b08a1a" stroke-width="{4 if i == 3 else 2.5}"/><circle cx="{x}" cy="{my - h - 5}" r="4" fill="#e3b341"/>')
svg.append(f'<text x="400" y="355" font-size="13" font-family="sans-serif" font-weight="600" fill="#1d1d1f">Menorah: 7 voices</text><text x="400" y="372" font-size="12" font-family="sans-serif" fill="#444">heptachord, mese = 154.2 Hz (the ark note)</text>')
svg.append(rect(560, 230, 120, 48, "#efe2c4", "#8c7f5a", "Table 2 x 1 x 1.5", "octave, fifth, fourth", 566, 250))
svg.append(rect(560, 385, 90, 50, "#efe2c4", "#8c7f5a", "Incense", "the breath", 566, 405))
svg.append(rect(105, 300, 160, 70, "#c9a27a", "#6d4a26", "Altar 5x5x3", "the drum: 77 / 129 Hz", 111, 322))
svg.append(rect(105, 160, 160, 60, "#b9c3c7", "#4d5b60", "Laver / sea", "the gong (~24 Hz)", 111, 182))
for y, nm in ((470, "Jachin"), (505, "Boaz")):
    svg.append(f'<rect x="40" y="{y}" width="340" height="22" fill="#b8916a" stroke="#6d4a26"/><text x="48" y="{y + 16}" font-size="12.5" font-family="sans-serif">{nm}: hollow bronze bass tube, struck ~118 Hz</text>')
svg.append('<text x="20" y="575" font-size="13" font-family="sans-serif" fill="#1d1d1f"><tspan font-weight="600">Worn by the player:</tspan> robe with 72 golden bells (shaker); breastpiece with 12 stones (12 notes).</text><text x="20" y="595" font-size="13" font-family="sans-serif" fill="#1d1d1f"><tspan font-weight="600">Signals:</tspan> two silver trumpets (~0.42 m, partials 408-1225 Hz).</text>')
svg.append('<text x="20" y="615" font-size="13" font-family="sans-serif" fill="#1d1d1f"><tspan font-weight="600">What it makes:</tspan> a walk-in resonator. One voice, sung on the ark note, excites the harmonic series of every chamber</text>')
svg.append('<text x="20" y="635" font-size="13" font-family="sans-serif" fill="#1d1d1f">and seems to come from between the cherubim.</text>')
svg.append('<text x="20" y="655" font-size="11.5" font-family="sans-serif" fill="#777">The Sound, round 56. Speculative mapping; physics from stated dimensions. Not a historical reconstruction.</text></svg>')
open(os.path.join(HERE, "round56_design.svg"), "w").write("\n".join(svg))

# ---------------------------------------------------------------- the sound of the design
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, bw in zip(freqs, bws): bb, aa = E.resonator_coeffs(f, bw); y += lfilter(bb, aa, x)
    return y
def pluck(f0, d):
    n = int(d * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 30):
        if k * f0 > 8000: break
        y += np.sin(2 * np.pi * k * f0 * tt) * abs(math.sin(k * math.pi * 0.2)) / k * np.exp(-tt * (1.0 + 0.4 * k))
    return y
def bell(f, d=2.5, amp=1.0):
    n = int(d * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for r, a in ((1, 1), (2.76, .5), (5.4, .3), (8.9, .15)): y += a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * (1.5 + r * 0.5))
    return amp * y
def reed(f0, n): tt = np.arange(n) / SR; return np.exp(-((f0 * tt) % 1.0) * 9) - 0.11
TOTAL = 62.0; mix = np.zeros(int(TOTAL * SR))
for t0 in (0.5, 4.0):  # two silver trumpets, tekiah
    E.place(mix, 0.5 * E.norm(E.inst_brass(408.0, 408.0, int(2.7 * SR), bright=1.4)) + 0.0, t0)
for i in range(60):    # the priest walking: 72 golden bells
    E.place(mix, 0.05 * bell(rng.uniform(2200, 4200), 0.6), 7.5 + i * 0.12 + rng.uniform(0, 0.05))
for t0 in (15.0, 18.0):  # Jachin and Boaz struck
    E.place(mix, 0.5 * E.norm(bell(119.0, 6.0)), t0)
E.place(mix, 0.35 * E.norm(bell(23.6 * 4, 9.0)), 21.0)   # the sea (its lowest audible partials)
for i, r in enumerate([4 / 3, 32 / 27, 256 / 243, 1, 8 / 9, 3 / 4 * 256 / 243, 3 / 4]):   # the menorah: seven voices, Moon to Saturn
    E.place(mix, 0.35 * E.norm(pluck(MESE * r, 2.2)), 25.0 + i * 0.9)
seq = [("e", 1), ("ɛ", 1), ("e", 2), ("ɛ", 1), ("a", 1), ("ɛ", 1), ("e", 1), ("ɛ", 1), ("e", 2)]   # ehyeh asher ehyeh (vowel line)
t0 = 34.0
for v, L in seq:   # the voice from between the cherubim: a reed on the ark note through the vowel tubes
    n = int(0.55 * L * SR); s = resonate(reed(MESE, n), R42[v]["machine"]) * E.env_adsr(n, 0.05, 0.1); E.place(mix, 0.6 * E.norm(s), t0); t0 += 0.55 * L + 0.05
tt = np.arange(len(mix)) / SR; room = sum(np.sin(2 * np.pi * COURT * k * tt) / k for k in (20, 30, 40, 50, 60, 80))   # the building's harmonic series sounding under it all
mix += 0.06 * room * np.minimum(1, tt / 4) * np.minimum(1, (TOTAL - tt) / 4)
E.MODAL_ROOMS["tabernacle_hoh"] = ((10 * CU,) * 3, 2.0)
y = E.reverb(E.norm(mix), "tabernacle_hoh")
wav = os.path.join(HERE, "audio", "r56_tabernacle_instrument.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
out["render"] = dict(file=os.path.relpath(mp3, ROOT), sequence=["0 s two silver trumpets", "7.5 s the 72 bells (the priest walking)", "15 s Jachin and Boaz struck",
    "21 s the bronze sea", "25 s the menorah's seven voices, Moon to Saturn", "34 s the voice from between the cherubim: 'ehyeh asher ehyeh' (vowel line) on the ark note",
    "throughout: the building's harmonic series (harmonics 20-80 of 3.85 Hz)"])
json.dump(out, open(os.path.join(HERE, "round56_results.json"), "w"), ensure_ascii=False, indent=1)
for p in parts: print(p["part"], "|", json.dumps(p["calc"], ensure_ascii=False)[:220])
print(out["render"]["file"])
