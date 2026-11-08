#!/usr/bin/env python3
"""Beyond the centre: open-ended scan of the four Gospels, with a chance check for every pattern.

1. BOOK ORDER: where the spoken midpoint of the four Gospels (and of the New Testament) falls under each
   book order attested in antiquity.
2. SPREAD-APART WORDS: words used exactly twice in a Gospel; do the pairs mirror around the book's own
   midpoint more than around any other point?  (Null = the same statistic at 99 other pseudo-centres.)
3. TRUE BEGINNINGS AND ENDINGS: how strongly the opening echoes the close (shared rare vocabulary) for each
   candidate ending (John 20:31 vs 21:25; Mark 16:8 vs 16:20), against random windows of the same size.
4. ALIGNMENT ACROSS GOSPELS: positions of the events all four narrate, and whether any falls at the same
   fraction in all four.
Usage: python3 gospels_scan.py <sblgnt dir>
"""
import collections, glob, json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL = sys.argv[1]; cache = {}; rng = random.Random(44); out = {}
def syl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]
BOOKS = {}
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    code = os.path.basename(f).split("-")[1]
    BOOKS[code] = [((int(l[2:4]), int(l[4:6])), l.split()[6], syl(l.split()[4])) for l in open(f, encoding="utf-8")]
def total(code): return sum(r[2] for r in BOOKS[code])

# 1. book order -------------------------------------------------------------------------------------
print("1. BOOK ORDER: spoken midpoint of the four Gospels under each ancient order")
ORDERS = {"Canonical (Mt Mk Lk Jn)": ["Mt", "Mk", "Lk", "Jn"], "Western (Mt Jn Lk Mk: Bezae, W)": ["Mt", "Jn", "Lk", "Mk"],
          "Cheltenham list (Mt Mk Jn Lk)": ["Mt", "Mk", "Jn", "Lk"], "Codex 888 type (Jn Mt Lk Mk)": ["Jn", "Mt", "Lk", "Mk"]}
def midpoint(order):
    T = sum(total(b) for b in order); acc = 0
    for b in order:
        for r in BOOKS[b]:
            if acc + r[2] > T / 2: return b, r[0], T
            acc += r[2]
res1 = {}
for lab, order in ORDERS.items():
    b, ref, T = midpoint(order); res1[lab] = f"{b} {ref[0]}:{ref[1]}"; print(f"   {lab:36s} midpoint in {b} {ref[0]}:{ref[1]}  (of {T} syllables)")
nt = ["Mt", "Mk", "Lk", "Jn", "Ac", "Ro", "1Co", "2Co", "Ga", "Eph", "Php", "Col", "1Th", "2Th", "1Ti", "2Ti", "Tit", "Phm", "Heb", "Jas", "1Pe", "2Pe", "1Jn", "2Jn", "3Jn", "Jud", "Re"]
nt = [b for b in nt if b in BOOKS]; b, ref, T = midpoint(nt); print(f"   Whole New Testament (canonical order): midpoint in {b} {ref[0]}:{ref[1]} of {T} syllables")
res1["NT"] = f"{b} {ref[0]}:{ref[1]}"; out["book_order"] = res1

# 2. spread-apart words ----------------------------------------------------------------------------
print("\n2. SPREAD-APART WORDS: twice-used words mirrored around the book's midpoint vs 99 other points")
res2 = {}
for code in ("Mt", "Mk", "Lk", "Jn"):
    rows = BOOKS[code]; T = total(code); pos = collections.defaultdict(list); acc = 0
    for r in rows: pos[r[1]].append(acc / T); acc += r[2]
    pairs = [(v[0], v[1]) for v in pos.values() if len(v) == 2 and v[1] - v[0] > 0.1]
    def score(c, eps=0.005): return sum(abs((a + b) / 2 - c) < eps for a, b in pairs)
    real = score(0.5); others = [score(c) for c in [0.25 + 0.5 * i / 99 for i in range(100)] if abs(c - 0.5) > 0.01]
    rank = sum(o >= real for o in others) / len(others)
    best_c = max([0.25 + 0.5 * i / 99 for i in range(100)], key=score)
    res2[code] = dict(pairs=len(pairs), mirrored_at_mid=real, share_other_points_as_high=round(rank, 3), best_point=round(best_c, 3))
    print(f"   {code}: {len(pairs)} spread pairs; mirrored around the midpoint: {real}; other points with as many: {rank:.0%}; most mirrored point {best_c:.3f}")
