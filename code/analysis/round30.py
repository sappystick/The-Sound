#!/usr/bin/env python3
"""Round 30: John's section structure from the text alone, in 4 to 8 parts.

Optimal segmentation (dynamic programming, minimum within-section variance, sections of at least 15 verses) of two
signals that know nothing of chapters or outlines:
  MODE  = discourse - action per verse (1st/2nd person vs 3rd-person narrative verbs), as in rounds 27-29;
  WORDS = each verse's content vocabulary (IDF-weighted lemmas, 40 latent dimensions), so a cut = a change of subject.
Each cut set is compared with a standard commentators' outline of John (1:19, 2:1, 5:1, 6:1, 7:1, 9:1, 10:22, 11:1, 12:12,
13:1, 13:31, 18:1, 20:1, 21:1) and with chapter starts (a later readers' division): mean distance of cuts to the nearest
break and hits within 3 verses, against 5,000 random cut sets of the same size and minimum length.
Each section is named by its own most distinctive words (no labels supplied).
Usage: python3 round30.py <sblgnt dir>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(30); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
V = collections.OrderedDict()
for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"):
    p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(lem=nrm(p[6]), pos=p[1], parse=p[2]))
keys = list(V); n = len(keys); lab = lambda i: f"{keys[i][0]}:{keys[i][1]}"
# signals
d, a = [], []
for v in V.values():
    m = len(v); speech = any(u["pos"][0] == "V" and u["parse"][0] in "12" for u in v)
    d.append(sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in v) / m)
    a.append(sum(t["pos"][0] == "V" and t["parse"][0] == "3" and t["parse"][3] == "I" and t["parse"][1] in "AIP" and not speech for t in v) / m)
d, a = np.array(d), np.array(a); MODE = ((d - d.mean()) / d.std() - (a - a.mean()) / a.std())[:, None]
STOP = set("ο και αυτος δε εν ειμι λεγω ου μη γαρ ουν οτι εγω συ ουτος εκεινος τις ινα προς εκ εις απο επι δια μετα περι αλλα ως καθως ημεις υμεις εαν αν οστις παρα υπο ηδη ετι ουδε τε η ποιεω εχω γινομαι ερχομαι".split())
docs = [[t["lem"] for t in V[k] if t["pos"][0] in "NVA" and t["lem"] not in STOP] for k in keys]
df = collections.Counter(l for x in docs for l in set(x)); vocab = {l: i for i, l in enumerate(df)}; idf = np.array([math.log(n / df[l]) for l in vocab])
X = np.zeros((n, len(vocab)))
for i, x in enumerate(docs):
    for l in x: X[i, vocab[l]] += 1
Xw = X * idf; Xw /= np.maximum(1e-9, np.linalg.norm(Xw, axis=1, keepdims=True))
U, S, _ = np.linalg.svd(Xw - Xw.mean(0), full_matrices=False); WORDS = U[:, :40] * S[:40]
# smooth words lightly (a verse is short); 5-verse window
WORDS = np.array([np.convolve(np.pad(WORDS[:, c], 2, mode="edge"), np.ones(5) / 5, mode="valid") for c in range(WORDS.shape[1])]).T
def segment(Y, k, minseg=15):
    c = np.vstack([np.zeros(Y.shape[1]), np.cumsum(Y, 0)]); c2 = np.concatenate([[0], np.cumsum((Y * Y).sum(1))])
    def cost(i, js):     # SSE of Y[i:j] for vector of j
        s = c[js] - c[i]; return (c2[js] - c2[i]) - (s * s).sum(1) / (js - i)
    INF = np.inf; D = np.full((k + 1, n + 1), INF); B = np.zeros((k + 1, n + 1), int); D[0, 0] = 0
    for s in range(1, k + 1):
        for i in range(n):
            if D[s - 1, i] == INF: continue
            js = np.arange(i + minseg, n + 1)
            if not len(js): continue
            v = D[s - 1, i] + cost(i, js); better = v < D[s, js]; D[s, js[better]] = v[better]; B[s, js[better]] = i
    cuts, j = [], n
    for s in range(k, 0, -1): j = B[s, j]; cuts.append(j)
    return sorted(cuts)[1:]
OUTLINE = [(1, 19), (2, 1), (5, 1), (6, 1), (7, 1), (9, 1), (10, 22), (11, 1), (12, 12), (13, 1), (13, 31), (18, 1), (20, 1), (21, 1)]
OL = [keys.index(k) for k in OUTLINE]; CH = [i for i, k in enumerate(keys) if k[1] == 1 and k[0] > 1]
def score(cuts, ref): dd = [min(abs(c - r) for r in ref) for c in cuts]; return float(np.mean(dd)), sum(x <= 3 for x in dd)
def rand_cuts(k, minseg=15):
    while True:
        c = sorted(rng.choice(np.arange(minseg, n - minseg), k - 1, replace=False))
        if all(b - a >= minseg for a, b in zip(c, c[1:])): return c
def name(i, j, top=4):
    sub = X[i:j].sum(0); rest = X.sum(0) - sub; ns, nr = sub.sum(), rest.sum()
    lo = (sub + 0.5) / (ns + 0.5 * len(vocab)); lr = (rest + 0.5) / (nr + 0.5 * len(vocab)); z = np.log(lo / lr) * np.sqrt(sub)
    inv = {v: k for k, v in vocab.items()}; return ", ".join(inv[q] for q in np.argsort(-z)[:top])
for sig, Y in (("MODE", MODE), ("WORDS", WORDS)):
    print(f"\n{sig} signal")
    for k in range(4, 9):
        cuts = segment(Y, k); mo, ho = score(cuts, OL); mc, hc = score(cuts, CH)
        nul = [rand_cuts(k) for _ in range(5000)]; no = np.array([score(c, OL) for c in nul]); nc = np.array([score(c, CH) for c in nul])
        po = float(np.mean(no[:, 0] <= mo)); pc = float(np.mean(nc[:, 0] <= mc))
        print(f"  {k} parts: cuts {' '.join(lab(c) for c in cuts)}")
        print(f"     to the outline: mean distance {mo:.1f} verses, {ho}/{k - 1} within 3 (random {no[:, 0].mean():.1f}, {no[:, 1].mean():.1f}; p {po:.3f});  to chapter starts: {mc:.1f}, {hc}/{k - 1} (random {nc[:, 0].mean():.1f}; p {pc:.3f})")
        b = [0] + cuts + [n]
        print("     sections:", " | ".join(f"{lab(b[s])}–{lab(b[s + 1] - 1)} [{name(b[s], b[s + 1])}]" for s in range(k)))
        out.setdefault(sig, {})[k] = dict(cuts=[lab(c) for c in cuts], outline_dist=mo, outline_hits=ho, p_outline=po, chapter_dist=mc, chapter_hits=hc, p_chapter=pc,
                                         sections=[[lab(b[s]), lab(b[s + 1] - 1), name(b[s], b[s + 1])] for s in range(k)])
# stability: cuts that recur across k and across both signals
allc = collections.Counter()
for sig in out:
    for k in out[sig]:
        for c in out[sig][k]["cuts"]: allc[c] += 1
print("\nRECURRING CUTS (count over 10 segmentations):", ", ".join(f"{c}×{m}" for c, m in sorted(allc.items(), key=lambda x: (-x[1], x[0])) if m >= 3))
out["recurring"] = allc.most_common()
json.dump(out, open(os.path.join(HERE, "round30_results.json"), "w"), ensure_ascii=False, indent=1, default=int)
