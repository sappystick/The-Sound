#!/usr/bin/env python3
"""Round 51. Other ways of measuring, and the band.

A. Position of the middle 'I am' (10:11) by: performed seconds (engine timing, declaimed, plus pauses at punctuation:
   period/question 0.8 s, raised dot 0.6 s, comma 0.3 s), breath groups (stretches between punctuation; any group over
   25 syllables split), and story time (John's festival frame). Each for two books: the Gospel as transmitted (SBLGNT,
   without 7:53-8:11) and the Gospel ending at 20:31 (chapter 21 widely judged an epilogue; Brown 1970).
B. Is the instrument failing because of how we assign vowels to strings? (1) The mode test (P2) is a contingency table;
   relabelling strings permutes its columns and cannot change chi-square: shown by computing it under 3 random
   vowel->string assignments. (2) A mapping-free version of P4: do 'I am' verses end on a different VOWEL distribution
   from other verses (chi-square, 10,000 verse permutations)? If not, no tuning can make them end on the mese.
C. The band: other instruments carry other layers. Drum = accent pattern of the verse-final word (oxytone,
   paroxytone, proparoxytone, perispomenon, unaccented); aulos = breath groups per verse; time = performed seconds per
   verse. Do the four movements (cuts 1:16, 13:33, 18:1) differ in any layer more than random cuts give?
D. Render John 10:11 for the band: lyre and vowel tubes (vowels), aulos drone on the mese, drum on accented syllables,
   a trumpet tekiah at the end.
Usage: python3 power/round51_other_measures.py
"""
import glob, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
rng = np.random.default_rng(51); SR = E.SR; out = {}
def bare(t): t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if not unicodedata.combining(c)).replace("ς", "σ")
V = {}
for l in open(glob.glob(os.path.join(ROOT, "sources/texts/sblgnt/*-Jn-morphgnt.txt"))[0], encoding="utf-8"):
    p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(p[3])
refs = list(V)
SIMS = np.sort(rng.random((400000, 7)), axis=1)[:, 3]
def p_mid(x): return float((np.abs(SIMS - 0.5) <= abs(x - 0.5)).mean())
PAUSE = {".": 0.8, ";": 0.8, "·": 0.6, ",": 0.3}
info = {}
for r, ws in V.items():
    words = E.parse_greek(" ".join(ws), "koine")
    _, notes, t = E.build_score(words, "greek", "koine", "declaim")
    pauses = sum(PAUSE.get(w[-1], 0) for w in ws)
    groups, cur = 0, 0
    for w, pw in zip(ws, words):
        cur += len(pw)
        if w[-1] in PAUSE or cur > 25: groups += 1; cur = 0
    if cur: groups += 1
    fw = words[-1] if words else []; sy = [x for x in fw if x.get("nuc")]
    a = next((i for i, x in enumerate(sy) if x["accent"] in ("acute", "grave", "circ")), None)
    drum = "unaccented" if a is None else ("perispomenon" if a == len(sy) - 1 and sy[a]["accent"] == "circ" else
            {0: "oxytone", 1: "paroxytone"}.get(len(sy) - 1 - a, "proparoxytone"))
    last_v = sy[-1]["nuc"][0].rstrip("ː") if sy else "?"
    info[r] = dict(sec=t + pauses, groups=groups, drum=drum, last_v=last_v, words=len(ws))
def position(units, end=None):
    rs = [r for r in refs if end is None or r <= end]; cum = np.cumsum([0] + [info[r][units] for r in rs]); i = rs.index((10, 11))
    x = float((cum[i] + cum[i + 1]) / 2 / cum[-1]); return dict(position=round(x, 4), p=round(p_mid(x), 4), total=round(float(cum[-1]), 1))
A = {}
for book, end in (("as transmitted (1:1-21:25)", None), ("ending at 20:31", (20, 31))):
    A[book] = {u: position(u, end) for u in ("sec", "groups", "words")}
