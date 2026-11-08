#!/usr/bin/env python3
"""Egypt and John, tested on texts: does John's vocabulary lean toward Alexandria and the Hermetic writings?

Corpora (all Greek): Egypt / Alexandria = Philo (Alexandrian Jew, d. c. 50 AD), Wisdom of Solomon (Alexandria,
1st c. BC), Corpus Hermeticum (Egyptian Hermetic tractates, 1st-3rd c. AD; mostly LATER than John).
Palestine / Jerusalem = Sirach (Jerusalem, c. 180 BC), Josephus' Antiquities (Jerusalem-born, written in Rome),
1-2 Maccabees.  Reference = Genesis 1-3 (Greek).
Test: words distinctive of John against Matthew, Mark and Luke, and words distinctive of those three against
John. Each corpus's 'lean' = how much more of John's distinctive vocabulary it uses than of the Synoptics'.
95% intervals by resampling the distinctive word lists.  Also: John 3 (born from above) against Corpus
Hermeticum XIII (on rebirth), and the prologue against the Poimandres (CH I).
Usage: python3 alexandria_test.py <sblgnt> <lxx-swete/data> <josephus Ant xml> <philo dir> <hermetica dir>
"""
import collections, glob, json, math, os, random, re, sys, unicodedata
import numpy as np
SBL, LXX, JOS, PHILO, HERM = sys.argv[1:6]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(9); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
stem = lambda w: w[:5]
def words(text): return [nrm(w) for w in text.split() if nrm(w)]
def xmltext(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    return re.sub(r"<[^>]+>", " ", x)
nt = {}
for f in glob.glob(os.path.join(SBL, "*-morphgnt.txt")):
    b = os.path.basename(f).split("-")[1]; nt[b] = [((int(l[2:4]), int(l[4:6])), nrm(l.split()[4])) for l in open(f, encoding="utf-8")]
def lxx(book, chs=None):
    f = glob.glob(os.path.join(LXX, f"*.{book}.txt"))[0]; ws = []
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2 and (chs is None or int(p[0].split(".")[1]) in chs): ws += words(p[1])
    return ws
herm_files = {re.search(r"<ti:title[^>]*>([^<]*)", open(os.path.join(d, "__cts__.xml"), encoding="utf-8").read()).group(1): glob.glob(os.path.join(d, "*grc*.xml"))[0]
              for d in sorted(glob.glob(os.path.join(HERM, "tlg*"))) if glob.glob(os.path.join(d, "*grc*.xml"))}
CORP = {"Philo (Alexandria)": [w for f in glob.glob(os.path.join(PHILO, "tlg*/*grc*.xml")) for w in words(xmltext(f))],
        "Wisdom of Solomon (Alexandria)": lxx("Sapientia_Salomonis"),
        "Corpus Hermeticum (Egypt)": [w for f in herm_files.values() for w in words(xmltext(f))],
        "Sirach (Jerusalem)": lxx("Ecclesiasticus"),
        "Josephus, Antiquities (Jerusalem/Rome)": words(xmltext(JOS)),
        "1-2 Maccabees (Judea)": lxx("Machabaeorum_i") + lxx("Machabaeorum_ii"),
        "Genesis 1-3 (reference)": lxx("Genesis", {1, 2, 3})}
for k, v in CORP.items(): print(f"   {k:40s} {len(v):>9,} words")
JN = [w for _, w in nt["Jn"]]; SYN = [w for b in ("Mt", "Mk", "Lk") for _, w in nt[b]]
cj = collections.Counter(stem(w) for w in JN if w not in STOP and len(w) > 3); cs = collections.Counter(stem(w) for w in SYN if w not in STOP and len(w) > 3)
Nj, Ns = sum(cj.values()), sum(cs.values())
lo = {s: math.log((cj[s] + .5) / Nj) - math.log((cs[s] + .5) / Ns) for s in set(cj) | set(cs) if cj[s] + cs[s] >= 10}
JD = [s for s, v in sorted(lo.items(), key=lambda x: -x[1])[:80]]; SD = [s for s, v in sorted(lo.items(), key=lambda x: x[1])[:80]]
print("   John's most distinctive stems:", " ".join(JD[:30])); print("   Synoptics' most distinctive:", " ".join(SD[:30]))
res = {}
print("\nLEAN TOWARD JOHN (log ratio of John-distinctive to Synoptic-distinctive vocabulary; >0 = closer to John)")
for k, ws in CORP.items():
    c = collections.Counter(stem(w) for w in ws); n = len(ws)
    def lean(jd, sd): return math.log((sum(c[s] for s in jd) + 1) / (sum(c[s] for s in sd) + 1))
    real = lean(JD, SD); boots = [lean(list(rng.choice(JD, len(JD))), list(rng.choice(SD, len(SD)))) for _ in range(2000)]
    lo_, hi_ = np.percentile(boots, [2.5, 97.5]); res[k] = dict(lean=round(real, 3), ci=[round(lo_, 3), round(hi_, 3)])
    print(f"   {k:40s} {real:+.2f}  [{lo_:+.2f}, {hi_:+.2f}]")
out["lean"] = res; out["john_distinctive"] = JD; out["synoptic_distinctive"] = SD
# targeted: John 3 vs Corpus Hermeticum XIII on rebirth; prologue vs Poimandres
def vec(ws):
    c = collections.Counter(stem(w) for w in ws if w not in STOP and len(w) > 3); n = math.sqrt(sum(v * v for v in c.values())); return {k: v / n for k, v in c.items()}
def cos(a, b): return sum(v * b.get(k, 0) for k, v in a.items())
ht = {t: words(xmltext(f)) for t, f in herm_files.items()}
for lab, seg in (("John 3:1-21 (born again / from above)", [w for r, w in nt["Jn"] if (3, 1) <= r <= (3, 21)]), ("John 1:1-18 (prologue)", [w for r, w in nt["Jn"] if r <= (1, 18)])):
    v = vec(seg); sims = sorted(((cos(v, vec(ws)), t) for t, ws in ht.items() if len(ws) > 300), reverse=True)
    shared = sorted(set(vec(seg)) & set(vec(ht[sims[0][1]])))[:25]
    print(f"\n   {lab}: nearest Hermetic tractates: " + "; ".join(f"{t[:45]} ({s:.3f})" for s, t in sims[:4]))
    print("      shared stems with the nearest:", " ".join(shared))
    out[lab] = [(t, round(s, 3)) for s, t in sims[:6]]
# phrase checks
P = {"light and life (phos kai zoe)": r"φωσ και ζωη|ζωη και φωσ", "rebirth (palingenesia)": r"παλιγγενεσια", "born from above / again (gennao anothen)": r"γεννηθη ανωθεν|ανωθεν γεννηθ",
     "the Logos ... son of God": r"λογοσ υιοσ θεου|υιοσ θεου λογοσ", "logos of god": r"λογοσ θεου|θεου λογοσ"}
print("\nPHRASES")
for lab, pat in P.items():
    row = {k: len(re.findall(pat, " ".join(ws))) for k, ws in list(CORP.items()) + [("John", JN), ("Synoptics", SYN)]}
    out.setdefault("phrases", {})[lab] = row; print(f"   {lab:40s} " + ", ".join(f"{k.split(' (')[0]} {v}" for k, v in row.items() if v))
json.dump(out, open(os.path.join(HERE, "alexandria_test_results.json"), "w"), ensure_ascii=False, indent=1)
