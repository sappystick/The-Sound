#!/usr/bin/env python3
"""Structure the text finds for itself.  Three unsupervised tests, each with a null or control.

1. LET THE LETTERS FIND THEIR OWN WORDS.  The unspaced letter stream of P66 and P75 (John) is segmented by a compression
   model (unigram lexicon with a Dirichlet-process prior, iterated Viterbi = minimum description length) and, separately,
   by byte-pair encoding.  The self-found boundaries are then compared with (a) the editors' word spaces, (b) clause /
   breath boundaries (SBLGNT punctuation, aligned word by word), (c) the scribe's own line breaks, against random boundaries
   at the same rate.  Multi-word units the model glues together are the text's own word-chains.  The prologue's centre is
   recomputed in self-found units.
2. RECURRENCE PLOT of John, verse by verse: IDF-weighted shared vocabulary (lemmas, function words dropped).  Echoes show as
   lines parallel to the diagonal, rings as lines perpendicular to it.  Diagonal / anti-diagonal line share is compared with
   a null that shuffles verses inside each chapter (keeps chapter themes, breaks order).  Controls: Mark x Matthew
   cross-recurrence (must show a diagonal); Mark joined to its own reversed verse order (must show an anti-diagonal).
3. LINE THE LAYERS UP.  Per verse: sound (noise share), tense (historic presents), voice (1st/2nd person), movement (body /
   motion verbs), themes (theme-word density), pointers (marker verses).  Smoothed, correlated against circular-shift nulls;
   moments where three or more layers peak together counted against the same null.
Usage: python3 self_structure.py <cntr class-1 dir> <sblgnt dir> <out png dir>
"""
import collections, difflib, glob, json, math, os, re, sys, unicodedata
import numpy as np
CN, SBL, PNG = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
rng = np.random.default_rng(26); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def sbl(code):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], w=nrm(p[4]), lem=nrm(p[6]), pos=p[1], parse=p[2]))
    return V
J = sbl("Jn")
# ---------------------------------------------------------------- 1. self-segmentation
def papyrus(fn):
    """-> list of verses: (ref, words, linebreak-before-word flags)"""
    res = []
    for l in open(os.path.join(CN, fn), encoding="utf-8"):
        if not l.startswith("43"): continue
        ref = (int(l[2:5]), int(l[5:8])); t = l[9:]
        t = re.sub(r"x\{[^}]*\}", "", t); t = t.replace("a{", "").replace("{", "").replace("}", "")
        words, lb = [], []
        for tok in t.split():
            w, offs, k = "", [], 0
            for ch in re.sub(r"[0-9]", "", tok):
                if ch == "/": offs.append(len(nrm(w)))
                else: w += ch
            w = nrm(w)
            if w: words.append(w); lb.append(offs)
        res.append((ref, words, lb))
    return res
def clause_ends(ref, words):
    """Which papyrus words end a clause (SBL punctuation after the aligned word)."""
    s = J.get(ref, []); sw = [t["w"] for t in s]; punct = [bool(re.search(r"[.,·;:]", t["raw"])) for t in s]
    ends = [False] * len(words); m = difflib.SequenceMatcher(None, words, sw, autojunk=False)
    for a, b, n in m.get_matching_blocks():
        for k in range(n): ends[a + k] = punct[b + k]
    if words: ends[-1] = True
    return ends
def stream(P):
    """letters, gold word-boundary set, clause-boundary set, line-break set, verse boundary list (positions after letter i)"""
    letters, wb, cb, lbk, vstart = [], set(), set(), set(), []
    for ref, words, lb in P:
        vstart.append((ref, len(letters))); ce = clause_ends(ref, words)
        for i, w in enumerate(words):
            for o in lb[i]:
                if letters or o: lbk.add(len(letters) + o)
            letters += list(w); wb.add(len(letters))
            if ce[i]: cb.add(len(letters))
    return "".join(letters), wb, cb, lbk, vstart