# story time (days, festival frame; model, labelled): Passover AD 28 = day 0 (2:13), Passover 29 = 365 (6:4),
# Tabernacles 29 = 543 (7:2), Dedication 29 = 613 (10:22), Passover 30 = 730 (11:55 -> 19), Easter + 8 days = 738 (20:26)
ANCH = [((1, 19), -21), ((2, 13), 0), ((6, 4), 365), ((7, 2), 543), ((7, 14), 547), ((10, 22), 613), ((11, 55), 724), ((12, 1), 724), ((13, 1), 729), ((19, 42), 730), ((20, 1), 732), ((20, 26), 740), ((21, 1), 750), ((21, 25), 755)]
def day(r):
    for (a, da), (b, db) in zip(ANCH, ANCH[1:]):
        if a <= r <= b:
            ia, ib = refs.index(a), refs.index(b); return da + (db - da) * (refs.index(r) - ia) / max(1, ib - ia)
    return ANCH[-1][1]
d1011 = day((10, 11))
A["story time (days, model)"] = dict(day_of_10_11=round(d1011, 1), position_full=round((d1011 + 21) / (755 + 21), 3), position_to_20_31=round((d1011 + 21) / (740 + 21), 3),
    share_of_book_on_last_week=round(sum(info[r]["words"] for r in refs if r >= (12, 1)) / sum(info[r]["words"] for r in refs), 3),
    middle_of_the_feast="7:14: 'when the feast was already at its middle (μεσούσης), Jesus went up into the temple and taught'")
out["A_positions"] = A

# B. the vowel-to-string assignment cannot rescue the tests
cuts = [refs.index((1, 16)), refs.index((13, 33)), refs.index((18, 1))]
VOWELS = sorted({info[r]["last_v"] for r in refs})
def table(labels, cutpos):
    b = [0] + list(cutpos) + [len(refs)]; cats = sorted(set(labels))
    return np.array([[sum(1 for x in labels[b[i]:b[i + 1]] if x == c) for c in cats] for i in range(4)], float)
def chi(tab):
    e = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum(); m = e > 0; return float((((tab - e) ** 2)[m] / e[m]).sum())
lv = [info[r]["last_v"] for r in refs]
inv = []
for _ in range(3):
    perm = dict(zip(VOWELS, rng.permutation(VOWELS))); inv.append(round(chi(table([perm[x] for x in lv], cuts)), 4))
out["B_relabelling_invariance"] = dict(chi2_under_3_random_assignments=inv, note="identical: no vowel-to-string assignment can change the mode test")
iam = np.array([any(bare(V[r][i]).strip(".,;·") == "εγω" and bare(V[r][i + 1]).startswith("ειμι") for i in range(len(V[r]) - 1)) for r in refs])
def chi_iam(lab):
    cats = sorted(set(lab)); t = np.array([[sum(1 for x, y in zip(lab, iam) if x == c and y == g) for c in cats] for g in (True, False)], float); return chi(t)
o = chi_iam(lv); nl = []
for _ in range(10000):
    iam_s = rng.permutation(iam); cats = sorted(set(lv))
    t = np.array([[sum(1 for x, y in zip(lv, iam_s) if x == c and y == g) for c in cats] for g in (True, False)], float); nl.append(chi(t))
out["B_iam_cadence_mapping_free"] = dict(chi2=round(o, 2), p=round(float((np.array(nl) >= o).mean()), 4), i_am_verses=int(iam.sum()),
    note="p >= 0.05 means no assignment of vowels to strings can make the 'I am' verses cadence differently")

# C. the band's layers by movement
def null_cuts(stat, reps=3000):
    obs = stat(cuts); nlv = [stat(np.sort(rng.choice(np.arange(15, len(refs) - 15), 3, replace=False))) for _ in range(reps)]
    return dict(stat=round(obs, 3), p=round(float((np.array(nlv) >= obs).mean()), 4))
