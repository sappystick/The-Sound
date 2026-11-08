#!/usr/bin/env python3
"""The ear's measures: John as heard, measured with criteria the ancient critics themselves used.

Dionysius of Halicarnassus (On Composition, 1st c. BC) judged prose by hiatus, rhythm, cadence and the
smoothness or roughness of its sounds.  Each becomes a number, computed from the reconstructed Koine sound:
  HIATUS        vowel meeting vowel across a word boundary, per 100 junctures (polished prose avoids it)
  STRESS TIMING how evenly stressed (accented) syllables are spaced: CV of inter-stress intervals; lower = more
                even, chant-like
  WEIGHT RHYTHM nPVI of syllable weights (heavy = long vowel or closed syllable = 2, light = 1), the standard
                speech-rhythm index (Grabe & Low 2002); and the strongest periodicity of the weight sequence
  CADENCE       does the weight pattern of the last 5 syllables before a full stop differ from the same span
                inside the sentence?  (designed sentence endings, the ancient 'clausula')
  NOISE         share of obstruent sounds (stops, fricatives: acoustically, noise bursts and hiss) against
                sonorants and vowels (voice); fricative share separately
  ECHO          alliteration: neighbouring words starting with the same sound, against shuffled word order
Control: Homeric Hymns (metrical verse) must show the strongest weight periodicity.
Also: the prologue's centre in the Syriac, Coptic and Latin versions (letters), against the Greek.
Usage: python3 acoustic.py <sblgnt> <lxx-swete/data> <greek dir> <pgm.txt or -> <versions dir>
"""
import collections, csv, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, LXX, GR, PGM, VER = sys.argv[1:6]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(2); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
OBS = {"p", "b", "t", "d", "k", "g", "pʰ", "tʰ", "kʰ", "f", "v", "θ", "ð", "s", "z", "x", "ɣ", "ç", "ʝ", "h", "ps", "ks", "β", "φ", "dz", "ts"}
FRIC = {"f", "v", "θ", "ð", "s", "z", "x", "ɣ", "ç", "ʝ", "h", "β", "φ"}
cache = {}
def word(raw):
    k = unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw.lower()))
    if not k: return None
    if k not in cache:
        try: cache[k] = E.parse_greek(k, "koine")[0]
        except Exception: cache[k] = None
    return cache[k]
def measures(raw_tokens):
    W = []; stops = []
    for t in raw_tokens:
        s = word(t)
        if s: W.append(s); stops.append(bool(re.search(r"[.;·;]$", t)))
    if len(W) < 40: return None
    vowel_end = [w[-1]["ph"][-1] in w[-1]["nuc"] for w in W]; vowel_start = [w[0]["ph"][0] in w[0]["nuc"] for w in W]
    hiatus = 100 * np.mean([a and b for a, b in zip(vowel_end, vowel_start[1:])])
    sy = [s for w in W for s in w]; weight = np.array([2 if (s["long"] or s["ph"][-1] not in s["nuc"]) else 1 for s in sy], float)
    stress = [i for i, s in enumerate(sy) if s["accent"]]; iv = np.diff(stress); stress_cv = float(np.std(iv) / np.mean(iv)) if len(iv) > 3 else np.nan
    npvi = float(100 * np.mean([abs(a - b) / ((a + b) / 2) for a, b in zip(weight, weight[1:])]))
    x = weight - weight.mean(); d = (x * x).sum() or 1; period = max(float((x[:-k] * x[k:]).sum() / d) for k in (2, 3, 4))
    ph = [p for s in sy for p in s["ph"]]; noise = np.mean([p in OBS for p in ph]); fric = np.mean([p in FRIC for p in ph])
    onset = [w[0]["ph"][0] for w in W]; echo = np.mean([a == b for a, b in zip(onset, onset[1:])])
    sh = [np.mean([a == b for a, b in zip(o, o[1:])]) for o in (list(rng.permutation(onset)) for _ in range(20))]
    # cadence: weight pattern (5 syllables) before a full stop vs elsewhere
    ends, mids, pos = [], [], 0
    for w, st in zip(W, stops):
        pos += len(w)
        if pos >= 5: (ends if st else mids).append(tuple(int(v) for v in weight[pos - 5:pos]))
    return dict(hiatus=hiatus, stress_cv=stress_cv, npvi=npvi, periodicity=period, noise=noise, fricative=fric, echo=echo / np.mean(sh), ends=ends, mids=mids)
