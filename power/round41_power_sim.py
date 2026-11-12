#!/usr/bin/env python3
"""Round 41. Power-word simulator: every mouth, pitch, loudness and room; original wording against translations;
the words decoded into notes by ancient systems; an instrument built to play them.

LAYER P (physics, measurable). Each utterance variant is a phoneme string (engine parsers for Greek/Hebrew; hand IPA
  for Aramaic, Coptic, Latin, Egyptian, labelled). A source-filter model computes, for every vowel and voiced
  consonant, the harmonic spectrum: A_k = (1/k) * prod_i |H_i(k f0)|, formant resonators F1-F3 (bandwidths 60/90/120
  Hz), formants scaled by vocal-tract length (13-19 cm: child to large adult). Grid: 4 tract lengths x 8 pitches
  (80-300 Hz) x 7 rooms (from round 40). Metrics:
    voiced   duration-weighted share of voiced sound (continuity)
    overtone salience of the strongest harmonic in the F2 band (600-2600 Hz): the 'hidden melody' strength
    body     share of energy below 300 Hz (chest and bone-conducted vibration)
    coupling share of energy below 320 Hz that falls on a room mode (+-B/2)
  Physical index = mean z-score of the four (each at the variant's best mouth and room). Equal weights: a choice.
  Test: within each meaning (I am, holy, light, ...), is the ORIGINAL wording stronger than its TRANSLATION?
LAYER T (the ancient theories' own criteria; not physics): Nicomachus' seven planetary vowels (completeness),
  Sefer Yetzirah mother letters (aleph, mem, shin share), Pythagorean consonance of the overtone melody
  (share of steps whose harmonic-number ratio is 2:1, 3:2, 4:3, 5:4 or 6:5), letter-number value (isopsephy/gematria).
LAYER D (decoding text into notes):
  D1 Nicomachus (Harmonicum Enchiridion / Excerpta 6): seven vowels = seven planets = seven lyre strings
     (Saturn = hypate = omega ... Moon = nete = alpha). Pythagorean heptachord, mese a = 220 Hz (absolute pitch unknown).
  D2 Alypius' vocal notation, Lydian tonos (APPROXIMATE reconstruction): the alphabet A..Omega descends in triplets,
     each triplet = a base note and its two raised forms (+1, +2 dieses = quarter tones); bases c' b a g f e d c with
     iota = mese a. Verify against Poehlmann & West, Documents of Ancient Greek Music (2001) before relying on exact pitches.
  D3 SPECULATIVE: letter-number value read as Hz and folded into one octave (no ancient source; Hz is modern).
  Instrument: monochord/lyre string lengths for D1 and D2; 'vowel pipes' (stopped pipes at F1 and F2 of each vowel,
  after Kratzenstein's 1779 vowel resonators).
Usage: python3 power/round41_power_sim.py [--no-audio]   -> power/round41_results.json, power/audio/r41_*.mp3
"""
import itertools, json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
C = 343.0; out = {}
E.CONS.setdefault("ʒ", ("fric", True, 3000, 1800)); E.ALIASES.setdefault("ʤ", ["d", "ʒ"])

