#!/usr/bin/env python3
"""Move 2 (round 91): Currier A and B as an internal Rosetta, exactly as pre-registered in ROSETTA_PREREG.md.
Usage: python3 mysteries/voynich/rosetta.py <sblgnt dir> <BSB.csv>"""
import collections, csv, glob, json, math, os, re, sys, unicodedata
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ZL = os.path.join(ROOT, "sources/texts/voynich/ZL3b-n.txt"); SBL, BSB = sys.argv[1:3]; rng = np.random.default_rng(91)
K, WIN, NNULL = 60, 10, 2000

def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@=\-]", "", w).strip()
def voynich():
    pages = {}; cur = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h:
            d = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))); cur = h.group(1)
            pages[cur] = dict(I=d.get("I"), L=d.get("L"), lines=[]); continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*]P\d*>\s*(.*)", ln)
        if not m or m.group(1) not in pages: continue
        ws = [c for c in (clean(w) for w in re.split(r"[.\s,]+", m.group(2))) if c and re.fullmatch(r"[a-z]+", c)]
        if ws: pages[m.group(1)]["lines"].append(ws)
    return pages
def nrm(w): w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in w if not unicodedata.combining(c)).replace("ς", "σ"))
def greek_john():
    ch = collections.defaultdict(lambda: collections.defaultdict(list))
    for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"):
        p = l.split(); w = nrm(p[5])
        if w: ch[int(p[0][2:4])][int(p[0][4:6])].append(w)
    return [[v for _, v in sorted(vs.items())] for _, vs in sorted(ch.items())]
def english(book, maxch=999):
    ch = collections.defaultdict(list)
    for r in csv.DictReader(open(BSB, encoding="utf-8")):
        if r["Book"] == book and int(r["Chapter"]) <= maxch:
            ws = re.findall(r"[a-z]+", r["Text"].lower())
            if ws: ch[int(r["Chapter"])].append(ws)
    return [v for _, v in sorted(ch.items())]

# ---- a corpus = list of pages, each a list of lines (lists of words)
def profile(corpus):
    toks = [w for pg in corpus for ln in pg for w in ln]; f = collections.Counter(toks); top = [w for w, _ in f.most_common(K)]
    pos = collections.defaultdict(list)
    for i, w in enumerate(toks): pos[w].append(i)
    pages_with = collections.Counter(w for pg in corpus for w in set(x for ln in pg for x in ln))
    first = collections.Counter(ln[0] for pg in corpus for ln in pg); last = collections.Counter(ln[-1] for pg in corpus for ln in pg)
    def burst(w):
        g = np.diff(pos[w]); return float(np.var(g) / (np.mean(g) ** 2 + 1e-9)) if len(g) > 1 else 0.0
    X = np.array([[math.log(f[w]), burst(w), pages_with[w] / len(corpus), first[w] / f[w], last[w] / f[w]] for w in top])
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    return top, X, f
def ppmi(corpus, top):
    idx = {w: i for i, w in enumerate(top)}; co = np.zeros((K, K)); mg = np.zeros(K)
    for pg in corpus:
        s = [idx.get(w) for ln in pg for w in ln]
        for i, a in enumerate(s):
            if a is None: continue
            mg[a] += 1
            for b in s[max(0, i - WIN):i]:
                if b is not None and b != a: co[a, b] += 1; co[b, a] += 1
    T = co.sum() + 1e-9; pa = co.sum(1) / T
    with np.errstate(divide="ignore", invalid="ignore"):
        P = np.log((co / T) / np.outer(pa, pa)); P[~np.isfinite(P)] = 0
    return np.maximum(P, 0)
IU = np.triu_indices(K, 1)
def score(PA, PB, m): return spearmanr(PA[IU], PB[np.ix_(m, m)][IU]).correlation
def band_perm():
    m = np.arange(K)
    for _ in range(K * 3):
        i = rng.integers(K); j = min(K - 1, max(0, i + rng.integers(-5, 6))); m[i], m[j] = m[j], m[i]
    return m