def chunks(t, n=400): return [t[i:i + n] for i in range(0, len(t) - n // 2, n)]
def xml(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<(note|bibl|head)[^>]*>.*?</\1>", " ", x, flags=re.S)
    return re.sub(r"<[^>]+>", " ", x).split()
NT = {os.path.basename(f).split("-")[1]: [(int(l[2:4]), int(l[4:6]), l.split()[3]) for l in open(f, encoding="utf-8")] for f in glob.glob(os.path.join(SBL, "*-morphgnt.txt"))}
C = {"John": chunks([t for *_, t in NT["Jn"]]), "John prologue": [[t for c, v, t in NT["Jn"] if c == 1 and v <= 18]],
     "Matthew, Mark, Luke": [c for b in ("Mt", "Mk", "Lk") for c in chunks([t for *_, t in NT[b]])], "Paul": [c for b in ("Ro", "1Co", "2Co", "Ga") for c in chunks([t for *_, t in NT[b]])],
     "Hebrews": chunks([t for *_, t in NT["Heb"]])}
ps = [l.split(maxsplit=1)[1].strip() for l in open(glob.glob(os.path.join(LXX, "*Psalmi.txt"))[0], encoding="utf-8") if len(l.split(maxsplit=1)) == 2]; C["Greek Psalms"] = chunks(ps)[:80]
C["Homeric Hymns (verse)"] = [c for f in glob.glob(os.path.join(GR, "perseus/data/tlg0013/tlg*/*grc*.xml")) for c in chunks(xml(f))]
C["Corpus Hermeticum"] = [c for f in glob.glob(os.path.join(GR, "f1k/data/tlg1286/tlg*/*grc*.xml")) for c in chunks(xml(f))][:80]
C["Josephus"] = chunks(xml(glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml"))[0]))[:80]
C["Philo"] = [c for f in sorted(glob.glob(os.path.join(GR, "f1k/data/tlg0018/tlg*/*grc*.xml")))[:4] for c in chunks(xml(f))][:80]
if PGM != "-" and os.path.exists(PGM): C["Magical Papyri"] = chunks(open(PGM, encoding="utf-8").read().replace("###", " ").split(), 300)
R = {}
print(f"{'class':24s} {'hiatus':>7s} {'stressCV':>8s} {'nPVI':>6s} {'period':>7s} {'noise':>6s} {'fric':>6s} {'echo':>6s}")
for k, v in C.items():
    ms = [m for m in (measures(u) for u in v) if m]
    if not ms: continue
    agg = {f: float(np.nanmean([m[f] for m in ms])) for f in ("hiatus", "stress_cv", "npvi", "periodicity", "noise", "fricative", "echo")}
    ends = [e for m in ms for e in m["ends"]]; mids = [e for m in ms for e in m["mids"]]
    if len(ends) > 20:
        ce, cm = collections.Counter(ends), collections.Counter(mids); keys = set(ce) | set(cm)
        pe = np.array([ce[x] + .5 for x in keys]) / (len(ends) + .5 * len(keys)); pm = np.array([cm[x] + .5 for x in keys]) / (len(mids) + .5 * len(keys))
        kl = float((pe * np.log(pe / pm)).sum()); allc = ends + mids; null = []
        for _ in range(200):
            idx = rng.permutation(len(allc)); e2 = collections.Counter(allc[i] for i in idx[:len(ends)]); m2 = collections.Counter(allc[i] for i in idx[len(ends):])
            p1 = np.array([e2[x] + .5 for x in keys]) / (len(ends) + .5 * len(keys)); p2 = np.array([m2[x] + .5 for x in keys]) / (len(mids) + .5 * len(keys)); null.append((p1 * np.log(p1 / p2)).sum())
        agg["cadence_kl"] = kl; agg["cadence_p"] = float(np.mean(np.array(null) >= kl)); agg["top_ending"] = "".join("–" if x == 2 else "u" for x in ce.most_common(1)[0][0])
    R[k] = agg
    print(f"{k:24s} {agg['hiatus']:7.1f} {agg['stress_cv']:8.3f} {agg['npvi']:6.1f} {agg['periodicity']:7.3f} {agg['noise']:6.3f} {agg['fricative']:6.3f} {agg['echo']:6.2f}" + (f"   cadence p={agg['cadence_p']:.3f} commonest ending {agg['top_ending']}" if "cadence_p" in agg else ""))
out["classes"] = R

print("\nINSIDE JOHN: noise share and stress evenness of key passages against John overall")
def verses(sel): return [t for c, v, t in NT["Jn"] if sel(c, v)]
for lab, sel in (("prologue 1:1-18", lambda c, v: c == 1 and v <= 18), ("'I am' sayings (6:35,8:12,10:7-14,11:25,14:6,15:1-5)", lambda c, v: (c, v) in {(6, 35), (6, 48), (6, 51), (8, 12), (10, 7), (10, 9), (10, 11), (10, 14), (11, 25), (14, 6), (15, 1), (15, 5)}),
                 ("farewell 13:31-17:26", lambda c, v: (13, 31) <= (c, v) <= (17, 26)), ("passion 18-19", lambda c, v: c in (18, 19)), ("signs narrative 2-11", lambda c, v: 2 <= c <= 11)):
    m = measures(verses(sel)); print(f"   {lab:52s} noise {m['noise']:.3f}  fricative {m['fricative']:.3f}  stressCV {m['stress_cv']:.3f}  hiatus {m['hiatus']:.1f}")
    out.setdefault("inside_john", {})[lab] = {k: float(m[k]) for k in ("noise", "fricative", "stress_cv", "hiatus")}
# null for the I-am noise: random 12-verse sets
jv = sorted({(c, v) for c, v, _ in NT["Jn"]}); iam = {(6, 35), (6, 48), (6, 51), (8, 12), (10, 7), (10, 9), (10, 11), (10, 14), (11, 25), (14, 6), (15, 1), (15, 5)}
real = measures(verses(lambda c, v: (c, v) in iam))["noise"]; null = []
for _ in range(300):
    s = set(map(tuple, np.array(jv)[rng.choice(len(jv), 12, replace=False)])); m = measures(verses(lambda c, v: (c, v) in s))
    if m: null.append(m["noise"])
print(f"   'I am' sayings noise {real:.3f}: share of random 12-verse sets as quiet or quieter: {np.mean(np.array(null) <= real):.3f}")

print("\nTHE PROLOGUE'S CENTRE IN TRANSLATION (by letters)")
def centre(rows):
    L = [len(re.sub(r"[\s\W\d_]", "", t)) for _, t in rows]; T = sum(L); acc = 0
    for (v, t), l in zip(rows, L):
        if acc + l > T / 2: return v, round((T / 2 - acc) / l, 2)
        acc += l
g = [(v, t) for c, v, t in NT["Jn"] if c == 1 and v <= 18]; gv = collections.OrderedDict()
for v, t in g: gv[v] = gv.get(v, "") + t
print(f"   Greek (SBLGNT): centre in verse {centre(list(gv.items()))[0]} (fraction into the verse {centre(list(gv.items()))[1]})")
for name in ("Peshitta", "CopSahBible2", "VulgClementine"):
    rows = [(int(r["Verse"]), r["Text"]) for r in csv.DictReader(open(os.path.join(VER, f"{name}.csv"), encoding="utf-8")) if r["Book"] == "John" and r["Chapter"] == "1" and int(r["Verse"]) <= 18]
    v, f = centre(rows); print(f"   {name:16s} centre in verse {v} (fraction into the verse {f})"); out.setdefault("versions", {})[name] = [v, f]
json.dump(out, open(os.path.join(HERE, "acoustic_results.json"), "w"), ensure_ascii=False, indent=1, default=str)

print("\nIS JOHN QUIETER? noise share per 400-word chunk, John against each class (Mann-Whitney)")
from scipy.stats import mannwhitneyu
jn = [m["noise"] for m in (measures(u) for u in C["John"]) if m]
for k in ("Matthew, Mark, Luke", "Paul", "Greek Psalms", "Josephus", "Philo", "Homeric Hymns (verse)"):
    o = [m["noise"] for m in (measures(u) for u in C[k]) if m]; p = mannwhitneyu(jn, o, alternative="less").pvalue
    print(f"   John {np.mean(jn):.3f} vs {k:22s} {np.mean(o):.3f}  p = {p:.2g}"); out.setdefault("quieter", {})[k] = float(p)
# which sounds make the difference?
def phcount(chs):
    c = collections.Counter()
    for u in chs:
        for t in u:
            s = word(t)
            if s: c.update(p for sy in s for p in sy["ph"])
    return c
cj, cs = phcount(C["John"]), phcount(C["Matthew, Mark, Luke"]); nj, ns = sum(cj.values()), sum(cs.values())
diff = sorted(((cj[p] / nj - cs[p] / ns) * 1000, p) for p in set(cj) | set(cs))
print("   sounds John uses less (per 1,000 sounds):", ", ".join(f"{p} {d:+.1f}" for d, p in diff[:6]))
print("   sounds John uses more:", ", ".join(f"{p} {d:+.1f}" for d, p in diff[-6:]))
json.dump(out, open(os.path.join(HERE, "acoustic_results.json"), "w"), ensure_ascii=False, indent=1, default=str)

print("\nHARDENING: is the quietness in John's vocabulary or in common words? (noise with the 150 commonest NT words removed)")
topw = {w for w, _ in collections.Counter(re.sub(r"[^\w]", "", t.lower()) for b in NT for *_, t in NT[b]).most_common(150)}
def strip(chs): return [[t for t in u if re.sub(r"[^\w]", "", t.lower()) not in topw] for u in chs]
jn2 = [m["noise"] for m in (measures(u) for u in strip(C["John"])) if m]
for k in ("Matthew, Mark, Luke", "Josephus", "Greek Psalms"):
    o = [m["noise"] for m in (measures(u) for u in strip(C[k])) if m]
    print(f"   content words only: John {np.mean(jn2):.3f} vs {k:20s} {np.mean(o):.3f}  p = {mannwhitneyu(jn2, o, alternative='less').pvalue:.2g}")
