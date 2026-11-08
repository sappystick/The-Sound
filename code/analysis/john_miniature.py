#!/usr/bin/env python3
"""Is John a miniature of the whole Bible, laying out its true order?

Every test compares John's REAL chapter sequence with the same 21 chapters in shuffled order. If the
sequence of John is a map, the real sequence must do better than shuffled versions of itself.

 1. JOHN-POSITION OF EVERY BOOK: each book is matched (wording, TF-IDF; and sound) to the John chapter it
    most resembles. Does that position follow the ancient book orders?  And the 'John order' of the books
    (books sorted by their John chapter): is it smoother than orders made from shuffled John templates?
 2. CENTRES: does each book's spoken centre (middle 10%) match John's centre more than its other parts do?
 3. STEP-BY-STEP: each book cut into 21 equal spoken parts, part k laid on John chapter k. Does part k
    resemble chapter k more than chance (segment order shuffled)?  Then the whole canon (without John) cut
    into 21 parts under each ancient order: is the canon a scaled-up John?
 4. POINTERS VETTED: each rare-word pointer (nt_pointers.csv) is checked for shared context: do the
    surrounding verses in the NT and in the OT share more rare words than random OT verses do?
Usage: python3 john_miniature.py <sblgnt dir> <lxx-swete/data>
"""
import collections, csv, glob, json, math, os, random, re, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL, LXX = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(21); nrng = np.random.default_rng(21); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
sc = {}
def syl(k):
    if k not in sc:
        try: sc[k] = max(1, len(E.parse_greek(k, "koine")[0]))
        except Exception: sc[k] = 1
    return sc[k]
# book -> list of (ch, vs, normalized word)
B = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    B[b] = [(p[0].split(".")[1], p[0].split(".")[2], nrm(p[1])) for p in (l.split(maxsplit=1) for l in open(f, encoding="utf-8")) if len(p) == 2]
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    B[b] = [(str(int(l[2:4])), str(int(l[4:6])), nrm(l.split()[4])) for l in open(f, encoding="utf-8")]
for b in B: B[b] = [x for x in B[b] if x[2]]
def content(w): return w not in STOP and len(w) > 3
stem = lambda w: w[:5]
# IDF over all chapters of the Bible
chap_sets = collections.defaultdict(set)
for b, ws in B.items():
    for c, v, w in ws:
        if content(w): chap_sets[(b, c)].add(stem(w))
df = collections.Counter(s for st in chap_sets.values() for s in st); NC = len(chap_sets)
idf = {s: math.log(NC / n) for s, n in df.items()}
def vec(words):
    cnt = collections.Counter(stem(w) for w in words if content(w))
    v = {s: (1 + math.log(n)) * idf[s] for s, n in cnt.items()}; nn = math.sqrt(sum(x * x for x in v.values())) or 1
    return {s: x / nn for s, x in v.items()}
def cos(a, b): return sum(x * b.get(s, 0) for s, x in a.items()) if len(a) < len(b) else sum(x * a.get(s, 0) for s, x in b.items())
JCH = [vec([w for c, v, w in B["Jn"] if c == str(k)]) for k in range(1, 22)]
OTHER = [b for b in B if b != "Jn" and len(B[b]) >= 600]

# ---------------------------------------------------------------- 1. John-position of each book
print("1. EVERY BOOK MATCHED TO THE JOHN CHAPTER IT MOST RESEMBLES (wording)")
M = np.array([[cos(vec([w for _, _, w in B[b]]), j) for j in JCH] for b in OTHER])
Z = (M - M.mean(0)) / (M.std(0) + 1e-9)          # remove John chapters that resemble everything
best = Z.argmax(1)                                # 0..20
for k in range(21):
    names = [OTHER[i] for i in range(len(OTHER)) if best[i] == k]
    print(f"   John {k + 1:2d}: {', '.join(names) if names else '-'}")
