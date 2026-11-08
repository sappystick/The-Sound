#!/usr/bin/env python3
"""Centering used as a probe: what sits at the exact spoken middle of each major unit of John and 1 John?
Units use the boundaries common in commentaries (fixed before looking).  For each unit, report the verse
at the syllable midpoint and the words around it.  Where scholars have proposed a centre independently,
compare.  This is a hypothesis generator, not a proof: every unit has a middle.
Usage: python3 centers_scan.py <sblgnt dir>
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL = sys.argv[1]; cache = {}
def nsyl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]
def load(fn):
    out = []
    for line in open(os.path.join(SBL, fn), encoding="utf-8"):
        p = line.split(); out.append(((int(p[0][2:4]), int(p[0][4:])), p[3], nsyl(p[4])))
    return out
JN, JN1 = load("64-Jn-morphgnt.txt"), load("83-1Jn-morphgnt.txt")
UNITS = [  # (label, book, start, end, scholars' proposed centre or None)
    ("Prologue", JN, (1, 1), (1, 18), "1:12b (Culpepper)"), ("First witnesses", JN, (1, 19), (1, 51), None),
    ("Cana wedding", JN, (2, 1), (2, 11), None), ("Nicodemus", JN, (3, 1), (3, 21), None),
    ("Samaritan woman", JN, (4, 1), (4, 42), None), ("Healing at Bethesda and discourse", JN, (5, 1), (5, 47), None),
    ("Bread of life discourse", JN, (6, 22), (6, 71), None), ("Tabernacles discourses", JN, (7, 1), (8, 59), None),
    ("Man born blind", JN, (9, 1), (9, 41), None), ("Good shepherd", JN, (10, 1), (10, 21), None),
    ("Lazarus", JN, (11, 1), (11, 44), None), ("Last supper and footwashing", JN, (13, 1), (13, 30), None),
    ("Farewell discourses", JN, (13, 31), (17, 26), None), ("Prayer of Jesus", JN, (17, 1), (17, 26), None),
    ("Trial before Pilate", JN, (18, 28), (19, 16), "19:1-3, the crowning with thorns (R.E. Brown)"),
    ("Passion and burial", JN, (18, 1), (19, 42), None), ("Resurrection", JN, (20, 1), (20, 31), None),
    ("1 John (whole letter)", JN1, (1, 1), (5, 21), None),
]
res = []
for lab, bk, a, b, sch in UNITS:
    ws = [w for w in bk if a <= w[0] <= b]; tot = sum(w[2] for w in ws); acc = 0
    for i, w in enumerate(ws):
        if acc + w[2] > tot / 2: mid = i; break
        acc += w[2]
    ctx = " ".join(x[1] for x in ws[max(0, mid - 6): mid + 7])
    ref = f"{ws[mid][0][0]}:{ws[mid][0][1]}"
    res.append(dict(unit=lab, span=f"{a[0]}:{a[1]}-{b[0]}:{b[1]}", syllables=tot, center=ref, words=ctx, scholars=sch))
    print(f"{lab:36s} {a[0]}:{a[1]}-{b[0]}:{b[1]:<3d} ({tot:5d} syl) centre {ref:6s} | {ctx}" + (f"   [scholars: {sch}]" if sch else ""))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "centers_scan_results.json"), "w"), ensure_ascii=False, indent=1)

# ---- chance check (added after seeing the results, labelled as such) -----------------------
# For each unit containing a predicate 'I am' saying, the share of its syllables lying within +-1 verse
# of a saying = the chance a random centre lands that close.  Combine across units (Poisson-binomial).
IAM = {(6, 35), (6, 48), (6, 51), (8, 12), (10, 7), (10, 9), (10, 11), (10, 14), (11, 25), (14, 6), (15, 1), (15, 5)}
def near(ref, unitw):
    vs = sorted({w[0] for w in unitw}); i = vs.index(ref)
    return any(v in IAM for v in vs[max(0, i - 1): i + 2])
probs, hits = [], []
for lab, bk, a, b, sch in UNITS:
    ws = [w for w in bk if a <= w[0] <= b]
    if bk is not JN or not any(w[0] in IAM for w in ws) or lab in ("Passion and burial",): continue
    tot = sum(w[2] for w in ws); p = sum(w[2] for w in ws if near(w[0], ws)) / tot
    acc = 0
    for w in ws:
        if acc + w[2] > tot / 2: c = w[0]; break
        acc += w[2]
    h = near(c, ws); probs.append(p); hits.append(h)
    print(f"   {lab:32s} chance {p:.2f}  centre {c[0]}:{c[1]}  {'HIT' if h else '-'}")
import itertools
k = sum(hits); n = len(probs)
pk = sum(__import__('math').prod(probs[i] if i in s else 1 - probs[i] for i in range(n))
         for r in range(k, n + 1) for s in map(set, itertools.combinations(range(n), r)))
print(f"   {k} of {n} units centre within one verse of an 'I am' saying; chance of {k} or more: p = {pk:.3f}")
# 'passed from death to life': share of John 5 and 1 John occupied by those verses
for lab, bk, a, b, ref in (("John 5", JN, (5, 1), (5, 47), (5, 24)), ("1 John", JN1, (1, 1), (5, 21), (3, 14))):
    ws = [w for w in bk if a <= w[0] <= b]; print(f"   {lab}: verse {ref[0]}:{ref[1]} is {sum(w[2] for w in ws if w[0] == ref) / sum(w[2] for w in ws):.1%} of the unit")
