#!/usr/bin/env python3
"""Round 59. (A) The remaining construction pieces added to the instrument. (B) The speaking planet organ: seven
planet-strings that say their vowels.

B. Two ancient planet tunings, each with the Sun 4th of 7:
   Nicomachus (round 41): the lyre heptachord, Saturn lowest (hypate) ... Moon highest (nete), Sun = mese.
   Pliny, Natural History 2.84 (Pythagoras): Earth-Moon a tone, Moon-Mercury 1/2, Mercury-Venus 1/2, Venus-Sun 1 1/2,
   Sun-Mars 1, Mars-Jupiter 1/2, Jupiter-Saturn 1/2 (Saturn-zodiac 1 1/2; 'seven tones').
   Both are anchored so the Sun = 154.2 Hz (the ark's note). Vowel of each planet: alpha Moon, epsilon Mercury,
   eta Venus, iota Sun, omicron Mars, upsilon Jupiter, omega Saturn.
   Each syllable sounds its vowel's planet string with a sustained (bowed / reed) source through that vowel's
   three-section tube (round 42), with 50 ms formant glides between syllables and consonant devices (bursts, hiss,
   nasal), held for its quantity. Intelligibility: an LPC formant recogniser classifies every vowel of the output
   among the seven; accuracy is compared with a control (the same strings without tubes) and with the round-44
   plucked lyre.
Usage: python3 power/round59_speaking_planets.py
"""
import json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
SR = E.SR; C = 343.0; CU = 0.445; LCU = 0.52; rng = np.random.default_rng(59); out = {}
f_len = lambda cubits, cu=CU: C / (2 * cubits * cu)
def note(f):
    m = 69 + 12 * math.log2(f / 440); n = round(m); N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{N[n % 12]}{n // 12 - 1}{(m - n) * 100:+.0f}c"

# ---------------------------------------------------------------- A. the remaining pieces
out["A_added"] = [
 dict(piece="Tabernacle bars (Exod 26:26-29)", text="5 bars per side; the middle bar runs end to end", calc="the long walls are 20 boards x 1.5 = 30 cubits; the middle bar rings at 131-187 Hz (round 58)", role="the frame's tie-rods / sound-posts"),
 dict(piece="Entrance screen on 5 pillars; veil on 4 pillars (Exod 26:32-37)", text="gold hooks; bronze and silver sockets", calc="5 and 4 supports: the two thresholds, outer and inner", role="the outer and inner baffles"),
 dict(piece="The court's 60 pillars (Exod 27:9-19)", text="hangings 100 cubits north and south (20 pillars each), 50 west (10), east 15 + 15 + a 20-cubit screen (3 + 3 + 4)",
      calc="pillar spacing 5 cubits: f = %.1f Hz; the court rings as a picket of 60 posts" % f_len(5), role="the outer picket"),
 dict(piece="Laver of bronze mirrors (Exod 38:8)", text="made from the mirrors of the women who served at the entrance", calc="polished bronze plates: thin bronze is a cymbal or bell material", role="the bright metal voice"),
 dict(piece="Anointing oil (Exod 30:23-24)", text="myrrh 500, cinnamon 250, calamus 250, cassia 500 shekels", calc="500 : 250 = 2 : 1, an octave; the recipe is octave-and-unison ratios 2:1:1:2", role="the tuning of the anointing (Reading)"),
 dict(piece="Incense (Exod 30:34)", text="stacte, onycha, galbanum and frankincense, 'equal part of each'", calc="1:1:1:1, unison", role="the unison of the breath (Reading)"),
 dict(piece="Ephod and shoulder stones (Exod 28:9-10)", text="two onyx stones, six names on each, in order of birth", calc="6 + 6 = 12", role="the 12 notes split into two hexachords"),
 dict(piece="Breastpiece (Exod 28:15-21)", text="a span square, doubled; 4 rows of 3 stones", calc="12 stones; 4 x 3", role="the 12-note display"),
 dict(piece="Gold plate, 'Holy to the LORD' (Exod 28:36-38)", text="on the front of the turban", calc="-", role="the name written on the instrument's player (cf. the War Scroll's inscribed trumpets)"),
 dict(piece="Solomon's ten stands and lavers (1 Kgs 7:27-39)", text="each stand 4 x 4 x 3 cubits on four 1.5-cubit wheels; laver 4 cubits, 40 baths",
      calc="stand axes %.0f / %.0f Hz; ten bronze basins of 4 cubits: a set of ten bowls" % (f_len(4), f_len(3)), role="ten tuned bowls (cf. the magrepha's ten holes, round 47)"),
 dict(piece="Solomon's doors (1 Kgs 6:31-34)", text="inner sanctuary: olive wood, lintel and posts 'a fifth' (hamishit); nave: posts 'a fourth' (revi'it)",
      calc="Hebrew 'fifth' and 'fourth' (five- and four-sided frames, or fractions of the wall); the musical fifth (3:2) and fourth (4:3) share the ordinal by coincidence of naming", role="Reading: the inner door 'a fifth', the outer 'a fourth'"),
 dict(piece="Solomon's windows (1 Kgs 6:4)", text="windows with recessed frames", calc="-", role="the sound holes"),
 dict(piece="Ezekiel's six gates (40:6-37)", text="each 50 x 25 cubits, with three chambers on each side, each chamber one rod (6 long cubits) square",
      calc="36 chambers of 6 long cubits: %.1f Hz each (%s); gates 50 x 25: %.1f / %.1f Hz" % (f_len(6, LCU), note(f_len(6, LCU)), f_len(50, LCU), f_len(25, LCU)), role="36 resonant cells on one note"),
 dict(piece="Ezekiel's 30 chambers on the pavement (40:17); the kitchens (46:21-24)", text="30 chambers; four courts 40 x 30", calc="40:30 = 4:3, a fourth", role="the outer cells"),
 dict(piece="The east gate shut (44:1-2)", text="'This gate shall be shut, it shall not be opened ... for the LORD has entered by it'", calc="a closed pipe sounds an octave below an open one of the same length", role="the stopped pipe"),
 dict(piece="Joshua's seven shofars (Josh 6)", text="7 priests, 7 shofars, 7 days; 13 circuits; a long blast, then the great shout", calc="round 40: the shout cannot topple walls (about 250 x short in pressure)", role="the horn section"),
 dict(piece="Gideon's trumpets and jars (Judg 7:16-20)", text="300 men, trumpets, empty jars with torches inside; they blew and smashed the jars", calc="smashing pottery = broadband impulses (round 40: a pop excites every room mode)", role="the percussion of breaking"),
 dict(piece="Miriam's drum (Exod 15:20)", text="a tof (frame drum), with the women dancing", calc="-", role="the frame drum"),
 dict(piece="David's 4,000 (1 Chr 23:5)", text="'4,000 praising the LORD with the instruments I made for praise'", calc="-", role="the full ensemble"),
 dict(piece="Herod's temple (Mishnah Middot 2:5; 4:6-7; Josephus, War 5.210)", text="house 100 x 100 x 100 cubits; 15 semicircular steps where the Levites sang; a golden vine over the entrance",
      calc="the 15 steps = the 15 Songs of Ascents (Ps 120-134)", role="the stage of 15 steps; the vine (John 15:1, 'I am the true vine', the 7th saying, round 54)")]

# ---------------------------------------------------------------- B. the speaking planet organ
SUN = 154.2
NICO = {"ω": 3 / 4, "υ": 3 / 4 * 256 / 243, "ο": 8 / 9, "ι": 1.0, "η": 256 / 243, "ε": 32 / 27, "α": 4 / 3}
PLINY_ST = {"α": 2 - 7, "ε": 3 - 7, "η": 4 - 7, "ι": 0, "ο": 9 - 7, "υ": 10 - 7, "ω": 11 - 7}   # semitones from the Sun
TUNE = {"Nicomachus": {g: SUN * r for g, r in NICO.items()}, "Pliny": {g: SUN * 2 ** (s / 12) for g, s in PLINY_ST.items()}}
PLANET = {"α": "Moon", "ε": "Mercury", "η": "Venus", "ι": "Sun", "ο": "Mars", "υ": "Jupiter", "ω": "Saturn"}
out["B_tunings"] = {k: {PLANET[g]: dict(vowel=g, Hz=round(f, 1), note=note(f)) for g, f in sorted(v.items(), key=lambda kv: kv[1])} for k, v in TUNE.items()}
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
FORM = {v: d["machine"] for v, d in R42.items()}
IPA2GK = {"a": "α", "ɛ": "ε", "e": "η", "i": "ι", "o": "ο", "y": "υ", "ɔ": "ω", "u": "ο"}
GK2IPA = {"α": "a", "ε": "ɛ", "η": "e", "ι": "i", "ο": "o", "υ": "y", "ω": "ɔ"}
def segments(text):
    segs = []
    for pw in E.parse_greek(text, "koine"):
        for s in pw:
            if not s.get("nuc"): continue
            v = s["nuc"][0].rstrip("ː"); long_ = s.get("long") or s["nuc"][0].endswith("ː")
            onset = [p for p in s["ph"] if p.rstrip("ː") not in E.VOWELS]
            nuc_i = next((i for i, p in enumerate(s["ph"]) if p.rstrip("ː") in E.VOWELS), 0)
            pre, post = [p for p in s["ph"][:nuc_i] if p.rstrip("ː") not in E.VOWELS], [p for p in s["ph"][nuc_i + 1:] if p.rstrip("ː") not in E.VOWELS]
            segs.append(dict(pre=pre, v=v, gk=IPA2GK.get(v, "α"), dur=0.42 if long_ else 0.26, post=post))
        segs.append(dict(gap=0.10))
    return segs
def resonate_track(src, F):  # time-varying 3-formant filter (blockwise coefficients)
    y = np.zeros_like(src); blk = 220; zi = [np.zeros(2) for _ in range(3)]
    for i in range(0, len(src), blk):
        for k, bw in enumerate((80, 100, 140)):
            b, a = E.resonator_coeffs(float(F[k][min(i, len(src) - 1)]), bw)
            seg, zi[k] = lfilter(b, a, src[i:i + blk], zi=zi[k] * 0 + zi[k]); y[i:i + blk] += seg
    return y
def bowed(f_track):
    ph = np.cumsum(f_track) / SR; saw = 2 * (ph % 1.0) - 1
    return saw * (1 + 0.03 * rng.standard_normal(len(saw)))
CONS_NOISE = {"s": 6000, "z": 5500, "θ": 5500, "ð": 4500, "f": 4500, "v": 4000, "x": 1800, "ɣ": 1600, "h": 1500, "ʃ": 3000}
NASAL = {"m": (250, 1100, 2300), "n": (250, 1600, 2600), "l": (360, 1100, 2700), "r": (450, 1300, 1700)}
def speak(text, tuning, tubes=True):
    segs = segments(text); f_tr, F_tr, gate, noise, log = [], [[], [], []], [], [], []
    prevF, prevf = FORM["a"], SUN
    def push(n, f, Fs, g, nz):
        f_tr.extend([f] * n); [F_tr[k].extend([Fs[k]] * n) for k in range(3)]; gate.extend([g] * n); noise.extend([nz] * n)
    for s in segs:
        if "gap" in s: push(int(s["gap"] * SR), prevf, prevF, 0.0, 0.0); continue
        f = tuning[s["gk"]]; Fv = FORM[s["v"]] if (tubes and s["v"] in FORM) else [700, 1300, 2500]
        for c in s["pre"] + s["post"][:0]:
            if c in NASAL: push(int(0.07 * SR), f, NASAL[c], 0.6, 0.0)
            elif c in CONS_NOISE: push(int(0.09 * SR), f, [CONS_NOISE[c]] * 3, 0.0, 1.0)
            else: push(int(0.05 * SR), f, prevF, 0.0, 0.0); push(int(0.015 * SR), f, [2500] * 3, 0.0, 1.5)
        nglide = int(0.05 * SR)
        for j in range(nglide):
            w = j / nglide; push(1, prevf * (1 - w) + f * w, [prevF[k] * (1 - w) + Fv[k] * w for k in range(3)], 1.0, 0.0)
        t_start = len(f_tr) / SR
        push(int(s["dur"] * SR), f, Fv, 1.0, 0.0); log.append(dict(t0=t_start, t1=len(f_tr) / SR, vowel=s["v"], gk=s["gk"]))
        for c in s["post"]:
            if c in NASAL: push(int(0.07 * SR), f, NASAL[c], 0.6, 0.0)
            elif c in CONS_NOISE: push(int(0.09 * SR), f, [CONS_NOISE[c]] * 3, 0.0, 1.0)
        prevF, prevf = Fv, f
    f_tr = np.array(f_tr); gate = np.convolve(np.array(gate), np.ones(200) / 200, mode="same"); noise = np.array(noise)
    src = bowed(f_tr) * gate + 0.4 * rng.standard_normal(len(f_tr)) * noise
    y = resonate_track(src, [np.array(F_tr[k]) for k in range(3)]) if tubes else lfilter(*E.butter(1, 3000 / (SR / 2)), src)
    return y / (np.abs(y).max() + 1e-9), log
# vowel recogniser: which of the seven tube shapes does the sound's spectral envelope match? (log-envelope correlation)
GRID = np.arange(150, 3500, 10.0)
def tube_template(v):
    w = 2 * np.pi * GRID / SR; z = np.exp(1j * w); H = np.zeros(len(GRID), complex)
    for F, bw in zip(FORM[v], (80, 100, 140)):
        bb, aa = E.resonator_coeffs(F, bw); H += np.polyval(bb[::-1], 1 / z) / np.polyval(aa[::-1], 1 / z)
    return np.log(np.abs(H) + 1e-9)
TEMPL = {v: tube_template(v) for v in FORM}
def envelope(x):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)), 1 << 15)); fr = np.fft.rfftfreq(1 << 15, 1 / SR)
    k = max(1, int(220 / (fr[1] - fr[0]))); env = np.convolve(X, np.ones(k) / k, mode="same")   # smooth across harmonics
    return np.log(np.interp(GRID, fr, env) + 1e-9)
