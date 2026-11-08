#!/usr/bin/env python3
"""Why does a shared rare phrase sit at the same fraction of both verses?  Every angle, each with its own control.

Effect: for two verses (in different books) sharing a rare phrase, |qA - qB| (relative position of the phrase
inside each verse) is smaller than under random pairing.

A. SLOT vs ECHO (the decisive test). Does each phrase simply have a habitual slot (some phrases open sentences,
   others close them)?  For phrases with 4+ occurrences: is a cross-book PAIR closer than two occurrences of
   the same phrase drawn at random?  If not, the effect is the phrase's slot (language), not pairing (echo).
B. GRADIENT: pairs whose verses share more rare words (quotation-like) against pairs sharing only this phrase.
C. WHERE: same chapter, same book, same testament, NT~OT (quotation), OT~OT parallels.
D. WHICH SLOT: does the effect come from verse openings, middles or endings?
E. LENGTH: short against long verses.
F. OUTSIDE THE BIBLE: the same measure in Josephus' Antiquities (sentences, across different books).
G. HEBREW: the same measure in the Hebrew Bible (lemma bigrams, unpointed).
Usage: python3 micro_verse.py <sblgnt> <lxx-swete/data> <morphhb/wlc> <josephus Ant xml>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC, JOS = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(3); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ εαν αν οσ ουτοσ τουτο παντα πασ".split())
NTB = set()
def greek_units():
    U = collections.OrderedDict()
    for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
        b = os.path.basename(f)[3:-4]
        if b.endswith("translatio_Graeca"): continue
        for l in open(f, encoding="utf-8"):
            p = l.split(maxsplit=1)
            if len(p) == 2: r = p[0].split("."); U.setdefault((b, r[1], r[2]), []).append(nrm(p[1]))
    for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
        b = os.path.basename(f).split("-")[1]; NTB.add(b)
        for l in open(f, encoding="utf-8"): U.setdefault((b, str(int(l[2:4])), str(int(l[4:6]))), []).append(nrm(l.split()[4]))
    return {k: [w for w in v if w] for k, v in U.items()}
def phrase_index(U, key=lambda w: w[:5], content=lambda w: w not in STOP and len(w) > 3):
    occ = collections.defaultdict(list); vstems = {}
    for k, ws in U.items():
        c = [(i, key(w)) for i, w in enumerate(ws) if content(w)]; vstems[k] = {s for _, s in c}
        for (i, a), (j, b) in zip(c, c[1:]):
            if j - i <= 3: occ[(a, b)].append((k, i / max(1, len(ws) - 1), len(ws)))
    return occ, vstems
def pairs(occ, lo=2, hi=12, cross=True):
    P = []
    for ph, v in occ.items():
        if lo <= len(v) <= hi:
            for x in range(len(v)):
                for y in range(x + 1, len(v)):
                    if (v[x][0][0] != v[y][0][0]) or not cross: P.append((ph, v[x], v[y]))
    return P
def effect(P, R=200):
    if len(P) < 30: return None
    a = np.array([x[1][1] for x in P]); b = np.array([x[2][1] for x in P]); d = float(np.mean(abs(a - b)))
    nd = np.array([np.mean(abs(a - rng.permutation(b))) for _ in range(R)])
    return dict(n=len(P), obs=round(d, 4), random=round(float(nd.mean()), 4), ratio=round(d / nd.mean(), 3), p=float(np.mean(nd <= d)))
def show(lab, e):
    if e: print(f"   {lab:44s} n={e['n']:6d}  |qA-qB| {e['obs']:.3f} vs random {e['random']:.3f}  (ratio {e['ratio']:.2f})  p={e['p']:.3f}")
    else: print(f"   {lab:44s} too few pairs")
    return e
U = greek_units(); occ, vst = phrase_index(U); P = pairs(occ)
print("GREEK BIBLE (Septuagint + NT)"); out["base"] = show("all cross-book pairs", effect(P))

print("\nA. SLOT vs ECHO: are pairs closer than two random occurrences of the SAME phrase?")
real, slot = [], []
for ph, v in occ.items():
    if 4 <= len(v) <= 30:
        qs = np.array([o[1] for o in v]); books = [o[0][0] for o in v]
        for x in range(len(v)):
            for y in range(x + 1, len(v)):
                if books[x] != books[y]: real.append(abs(qs[x] - qs[y]))
        for _ in range(len(v)):
            i, j = rng.choice(len(v), 2, replace=False); slot.append(abs(qs[i] - qs[j]))
real, slot = np.array(real), np.array(slot)
allq = np.array([o[1] for v in occ.values() if 4 <= len(v) <= 30 for o in v])
rand = np.mean(abs(rng.choice(allq, 50000) - rng.choice(allq, 50000)))
boot = [np.mean(rng.choice(real, len(real))) - np.mean(rng.choice(slot, len(slot))) for _ in range(500)]
print(f"   cross-book pairs {real.mean():.3f} | random pairs of the same phrase (its slot) {slot.mean():.3f} | any two phrases {rand:.3f}")
print(f"   echo beyond slot (pairs - slot): {real.mean() - slot.mean():+.4f}, 95% interval [{np.percentile(boot, 2.5):+.4f}, {np.percentile(boot, 97.5):+.4f}]")
out["slot_vs_echo"] = dict(pairs=float(real.mean()), slot=float(slot.mean()), any=float(rand))

print("\nB. GRADIENT: pairs whose verses share more rare words")
df = collections.Counter(s for st in vst.values() for s in st); NV = len(vst)
groups = collections.defaultdict(list)
for x in P:
    shared = len({s for s in vst[x[1][0]] & vst[x[2][0]] if df[s] < 0.001 * NV}) - 2
    groups[min(max(shared, 0), 4)].append(x)
for g in sorted(groups): out[f"gradient_{g}"] = show(f"other rare words shared: {g}{'+' if g == 4 else ''}", effect(groups[g]))

print("\nC. WHERE the two verses are")
def where(x):
    a, b = x[1][0], x[2][0]; ta, tb = a[0] in NTB, b[0] in NTB
    return "NT ~ OT (quotation)" if ta != tb else ("NT ~ NT" if ta else "OT ~ OT")
W = collections.defaultdict(list)
for x in P: W[where(x)].append(x)
for k, v in W.items(): out[f"where_{k}"] = show(k, effect(v))
same_book = pairs(occ, cross=False); sb = [x for x in same_book if x[1][0][0] == x[2][0][0] and x[1][0][1] != x[2][0][1]]; sc = [x for x in same_book if x[1][0][:2] == x[2][0][:2] and x[1][0] != x[2][0]]
show("same book, different chapter", effect(sb)); show("same chapter (refrains)", effect(sc))

print("\nD. WHICH SLOT drives it (position of the phrase in verse A)")
for lab, lo, hi in (("opening (q < 0.2)", 0, .2), ("middle (0.2-0.8)", .2, .8), ("ending (q > 0.8)", .8, 1.01)):
    sel = [x for x in P if lo <= x[1][1] < hi]; e = effect(sel)
    if e: print(f"   {lab:22s} n={e['n']:6d}  verse B within 0.1 of verse A: {np.mean([abs(x[1][1] - x[2][1]) < .1 for x in sel]):.1%} (random {np.mean(abs(np.array([x[1][1] for x in sel]) - rng.permutation(np.array([x[2][1] for x in P]))[:len(sel)]) < .1):.1%})")

print("\nE. LENGTH")
for lab, lo, hi in (("short verses (< 15 words)", 0, 15), ("medium (15-30)", 15, 30), ("long (> 30)", 30, 999)):
    show(lab, effect([x for x in P if lo <= x[1][2] < hi and lo <= x[2][2] < hi]))

print("\nF. OUTSIDE THE BIBLE: Josephus, Antiquities (sentence units, across different books)")
x = open(JOS, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
JU = collections.OrderedDict(); book = "0"
for piece in re.split(r'(<div[^>]*subtype="book"[^>]*n="[^"]+")', x):
    m = re.search(r'subtype="book"[^>]*n="([^"]+)"', piece)
    if m and piece.startswith("<div"): book = m.group(1); continue
    text = re.sub(r"<[^>]+>", " ", piece)
    for i, s in enumerate(re.split(r"[.;·]", text)):
        ws = [nrm(w) for w in s.split()]; ws = [w for w in ws if w]
        if len(ws) >= 5: JU[(f"Ant{book}", "0", str(len(JU)))] = ws
jocc, _ = phrase_index(JU); out["josephus"] = show("Josephus sentences", effect(pairs(jocc)))

print("\nG. HEBREW BIBLE (lemma bigrams, unpointed)")
HU = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    bk = os.path.basename(f)[:-4]; xx = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)">(.*?)</verse>', xx, re.S):
        HU[(bk, m.group(1), m.group(2))] = [re.sub(r"[^0-9]", "", lm.split("/")[-1]) or "x" for lm in re.findall(r'lemma="([^"]*)"', m.group(3))]
hcommon = {s for s, _ in collections.Counter(w for v in HU.values() for w in v).most_common(40)}
hocc, _ = phrase_index(HU, key=lambda w: w, content=lambda w: w not in hcommon)
out["hebrew"] = show("Hebrew verses", effect(pairs(hocc)))
json.dump(out, open(os.path.join(HERE, "micro_verse_results.json"), "w"), indent=1, default=str)

print("\nH. BLIND PARALLEL DETECTOR (from B): John's verses sharing a rare phrase in the same slot plus 2+ other rare words")
seen = set(); rows = []
for ph, a, b in P:
    if "Jn" not in (a[0][0], b[0][0]) or a[0][0] == b[0][0]: continue
    j, o = (a, b) if a[0][0] == "Jn" else (b, a)
    shared = {s for s in vst[j[0]] & vst[o[0]] if df[s] < 0.003 * NV}
    if len(shared) >= 3 and abs(j[1] - o[1]) < 0.15 and (j[0], o[0]) not in seen:
        seen.add((j[0], o[0])); rows.append((len(shared), j[0], o[0], sorted(shared)))
syn = {"Mt", "Mk", "Lk"}
for n, j, o, s in sorted(rows, key=lambda r: -r[0]):
    tag = "Synoptic parallel" if o[0] in syn else ("OT" if o[0] not in NTB else "other NT")
    print(f"   Jn {j[1]}:{j[2]:<3s} ~ {o[0]} {o[1]}:{o[2]:<4s} [{tag}] shared rare stems {n}: {' '.join(s[:8])}")
out["john_parallels"] = [(f"Jn {j[1]}:{j[2]}", f"{o[0]} {o[1]}:{o[2]}", n, s) for n, j, o, s in rows]
json.dump(out, open(os.path.join(HERE, "micro_verse_results.json"), "w"), indent=1, default=str)