drum = [info[r]["drum"] for r in refs]; grp = np.array([info[r]["groups"] for r in refs], float); sec = np.array([info[r]["sec"] for r in refs])
def anova(x, cutpos):
    b = [0] + list(cutpos) + [len(x)]; gm = x.mean(); return float(sum((b[i + 1] - b[i]) * (x[b[i]:b[i + 1]].mean() - gm) ** 2 for i in range(4)))
out["C_band_layers"] = {"drum (final-word accent)": null_cuts(lambda c: chi(table(drum, c))),
                        "aulos (breath groups per verse)": null_cuts(lambda c: anova(grp, c)),
                        "time (performed seconds per verse)": null_cuts(lambda c: anova(sec, c)),
                        "lyre (final vowel)": null_cuts(lambda c: chi(table(lv, c)))}
b = [0] + cuts + [len(refs)]
out["C_movement_means"] = [dict(movement=m, seconds_per_verse=round(float(sec[b[i]:b[i + 1]].mean()), 2), breath_groups=round(float(grp[b[i]:b[i + 1]].mean()), 2))
                           for i, m in enumerate(["prologue", "signs", "farewell", "passion"])]

# D. the band plays John 10:11
R41 = json.load(open(os.path.join(HERE, "round41_results.json")))["instrument"]["heptachord_lyre"]
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
STR = {s["vowel"]: s for s in R41}; IPA2GK = {"a": "α", "ɛ": "ε", "e": "η", "i": "ι", "o": "ο", "y": "υ", "ɔ": "ω", "u": "ο"}
def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, bw in zip(freqs, bws): bb, aa = E.resonator_coeffs(f, bw); y += lfilter(bb, aa, x)
    return y
def pluck(f0, n):
    tt = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 30):
        if k * f0 > 8000: break
        y += np.sin(2 * np.pi * k * f0 * tt) * abs(math.sin(k * math.pi * 0.2)) / k * np.exp(-tt * (1.2 + 0.5 * k))
    return y
lyre, drumtrack, tpos, beat = [], [], 0.0, 0.40
for pw in E.parse_greek(" ".join(V[(10, 11)]), "koine"):
    for s in pw:
        if not s.get("nuc"): continue
        v = s["nuc"][0].rstrip("ː"); st = STR[IPA2GK.get(v, "α")]; d = beat * (2 if s.get("long") or s["nuc"][0].endswith("ː") else 1); n = int(d * SR)
        tone = pluck(st["Hz"], n); sp = resonate(tone, R42[v]["machine"] if v in R42 else R42["a"]["machine"])
        lyre.append(0.45 * tone / np.abs(tone).max() + 0.55 * sp / np.abs(sp).max())
        if s["accent"] in ("acute", "grave", "circ"): drumtrack.append(tpos)
        tpos += d
    lyre.append(np.zeros(int(0.12 * SR))); tpos += 0.12
y = np.concatenate(lyre); L = len(y) + int(4 * SR); mix = np.zeros(L); mix[:len(y)] += E.norm(y, 0.8)
tt = np.arange(L) / SR; mix += 0.12 * (np.sin(2 * np.pi * 220 * tt) + 0.5 * np.sin(2 * np.pi * 440 * tt) + 0.3 * np.sin(2 * np.pi * 660 * tt)) * np.minimum(1, tt) * np.minimum(1, (L / SR - tt))
dr = E.inst_drum(int(0.4 * SR)) if True else None
for t0 in drumtrack: E.place(mix, 0.5 * E.norm(dr), t0)
E.place(mix, 0.6 * E.norm(E.inst_brass(233.0, 233.0, int(2.7 * SR), bright=1.2)), len(y) / SR + 0.3)
y = E.reverb(E.norm(mix), "temple")
wav = os.path.join(HERE, "audio", "r51_band_john_10_11.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
out["D_render"] = os.path.relpath(mp3, ROOT)
json.dump(out, open(os.path.join(HERE, "round51_results.json"), "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
