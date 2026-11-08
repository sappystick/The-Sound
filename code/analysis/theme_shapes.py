#!/usr/bin/env python3
"""Do John's great themes make shapes?

For each theme (fixed list, chosen before running), its occurrences are placed on John's spoken timeline.
 1. RING: are the occurrences mirrored around John's spoken midpoint (as the 'I am' sayings were)?
 2. REGULAR SHAPE: are they spaced more evenly than chance (points of a regular polygon on a circle)?
 3. CLUSTER: are they bunched into one stretch (a single 'node')?
    Null for all three: the same number of occurrences dropped at random verses of John (5,000 draws).
    With 15 themes x 3 tests, about 2 results will pass p < .05 by luck; Bonferroni threshold p < .0011.
 4. ARCHIMEDES TEST: 153 sits in Archimedes' ratio 265/153 for the square root of 3. Do the counts of John's
    theme words form ratios close to sqrt2, sqrt3, phi, pi or e more often than counts of random John words?
 5. COUNTS: are theme counts triangular / multiples of 7 more often than all John words with 10+ uses?
Usage: python3 theme_shapes.py <sblgnt dir>
"""
import collections, json, math, os, random, re, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(17); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
cache = {}
def syl(w):
    if w not in cache:
        try: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
        except Exception: cache[w] = 1
    return cache[w]
toks = [((int(l[2:4]), int(l[4:6])), nrm(l.split()[4]), nrm(l.split()[6])) for l in open(os.path.join(SBL, "64-Jn-morphgnt.txt"), encoding="utf-8")]
T = sum(syl(w) for _, w, _ in toks); acc = 0; vpos = {}; tokpos = []
for r, w, l in toks:
    vpos.setdefault(r, acc / T); tokpos.append(acc / T); acc += syl(w)
VERSES = sorted(vpos.values())
THEMES = {"light (phos)": ["φωσ"], "darkness (skotia/skotos)": ["σκοτια", "σκοτοσ"], "water (hydor)": ["υδωρ"], "spirit / breath (pneuma)": ["πνευμα"],
          "bread (artos)": ["αρτοσ"], "life (zoe)": ["ζωη"], "glory (doxa)": ["δοξα"], "hour (hora)": ["ωρα"], "abide (meno)": ["μενω"],
          "sign (semeion)": ["σημειον"], "truth (aletheia)": ["αληθεια"], "world (kosmos)": ["κοσμοσ"], "love (agapao/agape)": ["αγαπαω", "αγαπη"],
          "witness (martyria/martyreo)": ["μαρτυρια", "μαρτυρεω"], "sent (pempo/apostello)": ["πεμπω", "αποστελλω"]}
def positions(lems):
    seen = set(); ps = []
    for (r, w, l), p in zip(toks, tokpos):
        if l in lems and r not in seen: seen.add(r); ps.append(vpos[r])
    return np.array(sorted(ps))
def ring(ps):
    n = len(ps); return float(np.mean([abs((ps[i] - .5) + (ps[n - 1 - i] - .5)) for i in range(n // 2)]))
def even(ps):
    g = np.diff(np.concatenate([ps, [ps[0] + 1]])); return float(np.std(g) / np.mean(g))
def cluster(ps):
    return float(np.min([ps[i + len(ps) // 2] - ps[i] for i in range(len(ps) - len(ps) // 2)]))   # shortest stretch holding half
VA = np.array(VERSES)
res = {}
print("THEME SHAPES IN JOHN (p = share of random placements as extreme)")
for th, lems in THEMES.items():
    ps = positions(set(lems)); n = len(ps)
    if n < 6: continue
    R, Ev, C = ring(ps), even(ps), cluster(ps); nr = ne = nc = 0; D = 3000
    for _ in range(D):
        q = np.sort(rng.choice(VA, n, replace=False)); nr += ring(q) <= R; ne += even(q) <= Ev; nc += cluster(q) <= C
    res[th] = dict(n=n, ring_p=nr / D, even_p=ne / D, cluster_p=nc / D, centre=round(float(np.median(ps)), 3))
    flag = " ".join(f"{k}*" for k, v in (("ring", nr / D), ("even", ne / D), ("cluster", nc / D)) if v < .0011)
    print(f"   {th:28s} n={n:3d}  ring p={nr / D:.3f}  even p={ne / D:.3f}  cluster p={nc / D:.3f}  {flag}")
out["themes"] = res
print("   (* survives the correction for 45 tests)")

print("\nARCHIMEDES TEST: theme-word counts vs famous ratios")
CONST = {"sqrt2": math.sqrt(2), "sqrt3": math.sqrt(3), "phi": (1 + 5 ** .5) / 2, "pi": math.pi, "e": math.e}
cnt = collections.Counter(l for _, _, l in toks)
def ratio_hits(counts, tol=0.005):
    h = []
    for i, a in enumerate(counts):
        for b in counts[i + 1:]:
            r = max(a, b) / min(a, b)
            for k, c in CONST.items():
                if abs(r - c) / c < tol: h.append((a, b, k))
    return h
tc = [sum(cnt[l] for l in lems) for lems in THEMES.values()]
real = ratio_hits(tc); pool = [v for v in cnt.values() if v >= 10]
null = [len(ratio_hits(list(rng.choice(pool, len(tc), replace=False)))) for _ in range(3000)]
pa = float(np.mean(np.array(null) >= len(real)))
print(f"   theme counts {dict(zip(THEMES, tc))}")
print(f"   pairs within 0.5% of a famous ratio: {len(real)} {real};  random word sets average {np.mean(null):.1f}; p = {pa:.3f}")
out["archimedes"] = dict(counts=dict(zip(THEMES, tc)), hits=real, null_mean=float(np.mean(null)), p=pa)

print("\nCOUNTS: triangular numbers and sevens")
tri = {n * (n + 1) // 2 for n in range(1, 60)}
allc = [v for v in cnt.values() if v >= 10]
print(f"   theme counts triangular: {[c for c in tc if c in tri]} ({sum(c in tri for c in tc)} of {len(tc)}); all John words with 10+ uses: {np.mean([c in tri for c in allc]):.1%}")
print(f"   theme counts divisible by 7: {[c for c in tc if c % 7 == 0]} ({sum(c % 7 == 0 for c in tc)} of {len(tc)}); all John words: {np.mean([c % 7 == 0 for c in allc]):.1%}")
out["counts"] = dict(tri=[c for c in tc if c in tri], seven=[c for c in tc if c % 7 == 0])
json.dump(out, open(os.path.join(HERE, "theme_shapes_results.json"), "w"), ensure_ascii=False, indent=1)
