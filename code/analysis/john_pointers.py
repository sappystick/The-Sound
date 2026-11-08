#!/usr/bin/env python3
"""Each of John's outward pointers analysed on its own, and a systematic test of John's numbers.

A. POINTER CASES. For every pair (John passage -> Old Testament target):
   1. Wording: rank of the target chapter among all Greek-OT chapters by rare words shared with the passage.
   2. Placement: where the pointer sits in John's spoken time and where the target sits in its own book.
      Do targets fall at beginnings, centres or ends of their books more than uniform chance?
   3. Constellation: do John's targets share rare vocabulary WITH EACH OTHER more than random OT chapters do
      (a coherent hidden thread rather than a scatter)?
   4. Afterlife: which NT chapters outside John come nearest to each target (where else the thread surfaces).
B. JOHN'S NUMBERS (the 153 method made systematic). For each number in John's story: search every Hebrew
   verse holding a word worth that number, score its Greek text by rare words shared with John's scene, and
   compare with the same search for nearby numbers that John did not use. 153 -> Ezekiel 47:10 is the
   positive control: the method must find it before its other results mean anything.
C. GEOMETRY OF 153: triangular number of 17; Archimedes' bound for the square root of 3 (265/153).
Usage: python3 john_pointers.py <sblgnt dir> <lxx-swete/data> <morphhb/wlc>
"""
import collections, glob, json, math, os, random, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(7); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
content = lambda w: w not in STOP and len(w) > 3
stem = lambda w: w[:5]
V = collections.OrderedDict()           # (book, ch, vs) -> words, in order
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2:
            r = p[0].split("."); w = nrm(p[1])
            if w: V.setdefault((b, r[1], r[2]), []).append(w)
NTB = []
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]; NTB.append(b)
    for l in open(f, encoding="utf-8"):
        w = nrm(l.split()[4])
        if w: V.setdefault((b, str(int(l[2:4])), str(int(l[4:6]))), []).append(w)
CH = collections.defaultdict(set); BOOKLEN = collections.Counter(); POS = {}
for (b, c, v), ws in V.items():
    POS[(b, c, v)] = BOOKLEN[b]; BOOKLEN[b] += len(ws)
    CH[(b, c)] |= {stem(w) for w in ws if content(w)}
df = collections.Counter(s for st in CH.values() for s in st); NC = len(CH); idf = {s: math.log(NC / n) for s, n in df.items()}
rare = lambda s: df.get(s, NC) < 0.05 * NC
def verses(b, a, z):
    (c1, v1), (c2, v2) = a, z
    return [k for k in V if k[0] == b and (int(k[1]), int(k[2]) if k[2].isdigit() else 0) >= (c1, v1) and (int(k[1]) if k[1].isdigit() else 0, int(k[2]) if k[2].isdigit() else 0) <= (c2, v2) and k[1].isdigit()]
def stems_of(keys): return {stem(w) for k in keys for w in V[k] if content(w)}
def score(A, Bs): return sum(idf[s] for s in A & Bs if rare(s))
OTCH = [k for k in CH if k[0] not in NTB and len(CH[k]) >= 40]

