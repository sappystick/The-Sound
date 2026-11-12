#!/usr/bin/env python3
"""Round 93 (PREREG_93.md): coherence at every level, reading direction, page order, pointers.
Usage: python3 mysteries/voynich/coherence.py <macer html> <sblgnt dir> <BSB.csv>"""
import collections, csv, glob, html, json, math, os, re, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zl import load, split
HERE = os.path.dirname(os.path.abspath(__file__)); MAC, SBL, BSB = sys.argv[1:4]; rng = np.random.default_rng(93)
V = load(); ORDER = [k for k, p in V.items() if p["lines"]]; PG = {k: V[k] for k in ORDER}
def toks(k): return [w for l in PG[k]["lines"] for w in l]
def cos(a, b):
    ks = set(a) & set(b); num = sum(a[x] * b[x] for x in ks)
    return num / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())) + 1e-12)
CNT = {k: collections.Counter(toks(k)) for k in ORDER}
def jsd(fa, fb):
    ta, tb = sum(fa.values()), sum(fb.values()); d = 0.0
    for w in set(fa) | set(fb):
        x, y = fa[w] / ta, fb[w] / tb; m = (x + y) / 2
        d += (x * math.log2(x / m) if x else 0) + (y * math.log2(y / m) if y else 0)
    return d / 2
R = {}
# ================= C. coherence
same_sec = collections.defaultdict(list)
for k in ORDER: same_sec[PG[k]["I"]].append(k)
cons = [(a, b) for a, b in zip(ORDER, ORDER[1:]) if PG[a]["I"] == PG[b]["I"]]
obs = np.mean([cos(CNT[a], CNT[b]) for a, b in cons])
def rand_pairs(n):
    out = []
    while len(out) < n:
        a = ORDER[rng.integers(len(ORDER))]; L = same_sec[PG[a]["I"]]
        if len(L) > 1:
            b = L[rng.integers(len(L))]
            if b != a: out.append((a, b))
    return out
