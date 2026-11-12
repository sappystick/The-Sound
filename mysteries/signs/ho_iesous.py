#!/usr/bin/env python3
"""Pre-registration 2 (PREREGISTRATION_2.md): articular Ἰησοῦς as a Signs Source marker. Usage: python3 ho_iesous.py <sblgnt dir>"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(75)
def nrm(w): w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in w if not unicodedata.combining(c)).replace("ς", "σ"))
POST = {"δε", "ουν", "γαρ", "μεν", "τε"}
def load(book):
    V = collections.OrderedDict(); toks = []
    for l in open(glob.glob(os.path.join(SBL, f"*-{book}-*"))[0], encoding="utf-8"):
        p = l.split(); toks.append(((int(p[0][2:4]), int(p[0][4:6])), p[1], p[2], nrm(p[6])))
    for k, (v, pos, par, lem) in enumerate(toks):
        n, a = V.setdefault(v, [0, 0])
        if lem == "ιησουσ":
            case = par[4]; prev = [toks[j] for j in (k - 1, k - 2) if j >= 0]
            art = (prev and prev[0][1] == "RA" and prev[0][2][4] == case) or (len(prev) == 2 and prev[0][3] in POST and prev[1][1] == "RA" and prev[1][2][4] == case)
            V[v][0] += 1; V[v][1] += int(bool(art))
    return list(V.keys()), np.array([V[k] for k in V])
def idx(keys, spans): return sorted({i for a, b in spans for i in range(keys.index(a), keys.index(b) + 1)})
def blocks(keys, spans): return [list(range(keys.index(a), keys.index(b) + 1)) for a, b in spans]
def test(keys, C, target_spans, exclude, N=10000):
    T = blocks(keys, target_spans); excl = set(exclude); pool_ok = np.array([i not in excl for i in range(len(keys))])
    tn, ta = sum(C[i][0] for b in T for i in b), sum(C[i][1] for b in T for i in b); obs = ta / tn if tn else float("nan")
    starts = {}
    for b in T:
        L = len(b); starts[L] = [s for s in range(len(keys) - L + 1) if pool_ok[s:s + L].all()]
    null = []
    for _ in range(N):
        n = a = 0
        for b in T:
            ss = starts[len(b)]; s = ss[rng.integers(len(ss))]; n += C[s:s + len(b), 0].sum(); a += C[s:s + len(b), 1].sum()
        null.append(a / n if n else np.nan)
    null = np.array([x for x in null if x == x])
    pool_n, pool_a = C[pool_ok, 0].sum(), C[pool_ok, 1].sum()
    return dict(target_occurrences=int(tn), target_articular=int(ta), target_share=round(obs, 3), pool_share=round(pool_a / pool_n, 3), null_mean=round(float(null.mean()), 3),
                p_greater=round(float((np.sum(null >= obs) + 1) / (len(null) + 1)), 4), p_two_sided=round(float((np.sum(np.abs(null - null.mean()) >= abs(obs - null.mean())) + 1) / (len(null) + 1)), 4))
R = {}
jk, JC = load("Jn")
CORE = [((2, 1), (2, 11)), ((4, 46), (4, 54)), ((5, 2), (5, 9)), ((6, 1), (6, 14)), ((6, 16), (6, 21)), ((9, 1), (9, 7)), ((11, 1), (11, 44)), ((21, 1), (21, 14))]
EXT = [((1, 19), (1, 49)), ((2, 14), (2, 19)), ((4, 4), (4, 42)), ((12, 1), (12, 15)), ((18, 1), (19, 42)), ((20, 1), (20, 20))]
prologue = idx(jk, [((1, 1), (1, 18))])
R["T1_core_refined"] = test(jk, JC, CORE, set(idx(jk, CORE)) | set(prologue))
R["T2_extended_source"] = test(jk, JC, EXT, set(idx(jk, CORE + EXT)) | set(prologue))
MIR = {"Mt": [((8, 1), (8, 4)), ((8, 5), (8, 13)), ((8, 14), (8, 15)), ((8, 23), (8, 27)), ((8, 28), (8, 34)), ((9, 1), (9, 8)), ((9, 18), (9, 26)), ((9, 27), (9, 31)), ((14, 13), (14, 21)), ((14, 22), (14, 33)), ((15, 32), (15, 39)), ((20, 29), (20, 34))],
       "Mk": [((1, 29), (1, 31)), ((1, 40), (1, 45)), ((2, 1), (2, 12)), ((4, 35), (4, 41)), ((5, 1), (5, 20)), ((5, 21), (5, 43)), ((6, 32), (6, 44)), ((6, 45), (6, 52)), ((8, 1), (8, 10)), ((8, 22), (8, 26)), ((10, 46), (10, 52))],
       "Lk": [((4, 38), (4, 39)), ((5, 12), (5, 16)), ((5, 17), (5, 26)), ((7, 1), (7, 10)), ((7, 11), (7, 17)), ((8, 22), (8, 25)), ((8, 40), (8, 56)), ((9, 10), (9, 17)), ((13, 10), (13, 17)), ((18, 35), (18, 43))]}
R["T3_genre"] = {}
for b, sp in MIR.items():
    k, C = load(b); R["T3_genre"][b] = test(k, C, sp, idx(k, sp))
syn_genre = sum(1 for v in R["T3_genre"].values() if v["p_greater"] < 0.05)
t2 = R["T2_extended_source"]["p_greater"] < 0.05
R["decision"] = "SOURCE MARKER SUPPORTED" if t2 and syn_genre < 2 else ("GENRE EXPLANATION" if syn_genre >= 2 else "NOT SUPPORTED / INCONCLUSIVE")
R["decision_inputs"] = dict(T2_significant=t2, synoptics_with_significant_genre_effect=syn_genre)
# descriptive: where in John is Jesus anarthrous?
an = [f"{jk[i][0]}:{jk[i][1]}" for i in range(len(jk)) if JC[i][0] > JC[i][1]]
R["john_verses_with_anarthrous_jesus"] = an
json.dump(R, open(os.path.join(HERE, "ho_iesous_results.json"), "w"), indent=1, ensure_ascii=False, default=str)
for k in ("T1_core_refined", "T2_extended_source"): print(k, R[k])
for b, v in R["T3_genre"].items(): print("T3", b, v)
print("DECISION:", R["decision"], R["decision_inputs"]); print("anarthrous Jesus in John:", len(an), "verses:", " ".join(an))
