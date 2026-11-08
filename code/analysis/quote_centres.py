#!/usr/bin/env python3
"""Do New Testament writers quote from the beginnings, centres and ends of Old Testament books?

Blind quotation finder: every NT formula that announces scripture ('it is written', 'that it might be
fulfilled', 'the scripture says', 'as the prophet said') is followed by the next 25 words; the Greek-OT verse
(with its neighbours) sharing the most rare words is taken as the source if it shares at least 3 rare stems.
No hand-picked list. Each source's position in its book (by words) is compared with random positions in the
same books. Reported for each writer group, with and without the Psalms (an anthology, whose 'centre' is
least likely to mean anything).
Usage: python3 quote_centres.py <sblgnt dir> <lxx-swete/data>
"""
import collections, glob, json, math, os, random, re, sys, unicodedata
import numpy as np
SBL, LXX = sys.argv[1:3]; MINSH = int(sys.argv[3]) if len(sys.argv) > 3 else 3; HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(3); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
content = lambda w: w not in STOP and len(w) > 3
stem = lambda w: w[:5]
LV = []; BOOKWORDS = collections.Counter(); POS = []
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    cur = None
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) != 2: continue
        r = p[0].split("."); key = (b, r[1], r[2]); w = nrm(p[1])
        if key != cur: LV.append([key, [], BOOKWORDS[b]]); cur = key
        if w: LV[-1][1].append(w); BOOKWORDS[b] += 1
df = collections.Counter(s for _, ws, _ in LV for s in {stem(w) for w in ws if content(w)}); N = len(LV)
idf = {s: math.log(N / n) for s, n in df.items()}
inv = collections.defaultdict(list)
for i, (_, ws, _) in enumerate(LV):
    for s in {stem(w) for w in ws if content(w)}:
        if df[s] < 400: inv[s].append(i)
NT = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    NT[b] = [((int(l[2:4]), int(l[4:6])), nrm(l.split()[4])) for l in open(f, encoding="utf-8")]
FORM = [("γεγραπται",), ("γεγραμμενον",), ("γεγραμμενα",), ("πληρωθη",), ("επληρωθη",), ("πληρωθηναι",), ("λεγει", "η", "γραφη"), ("η", "γραφη", "λεγει"), ("ειπεν", "η", "γραφη"),
        ("δια", "του", "προφητου"), ("ησαιασ", "λεγει"), ("δαυιδ", "λεγει"), ("μωυσησ", "γαρ"), ("καθωσ", "ειπεν"), ("λεγει", "κυριοσ"), ("ειρηται",)]
GROUP = {"Mt": "Matthew", "Mk": "Mark", "Lk": "Luke-Acts", "Ac": "Luke-Acts", "Jn": "John", "Heb": "Hebrews", "Re": "Revelation"}
for b in "Ro 1Co 2Co Ga Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm".split(): GROUP[b] = "Paul"
for b in "Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud".split(): GROUP[b] = "Catholic letters"
found = []
for b, toks in NT.items():
    ws = [w for _, w in toks]; seen = set()
    for i in range(len(ws)):
        for f in FORM:
            if tuple(ws[i:i + len(f)]) == f:
                j = i + len(f); q = {stem(w) for w in ws[j:j + 25] if content(w)}
                sc = collections.Counter()
                for s in q:
                    for k in inv.get(s, ()):
                        for kk in (k - 1, k, k + 1):
                            if 0 <= kk < N: sc[kk] += idf[s] / 3 if kk != k else idf[s]
                if not sc: continue
                k, val = sc.most_common(1)[0]
                shared = q & {stem(w) for w in LV[k][1] if content(w)}
                if len(shared) >= MINSH and LV[k][0][0] != "Odae" and LV[k][0][1] != "0" and (LV[k][0], toks[i][0]) not in seen:
                    seen.add((LV[k][0], toks[i][0])); bk = LV[k][0][0]
                    found.append(dict(nt=f"{b} {toks[i][0][0]}:{toks[i][0][1]}", group=GROUP[b], src=f"{bk} {LV[k][0][1]}:{LV[k][0][2]}", book=bk,
                                      pos=round(LV[k][2] / BOOKWORDS[bk], 4), shared=len(shared)))
print(f"blind quotation finder: {len(found)} quotations located")
for g in ("John", "Matthew", "Paul", "Hebrews"):
    ex = [x for x in found if x["group"] == g][:8]; print(f"   {g}: " + "; ".join(f"{x['nt']} -> {x['src']}" for x in ex))
def dist(p, mode): return min(abs(p - x) for x in ((0, .5, 1) if mode == "any" else (.5,)))
def test(rows, mode):
    if len(rows) < 5: return None
    real = float(np.mean([dist(r["pos"], mode) for r in rows])); null = []
    for _ in range(5000): null.append(np.mean([dist(rng.random(), mode) for _ in rows]))
    return dict(n=len(rows), mean=round(real, 4), chance=round(float(np.mean(null)), 4), p=round(float(np.mean(np.array(null) <= real)), 4))
print("\nwhere the quoted verses sit in their books (distance to nearest beginning/centre/end; chance 0.125) and to the centre alone (chance 0.25)")
res = {}
for g in ["John", "Matthew", "Mark", "Luke-Acts", "Paul", "Hebrews", "Catholic letters", "Revelation", "ALL"]:
    rows = [x for x in found if g == "ALL" or x["group"] == g]
    for lab, rr in (("all books", rows), ("without Psalms", [x for x in rows if x["book"] != "Psalmi"])):
        a, c = test(rr, "any"), test(rr, "centre")
        if a: res[f"{g} | {lab}"] = dict(any=a, centre=c); print(f"   {g:17s} {lab:15s} n={a['n']:3d}  begin/centre/end {a['mean']:.3f} (p {a['p']:.3f})   centre {c['mean']:.3f} (p {c['p']:.3f})")
centre_hits = sorted([x for x in found if abs(x["pos"] - .5) < .03 and x["book"] != "Psalmi"], key=lambda x: x["nt"])
print("\nquotations taken from within 3% of a book's centre (Psalms excluded):")
for x in centre_hits: print(f"   {x['nt']:10s} -> {x['src']:28s} at {x['pos']:.3f}")
out = dict(found=found, tests=res, centre_hits=centre_hits)
json.dump(out, open(os.path.join(HERE, "quote_centres_results.json"), "w"), ensure_ascii=False, indent=1)