out["spread_words"] = res2

# 3. beginnings and endings ----------------------------------------------------------------------
print("\n3. TRUE BEGINNINGS AND ENDINGS: echo between opening and closing (rare words), vs random windows")
def echo(code, end_ref, frac=0.03):
    rows = [r for r in BOOKS[code] if r[0] <= end_ref]; T = sum(r[2] for r in rows); freq = collections.Counter(r[1] for r in BOOKS[code])
    acc = 0; tag = []
    for r in rows: tag.append(acc / T); acc += r[2]
    rare = lambda l: freq[l] <= 8
    opening = {r[1] for r, t in zip(rows, tag) if t < frac and rare(r[1])}
    closing = {r[1] for r, t in zip(rows, tag) if t > 1 - frac and rare(r[1])}
    real = len(opening & closing); cnt = 0; R = 2000
    for _ in range(R):
        x = rng.random() * (1 - 2 * frac); y = rng.random() * (1 - 2 * frac)
        if abs(x - y) < 2 * frac: continue
        A = {r[1] for r, t in zip(rows, tag) if x <= t < x + frac and rare(r[1])}
        B = {r[1] for r, t in zip(rows, tag) if y <= t < y + frac and rare(r[1])}
        cnt += len(A & B) >= real
    return real, sorted(opening & closing), cnt / R
res3 = {}
for code, end, lab in (("Jn", (20, 31), "John ending at 20:31"), ("Jn", (21, 25), "John ending at 21:25"),
                       ("Mk", (16, 8), "Mark ending at 16:8"), ("Mk", (16, 20), "Mark ending at 16:20"),
                       ("Mt", (28, 20), "Matthew"), ("Lk", (24, 53), "Luke")):
    if end not in {r[0] for r in BOOKS[code]}: print(f"   {lab}: verse not in this edition"); continue
    real, words, p = echo(code, end); res3[lab] = dict(shared=real, words=words, p=p)
    print(f"   {lab:22s} opening/closing share {real} rare words {words}; random window pairs with as many: p = {p:.3f}")
out["endings"] = res3

# 4. events aligned across the four ---------------------------------------------------------------
print("\n4. EVENTS ALL FOUR GOSPELS NARRATE: position in each Gospel's spoken time")
EV = {"Baptist / baptism": {"Mt": (3, 1), "Mk": (1, 4), "Lk": (3, 1), "Jn": (1, 19)},
      "Feeding of the 5,000": {"Mt": (14, 13), "Mk": (6, 32), "Lk": (9, 10), "Jn": (6, 1)},
      "Peter's confession": {"Mt": (16, 16), "Mk": (8, 29), "Lk": (9, 20), "Jn": (6, 68)},
      "Entry into Jerusalem": {"Mt": (21, 1), "Mk": (11, 1), "Lk": (19, 28), "Jn": (12, 12)},
      "Arrest": {"Mt": (26, 47), "Mk": (14, 43), "Lk": (22, 47), "Jn": (18, 1)},
      "Crucifixion": {"Mt": (27, 35), "Mk": (15, 24), "Lk": (23, 33), "Jn": (19, 18)},
      "Empty tomb": {"Mt": (28, 1), "Mk": (16, 1), "Lk": (24, 1), "Jn": (20, 1)}}
res4 = {}
for ev, refs in EV.items():
    ps = {}
    for code, ref in refs.items():
        T = total(code); acc = 0
        for r in BOOKS[code]:
            if r[0] == ref: ps[code] = acc / T; break
            acc += r[2]
    spread = max(ps.values()) - min(ps.values()); res4[ev] = dict(positions={k: round(v, 3) for k, v in ps.items()}, spread=round(spread, 3))
    print(f"   {ev:22s} " + "  ".join(f"{k} {v:.3f}" for k, v in ps.items()) + f"   spread {spread:.3f}")
out["events"] = res4
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gospels_scan_results.json"), "w"), ensure_ascii=False, indent=1)
