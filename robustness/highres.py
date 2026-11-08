#!/usr/bin/env python3
"""High-resolution p-values for C24 (John, baseline settings) with 1,000,000 random cut sets, so the result is not limited
by the 1/5,000 floor.  Usage: python3 highres.py <sblgnt dir>"""
import json, os, sys, numpy as np
sys.argv = [sys.argv[0], sys.argv[1], "", "", ""]
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "robustness.py"), encoding="utf-8").read().split("TEXTS = {c: greek(c)")[0]   # reuse definitions only
exec(src)
rng = np.random.default_rng(7); out = {}
for code, outs in (("Jn", ("Brown", "Moloney", "Dodd", "round30")), ("Mk", ("A", "B"))):
    V = greek(code); keys = list(V); n = len(keys); idx = {k: i for i, k in enumerate(keys)}; cuts = segment(greek_mode(V, "full"), 4, 15)
    N = 1_000_000; c = np.sort(rng.integers(15, n - 15, size=(N * 2, 3)), axis=1); ok = (np.diff(c, axis=1) >= 15).all(1); c = c[ok][:N]
    for o in outs:
        ref = np.array([idx[pv(b)] for b in OUT[code][o] if pv(b) in idx])
        dist = lambda cs: np.abs(cs[..., None] - ref).min(-1).mean(-1); real = dist(np.array(cuts)); nd = dist(c)
        p = (np.sum(nd <= real) + 1) / (len(nd) + 1); out[f"{code}/{o}"] = dict(p=float(p), real=float(real), n=int(len(nd)))
        print(f"{code} {o:8s} cuts {[f'{keys[x][0]}:{keys[x][1]}' for x in cuts]} mean dist {real:.2f}  p = {p:.2e}  ({len(nd)} random cut sets)")
json.dump(out, open(os.path.join(HERE, "highres_results.json"), "w"), indent=1)