# ---------------------------------------------------------------- A. pointer cases
P = [("1:1-5 'In the beginning', light", ("Jn", (1, 1), (1, 5)), ("Genesis", (1, 1), (1, 5))),
     ("1:14 'tabernacled among us'", ("Jn", (1, 14), (1, 14)), ("Ecclesiasticus", (24, 8), (24, 12))),
     ("1:29 'Lamb of God'", ("Jn", (1, 29), (1, 36)), ("Exodus", (12, 3), (12, 13))),
     ("1:51 angels ascending and descending", ("Jn", (1, 51), (1, 51)), ("Genesis", (28, 10), (28, 17))),
     ("3:14 serpent lifted up", ("Jn", (3, 14), (3, 15)), ("Numeri", (21, 6), (21, 9))),
     ("4:5-15 the well, living water", ("Jn", (4, 5), (4, 15)), ("Genesis", (29, 1), (29, 12))),
     ("5:5 38 years", ("Jn", (5, 1), (5, 9)), ("Deuteronomium", (2, 13), (2, 16))),
     ("6:31-35 manna; never thirst", ("Jn", (6, 31), (6, 35)), ("Exodus", (16, 13), (16, 21))),
     ("6:35 never hunger, never thirst", ("Jn", (6, 35), (6, 35)), ("Ecclesiasticus", (24, 19), (24, 22))),
     ("7:37-38 rivers of living water", ("Jn", (7, 37), (7, 39)), ("Zacharias", (14, 6), (14, 9))),
     ("7:37-38 rivers (Ezekiel)", ("Jn", (7, 37), (7, 39)), ("Ezechiel", (47, 1), (47, 12))),
     ("8:12 light of the world", ("Jn", (8, 12), (8, 12)), ("Isaias", (60, 1), (60, 3))),
     ("9:7 Siloam, 'Sent'", ("Jn", (9, 6), (9, 11)), ("Isaias", (8, 6), (8, 8))),
     ("10:1-16 the shepherd", ("Jn", (10, 1), (10, 16)), ("Ezechiel", (34, 1), (34, 31))),
     ("13:19 'that I AM'", ("Jn", (13, 19), (13, 19)), ("Isaias", (43, 10), (43, 13))),
     ("15:1-6 the vine", ("Jn", (15, 1), (15, 6)), ("Isaias", (5, 1), (5, 7))),
     ("19:5 'Behold the man'", ("Jn", (19, 5), (19, 5)), ("Zacharias", (6, 11), (6, 13))),
     ("19:23 the seamless tunic", ("Jn", (19, 23), (19, 24)), ("Exodus", (28, 27), (28, 34))),
     ("19:36 no bone broken", ("Jn", (19, 36), (19, 36)), ("Exodus", (12, 43), (12, 47))),
     ("19:37 'they will look on him whom they pierced'", ("Jn", (19, 37), (19, 37)), ("Zacharias", (12, 9), (12, 11))),
     ("20:1-18 seeking him in the garden", ("Jn", (20, 11), (20, 18)), ("Canticum", (3, 1), (3, 5))),
     ("19:41 the garden, the new tomb", ("Jn", (19, 41), (19, 42)), ("Canticum", (4, 12), (4, 16))),
     ("20:22 he breathed on them", ("Jn", (20, 22), (20, 22)), ("Genesis", (2, 7), (2, 8))),
     ("20:22 breath into the dead (Ezekiel)", ("Jn", (20, 22), (20, 22)), ("Ezechiel", (37, 9), (37, 10))),
     ("21:1-14 153 fish", ("Jn", (21, 1), (21, 14)), ("Ezechiel", (47, 9), (47, 10)))]
print("A. JOHN'S POINTERS, EACH ON ITS OWN")
rows = []
for lab, (jb, ja, jz), (ob, oa, oz) in P:
    jk = verses(jb, ja, jz); ok = verses(ob, oa, oz)
    if not jk or not ok: print("   missing:", lab, ob, oa); continue
    A = stems_of(jk); tgt = (ob, str(oa[0]))
    sc = {k: score(A, CH[k]) / math.sqrt(len(CH[k])) for k in OTCH}; rank = sorted(sc, key=lambda k: -sc[k]).index(tgt) + 1 if tgt in sc else None
    shared = sorted(s for s in A & stems_of(ok) if rare(s))
    jpos = POS[jk[0]] / BOOKLEN[jb]; opos = POS[ok[0]] / BOOKLEN[ob]
    rows.append(dict(case=lab, target=f"{ob} {oa[0]}:{oa[1]}", chapter_rank=rank, of=len(OTCH), shared=shared, john_pos=round(jpos, 3), target_pos=round(opos, 3)))
    print(f"   {lab:44s} -> {ob} {oa[0]}:{oa[1]:<3d} wording rank {rank:4d} of {len(OTCH)};  John at {jpos:.2f}, target at {opos:.2f} of its book;  shared rare: {' '.join(shared[:7])}")
