#!/usr/bin/env python3
"""Round 29: the two follow-ups to round 28.

A. WHY ARE JOHN'S CLAUSE EDGES AUDIBLE IN THE LETTERS?  Hypothesis: John's clauses open in a few recurring ways (stock
   openers), so the next clause begins with a predictable unit and the cut before it is cheap.
   A1. Opener predictability per book: entropy of the clause-opening word (first word, plus the second if it is a
       postpositive such as oun / de / gar), and the share covered by the 10 commonest openers.  From SBLGNT.
   A2. Split the matched lift by what follows: clause ends followed by one of the book's 10 commonest openers against
       clause ends followed by anything else.
   A3. Deletion: remove every stock-opener word from the letter stream, re-segment, and measure the lift again.  If the
       lift collapses in John, the openers are the mechanism.  Luke in P75 (same scribe) is the control.
B. THE THREE MOVEMENTS.  Best division of the mode series (discourse - action) into 3 parts (exhaustive two-cut search,
   minimum within-part variance): where do the cuts fall, and how close are they to the natural breaks scholars
   name (1:19, 2:1, 5:1, 7:1, 11:1, 12:1, 13:1, 18:1, 20:1, 21:1)?  Against a null of random cut pairs.  Significance of the
   one-third period against power-law (red-noise) surrogates, which are stricter than AR(1).  Same for Matthew.
Usage: python3 round29.py <cntr class-1 dir> <sblgnt dir>
"""
import collections, csv, difflib, glob, json, math, os, re, sys, unicodedata
import numpy as np
CN, SBL = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
rng = np.random.default_rng(29); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
SBLF = {40: "Mt", 41: "Mk", 42: "Lk", 43: "Jn"}; _sb = {}
def sbl(code):
    if code not in _sb:
        V = collections.OrderedDict()
        for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
            p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], w=nrm(p[4]), lem=nrm(p[6]), pos=p[1], parse=p[2]))
        _sb[code] = V
    return _sb[code]
POST = {"ουν", "δε", "γαρ", "μεν", "τε"}
def openers(V):
    """clause-opening keys in SBLGNT: first word after punctuation (+ postpositive)"""
    toks = [t for v in V.values() for t in v]; ops = []
    for i in range(len(toks) - 1):
        if re.search(r"[.,·;:]", toks[i]["raw"]):
            k = toks[i + 1]["w"];
            if i + 2 < len(toks) and toks[i + 2]["w"] in POST: k += " " + toks[i + 2]["w"]
            ops.append(k)
    return collections.Counter(ops)
def entropy(c):
    n = sum(c.values()); return -sum(v / n * math.log2(v / n) for v in c.values())
print("A1. HOW PREDICTABLE IS THE NEXT CLAUSE'S OPENING? (SBLGNT)")
TOP = {}
for code in ("Jn", "Mk", "Mt", "Lk"):
    c = openers(sbl(code)); n = sum(c.values()); TOP[code] = [k for k, _ in c.most_common(10)]
    # entropy on an equal sample size (bootstrap 2,000 openers) so books of different length compare fairly
    lst = list(c.elements()); hs = [entropy(collections.Counter(rng.choice(lst, 2000))) for _ in range(30)]
    cov = sum(v for _, v in c.most_common(10)) / n
    print(f"   {code}: {n} clause openings; entropy {np.mean(hs):.2f} bits (n = 2,000); top 10 cover {cov:.1%}: {', '.join(TOP[code])}")
    out.setdefault("A1", {})[code] = dict(entropy=float(np.mean(hs)), top10=cov, top=TOP[code])
# ---------------------------------------------------------------- segmentation machinery
def papyrus(fn, book):
    res = []
    for l in open(os.path.join(CN, fn), encoding="utf-8"):
        if not l.startswith(str(book)): continue
        ref = (int(l[2:5]), int(l[5:8])); t = re.sub(r"x\{[^}]*\}", "", l[9:]).replace("a{", "").replace("{", "").replace("}", "")
        ws = [nrm(re.sub(r"[0-9/]", "", tok)) for tok in t.split()]; ws = [w for w in ws if w]
        if ws: res.append((ref, ws))
    return res
