#!/usr/bin/env python3
"""Round 39, scribal lens: the copyists' own marks as data.

Usage:
  python3 round39/scribal/scribal.py sources/texts/cntr/"class 1" sources/texts/sblgnt \
          sources/texts/sblgnt-logos/data/sblgnt/xml code/engine round39/scribal/results.json

Data: CNTR MES transcriptions (Bunning, CC BY-SA 4.0). The MES encodes nomina sacra ('='), the overline/
suspension stroke (U+00AF), staurogram (U+2CE8), kai-compendium (U+03D7), line '/', column '|', page '\\' breaks,
corrections (x{original} {first-hand} a{2nd hand} b{3rd}), supplied words ('~'), missing ('^') and damaged ('%')
letters. It does NOT encode punctuation, high points, diaeresis, spacing (vacats) or paragraph signs, so Test 4
uses a layout proxy: a SHORT LINE (a line that the scribe left unfilled) = a sense break by the scribe.

PRE-REGISTERED TESTS (written before results were looked at)

T1  Nomina sacra as a theological signal. For each sacred word group in each manuscript: contraction rate.
    For groups with a referent contrast (theos, kyrios, pneuma, pater, huios, anthropos) every SBLGNT occurrence
    is labelled D (divine / sacred referent: God, Jesus, the divine Spirit; for anthropos: Son of Man or Jesus)
    or H (human, pagan, plural gods/masters/fathers/sons, wind, a person's spirit) or A (ambiguous, excluded),
    by rule (plural -> H) plus a fixed override list of verses written from the Greek before any manuscript was
    tabulated. Manuscript tokens are aligned to SBLGNT occurrences of the same group within the verse (equal
    counts -> in order; else only if all SBLGNT labels agree). Supplied or lacunose tokens are not counted.
    Test: exact two-sided Fisher test of contracted x label, per manuscript x corpus (John / Paul) x group,
    run when both labels have n >= 3 and contraction varies. Decision: BH q <= 0.05.
    Positive control: synthetic manuscript with contraction tied to label (90% D, 30% H) on real label
    counts (power); negative control: labels shuffled (false-positive rate).
T2  Staurogram and other special signs. List every staurogram; test it is confined to the stauros/stauroo words.
    Layout control: the nu-suspension stroke and kai-compendium should sit at line ends (space saving).
T3  Corrections map. LOADED verses of John, fixed before counting: L1 prologue 1:1-18; L2 'I am' verses
    (ego + eimi 1st sg adjacent); L3 Christological-title verses (Christos, Messias, monogenes, soter, amnos,
    huios + theou / anthropou within 3 words); L4 passion 18:1-19:42. Union = LOADED.
    Measure: corrections per surviving (seen) letter, loaded / other. Null (primary): circular shift of the
    loaded mask over the manuscript's verse sequence (keeps the blocks and the scribe's local habits).
    Secondary null: multinomial placement weighted by surviving letters. One-sided (more at loaded).
    Manuscripts: P66 (first-hand corrections, Royse) and 01 primary; P75, 03, 02 secondary.
    Positive control: synthetic corrections at 2x rate in loaded verses (power of the shift test).
    Sound: share of substitution corrections whose two readings sound identical in late Koine (engine phonology),
    Attic as control; compared with the C11 variant share.
T4  Scribes' breaks. Short line: complete line, < 0.6 x local median line length (+-20 lines), ending between
    words. Positive control: verses where SBLGNT starts a paragraph should begin after a short line more often
    than other verse starts (permutation of labels among observable verse starts).
    Main: distance (verses) from the C24 cuts {1:16, 13:33, 18:1} to the nearest scribal short-line break,
    against (a) random verse starts the manuscript preserves, (b) random SBLGNT paragraph starts (harder null).
"""
import collections, json, math, os, re, sys, types, unicodedata
import numpy as np

CN, SBL, SXML, ENG, OUT = sys.argv[1:6]
RNG_SEED = 39
R = {}

# ---------------------------------------------------------------- basic normalisation
def strip_acc(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))

def canon(w):  # spelling-insensitive key for matching (itacism ει/ι)
    return w.replace("ει", "ι")

BOOKS_SBL = {}  # cntr book number -> morphgnt file
for f in sorted(os.listdir(SBL)):
    m = re.match(r"(\d\d)-(\w+)-morphgnt\.txt", f)
    if m: BOOKS_SBL[int(m.group(1)) - 21] = f   # 61-Mt -> 40
XMLNAME = {40: "Matt", 41: "Mark", 42: "Luke", 43: "John", 44: "Acts", 45: "Rom", 46: "1Cor", 47: "2Cor", 48: "Gal", 49: "Eph",
           50: "Phil", 51: "Col", 52: "1Thess", 53: "2Thess", 58: "Heb"}
JOHN, PAUL = [43], [45, 46, 47, 48, 49, 50, 51, 52, 58]
CORPUS = {"John": JOHN, "Paul": PAUL}

# ---------------------------------------------------------------- SBLGNT (MorphGNT) by verse
GROUP_OF_LEMMA = {"θεοσ": "θεος", "κυριοσ": "κυριος", "ιησουσ": "ιησους", "χριστοσ": "χριστος", "πνευμα": "πνευμα",
                  "πατηρ": "πατηρ", "υιοσ": "υιος", "ανθρωποσ": "ανθρωπος", "σταυροσ": "σταυρ", "σταυροω": "σταυρ",
                  "συσταυροω": "σταυρ", "ανασταυροω": "σταυρ", "ουρανοσ": "ουρανος", "ισραηλ": "ισραηλ", "δαυιδ": "δαυιδ",
                  "μητηρ": "μητηρ", "ιερουσαλημ": "ιερουσαλημ", "ιεροσολυμα": "ιερουσαλημ", "σωτηρ": "σωτηρ"}
GROUPS = ["θεος", "κυριος", "ιησους", "χριστος", "πνευμα", "πατηρ", "υιος", "ανθρωπος", "σταυρ", "ουρανος", "ισραηλ",
          "δαυιδ", "μητηρ", "ιερουσαλημ", "σωτηρ"]
