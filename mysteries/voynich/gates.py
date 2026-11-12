#!/usr/bin/env python3
"""Round 83: the 231-gates test (Angle I of the plan). Is the Voynich a combinatorial letter-system, and if so of
which kind?

Sefer Yetzirah (round 39): 231 'gates' = the C(22,2) unordered adjacent letter-pairs. Its gates are explicitly
BI-DIRECTIONAL: 'two stones build two houses' - the pair alef-bet is the same gate read either way (ab = ba). A free
letter-combination system therefore has (i) high gate occupancy (most pairs occur) and (ii) high reciprocity (if ab
occurs, ba occurs). A DIRECTIONAL SLOT system (prefix -> core -> suffix) is the opposite: glyphs sit at fixed
positions, so transitions mostly go forward (high positional layering) and reciprocity is LOW (ab occurs, ba does not).
This test adjudicates between the two combination models for the Voynich.

Metrics per corpus (within-word adjacency only):
  n             alphabet size (distinct glyphs)
  occupancy     distinct unordered adjacent pairs / C(n,2)          free-combination -> high
  directed_den  distinct ordered pairs / n^2
  reciprocity   share of occurring ordered pairs whose reverse also occurs (weighted)   free -> high, slot -> low
  layering      share of adjacency weight going 'forward' when glyphs are ordered by mean within-word position
                                                                     slot/DAG -> high (~1), free/symmetric -> ~0.5
  branch_H      mean next-glyph conditional entropy (bits)          rigid gates -> low
Corpora: VOY (ZL3b), HEB (WLC = Sefer Yetzirah's own language), SY (the Sefer Yetzirah text itself), LAT (Geber),
  GRK, KANON (a known slot language), FREE (synthetic all-pairs over 12 symbols), SLOT (synthetic prefix/core/suffix DAG).
Usage: python3 mysteries/voynich/gates.py
"""
import collections, glob, json, math, os, re, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
rng = np.random.default_rng(83)

def voy_words():
    ws = []
    for ln in open(os.path.join(T, "voynich/ZL3b-n.txt"), encoding="utf-8", errors="replace"):
        if not re.match(r"<f\d+[rv]\d*\.", ln): continue
        body = ln.split(">", 1)[1] if ">" in ln else ""
        body = re.sub(r"\{[^}]*\}", "", body); body = re.sub(r"<[^>]*>", "", body); body = re.sub(r"[!*%?\[\]@]", "", body)
        ws += [w for w in re.split(r"[.\s]+", body.strip()) if w and re.search(r"[a-zA-Z]", w)]
    return ws

def heb_words(lo=40000):
    ws = []
    for f in sorted(glob.glob(os.path.join(T, "morphhb/wlc/*.xml"))):
        for m in re.finditer(r"<w[^>]*>(.*?)</w>", open(f, encoding="utf-8").read()):
            w = re.sub(r"[^א-ת]", "", re.sub(r"<[^>]+>", "", m.group(1)))
            if w: ws.append(w)
            if len(ws) > lo: return ws
    return ws