null = np.array([np.mean([cos(CNT[a], CNT[b]) for a, b in rand_pairs(len(cons))]) for _ in range(500)])
R["C_body_consecutive_pages"] = dict(consecutive=round(float(obs), 4), random_same_section=round(float(null.mean()), 4), p=round(float((np.sum(null >= obs) + 1) / 501), 4))
def page_halves(pages):
    """pages: list of (key, section, token list). Own halves vs halves of two different same-section pages."""
    H = {k: (collections.Counter(t[:len(t) // 2]), collections.Counter(t[len(t) // 2:]), s) for k, s, t in pages if len(t) >= 40}
    own = np.mean([jsd(a, b) for a, b, _ in H.values()]); bys = collections.defaultdict(list)
    for k, (_, _, s) in H.items(): bys[s].append(k)
    def cross():
        v = []
        for k, (a, _, s) in H.items():
            o = [x for x in bys[s] if x != k]
            if o: v.append(jsd(a, H[o[rng.integers(len(o))]][1]))
        return np.mean(v)
    nl = np.array([cross() for _ in range(200)]); return dict(pages=len(H), own_halves_jsd=round(float(own), 4), cross_page_jsd=round(float(nl.mean()), 4), p=round(float((np.sum(nl <= own) + 1) / 201), 4))
R["C_page_Voynich"] = page_halves([(k, PG[k]["I"], toks(k)) for k in ORDER])
def nrm(w): w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in w if not unicodedata.combining(c)).replace("ς", "σ"))
gj = [w for w in (nrm(l.split()[5]) for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8")) if w]
ej = [w for r in csv.DictReader(open(BSB, encoding="utf-8")) if r["Book"] == "John" for w in re.findall(r"[a-z]+", r["Text"].lower())]
t = open(MAC, encoding="utf-8").read(); mac = re.findall(r"[a-z]+", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S))).lower())
SIZE = int(np.median([len(toks(k)) for k in ORDER]))
def pg(ws): return [ws[i:i + SIZE] for i in range(0, len(ws) - SIZE + 1, SIZE)]
for name, ws in (("Greek John", gj), ("English John", ej), ("Latin Macer", mac)):
    R[f"C_page_{name}"] = page_halves([(i, "x", p) for i, p in enumerate(pg(ws))])
# line cohesion (Voynich): word pairs sharing a root, within a line vs across neighbouring lines
def rt(w): return split(w)[1]
win = acr = nwin = nacr = 0; idw = ida = 0
for k in ORDER:
    L = PG[k]["lines"]
    for i, l in enumerate(L):
        for a in range(len(l)):
            for b in range(a + 1, len(l)): nwin += 1; win += rt(l[a]) == rt(l[b]) and rt(l[a]) != ""; idw += l[a] == l[b]
        if i + 1 < len(L):
            for a in l:
                for b in L[i + 1]: nacr += 1; acr += rt(a) == rt(b) and rt(a) != ""; ida += a == b
R["C_line_root_sharing"] = dict(within_line=round(win / nwin, 4), across_adjacent_lines=round(acr / nacr, 4), identical_within=round(idw / nwin, 4), identical_across=round(ida / nacr, 4),
                                z=round((win / nwin - acr / nacr) / math.sqrt((acr / nacr) * (1 - acr / nacr) / nwin), 2))
# ================= character model (forward / backward), also word coherence
class CharWB:
    def __init__(s, lines, N=4):
        s.N = N; s.c = [collections.defaultdict(collections.Counter) for _ in range(N)]; s.V = set("$")
        for x in lines:
            t = "^" * (N - 1) + x + "$"; s.V |= set(x)
            for i in range(N - 1, len(t)):
                for k in range(N): s.c[k][t[i - k:i]][t[i]] += 1
    def bits(s, x):
        t = "^" * (s.N - 1) + x + "$"; b = 0.0
        for i in range(s.N - 1, len(t)):
            pr = 1 / (len(s.V) + 1); h = t[i - s.N + 1:i]
            for k in range(s.N):
                C = s.c[k].get(h[len(h) - k:] if k else "")
                if C: n = sum(C.values()); tt = len(C); lam = n / (n + tt); pr = lam * C[t[i]] / n + (1 - lam) * pr
            b -= math.log2(pr)
        return b / (len(x) + 1)
def direction(lines_even, lines_odd):
    f = CharWB(lines_even); b = CharWB([x[::-1] for x in lines_even])
    fw = np.mean([f.bits(x) for x in lines_odd]); bw = np.mean([b.bits(x[::-1]) for x in lines_odd])
    return dict(forward_bits_per_glyph=round(float(fw), 4), backward_bits_per_glyph=round(float(bw), 4), asymmetry_backward_minus_forward=round(float(bw - fw), 4))
vl = [" ".join(l) for k in ORDER for l in PG[k]["lines"]]
def chunk_lines(ws, n=8): return [" ".join(ws[i:i + n]) for i in range(0, len(ws) - n + 1, n)]
D = {"Voynich": direction(vl[0::2], vl[1::2])}
for name, ws in (("Greek John", gj), ("English John", ej), ("Latin Macer", mac)):
    L = chunk_lines(ws); D[name] = direction(L[0::2], L[1::2])
R["D1_glyph_direction"] = D
# word coherence: held-out glyph cost of real words vs the same words with glyphs shuffled
vw = [w for k in ORDER for w in toks(k)]; cw = CharWB(vw[0::2])
real = np.mean([cw.bits(w) for w in vw[1::2][:6000]]); shuf = np.mean([cw.bits("".join(rng.permutation(list(w)))) for w in vw[1::2][:6000]])
R["C_word_internal"] = dict(real_bits_per_glyph=round(float(real), 3), glyph_shuffled=round(float(shuf), 3))
# D2 word order forward vs backward (held-out bigram gain, add-one unigram backoff)
def word_dir(pages):
    def gain(P):
        tr, te = P[0::2], P[1::2]; uni = collections.Counter(w for p in tr for w in p); N = sum(uni.values()); Vn = len(uni) + 1
        big = collections.defaultdict(collections.Counter)
        for p in tr:
            for a, b in zip(p, p[1:]): big[a][b] += 1
        pu = lambda w: (uni[w] + 1) / (N + Vn); hu = hb = 0.0; n = 0
        for p in te:
            for a, b in zip(p, p[1:]):
                C = big.get(a); u = pu(b)
                if C: m = sum(C.values()); t_ = len(C); lam = m / (m + t_); pb = lam * C[b] / m + (1 - lam) * u
                else: pb = u
                hu -= math.log2(u); hb -= math.log2(pb); n += 1
        return (hu - hb) / n
    return dict(forward_gain=round(gain(pages), 4), backward_gain=round(gain([p[::-1] for p in pages]), 4))
R["D2_word_direction"] = {"Voynich": word_dir([toks(k) for k in ORDER]), "Greek John": word_dir(pg(gj)), "English John": word_dir(pg(ej)), "Latin Macer": word_dir(pg(mac))}
# D3 vertical reading: words directly above each other
def near(a, b): return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1
pairs = [(l1, l2) for k in ORDER for l1, l2 in zip(PG[k]["lines"], PG[k]["lines"][1:])]
def vert(shift=False):
    same = nr = n = 0
    for l1, l2 in pairs:
        m = min(len(l1), len(l2)); off = rng.integers(1, m) if shift and m > 1 else 0
        for i in range(m):
            a, b = l1[i], l2[(i + off) % len(l2)]; n += 1; same += a == b; nr += near(a, b)
    return same / n, nr / n
vs, vn = vert(); nulls = np.array([vert(True) for _ in range(300)])
R["D3_vertical"] = dict(identical_above=round(vs, 4), null=round(float(nulls[:, 0].mean()), 4), p_identical=round(float((np.sum(nulls[:, 0] >= vs) + 1) / 301), 4),
                        near_above=round(vn, 4), null_near=round(float(nulls[:, 1].mean()), 4), p_near=round(float((np.sum(nulls[:, 1] >= vn) + 1) / 301), 4))
# ================= O. order
rv = [(k, k[:-1] + "v") for k in ORDER if k.endswith("r") and k[:-1] + "v" in PG]
rv = [(a, b) for a, b in rv if PG[a]["I"] == PG[b]["I"]]
o = np.mean([cos(CNT[a], CNT[b]) for a, b in rv]); nl = np.array([np.mean([cos(CNT[a], CNT[b]) for a, b in rand_pairs(len(rv))]) for _ in range(500)])
R["O1_recto_verso"] = dict(pairs=len(rv), same_leaf=round(float(o), 4), random_same_section=round(float(nl.mean()), 4), p=round(float((np.sum(nl >= o) + 1) / 501), 4))
leaf = collections.defaultdict(collections.Counter); leafinfo = {}
for k in ORDER:
    lf = re.match(r"f(\d+)", k).group(1); leaf[lf].update(CNT[k]); leafinfo[lf] = (PG[k]["Q"], PG[k]["B"], PG[k]["F"], PG[k]["I"])
byq = collections.defaultdict(list)
for lf, (q, b, f, i) in leafinfo.items(): byq[q].append(lf)
conj, adj, other = [], [], []
for q, L in byq.items():
    L = sorted(L, key=int)
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            a, b = L[i], L[j]; s = cos(leaf[a], leaf[b])
            if leafinfo[a][1] == leafinfo[b][1]: conj.append(s)
            elif j == i + 1: adj.append(s)
            else: other.append(s)
allq = adj + other; nl = np.array([np.mean(rng.choice(allq, len(conj))) for _ in range(2000)])
R["O2_bifolia"] = dict(conjugate_pairs=len(conj), conjugate_sim=round(float(np.mean(conj)), 4), adjacent_sim=round(float(np.mean(adj)), 4), other_same_quire=round(float(np.mean(other)), 4),
                       p_conjugate_above_same_quire=round(float((np.sum(nl >= np.mean(conj)) + 1) / 2001), 4))
# ================= P. pointers
MAIN = {"H", "B", "S", "P", "C", "Z", "A", "T"}
keys = [k for k in ORDER if PG[k]["I"] in MAIN]; vocab = [w for w, c in collections.Counter(w for k in keys for w in toks(k)).items() if c >= 5]; wi = {w: i for i, w in enumerate(vocab)}
X = np.zeros((len(keys), len(vocab)))
for r, k in enumerate(keys):
    for w in toks(k):
        if w in wi: X[r, wi[w]] += 1
X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12; lab = [PG[k]["I"] for k in keys]
pred = []
for i in range(len(keys)):
    cents = {s: X[[j for j in range(len(keys)) if lab[j] == s and j != i]].mean(0) for s in MAIN if sum(1 for j in range(len(keys)) if lab[j] == s and j != i)}
    pred.append(max(cents, key=lambda s: X[i] @ cents[s]))
def agree(k_):
    idx = [i for i in range(len(keys)) if 0 <= i + k_ < len(keys)]; return np.array([pred[i] == lab[i + k_] for i in idx], float)
offs = {k_: float(agree(k_).mean()) for k_ in range(-6, 7)}; best = max((k_ for k_ in offs if k_ != 0), key=offs.get)
a0, ab = agree(0), agree(best); boots = []
for _ in range(2000):
    s0 = a0[rng.integers(len(a0), size=len(a0))].mean(); sb = ab[rng.integers(len(ab), size=len(ab))].mean(); boots.append(sb - s0)
R["P1_offset"] = dict(agreement_by_offset={str(k_): round(v, 3) for k_, v in offs.items()}, best_nonzero=best, p_best_beats_zero=round(float(np.mean(np.array(boots) <= 0)), 4))
mis = [i for i in range(len(keys)) if pred[i] != lab[i]]
qb = set()
for q in set(PG[k]["Q"] for k in keys):
    ks = [i for i, k in enumerate(keys) if PG[k]["Q"] == q]
    if ks: qb |= {ks[0], ks[-1]}
obsb = sum(1 for i in mis if i in qb); nlb = np.array([sum(1 for i in rng.choice(len(keys), len(mis), replace=False) if i in qb) for _ in range(2000)])
R["P2_misfits"] = dict(misfit_pages=len(mis), of=len(keys), at_quire_boundaries=obsb, null_mean=round(float(nlb.mean()), 2), p=round(float((np.sum(nlb >= obsb) + 1) / 2001), 4),
                       examples=[f"{keys[i]} picture {lab[i]} text reads as {pred[i]}" for i in mis[:20]])
json.dump(R, open(os.path.join(HERE, "coherence_results.json"), "w"), indent=1, ensure_ascii=False)
for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False)[:600])