CONTRAST = ["θεος", "κυριος", "πνευμα", "πατηρ", "υιος", "ανθρωπος"]

SB = collections.OrderedDict()  # (book,ch,vs) -> list of dicts
FORM2GROUP = {}
for b, f in BOOKS_SBL.items():
    for line in open(os.path.join(SBL, f), encoding="utf-8"):
        p = line.split()
        ref = (b, int(p[0][2:4]), int(p[0][4:6]))
        lem = strip_acc(p[6]); w = strip_acc(p[5]); g = GROUP_OF_LEMMA.get(lem)
        SB.setdefault(ref, []).append(dict(w=w, lem=lem, pos=p[1], parse=p[2], group=g, word=p[3]))
        if g: FORM2GROUP[canon(w)] = g
for extra, g in (("δαυειδ", "δαυιδ"), ("δαυιδ", "δαυιδ"), ("δαβιδ", "δαυιδ"), ("ιερουσαλημ", "ιερουσαλημ"), ("ιηρουσαλημ", "ιερουσαλημ"),
                 ("ισραηλ", "ισραηλ"), ("ιστραηλ", "ισραηλ")):
    FORM2GROUP[canon(extra)] = g

# ---------------------------------------------------------------- referent labels (rules + fixed overrides)
# override value: 'H' all occurrences of the group in the verse are human/other; 'A' ambiguous; or a string of
# per-occurrence labels in SBLGNT order, e.g. 'DH'. Written from the Greek text before tabulating manuscripts.
OV = {
 # John
 (43, 1, 42): {"υιος": "H"}, (43, 1, 45): {"υιος": "A"}, (43, 4, 5): {"υιος": "H"}, (43, 4, 46): {"υιος": "H"}, (43, 4, 47): {"υιος": "H"},
 (43, 4, 50): {"υιος": "H"}, (43, 4, 53): {"υιος": "H", "πατηρ": "H"}, (43, 6, 42): {"υιος": "A", "πατηρ": "H"}, (43, 9, 19): {"υιος": "H"},
 (43, 9, 20): {"υιος": "H"}, (43, 17, 12): {"υιος": "H"}, (43, 19, 26): {"υιος": "H"},
 (43, 4, 12): {"πατηρ": "H"}, (43, 4, 20): {"πατηρ": "H"}, (43, 8, 38): {"πατηρ": "DH"}, (43, 8, 39): {"πατηρ": "H"},
 (43, 8, 41): {"πατηρ": "HD"}, (43, 8, 44): {"πατηρ": "H"}, (43, 8, 53): {"πατηρ": "H"}, (43, 8, 56): {"πατηρ": "H"},
 (43, 12, 21): {"κυριος": "H"}, (43, 13, 16): {"κυριος": "H"}, (43, 15, 15): {"κυριος": "H"}, (43, 15, 20): {"κυριος": "H"},
 (43, 20, 15): {"κυριος": "DH"},
 (43, 3, 6): {"πνευμα": "DA"}, (43, 3, 8): {"πνευμα": "AD"}, (43, 4, 23): {"πνευμα": "A"}, (43, 4, 24): {"πνευμα": "DA"},
 (43, 6, 63): {"πνευμα": "DA"}, (43, 11, 33): {"πνευμα": "H"}, (43, 13, 21): {"πνευμα": "H"}, (43, 19, 30): {"πνευμα": "H"},
 (43, 19, 5): {"ανθρωπος": "D"}, (43, 10, 34): {"θεος": "H"}, (43, 10, 35): {"θεος": "HD"},
 # Paul (Romans - Hebrews, as in P46)
 (45, 1, 9): {"πνευμα": "H"}, (45, 8, 10): {"πνευμα": "A"}, (45, 8, 15): {"πνευμα": "HD"}, (45, 8, 16): {"πνευμα": "DH"},
 (45, 11, 8): {"πνευμα": "H"}, (45, 12, 11): {"πνευμα": "A"}, (46, 2, 11): {"πνευμα": "HD"}, (46, 2, 12): {"πνευμα": "HD"},
 (46, 4, 21): {"πνευμα": "H"}, (46, 5, 3): {"πνευμα": "H"}, (46, 5, 4): {"πνευμα": "H"}, (46, 5, 5): {"πνευμα": "H"},
 (46, 6, 17): {"πνευμα": "A"}, (46, 7, 34): {"πνευμα": "H"}, (46, 14, 14): {"πνευμα": "H"}, (46, 14, 15): {"πνευμα": "H"},
 (46, 14, 16): {"πνευμα": "H"}, (46, 16, 18): {"πνευμα": "H"}, (47, 2, 13): {"πνευμα": "H"}, (47, 4, 13): {"πνευμα": "A"},
 (47, 7, 1): {"πνευμα": "H"}, (47, 7, 13): {"πνευμα": "H"}, (47, 11, 4): {"πνευμα": "H"}, (47, 12, 18): {"πνευμα": "A"},
 (48, 6, 1): {"πνευμα": "H"}, (48, 6, 18): {"πνευμα": "H"}, (49, 2, 2): {"πνευμα": "H"}, (49, 4, 23): {"πνευμα": "H"},
 (50, 1, 27): {"πνευμα": "A"}, (51, 2, 5): {"πνευμα": "H"}, (52, 5, 23): {"πνευμα": "H"}, (58, 4, 12): {"πνευμα": "H"},
 (45, 4, 11): {"πατηρ": "H"}, (45, 4, 12): {"πατηρ": "H"}, (45, 4, 16): {"πατηρ": "H"}, (45, 4, 17): {"πατηρ": "H"},
 (45, 4, 18): {"πατηρ": "H"}, (45, 9, 10): {"πατηρ": "H"}, (46, 5, 1): {"πατηρ": "H"}, (49, 5, 31): {"πατηρ": "H"},
 (49, 6, 2): {"πατηρ": "H"}, (50, 2, 22): {"πατηρ": "H"}, (52, 2, 11): {"πατηρ": "H"}, (58, 7, 10): {"πατηρ": "H"},
 (58, 12, 7): {"πατηρ": "H"}, (58, 12, 9): {"πατηρ": "HD"}, (58, 1, 5): {"πατηρ": "D"},
 (48, 4, 1): {"κυριος": "H"}, (49, 6, 9): {"κυριος": "HD"}, (51, 3, 22): {"κυριος": "HD"}, (51, 4, 1): {"κυριος": "HD"},
 (45, 14, 4): {"κυριος": "A"}, (49, 6, 5): {"κυριος": "HD"},
 (47, 4, 4): {"θεος": "HD"}, (50, 3, 19): {"θεος": "H"}, (46, 8, 4): {"θεος": "D"}, (46, 8, 5): {"θεος": "H"}, (48, 4, 8): {"θεος": "DH"},
 (45, 5, 15): {"ανθρωπος": "HD"}, (46, 15, 21): {"ανθρωπος": "HD"}, (46, 15, 47): {"ανθρωπος": "HD"}, (45, 5, 12): {"ανθρωπος": "H"},
 (45, 5, 19): {"ανθρωπος": "A"}, (50, 2, 7): {"ανθρωπος": "A"}, (50, 2, 8): {"ανθρωπος": "A"}, (58, 2, 6): {"ανθρωπος": "A", "υιος": "A"},
 (45, 9, 9): {"υιος": "H"}, (48, 4, 7): {"υιος": "H"}, (48, 4, 30): {"υιος": "H"}, (58, 11, 24): {"υιος": "H"}, (58, 12, 5): {"υιος": "H"},
 (58, 12, 6): {"υιος": "H"}, (58, 12, 7): {"υιος": "H"}, (58, 11, 21): {"υιος": "H"},
}

