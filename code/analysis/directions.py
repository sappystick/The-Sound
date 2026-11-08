#!/usr/bin/env python3
"""The five new directions, run in dependency order: 1 -> 5 -> 4 -> 2 -> 3.

STEP 1  PHRASE CENTRES (list fixed before running). Which key phrases fall on the exact letter-centre verse of a
        Hebrew book, or the syllable-centre verse of a Greek NT book?  Exact chance per phrase (Poisson-binomial,
        1/verses-in-book per occurrence).  ~20 phrases -> Bonferroni threshold 0.0025.  'Living water' (the
        discovery) is reported for reference but not counted.
STEP 5  BLOOD, WATER, HYSSOP. Verses where hyssop, blood and water meet (3-verse window) in the Greek OT and NT;
        rank of Leviticus 14 and Numbers 19 against John 19:28-37; where Hebrews 9:19 sits in Hebrews.
STEP 4  LOGOS AS RATIO. The prologue's four agreed sections (1-5, 6-8, 9-13, 14-18) in spoken syllables: are their
        proportions simpler (small whole-number ratios) than random four-part cuts?  Golden-section points of the
        prologue and of John.
STEP 2  SPELL-LIKENESS. Sound and form features for John, Matthew/Mark/Luke, Greek Psalms, Homeric Hymns (cult
        hymns), Orphic fragments (mystery cult), Corpus Hermeticum (Egyptian), Philo and Josephus (prose).  Which
        class is John nearest?  With the optional fifth argument, PGM I and VI+II (Chronopoulou 2017) join as the spell class.
STEP 3  BREATH. Breath-group length and regularity, and the breathing rate implied at chant pace, for the same classes.
Usage: python3 directions.py <sblgnt> <lxx-swete/data> <morphhb/wlc> <greek dir with perseus/ and f1k/> [pgm.txt]
"""
import collections, glob, json, math, os, random, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC, GR = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(5); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
sc = {}
def syl(k):
    if not k: return 0
    if k not in sc:
        try: sc[k] = max(1, len(E.parse_greek(k, "koine")[0]))
        except Exception: sc[k] = 1
    return sc[k]
def pbinom_tail(probs, k):
    d = [1.0]
    for p in probs: d = [(d[i] if i < len(d) else 0) * (1 - p) + (d[i - 1] * p if i > 0 else 0) for i in range(len(d) + 1)]
    return sum(d[k:])
NT = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]; NT[b] = [((int(l[2:4]), int(l[4:6])), l.split()[3], nrm(l.split()[4]), nrm(l.split()[6])) for l in open(f, encoding="utf-8")]
LXXV = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); LXXV.setdefault((b, r[1], r[2]), []).append(p[1].strip())

# ======================================================================== STEP 1
print("=" * 100 + "\nSTEP 1  PHRASE CENTRES")
def cons(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת")
HEB = {}
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    bk = os.path.basename(f)[:-4]; x = open(f, encoding="utf-8").read(); vs = []
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S):
        ws = [[cons(p) for p in w.split("/") if cons(p)] for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2))]
        vs.append((m.group(1), sum(len(p) for w in ws for p in w), ws))
    HEB[bk] = vs
def centre_idx(lengths):
    T = sum(lengths); acc = 0
    for i, L in enumerate(lengths):
        if acc + L > T / 2: return i
        acc += L
HC = {b: centre_idx([v[1] for v in vs]) for b, vs in HEB.items()}
def has(ws, a, b=None):
    for i, w in enumerate(ws):
        if a in w:
            if b is None: return True
            if i + 1 < len(ws) and any(m in b for m in ws[i + 1]): return True
    return False
HP = {"light (or)": ("אור", None), "spirit / breath (ruach)": ("רוח", None), "breath of life (nishmat chayyim / ruach)": ("נשמת", ("חיים", "רוח")),
      "glory of YHWH": ("כבוד", ("יהוה",)), "tree of life": ("עץ", ("חיים",)), "holy of holies": ("קדש", ("קדשים",)), "I am YHWH": ("אני", ("יהוה",)),
      "word of YHWH": ("דבר", ("יהוה",)), "covenant (berit)": ("ברית", None), "my name (shemi)": ("שמי", None), "sabbath": ("שבת", None), "garden (gan)": ("גן", None),
      "living water (discovery, not counted)": ("מים", ("חיים",))}