# ---------------------------------------------------------------- variants: (meaning, label, original?, kind, text, ipa, basis)
V = [
 ("I am", "Greek Koine ἐγώ εἰμι", 1, "greek", "ἐγώ εἰμι", None, "John 8:58, 18:6"),
 ("I am", "Greek Attic", 0, "attic", "ἐγώ εἰμι", None, "classical pronunciation"),
 ("I am", "Greek late Koine", 0, "late", "ἐγώ εἰμι", None, "iotacist pronunciation"),
 ("I am", "Hebrew ani hu", 1, "hebrew", "אֲנִי הוּא", None, "Isa 43:10, Deut 32:39 (LXX ego eimi)"),
 ("I am", "Hebrew ehyeh", 1, "hebrew", "אֶהְיֶה", None, "Exod 3:14"),
 ("I am", "Aramaic ana hu", 1, "ipa", "", "ʔ ə ˈn a | h ˈu", "Jesus' likely speech (reconstructed)"),
 ("I am", "Coptic anok pe", 0, "ipa", "", "a ˈn o k | p e", "Sahidic John 8:58"),
 ("I am", "Latin ego sum", 0, "ipa", "", "ˈɛ g o | s u m", "Vulgate"),
 ("I am", "English I am", 0, "ipa", "", "ˈa i | ɛ m", "modern translation"),
 ("Ablanathanalba", "Greek magical name", 1, "ipa", "", "a b l a n a θ ˈa n a l b a", "PGM (16 times)"),
 ("Ablanathanalba", "proposed Aramaic 'ab lana atta' (you are our father)", 1, "ipa", "", "ʔ a b | l ˈa n a | ʔ a t t ˈa", "proposed etymology, uncertain"),
 ("Talitha koum", "Aramaic", 1, "ipa", "", "tˤ a l ˈi θ a | ˈq u m", "Mark 5:41"),
 ("Talitha koum", "Greek translation", 0, "greek", "τὸ κοράσιον, ἔγειρε", None, "Mark 5:41 (Mark's own)"),
 ("Ephphatha", "Greek transliteration", 1, "ipa", "", "ʔ ɛ f ˈf a θ a", "Mark 7:34"),
 ("Ephphatha", "Aramaic etpatah", 1, "ipa", "", "ʔ ɛ θ p ə θ ˈa ħ", "reconstructed"),
 ("Ephphatha", "Greek translation", 0, "greek", "διανοίχθητι", None, "Mark 7:34 (Mark's own)"),
 ("Abba", "Aramaic", 1, "ipa", "", "ˈa b b a", "Mark 14:36"),
 ("Abba", "Greek translation", 0, "greek", "ὁ πατήρ", None, "Mark 14:36"),
 ("Amen", "Hebrew", 1, "hebrew", "אָמֵן", None, "Deut 27:15"),
 ("Amen", "Greek", 0, "greek", "ἀμήν", None, "John"),
 ("Holy x3", "Hebrew", 1, "hebrew", "קָדוֹשׁ קָדוֹשׁ קָדוֹשׁ", None, "Isa 6:3"),
 ("Holy x3", "Greek", 0, "greek", "ἅγιος ἅγιος ἅγιος", None, "Isa 6:3 LXX, Rev 4:8"),
 ("Let there be light", "Hebrew", 1, "hebrew", "יְהִי אוֹר", None, "Gen 1:3"),
 ("Let there be light", "Greek", 0, "greek", "γενηθήτω φῶς", None, "Gen 1:3 LXX"),
 ("Seven vowels", "Greek", 1, "ipa", "", "ˈa | ˈɛ | ˈe | ˈi | ˈo | ˈy | ˈɔ", "Demetrius 71; PGM XIII"),
 ("IAO", "Greek", 1, "ipa", "", "i ˈa ɔ", "PGM"),
 ("Heka", "Egyptian", 1, "ipa", "", "ħ ˈi k a ʔ", "reconstructed"),
]
def parse(kind, text, ipa):
    if kind == "greek": return E.parse_greek(text, "koine")
    if kind == "attic": return E.parse_greek(text, "attic")
    if kind == "late": return E.parse_greek(text, "koine-late")
    if kind == "hebrew": return E.parse_hebrew(text, "tiberian")
    return E.parse_phonemes(ipa)

VOICED_C = {"m": (250, 1100, 2300), "n": (250, 1600, 2600), "ŋ": (250, 2000, 2700), "l": (360, 1100, 2700),
            "r": (450, 1300, 1700), "w": (300, 700, 2300), "j": (280, 2200, 2900)}
VOICED_OBS = {"b", "d", "g", "v", "z", "ð", "ɣ", "ʕ", "ʒ"}
BW = (60, 90, 120)
def segs_of(words):
    s = []
    for w in words:
        for sy in w:
            for p in sy["ph"]:
                b = p.rstrip("ː"); long = p.endswith("ː")
                if b in E.VOWELS: s.append(("v", E.VOWELS[b], 1.6 if long else 1.0, b))
                elif b in VOICED_C: s.append(("c", VOICED_C[b], 0.5, b))
                elif b in VOICED_OBS: s.append(("o", (300, 1200, 2500), 0.25, b))
                else: s.append(("n", None, 0.3, b))
    return s

def spectrum(F, f0, scale):
    k = np.arange(1, int(5000 / f0) + 1); f = k * f0; A = 1.0 / k
    for Fi, Bi in zip(F, BW):
        Fi = Fi * scale; A = A / np.sqrt((1 - (f / Fi) ** 2) ** 2 + (f * Bi / Fi ** 2) ** 2)
    return f, A ** 2