VAT = "Genesis Exodus Leviticus Numeri Deuteronomium Josue Judices Ruth Regnorum_I Regnorum_II Regnorum_III Regnorum_IV Paralipomenon_I Paralipomenon_II Esdras_A Esdras_B Psalmi Proverbia Canticum Job Sapientia_Salomonis Ecclesiasticus Esther Judith Tobias Osee Amos Michaeas Joel Abdias Jonas Nahum Habacuc Sophonias Aggaeus Zacharias Malachias Isaias Jeremias Baruch Threni_seu_Lamentationes Epistula_Jeremiae Ezechiel Daniel_Theodotionis_versio Machabaeorum_i Machabaeorum_ii Machabaeorum_iii Machabaeorum_iv Psalmi_Salomonis Odae Mt Mk Lk Ac Ro 1Co 2Co Ga Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Re".split()
canon_idx = np.array([VAT.index(b) if b in VAT else len(VAT) for b in OTHER])
def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b)); return float(np.corrcoef(ra, rb)[0, 1])
real_rho = spearman(canon_idx, best)
perm_rho = []
for _ in range(5000):
    p = nrng.permutation(21); perm_rho.append(spearman(canon_idx, p[best]))
p1 = float(np.mean(np.abs(perm_rho) >= abs(real_rho)))
print(f"   does a book's John-position follow its place in the canon (Vaticanus + NT)? rho = {real_rho:+.3f}; shuffled-John templates give |rho| this large in {p1:.1%}")
# John order smoothness vs shuffled templates
BV = [vec([w for _, _, w in B[b]]) for b in OTHER]
D = np.array([[1 - cos(a, b_) for b_ in BV] for a in BV])
def john_order(lab): return sorted(range(len(OTHER)), key=lambda i: (lab[i], -Z[i].max()))
def smooth(o): return sum(D[a, b_] for a, b_ in zip(o, o[1:]))
real_s = smooth(john_order(best)); null_s = []
for _ in range(2000):
    p = nrng.permutation(21); null_s.append(smooth(john_order(p[best])))
ps = float(np.mean(np.array(null_s) <= real_s))
print(f"   'John order' of the books: smoothness {real_s:.2f}; shuffled-John templates as smooth or smoother: {ps:.1%}")
jo = [OTHER[i] for i in john_order(best)]
print("   the John order itself:", " ".join(jo))
out["position"] = dict(by_chapter={k + 1: [OTHER[i] for i in range(len(OTHER)) if best[i] == k] for k in range(21)}, rho=real_rho, p=p1, smooth=real_s, smooth_p=ps, john_order=jo)

# ---------------------------------------------------------------- 2 + 3. centres and step-by-step
def parts(ws, k):
    S = [syl(w) for _, _, w in ws]; T = sum(S); acc = 0; seg = [[] for _ in range(k)]
    for (c, v, w), s in zip(ws, S):
        seg[min(k - 1, int(k * acc / T))].append(w); acc += s
    return seg
print("\n2. CENTRES: does each book's middle tenth resemble John's middle chapters (10-12) more than its other tenths do?")
ranks = []
for b in OTHER:
    seg = parts(B[b], 10); sims = [np.mean([cos(vec(s), JCH[j]) for j in (9, 10, 11)]) - np.mean([cos(vec(s), JCH[j]) for j in range(21)]) for s in seg]
    ranks.append(sorted(sims, reverse=True).index((sims[4] + sims[5]) / 2 if False else sims[4]) + 1)   # rank of the 5th tenth (just before the midpoint)
    # use the tenth that contains the midpoint: index 4 ends at 0.5; index 5 starts there; take the better of the two
mean_rank = float(np.mean(ranks))
print(f"   average rank of the central tenth among the 10 tenths of each book: {mean_rank:.2f} (chance 5.5; 1 = centre always most John-centre-like)")
out["centres"] = dict(mean_rank=mean_rank, n=len(ranks))
print("\n3. STEP-BY-STEP: book cut into 21 spoken parts; part k laid on John chapter k")
def diag_test(ws, R=500):
    seg = [vec(s) for s in parts(ws, 21)]; Mx = np.array([[cos(s, j) for j in JCH] for s in seg])
    Mx = (Mx - Mx.mean(0)) / (Mx.std(0) + 1e-9); real = float(np.trace(Mx))
    null = [float(Mx[nrng.permutation(21), range(21)].sum()) for _ in range(R)]
    return real, float(np.mean(np.array(null) >= real))
diag = {}
for b in OTHER:
    if len(B[b]) >= 4000: diag[b] = diag_test(B[b])