r1 = {}
for lab, (a, b) in HP.items():
    occ = [(bk, i) for bk, vs in HEB.items() for i, v in enumerate(vs) if has(v[2], a, b)]
    hits = [HEB[bk][i][0] for bk, i in occ if i == HC[bk]]
    p = pbinom_tail([1 / len(HEB[bk]) for bk, _ in occ], len(hits)) if hits else 1.0
    r1[lab] = dict(n=len(occ), centres=hits, p=p); print(f"   Hebrew {lab:42s} {len(occ):5d} verses; at a book centre: {hits or '-'}  p = {p:.4f}")
GC = {}
for b, toks in NT.items():
    vs = collections.OrderedDict()
    for r, t, w, l in toks: vs.setdefault(r, []).append((w, l))
    keys = list(vs); GC[b] = (keys, vs, centre_idx([sum(syl(w) for w, _ in vs[k]) for k in keys]))
GP = {"light (phos)": "φωσ", "spirit / breath (pneuma)": "πνευμα", "life (zoe)": "ζωη", "water (hydor)": "υδωρ", "glory (doxa)": "δοξα", "name (onoma)": "ονομα", "word (logos)": "λογοσ"}
for lab, lem in GP.items():
    occ = [(b, i) for b, (keys, vs, c) in GC.items() for i, k in enumerate(keys) if any(l == lem for _, l in vs[k])]
    hits = [f"{b} {GC[b][0][i][0]}:{GC[b][0][i][1]}" for b, i in occ if i == GC[b][2]]
    p = pbinom_tail([1 / len(GC[b][0]) for b, _ in occ], len(hits)) if hits else 1.0
    r1["NT " + lab] = dict(n=len(occ), centres=hits, p=p); print(f"   Greek NT {lab:40s} {len(occ):5d} verses; at a book centre: {hits or '-'}  p = {p:.4f}")
counted = {k: v for k, v in r1.items() if "discovery" not in k}
print(f"   phrases passing the corrected threshold (p < {0.05 / len(counted):.4f}): {[k for k, v in counted.items() if v['p'] < 0.05 / len(counted)] or 'none'}")
out["step1"] = r1

# ======================================================================== STEP 5
print("=" * 100 + "\nSTEP 5  BLOOD, WATER AND HYSSOP")
def keyset(text): return {k for k in (nrm(w) for w in text.split())}
def tri(ws):
    return (any(w.startswith("υσσωπ") for w in ws), any(w.startswith("αιμα") or w.startswith("αιματ") for w in ws), any(w.startswith(("υδωρ", "υδατ")) for w in ws))
keys = list(LXXV); hits5 = []
for i, k in enumerate(keys):
    ws = set().union(*[keyset(" ".join(LXXV[kk])) for kk in keys[max(0, i - 1): i + 2] if kk[0] == k[0]])
    if all(tri(ws)): hits5.append(f"{k[0]} {k[1]}:{k[2]}")
ntv = [(b, r, {w for _, _, w, _ in [t for t in toks if t[0] == r]}) for b, toks in NT.items() for r in sorted({t[0] for t in toks})]
nth = []
for i, (b, r, ws) in enumerate(ntv):
    W = set().union(*[x[2] for x in ntv[max(0, i - 3): i + 4] if x[0] == b])
    if all(tri(W)): nth.append(f"{b} {r[0]}:{r[1]}")
def collapse(lst):
    o = []
    for x in lst:
        if not o or x.rsplit(":", 1)[0] != o[-1][0].rsplit(":", 1)[0]: o.append([x])
        else: o[-1].append(x)
    return [g[0] if len(g) == 1 else f"{g[0]}-{g[-1].rsplit(':', 1)[1]}" for g in o]
print("   Greek OT passages where hyssop, blood and water meet:", ", ".join(collapse(hits5)))
print("   NT passages (7-verse window):", ", ".join(collapse(nth)))
syn = {b: [r for r, t, w, l in NT[b] if l.startswith("υσσωπ")] for b in ("Mt", "Mk", "Lk", "Jn")}
print("   hyssop at the crucifixion:", {b: [f"{a}:{c}" for a, c in v] for b, v in syn.items()}, "(Matthew and Mark: a reed, kalamos)")
def pos_in(book, ref):
    T = sum(syl(w) for _, _, w, _ in NT[book]); acc = 0
    for r, t, w, l in NT[book]:
        if r == ref: return acc / T
        acc += syl(w)