def rosetta(A, B, name):
    ta, XA, fa = profile(A); tb, XB, fb = profile(B); PA, PB = ppmi(A, ta), ppmi(B, tb)
    D = ((XA[:, None, :] - XB[None, :, :]) ** 2).sum(-1); r, c = linear_sum_assignment(D); m = c[np.argsort(r)]
    S = score(PA, PB, m); null = np.array([score(PA, PB, band_perm()) for _ in range(NNULL)])
    p = float((np.sum(null >= S) + 1) / (NNULL + 1))
    ident = score(PA, PB, np.arange(K))   # frequency-rank alignment alone, for reference
    res = dict(S=round(float(S), 4), null_mean=round(float(null.mean()), 4), null_95=round(float(np.percentile(null, 95)), 4), p=round(p, 4),
               rank_alignment_S=round(float(ident), 4), pairs=[f"{ta[i]}={tb[m[i]]}" for i in range(15)])
    print(f"{name:34s} S {S:.4f}  null {null.mean():.4f} (95% {np.percentile(null, 95):.4f})  p {p:.4f}   rank-only {ident:.4f}")
    return res, (ta, tb, m, PA, PB, XA, XB)

V = voynich(); HA = [p["lines"] for p in V.values() if p["I"] == "H" and p["L"] == "A" and p["lines"]]; HB = [p["lines"] for p in V.values() if p["I"] == "H" and p["L"] == "B" and p["lines"]]
R = {"pages": dict(herbal_A=len(HA), herbal_B=len(HB), tokens_A=sum(len(l) for p in HA for l in p), tokens_B=sum(len(l) for p in HB for l in p))}
# ---- R1 lexical distance
def jsd(a, b):
    fa, fb = collections.Counter(w for p in a for l in p for w in l), collections.Counter(w for p in b for l in p for w in l)
    V_ = set(fa) | set(fb); ta, tb = sum(fa.values()), sum(fb.values()); d = 0.0
    for w in V_:
        x, y = fa[w] / ta, fb[w] / tb; mm = (x + y) / 2
        d += (x * math.log2(x / mm) if x else 0) + (y * math.log2(y / mm) if y else 0)
    return d / 2
nb = R["pages"]["tokens_B"]; ceil = []
for _ in range(50):
    o = list(rng.permutation(len(HA))); half, k = [], 0
    for i in o:
        if k >= nb: break
        half.append(HA[i]); k += sum(len(l) for l in HA[i])
    ceil.append(jsd(half, [HA[i] for i in o if HA[i] not in half]))
R["R1"] = dict(jsd_HA_HB=round(jsd(HA, HB), 4), ceiling_HA_halves=round(float(np.mean(ceil)), 4), ceiling_sd=round(float(np.std(ceil)), 4),
               shared_types_of_B_tokens=round(sum(c for w, c in collections.Counter(w for p in HB for l in p for w in l).items() if w in set(w for p in HA for l in p for w in l)) / nb, 3))
print("R1", R["R1"])
# ---- R2 + controls
GJ = greek_john(); EJ = english("John"); EG = english("Genesis", 21)
R["positive_control_GreekJohn_EnglishJohn"], _ = rosetta(GJ, EJ, "POSITIVE  Greek John ~ English John")
R["negative_control_GreekJohn_EnglishGenesis"], _ = rosetta(GJ, EG, "NEGATIVE  Greek John ~ English Gen")
R["ceiling_HA_odd_even"], _ = rosetta(HA[0::2], HA[1::2], "CEILING   herbal-A odd ~ even")
R["PRIMARY_herbalA_herbalB"], keep = rosetta(HA, HB, "PRIMARY   herbal-A ~ herbal-B")
pc, nc, pr = R["positive_control_GreekJohn_EnglishJohn"], R["negative_control_GreekJohn_EnglishGenesis"], R["PRIMARY_herbalA_herbalB"]
valid = pc["p"] < 0.01 and pc["S"] > nc["S"]
R["method_valid"] = valid
R["decision"] = ("INCONCLUSIVE: method cannot detect a re-encoding even when one exists" if not valid else
                 "SHARED STRUCTURE: Rosetta candidate" if pr["p"] < 0.01 and pr["S"] >= nc["S"] else
                 "NO SHARED STRUCTURE: A and B are not word-for-word re-encodings of the same content" if pr["p"] >= 0.05 else "WEAK")
