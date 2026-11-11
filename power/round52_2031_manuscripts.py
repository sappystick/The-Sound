#!/usr/bin/env python3
"""Round 52. Pre-registered test (robustness/PREREG_R52.md, commit e7f7c5d): is John 10:11 at the centre of
John 1:1-20:31 measured in manuscript lines of Sinaiticus (01) and Vaticanus (03)? Secondary: 02, 04, 05, 032.
Usage: python3 power/round52_2031_manuscripts.py
"""
import json, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
rng = np.random.default_rng(52)
SIMS = np.sort(rng.random((400000, 7)), axis=1)[:, 3]
def p_mid(x): return float((np.abs(SIMS - 0.5) <= abs(x - 0.5)).mean())
# the verse list of 1:1-20:31 from SBLGNT (coverage reference)
REF = []
for l in open(os.path.join(ROOT, "sources/texts/sblgnt/64-Jn-morphgnt.txt"), encoding="utf-8"):
    r = (int(l[2:4]), int(l[4:6]))
    if r <= (20, 31) and (not REF or REF[-1] != r): REF.append(r)
def run(ms):
    f = os.path.join(ROOT, "sources/texts/cntr/class 1", f"{ms}.txt")
    if not os.path.exists(f): return dict(available=False)
    seq = []
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) < 2 or not p[0].startswith("43"): continue
        r = (int(p[0][2:5]), int(p[0][5:8]))
        if r <= (20, 31): seq.append((r, len(re.findall(r"[/|\\]", p[1]))))
    have = {r for r, _ in seq}; cov = len(have & set(REF)) / len(REF)
    pa = [(r, n) for r, n in seq if (7, 53) <= r <= (8, 11) and r != (8, 12)]
    def pos(s):
        tot = sum(n for _, n in s); c = 0
        for r, n in s:
            if r == (10, 11): return (c + n / 2) / tot, tot
            c += n
        return None, tot
    x, tot = pos(seq); res = dict(available=True, coverage=round(cov, 4), lines=tot, has_7_53_8_11=bool(pa))
    if x is not None: res.update(position=round(x, 4), p=round(p_mid(x), 4))
    if pa:
        y, t2 = pos([(r, n) for r, n in seq if not ((7, 53) <= r <= (8, 11))]); res.update(without_7_53_8_11=dict(position=round(y, 4), p=round(p_mid(y), 4)))
    tot = sum(n for _, n in seq); c = 0
    for r, n in seq:
        if c + n >= tot / 2: res["centre_verse"] = f"{r[0]}:{r[1]}"; break
        c += n
    return res
out = {"preregistration": "robustness/PREREG_R52.md (commit e7f7c5d)"}
for ms in ("01", "03"): out[ms] = run(ms)
out["H1_pass"] = all(out[m].get("p", 1) < 0.05 for m in ("01", "03"))
out["secondary"] = {}
for ms in ("02", "04", "05", "032"):
    r = run(ms); r["used"] = r.get("available") and r.get("coverage", 0) >= 0.95; out["secondary"][ms] = r
json.dump(out, open(os.path.join(HERE, "round52_results.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