hits = [b for b, (r, p) in diag.items() if p < .05]
print(f"   books tested: {len(diag)}; part k matches John chapter k beyond chance in {len(hits)} (expected by luck {0.05 * len(diag):.1f}): {hits}")
out["step_books"] = {b: dict(score=round(r, 2), p=p) for b, (r, p) in diag.items()}
NTO = "Mt Mk Lk Ac Ro 1Co 2Co Ga Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Re".split()
HEB = "Genesis Exodus Leviticus Numeri Deuteronomium Josue Judices Regnorum_I Regnorum_II Regnorum_III Regnorum_IV Isaias Jeremias Ezechiel Osee Joel Amos Abdias Jonas Michaeas Nahum Habacuc Sophonias Aggaeus Zacharias Malachias Psalmi Proverbia Job Canticum Ruth Threni_seu_Lamentationes Esther Daniel_Theodotionis_versio Esdras_B Paralipomenon_I Paralipomenon_II".split()
canon = {}
for lab, order in (("Whole Bible, Vaticanus order + NT (without John)", VAT), ("Hebrew order + NT (without John)", HEB + NTO),
                   ("New Testament (without John)", NTO), ("Old Testament, Vaticanus order", [b for b in VAT if b not in NTO])):
    ws = [x for b in order if b in B for x in B[b]]; r, p = diag_test(ws, 2000); canon[lab] = dict(score=round(r, 2), p=p)
    print(f"   {lab:50s} diagonal score {r:+.2f}; shuffled parts as high: {p:.1%}")
out["step_canon"] = canon

# ---------------------------------------------------------------- 4. pointers vetted
print("\n4. POINTERS VETTED: does the NT verse's neighbourhood share rare words with the OT verse's neighbourhood?")
vix = {}
for b, ws in B.items():
    order = []; d = collections.OrderedDict()
    for c, v, w in ws: d.setdefault((c, v), []).append(w)
    keys = list(d); vix[b] = (keys, d)
def ctx(b, c, v, rad=2):
    keys, d = vix[b]
    if (c, v) not in d: return set()
    i = keys.index((c, v)); return {stem(w) for k in keys[max(0, i - rad): i + rad + 1] for w in d[k] if content(w)}
allv = [(b, k) for b in B if b not in NTO and b != "Jn" for k in vix[b][0]]
def ov(a, b_, skip): return sum(idf.get(s, 0) for s in (a & b_) if s != skip and df.get(s, 0) < NC * 0.05)
echoes = []; rows = list(csv.DictReader(open(os.path.join(HERE, "nt_pointers.csv"), encoding="utf-8")))
name = {}
for r in rows:
    c, v = r["ref"].split(":"); A = ctx(r["book"], c, v); best_ = None
    for loc in r["lxx"].split("; "):
        bk, cv = loc.rsplit(" ", 1); oc, ovs = cv.split(":")
        if bk not in vix: continue
        real = ov(A, ctx(bk, oc, ovs), stem(r["lemma"]))
        null = [ov(A, ctx(x[0], *x[1]), stem(r["lemma"])) for x in rng.sample(allv, 300)]
        p = (sum(n >= real for n in null) + 1) / 301
        if best_ is None or p < best_[1]: best_ = (loc, p, round(real, 1), sorted((A & ctx(bk, oc, ovs)) - {stem(r["lemma"])})[:8])
    if best_ and best_[1] <= 0.01: echoes.append(dict(nt=f"{r['book']} {r['ref']}", word=r["word"], ot=best_[0], p=round(best_[1], 4), shared=best_[3]))
print(f"   {len(echoes)} of {len(rows)} pointers have a shared context beyond chance (p <= 0.01; about {0.01 * len(rows):.0f}-{0.02 * len(rows):.0f} expected by luck, given up to 3 targets each)")
for e in sorted(echoes, key=lambda e: e["p"])[:40]: print(f"      {e['nt']:9s} {e['word']:16s} -> {e['ot']:28s} p={e['p']:.4f} shared: {' '.join(e['shared'])}")
with open(os.path.join(HERE, "nt_echoes.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["nt", "word", "ot", "p", "shared"]); w.writeheader()
    for e in echoes: w.writerow({**e, "shared": " ".join(e["shared"])})
out["echoes"] = echoes
json.dump(out, open(os.path.join(HERE, "john_miniature_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