def classify_env(x):
    e = envelope(x); e = (e - e.mean()) / (e.std() + 1e-9)
    return max(TEMPL, key=lambda v: float(np.dot(e, (TEMPL[v] - TEMPL[v].mean()) / (TEMPL[v].std() + 1e-9))))
def accuracy(y, log):
    hit = tot = 0
    for e in log:
        a, b = int((e["t0"] + 0.06) * SR), int((e["t1"] - 0.02) * SR)
        if b - a < int(0.06 * SR): continue
        want = e["vowel"] if e["vowel"] in TEMPL else "o"; tot += 1; hit += classify_env(y[a:b]) == want
    return round(hit / max(1, tot), 3), tot
ctrl = {}
for f0 in (115.0, 154.2, 205.0):
    h = 0
    for v in FORM:
        n = int(0.5 * SR); ph = np.cumsum(np.full(n, f0)) / SR; src = 2 * (ph % 1) - 1; yv = np.zeros(n)
        for F, bw in zip(FORM[v], (80, 100, 140)):
            bb, aa = E.resonator_coeffs(F, bw); yv += lfilter(bb, aa, src)
        h += classify_env(yv[int(0.1 * SR):int(0.4 * SR)]) == v
    ctrl[f"{f0:.0f} Hz"] = f"{h}/7"