def modes(dims, fmax=320.0):
    nmax = [int(2 * fmax * d / C) + 1 for d in dims]; r = []
    for n in itertools.product(*(range(m + 1) for m in nmax)):
        if n == (0, 0, 0): continue
        f = C / 2 * math.sqrt(sum((a / d) ** 2 for a, d in zip(n, dims)))
        if f <= fmax: r.append(f)
    return np.array(sorted(r))
R40 = json.load(open(os.path.join(HERE, "round40_results.json")))["spaces"]
ROOMS = {k: (modes(v["dims_m"]), 2.2 / v["rt_s"]) for k, v in R40.items()}
TRACT = {"13 cm (child)": 17.5 / 13, "15 cm (woman)": 17.5 / 15, "17.5 cm (man)": 1.0, "19 cm (large man)": 17.5 / 19}
PITCH = [80, 100, 110, 132, 155, 171, 220, 300]

def physical(s):
    dur = sum(x[2] for x in s); voiced = sum(x[2] for x in s if x[0] != "n") / dur
    best = None
    for (tn, sc), f0 in itertools.product(TRACT.items(), PITCH):
        sal, low, tot, lowE = [], 0.0, 0.0, []
        for kind, F, d, _ in s:
            if kind == "n": continue
            f, P = spectrum(F, f0, sc); P = P * d
            tot += P.sum(); low += P[f < 300].sum(); lowE.append((f[f < 320], P[f < 320]))
            if kind == "v":
                band = (f > 600) & (f < 2600)
                if band.any(): sal.append(P[band].max() / P[band].sum())
        coup = {}
        for rn, (m, B) in ROOMS.items():
            on = sum(Pi[np.abs(fi[:, None] - m[None, :]).min(1) < B / 2].sum() for fi, Pi in lowE if len(fi))
            coup[rn] = on / max(1e-12, sum(Pi.sum() for _, Pi in lowE))
        rn = max(coup, key=coup.get)
        rec = dict(tract=tn, f0=f0, salience=float(np.mean(sal)) if sal else 0.0, body=low / tot if tot else 0.0,
                   coupling=coup[rn], room=rn)
        score = rec["salience"] + rec["body"] + rec["coupling"]
        if best is None or score > best[0]: best = (score, rec)
    r = best[1]; r["voiced"] = voiced; return r

