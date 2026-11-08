#!/usr/bin/env python3
"""Blind test, 1 John and Revelation, and John's signatures across the whole Bible.

A. BLIND TEST with the author's own markers.  John marks his weightiest sayings himself: the double
   'Amen, amen' (amen amen, 25 times, found only in John) and the predicate 'I am'.  Test: do spoken centres
   fall within one verse of such a marker more often than chance?  Run on (i) the 18 units used before and
   (ii) John's 21 chapters (13th-century divisions, chosen by nobody in this study = blind to unit choice).
   Chance = share of each unit's syllables lying within one verse of a marker (Poisson-binomial).
   Note: two of the unit centres (3:11, 5:24) had been seen before this marker was chosen; the chapter run
   is the cleaner test.
B. 1 JOHN and REVELATION: spoken midpoints against scholars' structural hinges; ring test for Revelation's
   seven beatitudes (1:3, 14:13, 16:15, 19:9, 20:6, 22:7, 22:14), as for John's 'I am' sayings.
C. JOHN'S SIGNATURES ACROSS THE BIBLE (Swete LXX + SBLGNT, same crude stem method for both):
   staircase rate per book; absolute 'ego eimi' per book; John's distinctive vocabulary per OT chapter.
Usage: python3 john_unique.py <sblgnt dir> <lxx-swete/data>
"""
import collections, glob, itertools, json, math, os, random, re, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL, LXX = sys.argv[1], sys.argv[2]; cache = {}; rng = random.Random(77); out = {}
def syl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def load(fn):
    return [((int(l[2:4]), int(l[4:6])), l.split()[3], l.split()[6], syl(l.split()[4]), nrm(l.split()[4]))
            for l in open(os.path.join(SBL, fn), encoding="utf-8")]
JN, JN1, RE = load("64-Jn-morphgnt.txt"), load("83-1Jn-morphgnt.txt"), load("87-Re-morphgnt.txt")

# ---------------------------------------------------------------- A. blind test
amen = set();
for i in range(len(JN) - 1):
    if JN[i][2] == "ἀμήν" and JN[i + 1][2] == "ἀμήν": amen.add(JN[i][0])
IAM = {(6, 35), (6, 48), (6, 51), (8, 12), (10, 7), (10, 9), (10, 11), (10, 14), (11, 25), (14, 6), (15, 1), (15, 5)}
MARK = amen | IAM
print(f"A. BLIND TEST: {len(amen)} 'Amen, amen' verses, {len(IAM)} 'I am' verses -> {len(MARK)} marker verses")
def unit_test(units, label):
    probs, hits, rows = [], [], []
    for lab, a, b in units:
        ws = [w for w in JN if a <= w[0] <= b]
        vs = sorted({w[0] for w in ws}); T = sum(w[3] for w in ws)
        near = lambda v: any(x in MARK for x in vs[max(0, vs.index(v) - 1): vs.index(v) + 2])
        p = sum(w[3] for w in ws if near(w[0])) / T
        acc = 0
        for w in ws:
            if acc + w[3] > T / 2: c = w[0]; break
            acc += w[3]
        h = near(c); probs.append(p); hits.append(h); rows.append((lab, f"{c[0]}:{c[1]}", round(p, 2), h))
    k, n = sum(hits), len(probs)
    # Poisson-binomial tail by dynamic programming
    dist = [1.0]
    for p in probs: dist = [ (dist[i] if i < len(dist) else 0) * (1 - p) + (dist[i - 1] * p if i > 0 else 0) for i in range(len(dist) + 1)]
    pv = sum(dist[k:]); exp = sum(probs)
    print(f"   {label}: {k} of {n} centres within one verse of a marker (expected {exp:.1f}); p = {pv:.4f}")
    for r in rows: print(f"      {r[0]:30s} centre {r[1]:6s} chance {r[2]:.2f} {'HIT' if r[3] else ''}")
    return dict(hits=k, n=n, expected=round(exp, 2), p=pv, rows=rows)
UNITS = [("Prologue", (1, 1), (1, 18)), ("First witnesses", (1, 19), (1, 51)), ("Cana", (2, 1), (2, 11)), ("Nicodemus", (3, 1), (3, 21)),
         ("Samaritan woman", (4, 1), (4, 42)), ("Bethesda", (5, 1), (5, 47)), ("Bread of life", (6, 22), (6, 71)), ("Tabernacles", (7, 1), (8, 59)),
         ("Blind man", (9, 1), (9, 41)), ("Shepherd", (10, 1), (10, 21)), ("Lazarus", (11, 1), (11, 44)), ("Footwashing", (13, 1), (13, 30)),
         ("Farewell", (13, 31), (17, 26)), ("Prayer", (17, 1), (17, 26)), ("Pilate", (18, 28), (19, 16)), ("Resurrection", (20, 1), (20, 31))]
out["blind_units"] = unit_test(UNITS, "18 units (commentary boundaries)")
CHS = [(f"Chapter {c}", (c, 1), (c, 99)) for c in range(1, 22)]
out["blind_chapters"] = unit_test(CHS, "21 chapters (medieval divisions, blind to this study)")

# ---------------------------------------------------------------- B. 1 John and Revelation
print("\nB. 1 JOHN AND REVELATION")
def pos_of(ws, ref):
    T = sum(w[3] for w in ws); acc = 0
    for w in ws:
        if w[0] == ref: return acc / T
        acc += w[3]
