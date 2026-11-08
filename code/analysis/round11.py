#!/usr/bin/env python3
"""Round 11: turning points, other texts' sound maps, and the open leads.

1. TURNING POINTS (lists fixed in advance, none of the three verses that suggested the idea included):
   (a) John's own 'Amen, amen' verses; (b) 'the hour' announcements (hora with come/has come);
   (c) the blind seams from order_tests.  Are they noisier (or quieter) than random verse sets?
2. OTHER TEXTS: speech against narrative, and the noise curve against 'Father' and first/second person, in
   Matthew, Mark, Luke; in the Greek Psalms, noise against first/second-person pronoun density.
   HARDENING: everything again with personal pronouns removed (me, my, you... contain m and s, which would
   make 'intimate' text quieter or noisier mechanically).
3a. REVERSED LINKS: among NT chapter pairs linked by 4+ rare phrases, are reversed-order links commoner than
   chance (2.5% expected each way)?
3b. DEAD SEA SCROLLS: does John's emphasis profile (against the Synoptics) match the Community Rule's (1QS,
   against the Hebrew Bible) over a fixed list of concepts?  'Sons of light' and 'spirit of truth'.
3c. ECHOES OF JOHN: phrases found in John but in none of Matthew, Mark, Luke (and the reverse), traced in
   Ignatius, Polycarp, Hermas, Clement of Alexandria; Philo and Josephus as negative controls.
Usage: python3 round11.py <sblgnt> <lxx-swete/data> <morphhb/wlc> <greek dir> <dss_scrolls.json> <order_tests_results.json>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC, GR, DSS, OTR = sys.argv[1:7]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(11); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
OBS = {"p", "b", "t", "d", "k", "g", "pʰ", "tʰ", "kʰ", "f", "v", "θ", "ð", "s", "z", "x", "ɣ", "ç", "ʝ", "h", "ps", "ks", "β", "φ", "dz", "ts"}
PRON = set("εγω μου μοι με εμου εμοι εμε συ σου σοι σε ημεισ ημων ημιν ημασ υμεισ υμων υμιν υμασ".split())
cache = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def phon(raw):
    k = unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw.lower()))
    if k not in cache:
        try: cache[k] = [p for s in E.parse_greek(k, "koine")[0] for p in s["ph"]]
        except Exception: cache[k] = []
    return cache[k]
def load_nt(code):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); r = (int(p[0][2:4]), int(p[0][4:6])); e = V.setdefault(r, dict(raw=[], lem=[], person=set()))
        e["raw"].append(p[3]); e["lem"].append(nrm(p[6]))
        if p[1].startswith("V") and p[2][0] in "12": e["person"].add(p[2][0])
    return V
def noise(raws, drop_pron=False):
    o = n = 0
    for t in raws:
        if drop_pron and nrm(t) in PRON: continue
        ph = phon(t); o += sum(x in OBS for x in ph); n += len(ph)
    return o, n
NT = {c: load_nt(c) for c in ("Jn", "Mt", "Mk", "Lk")}

# ---------------------------------------------------------------- 1
print("1. TURNING POINTS IN JOHN (fixed lists; percentile of the 5-verse window; 0.5 = average)")
J = NT["Jn"]; keys = list(J)
on = np.array([noise(J[k]["raw"])[0] for k in keys], float); nn = np.array([noise(J[k]["raw"])[1] for k in keys], float)
w5 = np.convolve(on, np.ones(5), "same") / np.maximum(np.convolve(nn, np.ones(5), "same"), 1); pct = np.array([np.mean(w5 <= x) for x in w5])
amen = [keys[i] for i in range(len(keys)) if sum(1 for a, b in zip(J[keys[i]]["lem"], J[keys[i]]["lem"][1:]) if a == b == "αμην")]
hour = [k for k in keys if "ωρα" in J[k]["lem"] and any(l in ("ερχομαι",) for l in J[k]["lem"])]
seams = [tuple(map(int, s.split(":"))) for s in json.load(open(OTR))["seams"]["john_top_seams"]]
EXCL = {(1, 12), (19, 30), (11, 25)}
for lab, lst in (("'Amen, amen' verses", amen), ("'the hour' announcements", hour), ("blind seams (order_tests)", seams)):
    lst = [k for k in lst if k in J and k not in EXCL]; idx = [keys.index(k) for k in lst]; real = pct[idx].mean()
    null = np.array([pct[rng.choice(len(keys), len(idx), replace=False)].mean() for _ in range(5000)])
    print(f"   {lab:28s} n={len(idx):2d}  mean percentile {real:.2f}  noisier p={np.mean(null >= real):.3f}  quieter p={np.mean(null <= real):.3f}")
    out.setdefault("turning", {})[lab] = dict(n=len(idx), mean_pct=float(real), p_noisy=float(np.mean(null >= real)))
    spk = [i for i, k in enumerate(keys) if J[k]["person"]]   # control: compare with random SPEECH verses
    null2 = np.array([pct[rng.choice(spk, len(idx), replace=False)].mean() for _ in range(5000)])
    print(f"   {'':28s}       against random speech verses: quieter p={np.mean(null2 <= real):.3f}")

# ---------------------------------------------------------------- 2
print("\n2. DO OTHER TEXTS GO QUIET IN INTIMATE SPEECH?  (difference speech - narrative; negative = speech quieter)")
for code, V in NT.items():
    for drop in (False, True):
        sp = [k for k in V if V[k]["person"]]; na = [k for k in V if not V[k]["person"]]
        on_ = {k: noise(V[k]["raw"], drop) for k in V}
        def share(ks): return sum(on_[k][0] for k in ks) / sum(on_[k][1] for k in ks)
        s1, s2 = share(sp), share(na); allk = list(V); null = []
        for _ in range(500):
            idx = rng.permutation(len(allk)); null.append(share([allk[i] for i in idx[:len(sp)]]) - share([allk[i] for i in idx[len(sp):]]))
        p = np.mean(np.abs(null) >= abs(s1 - s2))
        print(f"   {code} {'(pronouns removed)' if drop else '                  '} speech {s1:.3f} narrative {s2:.3f}  diff {s1 - s2:+.4f}  p={p:.3f}")
        out.setdefault("speech", {})[f"{code}{'_nopron' if drop else ''}"] = dict(diff=float(s1 - s2), p=float(p))
print("   'Father' density against the noise curve (15-verse windows; negative r = Father where quiet), with circular-shift p")
for code, V in NT.items():
    for drop in (False, True):
        ks = list(V); o = np.array([noise(V[k]["raw"], drop)[0] for k in ks], float); n = np.array([noise(V[k]["raw"], drop)[1] for k in ks], float)
        sm = np.convolve(o, np.ones(15), "same") / np.maximum(np.convolve(n, np.ones(15), "same"), 1)
        d = np.convolve(np.array([V[k]["lem"].count("πατηρ") for k in ks], float), np.ones(15), "same"); r = np.corrcoef(d, sm)[0, 1]
        null = [np.corrcoef(np.roll(d, s), sm)[0, 1] for s in rng.integers(30, len(d) - 30, 1000)]
        print(f"   {code} {'(pronouns removed)' if drop else '                  '} r = {r:+.2f}  p = {np.mean(np.abs(null) >= abs(r)):.3f}")
        out.setdefault("father", {})[f"{code}{'_nopron' if drop else ''}"] = float(r)
psv = collections.OrderedDict()
for l in open(glob.glob(os.path.join(LXX, "*Psalmi.txt"))[0], encoding="utf-8"):
    p = l.split(maxsplit=1)
    if len(p) == 2: psv.setdefault(tuple(p[0].split(".")[1:3]), []).extend(p[1].split())
dens = np.array([sum(nrm(t) in PRON for t in v) / len(v) for v in psv.values()])
for drop in (False, True):
    nz = np.array([(lambda o, n: o / max(n, 1))(*noise(v, drop)) for v in psv.values()])
    r = np.corrcoef(dens, nz)[0, 1]; null = [np.corrcoef(rng.permutation(dens), nz)[0, 1] for _ in range(1000)]
    print(f"   Greek Psalms {'(pronouns removed)' if drop else '                  '}: first/second-person density against verse noise r = {r:+.3f}  p = {np.mean(np.abs(null) >= abs(r)):.3f}")

# ---------------------------------------------------------------- 3a
print("\n3a. REVERSED LINKS across the New Testament")
V = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); V.setdefault((b, r[1], r[2]), []).append(nrm(p[1]))
NTB = set()
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]; NTB.add(b)
    for l in open(f, encoding="utf-8"): V.setdefault((b, str(int(l[2:4])), str(int(l[4:6]))), []).append(nrm(l.split()[4]))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ εαν αν οσ ουτοσ τουτο παντα πασ".split())
occ = collections.defaultdict(list); cv = collections.defaultdict(list)
for k, ws in V.items():
    ws = [w for w in ws if w]; cv[(k[0], k[1])].append(k[2]); c = [(i, w[:5]) for i, w in enumerate(ws) if w not in STOP and len(w) > 3]
    for (i, a), (j, b) in zip(c, c[1:]):
        if j - i <= 3: occ[(a, b)].append((k, i / max(1, len(ws) - 1)))
vi = {(b, c, v): i for (b, c), vs in cv.items() for i, v in enumerate(vs)}
links = collections.defaultdict(list)
for ph, v in occ.items():
    if 2 <= len(v) <= 12:
        for x in range(len(v)):
            for y in range(x + 1, len(v)):
                (ka, qa), (kb, qb) = v[x], v[y]; ca, cb = (ka[0], ka[1]), (kb[0], kb[1])
                if ca[0] != cb[0] and (ca[0] in NTB or cb[0] in NTB):
                    a, b = ((vi[ka] + qa) / len(cv[ca]), (vi[kb] + qb) / len(cv[cb])); links[(ca, cb) if ca < cb else (cb, ca)].append((a, b) if ca < cb else (b, a))
pos = neg = tot = 0; revs = []
for (ca, cb), pr in links.items():
    if len(pr) < 4: continue
    a = np.array([x for x, _ in pr]); b = np.array([y for _, y in pr])
    if a.std() == 0 or b.std() == 0: continue
    r = np.corrcoef(a, b)[0, 1]; na, nb = len(cv[ca]), len(cv[cb]); hits = 0
    for _ in range(200):
        pa, pb = rng.permutation(na), rng.permutation(nb)
        aa = pa[np.minimum((a * na).astype(int), na - 1)]; bb = pb[np.minimum((b * nb).astype(int), nb - 1)]
        if aa.std() > 0 and bb.std() > 0 and np.corrcoef(aa, bb)[0, 1] * np.sign(r) >= abs(r): hits += 1
    p = (hits + 1) / 201; tot += 1
    if p < .025: (pos := pos + 1) if r > 0 else (neg := neg + 1); revs.append((p, r, len(pr), ca, cb)) if r < 0 else None
print(f"   chapter pairs tested {tot}; significant forward {pos} ({pos / tot:.1%}), reversed {neg} ({neg / tot:.1%}); expected by chance ~2.5% each")
for p, r, n, ca, cb in sorted(revs)[:10]: print(f"      reversed: {ca[0]} {ca[1]} ~ {cb[0]} {cb[1]}  links {n} rho {r:+.2f} p {p:.3f}")
out["reversed"] = dict(tested=tot, forward=pos, reversed=neg, examples=[(f"{a[0]} {a[1]}", f"{b[0]} {b[1]}", n, round(float(r), 2)) for p, r, n, a, b in sorted(revs)[:20]])

# ---------------------------------------------------------------- 3b
print("\n3b. THE COMMUNITY RULE (1QS) AND JOHN: emphasis profiles over a fixed concept list")
dss = json.load(open(DSS)); qs = [w for w in dss["1QS"] if w.strip()]
hb = []
for f in glob.glob(os.path.join(WLC, "*.xml")):
    hb += [p for w in re.findall(r"<w [^>]*>([^<]+)</w>", open(f, encoding="utf-8").read()) for p in w.split("/")]
def hc(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת").replace("ך", "כ").replace("ם", "מ").replace("ן", "נ").replace("ף", "פ").replace("ץ", "צ")
qs = [hc(w) for w in qs]; hb = [hc(w) for w in hb]
CONC = {"light": (("אור",), ("φωσ", "φωτ")), "darkness": (("חושכ", "חשכ"), ("σκοτ",)), "truth": (("אמת",), ("αληθ",)), "spirit": (("רוח",), ("πνευμ",)),
        "love": (("אהב", "אהבת"), ("αγαπ",)), "hate": (("שנא",), ("μισ",)), "know/knowledge": (("דעת", "ידע"), ("γινωσκ", "εγνω", "γνωσ", "οιδ")),
        "walk": (("הלכ", "התהלכ"), ("περιπατ",)), "life": (("חיימ", "חיי"), ("ζωη", "ζωησ")), "judgement": (("משפט",), ("κρισ", "κριν")),
        "spirit of holiness": (("קודש", "קדש"), ("αγι",)), "commandment/law": (("תורה", "מצוה", "חוק"), ("εντολ", "νομ"))}
jn = [nrm(t) for k in NT["Jn"] for t in NT["Jn"][k]["raw"]]; sy = [nrm(t) for c in ("Mt", "Mk", "Lk") for k in NT[c] for t in NT[c][k]["raw"]]
def rate(ws, pre, exact=False): return (sum(1 for w in ws if (w in pre if exact else w.startswith(pre))) + .5) / len(ws)
rows = []
for c, (hp, gp) in CONC.items():
    a = math.log(rate(qs, hp, True) / rate(hb, hp, True)); b = math.log(rate(jn, gp) / rate(sy, gp)); rows.append((c, a, b))
    print(f"   {c:20s} 1QS vs Hebrew Bible {a:+.2f}   John vs Synoptics {b:+.2f}")
A = np.array([r[1] for r in rows]); B = np.array([r[2] for r in rows]); rho = np.corrcoef(np.argsort(np.argsort(A)), np.argsort(np.argsort(B)))[0, 1]
null = [np.corrcoef(np.argsort(np.argsort(A)), rng.permutation(np.argsort(np.argsort(B))))[0, 1] for _ in range(5000)]
print(f"   emphasis profiles: Spearman rho {rho:+.2f}; p = {np.mean(np.array(null) >= rho):.3f}")
def bigram(ws, a, b): return sum(1 for x, y in zip(ws, ws[1:]) if x.startswith(a) and y.startswith(b))
allq = [hc(w) for s in dss.values() for w in s if w.strip()]
print(f"   'sons of light' (בני אור): 1QS {bigram(qs, 'בני', 'אור')}, all scrolls {bigram(allq, 'בני', 'אור')}, Hebrew Bible {bigram(hb, 'בני', 'אור')};  John 12:36 'sons of light'; Luke 16:8; 1 Thessalonians 5:5")
print(f"   'spirit of truth' (רוח אמת / רוחות אמת): 1QS {bigram(qs, 'רוח', 'אמת')}, all scrolls {bigram(allq, 'רוח', 'אמת')}, Hebrew Bible {bigram(hb, 'רוח', 'אמת')};  John 14:17, 15:26, 16:13; 1 John 4:6")
out["dss"] = dict(profiles=rows, rho=float(rho))

# ---------------------------------------------------------------- 3c
print("\n3c. ECHOES OF JOHN in the early church writers (phrases in John and none of Matthew, Mark, Luke, and the reverse)")
def bigrams(ws): c = [w[:6] for w in ws if w not in STOP and len(w) > 3]; return collections.Counter(zip(c, c[1:]))
bj, bs = bigrams(jn), bigrams(sy)
JO = {g for g, n in bj.items() if n >= 2 and g not in bs}; SO = {g for g, n in bs.items() if n >= 2 and g not in bj}
def xml(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    return [w for w in (nrm(t) for t in re.sub(r"<[^>]+>", " ", x).split()) if w]
W = {"Ignatius (7 letters, c. 110)": "f1k/data/tlg1443/tlg001", "Polycarp, Philippians (c. 120)": "f1k/data/tlg1622/tlg001", "Shepherd of Hermas (c. 140)": "f1k/data/tlg1419/tlg001",
     "Clement of Alexandria (c. 200)": "f1k/data/tlg0555", "Philo (control, before John)": "f1k/data/tlg0018", "Josephus (control)": "perseus/data/tlg0526/tlg001"}
res = {}
for lab, d in W.items():
    ws = [w for f in glob.glob(os.path.join(GR, d, "**", "*grc*.xml"), recursive=True) for w in xml(f)]
    if not ws: continue
    b = bigrams(ws); j = sum(b[g] for g in JO); s = sum(b[g] for g in SO); lean = math.log(((j + .5) / len(JO)) / ((s + .5) / len(SO)))
    hits = sorted((g for g in JO if b[g]), key=lambda g: -b[g])[:6]
    res[lab] = dict(words=len(ws), john=j, synoptic=s, lean=round(lean, 2))
    print(f"   {lab:32s} words {len(ws):7d}  John-only phrases {j:4d}  Synoptic-only {s:4d}  lean to John {lean:+.2f}   e.g. {' | '.join(' '.join(g) for g in hits)}")
out["echoes"] = res
json.dump(out, open(os.path.join(HERE, "round11_results.json"), "w"), ensure_ascii=False, indent=1, default=str)

print("\n3c-2. TARGETED: John's signature phrases (fixed list) in each writer; Philo and Josephus as controls")
SIG = {"living water": r"υδωρ ζων|υδατοσ ζωντοσ|υδωρ το ζων", "bread of God / of life": r"αρτοσ του θεου|αρτον θεου|αρτοσ τησ ζωησ|αρτον τησ ζωησ|αρτοσ θεου",
       "spirit of truth": r"πνευμα τησ αληθειασ", "light of the world": r"φωσ του κοσμου", "lamb of God": r"αμνοσ του θεου", "only-begotten son": r"μονογενη υιον|μονογενησ υιοσ|υιοσ ο μονογενησ",
       "whence it comes and where it goes": r"ποθεν ερχεται και που υπαγει|ποθεν ερχεται και που", "the door (of the Father)": r"θυρα του πατροσ|αυτοσ ων θυρα|η θυρα",
       "the Word from silence / Logos made flesh": r"λογοσ απο σιγησ|λογοσ σαρξ", "true vine": r"αμπελοσ η αληθινη"}
TX = {lab: " ".join(w for f in glob.glob(os.path.join(GR, d, "**", "*grc*.xml"), recursive=True) for w in xml(f)) for lab, d in W.items()}
TX["Synoptics (reference)"] = " ".join(sy); TX["John (reference)"] = " ".join(jn)
for lab, txt in TX.items():
    found = {k: len(re.findall(v, txt)) for k, v in SIG.items()}; hit = {k: n for k, n in found.items() if n}
    print(f"   {lab:32s} {sum(hit.values()):3d}  {hit}")
    out.setdefault("signature", {})[lab] = hit
json.dump(out, open(os.path.join(HERE, "round11_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
