#!/usr/bin/env python3
"""Round 19: following the threads.

1. LAMB OR SERVANT?  John 1:29-36 against the Servant song (Isaiah 52:13-53:12) and the Passover lamb (Exodus 12):
   rank of each among all Greek-OT passages of similar size by rare shared words; the 'takes away / bears sin' wording.
2. JOHN 6 AND PASSOVER READINGS: nearest Old Testament chapters to John 6 (rare words), and where Exodus 16 (manna),
   Numbers 11 (quails, 'give us meat') and Isaiah 54-55 ('come, buy bread without money') rank.
3. THE VERTICAL AXIS ('bond of heaven and earth'): ascend / descend, 'from above' / 'from below', 'from heaven'
   per 10,000 words in John against the Synoptics, Paul, Hebrews, Revelation and the Septuagint; and where in John
   they fall.
4. SEVENS: John's 'I am the + noun' predicates, signs (semeia) narrated, and the seven-day opening week, listed.
5. THREE DAYS AND FOUR DAYS in John.
Usage: python3 round19.py <sblgnt> <lxx-swete/data>
"""
import collections, glob, json, math, os, re, sys, unicodedata
SBL, LXX = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
st = lambda w: w[:5]
LV = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); LV.setdefault((b, r[1], r[2]), []).extend(w for w in (nrm(t) for t in p[1].split()) if w)
NT = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for l in open(f, encoding="utf-8"): p = l.split(); NT.setdefault((b, int(p[0][2:4]), int(p[0][4:6])), []).append((p[3], nrm(p[4]), nrm(p[6])))
chap = collections.defaultdict(set)
for (b, c, v), ws in LV.items(): chap[(b, c)] |= {st(w) for w in ws if w not in STOP and len(w) > 3}
df = collections.Counter(s for x in chap.values() for s in x); N = len(chap); idf = {s: math.log(N / n) for s, n in df.items()}
def stems(ws): return {st(w) for w in ws if w not in STOP and len(w) > 3}
def score(A, B): return sum(idf.get(s, 0) for s in A & B if df.get(s, N) < .05 * N) / math.sqrt(len(B) + 1)
def windows(n):
    keys = list(LV); res = []
    for i in range(0, len(keys) - n, max(1, n // 2)):
        w = keys[i:i + n]
        if w[0][0] == w[-1][0]: res.append((f"{w[0][0]} {w[0][1]}:{w[0][2]}", stems([x for k in w for x in LV[k]])))
    return res
def passage(b, c1, v1, c2, v2): return stems([x for k, ws in LV.items() if k[0] == b and (c1, v1) <= (int(k[1]), int(k[2]) if k[2].isdigit() else 0) <= (c2, v2) for x in ws])
def jn(c1, v1, c2, v2): return stems([w for k, ws in NT.items() if k[0] == "Jn" and (c1, v1) <= k[1:] <= (c2, v2) for _, w, _ in ws])
print("1. LAMB OR SERVANT?  John 1:29-36 against 15-verse windows of the Greek Old Testament")
A = jn(1, 29, 1, 36); W = windows(15); sc = sorted(((score(A, s), lab) for lab, s in W), reverse=True)
for lab, (b, c1, v1, c2, v2) in (("Servant song (Isa 52:13-53:12)", ("Isaias", 52, 13, 53, 12)), ("Passover lamb (Exod 12:1-15)", ("Exodus", 12, 1, 12, 15))):
    s = score(A, passage(b, c1, v1, c2, v2)); rank = sum(x > s for x, _ in sc) + 1
    print(f"   {lab:32s} rank {rank:5d} of {len(sc)}  shared rare: {sorted(s_ for s_ in A & passage(b, c1, v1, c2, v2) if df.get(s_, N) < .05 * N)}")
print("   nearest windows:", "; ".join(l for _, l in sc[:6]))
for ref, txt in ((("Isaias", "53", "7"), "Isa 53:7"), (("Isaias", "53", "12"), "Isa 53:12"), (("Isaias", "53", "4"), "Isa 53:4")): print(f"   {txt}: {' '.join(LV.get(ref, []))[:140]}")
print("   John 1:29:", " ".join(t for t, _, _ in NT[("Jn", 1, 29)]))
print("\n2. JOHN 6 AND THE PASSOVER READINGS: nearest chapters")
A6 = jn(6, 1, 6, 71); cs = sorted(((score(A6, s), k) for k, s in chap.items() if len(s) > 40), reverse=True); rk = {k: i + 1 for i, (_, k) in enumerate(cs)}
print("   top:", "; ".join(f"{b} {c}" for _, (b, c) in cs[:8]))
for k in (("Exodus", "16"), ("Numeri", "11"), ("Isaias", "55"), ("Isaias", "54"), ("Psalmi", "77"), ("Nehemiah", "9")):
    if k in rk: print(f"   {k[0]} {k[1]}: rank {rk[k]} of {len(cs)}")
print("\n3. THE VERTICAL AXIS per 10,000 words")
AX = {"ascend / descend": ("αναβαιν", "καταβαιν", "ανεβ", "κατεβ", "αναβεβ", "καταβεβ", "αναβησ", "καταβησ", "αναβα", "καταβα"), "from above / below": ("ανωθεν", "ανω", "κατω"), "from heaven": None}
def axis(toks):
    ws = [w for w in toks]; n = len(ws); r = {}
    for k, pre in AX.items():
        if pre is None: r[k] = 1e4 * sum(1 for a, b in zip(ws, ws[1:]) if a == "εκ" and b.startswith("ουραν")) / n
        else: r[k] = 1e4 * sum(1 for w in ws if (w in pre if k == "from above / below" else w.startswith(pre))) / n
    return r
groups = {"John": ["Jn"], "Matthew, Mark, Luke": ["Mt", "Mk", "Lk"], "Paul": ["Ro", "1Co", "2Co", "Ga", "Eph", "Php", "Col", "1Th"], "Hebrews": ["Heb"], "Revelation": ["Re"]}
for lab, bs in groups.items():
    r = axis([w for k, ws in NT.items() if k[0] in bs for _, w, _ in ws]); print(f"   {lab:22s} " + "   ".join(f"{k} {v:5.1f}" for k, v in r.items()))
r = axis([w for ws in LV.values() for w in ws]); print(f"   {'Septuagint':22s} " + "   ".join(f"{k} {v:5.1f}" for k, v in r.items()))
vv = [f"{c}:{v}" for (b, c, v), ws in NT.items() if b == "Jn" and any(w.startswith(AX["ascend / descend"]) for _, w, _ in ws)]
print(f"   John's ascend/descend verses ({len(vv)}): {', '.join(vv)}")
print("\n4. SEVENS IN JOHN")
pred = []
for (b, c, v), ws in NT.items():
    if b != "Jn": continue
    w = [x for _, x, _ in ws]
    for i in range(len(w) - 3):
        if w[i] == "εγω" and w[i + 1] == "ειμι" and w[i + 2] in ("ο", "η") : pred.append((f"{c}:{v}", w[i + 3] if w[i + 3] not in ("ο", "η", "καλοσ", "αληθινη") else w[i + 4]))
print("   'I am the + noun':", "; ".join(f"{r} {p}" for r, p in pred)); print("   distinct images:", sorted({p for _, p in pred}))
sig = [f"{c}:{v}" for (b, c, v), ws in NT.items() if b == "Jn" and any(l == "σημειον" for _, _, l in ws)]
print(f"   'sign' (semeion) verses ({len(sig)}): {', '.join(sig)}")
print("\n5. THREE DAYS AND FOUR DAYS")
for (b, c, v), ws in NT.items():
    if b == "Jn" and any(l in ("τρεισ", "τεσσαρεσ", "τεταρταιοσ") for _, _, l in ws) and any(l == "ημερα" or l == "τεταρταιοσ" for _, _, l in ws):
        print(f"   John {c}:{v}  {' '.join(t for t, _, _ in ws)[:120]}")
json.dump(out, open(os.path.join(HERE, "round19_results.json"), "w"), ensure_ascii=False, indent=1)
