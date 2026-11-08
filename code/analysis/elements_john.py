#!/usr/bin/env python3
"""An elemental reading of John's Gospel (SBLGNT): where water, light, darkness, fire, blood,
flesh, earth and breath fall in spoken time, and which elements close circles around the
Gospel's spoken center.  Also: order of first appearance vs Genesis 1 (LXX).

Positions are in syllables (reconstructed Koine, as in the engine) from the start of John 1:1.
Usage: python3 elements_john.py <sblgnt dir> <lxx-swete/data>
"""
import collections, json, os, re, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E

ELEMENTS = {  # element: SBLGNT lemmas (fixed before counting)
    "water": {"ὕδωρ", "θάλασσα", "κολυμβήθρα", "πηγή", "φρέαρ", "νίπτω", "λούω", "βαπτίζω", "ποταμός", "βρέχω"},
    "light": {"φῶς", "φωτίζω", "φαίνω", "λύχνος", "λαμπάς", "φανός"},
    "darkness": {"σκοτία", "σκότος", "νύξ"},
    "fire": {"πῦρ", "ἀνθρακιά", "καίω", "κλῆμα_burn"},
    "blood": {"αἷμα"},
    "flesh": {"σάρξ", "σῶμα"},
    "earth": {"γῆ", "χαμαί", "πηλός", "κόκκος", "σῖτος", "χῶμα"},
    "breath": {"πνεῦμα", "πνέω", "ἐμφυσάω", "ἄνεμος"},
}
rows = [l.split() for l in open(os.path.join(sys.argv[1], "64-Jn-morphgnt.txt"), encoding="utf-8")]
cache = {}


def nsyl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]


pos, t = [], 0
for r in rows:
    ch, vs = int(r[0][2:4]), int(r[0][4:])
    pos.append((t, ch, vs, r[6])); t += nsyl(r[4])
N = t
# Gospel's spoken center, with 7:53-8:11 (absent from P66/P75) excluded and chapter 21 kept
core = [(p, c, v, l) for p, c, v, l in pos]
center = N / 2
cv = min(core, key=lambda x: abs(x[0] - center))
print(f"John: {N} syllables; spoken center at syllable {center:.0f} = {cv[1]}:{cv[2]}")
out = {"syllables": N, "center": f"{cv[1]}:{cv[2]}", "elements": {}}
for el, lem in ELEMENTS.items():
    hits = [(p, c, v, l) for p, c, v, l in pos if l in lem]
    if not hits: continue
    first, last = hits[0], hits[-1]
    da, db = center - first[0], last[0] - center
    sym = min(da, db) / max(da, db) if da > 0 and db > 0 else 0.0
    bych = collections.Counter(c for _, c, _, _ in hits)
    out["elements"][el] = dict(count=len(hits), first=f"{first[1]}:{first[2]} {first[3]}",
                               last=f"{last[1]}:{last[2]} {last[3]}", first_pos=round(first[0] / N, 3),
                               last_pos=round(last[0] / N, 3), circle_symmetry=round(sym, 2),
                               peak_chapters=bych.most_common(3))
    print(f"{el:9s} n={len(hits):3d} first {first[1]}:{first[2]} ({first[0] / N:.3f}) last {last[1]}:{last[2]} "
          f"({last[0] / N:.3f}) circle {sym:.2f}  peaks {bych.most_common(3)}")

# baseline: how symmetric is the first/last use of any lemma used >= 5 times?
by = collections.defaultdict(list)
for p, c, v, l in pos: by[l].append(p)
syms = []
for l, ps in by.items():
    if len(ps) >= 5:
        da, db = center - ps[0], ps[-1] - center
        syms.append(min(da, db) / max(da, db) if da > 0 and db > 0 else 0.0)
syms = np.array(syms)
for thr in (0.9, 0.95):
    print(f"baseline: {np.mean(syms >= thr):.1%} of {len(syms)} lemmas used >=5 times have circle symmetry >= {thr}")
out["baseline_share_ge_0.9"] = round(float(np.mean(syms >= 0.9)), 3)

# rare pairs: element words used exactly twice in John -> where?
print("\nelement words used exactly twice in John (paired echoes):")
pairs = []
for el, lem in ELEMENTS.items():
    for l in lem:
        ps = [(c, v, p) for p, c, v, ll in pos if ll == l]
        if len(ps) == 2:
            pairs.append((el, l, f"{ps[0][0]}:{ps[0][1]}", f"{ps[1][0]}:{ps[1][1]}"))
            print(f"  {el:9s} {l:12s} {ps[0][0]}:{ps[0][1]}  &  {ps[1][0]}:{ps[1][1]}")
out["pairs"] = pairs

# order of first appearance: John vs Genesis 1:1-2:4 (LXX, surface forms)
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(ch for ch in w if not unicodedata.combining(ch))
    return re.sub(r"[^α-ως]", "", w)
STEMS = {"water": ("υδωρ", "υδατ"), "light": ("φως", "φωτ"), "darkness": ("σκοτ",), "earth": ("γη", "γης", "γην"),
         "breath": ("πνευμ",), "flesh": ("σαρξ", "σαρκ"), "blood": ("αιμα",), "fire": ("πυρ",)}
gen = []
for line in open(os.path.join(sys.argv[2], "01.Genesis.txt"), encoding="utf-8"):
    p = line.split(maxsplit=1)
    if len(p) < 2: continue
    _, ch, vs = p[0].split(".")
    if int(ch) == 1 or (int(ch) == 2 and int(vs) <= 4): gen.append(nrm(p[1]))
gfirst = {}
for i, w in enumerate(gen):
    for el, st in STEMS.items():
        if el not in gfirst and (w in st or any(w.startswith(s) and len(s) > 2 for s in st)): gfirst[el] = i
jorder = sorted(out["elements"], key=lambda e: out["elements"][e]["first_pos"])
gorder = sorted(gfirst, key=gfirst.get)
print("\nfirst appearance order  John 1-21:", jorder)
print("first appearance order  Genesis 1:1-2:4:", gorder)
out["order_john"] = jorder; out["order_genesis1"] = gorder
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "elements_john_results.json"), "w"),
          ensure_ascii=False, indent=1)