def label_verse(ref):
    """Return list of (group, label) for SBLGNT tokens of a verse, labels for contrast groups."""
    toks = SB.get(ref, []); out = []; k = collections.Counter()
    for i, t in enumerate(toks):
        g = t["group"]
        if not g: continue
        lab = "-"
        if g in CONTRAST:
            plural = len(t["parse"]) > 5 and t["parse"][5] == "P"
            lab = "H" if plural else "D"
            if g == "ανθρωπος":   # Son of Man / Jesus = D, otherwise H
                prev = [x["lem"] for x in toks[max(0, i - 3):i]]
                lab = "D" if ("υιοσ" in prev and t["parse"][4] == "G") else "H"
            if g == "πατηρ" and not plural and any(x["lem"] in ("αβρααμ", "ιακωβ", "διαβολοσ") for x in toks):
                lab = "H"
            ov = OV.get(ref, {}).get(g)
            if ov:
                lab = ov if len(ov) == 1 else (ov[k[g]] if k[g] < len(ov) else "A")
        k[g] += 1
        out.append((g, lab, i, "P" if (len(t["parse"]) > 5 and t["parse"][5] == "P") else "S"))
    return out

# ---------------------------------------------------------------- CNTR parsing
LET = set("αβγδεζηθικλμνξοπρστυφχψωϛϟ⳨ϗ\ue001͵\ufffd")
def parse_word(s):
    """Parse one MES word -> dict(glyphs=[(ch, missing, damaged)], brk=[(pos,type)], ns, sup, vid, rem)."""
    d = dict(glyphs=[], brk=[], ns="=" in s, sup="~" in s, vid="+" in s[:3], rem=("&" in s or "*" in s), num="$" in s, raw=s, macron=0)
    for ch in s:
        if ch in "\\|/": d["brk"].append((len(d["glyphs"]), ch))
        elif ch in LET: d["glyphs"].append([ch, False, False])
        elif ch == "¯":
            d["macron"] += 1
            if d["glyphs"]: d["glyphs"][-1].append("¯")
        elif ch == "^" and d["glyphs"]: d["glyphs"][-1][1] = True
        elif ch == "%" and d["glyphs"]: d["glyphs"][-1][2] = True
    d["missing"] = sum(g[1] for g in d["glyphs"]); d["n"] = len(d["glyphs"])
    d["stauro"] = any(g[0] == "⳨" for g in d["glyphs"])
    txt = "".join(g[0] + ("ν" if "¯" in g[3:] and False else "") for g in d["glyphs"])
    d["letters"] = txt
    plain = txt.replace("ϗ", "και").replace("⳨", "τρ").replace("\ue001", "μου").replace("ϛ", "στ")
    plain = re.sub(r"[^α-ω]", "", plain)
    if d["macron"] and not d["ns"]: plain += "ν"          # suspended final nu
    d["plain"] = plain
    return d

TOKRE = re.compile(r"([xabc]?)\{([^}]*)\}|(\S+)")
def parse_verse(text):
    """-> readings dict (orig/first/final: list of words) and correction events [(orig_words, corr_words, hand)]."""
    items = []
    for m in TOKRE.finditer(text):
        if m.group(3) is not None: items.append(("w", m.group(3)))
        else: items.append(("e", m.group(1), m.group(2).split()))
    first, orig, final, events = [], [], [], []
    i = 0
    while i < len(items):
        it = items[i]
        if it[0] == "w":
            first.append(it[1]); orig.append(it[1]); final.append(it[1]); i += 1; continue
        # a correction group
        grp = []
        while i < len(items) and items[i][0] == "e":
            if grp and items[i][1] == "x": break
            if grp and items[i][1] == "" and grp[-1][0] != "x": break
            grp.append((items[i][1], items[i][2])); i += 1
        x = [g for g in grp if g[0] == "x"]; base = [g for g in grp if g[0] == ""]; corr = [g for g in grp if g[0] in "abc"]
        fw = base[0][1] if base else (x[0][1] if x else [])
        ow = x[0][1] if x else fw
        first += fw; orig += ow
        final += corr[-1][1] if corr else fw
        # one event per correction group: original (x, or the unlabeled text when no x) -> corrected text;
        # in the CNTR files a corrector edit (a/b/c) repeats the corrected text and names the hand
        fin = corr[-1][1] if corr else fw
        hand = "".join(h for h, _ in corr) or "x"
        if x: events.append((ow, fin if corr else fw, hand))
        elif corr: events.append((fw, fin, hand))
    return dict(first=first, orig=orig, final=final), events

