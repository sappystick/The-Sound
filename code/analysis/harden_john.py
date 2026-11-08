#!/usr/bin/env python3
"""Hardening checks for two John results.
1. 'I am' ring with the passage of the woman caught in adultery (7:53-8:11) inserted.  It is absent
   from P66/P75 but present in the Byzantine text.  Its length is estimated from its ~183 Greek words
   at John's mean of syllables per word.
2. Is the prologue's exclusive vocabulary unusual?  For every 18-verse window of John, count lemmas
   that occur in the window and nowhere else in John; compare the prologue.
"""
import collections, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL = sys.argv[1]; cache = {}
def nsyl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]
rows = [l.split() for l in open(os.path.join(SBL, "64-Jn-morphgnt.txt"), encoding="utf-8")]
vs, t, words = {}, 0, 0
for r in rows:
    k = (int(r[0][2:4]), int(r[0][4:])); vs.setdefault(k, t); t += nsyl(r[4]); words += 1
N = t; spw = N / words; PA = round(183 * spw)
print(f"John {N} syllables, {spw:.2f} syllables/word; adultery passage estimated at {PA} syllables")
def sym_err(ps):
    k = len(ps); return sum(abs((ps[i] - .5) + (ps[k - 1 - i] - .5)) for i in range(k // 2))
SAY = [(6, 35), (8, 12), (10, 7), (10, 11), (11, 25), (14, 6), (15, 1)]
rng = random.Random(9)
for label, extra in (("without 7:53-8:11 (earliest papyri)", 0), ("with 7:53-8:11 (Byzantine)", PA)):
    tot = N + extra
    ps = sorted((vs[k] + (extra if k >= (8, 12) else 0)) / tot for k in SAY)
    e = sym_err(ps); p = sum(sym_err(sorted(rng.random() for _ in range(7))) <= e for _ in range(100000)) / 100000
    print(f"  {label:38s} middle {ps[3]:.3f}  ring error {e:.3f}  p = {p:.3f}")
# 2. exclusive vocabulary per 18-verse window
verses = sorted(vs); lem_by_v = collections.defaultdict(list)
for r in rows: lem_by_v[(int(r[0][2:4]), int(r[0][4:]))].append(r[6])
total = collections.Counter(l for r in rows for l in [r[6]])
counts = []
for i in range(len(verses) - 17):
    win = verses[i:i + 18]; c = collections.Counter(l for v in win for l in lem_by_v[v])
    excl = sum(1 for l, n in c.items() if n == total[l] and total[l] >= 1)
    counts.append((excl, win[0]))
pro = next(e for e, v in counts if v == (1, 1))
rank = sum(e >= pro for e, _ in counts)
print(f"\nprologue: {pro} lemmas found nowhere else in John; windows with as many or more: {rank} of {len(counts)}")
print("  top windows:", sorted(counts, reverse=True)[:6])
