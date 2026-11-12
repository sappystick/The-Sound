#!/usr/bin/env python3
"""Signs Gospel source test, exactly as pre-registered in PREREGISTRATION.md (committed before this script).
Usage: python3 signs.py <sblgnt dir>"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(73)
def nrm(w): w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in w if not unicodedata.combining(c)).replace("ς", "σ"))
def load(book):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{book}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(pos=p[1], parse=p[2], lem=nrm(p[6]), w=nrm(p[5])))
    return V
JN, MK = load("Jn"), load("Mk")
SOURCE = [((2, 1), (2, 11)), ((4, 46), (4, 54)), ((5, 2), (5, 9)), ((6, 1), (6, 14)), ((6, 16), (6, 21)), ((9, 1), (9, 7)), ((11, 1), (11, 44)), ((21, 1), (21, 14))]
MARK = [((1, 29), (1, 31)), ((1, 40), (1, 45)), ((2, 1), (2, 12)), ((4, 35), (4, 41)), ((5, 21), (5, 43)), ((6, 32), (6, 44)), ((6, 45), (6, 52)), ((8, 22), (8, 26))]
FEAT = ["oun", "de", "kai", "asyndeton", "hist_present_legei", "ekeinos", "hina", "ho_iesous", "meta_touto", "palin", "ioudaioi", "words_per_verse"]
def verse_counts(toks):
    c = dict.fromkeys(FEAT, 0); lem = [t["lem"] for t in toks]
    c["oun"] = lem.count("ουν"); c["de"] = lem.count("δε"); c["kai"] = lem.count("και"); c["ekeinos"] = lem.count("εκεινοσ"); c["hina"] = lem.count("ινα"); c["palin"] = lem.count("παλιν")
    c["ioudaioi"] = lem.count("ιουδαιοσ"); c["asyndeton"] = int(not any(t["pos"].startswith("C") for t in toks[:3]))
    c["hist_present_legei"] = sum(1 for t in toks if t["lem"] == "λεγω" and t["parse"][0] == "3" and t["parse"][1] == "P" and t["parse"][3] == "I")
    c["ho_iesous"] = sum(1 for a, b in zip(toks, toks[1:]) if a["pos"] == "RA" and b["lem"] == "ιησουσ")
    c["meta_touto"] = sum(1 for a, b in zip(toks, toks[1:]) if a["lem"] == "μετα" and b["lem"] == "ουτοσ")
    return c, len(toks)
def narrative(toks): return not any((t["pos"].startswith("V") and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεισ", "υμεισ") for t in toks)
def rows(V): return [(k, *verse_counts(t), narrative(t)) for k, t in V.items()]
JR = rows(JN); MR = rows(MK); jkeys = [r[0] for r in JR]
def span(keys, a, b): i, j = keys.index(a), keys.index(b); return list(range(i, j + 1))
def rates(blocks, R):
    tot = dict.fromkeys(FEAT, 0.0); words = verses = 0
    for blk in blocks:
        for i in blk:
            c, n = R[i][1], R[i][2]; words += n; verses += 1
            for f in FEAT[:-1]: tot[f] += c[f]
    r = {f: tot[f] / words * 100 for f in FEAT[:-1]}; r["asyndeton"] = tot["asyndeton"] / verses * 100; r["words_per_verse"] = words / verses
    return r
def run(src_blocks, src_rows, use_source, pool=None, exclude=None):
    """src_blocks: index lists into src_rows. Null: matched blocks from the pool (default: John's non-source verses)."""
    PR, pkeys = (JR, jkeys) if pool is None else pool
    if exclude is None: exclude = set(i for b in [span(jkeys, a, b) for a, b in SOURCE if use_source(a)] for i in b)
    src_idx = exclude
    pool_ok = np.array([i not in src_idx and (pool is not None or pkeys[i] >= (1, 19)) for i in range(len(pkeys))])
    narr = np.array([r[3] for r in PR], float); jkeys_ = pkeys
    cands = {}
    for blk in src_blocks:
        L = len(blk); share = np.mean([src_rows[i][3] for i in blk]); ok = []
        for s in range(0, len(jkeys_) - L + 1):
            if pool_ok[s:s + L].all() and abs(narr[s:s + L].mean() - share) <= 0.15: ok.append(s)
        if not ok:   # widen to nearest shares if needed
            allst = [s for s in range(0, len(jkeys_) - L + 1) if pool_ok[s:s + L].all()]
            allst.sort(key=lambda s: abs(narr[s:s + L].mean() - share)); ok = allst[:50]
        cands[tuple(blk)] = (L, ok)
    obs = rates(src_blocks, src_rows); null = []
    for _ in range(5000):
        blocks = [list(range(s, s + L)) for (L, ok) in cands.values() for s in [ok[rng.integers(len(ok))]]]
        null.append(rates(blocks, PR))
    M = {f: np.mean([n[f] for n in null]) for f in FEAT}; SD = {f: np.std([n[f] for n in null]) + 1e-12 for f in FEAT}
    z = {f: (obs[f] - M[f]) / SD[f] for f in FEAT}; Q = sum(v * v for v in z.values())
    Qn = np.array([sum(((n[f] - M[f]) / SD[f]) ** 2 for f in FEAT) for n in null]); p = float((np.sum(Qn >= Q) + 1) / (len(Qn) + 1))
    pf = {f: float(np.mean([abs(n[f] - M[f]) >= abs(obs[f] - M[f]) for n in null])) for f in FEAT}
    # Benjamini-Hochberg over the 12 features
    order = sorted(FEAT, key=lambda f: pf[f]); bh = {}; m = len(FEAT)
    for k, f in enumerate(order): bh[f] = pf[f] <= 0.05 * (k + 1) / m
    for k in range(len(order) - 1, -1, -1):
        if bh[order[k]]:
            for f in order[:k]: bh[f] = True
            break
    return dict(omnibus_Q=round(Q, 2), omnibus_p=round(p, 4), z={f: round(v, 2) for f, v in z.items()}, feature_p={f: round(v, 4) for f, v in pf.items()},
                significant_after_BH=[f for f in FEAT if bh[f]], source_rates={f: round(v, 2) for f, v in obs.items()}, null_mean={f: round(v, 2) for f, v in M.items()},
                source_narrative_share=round(float(np.mean([src_rows[i][3] for b in src_blocks for i in b])), 2))
mkeys = [r[0] for r in MR]
R = {}
R["signs_source"] = run([span(jkeys, a, b) for a, b in SOURCE], JR, lambda a: True)
R["signs_source_without_21"] = run([span(jkeys, a, b) for a, b in SOURCE if a[0] != 21], JR, lambda a: a[0] != 21)
R["power_check_mark"] = run([span(mkeys, a, b) for a, b in MARK], MR, lambda a: True)
# EXPLORATORY (not pre-registered): the genre control. Mark is one author. Do Mark's miracle stories differ from
# Mark's OTHER narrative the same way John's signs differ from John's other narrative? If yes, the "source" signal is genre.
mexcl = set(i for a, b in MARK for i in span(mkeys, a, b)) | set(i for i, k in enumerate(mkeys) if k[0] == 16 and k[1] > 8)
R["exploratory_genre_control_mark_miracles_vs_mark"] = run([span(mkeys, a, b) for a, b in MARK], MR, None, pool=(MR, mkeys), exclude=mexcl)
zj, zm = R["signs_source"]["z"], R["exploratory_genre_control_mark_miracles_vs_mark"]["z"]
R["exploratory_same_direction"] = {f: bool(np.sign(zj[f]) == np.sign(zm[f])) for f in R["signs_source"]["significant_after_BH"]}
# EXPLORATORY sensitivity: drop the two features that could be genre (historic present) or passage-opening
# artefacts (meta touto: 6:1 and 21:1 open source passages)
_full = list(FEAT); FEAT[:] = [f for f in _full if f not in ("hist_present_legei", "meta_touto")]
R["exploratory_without_genre_and_boundary_features"] = run([span(jkeys, a, b) for a, b in SOURCE], JR, lambda a: True)
R["exploratory_power_check_same_features"] = run([span(mkeys, a, b) for a, b in MARK], MR, lambda a: True)
FEAT[:] = _full
pc = R["power_check_mark"]["omnibus_p"] < 0.01; sp = R["signs_source"]["omnibus_p"]
R["decision"] = ("SOURCE DETECTED" if sp < 0.01 and pc else "RUCKSTUHL SUPPORTED (style uniform; method has power)" if sp >= 0.05 and pc else "INCONCLUSIVE") + f" | power check {'passed' if pc else 'FAILED'}"
json.dump(R, open(os.path.join(HERE, "signs_results.json"), "w"), indent=1, ensure_ascii=False)
for k in ("signs_source", "signs_source_without_21", "power_check_mark", "exploratory_genre_control_mark_miracles_vs_mark", "exploratory_without_genre_and_boundary_features", "exploratory_power_check_same_features"):
    r = R[k]; print(f"{k:26s} Q {r['omnibus_Q']:7.2f}  p {r['omnibus_p']:.4f}  narrative share {r['source_narrative_share']}  BH-significant: {r['significant_after_BH']}")
    print("   z:", r["z"])
print("DECISION:", R["decision"]); print("EXPLORATORY: John's signature features in the same direction for Mark's miracles within Mark:", R["exploratory_same_direction"])