def load_ms(ms):
    V = collections.OrderedDict()
    for line in open(os.path.join(CN, ms + ".txt"), encoding="utf-8"):
        m = re.match(r"^(\d\d)(\d{3})(\d{3}) ?(.*)$", line.rstrip("\n"))
        if not m: continue
        ref = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        rd, ev = parse_verse(m.group(4))
        V[ref] = dict(words=[parse_word(w) for w in rd["first"]], events=ev, raw=m.group(4))
    return V

MSS = ["P66", "P75", "01", "02", "03", "P46", "P45"]
DATA = {ms: load_ms(ms) for ms in MSS}

def decode_ns(s):
    if s.startswith(("πνικ", "πνκ")): return None
    if s.startswith("πν"): return "πνευμα"
    if s.startswith("θ"): return "θεος"
    if s.startswith("κ"): return "κυριος"
    if s.startswith("ι"):
        if s in ("ιλημ", "ιηλμ") or s.startswith("ιλ"): return "ιερουσαλημ"
        if s.endswith("λ"): return "ισραηλ"
        return "ιησους"
    if s.startswith("χ"): return "χριστος"
    if s.startswith("π"): return "πατηρ"
    if s.startswith("υ"): return "υιος"
    if s.startswith(("αν", "αυ")): return "ανθρωπος"
    if s in ("σωρ", "σηρ", "σρσ"): return "σωτηρ"
    if "στρ" in s or s.startswith("σρ") or s.startswith("εστ") or "σταυρ" in s: return "σταυρ"
    if s.startswith("ου"): return "ουρανος"
    if s.startswith("δ"): return "δαυιδ"
    if s.startswith("μ"): return "μητηρ"
    return None

def ms_group(w):
    if w["ns"]: return decode_ns(w["plain"])
    g = FORM2GROUP.get(canon(w["plain"]))
    if g: return g
    if "σταυρ" in w["plain"]: return "σταυρ"
    return None

def usable(w): return not w["sup"] and w["missing"] == 0 and not w["rem"] and w["n"] > 0

def bh(ps):
    ps = np.asarray(ps, float); n = len(ps); o = np.argsort(ps); q = np.empty(n); prev = 1.0
    for r in range(n - 1, -1, -1):
        i = o[r]; prev = min(prev, ps[i] * n / (r + 1)); q[i] = prev
    return q

_LG = [0.0]
def _lf(n):
    while len(_LG) <= n: _LG.append(_LG[-1] + math.log(len(_LG)))
    return _LG[n]
def fisher2(a, b, c, d):
    """Exact two-sided Fisher p for [[a,b],[c,d]] (a = D contracted, b = D full, c = H contracted, d = H full)."""
    r1, r2, c1 = a + b, c + d, a + c; n = r1 + r2; c2 = n - c1
    base = _lf(r1) + _lf(r2) + _lf(c1) + _lf(c2) - _lf(n)
    def lp(x): return base - _lf(x) - _lf(r1 - x) - _lf(c1 - x) - _lf(r2 - c1 + x)
    lo, hi = max(0, c1 - r2), min(r1, c1); l0 = lp(a)
    return min(1.0, sum(math.exp(lp(x)) for x in range(lo, hi + 1) if lp(x) <= l0 + 1e-9))

ALLP = []   # (test id, p) for the round-wide BH
def addp(tid, p): ALLP.append((tid, float(p)))

# ================================================================= T1 nomina sacra
t1 = {"rates": {}, "contrast": [], "unmapped_ns": {}, "align": {}}
OCC = []   # (ms, corpus, group, label, contracted, ref)
for ms in MSS:
    unm = collections.Counter(); al = collections.Counter()
    for ref, v in DATA[ms].items():
        if ref not in SB: continue
        ms_by = collections.defaultdict(list)
        for w in v["words"]:
            g = ms_group(w)
            if w["ns"] and g is None: unm[w["plain"]] += 1
            if g: ms_by[g].append(w)
        sb_by = collections.defaultdict(list)
        for g, lab, i, num in label_verse(ref): sb_by[g].append((lab, num))
        corp = "John" if ref[0] == 43 else ("Paul" if ref[0] in PAUL else "other")
        for g, ws in ms_by.items():
            labs = sb_by.get(g, [])
            if len(labs) == len(ws): pairs = list(zip(ws, labs)); al["paired"] += len(ws)
            elif labs and len(set(labs)) == 1: pairs = [(w, labs[0]) for w in ws]; al["uniform"] += len(ws)
            else: al["dropped"] += len(ws); continue
            for w, lab in pairs:
                if usable(w): OCC.append((ms, corp, g, lab[0], bool(w["ns"]), ref, w["letters"], lab[1]))
    t1["unmapped_ns"][ms] = dict(unm.most_common(10)); t1["align"][ms] = dict(al)

for ms in MSS:
    for corp in ("John", "Paul", "all"):
        rows = {}
        for g in GROUPS:
            xs = [o for o in OCC if o[0] == ms and o[2] == g and (corp == "all" or o[1] == corp)]
            if xs: rows[g] = dict(n=len(xs), contracted=sum(o[4] for o in xs), rate=round(sum(o[4] for o in xs) / len(xs), 3))
        if rows: t1["rates"][f"{ms}|{corp}"] = rows

def contrast_cell(xs):
    D = [o[4] for o in xs if o[3] == "D"]; H = [o[4] for o in xs if o[3] == "H"]
    return D, H
