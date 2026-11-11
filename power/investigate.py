#!/usr/bin/env python3
"""The 'words of power' investigation: every hypothesis is taken seriously, then put to a test the data can answer.

T1  SOUND OVER SENSE. Origen (Contra Celsum 1.25) and Iamblichus (De Mysteriis 7.4-5) say a sacred formula keeps its
    power only in its original sound. Do the Gospels keep Jesus' words untranslated precisely at moments of power, and do
    later Gospels translate them away?
T2  THE VOICE IN JOHN. Rate of 'voice' (phone) per 1,000 words in John vs the Synoptics, and the passages where voice
    acts: the dead hear it, it is heard as thunder, 'I am' makes armed men fall.
T3  THE SEVEN VOWELS. Demetrius (On Style 71): Egyptian priests hymned the gods by sounding the seven vowels in order.
    Sung on one note, which overtone does each vowel brighten? (a hidden second melody: the principle of overtone singing)
T4  BREATH. Recited prayer can slow breathing to about 6 breaths a minute, the rate at which heart rhythm and blood
    pressure oscillations synchronise (Bernardi et al., BMJ 2001: rosary and mantra). Breaths per minute implied by the
    phrasing of sacred texts at chant pace.
T5  THE HUM. Humming raises nasal nitric oxide about fifteen-fold (Weitzberg & Lundberg 2002). Nasal and voiced-sound
    share of sacred formulas against ordinary text.
T6  THE HARMONIC WORLD. Plato, Timaeus 35b-36b: the world soul built from the numbers 1 2 3 4 8 9 27 and filled with
    9:8 tones: the scale it implies.
T7  MATTER AND GRAVITY. What force can sound exert? Acoustic radiation pressure and energy, from a voice to an ultrasonic
    levitator, against the weight of objects.
Usage: python3 investigate.py <sblgnt dir> <morphhb wlc dir> <egypt dir>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, WLC, EG = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); out = {}
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def book(code):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], w=nrm(p[4]), lem=nrm(p[6])))
    return V
B = {c: book(c) for c in ("Mt", "Mk", "Lk", "Jn")}
txt = lambda code, ref: " ".join(t["raw"] for t in B[code].get(ref, []))
# ---------------------------------------------------------------- T1
print("T1. SOUND OVER SENSE: words of Jesus kept in Aramaic, and what later Gospels did with them")
ARAM = {"ταλιθα": "talitha koum", "εφφαθα": "ephphatha", "αββα": "abba", "ελωι": "eloi eloi lema sabachthani", "ηλι": "eli eli lema sabachthani", "κορβαν": "korban", "βοανηργεσ": "boanerges", "ραββουνι": "rabbouni"}
rows = []
seen = set()
for code in ("Mk", "Mt", "Lk", "Jn"):
    for ref, toks in B[code].items():
        for i, t in enumerate(toks):
            if t["w"] not in ARAM or (code, ref, ARAM[t["w"]]) in seen: continue
            if t["w"] == "ηλι" and not (i + 1 < len(toks) and toks[i + 1]["w"] == "ηλι"): continue      # Eli the name (Luke 3:23)
            seen.add((code, ref, ARAM[t["w"]])); rows.append((code, f"{ref[0]}:{ref[1]}", ARAM[t["w"]], txt(code, ref)[:110]))
for r in rows: print("  ", *r[:3], "|", r[3])
PAR = [("talitha koum: raising a dead girl", (("Mk", (5, 41)), ("Mt", (9, 25)), ("Lk", (8, 54)))), ("ephphatha: opening deaf ears", (("Mk", (7, 34)),)),
       ("abba: the prayer in Gethsemane", (("Mk", (14, 36)), ("Mt", (26, 39)), ("Lk", (22, 42)))), ("eloi: the cry from the cross", (("Mk", (15, 34)), ("Mt", (27, 46)), ("Lk", (23, 46))))]
print("   the same moments in the later Gospels:")
for lab, refs in PAR:
    for code, ref in refs: print(f"      {lab:38s} {code} {ref[0]}:{ref[1]:<3d} {txt(code, ref)[:120]}")
out["T1"] = dict(found=rows)
# ---------------------------------------------------------------- T2
print("\nT2. THE VOICE IN JOHN")
for code in ("Jn", "Mk", "Mt", "Lk"):
    n = sum(len(v) for v in B[code].values()); f = sum(t["lem"] == "φωνη" for v in B[code].values() for t in v); print(f"   {code}: 'voice' {f} times, {1000 * f / n:.2f} per 1,000 words")
    out.setdefault("T2", {})[code] = dict(count=f, per_k=round(1000 * f / n, 2))
for ref in [(5, 25), (5, 28), (10, 3), (11, 43), (12, 28), (12, 29), (18, 5), (18, 6)]: print(f"   John {ref[0]}:{ref[1]}  {txt('Jn', ref)}")
# ---------------------------------------------------------------- T3
print("\nT3. THE SEVEN VOWELS SUNG ON ONE NOTE: the overtone each vowel brightens")
VOW = [("α", "a"), ("ε", "e"), ("η", "ɛ"), ("ι", "i"), ("ο", "o"), ("υ", "y"), ("ω", "ɔ")]   # classical values: eta open e, upsilon front rounded, omega open o
res = []
for f0 in (110.0, 130.8):
    seq = []
    for g, ipa in VOW:
        F1, F2, F3 = E.VOWELS[ipa]; h1, h2 = round(F1 / f0), round(F2 / f0); seq.append((g, ipa, F1, F2, h1, h2))
    res.append((f0, seq)); print(f"   on {f0:.1f} Hz:  " + "  ".join(f"{g} ({ipa}) F2 {F2} Hz = harmonic {h2}" for g, ipa, F1, F2, h1, h2 in seq))
out["T3"] = [dict(f0=f, seq=[dict(letter=g, ipa=i, F1=a, F2=b, h1=c, h2=d) for g, i, a, b, c, d in s]) for f, s in res]
# ---------------------------------------------------------------- T4
print("\nT4. BREATH: breaths per minute implied by the phrasing at chant pace (one breath per phrase)")
def greek_syll(text): return sum(len(E.parse_greek(unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", w)), "koine")[0]) for w in text.split() if re.sub(r"[^\wἀ-῿]", "", w))
def latin_syll(text): return sum(max(1, len(re.findall(r"[aeiouy]+", w.lower().replace("qu", "q")))) for w in text.split())
def heb_syll(ref_list):
    x = {}; n = 0
    for b, c, v in ref_list:
        if b not in x: x[b] = open(os.path.join(WLC, f"{b}.xml"), encoding="utf-8").read()
        m = re.search(rf'<verse osisID="{b}\.{c}\.{v}">(.*?)</verse>', x[b], re.S); words = re.findall(r">([^<>]+)</w>", m.group(1))
        n += sum(max(1, len(re.findall(r"[ְ-ׇּ]", w.replace("ְ", "")))) for w in words)   # vowel points ~ syllables
    return n
TEXTS = {"Ave Maria (Latin), each half recited on one breath": [latin_syll("Ave Maria gratia plena Dominus tecum benedicta tu in mulieribus et benedictus fructus ventris tui Iesus"), latin_syll("Sancta Maria Mater Dei ora pro nobis peccatoribus nunc et in hora mortis nostrae Amen")],
         "Om mani padme hum, repeated": [6, 6],
         "Lord's Prayer, Greek (Matthew 6:9-13), per clause": [greek_syll(c) for c in re.split(r"[,.;·]", txt("Mt", (6, 9)) + " " + txt("Mt", (6, 10)) + " " + txt("Mt", (6, 11)) + " " + txt("Mt", (6, 12)) + " " + txt("Mt", (6, 13))) if c.strip()],
         "John 1:1-5, Greek, per clause": [greek_syll(c) for c in re.split(r"[,.;·]", " ".join(txt("Jn", (1, v)) for v in range(1, 6))) if c.strip()],
         "Psalm 23, Hebrew, per half-verse (estimated from vowel points)": [heb_syll([("Ps", 23, v)]) / 2 for v in range(1, 7) for _ in (0, 1)],
         "Shema, Hebrew (Deuteronomy 6:4), per half": [heb_syll([("Deut", 6, 4)]) / 2] * 2}
for lab, groups in TEXTS.items():
    g = float(np.mean(groups)); line = f"   {lab:62s} {g:5.1f} syllables per breath"
    vals = {}
    for rate in (2.0, 3.0):
        bpm = 60 / (g / rate + 1.5); vals[rate] = round(bpm, 1); line += f" | at {rate:.0f} syll/s: {bpm:4.1f} breaths/min"
    print(line); out.setdefault("T4", {})[lab] = dict(syll=round(g, 1), bpm_2=vals[2.0], bpm_3=vals[3.0])
# ---------------------------------------------------------------- T5
print("\nT5. THE HUM: share of sounds that are nasal (m, n, ng) and voiced-continuous (vowels, nasals, l, r, w, y)")
NAS = {"m", "n", "ŋ"}; SON = NAS | {"l", "r", "w", "j", "ʎ"}
def shares(words, era="koine"):
    ph = [p.replace("ː", "") for w in words for s in E.parse_greek(w, era)[0] for p in s["ph"]]
    vow = sum(p[0] in "aeiouyɛɔə" for p in ph); return len(ph), sum(p in NAS for p in ph) / len(ph), (vow + sum(p in SON for p in ph)) / len(ph)
FORM = {"ἀμήν": "amen", "ὡσαννά": "hosanna", "ἀλληλουϊά": "alleluia", "κύριε ἐλέησον": "kyrie eleison", "μαρανα θα": "maranatha", "ἐγώ εἰμι": "ego eimi (I am)", "Ἰαώ": "IAO (magical papyri)",
        "ἀβλαναθαναλβα": "ablanathanalba (magical palindrome)", "Σαβαώθ": "Sabaoth", "Ἀδωναί": "Adonai", "ταλιθα κουμ": "talitha koum", "ἐφφαθα": "ephphatha"}
allf = []
for g, lab in FORM.items():
    n, na, so = shares(g.split()); allf += g.split(); print(f"   {lab:36s} nasal {na:4.0%}  voiced-continuous {so:4.0%}")
narr = [t["raw"] for ref in list(B["Jn"])[:200] for t in B["Jn"][ref]]; n0, na0, so0 = shares([re.sub(r"[^\wἀ-῿]", "", w) for w in narr if re.sub(r"[^\wἀ-῿]", "", w)])
n1, na1, so1 = shares(allf); print(f"   ALL FORMULAS TOGETHER                nasal {na1:4.0%}  voiced-continuous {so1:4.0%}   |  John 1-6 ordinary text: nasal {na0:4.0%}, voiced-continuous {so0:4.0%}")
out["T5"] = dict(formulas=dict(nasal=na1, voiced=so1), john=dict(nasal=na0, voiced=so0))
# ---------------------------------------------------------------- T6
print("\nT6. THE HARMONIC WORLD (Timaeus 35b-36b)")
nums = [1, 2, 3, 4, 8, 9, 27]; tones = sorted({1.0} | {2 ** a * 3 ** b for a in range(0, 5) for b in range(0, 4) if 2 ** a * 3 ** b <= 27})
from fractions import Fraction
# fill each octave with the Pythagorean diatonic: tones of 9/8 and the leimma 256/243
scale = [Fraction(1)]
for step in [Fraction(9, 8), Fraction(9, 8), Fraction(256, 243), Fraction(9, 8), Fraction(9, 8), Fraction(9, 8), Fraction(256, 243)] * 5:
    if scale[-1] * step > 27: break
    scale.append(scale[-1] * step)
print(f"   the numbers {nums} span {math.log2(27):.2f} octaves; filled with 9:8 tones and 256:243 'leftovers' they give {len(scale)} notes")
print("   first octave:", " ".join(str(f) for f in scale[:8]), "| on 110 Hz:", " ".join(f"{110 * float(f):.0f}" for f in scale[:8]))
out["T6"] = dict(ratios=[str(f) for f in scale], hz=[round(110 * float(f), 1) for f in scale])
# ---------------------------------------------------------------- T7
print("\nT7. MATTER AND GRAVITY: the push sound can give")
rho, c = 1.2, 343.0
print(f"   {'source':44s} {'level':>7s} {'intensity':>12s} {'radiation pressure':>20s} {'weight it could hold up on 1 m²':>32s}")
T7 = []
for lab, db in [("speaking voice at 1 m", 60), ("loud singing at 1 m", 100), ("trumpet bell / shout at close range", 120), ("rock concert stack, close", 135), ("jet engine at 30 m", 150), ("ultrasonic levitator node", 160)]:
    p = 20e-6 * 10 ** (db / 20); I = p ** 2 / (rho * c); P = I / c; grams = P / 9.81 * 1000; T7.append(dict(source=lab, db=db, I=I, P=P, grams_per_m2=grams))
    print(f"   {lab:44s} {db:5d} dB {I:10.2e} W/m² {P:16.2e} Pa {grams:24.4f} g")
print("   a standing wave multiplies the force on small objects at its nodes (acoustic levitation): it holds beads and droplets of a few millimetres at about 160 dB ultrasound.")
voice_W = 0.01; E_hour = voice_W * 3600; print(f"   a singer radiates about {voice_W} W of sound; in an hour that is {E_hour:.0f} J, the energy to lift a 1 kg stone {E_hour / 9.81:.1f} m, if all of it could be captured; its mass-equivalent (E/c²) is {E_hour / 9e16:.1e} kg.")
out["T7"] = T7
# ---------------------------------------------------------------- texts: Egyptian words of power and 'I am'
bod = open(os.path.join(EG, "pg69566.txt"), encoding="utf-8").read(); out["BOD"] = dict(words_of_power=len(re.findall(r"[Ww]ords of [Pp]ower", bod)), i_am_the=len(re.findall(r"\bI am the\b", bod)))
print(f"\nBook of the Dead (Renouf translation): 'words of power' {out['BOD']['words_of_power']} times; 'I am the' {out['BOD']['i_am_the']} times")
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), ensure_ascii=False, indent=1, default=float)
