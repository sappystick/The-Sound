#!/usr/bin/env python3
"""Round 40: the open investigations, and the project's methods applied across the Old and New Testaments.

1  JOHN 13:1 OR 13:31? A speech signal that shares nothing with the Greek: the share of each verse inside the quotation
   marks of the Berean Standard Bible (translators' quotes). Segment John blind; where does the farewell begin?
2  VOICE-DRAWN OUTLINES ELSEWHERE: Job and Deuteronomy (agreed outlines), Revelation, Hebrews, Acts (exploratory).
   Two independent signals per book: translators' quotes (BSB), and 1st/2nd-person morphology (Hebrew WLC or Greek SBLGNT).
3  KETIV AND QERE: the written-versus-read pairs of the Hebrew Bible. How many are sound-alikes?
4  MASORETIC MIDPOINTS: the Talmud (Kiddushin 30a) names the middle letter, words and verse of the Torah and of Psalms.
   Where are they in today's Leningrad text?
5  LIFE AT THE CENTRE, IN GREEK: does the Hebrew result (5 of 39 book centres) recur for zoe in the NT and the Septuagint?
6  SEMITIC SOUNDS LEFT UNTRANSLATED in the NT: which books, and where.
7  STATED NUMBERS: 318 (Gen 14:14), 666/616 (Rev 13:18), 153 (John 21:11), with how rare each value is.
8  BREATH IN THE PSALMS: syllables per half-verse (split at the atnach accent) as breath units.
9  ROOM MODES of the remaining described buildings.
Usage: python3 investigate.py <src dir> <versions dir>"""
import collections, glob, csv, itertools, json, math, os, re, sys, unicodedata
import numpy as np
SRC, VER = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(40); R = {}
def strip(w): return "".join(c for c in unicodedata.normalize("NFD", w) if not unicodedata.combining(c))
def gnorm(w): return re.sub(r"[^α-ω]", "", strip(w.lower()).replace("ς", "σ"))
def hcons(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת").translate(str.maketrans("ךםןףץ", "כמנפצ"))
# ------------------------------------------------------------ sources
BSB = collections.defaultdict(collections.OrderedDict)
for r in csv.DictReader(open(os.path.join(VER, "BSB.csv"), encoding="utf-8")): BSB[r["Book"]][(int(r["Chapter"]), int(r["Verse"]))] = r["Text"]
def quote_share(book):
    inside, out = False, []
    for k, t in BSB[book].items():
        n = q = 0
        for ch in t:
            if ch == "“": inside = True
            elif ch == "”": inside = False
            elif ch.isalpha(): n += 1; q += inside
        out.append(q / max(1, n))
        if not t.rstrip().endswith(("”", "’")) and inside and False: pass
    return list(BSB[book]), np.array(out)
SBL = {}
for f in glob.glob(os.path.join(SRC, "sblgnt", "*-morphgnt.txt")):
    ab = os.path.basename(f).split("-")[1]; V = collections.OrderedDict()
    for l in open(f, encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(pos=p[1], parse=p[2], lem=gnorm(p[6]), w=gnorm(p[5])))
    SBL[ab] = V
def greek_person(ab):
    V = SBL[ab]; return list(V), np.array([sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεισ", "υμεισ") for t in v) / len(v) for v in V.values()])
WLC = {}
for f in sorted(glob.glob(os.path.join(SRC, "morphhb", "wlc", "*.xml"))):
    x = open(f, encoding="utf-8").read(); V = collections.OrderedDict()
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)">(.*?)</verse>', x, re.S):
        body = re.sub(r"<note.*?</note>", "", m.group(3), flags=re.S)
        V[(int(m.group(1)), int(m.group(2)))] = [(w, mo) for mo, w in re.findall(r'<w [^>]*morph="([^"]+)"[^>]*>([^<]+)</w>', body)] if False else \
            [(w, mo) for mo, w in [(re.search(r'morph="([^"]+)"', a).group(1) if 'morph="' in a else "", b) for a, b in re.findall(r"<w ([^>]*)>([^<]+)</w>", body)]]
    if len(V) > 20: WLC[os.path.basename(f)[:-4]] = (V, x)
def hebrew_person(bk):
    V = WLC[bk][0]; s = []
    for toks in V.values():
        n = h = 0
        for w, mo in toks:
            for part in mo.lstrip("HA").split("/"):
                n += 1; h += bool(re.match(r"V[a-zA-Z][pqiwhjv]([12])", part) or re.match(r"P[pf]?([12])", part) or re.match(r"Sp([12])", part))
        s.append(h / max(1, n))
    return list(V), np.array(s)
# ------------------------------------------------------------ segmentation (as rounds 30-31)
def segment(y, k, minseg):
    n = len(y); c = np.concatenate([[0], np.cumsum(y)]); c2 = np.concatenate([[0], np.cumsum(y * y)])
    D = np.full((k + 1, n + 1), np.inf); B = np.zeros((k + 1, n + 1), int); D[0, 0] = 0
    for s in range(1, k + 1):
        for i in range(n):
            if not np.isfinite(D[s - 1, i]): continue
            js = np.arange(i + minseg, n + 1)
            if not len(js): continue
            sm = c[js] - c[i]; v = D[s - 1, i] + (c2[js] - c2[i]) - sm * sm / (js - i); b = v < D[s, js]; D[s, js[b]] = v[b]; B[s, js[b]] = i
    cuts, j = [], n
    for s in range(k, 0, -1): j = B[s, j]; cuts.append(j)
    return sorted(cuts)[1:]
def test(keys, y, ref, k, minseg=None, N=20000):
    n = len(y); minseg = minseg or max(6, n // 25); y = np.convolve(np.pad(y, 2, mode="edge"), np.ones(5) / 5, mode="valid")
    cuts = segment(y, k, minseg); R_ = [keys.index(r) for r in ref]
    sc = lambda cs: np.mean([min(abs(c - r) for r in R_) for c in cs]); s0 = sc(cuts); null = []
    while len(null) < N:
        cs = np.sort(rng.choice(np.arange(minseg, n - minseg), k - 1, replace=False))
        if np.all(np.diff(cs) >= minseg): null.append(sc(cs))
    lab = lambda i: f"{keys[i][0]}:{keys[i][1]}"
    return dict(cuts=[lab(c) for c in cuts], ref=[lab(r) for r in R_], mean_dist=round(float(s0), 1), p=float((np.sum(np.array(null) <= s0) + 1) / (N + 1)))
# 1 + 2 -------------------------------------------------------------------------------------------------------------
print("1-2. VOICE-DRAWN OUTLINES (blind cuts from a speech signal, scored against an agreed outline, 20,000 random cut sets)")
BOOKS = [("John", "Jn", None, [(1, 19), (13, 1), (18, 1)], 4, "Brown's four parts (prologue | signs | farewell | passion)"),
         ("Job", None, "Job", [(3, 1), (32, 1), (38, 1), (42, 7)], 5, "prologue | dialogues | Elihu | the LORD speaks | epilogue"),
         ("Deuteronomy", None, "Deut", [(4, 44), (29, 1), (31, 1)], 4, "Moses' three speeches | the death of Moses"),
         ("Revelation", "Re", None, [(1, 9), (4, 1), (22, 6)], 4, "opening | letters | visions | close (exploratory)"),
         ("Hebrews", "Heb", None, [(4, 14), (10, 19)], 3, "exposition | high priest | exhortation (exploratory)"),
         ("Acts", "Ac", None, [(13, 1)], 2, "Peter | Paul (exploratory control)")]
R["outlines"] = []
for name, g, h, ref, k, desc in BOOKS:
    row = dict(book=name, outline=desc)
    kq, yq = quote_share({"Revelation": "Revelation of John"}.get(name, name)); row["quotes_BSB"] = test(kq, yq, ref, k)
    if name == "Deuteronomy" or name == "Job":
        kh, yh = hebrew_person(h)
        if name == "Deuteronomy": ref_h = [r if r != (29, 1) else (28, 69) for r in ref]
        else: ref_h = ref
        row["person_hebrew"] = test(kh, yh, [r for r in ref_h if r in kh], k)
    else:
        ab = {"Jn": "Jn", "Re": "Re", "Heb": "Heb", "Ac": "Ac"}[g]; kg, yg = greek_person(ab); row["person_greek"] = test(kg, yg, ref, k)
    R["outlines"].append(row)
    for key in ("quotes_BSB", "person_hebrew", "person_greek"):
        if key in row: r = row[key]; print(f"   {name:12s} {key:14s} cuts {' '.join(r['cuts']):24s} outline {' '.join(r['ref']):22s} mean distance {r['mean_dist']:5.1f}  p {r['p']:.4f}")
# where does John's farewell begin under the quote signal at k = 4..6?
kq, yq = quote_share("John"); ys = np.convolve(np.pad(yq, 2, mode="edge"), np.ones(5) / 5, mode="valid")
R["john_farewell"] = {k: [f"{kq[c][0]}:{kq[c][1]}" for c in segment(ys, k, 15)] for k in (4, 5, 6)}
print("   John, translators' quotes, blind cuts at k = 4, 5, 6:", R["john_farewell"])
# 3 ------------------------------------------------------------------------------------------------------------------
print("\n3. KETIV AND QERE")
pairs = []
for bk, (V, x) in WLC.items():
    for m in re.finditer(r'<w[^>]*type="x-ketiv"[^>]*>([^<]+)</w>\s*<note[^>]*>.*?<rdg type="x-qere">(.*?)</rdg>', x, re.S):
        q = "".join(re.findall(r"<w[^>]*>([^<]+)</w>", m.group(2))); pairs.append((bk, hcons(m.group(1)), hcons(q)))
def kind(k, q):
    if k == q: return "same letters (vowels differ)"
    if {k, q} == {"לא", "לו"}: return "lo / lo (not / to him): pure homophone"
    MAT = "אהוי"; sk, sq = re.sub(f"[{MAT}]", "", k), re.sub(f"[{MAT}]", "", q)
    if sk == sq: return "differ only in vowel letters (sound alike)"
    if len(k) == len(q) and sum(a != b for a, b in zip(k, q)) == 1 and {a for a, b in zip(k, q) if a != b} <= set("והי"): return "differ only in vowel letters (sound alike)"
    if sorted(k) == sorted(q): return "letters swapped (seen, not heard)"
    if re.sub(" ", "", k) == q or len(q) > len(k) + 2 or len(k) > len(q) + 2: return "word split, added or dropped"
    return "different sound"
kinds = collections.Counter(kind(k, q) for _, k, q in pairs); n = len(pairs)
R["ketiv_qere"] = dict(pairs=n, kinds=dict(kinds), sound_alike_share=round((kinds["differ only in vowel letters (sound alike)"] + kinds["lo / lo (not / to him): pure homophone"] + kinds["same letters (vowels differ)"]) / n, 3))
for k_, v in kinds.most_common(): print(f"   {v:5d}  {v / n:5.1%}  {k_}")
print(f"   {n} pairs; sound-alike share {R['ketiv_qere']['sound_alike_share']:.0%}")
# 4 ------------------------------------------------------------------------------------------------------------------
print("\n4. MASORETIC MIDPOINTS (Kiddushin 30a) against the Leningrad text")
def flat(books):
    L, W, VV = [], [], []
    for b in books:
        for k, toks in WLC[b][0].items():
            VV.append((b, k)); ws = [hcons(w.replace("/", "")) for w, _ in toks]; ws = [w for w in ws if w]
            for wi, w in enumerate(ws):
                W.append((b, k, w))
                for li, c in enumerate(w): L.append((b, k, w, li))
    return L, W, VV
def mid(L): return L[len(L) // 2] if len(L) % 2 else (L[len(L) // 2 - 1], L[len(L) // 2])
TOR = ["Gen", "Exod", "Lev", "Num", "Deut"]; L, W, VV = flat(TOR); Lp, Wp, VVp = flat(["Ps"])
def ref(t): return f"{t[0]} {t[1][0]}:{t[1][1]}"
def dist_verses(a, b, VVx): return abs(VVx.index(a) - VVx.index(b))
claims = [("Torah middle letter: the vav of gachon, Lev 11:42", mid(L), ("Lev", (11, 42)), VV),
          ("Torah middle words: darosh darash, Lev 10:16", mid(W), ("Lev", (10, 16)), VV),
          ("Torah middle verse: ve-hitgalach, Lev 13:33", mid(VV), ("Lev", (13, 33)), VV),
          ("Psalms middle letter: the ayin of mi-ya'ar, Ps 80:14", mid(Lp), ("Ps", (80, 14)), VVp),
          ("Psalms middle verse: Ps 78:38", mid(VVp), ("Ps", (78, 38)), VVp)]
R["masorah"] = []
for lab, found, claim, VVx in claims:
    f = found if isinstance(found[0], str) else found[0]
    fv = (f[0], f[1]); d = dist_verses(fv, claim, VVx)
    R["masorah"].append(dict(claim=lab, found=ref(fv), verses_away=d, detail=str(found)[:120]))
    print(f"   {lab:58s} computed {ref(fv):14s} ({d} verses away)")
print(f"   (Torah: {len(L):,} letters, {len(W):,} words, {len(VV):,} verses)")
# 5 ------------------------------------------------------------------------------------------------------------------
print("\n5. LIFE AT THE CENTRE, IN GREEK (exact Poisson-binomial, as round 39)")
def centre_test(books, has):
    ps, hits = [], []
    for name, vs in books.items():
        if len(vs) < 20: continue
        L_ = [sum(len(w) for w in ws) for ws in vs]; T = sum(L_); acc = 0
        for c, l in enumerate(L_):
            if acc + l > T / 2: break
            acc += l
        win = [has([w for ws in vs[i - 2:i + 3] for w in ws]) for i in range(2, len(vs) - 2)]; ps.append(np.mean(win))
        if has([w for ws in vs[max(0, c - 2):c + 3] for w in ws]): hits.append(name)
    dist = np.zeros(len(ps) + 1); dist[0] = 1
    for q in ps: dist = np.concatenate([dist[:1] * (1 - q), dist[1:] * (1 - q) + dist[:-1] * q])
    return dict(books=len(ps), hit=len(hits), expected=round(float(sum(ps)), 2), p=float(dist[len(hits):].sum()), which=hits)
ZOE = lambda ws: "ζωη" in ws
nt = {ab: [[t["lem"] for t in v] for v in V.values()] for ab, V in SBL.items()}
lxx = collections.defaultdict(lambda: collections.OrderedDict())
for f in sorted(glob.glob(os.path.join(SRC, "lxx-swete", "data", "*.txt"))):
    b = os.path.basename(f)[3:-4]
    for l in open(f, encoding="utf-8"):
        p = l.split()
        if len(p) == 2: lxx[b].setdefault(p[0], []).append(gnorm(p[1]))
lx = {b: list(v.values()) for b, v in lxx.items()}
ZW = lambda ws: any(w.startswith("ζωη") or w in ("ζωησ",) for w in ws)
R["life_greek"] = dict(NT=centre_test(nt, ZOE), LXX=centre_test(lx, ZW))
for k_, v in R["life_greek"].items(): print(f"   {k_}: {v['hit']} of {v['books']} centres (expected {v['expected']}), exact p {v['p']:.4f}  {v['which']}")
# 6 ------------------------------------------------------------------------------------------------------------------
print("\n6. SEMITIC SOUNDS LEFT UNTRANSLATED IN THE NEW TESTAMENT")
SEM = {"αμην": "amen", "αββα": "abba", "ωσαννα": "hosanna", "μαραναθα": "maranatha", "μαρανα": "maranatha", "σαβαωθ": "sabaoth", "αλληλουια": "hallelujah", "ραββι": "rabbi",
       "ραββουνι": "rabbouni", "ταλιθα": "talitha", "κουμ": "koum", "εφφαθα": "ephphatha", "ελωι": "eloi", "ηλι": "eli", "λεμα": "lema", "σαβαχθανι": "sabachthani", "κορβαν": "korban", "ρακα": "raka", "μαμωνασ": "mammon", "εβραιστι": "(in Hebrew/Aramaic)"}
tab = {}
for ab, V in SBL.items():
    words = sum(len(v) for v in V.values()); c = collections.Counter(SEM[t["lem"]] for v in V.values() for t in v if t["lem"] in SEM)
    tab[ab] = dict(words=words, per_1000=round(sum(c.values()) / words * 1000, 2), terms=dict(c.most_common()))
R["semitic"] = tab
for ab, v in sorted(tab.items(), key=lambda kv: -kv[1]["per_1000"])[:10]: print(f"   {ab:4s} {v['per_1000']:5.2f} per 1,000 words  {v['terms']}")
# amen at the start of a saying ("amen I say to you") vs at the end of a prayer
amen = collections.Counter()
for ab, V in SBL.items():
    for v in V.values():
        for i, t in enumerate(v):
            if t["lem"] == "αμην": amen[(ab, "opens a saying" if i + 1 < len(v) and v[i + 1]["lem"] in ("αμην", "λεγω") else "closes or responds")] += 1
R["amen"] = {f"{a} {b}": c for (a, b), c in amen.items()}
print("   'amen' opening a saying (amen, I say to you):", {a: c for (a, b), c in amen.items() if b == "opens a saying"})
# 7 ------------------------------------------------------------------------------------------------------------------
print("\n7. STATED NUMBERS, CHECKED")
HV = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400])); HV.update({"ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90})
gem = lambda w: sum(HV.get(c, 0) for c in w)
GV = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800])); iso = lambda w: sum(GV.get(c, 0) for c in gnorm(w))
forms = collections.Counter()
for V, _ in WLC.values():
    for toks in V.values():
        for w, _ in toks:
            c = hcons(w.replace("/", ""))
            if c: forms[c] += 0; forms[c] = 1