for ms in MSS:
    for corp in ("John", "Paul"):
        for g in CONTRAST:
            xs = [o for o in OCC if o[0] == ms and o[1] == corp and o[2] == g]
            D, H = contrast_cell(xs)
            if len(D) < 3 or len(H) < 3: continue
            a, b, c, d = sum(D), len(D) - sum(D), sum(H), len(H) - sum(H)
            if a + c in (0, len(D) + len(H)): continue   # no variation -> untestable
            p = fisher2(a, b, c, d)
            tid = f"T1|{ms}|{corp}|{g}"; addp(tid, p)
            t1["contrast"].append(dict(test=tid, D_n=len(D), D_contr=a, D_rate=round(a / len(D), 3), H_n=len(H), H_contr=c,
                                       H_rate=round(c / len(H), 3), p=p,
                                       H_examples=[f"{o[5][0]} {o[5][1]}:{o[5][2]} {'=' if o[4] else ''}{o[6]}" for o in xs if o[3] == "H"][:12]))
# singular-only family: removes the grammatical-number confound (plural gods/masters/fathers/sons)
t1["contrast_singular"] = []
for ms in MSS:
    for corp in ("John", "Paul"):
        for g in CONTRAST:
            xs = [o for o in OCC if o[0] == ms and o[1] == corp and o[2] == g and o[7] == "S"]
            D, H = contrast_cell(xs)
            if len(D) < 3 or len(H) < 3: continue
            a, b, c, d = sum(D), len(D) - sum(D), sum(H), len(H) - sum(H)
            if a + c in (0, len(D) + len(H)): continue
            p = fisher2(a, b, c, d); tid = f"T1sg|{ms}|{corp}|{g}"; addp(tid, p)
            t1["contrast_singular"].append(dict(test=tid, D=f"{a}/{len(D)}", H=f"{c}/{len(H)}", p=p,
                H_examples=[f"{o[5][0]} {o[5][1]}:{o[5][2]} {'=' if o[4] else ''}{o[6]}" for o in xs if o[3] == "H"][:12]))
# also untestable but informative: both labels present
t1["descriptive_DH"] = {}
for ms in MSS:
    for corp in ("John", "Paul"):
        for g in CONTRAST:
            D, H = contrast_cell([o for o in OCC if o[0] == ms and o[1] == corp and o[2] == g])
            if D or H: t1["descriptive_DH"][f"{ms}|{corp}|{g}"] = dict(D=f"{sum(D)}/{len(D)}", H=f"{sum(H)}/{len(H)}")
# controls
rng = np.random.default_rng(RNG_SEED)
cells = [c for c in t1["contrast"]]
pc, nc = [], []
for c in cells:
    for _ in range(200):
        D = rng.random(c["D_n"]) < 0.9; H = rng.random(c["H_n"]) < 0.3
        a, b, cc, d = int(D.sum()), c["D_n"] - int(D.sum()), int(H.sum()), c["H_n"] - int(H.sum())
        pc.append(fisher2(a, b, cc, d) < 0.05 if 0 < a + cc < c["D_n"] + c["H_n"] else False)
        # negative: shuffle real contraction flags among the cell's tokens
        flags = np.array([1] * (c["D_contr"] + c["H_contr"]) + [0] * (c["D_n"] + c["H_n"] - c["D_contr"] - c["H_contr"]))
        rng.shuffle(flags); a = int(flags[:c["D_n"]].sum()); cc = int(flags[c["D_n"]:].sum())
        nc.append(fisher2(a, c["D_n"] - a, cc, c["H_n"] - cc) < 0.05)
t1["positive_control_power"] = round(float(np.mean(pc)), 3) if pc else None
t1["negative_control_fpr"] = round(float(np.mean(nc)), 3) if nc else None
# hand-check sample of labels
smp_pool = [o for o in OCC if o[2] in CONTRAST and o[3] in "DH" and o[1] in ("John", "Paul")]
idx = np.random.default_rng(7).choice(len(smp_pool), size=min(40, len(smp_pool)), replace=False)
t1["handcheck_sample"] = []
for i in sorted(idx):
    o = smp_pool[i]; ref = o[5]
    t1["handcheck_sample"].append(f"{o[0]} {ref[0]} {ref[1]}:{ref[2]} {o[2]} label={o[3]} | " + " ".join(t["word"] for t in SB[ref]))
R["T1_nomina_sacra"] = t1

# ================================================================= T2 staurogram and special signs
t2 = {"staurograms": [], "stauros_tokens": {}, "line_end": {}}
for ms in MSS:
    sw = collections.Counter()
    for ref, v in DATA[ms].items():
        for w in v["words"]:
            g = ms_group(w)
            if w["stauro"]:
                t2["staurograms"].append(dict(ms=ms, ref=f"{ref[0]} {ref[1]}:{ref[2]}", form=w["raw"], group=g, supplied=w["sup"]))
            if g == "σταυρ" and not w["sup"]:
                sw["stauro" if w["stauro"] else ("ns_no_stauro" if w["ns"] else "plain")] += 1
    if sw: t2["stauros_tokens"][ms] = dict(sw)
t2["n_staurograms"] = len(t2["staurograms"])
t2["staurogram_off_stauros"] = [s for s in t2["staurograms"] if s["group"] != "σταυρ"]
# line-end control: macron (nu suspension) and kai compendium sit at line ends?
for ms in MSS:
    seq = [w for v in DATA[ms].values() for w in v["words"]]
    nu_end = collections.Counter(); kai = collections.Counter()
    for i, w in enumerate(seq[:-1]):
        nxt = seq[i + 1]
        lineend = any(p == 0 for p, _ in nxt["brk"])
        if not usable(w) or w["ns"] or not w["glyphs"]: continue
        endsnu = w["glyphs"][-1][0] == "ν" or w["macron"] > 0
        if endsnu: nu_end[(lineend, w["macron"] > 0)] += 1
        if w["letters"] in ("ϗ", "και"): kai[(lineend, w["letters"] == "ϗ")] += 1
    def cell(c):
        a, b, cc, d = c[(True, True)], c[(True, False)], c[(False, True)], c[(False, False)]
        if a + b == 0 or cc + d == 0 or a + cc == 0: return None
        return dict(at_line_end=f"{a}/{a+b}", elsewhere=f"{cc}/{cc+d}", rate_end=round(a / (a + b), 3),
                    rate_else=round(cc / (cc + d), 4), p=fisher2(a, b, cc, d))
    t2["line_end"][ms] = dict(nu_suspension=cell(nu_end), kai_compendium=cell(kai))