def midref(ws):
    T = sum(w[3] for w in ws); acc = 0
    for w in ws:
        if acc + w[3] > T / 2: return w[0]
        acc += w[3]
m1 = midref(JN1); p311 = pos_of(JN1, (3, 11))
print(f"   1 John: spoken midpoint {m1[0]}:{m1[1]}; the hinge 'this is the message' 3:11 (cf. 1:5; R.E. Brown's two-part division) at {p311:.3f}")
mr = midref(RE); p12 = pos_of(RE, (12, 1))
print(f"   Revelation: spoken midpoint {mr[0]}:{mr[1]}; chapter 12 (proposed centre of its concentric structure) begins at {p12:.3f}")
BLESS = [(1, 3), (14, 13), (16, 15), (19, 9), (20, 6), (22, 7), (22, 14)]
ps = sorted(pos_of(RE, r) for r in BLESS)
err = sum(abs((ps[i] - .5) + (ps[6 - i] - .5)) for i in range(3))
pb = sum(sum(abs((x[i] - .5) + (x[6 - i] - .5)) for i in range(3)) <= err for x in (sorted(rng.random() for _ in range(7)) for _ in range(50000))) / 50000
print(f"   Revelation's seven beatitudes at {[round(x, 3) for x in ps]}: ring error {err:.3f}, p = {pb:.3f}")
# 1 John's own 'amen'-like markers: 'in this we know' (en touto ginoskomen)
out["1john"] = dict(midpoint=f"{m1[0]}:{m1[1]}", hinge_3_11=round(p311, 3)); out["revelation"] = dict(midpoint=f"{mr[0]}:{mr[1]}", ch12=round(p12, 3), beatitudes=ps, ring_p=pb)

# ---------------------------------------------------------------- C. signatures across the Bible
print("\nC. JOHN'S SIGNATURES ACROSS THE BIBLE")
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
def books():
    for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
        name = os.path.basename(f)[3:-4]; toks = []
        for line in open(f, encoding="utf-8"):
            p = line.split(maxsplit=1)
            if len(p) == 2: toks.append((".".join(p[0].split(".")[1:]), p[1].strip()))
        yield "LXX " + name, toks
    for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
        name = os.path.basename(f).split("-")[1]
        yield "NT " + name, [(f"{int(l[2:4])}.{int(l[4:6])}", l.split()[3]) for l in open(f, encoding="utf-8")]
stair, egoeimi, chap_tokens = {}, {}, collections.defaultdict(list)
for name, toks in books():
    clauses, cur = [], []
    for ref, t in toks:
        w = nrm(t)
        if w: cur.append(w)
        if re.search(r"[,.·;:]$", t) and cur: clauses.append(cur); cur = []
        if name.startswith("LXX") and w: chap_tokens[(name, ref.split(".")[0])].append(w)
    links = sum(1 for a, b in zip(clauses, clauses[1:]) if {x[:5] for x in a[-3:] if x not in STOP and len(x) > 3} & {x[:5] for x in b[:4] if x not in STOP and len(x) > 3})
    if len(clauses) > 30: stair[name] = round(links / (len(clauses) - 1), 3)
    flat = [nrm(t) for _, t in toks]
    egoeimi[name] = sum(1 for a, b in zip(flat, flat[1:]) if a == "εγω" and b == "ειμι")
rank = sorted(stair.items(), key=lambda x: -x[1])
print("   staircase rate (clause hands a word to the next), highest books:")
for n_, v in rank[:12]: print(f"      {n_:32s} {v:.3f}")
print(f"   John's rank: {[n_ for n_, _ in rank].index('NT Jn') + 1} of {len(rank)}")
print("   'ego eimi' (I am) per book, most:", sorted(((v, k) for k, v in egoeimi.items() if v), reverse=True)[:10])
# John's distinctive vocabulary vs the Synoptics, then densest OT chapters
syn = collections.Counter(); jn = collections.Counter()
for code in ("Mt", "Mk", "Lk"):
    for l in open(os.path.join(SBL, glob.glob(os.path.join(SBL, f"*-{code}-morphgnt.txt"))[0].split("/")[-1]), encoding="utf-8"): syn[nrm(l.split()[4])[:6]] += 1
for w in JN: jn[w[4][:6]] += 1
Ns, Nj = sum(syn.values()), sum(jn.values())
lo = {k: math.log((jn[k] + .5) / Nj) - math.log((syn[k] + .5) / Ns) for k in jn if jn[k] >= 12 and k not in {x[:6] for x in STOP}}
dist = [k for k, _ in sorted(lo.items(), key=lambda x: -x[1])[:40]]
print("   John's 40 most distinctive word-stems vs the Synoptics:", " ".join(dist))
dens = sorted(((sum(1 for w in toks if w[:6] in dist) / len(toks), k) for k, toks in chap_tokens.items() if len(toks) >= 150), reverse=True)
print("   Old Testament chapters densest in John's distinctive vocabulary:")
for d, (b, c) in dens[:15]: print(f"      {b[4:]:28s} ch {c:4s} {d:.3f}")
out["signatures"] = dict(staircase_top=rank[:15], john_rank=[n_ for n_, _ in rank].index("NT Jn") + 1, n_books=len(rank),
                         egoeimi=sorted(((v, k) for k, v in egoeimi.items() if v), reverse=True)[:12], distinctive=dist,
                         densest_ot=[(b[4:], c, round(d, 3)) for d, (b, c) in dens[:15]])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "john_unique_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
