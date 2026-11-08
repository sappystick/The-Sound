#!/usr/bin/env python3
"""Round 28: the two follow-ups to round 27.

A. IS THE BREATH-EDGE EFFECT JOHN'S OR GREEK'S?  The same self-segmentation (MDL compression and byte-pair) and the same
   matched test (the same word form at a clause end vs elsewhere) on: John in P66, P75, Sinaiticus (01), Vaticanus (03);
   controls Luke in P75 (same scribe, other author), Mark in 01 and 03 (same codices, other Gospel), Romans and 1 Corinthians
   in P46 (Paul, letters), Hebrews in P46.  Equal-length samples (first 40,000 letters) so the lift is comparable.
B. DOES THE ACTION / DISCOURSE SWITCH HAVE A RHYTHM?  Per verse: discourse = 1st/2nd-person verbs and pronouns per word;
   action = 3rd-person indicative narrative verbs (aorist, imperfect, historic present) per word.  Mode = smoothed
   (discourse - action).  Switches = sign changes.  Tests: (1) regularity of the stretches between switches (coefficient
   of variation; lower = more regular) and (2) the strongest period in the mode series and its share of power, both against
   surrogates with the same autocorrelation (AR(1) fitted to each Gospel, 2,000 surrogates).  John, Mark, Matthew, Luke;
   also John measured in spoken seconds (from the sound model) instead of verses.
Usage: python3 round28.py <cntr class-1 dir> <sblgnt dir>
"""
import collections, csv, difflib, glob, json, math, os, re, sys, unicodedata
import numpy as np
CN, SBL = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
rng = np.random.default_rng(28); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
SBLF = {40: "Mt", 41: "Mk", 42: "Lk", 43: "Jn", 45: "Ro", 46: "1Co", 58: "Heb"}
_sb = {}
def sbl(code):
    if code not in _sb:
        V = collections.OrderedDict()
        for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
            p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], w=nrm(p[4]), lem=nrm(p[6]), pos=p[1], parse=p[2]))
        _sb[code] = V
    return _sb[code]
# ------------------------------------------------------------------ A
def papyrus(fn, book):
    res = []
    for l in open(os.path.join(CN, fn), encoding="utf-8"):
        if not l.startswith(str(book)): continue
        ref = (int(l[2:5]), int(l[5:8])); t = re.sub(r"x\{[^}]*\}", "", l[9:]).replace("a{", "").replace("{", "").replace("}", "")
        ws = [nrm(re.sub(r"[0-9/]", "", tok)) for tok in t.split()]; ws = [w for w in ws if w]
        if ws: res.append((ref, ws))
    return res
def stream(P, S, cap=40000):
    letters, wb, cb = [], set(), set()
    for ref, words in P:
        s = S.get(ref, []); sw = [t["w"] for t in s]; pu = [bool(re.search(r"[.,·;:]", t["raw"])) for t in s]
        ends = [False] * len(words)
        for a, b, n in difflib.SequenceMatcher(None, words, sw, autojunk=False).get_matching_blocks():
            for k in range(n): ends[a + k] = pu[b + k]
        ends[-1] = True
        for i, w in enumerate(words):
            letters += list(w); wb.add(len(letters))
            if ends[i]: cb.add(len(letters))
        if len(letters) >= cap: break
    return "".join(letters), wb, cb
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
def matched(text, wb, cb, B, reps=400):
    endw, prev = {}, 0
    for x in sorted(wb): endw[x] = text[prev:x]; prev = x
    byw = collections.defaultdict(lambda: [[], []])
    for x, w in endw.items(): byw[w][x in cb].append(x in B)
    grp = [(np.array(a[0] + a[1], float), len(a[1])) for a in byw.values() if a[0] and a[1]]
    def stat(gs): return np.average([g[:k].mean() - g[k:].mean() for g, k in gs], weights=[k for _, k in gs])
    real = stat([(np.concatenate([g[len(g) - k:], g[:len(g) - k]]), k) for g, k in grp])   # clause items first
    null = [stat([(rng.permutation(g), k) for g, k in grp]) for _ in range(reps)]
    raw = len(B & cb) / len(cb) - len(B & (wb - cb)) / len(wb - cb)
    return float(real), float(np.mean(np.array(null) >= real)), float(raw)
SETS = [("John P66", "P66.txt", 43), ("John P75", "P75.txt", 43), ("John 01", "01.txt", 43), ("John 03", "03.txt", 43),
        ("Luke P75 (same scribe)", "P75.txt", 42), ("Mark 01", "01.txt", 41), ("Mark 03", "03.txt", 41),
        ("Romans P46", "P46.txt", 45), ("1 Cor P46", "P46.txt", 46), ("Hebrews P46", "P46.txt", 58)]
print("A. BREATH EDGES IN THE UNSPACED LETTERS: John against other books (first 40,000 letters each)")
print(f"   {'text':24s} {'letters':>7s} {'clause':>6s}   MDL: raw lift / same-word lift (p)        BPE: raw lift / same-word lift (p)")
for lab, fn, bk in SETS:
    text, wb, cb = stream(papyrus(fn, bk), sbl(SBLF[bk]))
    row = {}
    for m, B in (("mdl", dp_segment(text)), ("bpe", bpe_segment(text, len(wb) / len(text)))):
        md, p, raw = matched(text, wb, cb, B); row[m] = dict(raw=raw, matched=md, p=p)
    row.update(letters=len(text), clause_share=len(cb) / len(wb))
    print(f"   {lab:24s} {len(text):7d} {len(cb) / len(wb):6.1%}   {row['mdl']['raw']:+.1%} / {row['mdl']['matched']:+.1%} (p {row['mdl']['p']:.3f})        {row['bpe']['raw']:+.1%} / {row['bpe']['matched']:+.1%} (p {row['bpe']['p']:.3f})")
    out.setdefault("A", {})[lab] = row
