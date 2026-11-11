#!/usr/bin/env python3
"""Round 39, lens 'syriac': the Semitic echo of John (sound-play visible only in Syriac) and the Odes of Solomon.

Hypotheses and decision rules, fixed before running.

TEST 1  Paronomasia density.  Unit = verse.  A verse is a SOUND-PLAY verse when it holds two content words
  (noun / verb / adjective) of DIFFERENT lexemes whose roots sound alike:
    R  same SEDRA root (e.g. 'MR "say" and 'MR' "lamb"),
    S  different roots with the same sound skeleton after merging the gutturals (' h h. ') and dropping the
       weak radicals w, y (guttural merger as in Galilean / later Aramaic speech).
  Measure: share of sound-play verses.  Null: the content words of each book are shuffled across that book's
  verses (verse sizes kept), 1000 times, seed 39.  Excess = observed / null mean; p = share of shuffles >= observed.
  Comparison: John against Matthew, Mark, Luke, Acts (per-verse excess = indicator - null probability of that
  verse; John vs the four pooled, verse-label permutation, 5000 times).
  SYRIAC-ONLY: each Syriac lexeme is given its 3 best Greek equivalents (Dice association over all NT verses,
  SBLGNT/MorphGNT).  A Syriac pair is "also in Greek" if some equivalent of one and some equivalent of the other
  are the same Greek lemma or share a Greek root (prefix-stripped consonant stem; small declared list of
  suppletive families).  Otherwise it is Syriac-only.  The density test is repeated on Syriac-only pairs, and on
  the Greek itself (same-root, different-lemma pairs) to see what John's Greek already has.
  POSITIVE CONTROL: the same skeleton detector run on the Hebrew Bible (WLC, OSHB lemmas) must flag Gen 2:7
  adam/adamah, Amos 8:2 qayits/qets, Jer 1:11-12 shaqed/shoqed (exact skeleton); Isa 5:7 mishpat/mishpach and
  tsedaqah/tse'aqah (near rule: one radical different).  Reported with the base rate of flagged verses.
  Decision: John is "more Syriac-punning" only if its Syriac-only excess beats the pooled comparison books at
  BH q < 0.05.

TEST 2  Odes of Solomon vs John (English, Harris 1911, the same translator also gives the Psalms of Solomon,
  which are the control).  Pre-registered Johannine marker set: word, light, living/life, water, truth, love,
  rest, "I am", "he who / they who / whoever".  Measure: markers per 1000 words.  Null: 300-word chunks of
  Odes + Psalms of Solomon pooled and relabelled at random (10000, seed 39).  Positive control: the same
  markers (Greek equivalents) must separate John from the Synoptics with the same chunk null.
TEST 3  Rank Syriac-only sound-plays in John (rarity of both lexemes + closeness in the verse).

Usage: python3 syriac.py <syrnt tf dir> <sblgnt dir> <morphhb wlc dir> <odes djvu txt> <outdir>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tfload as T

SYR, SBL, WLC, ODES, OUT = sys.argv[1:6]
RNG = np.random.default_rng(39)
NSHUF = 1000
RES = {"tests": []}

# ---------------------------------------------------------------- Syriac NT
bk = T.node_feature(SYR, "book"); ch = T.node_feature(SYR, "chapter"); vs = T.node_feature(SYR, "verse")
osl = T.oslots(SYR)
LX = T.node_feature(SYR, "lexeme_etcbc"); RT = T.node_feature(SYR, "root_etcbc")
WD = T.node_feature(SYR, "word_etcbc"); SP = T.node_feature(SYR, "sp"); WS = T.node_feature(SYR, "word")
vtype = [t for t in T.otypes(SYR) if t[2] == "verse"][0]
SVERSES = collections.OrderedDict()   # (book, ch, v) -> list of word slots
for n in range(vtype[0], vtype[1] + 1):
    SVERSES[(bk[n], int(ch[n]), int(vs[n]))] = osl[n]
CONTENT = {"noun", "verb", "adjective"}
TR = {">": "ʾ", "B": "b", "G": "g", "D": "d", "H": "h", "W": "w", "Z": "z", "X": "ḥ", "V": "ṭ", "J": "y", "K": "k",
      "L": "l", "M": "m", "N": "n", "S": "s", "<": "ʿ", "P": "p", "Y": "ṣ", "Q": "q", "R": "r", "C": "š", "T": "t", "F": "ś"}
def tr(s): return "".join(TR.get(c, c) for c in s)
def skel(root):
    s = re.sub(r"[>HX<]", "@", root); s = s.replace("W", "").replace("J", "")   # '@' = any guttural (ETCBC 'G' is gimel)
    return s
def skel_ok(k):  # a sound skeleton must carry real consonants: 3+ radicals, or 2 non-gutturals
    return len(k) >= 3 or (len(k) == 2 and "@" not in k)

# ---------------------------------------------------------------- Greek NT
GB = {"Matt": "Mt", "Mark": "Mk", "Luke": "Lk", "John": "Jn", "Acts": "Ac", "Rom": "Ro", "1Cor": "1Co", "2Cor": "2Co",
      "Gal": "Ga", "Eph": "Eph", "Phil": "Php", "Col": "Col", "1Thess": "1Th", "2Thess": "2Th", "1Tim": "1Ti",
      "2Tim": "2Ti", "Titus": "Tit", "Phlm": "Phm", "Heb": "Heb", "James": "Jas", "1Peter": "1Pe", "2Peter": "2Pe",
      "1John": "1Jn", "2John": "2Jn", "3John": "3Jn", "Jude": "Jud", "Rev": "Re"}
def gn(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
GVERSES = {}
for sb, gb in GB.items():
    f = glob.glob(os.path.join(SBL, f"*-{gb}-morphgnt.txt"))
    if not f: continue
    for l in open(f[0], encoding="utf-8"):
        p = l.split(); key = (sb, int(p[0][2:4]), int(p[0][4:6]))
        GVERSES.setdefault(key, []).append((gn(p[6]), p[1]))
GCONTENT = ("N-", "V-", "A-")
PREF = sorted("αντι ανα απο αφ απ δια εισ εκ εξ εν εμ εγ επι εφ επ κατα καθ κατ μετα μεθ μετ παρα παρ περι προσ προ συν συμ συλ συγ συσ υπερ υπο υφ υπ".split(), key=len, reverse=True)
SUPPLETIVE = [{"ζαω", "ζωη", "ζωοποιεω"}, {"φωσ", "φωτιζω", "φωτεινοσ", "φωτισμοσ"}, {"οραω", "ειδον", "οψισ", "οπτασια"},
              {"λεγω", "ειπον", "ρημα", "ερω"}, {"ερχομαι", "ηλθον"}, {"πασχω", "παθοσ", "παθημα"}, {"γινωσκω", "γνωσισ", "γνωστοσ"},
              {"γενναω", "γενοσ", "γενεα", "γινομαι", "γενεσισ"}, {"πινω", "ποτηριον", "ποτιζω", "ποτον"}, {"εσθιω", "φαγω", "βρωμα", "βρωσισ"}]
def gstem(l):
    for p in PREF:
        if l.startswith(p) and len(l) - len(p) >= 4:
            l = l[len(p):]; break
    return l
def gskel(l): return re.sub(r"[αεηιουω]", "", gstem(l))
import functools
@functools.lru_cache(maxsize=None)
def groot_same(a, b):
    if a == b: return True
    for fam in SUPPLETIVE:
        if a in fam and b in fam: return True
    sa, sb = gstem(a), gstem(b)
    if len(sa) >= 4 and len(sb) >= 4 and sa[:4] == sb[:4]: return True
    ka, kb = gskel(a), gskel(b)
    k = min(len(ka), len(kb), 2)   # two stem consonants (κρινω/κρισισ, θνησκω/θανατοσ): errs toward "also in Greek"
    if k >= 2 and ka[:k] == kb[:k] and sa[0] == sb[0]: return True
    fa, fb = re.sub(r"[αεηιουω]", "", a), re.sub(r"[αεηιουω]", "", b)   # unstripped (απολλυμι / απωλεια)
    k = min(len(fa), len(fb), 3)
    return k >= 2 and fa[:k] == fb[:k] and a[0] == b[0]

# ---------------------------------------------------------------- Syriac -> Greek equivalents (Dice)
sy_df = collections.Counter(); gr_df = collections.Counter(); co = collections.Counter()
for key, slots in SVERSES.items():
    g = GVERSES.get(key)
    if not g: continue
    L = {LX[s] for s in slots if SP.get(s) in CONTENT}
    G = {w for w, pos in g if pos in GCONTENT}
    for a in L: sy_df[a] += 1
    for b in G: gr_df[b] += 1
    for a in L:
        for b in G: co[(a, b)] += 1
EQ = collections.defaultdict(list)
DICE = {}
for (a, b), c in co.items():
    DICE[(a, b)] = 2 * c / (sy_df[a] + gr_df[b])
    EQ[a].append((DICE[(a, b)], b))
for a in EQ: EQ[a] = [b for d, b in sorted(EQ[a], reverse=True)[:3]]
def in_greek(a, b):
    return any(groot_same(x, y) for x in EQ.get(a, []) for y in EQ.get(b, []))
def in_greek_verse(a, b, key):
    """verse-local check: the Greek word of this verse best associated with each Syriac lexeme; same lemma/root?"""
    G = sorted({w for w, pos in GVERSES.get(key, []) if pos in GCONTENT})
    if not G: return in_greek(a, b), None, None
    ga = max(G, key=lambda w: DICE.get((a, w), 0)); gb = max(G, key=lambda w: DICE.get((b, w), 0))
    if ga == gb and len(G) > 1:   # one Greek word cannot render both Syriac words: give it to the stronger link
        if DICE.get((a, ga), 0) >= DICE.get((b, gb), 0): gb = max([w for w in G if w != ga], key=lambda w: DICE.get((b, w), 0))
        else: ga = max([w for w in G if w != gb], key=lambda w: DICE.get((a, w), 0))
    return groot_same(ga, gb), ga, gb

# ---------------------------------------------------------------- book token tables and pair finder
BOOKS = ["John", "Matt", "Mark", "Luke", "Acts"]
def book_tokens(book):
    keys = [k for k in SVERSES if k[0] == book]
    toks = []   # (verse index, position, lexeme, root)
    for vi, k in enumerate(keys):
        for pos, s in enumerate(SVERSES[k]):
            if SP.get(s) in CONTENT and RT.get(s):
                toks.append((vi, pos, LX[s], RT[s], s))
    return keys, toks

def verse_pairs(lexroots, kind):
    """lexroots: list of (lex, root) in one verse.  Returns set of unordered lexeme pairs that sound-play."""
    out = set()
    by = collections.defaultdict(set)
    for lx, rt in lexroots:
        k = rt if kind == "R" else skel(rt)
        if kind == "S" and not skel_ok(k): continue
        by[k].add((lx, rt))
    for k, items in by.items():
        if len(items) < 2: continue
        items = sorted(items)
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                (l1, r1), (l2, r2) = items[i], items[j]
                if l1 == l2: continue
                if kind == "R" and r1 != r2: continue
                if kind == "S" and r1 == r2: continue
                out.add((l1, l2))
    return out

PAIRCACHE = {}
def pair_flags(groups, filt):
    """groups: per verse list of (lex, root).  filt in {'all', 'syr_only'}"""
    flags = np.zeros(len(groups), bool)
    for i, g in enumerate(groups):
        ps = verse_pairs(g, "S") if filt == "S_syr_only" else verse_pairs(g, "R") | verse_pairs(g, "S")
        if filt in ("syr_only", "S_syr_only"):
            ps = {p for p in ps if not PAIRCACHE.setdefault(p, in_greek(*p))}
        flags[i] = bool(ps)
    return flags

def density(book, filt):
    keys, toks = book_tokens(book)
    nv = len(keys)
    vi = np.array([t[0] for t in toks]); lr = [(t[2], t[3]) for t in toks]
    def groups_from(vidx):
        g = [[] for _ in range(nv)]
        for v, x in zip(vidx, lr): g[v].append(x)
        return g
    obs = pair_flags(groups_from(vi), filt)
    nullp = np.zeros(nv); nullshare = []
    for _ in range(NSHUF):
        f = pair_flags(groups_from(RNG.permutation(vi)), filt)
        nullp += f; nullshare.append(f.mean())
    nullp /= NSHUF; nullshare = np.array(nullshare)
    p = (1 + np.sum(nullshare >= obs.mean())) / (NSHUF + 1)
    return dict(verses=nv, observed=float(obs.mean()), null_mean=float(nullshare.mean()), null_sd=float(nullshare.std()),
                excess_ratio=float(obs.mean() / nullshare.mean()), p=float(p)), obs.astype(float) - nullp

def compare(ex, label):
    j = ex["John"]; o = np.concatenate([ex[b] for b in BOOKS[1:]]); allv = np.concatenate([j, o])
    d = j.mean() - o.mean(); cnt = 0
    for _ in range(5000):
        perm = RNG.permutation(allv); cnt += perm[:len(j)].mean() - perm[len(j):].mean() >= d
    return dict(john_excess_per_verse=float(j.mean()), others_excess_per_verse=float(o.mean()), diff=float(d), p=float((cnt + 1) / 5001))

T1 = {}
for filt in ("all", "syr_only", "S_syr_only"):
    T1[filt] = {}; ex = {}
    for b in BOOKS:
        r, e = density(b, filt); T1[filt][b] = r; ex[b] = e
        RES["tests"].append((f"T1 {filt}: {b} sound-play verses vs shuffle null", r["p"]))
        print(f"T1 {filt:8s} {b:5s} obs {r['observed']:.3f} null {r['null_mean']:.3f} ratio {r['excess_ratio']:.2f} p {r['p']:.4f}")
    c = compare(ex, filt); T1[filt]["John_vs_others"] = c
    RES["tests"].append((f"T1 {filt}: John excess > Mt+Mk+Lk+Acts", c["p"]))
    print(f"   John vs others ({filt}): {c}")

# ---------------------------------------------------------------- Greek same-root density (what John's Greek already has)
GSTOPV = {"ειμι", "λεγω", "γινομαι", "εχω", "ποιεω", "ερχομαι"}
def gdensity(book):
    keys = [k for k in GVERSES if k[0] == book]
    toks = [(vi, w) for vi, k in enumerate(keys) for w, pos in GVERSES[k] if pos in GCONTENT]
    vi = np.array([t[0] for t in toks]); ws = [t[1] for t in toks]
    keyof = {w: (gskel(w)[:3], gstem(w)[0]) for w in set(ws)}
    def flags(vidx):
        g = [set() for _ in keys]
        for v, w in zip(vidx, ws): g[v].add(w)
        f = np.zeros(len(keys), bool)
        for i, s in enumerate(g):
            s = sorted(s); hit = False
            for a in range(len(s)):
                for b in range(a + 1, len(s)):
                    if groot_same(s[a], s[b]): hit = True; break
                if hit: break
            f[i] = hit
        return f
    obs = flags(vi); nulls = []; nullp = np.zeros(len(keys))
    for _ in range(200):
        f = flags(RNG.permutation(vi)); nulls.append(f.mean()); nullp += f
    nulls = np.array(nulls); nullp /= 200
    return dict(verses=len(keys), observed=float(obs.mean()), null_mean=float(nulls.mean()), excess_ratio=float(obs.mean() / nulls.mean()),
                p=float((1 + np.sum(nulls >= obs.mean())) / 201)), obs - nullp
T1["greek_same_root"] = {}; gex = {}
for b in BOOKS:
    r, e = gdensity(b); T1["greek_same_root"][b] = r; gex[b] = e
    print(f"T1 greek    {b:5s} obs {r['observed']:.3f} null {r['null_mean']:.3f} ratio {r['excess_ratio']:.2f}")
c = compare(gex, "greek"); T1["greek_same_root"]["John_vs_others"] = c
RES["tests"].append(("T1 greek: John same-root excess > Mt+Mk+Lk+Acts", c["p"])); print("   Greek John vs others:", c)
RES["T1"] = T1

# ---------------------------------------------------------------- Hebrew positive control
def hnorm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת")
    return s.translate(str.maketrans("ךםןףץ", "כמנפצ"))
def hskel(stem):
    s = hnorm(stem).replace("ו", "").replace("י", "")
    if len(s) > 2 and s.endswith("ה"): s = s[:-1]
    return re.sub("[אהחע]", "G", s)
HV = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    if "VerseMap" in f: continue
    x = open(f, encoding="utf-8").read()
    for vid, body in re.findall(r'<verse osisID="([^"]+)">(.*?)</verse>', x, flags=re.S):
        toks = []
        for lem, morph, txt in re.findall(r'<w lemma="([^"]*)"[^>]*?morph="([^"]*)"[^>]*>([^<]*)</w>', body):
            lp = lem.split("/"); mp = morph[1:].split("/"); tp = txt.split("/")
            for a, m, t in zip(lp, mp, tp):
                if re.match(r"\d", a) and m[:1] in "NVA" and not m.startswith("Np"):
                    toks.append((a.split()[0], hskel(t)))
        HV[vid] = toks
def hpairs(toks, near=False):
    out = set()
    for i in range(len(toks)):
        for j in range(i + 1, len(toks)):
            (l1, s1), (l2, s2) = toks[i], toks[j]
            if l1 == l2 or not (len(s1) >= 3 or (len(s1) == 2 and "G" not in s1)) or not (len(s2) >= 3 or (len(s2) == 2 and "G" not in s2)): continue
            if s1 == s2: out.add(tuple(sorted((l1, l2))))
            elif near and len(s1) == len(s2) >= 3 and sum(a != b for a, b in zip(s1, s2)) == 1: out.add(tuple(sorted((l1, l2))))
    return out
CONTROLS = [("Gen 2:7 adam/adamah", ["Gen.2.7"], {"120", "127"}, False),
            ("Amos 8:2 qayits/qets", ["Amos.8.2"], {"7019", "7093"}, False),
            ("Jer 1:11-12 shaqed/shoqed", ["Jer.1.11", "Jer.1.12"], {"8247", "8245"}, False),
            ("Isa 5:7 mishpat/mishpach", ["Isa.5.7"], {"4941", "4939"}, True),
            ("Isa 5:7 tsedaqah/tse'aqah", ["Isa.5.7"], {"6666", "6818"}, True)]
ctrl = []
for name, vids, lems, near in CONTROLS:
    toks = [t for v in vids for t in HV[v]]
    hit = tuple(sorted(lems)) in hpairs(toks, near)
    ctrl.append(dict(control=name, rule="near (one radical)" if near else "exact skeleton", found=hit))
    print("control", name, hit)
hflag = np.array([bool(hpairs(t)) for t in HV.values()]); hnear = np.array([bool(hpairs(t, True)) for t in HV.values()])
RES["hebrew_control"] = dict(controls=ctrl, verses=len(HV), share_flagged_exact=float(hflag.mean()), share_flagged_near=float(hnear.mean()))
# Hebrew aggregate: prophets known for paronomasia (Casanowicz 1894) vs shuffle null, Isaiah and Genesis
def hdens(book):
    keys = [k for k in HV if k.split(".")[0] == book]
    toks = [(vi, t) for vi, k in enumerate(keys) for t in HV[k]]
    vi = np.array([a for a, _ in toks]); tt = [b for _, b in toks]
    def fl(v):
        g = [[] for _ in keys]
        for a, b in zip(v, tt): g[a].append(b)
        return np.mean([bool(hpairs(x)) for x in g])
    obs = fl(vi); nulls = np.array([fl(RNG.permutation(vi)) for _ in range(100)])
    return dict(observed=float(obs), null_mean=float(nulls.mean()), excess_ratio=float(obs / nulls.mean()), p=float((1 + np.sum(nulls >= obs)) / 101))
RES["hebrew_control"]["books"] = {b: hdens(b) for b in ("Gen", "Isa", "Amos", "Jer")}
print(RES["hebrew_control"]["books"])

# ---------------------------------------------------------------- TEST 3 ranking
NTFREQ = collections.Counter(LX[s] for slots in SVERSES.values() for s in slots if SP.get(s) in CONTENT)
NTOT = sum(NTFREQ.values())
cands = {}
keys, toks = book_tokens("John")
byv = collections.defaultdict(list)
for t in toks: byv[t[0]].append(t)
pairseen = collections.Counter()
for vi, tl in byv.items():
    lr = [(t[2], t[3]) for t in tl]
    for kind in ("R", "S"):
        for (a, b) in verse_pairs(lr, kind):
            pairseen[(a, b)] += 1
            if keys[vi] not in GVERSES: continue          # verse absent from the Greek (e.g. John 5:4)
            ig, ga, gb = in_greek_verse(a, b, keys[vi])
            if ig: continue
            ta = [t for t in tl if t[2] == a]; tb = [t for t in tl if t[2] == b]
            dist = min(abs(x[1] - y[1]) for x in ta for y in tb)
            rar = -math.log10(NTFREQ[a] / NTOT) - math.log10(NTFREQ[b] / NTOT)
            sc = rar - math.log10(1 + dist)
            k = (a, b)
            if k not in cands or cands[k]["score"] < sc:
                x, y = min(((x, y) for x in ta for y in tb), key=lambda p: abs(p[0][1] - p[1][1]))
                ref = keys[vi]
                cands[k] = dict(verse=f"John {ref[1]}:{ref[2]}", kind=kind, lex1=a, lex2=b, root1=x[3], root2=y[3],
                                word1=WD[x[4]], word2=WD[y[4]], syriac1=WS[x[4]], syriac2=WS[y[4]],
                                translit1=tr(WD[x[4]]), translit2=tr(WD[y[4]]), root_translit=f"{tr(x[3])} / {tr(y[3])}",
                                greek_in_verse1=ga, greek_in_verse2=gb, greek_equiv1=EQ.get(a, []), greek_equiv2=EQ.get(b, []), distance=dist, rarity=round(rar, 2), score=round(sc, 2))
for k in cands: cands[k]["verses_in_john_with_pair"] = pairseen[k]
top = sorted(cands.values(), key=lambda d: -d["score"])
RES["T3_top_syriac_only"] = top[:60]; RES["T3_n_candidates"] = len(top)
for d in top[:60]:
    print(d["verse"], d["kind"], d["translit1"], d["translit2"], d["root_translit"], d["greek_in_verse1"], d["greek_in_verse2"], d["score"], d["verses_in_john_with_pair"])

# ---------------------------------------------------------------- TEST 2 Odes of Solomon vs Psalms of Solomon (English, Harris 1911)
raw = open(ODES, encoding="utf-8", errors="replace").read().split("\n")
def clean(lines):
    keep = []
    for l in lines:
        s = l.strip()
        if not s or re.match(r"^(\d+\s*)?THE (ODES|PSALMS) OF SOLOMON", s) or re.search(r"PSALMS OF SOLOMON\s*\S*$", s) and len(s) < 40: continue
        if re.match(r"^[\^'\"\d]*\s*(Or|Lit\.|lit\.|Cf\.|Gk\.|Syr\.|Hi\.|MS)", s) and len(s) < 90: continue
        if re.match(r"^\d+\s+[A-Z][a-z]+\s*:", s): continue
        keep.append(s)
    return " ".join(keep)
odes, pss = [], []
i = 0; n = len(raw)
start = next(k for k, l in enumerate(raw) if l.startswith("ODE I. {Pistis"))
pstart = next(k for k, l in enumerate(raw) if l.startswith("PSALM 43 = Psalms of Solomon"))
pend = next(k for k, l in enumerate(raw) if k > pstart and l.strip().startswith("(Caetera desunt.)"))
k = start; cur = None; buf = []
while k < pstart:
    l = raw[k]
    if re.match(r"^ODE [\dIlTSsio]+\.?", l):
        if cur is not None: odes.append(clean(buf))
        cur = l; buf = []
    elif re.match(r"^Ode \d+ ?\d*\.", l):      # commentary starts: stop collecting until the next ODE heading
        if cur is not None: odes.append(clean(buf)); cur = None; buf = []
    elif cur is not None: buf.append(l)
    k += 1
if cur is not None: odes.append(clean(buf))
buf = []
for l in raw[pstart:pend]:
    if re.match(r"^PSALM \S+ .*= Ps", l):
        if buf: pss.append(clean(buf)); buf = []
    else: buf.append(l)
if buf: pss.append(clean(buf))
def ewords(t): return re.findall(r"[a-z]+", t.lower().replace("’", "'"))
OW = [w for t in odes for w in ewords(t)]; PW = [w for t in pss for w in ewords(t)]
MARK = {"word": lambda ws, i: ws[i] in ("word", "words"),
        "light": lambda ws, i: ws[i] in ("light", "lights", "lighted", "lightened", "illuminated", "illumination"),
        "life/living": lambda ws, i: ws[i] in ("life", "living", "live", "liveth", "lives", "lived", "alive"),
        "water": lambda ws, i: ws[i] in ("water", "waters"),
        "truth": lambda ws, i: ws[i] in ("truth", "true", "truly"),
        "love": lambda ws, i: ws[i] in ("love", "loved", "loves", "loveth", "lover", "beloved", "loving"),
        "rest": lambda ws, i: ws[i] in ("rest", "rested", "resting"),
        "I am": lambda ws, i: ws[i] == "i" and i + 1 < len(ws) and ws[i + 1] == "am",
        "he who": lambda ws, i: (ws[i] in ("he", "they", "him", "those") and i + 1 < len(ws) and ws[i + 1] in ("who", "that") ) or ws[i] == "whoever" or ws[i] == "whosoever"}
def counts(ws):
    c = {m: 0 for m in MARK}
    for i in range(len(ws)):
        for m, f in MARK.items():
            if f(ws, i): c[m] += 1
    return c
def rate(ws): c = counts(ws); return {m: 1000 * v / len(ws) for m, v in c.items()}, 1000 * sum(c.values()) / len(ws)
def chunk(ws, n=300): return [ws[i:i + n] for i in range(0, len(ws) - n + 1, n)]
def chunk_null(A, B, label, measure_terms=True, n=10000):
    ca, cb = chunk(A), chunk(B)
    va = np.array([[v for v in counts(c).values()] for c in ca], float); vb = np.array([[v for v in counts(c).values()] for c in cb], float)
    allv = np.vstack([va, vb]); na = len(va)
    obs_tot = va.sum(1).mean() - vb.sum(1).mean(); obs_term = va.mean(0) - vb.mean(0)
    ge_tot = 0; ge_term = np.zeros(len(MARK))
    for _ in range(n):
        p = RNG.permutation(len(allv)); a, b = allv[p[:na]], allv[p[na:]]
        ge_tot += a.sum(1).mean() - b.sum(1).mean() >= obs_tot
        ge_term += (a.mean(0) - b.mean(0)) >= obs_term
    return dict(chunks=[na, len(vb)], diff_markers_per_300w=float(obs_tot), p_total=float((ge_tot + 1) / (n + 1)),
                per_term={m: dict(diff_per_300w=float(d), p=float((g + 1) / (n + 1))) for m, d, g in zip(MARK, obs_term, ge_term)})
ro, to = rate(OW); rp, tp = rate(PW)
t2 = dict(odes_words=len(OW), odes_count=len(odes), psssol_words=len(PW), pssol_count=len(pss), odes_rates=ro, odes_total=to, pssol_rates=rp, pssol_total=tp)
t2["odes_vs_pssol"] = chunk_null(OW, PW, "odes")
RES["tests"].append(("T2 Odes > Psalms of Solomon, Johannine markers (total)", t2["odes_vs_pssol"]["p_total"]))
for m, d in t2["odes_vs_pssol"]["per_term"].items(): RES["tests"].append((f"T2 Odes > PsSol: {m}", d["p"]))
print("T2 odes", len(odes), len(OW), "pssol", len(pss), len(PW), to, tp, t2["odes_vs_pssol"]["p_total"])
# Greek positive control: John vs Synoptics, same markers in Greek
GMARK = {"word": lambda ws, i: ws[i] in ("λογοσ",), "light": lambda ws, i: ws[i] in ("φωσ", "φωτιζω", "φαινω"),
         "life/living": lambda ws, i: ws[i] in ("ζωη", "ζαω", "ζωοποιεω"), "water": lambda ws, i: ws[i] == "υδωρ",
         "truth": lambda ws, i: ws[i] in ("αληθεια", "αληθησ", "αληθινοσ", "αληθωσ"), "love": lambda ws, i: ws[i] in ("αγαπαω", "αγαπη", "αγαπητοσ", "φιλεω"),
         "rest": lambda ws, i: ws[i] in ("αναπαυσισ", "αναπαυω", "καταπαυσισ"),
         "I am": lambda ws, i: ws[i] == "εγω" and i + 1 < len(ws) and ws[i + 1] == "ειμι",
         "he who": lambda ws, i: ws[i] == "ο" and i + 1 < len(ws) and ws[i + 1].startswith("PTC")}
def glemmas(book):
    out = []
    for k in [k for k in GVERSES if k[0] == book]:
        for w, pos in GVERSES[k]: out.append(w)
    return out
# participles need morphology: rebuild with a marker
def glem_ptc(book):
    gb = GB[book]; out = []
    for l in open(glob.glob(os.path.join(SBL, f"*-{gb}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); w = gn(p[6])
        out.append(w)
        if p[1] == "RA" and False: pass
    # mark article followed by participle
    toks = [l.split() for l in open(glob.glob(os.path.join(SBL, f"*-{gb}-morphgnt.txt"))[0], encoding="utf-8")]
    res = []
    for i, p in enumerate(toks):
        if p[1] == "RA" and i + 1 < len(toks) and toks[i + 1][2][3:4] == "P" and toks[i + 1][1] == "V-": res += ["ο", "PTC"]
        else: res.append(gn(p[6]))
    return res
MARK_SAVE = MARK; MARK = GMARK
Jg = glem_ptc("John"); Sg = glem_ptc("Matt") + glem_ptc("Mark") + glem_ptc("Luke")
t2["greek_control_john_vs_synoptics"] = chunk_null(Jg, Sg, "greek", n=3000)
MARK = MARK_SAVE
RES["tests"].append(("T2 control: John > Synoptics, Johannine markers (Greek)", t2["greek_control_john_vs_synoptics"]["p_total"]))
print("T2 greek control", t2["greek_control_john_vs_synoptics"]["diff_markers_per_300w"], t2["greek_control_john_vs_synoptics"]["p_total"])
# where do the Odes sit on a John <-> Synoptics scale?  ratio of rates
t2["note"] = "English (Odes, PsSol) and Greek (John, Synoptics) rates are not on one scale; compare the lean (ratio), not the level."
RES["T2"] = t2

# ---------------------------------------------------------------- Benjamini-Hochberg
names = [t[0] for t in RES["tests"]]; ps = np.array([t[1] for t in RES["tests"]]); m = len(ps)
order = np.argsort(ps); q = np.empty(m); prev = 1.0
for r, i in reversed(list(enumerate(order, 1))):
    prev = min(prev, ps[i] * m / r); q[i] = prev
RES["tests"] = [dict(test=nm, p=float(p), q_bh=float(qq), significant=bool(qq < 0.05)) for nm, p, qq in zip(names, ps, q)]
RES["n_tests"] = m
json.dump(RES, open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for t in RES["tests"]: print(f"{t['p']:.4f} {t['q_bh']:.4f} {'*' if t['significant'] else ' '} {t['test']}")
