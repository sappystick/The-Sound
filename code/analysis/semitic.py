#!/usr/bin/env python3
"""Translated or composed?  John against Greek known to be translated from Hebrew/Aramaic and Greek known to be
composed in Greek (after R. A. Martin's 'syntactical evidence of Semitic sources', reduced to criteria that need
no grammatical tagging).
Features per 1,000 words (or share): kai share; kai/(kai+de); postpositive particles men, gar, te, oun; sentence-
initial 'and' (kai at sentence start); asyndeton (sentences with no connective in the first two words); mean
sentence length.  Translation Greek: Genesis, 1-4 Kingdoms, Psalms, Daniel (Theodotion), Ezekiel.  Composed Greek:
Wisdom, 2 and 4 Maccabees, Josephus, Philo, Corpus Hermeticum.  A score from a nearest-centroid model trained on
those two groups places every NT book (and John's parts) on a translated <-> composed scale (0 = composed, 1 = translated).
Usage: python3 semitic.py <sblgnt> <lxx-swete/data> <greek dir>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, LXX, GR = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
CONN = {"και", "δε", "γαρ", "ουν", "αλλα", "τοτε", "μεν", "τε", "ωστε", "διο", "ουτωσ", "καιγε", "ειτα", "επειτα", "πλην", "μετα", "οτε", "ωσ", "ινα", "οτι", "εαν", "ει", "καθωσ"}
def feats(raw):
    sents, cur = [], []
    for t in raw:
        w = nrm(t)
        if w: cur.append(w)
        if re.search(r"[.;·;]$", t) and cur: sents.append(cur); cur = []
    if cur: sents.append(cur)
    ws = [w for s in sents for w in s]; n = len(ws) or 1; c = collections.Counter(ws)
    return np.array([c["και"] / n, c["και"] / max(1, c["και"] + c["δε"]), 1000 * c["μεν"] / n, 1000 * c["γαρ"] / n, 1000 * c["τε"] / n, 1000 * c["ουν"] / n,
                     np.mean([s[0] == "και" for s in sents]), np.mean([not (set(s[:2]) & CONN) for s in sents]), np.mean([len(s) for s in sents])])
FN = ["kai share", "kai/(kai+de)", "men /1000", "gar /1000", "te /1000", "oun /1000", "sentence-initial kai", "asyndeton", "sentence length"]
def chunks(t, n=500): return [t[i:i + n] for i in range(0, len(t) - n // 2, n)]
def lxx(b): return [t for l in open(glob.glob(os.path.join(LXX, f"*.{b}.txt"))[0], encoding="utf-8") for p in [l.split(maxsplit=1)] if len(p) == 2 for t in p[1].split()]
def xml(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<(note|bibl|head)[^>]*>.*?</\1>", " ", x, flags=re.S)
    return re.sub(r"<[^>]+>", " ", x).split()
NT = {os.path.basename(f).split("-")[1]: [(int(l[2:4]), int(l[4:6]), l.split()[3]) for l in open(f, encoding="utf-8")] for f in glob.glob(os.path.join(SBL, "*-morphgnt.txt"))}
TR = {k: chunks(lxx(k))[:60] for k in ("Genesis", "Regnorum_I", "Regnorum_III", "Psalmi", "Daniel_Theodotionis_versio", "Ezechiel")}
CO = {"Wisdom": chunks(lxx("Sapientia_Salomonis")), "2 Maccabees": chunks(lxx("Machabaeorum_ii")), "4 Maccabees": chunks(lxx("Machabaeorum_iv")),
      "Josephus": chunks(xml(glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml"))[0]))[:60],
      "Philo": [c for f in sorted(glob.glob(os.path.join(GR, "f1k/data/tlg0018/tlg*/*grc*.xml")))[:3] for c in chunks(xml(f))][:60],
      "Corpus Hermeticum": [c for f in glob.glob(os.path.join(GR, "f1k/data/tlg1286/tlg*/*grc*.xml")) for c in chunks(xml(f))][:60]}
Xt = np.array([feats(c) for v in TR.values() for c in v]); Xc = np.array([feats(c) for v in CO.values() for c in v])
mu, sd = np.vstack([Xt, Xc]).mean(0), np.vstack([Xt, Xc]).std(0) + 1e-9; ct, cc = ((Xt - mu) / sd).mean(0), ((Xc - mu) / sd).mean(0)
def score(X):
    Z = (X - mu) / sd; dt = np.linalg.norm(Z - ct, axis=1); dc = np.linalg.norm(Z - cc, axis=1); return dc / (dt + dc)
acc = (np.mean(score(Xt) > .5) + np.mean(score(Xc) < .5)) / 2
print(f"calibration: the model separates translated from composed chunks with {acc:.0%} accuracy")
print(f"\n{'text':30s} {'score':>6s}  " + "  ".join(f"{f[:10]:>10s}" for f in FN))
def row(lab, chs):
    X = np.array([feats(c) for c in chs]); s = score(X).mean(); m = X.mean(0); out[lab] = dict(score=float(s), **{f: float(v) for f, v in zip(FN, m)})
    print(f"{lab:30s} {s:6.2f}  " + "  ".join(f"{v:10.3f}" for v in m))
for k, v in TR.items(): row(f"[translated] {k}", v)
for k, v in CO.items(): row(f"[composed]   {k}", v)
print()
for b, lab in (("Mk", "Mark"), ("Mt", "Matthew"), ("Lk", "Luke"), ("Ac", "Acts"), ("Ro", "Romans"), ("Heb", "Hebrews"), ("Re", "Revelation"), ("1Jn", "1 John"), ("Jn", "John (whole)")):
    row(lab, chunks([t for *_, t in NT[b]]))
J = NT["Jn"]
row("John: prologue 1:1-18", [[t for c, v, t in J if c == 1 and v <= 18]])
row("John: signs narrative 2-12", chunks([t for c, v, t in J if 2 <= c <= 12]))
row("John: farewell 13-17", chunks([t for c, v, t in J if 13 <= c <= 17]))
row("John: passion and resurrection 18-21", chunks([t for c, v, t in J if c >= 18]))
json.dump(out, open(os.path.join(HERE, "semitic_results.json"), "w"), indent=1)