ALPH = "αβγδεζηθικλμνξοπρστυφχψω"
def dp_segment(text, iters=12, alpha=20.0, pstop=0.25, L=14, seed=0):
    """Iterated Viterbi under a unigram Dirichlet-process lexicon (Goldwater-style MDL)."""
    r = np.random.default_rng(seed); f = collections.Counter(text); tot = sum(f.values()); lp = {c: math.log(f[c] / tot) for c in f}
    def p0(w): return sum(lp[c] for c in w) + (len(w) - 1) * math.log(1 - pstop) + math.log(pstop)
    b = sorted(set(np.flatnonzero(r.random(len(text)) < 0.35) + 1) | {len(text)})
    for it in range(iters):
        units, prev = collections.Counter(), 0
        for x in b: units[text[prev:x]] += 1; prev = x
        N = sum(units.values()); logN = math.log(N + alpha); la = math.log(alpha)
        cache = {}
        def cost(w):
            if w not in cache: cache[w] = -(math.log(units[w] + alpha * math.exp(p0(w))) - logN)
            return cache[w]
        n = len(text); best = np.full(n + 1, np.inf); best[0] = 0; back = np.zeros(n + 1, int)
        for j in range(1, n + 1):
            for k in range(max(0, j - L), j):
                c = best[k] + cost(text[k:j])
                if c < best[j]: best[j] = c; back[j] = k
        nb, j = [], n
        while j > 0: nb.append(j); j = back[j]
        b = sorted(nb)
    units, prev = collections.Counter(), 0
    for x in b: units[text[prev:x]] += 1; prev = x
    return set(b), units
def bpe_segment(text, wb_rate):
    """Byte-pair encoding over the unspaced stream until the unit count matches the word count."""
    seq = list(text); target = int(len(text) * wb_rate)
    while len(seq) > target:
        pc = collections.Counter(zip(seq, seq[1:])); (a, c), _ = pc.most_common(1)[0]; ns, i = [], 0
        while i < len(seq):
            if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == c: ns.append(a + c); i += 2
            else: ns.append(seq[i]); i += 1
        seq = ns
    b, pos = set(), 0
    for u in seq: pos += len(u); b.add(pos)
    return b, collections.Counter(seq)
def prf(found, gold, n):
    tp = len(found & gold); p = tp / max(1, len(found)); r = tp / max(1, len(gold)); return p, r, 2 * p * r / max(1e-9, p + r)
