#!/usr/bin/env python3
"""Rhythm and motion with a validated scanner, and structure found without imposing our units.

A. HOMER (control): lines with verbs of rapid motion against other lines: dactyls per line (light, quick feet).
B. JOHN AND THE SYNOPTICS (prose quantity from the same engine): heavy-syllable share in fast-action narrative verses against
   other narrative verses; and each Gospel's overall prose rhythm.
C. UNITS FROM THE TEXT ITSELF (no verses, no chapters): detrended fluctuation analysis (DFA) of the syllable-weight stream
   and of the word-length stream.  Exponent alpha = 0.5 means no memory; above 0.5, long-range structure across scales
   (patterns that repeat at the level of phrases, paragraphs and sections at once).  Against shuffled versions of the
   same text and against Josephus.
Usage: python3 rhythm_dimensions.py <sblgnt> <greek dir>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, GR = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); rng = np.random.default_rng(31); out = {}
import scanner as SC
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def homer(work):
    x = open(glob.glob(os.path.join(GR, f"perseus/data/tlg0012/{work}/*grc*.xml"))[0], encoding="utf-8").read(); res = {}
    for m in re.finditer(r'<div (?:n="(\d+)" type="textpart" subtype="[Bb]ook"|type="textpart" subtype="[Bb]ook" n="(\d+)")>(.*?)(?=<div (?:n="\d+" type="textpart" subtype="[Bb]ook"|type="textpart" subtype="[Bb]ook" n="\d+")>|\Z)', x, re.S):
        bk = int(m.group(1) or m.group(2))
        for a, b in re.findall(r'<l n="(\d+)"[^>]*>(.*?)</l>', m.group(3), re.S): res[(bk, int(a))] = re.sub(r"<[^>]+>", "", b)
    return res
print("A. HOMER: rapid-motion lines against other lines (dactyls per line, of 5)")
FAST = ("αιξ", "αισσ", "ηιξ", "ορμ", "ωρμ", "πετο", "επτα", "ρεε", "ερρε", "κυλινδ", "εκυλ", "πιπτ", "πεσε", "επεσ", "αλτ", "θορ", "εθορ", "δραμ", "τρεχ", "σευ", "εσσυ", "θεε", "εθεε", "θεον", "θεουσ")
SLOW = ("ωθε", "ωσασ", "βασταζ", "ελκ", "φερ", "τλη", "ανεχ", "μογ", "πον", "βαρ", "αχθ", "ερειδ")
for work, lab in (("tlg001", "Iliad"), ("tlg002", "Odyssey")):
    L = homer(work); fast, slow, rest = [], [], []
    for k, line in L.items():
        r, n = SC.scan(line)
        if not r or r[1] > 0: continue
        d = r[0].count("D"); ws = [nrm(t) for t in line.split()]
        if any(w.startswith(FAST) for w in ws): fast.append(d)
        elif any(w.startswith(SLOW) for w in ws): slow.append(d)
        else: rest.append(d)
    fast, slow, rest = map(np.array, (fast, slow, rest)); allv = np.concatenate([fast, rest]); d0 = fast.mean() - rest.mean()
    null = [np.mean(p[:len(fast)]) - np.mean(p[len(fast):]) for p in (rng.permutation(allv) for _ in range(3000))]
    print(f"   {lab}: rapid-motion lines {fast.mean():.3f} dactyls (n {len(fast)})  strain lines {slow.mean():.3f} (n {len(slow)})  other {rest.mean():.3f};  rapid - other {d0:+.3f}, p = {np.mean(np.array(null) >= d0):.4f}")
    out.setdefault("homer", {})[lab] = dict(fast=float(fast.mean()), slow=float(slow.mean()), rest=float(rest.mean()), p=float(np.mean(np.array(null) >= d0)))
print("\nB. THE GOSPELS: heavy-syllable share (prose quantity, same engine)")
JFAST = {"τρεχω", "πιπτω", "αλλομαι", "βαλλω", "σπευδω", "εγειρω", "ανιστημι", "φευγω", "σπαω", "παιω", "ραπιζω", "ελκω", "εξερχομαι"}
for code in ("Jn", "Mk", "Mt", "Lk"):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append((p[3], nrm(p[6]), p[1], p[2]))
    f_, r_, allw = [], [], []
    for k, v in V.items():
        w = SC.prose_weights(" ".join(t for t, _, _, _ in v)); allw += w
        if any(pos.startswith("V") and par[0] in "12" for _, _, pos, par in v): continue
        (f_ if any(l in JFAST for _, l, _, _ in v) else r_).append(np.mean(w) if w else np.nan)
    f_, r_ = np.array([x for x in f_ if x == x]), np.array([x for x in r_ if x == x]); d0 = f_.mean() - r_.mean(); allv = np.concatenate([f_, r_])
    null = [np.mean(p[:len(f_)]) - np.mean(p[len(f_):]) for p in (rng.permutation(allv) for _ in range(3000))]
    print(f"   {code}: overall heavy share {np.mean(allw):.3f};  fast-action verses {f_.mean():.3f} (n {len(f_)}) vs other narrative {r_.mean():.3f}; difference {d0:+.3f}; lighter p = {np.mean(np.array(null) <= d0):.3f}")
    out.setdefault("gospels", {})[code] = dict(heavy=float(np.mean(allw)), diff=float(d0))
print("\nC. STRUCTURE ACROSS SCALES (DFA exponent; 0.5 = no memory)")
def dfa(x, scales=(8, 16, 32, 64, 128, 256, 512)):
    y = np.cumsum(np.asarray(x, float) - np.mean(x)); F = []
    for s in scales:
        n = len(y) // s
        if n < 4: continue
        segs = y[: n * s].reshape(n, s); t = np.arange(s); f = []
        for seg in segs: c = np.polyfit(t, seg, 1); f.append(np.sqrt(np.mean((seg - np.polyval(c, t)) ** 2)))
        F.append((s, np.mean(f)))
    s, f = zip(*F); return float(np.polyfit(np.log(s), np.log(f), 1)[0])
def streams(text_tokens):
    w = SC.prose_weights(" ".join(text_tokens)); wl = [len(nrm(t)) for t in text_tokens if nrm(t)]; return w, wl
def xmlt(p):
    x = open(p, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); return re.sub(r"<[^>]+>", " ", x).split()
CORP = {c: [l.split()[3] for l in open(glob.glob(os.path.join(SBL, f"*-{c}-*"))[0], encoding="utf-8")] for c in ("Jn", "Mk", "Mt", "Lk")}
CORP["Josephus"] = xmlt(glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml"))[0])[:16000]
for lab, toks in CORP.items():
    w, wl = streams(toks[:16000]); a_w, a_l = dfa(w), dfa(wl)
    s_w = np.mean([dfa(rng.permutation(w)) for _ in range(5)]); s_l = np.mean([dfa(rng.permutation(wl)) for _ in range(5)])
    print(f"   {lab:9s} syllable weight alpha {a_w:.3f} (shuffled {s_w:.3f})   word length alpha {a_l:.3f} (shuffled {s_l:.3f})")
    out.setdefault("dfa", {})[lab] = dict(weight=a_w, weight_shuf=float(s_w), wordlen=a_l, wordlen_shuf=float(s_l))
json.dump(out, open(os.path.join(HERE, "rhythm_dimensions_results.json"), "w"), indent=1)
