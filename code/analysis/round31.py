#!/usr/bin/env python3
"""Round 31: the blind section-finder of round 30 applied to Mark, Matthew and Luke (John repeated for comparison).

Same two signals (MODE = discourse - action; WORDS = content vocabulary, 40 latent dimensions, 5-verse smoothing), same
optimal segmentation into 4-8 parts (min 15 verses), same scoring: mean distance of cuts to the nearest break of a
standard outline, and hits within 3 verses, against 5,000 random cut sets.  Also against chapter starts.
Outlines (conventional, fixed before running):
  Mark: 1:14 Galilee ministry, 3:7, 6:7 (mission), 8:27 (Caesarea Philippi), 11:1 (Jerusalem), 14:1 (passion), 16:1.
  Matthew: 3:1, 4:17, 5:1 / 8:1 (Sermon), 10:1 / 11:1 (mission discourse), 13:1 / 13:53 (parables), 16:21, 18:1 / 19:1
           (community discourse), 21:1, 24:1 / 26:1 (eschatological discourse), 28:1.
  Luke: 1:5, 3:1, 4:14, 6:20 (Sermon on the Plain), 9:51 (journey), 19:28 (Jerusalem), 22:1 (passion), 24:1.
  John: as round 30.
Usage: python3 round31.py <sblgnt dir>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(31); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
OUTLINES = {"Mk": [(1, 14), (3, 7), (6, 7), (8, 27), (11, 1), (14, 1), (16, 1)],
            "Mt": [(3, 1), (4, 17), (5, 1), (8, 1), (10, 1), (11, 1), (13, 1), (13, 53), (16, 21), (18, 1), (19, 1), (21, 1), (24, 1), (26, 1), (28, 1)],
            "Lk": [(1, 5), (3, 1), (4, 14), (6, 20), (9, 51), (19, 28), (22, 1), (24, 1)],
            "Jn": [(1, 19), (2, 1), (5, 1), (6, 1), (7, 1), (9, 1), (10, 22), (11, 1), (12, 12), (13, 1), (13, 31), (18, 1), (20, 1), (21, 1)]}
STOP = set("ο και αυτος δε εν ειμι λεγω ου μη γαρ ουν οτι εγω συ ουτος εκεινος τις ινα προς εκ εις απο επι δια μετα περι αλλα ως καθως ημεις υμεις εαν αν οστις παρα υπο ηδη ετι ουδε τε η ποιεω εχω γινομαι ερχομαι".split())
def segment(Y, k, n, minseg=15):
    c = np.vstack([np.zeros(Y.shape[1]), np.cumsum(Y, 0)]); c2 = np.concatenate([[0], np.cumsum((Y * Y).sum(1))])
    D = np.full((k + 1, n + 1), np.inf); B = np.zeros((k + 1, n + 1), int); D[0, 0] = 0
    for s in range(1, k + 1):
        for i in range(n):
            if D[s - 1, i] == np.inf: continue
            js = np.arange(i + minseg, n + 1)
            if not len(js): continue
            sm = c[js] - c[i]; v = D[s - 1, i] + (c2[js] - c2[i]) - (sm * sm).sum(1) / (js - i); b = v < D[s, js]; D[s, js[b]] = v[b]; B[s, js[b]] = i
    cuts, j = [], n
    for s in range(k, 0, -1): j = B[s, j]; cuts.append(j)
    return sorted(cuts)[1:]
for code in ("Jn", "Mk", "Mt", "Lk"):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(lem=nrm(p[6]), pos=p[1], parse=p[2]))
    keys = list(V); n = len(keys); lab = lambda i: f"{keys[i][0]}:{keys[i][1]}"
    d, a = [], []
    for v in V.values():
        m = len(v); sp = any(u["pos"][0] == "V" and u["parse"][0] in "12" for u in v)
        d.append(sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in v) / m)
        a.append(sum(t["pos"][0] == "V" and t["parse"][0] == "3" and t["parse"][3] == "I" and t["parse"][1] in "AIP" and not sp for t in v) / m)
    d, a = np.array(d), np.array(a); MODE = ((d - d.mean()) / d.std() - (a - a.mean()) / a.std())[:, None]
    docs = [[t["lem"] for t in V[k] if t["pos"][0] in "NVA" and t["lem"] not in STOP] for k in keys]
    df = collections.Counter(l for x in docs for l in set(x)); vocab = {l: i for i, l in enumerate(df)}; idf = np.array([math.log(n / df[l]) for l in vocab])
    X = np.zeros((n, len(vocab)))
    for i, x in enumerate(docs):
        for l in x: X[i, vocab[l]] += 1
    Xw = X * idf; Xw /= np.maximum(1e-9, np.linalg.norm(Xw, axis=1, keepdims=True)); U, S, _ = np.linalg.svd(Xw - Xw.mean(0), full_matrices=False)
    W = U[:, :40] * S[:40]; WORDS = np.array([np.convolve(np.pad(W[:, c], 2, mode="edge"), np.ones(5) / 5, mode="valid") for c in range(40)]).T
    OL = [keys.index(k) for k in OUTLINES[code] if k in V]; CH = [i for i, k in enumerate(keys) if k[1] == 1 and k[0] > 1]
    def score(cuts, ref): dd = [min(abs(c - r) for r in ref) for c in cuts]; return float(np.mean(dd)), sum(x <= 3 for x in dd)
    def rand_cuts(k, minseg=15):
        while True:
            c = sorted(rng.choice(np.arange(minseg, n - minseg), k - 1, replace=False))
            if all(b - a_ >= minseg for a_, b in zip(c, c[1:])): return c
    inv = {v: k for k, v in vocab.items()}
    def name(i, j, top=3):
        sub = X[i:j].sum(0); rest = X.sum(0) - sub; lo = (sub + .5) / (sub.sum() + .5 * len(vocab)); lr = (rest + .5) / (rest.sum() + .5 * len(vocab))
        return ", ".join(inv[q] for q in np.argsort(-(np.log(lo / lr) * np.sqrt(sub)))[:top])
    print(f"\n{code} ({n} verses)")
    for sig, Y in (("MODE", MODE), ("WORDS", WORDS)):
        for k in (4, 6, 8):
            cuts = segment(Y, k, n); mo, ho = score(cuts, OL); mc, hc = score(cuts, CH)
            nul = [rand_cuts(k) for _ in range(5000)]; no = np.array([score(c, OL) for c in nul]); nc = np.array([score(c, CH) for c in nul])
            po, pc = float(np.mean(no[:, 0] <= mo)), float(np.mean(nc[:, 0] <= mc)); b = [0] + cuts + [n]
            print(f"  {sig:5s} {k}: cuts {' '.join(lab(c) for c in cuts)}")
            print(f"        outline: mean dist {mo:.1f} (random {no[:, 0].mean():.1f}), {ho}/{k - 1} within 3, p {po:.3f};  chapters: {mc:.1f} (random {nc[:, 0].mean():.1f}), p {pc:.3f}")
            if k == 4 or (k == 8 and sig == "WORDS"): print("        sections:", " | ".join(f"{lab(b[s])}–{lab(b[s + 1] - 1)} [{name(b[s], b[s + 1])}]" for s in range(k)))
            out.setdefault(code, {}).setdefault(sig, {})[k] = dict(cuts=[lab(c) for c in cuts], outline_dist=mo, random=float(no[:, 0].mean()), hits=int(ho), p_outline=po, chapter_dist=mc, p_chapter=pc,
                                                              sections=[[lab(b[s]), lab(b[s + 1] - 1), name(b[s], b[s + 1])] for s in range(k)])
print("\nSUMMARY: p (cuts closer to the outline than random), per Gospel / signal / parts")
for code in out:
    print(f"   {code}: " + "  ".join(f"{sig} " + "/".join(f"{out[code][sig][k]['p_outline']:.3f}" for k in (4, 6, 8)) for sig in ("MODE", "WORDS")))
json.dump(out, open(os.path.join(HERE, "round31_results.json"), "w"), ensure_ascii=False, indent=1)