# EXPLORATORY confound control for O2 (not pre-registered): hands change by bifolium (Davis 2020), so conjugate leaves
# may look alike because the same scribe wrote them. Repeat O2 using only leaf pairs written by the same hand and in the
# same language and section.
lh = {}
for k in ORDER:
    lf = re.match(r"f(\d+)", k).group(1); lh[lf] = (PG[k]["H"], PG[k]["L"], PG[k]["I"])
conj2, pool2 = [], []
for q, L in byq.items():
    L = sorted(L, key=int)
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            a, b = L[i], L[j]
            if lh[a] != lh[b]: continue
            s = cos(leaf[a], leaf[b]); (conj2 if leafinfo[a][1] == leafinfo[b][1] else pool2).append(s)
nl2 = np.array([np.mean(rng.choice(pool2, len(conj2))) for _ in range(2000)]) if conj2 and pool2 else np.array([0])
R["O2_EXPLORATORY_same_hand_language_section"] = dict(conjugate_pairs=len(conj2), conjugate_sim=round(float(np.mean(conj2)), 4), other_pairs=len(pool2), other_sim=round(float(np.mean(pool2)), 4),
    p=round(float((np.sum(nl2 >= np.mean(conj2)) + 1) / (len(nl2) + 1)), 4))
print("O2 same hand/language/section:", R["O2_EXPLORATORY_same_hand_language_section"])
# classifier accuracy for P (to judge whether P2 is interpretable)
R["P_classifier_accuracy"] = round(1 - len(mis) / len(keys), 3); print("classifier accuracy", R["P_classifier_accuracy"])
json.dump(R, open(os.path.join(HERE, "coherence_results.json"), "w"), indent=1, ensure_ascii=False)