def aligned(P, S, cap=40000):
    """-> list of (word, clause_end, followed_by_top_opener) in papyrus order"""
    items = []; n = 0
    for ref, words in P:
        s = S.get(ref, []); sw = [t["w"] for t in s]; pu = [bool(re.search(r"[.,·;:]", t["raw"])) for t in s]
        ends = [False] * len(words)
        for a, b, k in difflib.SequenceMatcher(None, words, sw, autojunk=False).get_matching_blocks():
            for j in range(k): ends[a + j] = pu[b + j]
        ends[-1] = True
        for i, w in enumerate(words): items.append([w, ends[i]]); n += len(w)
        if n >= cap: break
    return items
def build(items, top, drop=False):
    """letters, word ends, clause ends split by what follows (top opener / other); optionally drop stock-opener words"""
    keys = []
    for i, (w, e) in enumerate(items):
        nxt = items[i + 1][0] if i + 1 < len(items) else ""; nx2 = items[i + 2][0] if i + 2 < len(items) else ""
        k = nxt + (" " + nx2 if nx2 in POST else ""); keys.append(k)
    letters, wb, ct, co = [], set(), set(), set(); skip = set()
    if drop:
        for i, (w, e) in enumerate(items):
            if e and keys[i] in top:
                skip.add(i + 1)
                if " " in keys[i]: skip.add(i + 2)
    for i, (w, e) in enumerate(items):
        if i in skip: continue
        letters += list(w); wb.add(len(letters))
        if e: (ct if keys[i] in top else co).add(len(letters))
    return "".join(letters), wb, ct, co
def dp_segment(text, iters=10, alpha=20.0, pstop=0.25, L=14, seed=0):
    r = np.random.default_rng(seed); f = collections.Counter(text); tot = sum(f.values()); lp = {c: math.log(f[c] / tot) for c in f}
    def p0(w): return sum(lp[c] for c in w) + (len(w) - 1) * math.log(1 - pstop) + math.log(pstop)
    b = sorted(set(np.flatnonzero(r.random(len(text)) < 0.35) + 1) | {len(text)})
    for _ in range(iters):
        units, prev = collections.Counter(), 0
        for x in b: units[text[prev:x]] += 1; prev = x
        logN = math.log(sum(units.values()) + alpha); cache = {}
        def cost(w):
            if w not in cache: cache[w] = -(math.log(units[w] + alpha * math.exp(p0(w))) - logN)
            return cache[w]
        n = len(text); best = [0.0] + [math.inf] * n; back = [0] * (n + 1)
        for j in range(1, n + 1):
            bj, bk = math.inf, 0
            for k in range(max(0, j - L), j):
                c = best[k] + cost(text[k:j])
                if c < bj: bj, bk = c, k
            best[j], back[j] = bj, bk
        nb, j = [], n
        while j > 0: nb.append(j); j = back[j]
        b = sorted(nb)
    return set(b)
def bpe_segment(text, rate):
    seq = list(text); target = int(len(text) * rate)
    while len(seq) > target:
        (a, c), cnt = collections.Counter(zip(seq, seq[1:])).most_common(1)[0]; ns, i = [], 0
        if cnt < 2: break
        while i < len(seq):
            if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == c: ns.append(a + c); i += 2
            else: ns.append(seq[i]); i += 1
        seq = ns
    b, pos = set(), 0
    for u in seq: pos += len(u); b.add(pos)
    return b