ranks = [r["chapter_rank"] for r in rows if r["chapter_rank"]]
print(f"   median wording rank {int(np.median(ranks))} of {len(OTCH)}; in the top 5%: {sum(r <= 0.05 * len(OTCH) for r in ranks)} of {len(ranks)}")
# placement: distance of target position to nearest of {0, 0.5, 1}
d = [min(abs(r["target_pos"] - x) for x in (0, .5, 1)) for r in rows]; real = float(np.mean(d))
null = [np.mean([min(abs(rng.random() - x) for x in (0, .5, 1)) for _ in d]) for _ in range(20000)]
pp = float(np.mean(np.array(null) <= real))
print(f"   placement: targets sit on average {real:.3f} from a beginning, centre or end of their book (uniform chance 0.125); p = {pp:.3f}")
# constellation
tchs = sorted({(r["target"].split()[0], r["target"].split()[1].split(":")[0]) for r in rows})
def coh(chs): return float(np.mean([score(CH[a], CH[b]) / math.sqrt(len(CH[a]) * len(CH[b])) for i, a in enumerate(chs) for b in chs[i + 1:]]))
real_c = coh(tchs); null_c = [coh(rng.sample(OTCH, len(tchs))) for _ in range(1000)]
pc = float(np.mean(np.array(null_c) >= real_c))
print(f"   constellation: John's {len(tchs)} target chapters share rare words with each other: {real_c:.3f} vs random chapter sets {np.mean(null_c):.3f}; p = {pc:.3f}")
# strongest links within the constellation
pairs = sorted(((score(CH[a], CH[b]) / math.sqrt(len(CH[a]) * len(CH[b])), a, b) for i, a in enumerate(tchs) for b in tchs[i + 1:]), reverse=True)[:8]
print("   strongest links between targets:", "; ".join(f"{a[0]} {a[1]} - {b[0]} {b[1]}" for _, a, b in pairs))
# afterlife: nearest NT chapters (not John) to each target
NTCH = [k for k in CH if k[0] in NTB and k[0] != "Jn" and len(CH[k]) >= 40]
after = {}
for r in rows:
    ob, cv = r["target"].split(); oc = cv.split(":")[0]; T = CH[(ob, oc)]
    near = sorted(NTCH, key=lambda k: -score(T, CH[k]) / math.sqrt(len(CH[k])))[:3]; after[r["target"]] = [f"{a} {c}" for a, c in near]
print("   where each target surfaces again in the NT (outside John):")
for t, n in after.items(): print(f"      {t:22s} -> {', '.join(n)}")
out["pointers"] = dict(rows=rows, placement=dict(mean=real, p=pp), constellation=dict(real=real_c, null=float(np.mean(null_c)), p=pc, top_pairs=[(f"{a[0]} {a[1]}", f"{b[0]} {b[1]}") for _, a, b in pairs]), afterlife=after)

# ---------------------------------------------------------------- B. John's numbers
print("\nB. JOHN'S NUMBERS, EACH SEARCHED THE 153 WAY (Hebrew letter values -> Greek text of that verse vs John's scene)")
HV = dict(zip("אבגדהוזחטיכלמנסעפצקרשתךםןףץ", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 20, 40, 50, 80, 90]))
cons = lambda s: "".join(c for c in unicodedata.normalize("NFD", s) if c in HV)
MAPB = dict(Gen="Genesis", Exod="Exodus", Lev="Leviticus", Num="Numeri", Deut="Deuteronomium", Josh="Josue", Judg="Judices", Ruth="Ruth",
            **{"1Sam": "Regnorum_I", "2Sam": "Regnorum_II", "1Kgs": "Regnorum_III", "2Kgs": "Regnorum_IV", "1Chr": "Paralipomenon_I", "2Chr": "Paralipomenon_II"},
            Ezra="Esdras_B", Esth="Esther", Job="Job", Ps="Psalmi", Prov="Proverbia", Song="Canticum", Isa="Isaias", Lam="Threni_seu_Lamentationes",
            Ezek="Ezechiel", Dan="Daniel_Theodotionis_versio", Hos="Osee", Joel="Joel", Amos="Amos", Obad="Abdias", Jonah="Jonas", Mic="Michaeas",
            Nah="Nahum", Hab="Habacuc", Zeph="Sophonias", Hag="Aggaeus", Zech="Zacharias", Mal="Malachias")