R["T2_special_signs"] = t2

# ================================================================= T3 corrections map (John)
jrefs = [r for r in SB if r[0] == 43]
JIDX = {r: i for i, r in enumerate(jrefs)}
def loaded_sets():
    L = {"prologue": set(), "I_am": set(), "titles": set(), "passion": set()}
    for r in jrefs:
        t = SB[r]; lem = [x["lem"] for x in t]
        if r[1] == 1 and r[2] <= 18: L["prologue"].add(r)
        if r[1] in (18, 19): L["passion"].add(r)
        for i in range(len(t) - 1):
            if t[i]["lem"] == "εγω" and t[i + 1]["lem"] == "ειμι" and t[i + 1]["parse"][:3] == "1PA": L["I_am"].add(r)
            if t[i]["lem"] == "ειμι" and t[i]["parse"][:3] == "1PA" and t[i + 1]["lem"] == "εγω": L["I_am"].add(r)
        if set(lem) & {"χριστοσ", "μεσσιασ", "μονογενησ", "σωτηρ", "αμνοσ"}: L["titles"].add(r)
        for i, x in enumerate(t):
            if x["lem"] == "υιοσ" and any(y["lem"] in ("θεοσ", "ανθρωποσ") and y["parse"][4] == "G" for y in t[i + 1:i + 4]): L["titles"].add(r)
    return L
LOADED = loaded_sets()
LOADED["ALL"] = set().union(*LOADED.values())
t3 = {"loaded_sizes": {k: len(v) for k, v in LOADED.items()}, "I_am_verses": sorted(f"{r[1]}:{r[2]}" for r in LOADED["I_am"]), "ms": {}}

def seen_letters(v): return sum(1 for w in v["words"] if not w["sup"] for g in w["glyphs"] if not g[1])
def shift_test(counts, letters, mask, mult=True):
    counts, letters, mask = map(np.asarray, (counts, letters, mask))
    def stat(m):
        a = counts[m].sum() / max(letters[m].sum(), 1); b = counts[~m].sum() / max(letters[~m].sum(), 1)
        return a / b if b > 0 else np.inf
    obs = stat(mask); n = len(mask)
    sh = np.array([stat(np.roll(mask, k)) for k in range(1, n)])
    p_shift = (np.sum(sh >= obs) + 1) / n
    if not mult: return float(obs), float(p_shift), None
    rng = np.random.default_rng(RNG_SEED); tot = int(counts.sum()); w = letters / letters.sum()
    sims = rng.multinomial(tot, w, size=20000)
    mn = (sims[:, mask].sum(1) / letters[mask].sum()) / np.maximum(sims[:, ~mask].sum(1) / letters[~mask].sum(), 1e-12)
    p_mult = (np.sum(mn >= obs) + 1) / (len(mn) + 1)
    return float(obs), float(p_shift), float(p_mult)

import importlib
for name in ("scipy", "scipy.signal", "scipy.io", "scipy.io.wavfile"):
    sys.modules.setdefault(name, types.ModuleType(name))
for attr in ("lfilter", "butter", "fftconvolve"): setattr(sys.modules["scipy.signal"], attr, None)
sys.modules["scipy.io"].wavfile = sys.modules["scipy.io.wavfile"]
sys.path.insert(0, ENG); import engine as E
_kc = {}
def skey(s, era):
    if (s, era) not in _kc:
        try: _kc[(s, era)] = "".join(p for sy in E.parse_greek(s, era) for x in sy for p in x["ph"]).replace("ː", "").replace(" ", "")
        except Exception: _kc[(s, era)] = s
    return _kc[(s, era)]
NSX = {"θσ": "θεοσ", "θυ": "θεου", "θν": "θεον", "θω": "θεω", "ισ": "ιησουσ", "ιυ": "ιησου", "ιν": "ιησουν", "κσ": "κυριοσ", "κυ": "κυριου",
       "κν": "κυριον", "κε": "κυριε", "χσ": "χριστοσ", "χυ": "χριστου", "χν": "χριστον", "πηρ": "πατηρ", "πρσ": "πατροσ", "πρα": "πατερα",
       "πρι": "πατρι", "περ": "πατερ", "υσ": "υιοσ", "υν": "υιον", "υυ": "υιου", "πνα": "πνευμα", "πνσ": "πνευματοσ", "πνι": "πνευματι",
       "ανοσ": "ανθρωποσ", "ανον": "ανθρωπον", "ανου": "ανθρωπου", "ανοι": "ανθρωποι", "ανων": "ανθρωπων"}
def ev_text(ws):
    out = []
    for s in ws:
        w = parse_word(s); out.append(NSX.get(w["plain"], w["plain"]) if w["ns"] else w["plain"])
    return "".join(out)
def ev_missing(ws): return any("^" in s or "~" in s for s in ws)

