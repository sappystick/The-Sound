#!/usr/bin/env python3
"""Round 45. Axiom: John is the score of a lost instrument (seven strings tuned by ratio, mese = 'I am', vowel tubes for
breath, the body as temple). Every syllable of the Gospel is mapped onto it; the book's own sevens are placed on the
strings; and the axiom's predictions are tested so that it can fail.

Mapping (rounds 41-44): each syllable sounds the Nicomachus string of its Koine vowel (alpha Moon/nete ... omega
Saturn/hypate; Koine iotacism: ei -> i), held for its quantity; verse-final syllables are cadences.
P1  The mese (Sun, iota) is the governing string: is it the most-sounded string of John, and more so than in the
    Synoptics (same mapping)?
P2  The book's four movements (blind cuts 1:16, 13:33, 18:1; AUDIT C24) are 'modes': do their cadence-string
    distributions differ more than random cuts give?
P3  The middle sign and the middle 'I am' saying sit at the book's syllable centre (the mese of the book).
P4  The 'I am' sayings cadence on the mese more than other verses do.
Usage: python3 power/round45_axiom.py [--no-audio]
"""
import glob, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
rng = np.random.default_rng(45); SR = E.SR; out = {}
R41 = json.load(open(os.path.join(HERE, "round41_results.json")))["instrument"]["heptachord_lyre"]
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
IPA2GK = {"a": "α", "ɛ": "ε", "e": "η", "i": "ι", "o": "ο", "y": "υ", "ɔ": "ω", "u": "ο"}
STR = {s["vowel"]: s for s in R41}; ORDER = [s["vowel"] for s in R41]  # hypate (omega) ... nete (alpha)
def verses(code):
    V = {}
    for l in open(glob.glob(os.path.join(ROOT, f"sources/texts/sblgnt/*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(p[3])
    return V
CACHE = {}
def strings_of(word):
    if word not in CACHE:
        CACHE[word] = [(IPA2GK.get(s["nuc"][0].rstrip("ː"), "α"), 2 if (s.get("long") or s["nuc"][0].endswith("ː")) else 1)
                       for w in E.parse_greek(word, "koine") for s in w if s.get("nuc")]
    return CACHE[word]
def book(code):
    V = verses(code); rows = []
    for ref, ws in V.items():
        seq = [x for w in ws for x in strings_of(w)]
        if seq: rows.append(dict(ref=ref, seq=seq))
    return rows
B = {c: book(c) for c in ("Jn", "Mt", "Mk", "Lk")}
def share(rows):
    c = {g: 0.0 for g in ORDER}
    for r in rows:
        for g, d in r["seq"]: c[g] += d
    t = sum(c.values()); return {STR[g]["string"]: round(c[g] / t, 4) for g in ORDER}
out["P1_string_shares"] = {c: share(rows) for c, rows in B.items()}
jn = out["P1_string_shares"]["Jn"]; out["P1_verdict"] = dict(most_sounded_in_John=max(jn, key=jn.get),
    mese_share={c: v["mese"] for c, v in out["P1_string_shares"].items()})

# P2: modes of the four movements
J = B["Jn"]; refs = [r["ref"] for r in J]; cad = np.array([ORDER.index(r["seq"][-1][0]) for r in J])
cuts = [refs.index((1, 16)), refs.index((13, 33)), refs.index((18, 1))]
def chi(cutpos):
    b = [0] + list(cutpos) + [len(J)]; tab = np.array([np.bincount(cad[b[i]:b[i + 1]], minlength=7) for i in range(4)], float)
    e = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum(); return float(((tab - e) ** 2 / np.maximum(e, 1e-9)).sum()), tab
obs, tab = chi(cuts); nulls = []
for _ in range(5000):
    c = np.sort(rng.choice(np.arange(15, len(J) - 15), 3, replace=False)); nulls.append(chi(c)[0])
movements = ["1. Prologue (1:1-15)", "2. Signs and discourses (1:16-13:32)", "3. Farewell (13:33-17:26)", "4. Passion and resurrection (18:1-21:25)"]
out["P2_modes"] = dict(chi2=round(obs, 2), p_random_cuts=round(float((np.array(nulls) >= obs).mean()), 4),
    cadence_counts={m: {STR[ORDER[i]]["string"]: int(tab[k, i]) for i in range(7)} for k, m in enumerate(movements)},
    final_of_each_movement={m: STR[ORDER[int(np.argmax(tab[k]))]]["string"] for k, m in enumerate(movements)})

# P3: positions by syllables
cum = np.cumsum([0] + [sum(d for _, d in r["seq"]) for r in J]); TOT = cum[-1]
def frac(ref): i = refs.index(ref); return round(float((cum[i] + cum[i + 1]) / 2 / TOT), 3)
SIGNS = [("water to wine", (2, 9)), ("official's son", (4, 50)), ("the paralysed man", (5, 8)), ("five thousand fed", (6, 11)),
         ("walking on the sea", (6, 19)), ("the man born blind", (9, 7)), ("Lazarus", (11, 43))]
IAM = [("bread of life", (6, 35)), ("light of the world", (8, 12)), ("the door", (10, 7)), ("the good shepherd", (10, 11)),
       ("resurrection and life", (11, 25)), ("way, truth, life", (14, 6)), ("the true vine", (15, 1))]
out["P3_positions"] = dict(signs=[(n, f"{a}:{b}", frac((a, b)), STR[ORDER[k]]["string"]) for k, (n, (a, b)) in enumerate(SIGNS)],
                           i_am=[(n, f"{a}:{b}", frac((a, b)), STR[ORDER[k]]["string"]) for k, (n, (a, b)) in enumerate(IAM)],
                           book_centre_verse=f"{refs[int(np.searchsorted(cum, TOT / 2)) - 1][0]}:{refs[int(np.searchsorted(cum, TOT / 2)) - 1][1]}")
mid_iam = frac((10, 11)); mid_sign = frac((6, 11))
# chance that a 4th-of-7 item lands within |d| of 0.5: order statistics of 7 uniform positions (simulation)
sims = np.sort(rng.random((200000, 7)), axis=1)[:, 3]
out["P3_test"] = dict(middle_i_am_position=mid_iam, middle_sign_position=mid_sign,
    p_middle_i_am_this_close=round(float((np.abs(sims - 0.5) <= abs(mid_iam - 0.5)).mean()), 3),
    p_middle_sign_this_close=round(float((np.abs(sims - 0.5) <= abs(mid_sign - 0.5)).mean()), 3),
    note="null: the 4th of 7 points placed at random along the book")

# P4: 'I am' verses cadence on the mese?
JV = verses("Jn")
def bare(t): t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if not unicodedata.combining(c))
iam_refs = sorted({ref for ref, ws in JV.items() for i in range(len(ws) - 1) if bare(ws[i]).strip(".,;·") == "ἐγω".replace("ἐ", "ε") and bare(ws[i + 1]).startswith("ειμι")})
mese = ORDER.index("ι"); is_iam = np.array([r["ref"] in iam_refs for r in J])
a = int((cad[is_iam] == mese).sum()); n1 = int(is_iam.sum()); base = float((cad[~is_iam] == mese).mean())
p4 = sum(math.comb(n1, k) * base ** k * (1 - base) ** (n1 - k) for k in range(a, n1 + 1))
out["P4_i_am_cadence_on_mese"] = dict(i_am_verses=n1, cadence_on_mese=a, other_verses_rate=round(base, 3), p_binomial=round(p4, 4))

# the framework table (axiom -> where John has it) - textual facts, each with its verse
out["framework"] = [
 ("tuning by ratio (logos)", "1:1-3 the Logos through whom all things came to be; prologue syllable centre at 1:12 (C1)"),
 ("seven strings", "seven signs (2:1-11:44) and seven 'I am' + predicate sayings (6:35-15:1)"),
 ("the mese, the governing string", "'I am' (ego eimi -> i-mi on the Sun string); the middle place always holds Jesus (1:26, 19:18, 20:19, 20:26)"),
 ("the tube and breath (aulos, pneuma)", "3:8 the wind blows and you hear its voice; 19:30 he handed over the breath; 20:22 he breathed on them"),
 ("the temple (the resonant body)", "2:19-21 'destroy this temple ... he spoke of the temple of his body'"),
 ("the sound (phone)", "5:25 the dead will hear the voice; 10:3-4 the sheep know his voice; 11:43 a great voice; 18:37 everyone of the truth hears my voice"),
 ("the instrument kept whole", "19:23-24 the seamless tunic not torn; 19:36 no bone broken; 21:11 the net not torn"),
 ("many waters (many voices)", "7:38 rivers of living water; 19:34 blood and water"),
]
# renders: the harmonic outline - each chapter's most sounded cadence string, through its vowel tube, 2.2 s per chapter
def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, b in zip(freqs, bws): bb, aa = E.resonator_coeffs(f, b); y += lfilter(bb, aa, x)
    return y
def tone(g, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f0 = STR[g]["Hz"]; y = np.zeros(n)
    for k in range(1, 25):
        if k * f0 > 7000: break
        y += np.sin(2 * np.pi * k * f0 * t) * abs(math.sin(k * math.pi * 0.2)) / k * np.exp(-t * (0.8 + 0.3 * k))
    v = {"α": "a", "ε": "ɛ", "η": "e", "ι": "i", "ο": "o", "υ": "y", "ω": "ɔ"}[g]
    s = resonate(y, R42[v]["machine"]); return (0.5 * y / np.abs(y).max() + 0.5 * s / np.abs(s).max()) * E.env_adsr(n, 0.01, 0.4)
chap = {}
for r, c in zip(J, cad): chap.setdefault(r["ref"][0], []).append(c)
outline = [(ch, ORDER[np.bincount(v, minlength=7).argmax()]) for ch, v in sorted(chap.items())]
out["chapter_outline"] = [(ch, STR[g]["string"], STR[g]["planet"]) for ch, g in outline]
rend = []
if "--no-audio" not in sys.argv:
    drone = lambda n: 0.15 * np.sin(2 * np.pi * 110 * np.arange(n) / SR)
    y = np.concatenate([tone(g, 2.2) + drone(int(2.2 * SR)) for _, g in outline])
    y = E.reverb(y / np.abs(y).max(), "holy_of_holies")
    wav = os.path.join(HERE, "audio", "r45_john_harmonic_outline.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
    mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav); rend.append(os.path.relpath(mp3, ROOT))
out["renders"] = rend
json.dump(out, open(os.path.join(HERE, "round45_results.json"), "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
for k in ("P1_string_shares", "P1_verdict", "P2_modes", "P3_positions", "P3_test", "P4_i_am_cadence_on_mese", "chapter_outline"):
    print(k, json.dumps(out[k], ensure_ascii=False, default=str))