def matched(text, wb, cb, B, reps=300):
    """same word form at a clause end (cb) vs at a non-clause word end"""
    endw, prev = {}, 0
    for x in sorted(wb): endw[x] = text[prev:x]; prev = x
    byw = collections.defaultdict(lambda: [[], []])
    for x, w in endw.items():
        if x in cb: byw[w][1].append(x in B)
        elif x not in ALLC: byw[w][0].append(x in B)
    grp = [(np.array(a[1] + a[0], float), len(a[1])) for a in byw.values() if a[0] and a[1]]
    if not grp: return float("nan"), float("nan"), 0
    def stat(gs): return np.average([g[:k].mean() - g[k:].mean() for g, k in gs], weights=[k for _, k in gs])
    real = stat(grp); null = [stat([(rng.permutation(g), k) for g, k in grp]) for _ in range(reps)]
    return float(real), float(np.mean(np.array(null) >= real)), sum(k for _, k in grp)
print("\nA2/A3. SPLIT BY WHAT FOLLOWS, AND DELETE THE STOCK OPENERS (matched same-word lift, p)")
SETS = [("John P66", "P66.txt", 43), ("John 03", "03.txt", 43), ("John 01", "01.txt", 43), ("Luke P75 (control)", "P75.txt", 42), ("Mark 03 (control)", "03.txt", 41)]
for lab, fn, bk in SETS:
    code = SBLF[bk]; top = set(TOP[code]); items = aligned(papyrus(fn, bk), sbl(code)); row = {}
    for cond in ("full", "deleted"):
        text, wb, ct, co = build(items, top, drop=(cond == "deleted")); ALLC = ct | co
        for m, B in (("MDL", dp_segment(text)), ("BPE", bpe_segment(text, len(wb) / len(text)))):
            if cond == "full":
                a = matched(text, wb, ct, B); b = matched(text, wb, co, B); row[f"{m} before stock opener"] = a; row[f"{m} before other opening"] = b
            else:
                row[f"{m} after deletion (all clause ends)"] = matched(text, wb, ct | co, B)
        if cond == "full":
            for m in ("MDL", "BPE"): pass
    print(f"   {lab}: clause ends before a stock opener {len(build(items, top)[2])}, before another opening {len(build(items, top)[3])}")
    for k, (d, p, n) in row.items(): print(f"      {k:38s} {d:+.1%} (p {p:.3f}, n {n})")
    out.setdefault("A23", {})[lab] = {k: dict(lift=v[0], p=v[1], n=v[2]) for k, v in row.items()}
# ---------------------------------------------------------------- B. three movements
print("\nB. THE THREE MOVEMENTS")
def mode_series(V):
    d, a = [], []
    for v in V.values():
        n = len(v); speech = any(u["pos"][0] == "V" and u["parse"][0] in "12" for u in v)
        d.append(sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in v) / n)
        a.append(sum(t["pos"][0] == "V" and t["parse"][0] == "3" and t["parse"][3] == "I" and t["parse"][1] in "AIP" and not speech for t in v) / n)
    d, a = np.array(d), np.array(a); return (d - d.mean()) / d.std() - (a - a.mean()) / a.std()
def best3(x, minseg=40):
    c = np.concatenate([[0], np.cumsum(x)]); c2 = np.concatenate([[0], np.cumsum(x * x)]); n = len(x)
    def sse(i, j): s = c[j] - c[i]; return (c2[j] - c2[i]) - s * s / (j - i)
    best = (np.inf, 0, 0)
    for i in range(minseg, n - 2 * minseg):
        js = np.arange(i + minseg, n - minseg)
        s1 = c[js] - c[i]; s2 = c[n] - c[js]
        v = sse(0, i) + (c2[js] - c2[i]) - s1 * s1 / (js - i) + (c2[n] - c2[js]) - s2 * s2 / (n - js); k = int(np.argmin(v))
        if v[k] < best[0]: best = (float(v[k]), i, int(js[k]))
    tot = sse(0, n); return best[1], best[2], 1 - best[0] / tot
def powerlaw_surr(x):
    """surrogate with the same power-law slope as x (fitted on log-log periodogram), random phases"""
    n = len(x); f = np.fft.rfftfreq(n)[1:]; P = np.abs(np.fft.rfft(x - x.mean()))[1:] ** 2
    beta = -np.polyfit(np.log(f), np.log(P), 1)[0]; amp = f ** (-beta / 2); ph = rng.uniform(0, 2 * np.pi, len(f))
    y = np.fft.irfft(np.concatenate([[0], amp * np.exp(1j * ph)]), n); return (y - y.mean()) / y.std() * x.std(), beta
