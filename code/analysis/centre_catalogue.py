#!/usr/bin/env python3
"""Blind catalogue: what sits at the exact centre of every book of the Hebrew Bible (letters) and of the
Greek New Testament (syllables)?  And are centre verses special?  Test: does the centre verse (with its two
neighbours) contain the divine name (YHWH / Elohim; Theos / Kyrios) more often than a random 3-verse window of
the same book?  Null = 5,000 draws of one random window per book.
Usage: python3 centre_catalogue.py <morphhb/wlc> <sblgnt dir>
"""
import glob, json, os, random, re, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
WLC, SBL = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(1); out = {}
def cons(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת")
heb = {}
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    bk = os.path.basename(f)[:-4]; x = open(f, encoding="utf-8").read(); vs = []
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S):
        ws = [w.replace("/", "") for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2))]
        vs.append((m.group(1), sum(len(cons(w)) for w in ws), any(cons(w).endswith(("יהוה", "אלהים")) or cons(w) in ("יהוה", "אלהים", "אלהי") for w in ws), " ".join(ws)))
    heb[bk] = vs
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
sc = {}
def syl(k):
    if k not in sc:
        try: sc[k] = max(1, len(E.parse_greek(k, "koine")[0]))
        except Exception: sc[k] = 1
    return sc[k]
grk = {}
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]; d = {}
    for l in open(f, encoding="utf-8"):
        p = l.split(); r = f"{b}.{int(p[0][2:4])}.{int(p[0][4:6])}"; k = nrm(p[4])
        e = d.setdefault(r, [r, 0, False, []]); e[1] += syl(k) if k else 0; e[2] |= nrm(p[6]) in ("θεοσ", "κυριοσ"); e[3].append(p[3])
    grk[b] = [(a, s, g, " ".join(t)) for a, s, g, t in d.values()]
def centre(vs):
    T = sum(v[1] for v in vs); acc = 0
    for i, v in enumerate(vs):
        if acc + v[1] > T / 2: return i
        acc += v[1]
def win(vs, i): return any(v[2] for v in vs[max(0, i - 1): i + 2])
res = {}
for lab, corpus in (("Hebrew Bible (letters)", heb), ("Greek NT (syllables)", grk)):
    books = {b: vs for b, vs in corpus.items() if len(vs) >= 20}
    cat = {b: books[b][centre(books[b])] for b in books}
    hits = sum(win(books[b], centre(books[b])) for b in books)
    null = [sum(win(vs, rng.randrange(1, len(vs) - 1)) for vs in books.values()) for _ in range(5000)]
    p = sum(n >= hits for n in null) / len(null)
    print(f"\n{lab}: centre windows with the divine name: {hits} of {len(books)}; random windows average {sum(null) / len(null):.1f}; p = {p:.3f}")
    for b, v in cat.items(): print(f"   {b:6s} centre {v[0]:14s} {v[3][:110]}")
    res[lab] = dict(hits=hits, n=len(books), null=sum(null) / len(null), p=p, catalogue={b: [v[0], v[3]] for b, v in cat.items()})
json.dump(res, open(os.path.join(HERE, "centre_catalogue_results.json"), "w"), ensure_ascii=False, indent=1)

# 'living water' (mayim hayyim) verses and book centres: chance that 2+ of them are centre verses
lw = []
for b, vs in heb.items():
    for i, v in enumerate(vs):
        c = [cons(w) for w in v[3].split()]
        if any(c[j].endswith("מים") and c[j + 1] in ("חיים",) for j in range(len(c) - 1)): lw.append((b, i, v[0], len(vs), i == centre(vs)))
probs = [1 / n for _, _, _, n, _ in lw]
dist = [1.0]
for p in probs: dist = [(dist[k] if k < len(dist) else 0) * (1 - p) + (dist[k - 1] * p if k > 0 else 0) for k in range(len(dist) + 1)]
hits = sum(x[4] for x in lw)
print(f"\n'living water' verses in the Hebrew Bible: {len(lw)}: {[x[2] for x in lw]}")
print(f"   of these, exact book centres (by letters): {[x[2] for x in lw if x[4]]}; chance of {hits}+ = {sum(dist[hits:]):.5f} (before allowing for having looked at many themes)")
res["living_water_centres"] = dict(verses=[x[2] for x in lw], centres=[x[2] for x in lw if x[4]], p=sum(dist[hits:]))
json.dump(res, open(os.path.join(HERE, "centre_catalogue_results.json"), "w"), ensure_ascii=False, indent=1)