# ------------------------------------------------------------------ B
print("\nB. THE RHYTHM OF THE ACTION / DISCOURSE SWITCH")
def mode_series(V):
    d, a, nw = [], [], []
    for v in V.values():
        n = len(v); nw.append(n)
        d.append(sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in v) / n)
        a.append(sum(t["pos"][0] == "V" and t["parse"][0] == "3" and t["parse"][3] == "I" and t["parse"][1] in "AIP" and not any(u["pos"][0] == "V" and u["parse"][0] in "12" for u in v) for t in v) / n)
    d, a = np.array(d), np.array(a); return (d - d.mean()) / d.std() - (a - a.mean()) / a.std(), np.array(nw)
def smooth(x, w=7): return np.convolve(np.pad(x, w // 2, mode="edge"), np.ones(w) / w, mode="valid")
def stats(x):
    s = smooth(x); sg = np.sign(s); sw = np.flatnonzero(np.diff(sg) != 0); seg = np.diff(np.concatenate([[0], sw + 1, [len(s)]]))
    seg = seg[seg > 0]; cv = seg.std() / seg.mean()
    P = np.abs(np.fft.rfft(s - s.mean())) ** 2; fr = np.fft.rfftfreq(len(s)); k = 1 + np.argmax(P[1:]); share = P[k] / P[1:].sum()
    return dict(switches=len(sw), mean_len=float(seg.mean()), cv=float(cv), period=float(1 / fr[k]), peak_share=float(share)), sw
def ar1(x, n):
    x = x - x.mean(); phi = np.corrcoef(x[:-1], x[1:])[0, 1]; e = rng.normal(0, x.std() * math.sqrt(1 - phi ** 2), n); y = np.zeros(n); y[0] = e[0]
    for i in range(1, n): y[i] = phi * y[i - 1] + e[i]
    return y, phi
for code in ("Jn", "Mk", "Mt", "Lk"):
    V = sbl(code); x, nw = mode_series(V); st, sw = stats(x)
    nulls = [stats(ar1(x, len(x))[0])[0] for _ in range(2000)]; phi = ar1(x, 10)[1]
    pcv = float(np.mean([n["cv"] <= st["cv"] for n in nulls])); ppk = float(np.mean([n["peak_share"] >= st["peak_share"] for n in nulls]))
    psw = float(np.mean([n["switches"] >= st["switches"] for n in nulls]))
    print(f"   {code}: {len(x)} verses (lag-1 r {phi:.2f}); {st['switches']} switches (AR null {np.mean([n['switches'] for n in nulls]):.0f}, p more {psw:.3f}); mean stretch {st['mean_len']:.1f} verses;"
          f" regularity CV {st['cv']:.2f} (null {np.mean([n['cv'] for n in nulls]):.2f}, p more regular {pcv:.3f}); strongest period {st['period']:.0f} verses, power share {st['peak_share']:.3f} (p {ppk:.3f})")
    out.setdefault("B", {})[code] = dict(st, p_cv=pcv, p_peak=ppk, p_switch=psw, lag1=float(phi))
    if code == "Jn":
        keys = list(V); out["B"]["Jn"]["switch_verses"] = [f"{keys[i + 1][0]}:{keys[i + 1][1]}" for i in sw]
        print("      John's switch points:", " ".join(out["B"]["Jn"]["switch_verses"]))
        # in spoken time: resample the mode onto a 10-second grid using the sound model's verse start times
        rows = list(csv.DictReader(open(os.path.join(ROOT, "model/out/john_verses.csv")))); t = {r["verse"]: float(r["start_s"]) for r in rows}
        ts = np.array([t.get(f"{c}:{v}", np.nan) for c, v in keys]); ok = ~np.isnan(ts); grid = np.arange(0, ts[ok].max(), 10.0)
        xt = np.interp(grid, ts[ok], x[ok]); stt, _ = stats(xt); nt = [stats(ar1(xt, len(xt))[0])[0] for _ in range(1000)]
        print(f"      in spoken time (10-s steps, {len(grid)} steps): mean stretch {10 * stt['mean_len'] / 60:.1f} min; CV {stt['cv']:.2f} (null {np.mean([n['cv'] for n in nt]):.2f}, p {np.mean([n['cv'] <= stt['cv'] for n in nt]):.3f});"
              f" strongest period {10 * stt['period'] / 60:.1f} min, share {stt['peak_share']:.3f} (p {np.mean([n['peak_share'] >= stt['peak_share'] for n in nt]):.3f})")
        out["B"]["Jn_time"] = dict(mean_min=10 * stt["mean_len"] / 60, cv=stt["cv"], period_min=10 * stt["period"] / 60, share=stt["peak_share"])
json.dump(out, open(os.path.join(HERE, "round28_results.json"), "w"), ensure_ascii=False, indent=1)