print("method valid:", valid, "| DECISION:", R["decision"])
json.dump(R, open(os.path.join(HERE, "rosetta_results.json"), "w"), indent=1, ensure_ascii=False)

# =====================================================================================================================
# EXPLORATORY (pre-registered as exploratory): refined graph matching. Start from the profile mapping, then repeatedly
# re-match each A word to the B word whose co-occurrence row (under the current mapping) correlates best with its own,
# using EVEN pages only; then score the final mapping on ODD pages. Null: the same refinement from random starts.
# For the ceiling (herbal-A against itself) the true mapping is the identity, so recovery can be measured directly.
def split(C): return C[0::2], C[1::2]
def refine(PA, PB, m, iters=25):
    for _ in range(iters):
        Bm = PB[:, m]                                   # B rows expressed in A's index order
        Za = (PA - PA.mean(1, keepdims=True)) / (PA.std(1, keepdims=True) + 1e-9); Zb = (Bm - Bm.mean(1, keepdims=True)) / (Bm.std(1, keepdims=True) + 1e-9)
        Sim = Za @ Zb.T / K; r, c = linear_sum_assignment(-Sim); new = c[np.argsort(r)]
        if np.array_equal(new, m): break
        m = new
    return m
def explore(A, B, name, nnull=60):
    Atr, Ate = split(A); Btr, Bte = split(B)
    ta, XA, _ = profile(A); tb, XB, _ = profile(B)
    PAtr, PBtr, PAte, PBte = ppmi(Atr, ta), ppmi(Btr, tb), ppmi(Ate, ta), ppmi(Bte, tb)
    D = ((XA[:, None, :] - XB[None, :, :]) ** 2).sum(-1); r, c = linear_sum_assignment(D); m0 = c[np.argsort(r)]
    m = refine(PAtr, PBtr, m0); S = score(PAte, PBte, m)
    null = np.array([score(PAte, PBte, refine(PAtr, PBtr, rng.permutation(K))) for _ in range(nnull)])
    p = float((np.sum(null >= S) + 1) / (nnull + 1))
    out = dict(S_heldout=round(float(S), 4), null_mean=round(float(null.mean()), 4), null_95=round(float(np.percentile(null, 95)), 4), p=round(p, 4),
               pairs=[f"{ta[i]}={tb[m[i]]}" for i in range(20)])
    if ta == tb or name.startswith("CEILING"):
        tbi = {w: j for j, w in enumerate(tb)}; out["identity_recovery"] = round(float(np.mean([tbi.get(ta[i]) == m[i] for i in range(K)])), 3)
    print(f"[expl] {name:30s} held-out S {S:.4f}  null {null.mean():.4f} (95% {np.percentile(null, 95):.4f})  p {p:.4f}", "recovery " + str(out.get("identity_recovery")) if "identity_recovery" in out else "")
    print("        pairs:", " ".join(out["pairs"][:14]))
    return out
R["EXPLORATORY_refined"] = {
    "positive_GreekJohn_EnglishJohn": explore(GJ, EJ, "POSITIVE Greek~English John"),
    "negative_GreekJohn_EnglishGenesis": explore(GJ, EG, "NEGATIVE Greek John~Eng Gen"),
    "ceiling_HA_vs_HA_shuffled_names": None,
    "herbalA_herbalB": explore(HA, HB, "PRIMARY herbal-A~herbal-B"),
}
# ceiling: herbal-A odd pages against herbal-A even pages, true mapping = identity
def explore_ceiling():
    A, B = HA[0::2], HA[1::2]; return explore(A, B, "CEILING herbal-A odd~even")
R["EXPLORATORY_refined"]["ceiling_HA_vs_HA_shuffled_names"] = explore_ceiling()
json.dump(R, open(os.path.join(HERE, "rosetta_results.json"), "w"), indent=1, ensure_ascii=False)

