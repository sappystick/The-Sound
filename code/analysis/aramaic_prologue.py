#!/usr/bin/env python3
"""The prologue in Aramaic (Syriac Peshitta) against the Greek: does it look more like an original in Aramaic?

Burney (1922) argued the prologue was an Aramaic hymn: couplets, rhyme, staircase repetition and word-play that
the Greek blurs.  Tested on John 1:1-18 in each language, each against its OWN baseline (every other 18-verse
window of the Gospels in the same language):
  STAIRCASE   a content word of one line is picked up in the next line
  RHYME       consecutive lines end in the same two letters (Syriac consonants; Greek letters)
  WORD-PLAY   neighbouring words sharing a run of 3 consonants (paronomasia), per 100 word pairs
  CENTRE      where the midpoint (letters) falls
Lines = verse halves split at the Syriac/Greek clause punctuation; when absent, whole verses.
Usage: python3 aramaic_prologue.py <sblgnt> <Peshitta.csv>
"""
import collections, csv, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, PESH = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
SY = re.compile(r"[ܐ-ܯ]")
def syr(w): return "".join(SY.findall(w))
GSTOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον ην ησαν ωσ εστιν".split())
# Gospels by verse, both languages
GR = collections.OrderedDict()
for code, name in (("Mt", "Matthew"), ("Mk", "Mark"), ("Lk", "Luke"), ("Jn", "John")):
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); GR.setdefault((name, int(p[0][2:4]), int(p[0][4:6])), []).append(p[3])
SYV = collections.OrderedDict()
for r in csv.DictReader(open(PESH, encoding="utf-8")):
    if r["Book"] in ("Matthew", "Mark", "Luke", "John") and r["Text"].strip(): SYV[(r["Book"], int(r["Chapter"]), int(r["Verse"]))] = r["Text"].split()
def g_lines(keys):
    L = []
    for k in keys:
        cur = []
        for t in GR.get(k, []):
            w = nrm(t)
            if w: cur.append(w)
            if re.search(r"[,.·;:]$", t) and cur: L.append(cur); cur = []
        if cur: L.append(cur)
    return L
def s_lines(keys):
    L = []
    for k in keys:
        cur = []
        for t in SYV.get(k, []):
            w = syr(t)
            if w: cur.append(w)
            if re.search(r"[܀܂܃܄܆܇.:]", t) and cur: L.append(cur); cur = []
        if cur: L.append(cur)
    return L
def measures(lines, lang):
    stop = GSTOP if lang == "gr" else set()
    content = [[w for w in l if (w not in stop and len(w) > (3 if lang == "gr" else 2))] for l in lines]
    stem = (lambda w: w[:5]) if lang == "gr" else (lambda w: re.sub(r"^[ܘܕܒܠ]", "", w)[:4])
    stair = np.mean([bool({stem(w) for w in a} & {stem(w) for w in b}) for a, b in zip(content, content[1:])]) if len(lines) > 1 else 0
    rhyme = np.mean([a[-1][-2:] == b[-1][-2:] for a, b in zip(lines, lines[1:]) if a and b]) if len(lines) > 1 else 0
    ws = [w for l in lines for w in l]; cons = (lambda w: re.sub(r"[αεηιουω]", "", w)) if lang == "gr" else (lambda w: re.sub(r"[ܐܘܝ]", "", w))
    tri = lambda w: {cons(w)[i:i + 3] for i in range(max(0, len(cons(w)) - 2))}
    play = 100 * np.mean([bool(tri(a) & tri(b)) and stem(a) != stem(b) for a, b in zip(ws, ws[1:])]) if len(ws) > 1 else 0
    return dict(staircase=float(stair), rhyme=float(rhyme), wordplay=float(play))
def baseline(D, liner, lang):
    keys = list(D); vals = collections.defaultdict(list)
    for i in range(0, len(keys) - 18, 9):
        win = keys[i:i + 18]
        if win[0][:2] == ("John", 1) and win[0][2] <= 18: continue
        for k, v in measures(liner(win), lang).items(): vals[k].append(v)
    return vals
pro_keys = [("John", 1, v) for v in range(1, 19)]
print("THE PROLOGUE IN GREEK AND IN SYRIAC (each against every other 18-verse window of the Gospels in its own language)")
for lang, D, liner, lab in (("gr", GR, g_lines, "Greek"), ("sy", SYV, s_lines, "Syriac (Peshitta)")):
    m = measures(liner(pro_keys), lang); base = baseline(D, liner, lang); out[lab] = {}
    for k, v in m.items():
        b = np.array(base[k]); pct = float(np.mean(b < v)); out[lab][k] = dict(value=round(v, 3), baseline_mean=round(float(b.mean()), 3), percentile=round(pct, 3))
        print(f"   {lab:18s} {k:10s} prologue {v:6.3f}   baseline mean {b.mean():6.3f}   percentile {pct:.3f}{'  (top 5%)' if pct >= .95 else ''}")
print("\nSTAIRCASE CHAINS (the word carried from line to line) in each language")
for lang, liner, lab in (("gr", g_lines, "Greek"), ("sy", s_lines, "Syriac")):
    L = liner(pro_keys); stem = (lambda w: w[:5]) if lang == "gr" else (lambda w: re.sub(r"^[ܘܕܒܠ]", "", w)[:4])
    links = []
    for a, b in zip(L, L[1:]):
        sh = {stem(w) for w in a if len(w) > 3} & {stem(w) for w in b if len(w) > 3} - ({"αυτο", "εγεν"} if lang == "gr" else set())
        if sh: links.append(sorted(sh)[0])
    print(f"   {lab}: {len(links)} of {len(L) - 1} line-links: {' > '.join(links[:14])}")
print("\nTHE CENTRE (letters)")
for lab, D, fn in (("Greek", GR, lambda ts: sum(len(nrm(t)) for t in ts)), ("Syriac", SYV, lambda ts: sum(len(syr(t)) for t in ts))):
    L = [fn(D[k]) for k in pro_keys]; T = sum(L); acc = 0
    for v, l in zip(range(1, 19), L):
        if acc + l > T / 2: print(f"   {lab:7s} centre in 1:{v} at {(T / 2 - acc) / l:.2f} of the verse"); break
        acc += l
print("\nKNOWN ARAMAIC PROPOSALS, checked in the Syriac:")
for ref, note in (((1, 5), "Black: 'katelaben' (overcame / grasped) from Aramaic qbl (receive) with a play on 'darken' (aqbel)"), ((1, 14), "'dwelt' (eskēnōsen): Syriac root (aggen / shkn?)"),
                  ((1, 29), "Burney: 'lamb' (amnos) from talyā (lamb / servant / child); the Peshitta has emmrā (lamb)")):
    print(f"   John {ref[0]}:{ref[1]}  Syriac: {' '.join(SYV.get(('John',) + ref, []))}\n      {note}")
json.dump(out, open(os.path.join(HERE, "aramaic_prologue_results.json"), "w"), ensure_ascii=False, indent=1)