def third_share(x):
    s = np.convolve(np.pad(x, 3, mode="edge"), np.ones(7) / 7, mode="valid"); P = np.abs(np.fft.rfft(s - s.mean())) ** 2; return P[3] / P[1:].sum(), P[1:].argmax() + 1
NAT = {"Jn": [(1, 19), (2, 1), (5, 1), (7, 1), (11, 1), (12, 1), (13, 1), (18, 1), (20, 1), (21, 1)],
       "Mt": [(3, 1), (5, 1), (8, 1), (11, 1), (13, 1), (14, 1), (16, 13), (19, 1), (21, 1), (24, 1), (26, 1), (28, 1)]}
for code in ("Jn", "Mt"):
    V = sbl(code); keys = list(V); x = mode_series(V); n = len(x)
    i, j, r2 = best3(x); nat = [keys.index(k) for k in NAT[code] if k in V]
    dist = lambda c: min(abs(c - q) for q in nat); real_d = dist(i) + dist(j)
    nulld = []
    for _ in range(5000):
        a, b = sorted(rng.choice(np.arange(40, n - 40), 2, replace=False)); nulld.append(dist(a) + dist(b))
    pd_ = float(np.mean(np.array(nulld) <= real_d))
    r2n = [best3(powerlaw_surr(x)[0])[2] for _ in range(300)]; beta = powerlaw_surr(x)[1]
    sh, pk = third_share(x); shn = [third_share(powerlaw_surr(x)[0])[0] for _ in range(2000)]
    lab = lambda q: f"{keys[q][0]}:{keys[q][1]}"
    parts = [x[:i].mean(), x[i:j].mean(), x[j:].mean()]
    print(f"   {code}: best cuts at {lab(i)} and {lab(j)} (parts of {i}, {j - i}, {n - j} verses; mode means {parts[0]:+.2f} {parts[1]:+.2f} {parts[2]:+.2f}, + = discourse)")
    print(f"      distance of cuts to the nearest natural break: {dist(i)} + {dist(j)} verses (random cut pairs median {np.median(nulld):.0f}; p {pd_:.3f})")
    print(f"      variance explained by 3 parts {r2:.3f} vs power-law surrogates {np.mean(r2n):.3f} (p {np.mean(np.array(r2n) >= r2):.3f}; spectral slope {beta:.2f})")
    print(f"      one-third period power share {sh:.3f} vs power-law surrogates {np.mean(shn):.3f} (p {np.mean(np.array(shn) >= sh):.3f})")
    res = dict(cuts=[lab(i), lab(j)], sizes=[i, j - i, n - j], means=[float(p) for p in parts], dist=[dist(i), dist(j)], p_dist=pd_, r2=float(r2), r2_null=float(np.mean(r2n)),
               p_r2=float(np.mean(np.array(r2n) >= r2)), third=float(sh), p_third=float(np.mean(np.array(shn) >= sh)))
    if code == "Jn":
        t = {r["verse"]: float(r["start_s"]) for r in csv.DictReader(open(os.path.join(ROOT, "model/out/john_verses.csv")))}
        tm = [t.get(lab(q), np.nan) / 60 for q in (i, j)]; total = max(t.values()) / 60
        print(f"      in the sound model the cuts fall at {tm[0]:.0f} and {tm[1]:.0f} minutes of {total:.0f}: parts of {tm[0]:.0f}, {tm[1] - tm[0]:.0f}, {total - tm[1]:.0f} minutes")
        res["minutes"] = [tm[0], tm[1] - tm[0], total - tm[1]]
    out.setdefault("B", {})[code] = res
json.dump(out, open(os.path.join(HERE, "round29_results.json"), "w"), ensure_ascii=False, indent=1)