# =====================================================================================================================
# EXPLORATORY 2 (pre-registered as exploratory): rewrite rules. If A and B are the same vocabulary spelled two ways (a
# dialect or a re-encoding at the affix level), a few systematic prefix/suffix swaps should turn herbal-A's word
# distribution into herbal-B's. Rules are learned greedily on EVEN pages and judged on ODD pages, against
#   - the identity (no rules), - the same-language ceiling (herbal-A odd against token-matched herbal-A even), and
#   - random rules of the same number (how much any rewriting helps by chance).
PRE = ["qo", "ch", "sh", "ok", "ot", "o", "c", "q", "s", "d", "da", "a", "y", "l", "k", "t", ""]
SUF = ["y", "dy", "edy", "eedy", "ey", "eey", "ol", "or", "al", "ar", "aiin", "ain", "iin", "in", "n", "l", "r", "hy", "ody", "chy", ""]
def counts(C): return collections.Counter(w for p in C for l in p for w in l)
def jsdc(fa, fb):
    ta, tb = sum(fa.values()), sum(fb.values()); d = 0.0
    for w in set(fa) | set(fb):
        x, y = fa[w] / ta, fb[w] / tb; mm = (x + y) / 2
        d += (x * math.log2(x / mm) if x else 0) + (y * math.log2(y / mm) if y else 0)
    return d / 2
def apply(fa, rules):
    out = collections.Counter()
    for w, c in fa.items():
        for kind, a, b in rules:
            if kind == "s" and a and w.endswith(a) and len(w) > len(a): w = w[:-len(a)] + b; break
            if kind == "p" and a and w.startswith(a) and len(w) > len(a): w = b + w[len(a):]; break
        out[w] += c
    return out
CANDS = [("s", a, b) for a in SUF if a for b in SUF if b != a] + [("p", a, b) for a in PRE if a for b in PRE if b != a]
def learn(fa, fb, n=12):
    rules = []; cur = jsdc(fa, fb)
    for _ in range(n):
        best = min(CANDS, key=lambda r: jsdc(apply(fa, rules + [r]), fb))
        new = jsdc(apply(fa, rules + [best]), fb)
        if new >= cur - 1e-4: break
        rules.append(best); cur = new
    return rules
Atr, Ate, Btr, Bte = HA[0::2], HA[1::2], HB[0::2], HB[1::2]
fAtr, fAte, fBtr, fBte = counts(Atr), counts(Ate), counts(Btr), counts(Bte)
rules = learn(fAtr, fBtr)
base, after = jsdc(fAte, fBte), jsdc(apply(fAte, rules), fBte)
nb_ = sum(fBte.values()); ceil2 = []
for _ in range(30):
    o = list(rng.permutation(len(Atr))); sub, k = [], 0
    for i in o:
        if k >= nb_: break
        sub.append(Atr[i]); k += sum(len(l) for l in Atr[i])
    ceil2.append(jsdc(fAte, counts(sub)))
rand = [jsdc(apply(fAte, [CANDS[i] for i in rng.choice(len(CANDS), len(rules), replace=False)]), fBte) for _ in range(200)]
gap = base - float(np.mean(ceil2)); closed = (base - after) / gap if gap > 0 else float("nan")
R["EXPLORATORY_rewrite_rules"] = dict(rules=[f"{'-' if k == 's' else ''}{a}{'-' if k == 'p' else ''} -> {'-' if k == 's' else ''}{b}{'-' if k == 'p' else ''}" for k, a, b in rules],
    heldout_jsd_before=round(base, 4), heldout_jsd_after=round(after, 4), same_language_ceiling=round(float(np.mean(ceil2)), 4),
    random_rules_mean=round(float(np.mean(rand)), 4), random_rules_best=round(float(np.min(rand)), 4), share_of_gap_closed=round(closed, 3))
print("[expl] rewrite rules:", R["EXPLORATORY_rewrite_rules"])
json.dump(R, open(os.path.join(HERE, "rosetta_results.json"), "w"), indent=1, ensure_ascii=False)
