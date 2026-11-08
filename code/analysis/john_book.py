#!/usr/bin/env python3
"""Picking apart John's Gospel in spoken time (SBLGNT, syllables as in the engine).

1. Book-level structure: positions of the seven predicate 'I am' sayings, the seven signs and the
   feast notices.  Test (fixed before looking): is the MIDDLE item of each sequence of seven closer
   to the Gospel's spoken midpoint than chance?  Null = 7 positions drawn uniformly at random,
   sorted, 4th taken (100,000 draws); also pair symmetry (1-7, 2-6, 3-5 around the midpoint)
   against the same null.
2. Prologue vocabulary at book scale: for each content word of 1:1-18, where else in John does it
   occur?  Words that vanish after the prologue and words that return only at the end.
3. Visual layer: the nomina sacra (sacred names written abbreviated with an overline in P66/P75
   and other early papyri).  Density per chapter, using the lemma as proxy for the manuscripts'
   practice, which varies.
Usage: python3 john_book.py <sblgnt dir>
"""
import collections, json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E

rows = [l.split() for l in open(os.path.join(sys.argv[1], "64-Jn-morphgnt.txt"), encoding="utf-8")]
cache = {}
def nsyl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]
pos, t, vstart = [], 0, {}
for r in rows:
    ch, vs = int(r[0][2:4]), int(r[0][4:])
    vstart.setdefault((ch, vs), t)
    pos.append((t, ch, vs, r[6], r[3])); t += nsyl(r[4])
N = t
def at(ch, vs): return vstart[(ch, vs)] / N
mid_cv = min(vstart, key=lambda k: abs(vstart[k] - N / 2))
print(f"John: {N} syllables; spoken midpoint at {mid_cv[0]}:{mid_cv[1]}")
out = {"syllables": N, "midpoint": f"{mid_cv[0]}:{mid_cv[1]}"}