byval = collections.defaultdict(set)
for f in glob.glob(os.path.join(WLC, "*.xml")):
    x = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S):
        bk, c, v = m.group(1).split(".")
        if bk not in MAPB: continue
        if bk == "Ps": c = str(int(c) - 1) if 10 <= int(c) <= 146 else c    # Greek psalm numbering, approximately
        for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2)):
            for p in w.split("/") + [w.replace("/", "")]:
                s = cons(p)
                if s: byval[sum(HV[ch] for ch in s)].add((MAPB[bk], c, v))
def greek_ctx(k):
    b, c, v = k; keys = [(b, c, str(int(v) + d)) for d in (-1, 0, 1)] if v.isdigit() else [k]
    return {stem(w) for kk in keys if kk in V for w in V[kk] if content(w)}
gcache = {}
def best_hit(N, A):
    best = (0, None)
    for k in byval.get(N, ()):
        if k not in gcache: gcache[k] = greek_ctx(k)
        s = score(A, gcache[k])
        if s > best[0]: best = (s, k)
    return best
NUMS = [("2:6 six stone jars", 6, (2, 1), (2, 11)), ("2:20 forty-six years to build this temple", 46, (2, 18), (2, 22)),
        ("4:18 five husbands", 5, (4, 16), (4, 19)), ("4:52 the seventh hour", 7, (4, 46), (4, 54)), ("5:2 five porticoes", 5, (5, 1), (5, 4)),
        ("5:5 thirty-eight years", 38, (5, 1), (5, 9)), ("6:7 two hundred denarii", 200, (6, 5), (6, 9)), ("6:9 five loaves, two fish", 5, (6, 8), (6, 13)),
        ("6:13 twelve baskets", 12, (6, 10), (6, 14)), ("6:19 twenty-five or thirty stadia", 25, (6, 16), (6, 21)), ("11:17 four days in the tomb", 4, (11, 17), (11, 20)),
        ("11:18 fifteen stadia", 15, (11, 17), (11, 20)), ("12:5 three hundred denarii", 300, (12, 1), (12, 8)), ("19:39 a hundred pounds of myrrh and aloes", 100, (19, 38), (19, 42)),
        ("21:8 two hundred cubits", 200, (21, 4), (21, 9)), ("21:11 153 fish (control)", 153, (21, 1), (21, 14))]