out["B_recogniser_positive_control_steady_vowels"] = ctrl
TEXTS = {"ego_eimi": "ἐγώ εἰμι.", "john_1_1": "Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος.", "seven_vowels": "ἀ ἐ ἠ ἰ ὀ ὐ ὠ",
         "talitha_koum": "ταλιθα κουμ.", "lazarus": "Λάζαρε, δεῦρο ἔξω."}
res, rend = {}, []
for key, text in TEXTS.items():
    row = {}
    for tname, tun in TUNE.items():
        y, log = speak(text, tun, True); acc, n = accuracy(y, log); yc, logc = speak(text, tun, False); accc, _ = accuracy(yc, logc)
        row[tname] = dict(vowels=n, recognised_with_tubes=acc, control_without_tubes=accc, melody=[f"{PLANET[e['gk']]}" for e in log])
        if tname == "Pliny" or key == "ego_eimi":
            z = E.reverb(E.norm(y), "holy_of_holies"); wav = os.path.join(HERE, "audio", f"r59_{key}_{tname.lower()}.wav")
            wavfile.write(wav, SR, (E.norm(z) * 32767).astype(np.int16)); mp3 = wav[:-4] + ".mp3"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav); rend.append(os.path.relpath(mp3, ROOT))
    res[key] = row
out["B_speaking"] = res; out["renders"] = rend
allv = [(r[t]["recognised_with_tubes"], r[t]["control_without_tubes"], r[t]["vowels"]) for r in res.values() for t in r]
out["B_summary"] = dict(mean_recognised_with_tubes=round(float(np.average([a for a, _, n in allv], weights=[n for *_, n in allv])), 3),
                        mean_control=round(float(np.average([c for _, c, n in allv], weights=[n for *_, n in allv])), 3), chance=round(1 / 7, 3))
json.dump(out, open(os.path.join(HERE, "round59_results.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out["B_tunings"], ensure_ascii=False)); print(json.dumps(out["B_summary"]))
for k, r in res.items(): print(k, {t: (v["recognised_with_tubes"], v["control_without_tubes"], v["vowels"]) for t, v in r.items()}, r["Pliny"]["melody"][:12])
print(rend)
