#!/usr/bin/env python3
"""Round 92 P: phrase anchors between Currier A and B, as pre-registered in PREREG_92.md.
Usage: python3 mysteries/voynich/anchors.py"""
import collections, json, math, os, sys
import numpy as np
from scipy.stats import norm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zl import load, split, PRE, SUF
HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(92); NSH = 200
P = load()
def pages(I, L): return [p["lines"] for k, p in P.items() if p["I"] == I and p["L"] == L and p["lines"]]
HA, HB, SB = pages("H", "A"), pages("H", "B"), pages("S", "B")
odd, even = (lambda C: C[1::2]), (lambda C: C[0::2])
def ntok(C): return sum(len(l) for p in C for l in p)
def match(C, n):   # random page subset with about n tokens
    out, k = [], 0
    for i in rng.permutation(len(C)):
        if k >= n: break
        out.append(C[i]); k += sum(len(l) for l in C[i])
    return out
# ---- formulas
def learn_rules(A, B):
    fa = collections.Counter(w for p in A for l in p for w in l); fb = collections.Counter(w for p in B for l in p for w in l)
    S = [s for s in SUF] + [""]; Pp = [p for p in PRE] + [""]
    cands = [("s", a, b) for a in S if a for b in S if b != a] + [("p", a, b) for a in Pp if a for b in Pp if b != a]
    def ap(f, rules):
        o = collections.Counter()
        for w, c in f.items(): o[rw(w, rules)] += c
        return o
    def jsd(x, y):
        tx, ty = sum(x.values()), sum(y.values()); d = 0.0
        for w in set(x) | set(y):
            a, b = x[w] / tx, y[w] / ty; m = (a + b) / 2
            d += (a * math.log2(a / m) if a else 0) + (b * math.log2(b / m) if b else 0)
        return d / 2
    rules = []; cur = jsd(fa, fb)
    for _ in range(12):
        best = min(cands, key=lambda r: jsd(ap(fa, rules + [r]), fb)); new = jsd(ap(fa, rules + [best]), fb)
        if new >= cur - 1e-4: break
        rules.append(best); cur = new
    return rules
def rw(w, rules):
    for kind, a, b in rules:
        if kind == "s" and w.endswith(a) and len(w) > len(a): return w[:-len(a)] + b
        if kind == "p" and w.startswith(a) and len(w) > len(a): return b + w[len(a):]
    return w
RULES = learn_rules(even(HA), even(HB))
def skel(w): return "".join(c for c in w if c not in "eoaiy") or "_"
def root(w): return split(w)[1] or "_"
def sclass(w): p, r, s = split(w); return p + r + ("·" if s else "")
F = {"F0 identity": (lambda w, side: w), "F1 rewrite": (lambda w, side: rw(w, RULES) if side == "A" else w), "F2 root": (lambda w, side: root(w)),
     "F3 suffix-class": (lambda w, side: sclass(w)), "F4 skeleton": (lambda w, side: skel(w)),
     "F5 rewrite+skeleton": (lambda w, side: skel(rw(w, RULES) if side == "A" else w)), "F6 root+skeleton": (lambda w, side: skel(root(w)))}
def norm_c(C, f, side): return [[[f(w, side) for w in l] for l in p] for p in C]
def grams(C, n): return collections.Counter(tuple(l[i:i + n]) for p in C for l in p for i in range(len(l) - n + 1))
def shuffled(C):
    flat = [w for p in C for l in p for w in l]; f = list(rng.permutation(flat)); out, k = [], 0
    for p in C:
        q = []
        for l in p: q.append(f[k:k + len(l)]); k += len(l)
        out.append(q)
    return out
def compare(X, Y, n):
    gx, gy = grams(X, n), grams(Y, n); obs = len(set(gx) & set(gy)); shared_null = collections.Counter(); null = []
    for _ in range(NSH):
        a, b = grams(shuffled(X), n), grams(shuffled(Y), n); s = set(a) & set(b); null.append(len(s)); shared_null.update(s)
    null = np.array(null); z = (obs - null.mean()) / (null.std() + 1e-9)
    anchors = sorted([(g, gx[g], gy[g], shared_null[g] / NSH) for g in set(gx) & set(gy) if shared_null[g] / NSH < 0.05], key=lambda t: (t[3], -min(t[1], t[2])))
    return dict(observed=obs, null_mean=round(float(null.mean()), 1), excess=round(obs / max(1e-9, null.mean()), 3), z=round(float(z), 2), p=float(norm.sf(z))), anchors
Aodd, Bodd = odd(HA), odd(HB); nB = ntok(Bodd)
Aceil, Bceil = Aodd, match(even(HA), nB); Sfloor = match(odd(SB), nB)
R = dict(rules=[f"{k}:{a}->{b}" for k, a, b in RULES], tokens=dict(A_odd=ntok(Aodd), B_odd=nB, ceiling_A_even=ntok(Bceil), floor_stars_B=ntok(Sfloor)), results={})
tests = []
for name, f in F.items():
    for n in (2, 3):
        ab, anc = compare(norm_c(Aodd, f, "A"), norm_c(Bodd, f, "B"), n)
        ce, _ = compare(norm_c(Aceil, f, "A"), norm_c(Bceil, f, "A"), n)
        fl, _ = compare(norm_c(Bodd, f, "B"), norm_c(Sfloor, f, "B"), n)
        key = f"{name} | {n}-grams"; R["results"][key] = dict(AB=ab, ceiling=ce, floor=fl, AB_anchors=[dict(phrase=" ".join(g), in_A=a, in_B=b, null_share_prob=pn) for g, a, b, pn in anc[:15]])
        tests.append((key, ab["p"], ab["excess"] >= fl["excess"]))
        print(f"{key:30s} AB excess {ab['excess']:.2f} (z {ab['z']:5.1f})  ceiling {ce['excess']:.2f}  floor {fl['excess']:.2f}   anchors {len(anc)}")
# Holm over 14
order = sorted(tests, key=lambda t: t[1]); m = len(order); passed = {}
for i, (k, p, beats) in enumerate(order):
    if p <= 0.01 / (m - i): passed[k] = beats
    else: break
R["holm_significant"] = list(passed); R["significant_and_beats_floor"] = [k for k, b in passed.items() if b]
R["decision"] = ("SHARED PHRASES BEYOND SYSTEM HABIT (anchors listed) under: " + ", ".join(R["significant_and_beats_floor"])) if R["significant_and_beats_floor"] else "NO PHRASE ANCHORS: A and B share only what two texts of the system share"
best = max(R["results"], key=lambda k: R["results"][k]["AB"]["excess"] / max(1e-9, R["results"][k]["ceiling"]["excess"]))
R["closest_to_ceiling"] = best
print("Holm-significant AB:", R["holm_significant"]); print("DECISION:", R["decision"]); print("closest to ceiling:", best)
json.dump(R, open(os.path.join(HERE, "anchors_results.json"), "w"), indent=1, ensure_ascii=False)