vals = collections.Counter(gem(w) for w in forms)
checks = [("Eliezer (Gen 15:2) and the 318 men of Gen 14:14", "אליעזר", 318), ("Nero Caesar, Hebrew spelling with final nun (Rev 13:18, 666)", "נרונקסר", 666),
          ("Nero Caesar, Latin-style spelling without it (variant 616, P115 and Codex C)", "נרוקסר", 616), ("'sons of God' (bene ha-Elohim), John 21:11 153 fish", "בניהאלהים", 153)]
R["numbers"] = []
for lab, w, target in checks:
    v = gem(w); R["numbers"].append(dict(claim=lab, word=w, value=v, matches=v == target, bible_forms_with_value=vals[v], share=round(vals[v] / len(forms), 5)))
    print(f"   {lab:78s} {w:10s} = {v:4d}  {'MATCHES' if v == target else 'no'}   ({vals[v]} of {len(forms):,} Bible forms share it)")
tri = [n * (n + 1) // 2 for n in range(1, 30)]; R["numbers"].append(dict(claim="153 = 1+2+...+17 (triangular)", matches=153 in tri))
for lab, w in [("ichthys, fish (singular)", "ιχθυς"), ("ichthyes, fishes (plural)", "ιχθυες"), ("to diktyon, the net (John 21:11)", "τοδικτυον")]:
    R["numbers"].append(dict(claim=lab + " vs 8 x 153 = 1224", value=iso(w), matches=iso(w) == 1224)); print(f"   {lab:40s} = {iso(w)}  {'= 8 x 153' if iso(w) == 1224 else ''}")
print("   153 is triangular (1+...+17):", 153 in tri)
# 8 ------------------------------------------------------------------------------------------------------------------
print("\n8. BREATH UNITS (syllables per half-verse, split at the atnach)")
VOW = set("ְֱֲֳִֵֶַָֹֺֻּ")
def halves(bk):
    out = []
    for toks in WLC[bk][0].values():
        s = "".join(w for w, _ in toks); parts = s.split("֑") if "֑" in s else [s]
        for p in parts:
            syl = sum(1 for c in p if c in "ֱֲֳִֵֶַָֹֺֻ") + p.count("וּ") + p.count("וֹ") * 0
            out.append(syl)
    return np.array(out)
RATE = 4.5    # syllables per second in measured chant-like delivery (round 22 voice model, John)
R["breath"] = {}
for bk in ["Gen", "Exod", "Ps", "Lam", "Song", "Prov", "Job", "Isa"]:
    h = halves(bk); sec = h / RATE + 0.8; R["breath"][bk] = dict(median_syllables=float(np.median(h)), breaths_per_min=round(60 / float(np.median(sec)), 1), cv=round(float(h.std() / h.mean()), 2))
    print(f"   {bk:5s} median {np.median(h):4.0f} syllables per half-verse -> {R['breath'][bk]['breaths_per_min']:5.1f} breaths/min at {RATE} syll/s; evenness (CV) {R['breath'][bk]['cv']}")
# 9 ------------------------------------------------------------------------------------------------------------------
print("\n9. ROOM MODES")
c0 = 343.0
def modes(L, fmax=200):
    return sorted(round(c0 / 2 * math.sqrt(sum((k / l) ** 2 for k, l in zip(n, L))), 1) for n in itertools.product(range(0, 30), repeat=3) if n != (0, 0, 0) and c0 / 2 * math.sqrt(sum((k / l) ** 2 for k, l in zip(n, L))) <= fmax)
ROOMS = [("Tabernacle most holy (10 cubit cube)", (10, 10, 10)), ("Solomon's debir (20 cubit cube)", (20, 20, 20)), ("Solomon's hekal (40 x 20 x 30)", (40, 20, 30)),
         ("Ezekiel's most holy (20 x 20, height taken as 20)", (20, 20, 20)), ("Ezekiel's nave (40 x 20, height 20 assumed)", (40, 20, 20)), ("Ordinary room, same volume as the debir (golden-ish 1 : 1.26 : 1.59)", (20 / 1.26 ** (1 / 1), 20, 20 * 1.26))]
R["rooms"] = []
for nm, d in ROOMS:
    L_ = [x * 0.445 for x in d]; M = modes(L_, 120); u = sorted(set(round(m) for m in M))
    R["rooms"].append(dict(room=nm, dims_m=[round(x, 2) for x in L_], fundamental=M[0], modes_to_120=len(M), distinct_freqs=len(u), freqs=u[:20]))
    print(f"   {nm:62s} fundamental {M[0]:5.1f} Hz; {len(M):3d} modes to 120 Hz on {len(u):3d} distinct frequencies")
nj = 12000 * 185.0; R["rooms"].append(dict(room="New Jerusalem (12,000 stadia cube, Rev 21:16)", side_m=nj, fundamental_hz=c0 / (2 * nj), period_s=2 * nj / c0))
print(f"   New Jerusalem cube: side {nj / 1000:.0f} km; fundamental {c0 / (2 * nj):.2e} Hz = one cycle every {2 * nj / c0 / 3600:.1f} hours")
json.dump(R, open(os.path.join(HERE, "results.json"), "w"), ensure_ascii=False, indent=1, default=str)