resB = []
for lab, N, a, z in NUMS:
    A = stems_of(verses("Jn", a, z)); s, k = best_hit(N, A)
    pool = [n for n in range(max(2, N // 2), 2 * N + 3) if n != N and n in byval]
    null = [best_hit(n, A)[0] for n in rng.sample(pool, min(60, len(pool)))]
    p = (sum(x >= s for x in null) + 1) / (len(null) + 1)
    shared = sorted(x for x in A & gcache.get(k, set()) if rare(x)) if k else []
    resB.append(dict(number=N, scene=lab, best=f"{k[0]} {k[1]}:{k[2]}" if k else None, score=round(s, 1), p=round(p, 3), shared=shared))
    print(f"   {lab:44s} best verse {k[0] + ' ' + k[1] + ':' + k[2] if k else '-':28s} p = {p:.3f}  shared: {' '.join(shared[:6])}")
print(f"   numbers (besides the control) pointing beyond chance (p < .05): {[r['scene'] for r in resB[:-1] if r['p'] < .05]}")
out["numbers"] = resB

# ---------------------------------------------------------------- C. geometry
print("\nC. THE GEOMETRY OF 153")
GV = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800]))
tri = [n * (n + 1) // 2 for n in range(1, 30)]
print(f"   153 = triangle of 17 (1+...+17); 17 = 10 + 7. 153 = 1^3 + 5^3 + 3^3 = {1 + 125 + 27}.")
print(f"   Archimedes, Measurement of a Circle: 265/153 = {265 / 153:.6f} < sqrt(3) = {math.sqrt(3):.6f} (the height-to-width ratio of the 'vesica piscis', the fish shape)")
print(f"   John's other numbers that are triangular: {[n for n in (6, 46, 5, 7, 38, 200, 12, 25, 30, 4, 15, 300, 100, 153) if n in tri]}  (chance: {sum(1 for t in tri if t <= 300)} of 300 numbers)")
adam = sum(GV[c] for c in "αδαμ"); vals46 = sorted({w for ws in V.values() for w in ws if sum(GV.get(c, 0) for c in w) == 46})
print(f"   Greek ADAM = {adam} (Augustine's reading of the 46 years of 2:20: the temple of his body = Adam). Distinct Greek Bible words worth 46: {len(vals46)}: {' '.join(vals46[:12])}")
out["geometry"] = dict(adam=adam, words46=vals46)
json.dump(out, open(os.path.join(HERE, "john_pointers_results.json"), "w"), ensure_ascii=False, indent=1, default=str)

# ---------------------------------------------------------------- D. robustness checks
print("\nD. ROBUSTNESS")
# D1 placement with one entry per target chapter (repeats removed)
uniq = {}
for r in rows: uniq.setdefault(r["target"].split(":")[0], r["target_pos"])
d2 = [min(abs(p_ - x) for x in (0, .5, 1)) for p_ in uniq.values()]; real2 = float(np.mean(d2))
null2 = [np.mean([min(abs(rng.random() - x) for x in (0, .5, 1)) for _ in d2]) for _ in range(20000)]
print(f"   placement, one per target chapter ({len(d2)}): mean distance {real2:.3f}; p = {float(np.mean(np.array(null2) <= real2)):.3f}")
for t, p_ in sorted(uniq.items(), key=lambda x: min(abs(x[1] - y) for y in (0, .5, 1))): print(f"      {t:22s} at {p_:.3f}")
# D2 constellation with random chapters drawn from the SAME books as the targets
bybook = collections.defaultdict(list)
for k in OTCH: bybook[k[0]].append(k)
def matched():
    s = []
    for b, c in tchs:
        pool = [k for k in bybook[b] if k not in s] or bybook[b]; s.append(rng.choice(pool))
    return s
null_m = [coh(matched()) for _ in range(1000)]
pm = float(np.mean(np.array(null_m) >= real_c))
print(f"   constellation vs random chapters from the same books: {real_c:.3f} vs {np.mean(null_m):.3f}; p = {pm:.3f}")
# D3 the 153 control: where does Ezekiel 47:10 rank among the verses worth 153?
A = stems_of(verses("Jn", (21, 1), (21, 14))); cand = sorted(((score(A, gcache.get(k) or greek_ctx(k)), k) for k in byval[153]), reverse=True)
ez = [i for i, (_, k) in enumerate(cand) if k[0] == "Ezechiel" and k[1] == "47"]
print(f"   control: Ezekiel 47:10 ranks {ez[0] + 1 if ez else 'absent'} of {len(cand)} verses holding a word worth 153 (by shared rare words with John 21)")
out["robust"] = dict(placement_unique=real2, constellation_matched_p=pm, control_rank=(ez[0] + 1 if ez else None), control_n=len(cand))
json.dump(out, open(os.path.join(HERE, "john_pointers_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