def sy_words():
    ws = []
    for f in sorted(glob.glob(os.path.join(T, "sefer_yetzirah/sy*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        def walk(x):
            if isinstance(x, str): ws.extend(re.sub(r"[^א-ת ]", " ", x).split())
            elif isinstance(x, list): [walk(y) for y in x]
            elif isinstance(x, dict): [walk(v) for v in x.values()]
        walk(d.get("text", d))
    return [w for w in ws if w]

def lat_words(path, lo=40000):
    t = re.sub(r"[^a-z\s]", " ", open(path, encoding="utf-8", errors="ignore").read().lower())
    return [w for w in t.split() if 2 <= len(w) <= 20 and re.search(r"[aeiou]", w)][:lo]

def grk_words(lo=40000):
    ws = []
    for f in sorted(glob.glob(os.path.join(T, "sblgnt/*-morphgnt.txt"))):
        for l in open(f, encoding="utf-8"):
            w = unicodedata.normalize("NFD", l.split()[3].lower()); w = "".join(c for c in w if not unicodedata.combining(c))
            w = re.sub(r"[^α-ω]", "", w)
            if w: ws.append(w)
            if len(ws) > lo: return ws
    return ws

def kanon_words(n=8000):
    C, V = "ktpbdglmnrsh", "aeyiouw"
    return ["".join(C[rng.integers(12)] + V[rng.integers(7)] for _ in range(int(rng.integers(1, 4)))) + (V[rng.integers(7)] if rng.random() < .3 else "") for _ in range(n)]

def free_words(n=8000):           # synthetic FREE combination: any of 12 symbols in any order
    A = "abcdefghijkl"
    return ["".join(A[rng.integers(12)] for _ in range(int(rng.integers(2, 7)))) for _ in range(n)]

def slot_words(n=8000):           # synthetic directional SLOT DAG: disjoint prefix/core/suffix inventories
    P, Cc, S = ["qo", "ch", "ok", "da"], ["ke", "te", "ol", "ai", "or"], ["dy", "in", "ey", "ar"]
    return [P[rng.integers(4)] + Cc[rng.integers(5)] + S[rng.integers(4)] for _ in range(n)]

def metrics(words):
    uni = collections.Counter(c for w in words for c in w)
    alpha = sorted(uni); n = len(alpha); idx = {c: i for i, c in enumerate(alpha)}
    pos = collections.defaultdict(list)
    O = np.zeros((n, n))                      # ordered adjacency counts
    for w in words:
        L = len(w)
        for k, c in enumerate(w): pos[c].append(k / max(1, L - 1))
        for a, b in zip(w, w[1:]):
            if a != b: O[idx[a], idx[b]] += 1
    occ_pairs = set()
    for i in range(n):
        for j in range(n):
            if O[i, j] > 0 and i != j: occ_pairs.add(frozenset((i, j)))
    occupancy = len(occ_pairs) / (n * (n - 1) / 2)
    directed = int((O > 0).sum()) / (n * n)
    # reciprocity (weighted): of total forward+back weight on used ordered pairs, how much has a nonzero reverse
    used = O > 0; recip_w = O[used & used.T].sum() / (O[used].sum() + 1e-9)
    # layering: order glyphs by mean within-word position; forward edge share by weight
    mp = {c: np.mean(pos[c]) for c in alpha}; order = {c: r for r, c in enumerate(sorted(alpha, key=lambda c: mp[c]))}
    fwd = bwd = 0.0
    for i in range(n):
        for j in range(n):
            if O[i, j] > 0:
                if order[alpha[i]] < order[alpha[j]]: fwd += O[i, j]
                elif order[alpha[i]] > order[alpha[j]]: bwd += O[i, j]
    layering = fwd / (fwd + bwd + 1e-9)
    # branching: mean conditional next-glyph entropy
    H = []
    for i in range(n):
        row = O[i]; s = row.sum()
        if s > 0:
            p = row[row > 0] / s; H.append(-np.sum(p * np.log2(p)))
    return dict(n=n, occupancy=round(occupancy, 3), directed_density=round(directed, 3),
                reciprocity=round(float(recip_w), 3), layering=round(float(layering), 3),
                branch_H=round(float(np.mean(H)), 3))

CORP = {
 "VOY": voy_words(), "HEB": heb_words(), "SY": sy_words(),
 "LAT": lat_words(os.path.join(T, "alchemy/geberisphilosoph00gebe.txt")),
 "GRK": grk_words(), "KANON": kanon_words(), "FREE": free_words(), "SLOT": slot_words()}
res = {k: metrics(v) for k, v in CORP.items()}

# classify VOY by nearest synthetic model on (occupancy, reciprocity, layering)
def vec(k): return np.array([res[k]["occupancy"], res[k]["reciprocity"], res[k]["layering"]])
d_free = float(np.linalg.norm(vec("VOY") - vec("FREE"))); d_slot = float(np.linalg.norm(vec("VOY") - vec("SLOT")))
out = dict(metrics=res, sizes={k: len(v) for k, v in CORP.items()},
    voynich_vs_models=dict(distance_to_FREE_combination=round(d_free, 3), distance_to_SLOT_directional=round(d_slot, 3),
        verdict=("directional slot" if d_slot < d_free else "free combination")),
    interpretation=("Sefer Yetzirah's 231 gates are a FREE, bi-directional letter-combination (high occupancy + high "
        "reciprocity, no layering). A directional SLOT grammar is the opposite (high layering, low reciprocity). "
        "Whichever the Voynich is nearer tells us which combinatorial idea generated it."))
json.dump(out, open(os.path.join(HERE, "gates_results.json"), "w"), indent=1)
cols = list(CORP)
print(f"{'metric':<16}" + "".join(f"{k:>8}" for k in cols))
for m in ("n", "occupancy", "directed_density", "reciprocity", "layering", "branch_H"):
    print(f"{m:<16}" + "".join(f"{res[k][m]:>8}" for k in cols))
print("\nVOY nearest model:", out["voynich_vs_models"])