c11 = {"P66": 0.60, "P75": 0.35, "01": 0.53, "03": 0.53}
for ms in ("P66", "01", "P75", "03", "02"):
    seq = [r for r in jrefs if r in DATA[ms]]
    letters = [seen_letters(DATA[ms][r]) for r in seq]
    keep = [i for i, n in enumerate(letters) if n > 0]
    seq = [seq[i] for i in keep]; letters = [letters[i] for i in keep]
    res = {"verses": len(seq), "letters": int(sum(letters))}
    for hand in ("x", "all"):
        cnt = [sum(1 for e in DATA[ms][r]["events"] if hand == "all" or e[2] == "x") for r in seq]   # x = first hand only
        res[f"corrections_{hand}"] = int(sum(cnt))
        for comp in ("ALL", "prologue", "I_am", "titles", "passion"):
            mask = [r in LOADED[comp] for r in seq]
            if sum(mask) < 3 or sum(cnt) < 5: continue
            obs, ps, pm = shift_test(cnt, letters, mask)
            nL = sum(c for c, m in zip(cnt, mask) if m)
            res[f"{hand}|{comp}"] = dict(rate_ratio=round(obs, 3), loaded_corr=nL, loaded_verses=sum(mask), p_shift=round(ps, 4), p_multinomial=round(pm, 4))
            if hand == ("x" if ms == "P66" else "all"): addp(f"T3|{ms}|{comp}", ps)
        if hand == ("x" if ms == "P66" else "all") and ms in ("P66", "01"):
            mask = np.array([r in LOADED["ALL"] for r in seq]); L = np.array(letters); hits = []
            r2 = np.random.default_rng(RNG_SEED + 1); tot = int(sum(cnt))
            for _ in range(200):
                w = L * np.where(mask, 2.0, 1.0); sim = r2.multinomial(tot, w / w.sum())
                hits.append(shift_test(sim, L, mask, mult=False)[1] < 0.05)
            res["positive_control_power_2x"] = round(float(np.mean(hits)), 3)
    # sound of corrections
    sc = collections.Counter(); exs = []
    for r in seq:
        for o, c, h in DATA[ms][r]["events"]:
            if ev_missing(o) or ev_missing(c): sc["lacunose"] += 1; continue
            a, b = ev_text(o), ev_text(c)
            if not a or not b: sc["add/omit"] += 1; continue
            if a == b: sc["layout only"] += 1; continue
            if len(o) == len(c):     # word-for-word substitution: compare each changed word pair by sound
                wa = [ev_text([x]) for x in o]; wb = [ev_text([x]) for x in c]
                diff = [(x, y) for x, y in zip(wa, wb) if x != y]
                if not diff: sc["layout only"] += 1; continue
                same_k = all(skey(x, "koine-late") == skey(y, "koine-late") for x, y in diff)
                same_a = all(skey(x, "attic") == skey(y, "attic") for x, y in diff)
                sc["subst"] += 1; sc["same_koine"] += same_k; sc["same_attic"] += same_a
                if same_k and len(exs) < 10: exs.append(f"{r[1]}:{r[2]} {a}->{b}")
            else: sc["other (word count changes)"] += 1
    res["sound"] = dict(sc); res["sound"]["share_same_koine"] = round(sc["same_koine"] / max(sc["subst"], 1), 3)
    res["sound"]["share_same_attic"] = round(sc["same_attic"] / max(sc["subst"], 1), 3); res["sound"]["examples"] = exs
    res["sound"]["C11_variant_share"] = c11.get(ms)
    # direction: does the correction move toward the SBLGNT wording?
    tow = collections.Counter()
    for r in seq:
        sbt = "".join(t["w"] for t in SB[r])
        for o, c, h in DATA[ms][r]["events"]:
            if ev_missing(o) or ev_missing(c): continue
            a, b = ev_text(o), ev_text(c)
            if a == b: continue
            ia, ib = (a in sbt) if a else None, (b in sbt) if b else None
            tow["to_SBL" if (ib and not ia) or (not b and a and not ia) else ("away" if (ia and not ib) else "neutral")] += 1
    res["direction"] = dict(tow)
    t3["ms"][ms] = res
# itacism: one-sided binomial-type comparison with C11 is descriptive (different populations)
R["T3_corrections"] = t3

# ================================================================= T4 scribal breaks
def sbl_paragraphs(book):
    fn = os.path.join(SXML, XMLNAME[book] + ".xml"); starts = set(); cur = None; pend = False; seen_word = False
    for line in open(fn, encoding="utf-8-sig"):
        line = line.strip()
        if line.startswith("<p>"): pend = True; seen_word = False; continue
        m = re.match(r'<verse-number id="[^"]* (\d+):(\d+)">', line)
        if m:
            cur = (book, int(m.group(1)), int(m.group(2)))
            if pend: starts.add(cur); pend = False
            continue
        if line.startswith("<w>") and pend and cur:
            starts.add(cur); pend = False      # paragraph begins inside a verse: count that verse
    return starts

def lines_of(ms, books):
    """Return list of lines: dict(n, missing, ok, end_mid, next_ref, next_is_vstart, last_lastmiss)."""
    seq = []
    prev = None
    for ref, v in DATA[ms].items():
        if ref[0] not in books: continue
        gap = prev is not None and (ref[0] != prev[0] or (ref in JIDX and prev in JIDX and JIDX[ref] - JIDX[prev] != 1))
        for j, w in enumerate(v["words"]): seq.append((ref, j, w, gap and j == 0))
        prev = ref
    lines, cur = [], dict(n=0, missing=0, bad=False, glyph_miss=[])
    def close(nref, mid, vstart):
        cur.update(next_ref=nref, end_mid=mid, next_vstart=vstart); lines.append(cur)
    for ref, j, w, gap in seq:
        if gap: cur["bad"] = True
        if w["sup"] or w["rem"]: cur["bad"] = True
        pos = 0
        for (bp, bt) in w["brk"]:
            for g in w["glyphs"][pos:bp]:
                cur["n"] += 1; cur["missing"] += g[1]; cur["glyph_miss"].append(g[1])
            pos = bp
            close(ref, bp > 0, bp == 0 and j == 0)
            cur = dict(n=0, missing=0, bad=w["sup"] or w["rem"], glyph_miss=[])
        for g in w["glyphs"][pos:]:
            cur["n"] += 1; cur["missing"] += g[1]; cur["glyph_miss"].append(g[1])
    for L in lines:
        L["ok"] = (not L["bad"]) and L["n"] > 0 and L["missing"] <= 0.2 * L["n"] and not any(L["glyph_miss"][-3:])
        del L["glyph_miss"]
    return lines

