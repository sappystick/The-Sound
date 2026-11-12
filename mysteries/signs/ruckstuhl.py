#!/usr/bin/env python3
"""Pre-registered test 3 (PREREGISTRATION_3.md): are the evangelist's characteristics (Ruckstuhl / Schweizer) thinner
in the sign stories? Usage: python3 ruckstuhl.py <sblgnt dir>"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(79)
def nrm(w): w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in w if not unicodedata.combining(c)).replace("ς", "σ"))
def load(book):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{book}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(pos=p[1], parse=p[2], lem=nrm(p[6])))
    return V
SOURCE = [((2, 1), (2, 11)), ((4, 46), (4, 54)), ((5, 2), (5, 9)), ((6, 1), (6, 14)), ((6, 16), (6, 21)), ((9, 1), (9, 7)), ((11, 1), (11, 44)), ((21, 1), (21, 14))]
MARK = [((1, 29), (1, 31)), ((1, 40), (1, 45)), ((2, 1), (2, 12)), ((4, 35), (4, 41)), ((5, 21), (5, 43)), ((6, 32), (6, 44)), ((6, 45), (6, 52)), ((8, 22), (8, 26))]
CH = ["ekeinos", "hina", "oun", "emos", "ide", "amen_amen", "kathos", "apekrithe_kai_eipen", "all_hina", "tote_oun", "partitive_ek"]
def counts(t):
    L = [x["lem"] for x in t]; c = dict.fromkeys(CH, 0)
    for k, lem in (("ekeinos", "εκεινοσ"), ("hina", "ινα"), ("oun", "ουν"), ("emos", "εμοσ"), ("ide", "ιδε"), ("kathos", "καθωσ")): c[k] = L.count(lem)
    for i in range(len(t)):
        if L[i] == "αμην" and i + 1 < len(t) and L[i + 1] == "αμην": c["amen_amen"] += 1
        if L[i] == "αποκρινομαι" and any(L[j] == "και" and j + 1 < len(t) and L[j + 1] == "λεγω" for j in range(i + 1, min(len(t), i + 4))): c["apekrithe_kai_eipen"] += 1
        if L[i] == "αλλα" and "ινα" in L[i + 1:i + 3]: c["all_hina"] += 1
        if L[i] == "τοτε" and i + 1 < len(t) and L[i + 1] == "ουν": c["tote_oun"] += 1
        if L[i] == "εκ" and i + 1 < len(t) and t[i + 1]["pos"] == "RA" and len(t[i + 1]["parse"]) > 5 and t[i + 1]["parse"][4:6] == "GP": c["partitive_ek"] += 1
    return c
def narrative(t): return not any((x["pos"].startswith("V") and x["parse"][0] in "12") or x["lem"] in ("εγω", "συ", "ημεισ", "υμεισ") for x in t)
def rows(V): return [(k, counts(t), len(t), narrative(t)) for k, t in V.items()]
JR, MR = rows(load("Jn")), rows(load("Mk")); jk, mk = [r[0] for r in JR], [r[0] for r in MR]
def span(keys, a, b): return list(range(keys.index(a), keys.index(b) + 1))
def rate(blocks, R):
    tot = collections.Counter(); w = 0
    for b in blocks:
        for i in b: tot.update(R[i][1]); w += R[i][2]
    return sum(tot.values()) / w * 100, {f: tot[f] / w * 100 for f in CH}
src_idx = set(i for a, b in SOURCE for i in span(jk, a, b)); ok_pool = np.array([i not in src_idx and jk[i] >= (1, 19) for i in range(len(jk))])
narr = np.array([r[3] for r in JR], float)
def test(blocks, R):
    cands = []
    for b in blocks:
        L = len(b); share = np.mean([R[i][3] for i in b])
        ok = [s for s in range(len(jk) - L + 1) if ok_pool[s:s + L].all() and abs(narr[s:s + L].mean() - share) <= 0.15]
        cands.append((L, ok))
    obs, per = rate(blocks, R); null = []; nper = []
    for _ in range(5000):
        bl = [list(range(s, s + L)) for L, ok in cands for s in [ok[rng.integers(len(ok))]]]
        r, pr = rate(bl, JR); null.append(r); nper.append(pr)
    null = np.array(null); p = float((np.sum(null <= obs) + 1) / (len(null) + 1))
    return dict(composite_per_100=round(obs, 2), null_mean=round(float(null.mean()), 2), null_5pct=round(float(np.percentile(null, 5)), 2), p_one_sided_lower=round(p, 4),
                per_characteristic=({f: [round(per[f], 2), round(float(np.mean([n[f] for n in nper])), 2)] for f in CH}))
R = dict(signs=test([span(jk, a, b) for a, b in SOURCE], JR), power_mark=test([span(mk, a, b) for a, b in MARK], MR))
R["signs_without_21"] = test([span(jk, a, b) for a, b in SOURCE if a[0] != 21], JR)
pw = R["power_mark"]["p_one_sided_lower"] < 0.01; sp = R["signs"]["p_one_sided_lower"]
R["decision"] = ("CHARACTERISTICS THINNED (supports a source)" if sp < 0.05 else "EVANGELIST'S STYLE PRESENT") if pw else "INCONCLUSIVE (power failed)"
json.dump(R, open(os.path.join(HERE, "ruckstuhl_results.json"), "w"), indent=1, ensure_ascii=False)
for k in ("signs", "signs_without_21", "power_mark"):
    r = R[k]; print(f"{k:18s} composite {r['composite_per_100']:5.2f} /100 words  null {r['null_mean']:5.2f} (5% {r['null_5pct']})  p(lower) {r['p_one_sided_lower']}")
    print("   per characteristic [observed, null]:", r["per_characteristic"])
print("DECISION:", R["decision"])