print(f"   Hebrews 9:19 (blood, water, scarlet wool, hyssop) sits at {pos_in('Heb', (9, 19)):.3f} of Hebrews; Hebrews' centre verse is 9:7 (the high priest, once a year, not without blood)")
print("   1 John 5:6-8 ('he who came by water and blood ... the Spirit, the water and the blood')")
out["step5"] = dict(lxx=collapse(hits5), nt=collapse(nth), heb_9_19=pos_in("Heb", (9, 19)))

# ======================================================================== STEP 4
print("=" * 100 + "\nSTEP 4  LOGOS AS RATIO")
pro = [t for t in NT["Jn"] if t[0] <= (1, 18)]
vs = collections.OrderedDict()
for r, t, w, l in pro: vs[r[1]] = vs.get(r[1], 0) + syl(w)
L = [vs[v] for v in sorted(vs)]; secs = [(1, 5), (6, 8), (9, 13), (14, 18)]
parts = [sum(vs[v] for v in range(a, b + 1)) for a, b in secs]; T = sum(L)
print(f"   prologue {T} syllables; sections 1-5 / 6-8 / 9-13 / 14-18 = {parts}")
def simplicity(ps):
    errs = []
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            r = max(ps[i], ps[j]) / min(ps[i], ps[j]); errs.append(min(abs(r - p / q) / (p / q) for p in range(1, 6) for q in range(1, 6) if p >= q))
    return float(np.mean(errs))
real = simplicity(parts); null = []
for _ in range(20000):
    cuts = sorted(rng.choice(range(1, 18), 3, replace=False)); bounds = [0] + list(cuts) + [18]
    null.append(simplicity([sum(L[bounds[i]:bounds[i + 1]]) for i in range(4)]))
p4 = float(np.mean(np.array(null) <= real))
print(f"   mean distance of section ratios from the nearest simple ratio (up to 5:4 etc.): {real:.3f}; random four-part cuts as simple or simpler: {p4:.1%}")
def at(frac, toks):
    T = sum(syl(w) for _, _, w, _ in toks); acc = 0
    for r, t, w, l in toks:
        if acc + syl(w) > frac * T: return r
        acc += syl(w)
phi = (5 ** .5 - 1) / 2
for lab, toks in (("prologue", pro), ("John", NT["Jn"])):
    print(f"   {lab}: golden-section points at {at(phi, toks)} (0.618) and {at(1 - phi, toks)} (0.382); centre {at(.5, toks)}")
out["step4"] = dict(parts=parts, simplicity=real, p=p4, golden={lab: [str(at(phi, toks)), str(at(1 - phi, toks))] for lab, toks in (("prologue", pro), ("John", NT["Jn"]))})