print("1. LET THE LETTERS FIND THEIR OWN WORDS")
for fn in ("P66.txt", "P75.txt"):
    P = papyrus(fn); text, wb, cb, lbk, vstart = stream(P); n = len(text)
    dpb, dpu = dp_segment(text); bpb, bpu = bpe_segment(text, len(wb) / n)
    print(f"   {fn[:-4]}: {len(P)} verses, {n} letters, {len(wb)} words, {len(cb)} clause ends, {len(lbk)} line breaks")
    res = {}
    for lab, B in (("compression (MDL)", dpb), ("byte-pair", bpb)):
        rate = len(B) / n; p, r, f = prf(B, wb, n)
        rnd = [prf(set(np.flatnonzero(rng.random(n) < rate) + 1), wb, n)[2] for _ in range(50)]
        # recall at clause ends vs at other word ends; and at line breaks vs other positions
        other_wb = wb - cb; rc, ro = len(B & cb) / len(cb), len(B & other_wb) / len(other_wb)
        mid_lb = lbk - wb; lb_hit = len(B & mid_lb) / max(1, len(mid_lb)); nonw = set(range(1, n)) - wb; base_nw = len(B & nonw) / len(nonw)
        # null for clause recall: random subsets of word ends, same size as clause set
        wl = sorted(wb); hits = np.array([x in B for x in wl]); ncl = len(cb)
        null = [hits[rng.permutation(len(wl))[:ncl]].mean() for _ in range(2000)]
        pc = float(np.mean(np.array(null) >= rc))
        # matched control: the same word form at a clause end vs elsewhere (removes word-type effects)
        endword = {}; prev = 0
        for x in sorted(wb):
            endword[x] = text[prev:x]; prev = x
        byw = collections.defaultdict(lambda: [[], []])
        for x, w in endword.items(): byw[w][x in cb].append(x in B)
        diffs = [(np.mean(a[1]) - np.mean(a[0]), len(a[1])) for a in byw.values() if a[0] and a[1]]
        md = float(np.average([d for d, _ in diffs], weights=[w for _, w in diffs]))
        mnull = []
        for _ in range(500):
            ds = []
            for a in byw.values():
                if a[0] and a[1]:
                    al = np.array(a[0] + a[1], float); pm = rng.permutation(len(al)); ds.append((al[pm[:len(a[1])]].mean() - al[pm[len(a[1]):]].mean(), len(a[1])))
            mnull.append(np.average([d for d, _ in ds], weights=[w for _, w in ds]))
        pm_ = float(np.mean(np.array(mnull) >= md))
        print(f"     {lab:18s} {len(B)} units; word-boundary F {f:.2f} (P {p:.2f} R {r:.2f}; random boundaries F {np.mean(rnd):.2f})")
        print(f"       found at clause/breath ends {rc:.1%} vs other word ends {ro:.1%}  (p {pc:.4f});  at mid-word line breaks {lb_hit:.1%} vs other mid-word points {base_nw:.1%} (n {len(mid_lb)})")
        print(f"       same word form, at a clause end vs not: {md:+.1%} boundary rate (p {pm_:.4f})")
        res[lab] = dict(units=len(B), F=f, P=p, R=r, F_random=float(np.mean(rnd)), clause=rc, other=ro, p_clause=pc, linebreak_midword=lb_hit, midword_base=base_nw, matched_diff=md, p_matched=pm_)
    # word-chains: MDL units spanning 2+ gold words, frequent
    chains = collections.Counter(); prev = 0
    for x in sorted(dpb):
        inner = [k for k in range(prev + 1, x) if k in wb]
        if inner and prev in wb | {0} and x in wb: chains[text[prev:x]] += 1
        prev = x
    top = [(u, c) for u, c in chains.most_common(25)]
    print("       word-chains the model glued (unit spans whole words):", ", ".join(f"{u}×{c}" for u, c in top[:18]))
    res["chains"] = top
    # prologue centre in self-found units
    pv = [(r, s) for r, s in vstart if r[0] == 1 and r[1] <= 18]
    if len(pv) >= 17:
        end = next(s for r, s in vstart if r > (1, 18)); start = pv[0][1]
        u = [x for x in sorted(dpb) if start < x <= end]; mid = u[len(u) // 2 - 1]
        cv = max(r for r, s in pv if s < mid)
        # same for gold words and letters
        gw = [x for x in sorted(wb) if start < x <= end]; gv = max(r for r, s in pv if s < gw[len(gw) // 2 - 1]); lv = max(r for r, s in pv if s < (start + end) / 2)
        print(f"       prologue (1:1-18) midpoint: in self-found units at {cv[0]}:{cv[1]}; in words {gv[0]}:{gv[1]}; in letters {lv[0]}:{lv[1]}")
        res["prologue_centre"] = dict(units=f"{cv[0]}:{cv[1]}", words=f"{gv[0]}:{gv[1]}", letters=f"{lv[0]}:{lv[1]}")
    out.setdefault("segment", {})[fn[:-4]] = res
# ---------------------------------------------------------------- 2. recurrence plot
STOP = set("ο και αυτος δε εν ειμι λεγω ου μη γαρ ουν οτι εγω συ ουτος εκεινος τις ινα προς εκ εις απο επι δια μετα περι αλλα ως καθως ημεις υμεις εαν αν οστις παρα υπο ηδη ετι ουδε μηδε τε η ωστε οπως ιδε ιδου σος εμος ημετερος υμετερος εαυτου αλληλων παλιν νυν οτε ποτε που πως ουκετι ναι αμην πας".split())
def verse_vecs(V):
    keys = list(V); docs = [[t["lem"] for t in V[k] if t["lem"] not in STOP and t["pos"][0] in "NVA"] for k in keys]
    df = collections.Counter(l for d in docs for l in set(d)); N = len(docs); idf = {l: math.log(N / c) for l, c in df.items()}
    vocab = {l: i for i, l in enumerate(df)}; M = np.zeros((N, len(vocab)))
    for i, d in enumerate(docs):
        for l in d: M[i, vocab[l]] += idf[l]
    M /= np.maximum(1e-9, np.linalg.norm(M, axis=1, keepdims=True)); return keys, M, vocab
def cross(VA, VB):
    ka, kb = list(VA), list(VB); docs = [[t["lem"] for t in VA[k] if t["lem"] not in STOP and t["pos"][0] in "NVA"] for k in ka] + [[t["lem"] for t in VB[k] if t["lem"] not in STOP and t["pos"][0] in "NVA"] for k in kb]
    df = collections.Counter(l for d in docs for l in set(d)); N = len(docs); idf = {l: math.log(N / c) for l, c in df.items()}; vocab = {l: i for i, l in enumerate(df)}
    M = np.zeros((N, len(vocab)))
    for i, d in enumerate(docs):
        for l in d: M[i, vocab[l]] += idf[l]
    M /= np.maximum(1e-9, np.linalg.norm(M, axis=1, keepdims=True)); return M[:len(ka)], M[len(ka):]
def lines(R, anti=False, minlen=2, band=3):
    """share of recurrent off-diagonal points that lie on diagonal (or anti-diagonal) runs of length >= minlen, and the runs"""
    n, m = R.shape; on = 0; runs = []
    A = R[:, ::-1] if anti else R
    for d in range(-(n - 1), m):
        dg = np.diagonal(A, d)
        if not dg.any(): continue
        x = np.concatenate([[0], dg.astype(int), [0]]); st = np.flatnonzero(np.diff(x) == 1); en = np.flatnonzero(np.diff(x) == -1)
        for a, b in zip(st, en):
            i0 = a + max(0, -d); j0 = a + max(0, d)
            if anti: j0 = m - 1 - j0
            if abs(i0 - j0) <= band and R.shape[0] == R.shape[1]: continue
            if b - a >= minlen: on += b - a; runs.append((b - a, i0, j0))
    tot = R.sum() - (sum(np.trace(R, k) for k in range(-band, band + 1)) if R.shape[0] == R.shape[1] else 0)
    return on / max(1, tot), sorted(runs, reverse=True)
def thresh(S, q=0.985, band=3):
    n = S.shape[0]; mask = np.abs(np.subtract.outer(np.arange(n), np.arange(S.shape[1]))) > band if S.shape[0] == S.shape[1] else np.ones_like(S, bool)
    t = np.quantile(S[mask], q); return (S >= t) & mask
print("\n2. RECURRENCE PLOT")
keys, M, _ = verse_vecs(J); S = M @ M.T; R = thresh(S); n = len(keys)
dg, druns = lines(R); ad, aruns = lines(R, anti=True)
chap = np.array([k[0] for k in keys]); nd, na = [], []
for _ in range(200):
    perm = np.concatenate([rng.permutation(np.flatnonzero(chap == c)) for c in sorted(set(chap))]); Sp = S[np.ix_(perm, perm)]; Rp = thresh(Sp)
    nd.append(lines(Rp)[0]); na.append(lines(Rp, anti=True)[0])
pd_, pa_ = float(np.mean(np.array(nd) >= dg)), float(np.mean(np.array(na) >= ad))
print(f"   John: {n} verses, top 1.5% of verse pairs recurrent")
print(f"   points on echo lines (parallel)  {dg:.3f}  vs order-shuffled-within-chapter {np.mean(nd):.3f}  p {pd_:.3f}")
print(f"   points on ring lines (crossing)  {ad:.3f}  vs order-shuffled-within-chapter {np.mean(na):.3f}  p {pa_:.3f}")
ratio = ad / dg; nratio = np.array(na) / np.array(nd); pr = float(np.mean(nratio >= ratio))
print(f"   ring : echo ratio {ratio:.2f} vs null {nratio.mean():.2f}  (p rings favoured {pr:.3f})")
def far(R, b=30): Rf = R.copy(); idx = np.abs(np.subtract.outer(np.arange(R.shape[0]), np.arange(R.shape[1]))) <= b; Rf[idx] = False; return Rf
fd, fdr = lines(far(R), band=30); fa, far_r = lines(far(R), anti=True, band=30); fnd, fna = [], []
for _ in range(200):
    pm = rng.permutation(n); Rp = far(thresh(S[np.ix_(pm, pm)])); fnd.append(lines(Rp, band=30)[0]); fna.append(lines(Rp, anti=True, band=30)[0])
print(f"   long range only (verses 30+ apart), null = whole-book shuffle: echo {fd:.3f} vs {np.mean(fnd):.3f} (p {np.mean(np.array(fnd) >= fd):.3f});  ring {fa:.3f} vs {np.mean(fna):.3f} (p {np.mean(np.array(fna) >= fa):.3f})")
out["recurrence_far"] = dict(echo=fd, echo_null=float(np.mean(fnd)), ring=fa, ring_null=float(np.mean(fna)), ratio=ratio, ratio_null=float(nratio.mean()), p_ratio=pr)
lab = lambda i: f"{keys[i][0]}:{keys[i][1]}"
print("   longest far echoes:", "; ".join(f"{lab(i)} ~ {lab(j)} ({L})" for L, i, j in fdr[:10:2]))
print("   longest far rings: ", "; ".join(f"{lab(i)}..{lab(i + L - 1)} ~ {lab(j)}..{lab(j - L + 1)} ({L})" for L, i, j in far_r[:10:2]))
print("   longest echoes:", "; ".join(f"{lab(i)}… ~ {lab(j)}… ({L} verses)" for L, i, j in druns[:8]))
print("   longest rings: ", "; ".join(f"{lab(i)}…{lab(i + L - 1)} ~ {lab(j)}…{lab(j - L + 1)} ({L})" for L, i, j in aruns[:8]))
out["recurrence"] = dict(echo=dg, echo_null=float(np.mean(nd)), p_echo=pd_, ring=ad, ring_null=float(np.mean(na)), p_ring=pa_,
                         echoes=[(L, lab(i), lab(j)) for L, i, j in druns[:15]], rings=[(L, lab(i), lab(j)) for L, i, j in aruns[:15]])
# controls
Mk, Mt = sbl("Mk"), sbl("Mt"); A, B = cross(Mk, Mt); C = A @ B.T; Rc = thresh(C, 0.995)
cd, _ = lines(Rc); ca, _ = lines(Rc, anti=True); cnull = []
for _ in range(50):
    pm = rng.permutation(C.shape[1]); cnull.append(lines(thresh(C[:, pm], 0.995))[0])
print(f"   control, Mark x Matthew: on parallel lines {cd:.3f} vs shuffled {np.mean(cnull):.3f}  (crossing {ca:.3f})")
km, Mm, _ = verse_vecs(Mk); half = Mm[:300]; Mr = np.vstack([half, half[::-1] * 0.9 + 0.1 * Mm[300:600]]); Sr = Mr @ Mr.T; Rr = thresh(Sr)
rd, _ = lines(Rr); ra, _ = lines(Rr, anti=True)
print(f"   control, Mark 1-300 then the same verses reversed (blurred): crossing lines {ra:.3f}, parallel {rd:.3f}")
out["controls"] = dict(mk_mt_parallel=cd, mk_mt_null=float(np.mean(cnull)), mk_mt_cross=ca, ring_ctrl_cross=ra, ring_ctrl_parallel=rd)
# image
try:
    from PIL import Image, ImageDraw
    sc = 1; W = n * sc + 60; img = Image.new("RGB", (W, W), (250, 248, 242)); dr = ImageDraw.Draw(img); o = 40
    starts = {}
    for i, k in enumerate(keys): starts.setdefault(k[0], i)
    for c, i in starts.items():
        dr.line([(o + i, o), (o + i, o + n)], fill=(225, 220, 205)); dr.line([(o, o + i), (o + n, o + i)], fill=(225, 220, 205)); dr.text((o + i + 1, 5 + (c % 2) * 14), str(c), fill=(90, 80, 60))
    v = np.clip((S - np.quantile(S, 0.9)) / (np.quantile(S, 0.999) - np.quantile(S, 0.9)), 0, 1)
    px = img.load()
    for i in range(n):
        for j in range(n):
            if v[i, j] > 0: g = int(250 - 220 * v[i, j]); px[o + j, o + i] = (g, int(g * 0.95), int(g * 0.8) if i != j else g)
    for L, i, j in druns[:12]:
        dr.line([(o + j, o + i), (o + j + L, o + i + L)], fill=(30, 90, 170), width=2)
    for L, i, j in aruns[:12]:
        dr.line([(o + j, o + i), (o + j - L, o + i + L)], fill=(190, 40, 70), width=2)
    img = img.resize((W * 2, W * 2), Image.NEAREST); os.makedirs(PNG, exist_ok=True); img.save(os.path.join(PNG, "john_recurrence.png"))
    print("   image: john_recurrence.png (blue = longest echoes, red = longest rings)")
except Exception as e: print("   image failed:", e)
# ---------------------------------------------------------------- 3. layers
print("\n3. LINE THE LAYERS UP")
import csv
noise = {r["verse"]: float(r["noise_share"]) for r in csv.DictReader(open(os.path.join(ROOT, "model/out/john_verses.csv")))}
mv = {d["v"]: (len(d["body"]) + (1 if (d["x"] or d["y"] or d["z"]) else 0)) for d in json.load(open(os.path.join(HERE, "movement_path.json")))}
HPV = {"λεγω", "ερχομαι", "βλεπω", "ευρισκω", "λαμβανω", "ακολουθεω", "τρεχω", "φωνεω", "αγω", "φερω", "εισερχομαι", "εξερχομαι", "θεωρεω", "παραλαμβανω", "εγειρω", "αποστελλω", "πεμπω", "μαρτυρεω", "κραζω", "κραυγαζω"}
THEME = {"υδωρ", "αρτος", "φως", "ζωη", "ζαω", "αγαπαω", "αγαπη", "μενω", "δοξα", "δοξαζω", "ωρα", "αληθεια", "σκοτια", "κοσμος", "πνευμα", "αιμα", "σαρξ", "ποιμην", "αμπελος", "θυρα", "οδος", "αναστασις", "πιστευω", "γινωσκω", "οιδα", "μαρτυρια"}
MK = re.search(r"const MARKERS = \{(.*?)\n\};", open(os.path.join(ROOT, "map/template.html"), encoding="utf-8").read(), re.S).group(1)
PTR = set(re.findall(r'"(\d+:\d+)"', MK))
vk = [f"{c}:{v}" for c, v in keys]
T = collections.OrderedDict()
T["sound (noise)"] = np.array([noise.get(k, np.nan) for k in vk])
T["tense (hist. present)"] = np.array([sum(t["pos"][0] == "V" and t["parse"][:2] == "3P" and t["parse"][3] == "I" and t["lem"] in HPV for t in J[k]) / len(J[k]) for k in keys])
T["voice (1st/2nd)"] = np.array([sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in J[k]) / len(J[k]) for k in keys])
T["movement"] = np.array([mv.get(k, 0) for k in vk], float)
T["themes"] = np.array([sum(t["lem"] in THEME for t in J[k]) / len(J[k]) for k in keys])
T["pointers"] = np.array([1.0 if k in PTR else 0.0 for k in vk])
for k, x in T.items():
    if np.isnan(x).any(): x[np.isnan(x)] = np.nanmean(x)
def smooth(x, w=7): return np.convolve(np.pad(x, w // 2, mode="edge"), np.ones(w) / w, mode="valid")
Z = {k: (smooth(x) - smooth(x).mean()) / smooth(x).std() for k, x in T.items()}; names = list(Z); X = np.array([Z[k] for k in names])
C = np.corrcoef(X); shifts = 1000; Cn = np.zeros((shifts, len(names), len(names)))
for s in range(shifts): Xs = np.array([np.roll(x, rng.integers(30, n - 30)) for x in X]); Cn[s] = np.corrcoef(Xs)
print("   correlations between layers (7-verse smoothing; p from circular shifts, two-sided):")
pairs = []
for a in range(len(names)):
    for b in range(a + 1, len(names)):
        p = float(np.mean(np.abs(Cn[:, a, b]) >= abs(C[a, b]))); pairs.append((names[a], names[b], float(C[a, b]), p))
for a, b, r, p in sorted(pairs, key=lambda x: x[3]): print(f"     {a:22s} ~ {b:22s} r {r:+.2f}  p {p:.3f}")
out["layers_corr"] = pairs
def copeaks(X, q=0.85, k=3):
    top = X >= np.quantile(X, q, axis=1, keepdims=True); return top.sum(0) >= k, top
real, top = copeaks(X); cnt = real.sum(); nullc = []
for _ in range(2000):
    Xs = np.array([np.roll(x, rng.integers(30, n - 30)) for x in X]); nullc.append(copeaks(Xs)[0].sum())
pk = float(np.mean(np.array(nullc) >= cnt))
print(f"   verses where 3+ layers are in their top 15% together: {cnt} vs {np.mean(nullc):.1f} expected (circular-shift null), p {pk:.3f}")
# group into moments
mom, cur = [], []
for i in np.flatnonzero(real):
    if cur and i - cur[-1] > 2: mom.append(cur); cur = []
    cur.append(i)
if cur: mom.append(cur)
desc = []
for m in mom:
    lay = [names[a].split(" ")[0] for a in range(len(names)) if top[a, m].any()]
    desc.append((lab(m[0]) + ("–" + lab(m[-1]) if len(m) > 1 else ""), lay))
print("   multi-layer moments:", "; ".join(f"{a} [{'+'.join(l)}]" for a, l in desc))
out["copeaks"] = dict(count=int(cnt), null=float(np.mean(nullc)), p=pk, moments=desc)
# leave out the two known-coupled layers (sound and voice) and the two built from the same pointer set: does co-peaking survive?
sub = [names.index(x) for x in ("tense (hist. present)", "movement", "themes", "pointers")]
r2, _ = copeaks(X[sub], k=2); c2 = r2.sum(); n2 = [copeaks(np.array([np.roll(x, rng.integers(30, n - 30)) for x in X[sub]]), k=2)[0].sum() for _ in range(2000)]
print(f"   without sound and voice: verses where 2+ of tense/movement/themes/pointers peak together {c2} vs {np.mean(n2):.1f}, p {np.mean(np.array(n2) >= c2):.3f}")
out["copeaks_sub"] = dict(count=int(c2), null=float(np.mean(n2)), p=float(np.mean(np.array(n2) >= c2)))
json.dump(out, open(os.path.join(HERE, "self_structure_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