# ---------------------------------------------------------------- theory layer
PLANET = {"a": "Moon", "ɛ": "Mercury", "e": "Venus", "i": "Sun", "o": "Mars", "y": "Jupiter", "ɔ": "Saturn"}
GK_VAL = dict(zip("αβγδεϛζηθικλμνξοπρστυφχψω", [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,100,200,300,400,500,600,700,800]))
HE_VAL = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400]))
HE_VAL.update({"ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90})
GREEK_SPELL = {"Ablanathanalba": "αβλαναθαναλβα", "Seven vowels": "αεηιουω", "IAO": "ιαω", "Ephphatha": "εφφαθα",
               "Talitha koum": "ταλιθακουμ", "Abba": "αββα"}
import unicodedata
def bare(t): return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if not unicodedata.combining(c)).replace("ς", "σ")
CONS_RATIOS = [2, 1.5, 4 / 3, 1.25, 1.2]
def theory(meaning, label, kind, text, s, f0=132):
    vow = [x[3] for x in s if x[0] == "v"]
    planets = sorted({PLANET[v] for v in vow if v in PLANET})
    harm = [round(E.VOWELS[v][1] / f0) for v in vow]
    steps = [max(a, b) / min(a, b) for a, b in zip(harm, harm[1:]) if a != b]
    cons = sum(any(abs(r - c) < 0.02 for c in CONS_RATIOS) for r in steps) / len(steps) if steps else None
    if kind == "hebrew": sp = "".join(c for c in text if c in HE_VAL); val = sum(HE_VAL[c] for c in sp)
    elif kind in ("greek", "attic", "late"): sp = "".join(c for c in bare(text) if c in GK_VAL); val = sum(GK_VAL[c] for c in sp)
    elif meaning in GREEK_SPELL and "Greek" in label: sp = GREEK_SPELL[meaning]; val = sum(GK_VAL[c] for c in sp)
    else: sp, val = "", None
    mothers = sum(c in "אמםש" for c in sp) / len(sp) if kind == "hebrew" and sp else None
    return dict(planets=planets, planet_complete=len(planets) == 7, overtone_harmonics=harm,
                pythagorean_consonant_steps=None if cons is None else round(cons, 2),
                letter_value=val, value_mod7=None if val is None else val % 7, mothers_share=mothers, spelled=sp)

# ---------------------------------------------------------------- decoding layer
MESE = 220.0
NICO = {"ω": 3 / 4, "υ": 3 / 4 * 256 / 243, "ο": 8 / 9, "ι": 1.0, "η": 256 / 243, "ε": 32 / 27, "α": 4 / 3}  # x mese
BASES = [32 / 27, 9 / 8, 1.0, 8 / 9, 64 / 81, 3 / 4, 2 / 3, 16 / 27]  # c' b a g f e d c relative to a (Pythagorean)
ALPHA = "αβγδεζηθικλμνξοπρστυφχψω"
def alypius(ch):
    i = ALPHA.index(ch); t, pos = divmod(i, 3)
    return MESE * BASES[t] * 2 ** ((2 - pos) / 24)
def name(f):
    m = 69 + 12 * math.log2(f / 440); n = round(m); N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{N[n % 12]}{n // 12 - 1}{(m - n) * 100:+.0f}c"
def decode(sp):
    sp = "".join(c for c in sp if c in ALPHA)
    nico = [(c, round(MESE * NICO[c], 1)) for c in sp if c in NICO]
    aly = [(c, round(alypius(c), 1)) for c in sp]
    return dict(nicomachus=[dict(letter=c, Hz=f, note=name(f)) for c, f in nico],
                alypius_lydian=[dict(letter=c, Hz=f, note=name(f)) for c, f in aly],
                alypius_is_palindrome=[f for _, f in aly] == [f for _, f in aly][::-1])
def fold(v, lo=110.0):
    f = float(v)
    while f >= 2 * lo: f /= 2
    while f < lo: f *= 2
    return f

# ---------------------------------------------------------------- run
res = []
for meaning, label, orig, kind, text, ipa, basis in V:
    s = segs_of(parse(kind, text, ipa)); p = physical(s); t = theory(meaning, label, kind, text, s)
    res.append(dict(meaning=meaning, variant=label, original=bool(orig), basis=basis, phonemes=" ".join(x[3] for x in s), physical=p, theory=t))
keys = ["voiced", "salience", "body", "coupling"]
M = np.array([[r["physical"][k] for k in keys] for r in res]); Z = (M - M.mean(0)) / (M.std(0) + 1e-12)
for r, z in zip(res, Z): r["physical_index"] = round(float(z.mean()), 3); r["physical"] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r["physical"].items()}
out["variants"] = res
out["coupling_note"] = "coupling saturates (1.0 for every variant at its best mouth): above a room's Schroeder frequency modes overlap and any pitch couples; it drops out of the index (zero variance)."
out["schroeder_Hz"] = {k: round(2000 * math.sqrt(v["rt_s"] / (v["dims_m"][0] * v["dims_m"][1] * v["dims_m"][2])), 0) for k, v in R40.items()}
# best per meaning, and original vs translation
best = {}
for m in dict.fromkeys(r["meaning"] for r in res):
    grp = sorted([r for r in res if r["meaning"] == m], key=lambda r: -r["physical_index"])
    best[m] = [(r["variant"], r["physical_index"]) for r in grp]
out["ranking_per_meaning"] = best
pairs = []
for m in best:
    o = [r["physical_index"] for r in res if r["meaning"] == m and r["original"]]
    t = [r["physical_index"] for r in res if r["meaning"] == m and not r["original"]]
    if o and t: pairs.append((m, max(o), max(t)))
wins = sum(a > b for _, a, b in pairs); n = len(pairs)
p_sign = sum(math.comb(n, k) for k in range(wins, n + 1)) / 2 ** n
out["original_vs_translation"] = dict(pairs=[dict(meaning=m, original=a, translation=b) for m, a, b in pairs], original_wins=wins, n=n, sign_test_p=round(p_sign, 4))
lang = {}
for r in res:
    key = r["variant"].split()[0]; lang.setdefault(key, []).append(r["physical_index"])
out["by_language_mean_index"] = {k: round(float(np.mean(v)), 3) for k, v in sorted(lang.items(), key=lambda kv: -np.mean(kv[1]))}

# decoding and instrument
DEC = {"Ablanathanalba": "αβλαναθαναλβα", "I am (ἐγὼ εἰμι)": "εγωειμι", "Seven vowels": "αεηιουω", "IAO": "ιαω", "Abrasax": "αβρασαξ"}
out["decoded"] = {k: decode(v) for k, v in DEC.items()}
out["speculative_value_as_pitch"] = {k: dict(value=sum(GK_VAL[c] for c in v), folded_Hz=round(fold(sum(GK_VAL[c] for c in v)), 1),
                                     note=name(fold(sum(GK_VAL[c] for c in v)))) for k, v in DEC.items()}
MONO = 650.0  # mm, sounding length of the lowest string (hypate e = 165 Hz)
low = MESE * 3 / 4
out["instrument"] = dict(
    heptachord_lyre=[dict(string=s, vowel=v, planet=PLANET_G, Hz=round(MESE * NICO[v], 1), note=name(MESE * NICO[v]), length_mm=round(MONO * low / (MESE * NICO[v]), 1))
                     for s, v, PLANET_G in [("hypate", "ω", "Saturn"), ("parhypate", "υ", "Jupiter"), ("lichanos", "ο", "Mars"), ("mese", "ι", "Sun"),
                                            ("trite", "η", "Venus"), ("paranete", "ε", "Mercury"), ("nete", "α", "Moon")]],
    vowel_pipes=[dict(vowel=v, F1_Hz=E.VOWELS[v][0], F1_pipe_mm=round(1000 * C / (4 * E.VOWELS[v][0]), 0), F2_Hz=E.VOWELS[v][1], F2_pipe_mm=round(1000 * C / (4 * E.VOWELS[v][1]), 0))
                 for v in ["a", "ɛ", "e", "i", "o", "y", "ɔ"]],
    note="Stopped pipes, length = c/4f (end correction ignored). Kratzenstein (1779) built resonators that sounded the vowels.")

# audio: lyre renders of the decoded melodies, over a drone on the King's Chamber note (132 Hz)
rend = []
if "--no-audio" not in sys.argv:
    from scipy.io import wavfile
    os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
    for key, sys_ in [("Ablanathanalba", "alypius_lydian"), ("Ablanathanalba", "nicomachus"), ("I am (ἐγὼ εἰμι)", "alypius_lydian"),
                      ("I am (ἐγὼ εἰμι)", "nicomachus"), ("Seven vowels", "nicomachus")]:
        notes = out["decoded"][key][sys_]; step = 0.45; L = int(E.SR * (step * len(notes) + 3))
        y = np.zeros(L)
        for i, nt in enumerate(notes):
            tone = E.inst_string({"f0": [nt["Hz"]], "d": 1.5}, 0, bright=1.2, decay=2.0)
            E.place(y, tone, i * step)
        t = np.arange(L) / E.SR; y = E.norm(y) + 0.12 * np.sin(2 * np.pi * 132 * t) * np.minimum(1, t) * np.minimum(1, (L / E.SR - t))
        slug = key.split()[0].lower() if key != "I am (ἐγὼ εἰμι)" else "ego_eimi"
        wav = os.path.join(HERE, "audio", f"r41_{slug}_{sys_}.wav"); wavfile.write(wav, E.SR, (E.norm(y) * 32767).astype(np.int16))
        mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
        rend.append(os.path.relpath(mp3, ROOT))
out["renders"] = rend
json.dump(out, open(os.path.join(HERE, "round41_results.json"), "w"), ensure_ascii=False, indent=1)
for r in res: print(f'{r["meaning"]:<20}{r["variant"][:34]:<35}{r["physical_index"]:+.2f}', {k: r["physical"][k] for k in ("voiced", "salience", "body", "coupling", "tract", "f0", "room")})
print(out["schroeder_Hz"]); print(out["original_vs_translation"]); print(out["by_language_mean_index"])
for k, d in out["decoded"].items(): print(k, [n["note"] for n in d["alypius_lydian"]], d["alypius_is_palindrome"], [n["note"] for n in d["nicomachus"]])
print(out["speculative_value_as_pitch"]); print(rend)