# ======================================================================== STEP 2
print("=" * 100 + "\nSTEP 2  SPELL-LIKENESS: which kind of text is John nearest?")
def xmltext(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<(note|bibl|head)[^>]*>.*?</\1>", " ", x, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))
def chunks(raw_tokens, size=400): return [raw_tokens[i:i + size] for i in range(0, len(raw_tokens) - size // 2, size)]
UNITS = collections.defaultdict(list)
UNITS["John"] = chunks([t for _, t, _, _ in NT["Jn"]]); UNITS["John prologue"] = [[t for _, t, _, _ in pro]]
UNITS["Matthew, Mark, Luke"] = [c for b in ("Mt", "Mk", "Lk") for c in chunks([t for _, t, _, _ in NT[b]])]
ps = [w for k, v in LXXV.items() if k[0] == "Psalmi" for w in " ".join(v).split()]; UNITS["Greek Psalms"] = chunks(ps)
for f in glob.glob(os.path.join(GR, "perseus/data/tlg0013/tlg*/*grc*.xml")): UNITS["Homeric Hymns"] += chunks(xmltext(f).split())
for f in glob.glob(os.path.join(GR, "f1k/data/tlg0579/tlg*/*grc*.xml")): UNITS["Orphic fragments"] += chunks(xmltext(f).split())
for f in glob.glob(os.path.join(GR, "f1k/data/tlg1286/tlg*/*grc*.xml")): UNITS["Corpus Hermeticum"] += chunks(xmltext(f).split())
ph = [w for f in sorted(glob.glob(os.path.join(GR, "f1k/data/tlg0018/tlg*/*grc*.xml")))[:6] for w in xmltext(f).split()]; UNITS["Philo"] = chunks(ph)[:120]
if len(sys.argv) > 5:   # optional: interpretative text of PGM I and VI+II (see pgm_extract.py)
    UNITS["Greek Magical Papyri (PGM I, VI+II)"] = chunks(open(sys.argv[5], encoding="utf-8").read().replace("###", " ").split(), 300)
jo = xmltext(glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml"))[0]).split(); UNITS["Josephus"] = chunks(jo)[:120]
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν".split())
INVOC = {"κλυθι", "κλυτε", "ελθε", "ελθετε", "δοσ", "δοτε", "σωσον", "επακουσον", "χαιρε", "χαιρετε", "ιλαθι", "ιλαοσ", "μακαρ"}
def feats(raw):
    ws = [nrm(t) for t in raw]; idx = [i for i, w in enumerate(ws) if w]; ws = [ws[i] for i in idx]; raw = [raw[i] for i in idx]
    letters = "".join(ws); vow = sum(c in "αεηιουω" for c in letters) / max(1, len(letters))
    runs = sum(1 for w in ws if re.search(r"[αεηιουω]{3,}", w)) / len(ws)
    rep = sum(1 for i, w in enumerate(ws) if w not in STOP and len(w) > 3 and w in ws[max(0, i - 30):i]) / len(ws)
    iam = 1000 * sum(1 for a, b in zip(ws, ws[1:]) if a == "εγω" and b == "ειμι") / len(ws)
    inv = 1000 * sum(w in INVOC for w in ws) / len(ws)
    S = [syl(w) for w in ws]; spw = sum(S) / len(ws)
    groups, cur = [], 0
    for t, s in zip(raw, S):
        cur += s
        if re.search(r"[,.·;:;]$", t): groups.append(cur); cur = 0
    groups = groups or [sum(S)]; gm = float(np.mean(groups)); gcv = float(np.std(groups) / gm) if gm else 0
    clauses, c2 = [], []
    for t, w in zip(raw, ws):
        c2.append(w)
        if re.search(r"[,.·;:;]$", t): clauses.append(c2); c2 = []
    stair = sum(1 for a, b in zip(clauses, clauses[1:]) if {x[:5] for x in a[-3:] if x not in STOP and len(x) > 3} & {x[:5] for x in b[:4] if x not in STOP and len(x) > 3}) / max(1, len(clauses) - 1)
    return [vow, runs, rep, iam, inv, spw, gm, gcv, stair]
FN = ["vowel share", "3-vowel runs", "repetition", "'I am' /1000", "invocations /1000", "syllables/word", "breath group", "breath irregularity", "staircase"]
F = {k: np.array([feats(u) for u in v if len(u) > 100]) for k, v in UNITS.items() if v}
allx = np.vstack([v for v in F.values()]); mu, sd = allx.mean(0), allx.std(0) + 1e-9
cent = {k: ((v - mu) / sd).mean(0) for k, v in F.items()}
print("   class means:")
print("      " + " | ".join(f"{n[:12]:>12s}" for n in FN))
for k, v in F.items(): print(f"   {k:22s} n={len(v):3d} " + " ".join(f"{x:12.3f}" for x in v.mean(0)))
REF = [k for k in cent if k not in ("John", "John prologue")]
res2 = {}
for k in ("John", "John prologue"):
    d = sorted((float(np.linalg.norm(cent[k] - cent[r])), r) for r in REF); res2[k] = d
    print(f"   {k} is nearest to: " + ", ".join(f"{r} ({x:.2f})" for x, r in d[:4]))
out["step2"] = dict(features=FN, means={k: v.mean(0).round(4).tolist() for k, v in F.items()}, nearest=res2)

# ======================================================================== STEP 3
print("=" * 100 + "\nSTEP 3  BREATH")
r3 = {}
for k, v in F.items():
    gm = float(v[:, 6].mean()); cv = float(v[:, 7].mean()); bpm = 60 / (gm / 2 + 1.5)
    r3[k] = dict(group=round(gm, 1), irregularity=round(cv, 2), breaths_per_min_chant=round(bpm, 1))
    print(f"   {k:22s} breath group {gm:5.1f} syllables, irregularity {cv:.2f}, at chant pace (2 syll/s + 1.5 s breath) = {bpm:4.1f} breaths/min")
out["step3"] = r3
json.dump(out, open(os.path.join(HERE, "directions_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