SEQS = {
    "I am sayings": [("bread of life", 6, 35), ("light of the world", 8, 12), ("the door", 10, 7), ("the good shepherd", 10, 11),
                     ("resurrection and life", 11, 25), ("way, truth, life", 14, 6), ("the true vine", 15, 1)],
    "signs": [("water into wine", 2, 9), ("official's son", 4, 50), ("paralysed man", 5, 8), ("feeding 5,000", 6, 11),
              ("walking on water", 6, 19), ("man born blind", 9, 7), ("Lazarus raised", 11, 43)],
    "feasts": [("Passover", 2, 13), ("a feast", 5, 1), ("Passover", 6, 4), ("Tabernacles", 7, 2), ("Dedication", 10, 22),
               ("Passover", 11, 55)],
}
rng = random.Random(3); R = 100000
for name, items in SEQS.items():
    ps = [at(c, v) for _, c, v in items]; k = len(ps)
    print(f"\n{name}:")
    for (lab, c, v), p in zip(items, ps): print(f"   {lab:24s} {c}:{v:<3d} at {p:.3f}")
    mid_item = sorted(ps)[k // 2] if k % 2 else None
    sym = sum(abs((ps[i] - 0.5) + (ps[k - 1 - i] - 0.5)) for i in range(k // 2))
    res = dict(items=[(lab, f"{c}:{v}", round(p, 3)) for (lab, c, v), p in zip(items, ps)], symmetry_error=round(sym, 3))
    sims_m, sims_s = 0, 0
    for _ in range(R):
        x = sorted(rng.random() for _ in range(k))
        if mid_item is not None and abs(x[k // 2] - 0.5) <= abs(mid_item - 0.5): sims_m += 1
        if sum(abs((x[i] - 0.5) + (x[k - 1 - i] - 0.5)) for i in range(k // 2)) <= sym: sims_s += 1
    if mid_item is not None:
        res["middle_item_offset"] = round(mid_item - 0.5, 3); res["p_middle"] = sims_m / R
        print(f"   middle item at {mid_item:.3f} (offset {mid_item - 0.5:+.3f}); chance of being this close: p = {sims_m / R:.3f}")
    res["p_symmetry"] = sims_s / R
    print(f"   pair symmetry error {sym:.3f}; chance of a ring this tight: p = {sims_s / R:.3f}")
    out[name] = res

# 2. prologue vocabulary at book scale
STOP = {"ὁ", "καί", "δέ", "ἐν", "αὐτός", "οὗτος", "εἰμί", "ὅς", "ἵνα", "ὅτι", "οὐ", "πρός", "διά", "εἰς", "ἐκ", "οὐδέ", "μή",
        "ἐγώ", "ὅσος", "ἀλλά", "πᾶς", "εἷς", "ἀπό", "ἀντί", "οὐδείς", "κατά", "τις", "ἐκεῖνος", "λέγω", "ἔρχομαι", "λαμβάνω",
        "γάρ", "ἡμεῖς", "σύ", "παρά", "περί", "ἔμπροσθεν", "γίνομαι", "ἐκεῖ", "πρῶτος", "ὀπίσω", "ἴδιος", "ὅτι", "πώποτε", "οὔπω"}
prol = collections.Counter(l for p, c, v, l, _ in pos if c == 1 and v <= 18 and l not in STOP)
rest = collections.defaultdict(list)
for p, c, v, l, _ in pos:
    if not (c == 1 and v <= 18) and l in prol: rest[l].append((c, v))
print("\nprologue words: uses in the rest of the Gospel (first and last)")
pv = []
for l, n in prol.most_common():
    rs = rest.get(l, [])
    print(f"   {l:14s} prologue {n:2d} | rest {len(rs):3d} | " + (f"{rs[0][0]}:{rs[0][1]} ... {rs[-1][0]}:{rs[-1][1]}" if rs else "NEVER AGAIN"))
    pv.append((l, n, len(rs), f"{rs[0][0]}:{rs[0][1]}" if rs else "", f"{rs[-1][0]}:{rs[-1][1]}" if rs else ""))
out["prologue_vocab"] = pv

# 3. nomina sacra (lemma proxy)
NS = {"θεός", "Ἰησοῦς", "Χριστός", "κύριος", "πνεῦμα", "πατήρ", "υἱός", "ἄνθρωπος", "σταυρός", "σταυρόω", "οὐρανός",
      "Ἰσραήλ", "Δαυίδ", "Ἰερουσαλήμ", "μήτηρ", "σωτήρ"}
chw = collections.Counter(c for _, c, _, _, _ in pos); chn = collections.Counter(c for _, c, _, l, _ in pos if l in NS)
tot = sum(chn.values()) / len(pos)
print(f"\nnomina sacra (proxy): {sum(chn.values())} of {len(pos)} words ({tot:.1%})")
dens = []
for c in sorted(chw):
    d = chn[c] / chw[c]; dens.append((c, chn[c], chw[c], round(d, 3)))
    print(f"   ch {c:2d}: {chn[c]:3d}/{chw[c]:4d} = {d:.1%} {'#' * int(d * 200)}")
prol_ns = [(c, v, l) for p, c, v, l, _ in pos if c == 1 and v <= 18 and l in NS]
print("   in the prologue:", [(f"1:{v}", l) for c, v, l in prol_ns])
out["nomina_sacra"] = dict(by_chapter=dens, overall=round(tot, 4), prologue=[(f"1:{v}", l) for c, v, l in prol_ns])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "john_book_results.json"), "w"), ensure_ascii=False, indent=1)

# ---- robustness for the 'I am' ring (added after the first run, labelled as such) ----------
print("\n[robustness] 'I am' ring")
def sym_err(ps):
    k = len(ps); return sum(abs((ps[i] - 0.5) + (ps[k - 1 - i] - 0.5)) for i in range(k // 2))
variants = {
    "first occurrence (as above)": [(6, 35), (8, 12), (10, 7), (10, 11), (11, 25), (14, 6), (15, 1)],
    "second occurrence where repeated": [(6, 48), (8, 12), (10, 9), (10, 14), (11, 25), (14, 6), (15, 5)],
    "mixed": [(6, 51), (8, 12), (10, 9), (10, 11), (11, 25), (14, 6), (15, 5)],
}
# all occurrences of the phrase ego eimi in John (any form), as a tougher null pool
egoeimi = []
for i in range(len(pos) - 1):
    if pos[i][3] == "ἐγώ" and pos[i + 1][3] == "εἰμί": egoeimi.append(pos[i][0] / N)
    elif pos[i][3] == "εἰμί" and pos[i + 1][3] == "ἐγώ": egoeimi.append(pos[i][0] / N)
egoeimi = sorted(set(round(x, 5) for x in egoeimi))
print(f"   'ego eimi' occurrences in John: {len(egoeimi)} (range {egoeimi[0]:.2f}-{egoeimi[-1]:.2f})")
rob = {}
for name, vv in variants.items():
    ps = sorted(at(c, v) for c, v in vv); s = sym_err(ps)
    pu = sum(sym_err(sorted(rng.random() for _ in range(7))) <= s for _ in range(R)) / R
    pe = sum(sym_err(sorted(rng.sample(egoeimi, 7))) <= s for _ in range(R)) / R
    rob[name] = dict(symmetry_error=round(s, 3), middle=round(ps[3], 3), p_uniform=pu, p_ego_eimi_pool=pe)
    print(f"   {name:34s} middle {ps[3]:.3f}  error {s:.3f}  p(uniform) {pu:.3f}  p(any 7 'I am' phrases) {pe:.3f}")
out["I am robustness"] = rob
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "john_book_results.json"), "w"), ensure_ascii=False, indent=1)