def short_breaks(ms, books):
    lines = lines_of(ms, books); n = len(lines)
    lens = np.array([L["n"] if L["ok"] else -1 for L in lines])
    out_start, out_any, observable = set(), set(), set()
    nshort = 0
    for i, L in enumerate(lines[1:-1], start=1):
        if not L["ok"]: continue
        win = [lens[k] for k in range(max(0, i - 20), min(n, i + 21)) if k != i and lens[k] > 0]
        if len(win) < 8: continue
        med = float(np.median(win))
        if L["next_vstart"]: observable.add(L["next_ref"])
        if L["n"] < 0.6 * med and not L["end_mid"] and med >= 8:
            nshort += 1; out_any.add(L["next_ref"])
            if L["next_vstart"]: out_start.add(L["next_ref"])
    # verse starts that fall mid-line in an ok line are observable (no break there)
    for ms_ref, v in DATA[ms].items():
        pass
    return out_start, out_any, observable, nshort, len(lines)

def observable_vstarts(ms, books):
    """verse starts whose surrounding line is complete (either broken there, or mid-line)."""
    lines = lines_of(ms, books)
    obs = set()
    # walk words again to know which line each verse start falls on
    li = 0; seqlines = []
    for ref, v in DATA[ms].items():
        if ref[0] not in books: continue
        for j, w in enumerate(v["words"]):
            if j == 0 and not any(p == 0 for p, _ in w["brk"]) and not w["sup"]:
                seqlines.append((ref, li))
            li += sum(1 for _ in w["brk"])
    for ref, k in seqlines:
        if 0 <= k < len(lines) and lines[k]["ok"]: obs.add(ref)
    return obs

t4 = {"ms": {}}
CUTS = [(43, 1, 16), (43, 13, 33), (43, 18, 1)]
OUTLINE = [(43, 1, 19), (43, 13, 1), (43, 13, 31), (43, 18, 1), (43, 20, 1), (43, 21, 1)]
SBLP = {b: sbl_paragraphs(b) for b in set(JOHN + PAUL)}
VIDX = {}
for b in set(JOHN + PAUL):
    for i, r in enumerate([r for r in SB if r[0] == b]): VIDX[r] = i
for ms, books in (("P66", JOHN), ("P75", JOHN), ("01", JOHN), ("02", JOHN), ("03", JOHN), ("P46", PAUL), ("01", PAUL), ("03", PAUL)):
    key = f"{ms}|{'John' if books == JOHN else 'Paul'}"
    s_start, s_any, obs_b, nshort, nlines = short_breaks(ms, books)
    obs = {r for r in (obs_b | observable_vstarts(ms, books)) if r in VIDX}
    s_start = {r for r in s_start if r in VIDX}; s_any = {r for r in s_any if r in VIDX}
    para = set().union(*[SBLP[b] for b in books])
    P = [r for r in obs if r in para]; Q = [r for r in obs if r not in para]
    a = sum(r in s_start for r in P); c = sum(r in s_start for r in Q)
    res = dict(lines=nlines, short_lines=nshort, observable_vstarts=len(obs), sbl_para_starts_observable=len(P),
               short_at_para=f"{a}/{len(P)}", short_at_other=f"{c}/{len(Q)}")
    if P and Q and a + c > 0:
        rp, rq = a / len(P), c / len(Q); res["enrichment"] = round(rp / rq, 2) if rq > 0 else None
        # permutation p (labels shuffled among observable verse starts)
        rng = np.random.default_rng(RNG_SEED); flags = np.array([r in s_start for r in P + Q]); nP = len(P)
        sims = np.array([rng.permutation(flags)[:nP].sum() for _ in range(20000)])
        res["p_perm"] = float((np.sum(sims >= a) + 1) / 20001); addp(f"T4pc|{key}", res["p_perm"])
        # how many scribal short-line breaks (at verse starts) are SBLGNT paragraph starts
        res["scribal_breaks_that_are_SBL_para"] = f"{sum(r in para for r in s_start)}/{len(s_start)}"
    if books == JOHN:
        B = sorted(s_any, key=lambda r: VIDX[r]); bi = np.array([VIDX[r] for r in B])
        lo = min(VIDX[r] for r in obs) if obs else 0; hi = max(VIDX[r] for r in obs) if obs else 0
        cuts = [c for c in CUTS if lo <= VIDX[c] <= hi]
        res["breaks_listed"] = [f"{r[1]}:{r[2]}" for r in B]
        res["near_cuts"] = {f"{c[1]}:{c[2]}": [f"{r[1]}:{r[2]}" for r in B if abs(VIDX[r] - VIDX[c]) <= 5] for c in cuts}
        if cuts and len(bi):
            def md(ix): return float(np.mean([np.min(np.abs(bi - x)) for x in ix]))
            obsd = md([VIDX[c] for c in cuts]); res["cuts_tested"] = [f"{c[1]}:{c[2]}" for c in cuts]; res["mean_dist"] = obsd
            pool = np.array(sorted(VIDX[r] for r in obs)); rng = np.random.default_rng(RNG_SEED)
            sims = np.array([md(rng.choice(pool, len(cuts), replace=False)) for _ in range(20000)])
            res["p_random_vstart"] = float((np.sum(sims <= obsd) + 1) / 20001)
            ppool = np.array(sorted(VIDX[r] for r in para if r in VIDX and lo <= VIDX[r] <= hi))
            sims2 = np.array([md(rng.choice(ppool, len(cuts), replace=False)) for _ in range(20000)])
            res["p_random_SBLpara"] = float((np.sum(sims2 <= obsd) + 1) / 20001)
            addp(f"T4|{key}|vs_random", res["p_random_vstart"]); addp(f"T4|{key}|vs_SBLpara", res["p_random_SBLpara"])
            res["outline_dist"] = md([VIDX[c] for c in OUTLINE if lo <= VIDX[c] <= hi])
    t4["ms"][key] = res
R["T4_breaks"] = t4

# ================================================================= BH
ids = [t for t, _ in ALLP]; ps = [p for _, p in ALLP]; qs = bh(ps)
R["BH"] = {"n_tests": len(ps), "tests": [dict(test=t, p=round(p, 5), q=round(float(q), 5)) for t, p, q in zip(ids, ps, qs)]}
json.dump(R, open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"{len(ps)} tests; significant at q<=0.05: {[t for t, q in zip(ids, qs) if q <= 0.05]}")
