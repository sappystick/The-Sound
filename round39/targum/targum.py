#!/usr/bin/env python3
"""Round 39 lens: the Aramaic Targums as the hidden layer behind John's "Word".

Sources (new to the project): Targum Onkelos, Targum Neofiti (Codex Neofiti 1), Targum Pseudo-Jonathan,
Fragment Targum (Targum Jerusalem), Targum Jonathan on the Prophets, Targums of the Writings, all via the
Sefaria API (see fetch.sh).  Compared with the Hebrew (WLC, morphhb), the Swete LXX and the SBLGNT.

Hypotheses, measures and decision rules, fixed before running:

T1  MAP.  Per Targum and book, the rate of verses carrying a mediating term
       MEMRA   (מימרא / ממרא, any suffix; the infinitive למימר "saying" excluded)
       SHEKINAH (שכינתא, any suffix)
       YEQARA  (יקרא "glory") only when bound to God (followed by דיי / שכינת-, or suffixed in a verse whose Hebrew
               names God) AND the Hebrew verse lacks כבוד (Strong 3519)  -> an insertion, not a translation of kavod
       ANA HU  (אנא הוא "I am he") where the Hebrew lacks אני/אנכי הוא
     reported per 1000 verses and as the share of Hebrew divine-name verses (YHWH, Elohim, El, Eloah, Yah,
     Shaddai, Adonai) that receive a mediating term.  Descriptive; one inferential check: is a term more likely
     in divine-name verses than in other verses (2x2, permutation of the divine-name labels within book).
     Positive control: the method must recover the well-known Memra verses Gen 3:8 (PsJ/Neofiti), Gen 28:20-21
     (Onkelos), Exod 19:17 (Onkelos) and the "I am he" of Deut 32:39 and Isa 43:10.

T2  POINTERS.  Statistic = mean number of mediating-term tokens per pointed verse (primary Targum per book:
     Onkelos for the Torah, Jonathan for the Prophets, the Writings Targum otherwise; Neofiti as a second
     Torah layer).  Null = for every pointed verse draw a random verse of the same book (10,000 draws, seed 39);
     a second null also matches the Targum verse length (same book, length within +-25%).
     Sets: John formal quotations (12 + 6 others), John quotations + major allusions, Matthew quotations, Luke
     quotations, and the rare-word pointers of nt_pointers.csv for Jn/Mt/Lk.  Decision: John is "Targum-rich"
     only if its set beats the null at BH q < 0.05 AND Matthew and Luke do not.
     Positive control: verses where the Hebrew has YHWH as the subject of "I am YHWH" (אני יהוה) - the
     classic Memra contexts - must show enrichment; a planted-power check (half of a John-size set replaced
     by term-bearing verses) gives the power.

T3  PROLOGUE.  John 1:1-18 concept order C = beginning, word, God, life, light, darkness, world, dwelt, glory,
     grace/truth, Moses/law, seen-God.  For a text: map tokens to concepts with a fixed lexicon per language,
     take the order of first occurrence, score = LCS(first-occurrence order, C) (0-12).  Targets: Gen 1 + Exod
     33-34 in Neofiti, Onkelos, LXX.  Null: random (chapter, chapter) pairs from the same corpus (Pentateuch),
     total length within +-25% of the target (10,000 draws).  Report percentile and p for each; the Targum
     hypothesis needs Neofiti p < 0.05 and Neofiti's z > LXX's z.  Positive control: the Genesis overlay
     subsequence (beginning, God, light, darkness) must put Gen 1 in the top 5% of chapters in every corpus.

T4  SOUND.  For a fixed list of John's key Greek words and the Targum word for the same idea (chosen by the
     Hebrew it renders, listed below before scoring), map consonants to shared phonetic classes (labial,
     dental, velar, sibilant, l, r, m, n; gutturals and vowels dropped; matres ו/י dropped inside words) and
     call a pair an ECHO when their class skeletons share an ordered run of >= 3 consonants (LCS >= 3).
     Null 1: permute the Aramaic side across the list (10,000).  Null 2: John's content lemmas x random Targum
     words (Onkelos), with skeleton lengths matched.  Positive control: names and loanwords (Sabbath, Israel,
     Satan, Golgotha...) must echo at a high rate.
Usage: python3 targum.py <sources/texts>
"""
import collections, csv, glob, json, os, re, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import neofiti_en as NEN

SRC = sys.argv[1] if len(sys.argv) > 1 else "sources/texts"
HERE = os.path.dirname(os.path.abspath(__file__))
TG = os.path.join(SRC, "targum")
R = {}  # results
PV = []  # (test name, p) for BH

# ---------------------------------------------------------------- books
TORAH = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
PROPH = ["Joshua", "Judges", "I_Samuel", "II_Samuel", "I_Kings", "II_Kings", "Isaiah", "Jeremiah", "Ezekiel",
         "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
         "Zechariah", "Malachi"]
WRIT = ["Psalms", "Proverbs", "Job", "Song_of_Songs", "Ruth", "Lamentations", "Ecclesiastes", "Esther",
        "I_Chronicles", "II_Chronicles"]
WLC = dict(Genesis="Gen", Exodus="Exod", Leviticus="Lev", Numbers="Num", Deuteronomy="Deut", Joshua="Josh",
           Judges="Judg", I_Samuel="1Sam", II_Samuel="2Sam", I_Kings="1Kgs", II_Kings="2Kgs", Isaiah="Isa",
           Jeremiah="Jer", Ezekiel="Ezek", Hosea="Hos", Joel="Joel", Amos="Amos", Obadiah="Obad", Jonah="Jonah",
           Micah="Mic", Nahum="Nah", Habakkuk="Hab", Zephaniah="Zeph", Haggai="Hag", Zechariah="Zech",
           Malachi="Mal", Psalms="Ps", Proverbs="Prov", Job="Job", Song_of_Songs="Song", Ruth="Ruth",
           Lamentations="Lam", Ecclesiastes="Eccl", Esther="Esth", I_Chronicles="1Chr", II_Chronicles="2Chr")
GENRE = {**{b: "Torah" for b in TORAH}, **{b: "Former prophets" for b in PROPH[:6]},
         **{b: "Latter prophets" for b in PROPH[6:]}, **{b: "Writings" for b in WRIT}}

# ---------------------------------------------------------------- normalisation
FINAL = str.maketrans("ךםןףץ", "כמנפצ")
def heb_letters(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if "א" <= c <= "ת")
def strip_html(s): return re.sub(r"<[^>]+>", " ", s)
def tokens(text, neofiti_margins=False):
    """Aramaic/Hebrew verse -> list of consonantal tokens (final letters normalised)."""
    t = strip_html(text)
    if neofiti_margins:  # keep marginal/alternative readings, drop the "נ"א" sigla
        t = t.replace("[", " ").replace("]", " ")
    else:
        t = re.sub(r"\[[^\]]*\]", " ", t)  # main text only
    t = t.replace("(", "").replace(")", "")
    t = t.replace("־", " ").replace("־", " ")  # maqaf
    out = []
    for w in re.split(r"[\s:׃.,;]+", t):
        w = heb_letters(w).translate(FINAL)
        if w: out.append(w)
    return out

def load_targum(title):
    """title -> {(chapter, verse): text}"""
    out = {}
    if title.startswith("NeofitiEN_"):  # English translation of Neofiti (Diez Macho ed.), OCR, parsed by neofiti_en.py
        return NEN.parse(os.path.join(SRC, "neofiti_ia", title.split("_", 1)[1] + "_en.txt"))
    f = os.path.join(TG, title + ".json")
    if not os.path.exists(f): return out
    d = json.load(open(f, encoding="utf-8"))
    txt = d["versions"][0]["text"]
    for c, ch in enumerate(txt, 1):
        for v, s in enumerate(ch, 1):
            if isinstance(s, list): s = " ".join(x for x in s if isinstance(x, str))
            if isinstance(s, str) and s.strip(): out[(c, v)] = s
    return out

def targum_titles(book):
    if book in TORAH:
        return {"Onkelos": f"Onkelos_{book}", "Neofiti": f"NeofitiEN_{book}",
                "PsJonathan": f"Targum_Jonathan_on_{book}", "Fragment": f"Targum_Jerusalem,_{book}"}
    if book in PROPH: return {"Jonathan": f"Targum_Jonathan_on_{book}"}
    return {"Writings": f"Aramaic_Targum_to_{book}"}
PRIMARY = lambda b: "Onkelos" if b in TORAH else ("Jonathan" if b in PROPH else "Writings")

# ---------------------------------------------------------------- Hebrew (WLC)
DIVINE = {"3068", "3069", "430", "410", "433", "3050", "7706", "136"}
def load_wlc(code):
    x = open(os.path.join(SRC, "morphhb", "wlc", code + ".xml"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)">(.*?)</verse>', x, re.S):
        c, v, body = int(m.group(1)), int(m.group(2)), m.group(3)
        ws = re.findall(r'<w lemma="([^"]*)"[^>]*>([^<]*)</w>', body)
        lem = [set(re.findall(r"\d+", l)) for l, _ in ws]
        out[(c, v)] = dict(lem=lem, words=[heb_letters(w.replace("/", "")).translate(FINAL) for _, w in ws])
    return out
def heb_flags(h):
    lem = h["lem"]
    divine = any(l & DIVINE for l in lem)
    kavod = any("3519" in l for l in lem)
    anihu = any(("589" in lem[i] or "595" in lem[i]) and "1931" in lem[i + 1] for i in range(len(lem) - 1))
    aniyhwh = any(("589" in lem[i] or "595" in lem[i]) and ("3068" in lem[i + 1]) for i in range(len(lem) - 1))
    return divine, kavod, anihu, aniyhwh

# ---------------------------------------------------------------- term finder
PFX = r"(?:[ודבלכמ]{0,3})"
# Memra is spelled מימר- in these editions; bare ממרא is the place name Mamre, so it is not counted.
MEMRA = re.compile(rf"^{PFX}מימר(א|י|יה|ה|כ|כונ|הונ|יהונ|נא|יכ|יכונ|וי|ן|)$")
# Shekinah: שכינת- or defective שכנת- (Onkelos Exod 33:14 שכנתי); the prefix מ is excluded so that משכנא
# 'tabernacle' (which renders Hebrew mishkan) is not counted.
SHEK = re.compile(r"^[ודבלכ]{0,3}(?:שכינ|שכנ)(?:ת|תא|תיה|תי|תכ|תה|תהונ|תכונ|תנא)$|^[ודבלכ]{0,3}שכינא$")
YEQ = re.compile(rf"^{PFX}(?:א?יקר)(א|יה|י|כ|ה|)$")
DN = {"יי", "ייי", "דיי", "דייי", "יהוה", "ייה", "דה", "יוי", "דיוי"}
def find_terms(toks, heb):
    divine, kavod, anihu, _ = heb if heb else (False, False, False, False)
    c = collections.Counter()
    for i, w in enumerate(toks):
        nxt = toks[i + 1] if i + 1 < len(toks) else ""
        m = MEMRA.match(w)
        if m and not (m.group(1) == "" and w.lstrip("ו").startswith("ל")):  # exclude למימר 'saying'
            c["memra"] += 1
        if SHEK.match(w): c["shekinah"] += 1
        m = YEQ.match(w)
        if m and not w.lstrip("וד").startswith("ל"):
            bound = nxt in DN or nxt.lstrip("ד").startswith("שכינ") or (m.group(1) in ("יה", "י", "כ") and divine)
            if bound:
                c["yeqara_all"] += 1
                if not kavod: c["yeqara"] += 1
        if w.lstrip("ו") == "אנא" and nxt in ("הוא", "הו"):
            c["anahu_all"] += 1
            if not anihu: c["anahu"] += 1
        if re.match(rf"^{PFX}(?:דיבור|דבור|דביר|דבר)(א|יה|ה)$", w): c["dibbera"] += 1
    c["mediating"] = c["memra"] + c["shekinah"] + c["yeqara"] + c["anahu"]
    return c

# ---------------------------------------------------------------- load everything
ALLB = TORAH + PROPH + WRIT
HEB = {b: load_wlc(WLC[b]) for b in ALLB}
TV = {}   # (targum, book) -> {(c,v): Counter}
TLEN = {}
for b in ALLB:
    for tname, title in targum_titles(b).items():
        raw = load_targum(title)
        if not raw: continue
        d, L = {}, {}
        for k, s in raw.items():
            hf = heb_flags(HEB[b][k]) if k in HEB[b] else None
            if tname == "Neofiti":  # English: Word = Memra, Glory = Yeqara, Shekinah; insertion rules as for Aramaic
                c = collections.Counter(NEN.en_terms(s)); kav, ah = (hf[1], hf[2]) if hf else (False, False)
                c["yeqara"] = 0 if kav else c["yeqara_all"]; c["anahu"] = 0 if ah else c["anahu_all"]
                c["mediating"] = c["memra"] + c["shekinah"] + c["yeqara"] + c["anahu"]
                d[k] = c; L[k] = len(NEN.clean(s).split())
                continue
            tk = tokens(s)
            d[k] = find_terms(tk, hf); L[k] = len(tk)
        TV[(tname, b)] = d; TLEN[(tname, b)] = L

# ---------------------------------------------------------------- T1 map
T1 = {}
cats = ["memra", "shekinah", "yeqara", "yeqara_all", "anahu", "anahu_all", "dibbera", "mediating"]
rng = np.random.default_rng(39)
for (tname, b), d in TV.items():
    keys = list(d)
    hk = [k for k in keys if k in HEB[b]]
    div = np.array([heb_flags(HEB[b][k])[0] for k in hk])
    med = np.array([d[k]["mediating"] > 0 for k in hk])
    row = {c: int(sum(d[k][c] for k in keys)) for c in cats}
    row.update(verses=len(keys), aligned=len(hk), divine_verses=int(div.sum()),
               per1000=round(1000 * sum(d[k]["mediating"] > 0 for k in keys) / max(1, len(keys)), 1),
               share_divine_with_term=round(float(med[div].mean()) if div.any() else 0, 3),
               share_other_with_term=round(float(med[~div].mean()) if (~div).any() else 0, 3))
    if tname == "Neofiti": row["note"] = "English translation OCR (Word=Memra); verses parsed: %d" % len(keys)
    T1[f"{tname}|{b}"] = row
# totals per targum
tot = collections.defaultdict(lambda: collections.Counter())
for key, row in T1.items():
    t = key.split("|")[0]
    for c in cats + ["verses", "divine_verses"]: tot[t][c] += row[c]
# divine vs other: pooled within-book label permutation per targum (one test per targum)
T1div = {}
for t in tot:
    D, M, B = [], [], []
    for (tn, b), d in TV.items():
        if tn != t: continue
        for k in d:
            if k in HEB[b]: D.append(heb_flags(HEB[b][k])[0]); M.append(d[k]["mediating"] > 0); B.append(b)
    D, M, B = np.array(D), np.array(M), np.array(B)
    obs = M[D].mean() - M[~D].mean()
    null = []
    idx = {b: np.where(B == b)[0] for b in set(B)}
    for _ in range(1000):
        Dp = D.copy()
        for b, ii in idx.items(): Dp[ii] = rng.permutation(D[ii])
        null.append(M[Dp].mean() - M[~Dp].mean())
    p = (1 + sum(n >= obs for n in null)) / 1001
    T1div[t] = dict(rate_divine=round(float(M[D].mean()), 3), rate_other=round(float(M[~D].mean()), 3),
                    diff=round(float(obs), 3), p=round(p, 4))
    PV.append((f"T1 divine-name verses carry more mediating terms ({t})", p))
# positive control verses
def terms_at(t, b, c, v):
    d = TV.get((t, b), {}); return dict(d.get((c, v), {}))
CTRL = {"Gen 3:8 PsJonathan": terms_at("PsJonathan", "Genesis", 3, 8), "Gen 3:8 Neofiti": terms_at("Neofiti", "Genesis", 3, 8),
        "Gen 28:21 Onkelos": terms_at("Onkelos", "Genesis", 28, 21), "Exod 19:17 Onkelos": terms_at("Onkelos", "Exodus", 19, 17),
        "Deut 32:39 PsJonathan": terms_at("PsJonathan", "Deuteronomy", 32, 39), "Deut 32:39 Neofiti": terms_at("Neofiti", "Deuteronomy", 32, 39),
        "Isa 43:10 Jonathan": terms_at("Jonathan", "Isaiah", 43, 10), "Gen 1:1 Neofiti (main text)": terms_at("Neofiti", "Genesis", 1, 1),
        "Gen 1:3 Neofiti": terms_at("Neofiti", "Genesis", 1, 3), "Exod 33:14 Onkelos": terms_at("Onkelos", "Exodus", 33, 14)}
# Neofiti Gen 1:1 raw reading (short quotation)
neo11 = load_targum("Targum_Neofiti").get((1, 1), "")  # Sefaria stub (Gen 1:1-8 only), Aramaic main text
R["T1"] = dict(by_targum_book=T1, totals={t: dict(v) for t, v in tot.items()}, divine_vs_other=T1div,
               positive_control_verses={k: {kk: vv for kk, vv in v.items() if vv} for k, v in CTRL.items()},
               neofiti_gen1_1=neo11[:90])
genre_rate = collections.defaultdict(lambda: [0, 0])
for (t, b), d in TV.items():
    if t != PRIMARY(b): continue
    genre_rate[GENRE[b]][0] += sum(x["mediating"] > 0 for x in d.values()); genre_rate[GENRE[b]][1] += len(d)
R["T1"]["primary_by_genre_per1000"] = {g: round(1000 * a / n, 1) for g, (a, n) in genre_rate.items()}

# ---------------------------------------------------------------- T2 pointers
def R_(s):  # "Book c:v[-v2]" -> list of (book, c, v)   (Hebrew versification)
    out = []
    for part in s.split(";"):
        part = part.strip(); b, cv = part.rsplit(" ", 1); c, v = cv.split(":")
        if "-" in v: a, z = map(int, v.split("-")); out += [(b, int(c), x) for x in range(a, z + 1)]
        else: out.append((b, int(c), int(v)))
    return out
# John: formal quotations (the 12 in the brief + Ps 35:19/69:5, Ps 118:25-26, Ps 34:21/Num 9:12, Ps 69:22, Mic 5:1/2 Sam 7:12, Isa 12:3)
JOHN_Q = R_("Psalms 69:10; Isaiah 6:10; Isaiah 53:1; Psalms 82:6; Zechariah 9:9; Psalms 22:19; Exodus 12:46; Zechariah 12:10; "
            "Isaiah 40:3; Psalms 78:24; Isaiah 54:13; Psalms 41:10; Psalms 69:5; Psalms 35:19; Psalms 118:25-26; Psalms 34:21; "
            "Numbers 9:12; Psalms 69:22; Micah 5:1; II_Samuel 7:12; Exodus 16:4; Exodus 16:15")
JOHN_A = JOHN_Q + R_("Genesis 1:1-5; Genesis 2:7; Genesis 28:12; Exodus 3:14; Numbers 21:8-9; Exodus 33:18-23; Exodus 34:6; "
                     "Exodus 40:34; Deuteronomy 18:15; Isaiah 43:10; Isaiah 41:4; Isaiah 52:13; Ezekiel 34:11-16; Ezekiel 47:1-9; "
                     "Zechariah 14:8; Isaiah 55:1; Deuteronomy 19:15; Leviticus 24:16; Psalms 89:5; Psalms 89:37; Isaiah 5:1-7; "
                     "Deuteronomy 32:39; Isaiah 12:3; Genesis 22:8; Exodus 12:3-6; Isaiah 53:7")
MATT_Q = R_("Isaiah 7:14; Micah 5:1; II_Samuel 5:2; Hosea 11:1; Jeremiah 31:15; Isaiah 40:3; Deuteronomy 8:3; Psalms 91:11-12; "
            "Deuteronomy 6:16; Deuteronomy 6:13; Isaiah 8:23; Isaiah 9:1; Exodus 20:13; Exodus 20:14; Deuteronomy 24:1; "
            "Leviticus 19:12; Exodus 21:24; Leviticus 19:18; Isaiah 53:4; Hosea 6:6; Malachi 3:1; Isaiah 42:1-4; Jonah 2:1; "
            "Isaiah 6:9-10; Psalms 78:2; Isaiah 29:13; Exodus 20:12; Exodus 21:17; Deuteronomy 19:15; Genesis 1:27; Genesis 2:24; "
            "Zechariah 9:9; Isaiah 62:11; Isaiah 56:7; Jeremiah 7:11; Psalms 8:3; Psalms 118:22-23; Deuteronomy 25:5; Exodus 3:6; "
            "Deuteronomy 6:5; Psalms 110:1; Zechariah 13:7; Zechariah 11:13; Psalms 22:2; Isaiah 35:5")
LUKE_Q = R_("Malachi 3:23-24; Exodus 13:2; Exodus 13:12; Leviticus 12:8; Isaiah 40:3-5; Deuteronomy 8:3; Deuteronomy 6:13; "
            "Psalms 91:11-12; Deuteronomy 6:16; Isaiah 61:1-2; Isaiah 58:6; I_Kings 17:9; II_Kings 5:14; Malachi 3:1; Isaiah 6:9; "
            "Deuteronomy 6:5; Leviticus 19:18; Leviticus 18:5; Psalms 118:26; Isaiah 56:7; Jeremiah 7:11; Psalms 118:22; "
            "Deuteronomy 25:5; Exodus 3:6; Psalms 110:1; Isaiah 53:12; Hosea 10:8; Psalms 31:6; Psalms 22:8; Psalms 22:19; "
            "Genesis 19:26; Exodus 20:12-16")
SW2B = {"Genesis": "Genesis", "Exodus": "Exodus", "Leviticus": "Leviticus", "Numeri": "Numbers", "Deuteronomium": "Deuteronomy",
        "Josue": "Joshua", "Judices": "Judges", "Ruth": "Ruth", "Regnorum_I": "I_Samuel", "Regnorum_II": "II_Samuel",
        "Regnorum_III": "I_Kings", "Regnorum_IV": "II_Kings", "Paralipomenon_I": "I_Chronicles", "Paralipomenon_II": "II_Chronicles",
        "Esther": "Esther", "Psalmi": "Psalms", "Proverbia": "Proverbs", "Canticum": "Song_of_Songs", "Job": "Job",
        "Osee": "Hosea", "Amos": "Amos", "Michaeas": "Micah", "Joel": "Joel", "Abdias": "Obadiah", "Jonas": "Jonah",
        "Nahum": "Nahum", "Habacuc": "Habakkuk", "Sophonias": "Zephaniah", "Aggaeus": "Haggai", "Zacharias": "Zechariah",
        "Malachias": "Malachi", "Isaias": "Isaiah", "Jeremias": "Jeremiah", "Threni_seu_Lamentationes": "Lamentations",
        "Ezechiel": "Ezekiel"}
def lxx_ps_to_mt(c):
    if c <= 8: return c
    if c in (9,): return 9
    if c <= 112: return c + 1
    if c == 113: return 114
    if c in (114, 115): return 116
    if c <= 145: return c + 1
    if c in (146, 147): return 147
    return c
def csv_pointers(code):
    out = []
    for r in csv.DictReader(open(os.path.join(os.path.dirname(HERE), "..", "code", "analysis", "nt_pointers.csv"), encoding="utf-8")):
        if r["book"] != code: continue
        for ref in r["lxx"].split(";"):
            ref = ref.strip()
            if not ref: continue
            bk, cv = ref.rsplit(" ", 1)
            if bk not in SW2B or ":" not in cv: continue
            c, v = cv.split(":"); c = int(re.sub(r"\D", "", c)); v = int(re.sub(r"\D", "", v) or 0)
            b = SW2B[bk]
            if b == "Psalms": c = lxx_ps_to_mt(c)
            out.append((b, c, v))
    return out
SETS = {"John quotations": JOHN_Q, "John quotations+allusions": JOHN_A, "Matthew quotations": MATT_Q,
        "Luke quotations": LUKE_Q, "John rare-word pointers (csv)": csv_pointers("Jn"),
        "Matthew rare-word pointers (csv)": csv_pointers("Mt"), "Luke rare-word pointers (csv)": csv_pointers("Lk")}
# positive control set: every 'I am YHWH' verse (Hebrew) - classic Memra/self-revelation contexts; sample 40 at random
iam = [(b, c, v) for b in ALLB for (c, v), h in HEB[b].items() if heb_flags(h)[3]]
SETS["CONTROL: 'I am YHWH' verses (40 random)"] = [iam[i] for i in np.random.default_rng(7).choice(len(iam), 40, replace=False)]

def pointer_test(refs, layer="primary", n=10000, seed=39, lenmatch=False, divmatch=False):
    rg = np.random.default_rng(seed)
    obs, pools = [], []
    for b, c, v in refs:
        t = PRIMARY(b) if layer == "primary" else layer
        d = TV.get((t, b))
        if not d or (c, v) not in d: continue
        obs.append(d[(c, v)]["mediating"])
        ks = list(d)
        if lenmatch:
            L0 = TLEN[(t, b)][(c, v)]
            ks = [k for k in ks if abs(TLEN[(t, b)][k] - L0) <= 0.25 * L0 + 1]
        if divmatch and (c, v) in HEB[b]:  # same book AND same Hebrew divine-name status (added after first run)
            f0 = heb_flags(HEB[b][(c, v)])[0]
            ks = [k for k in ks if k in HEB[b] and heb_flags(HEB[b][k])[0] == f0] or ks
        pools.append(np.array([d[k]["mediating"] for k in ks]))
    if not obs: return None
    o = float(np.mean(obs))
    sims = np.zeros(n)
    for pool in pools: sims += pool[rg.integers(0, len(pool), n)]
    sims /= len(pools)
    p = (1 + np.sum(sims >= o)) / (n + 1)
    return dict(n_verses=len(obs), observed_mean=round(o, 3), null_mean=round(float(sims.mean()), 3),
                share_with_term=round(float(np.mean(np.array(obs) > 0)), 3), ratio=round(o / max(sims.mean(), 1e-9), 2), p=round(float(p), 4))
T2 = {}
for name, refs in SETS.items():
    T2[name] = dict(book_matched=pointer_test(refs), book_and_length_matched=pointer_test(refs, lenmatch=True),
                    book_and_divine_name_matched=pointer_test(refs, divmatch=True))
    for lay in ("Neofiti", "PsJonathan", "Onkelos"):
        tor = [r for r in refs if r[0] in TORAH]
        T2[name][f"{lay}_torah_only"] = pointer_test(tor, layer=lay)
        T2[name][f"{lay}_torah_only_divine_matched"] = pointer_test(tor, layer=lay, divmatch=True)
    T2[name]["genres"] = dict(collections.Counter(GENRE.get(b, "?") for b, _, _ in refs))
    PV.append((f"T2 pointer enrichment: {name} (book-matched)", T2[name]["book_matched"]["p"]))
    if T2[name]["Neofiti_torah_only"]:
        PV.append((f"T2 pointer enrichment: {name} (Neofiti, Torah verses, book+divine-name matched)", T2[name]["Neofiti_torah_only_divine_matched"]["p"]))
# per-verse detail for John's quotations
T2["John quotations detail"] = {f"{b} {c}:{v}": TV[(PRIMARY(b), b)].get((c, v), {}).get("mediating") for b, c, v in JOHN_Q}
# power: plant term-bearing verses into a John-size set
rgp = np.random.default_rng(11)
pos = [(b, c, v) for (t, b), d in TV.items() if t == PRIMARY(b) for (c, v), x in d.items() if x["mediating"] > 0]
alls = [(b, c, v) for (t, b), d in TV.items() if t == PRIMARY(b) for (c, v) in d]
hits = 0
for rep in range(100):
    s = [alls[i] for i in rgp.choice(len(alls), len(JOHN_Q) // 2, replace=False)] + [pos[i] for i in rgp.choice(len(pos), len(JOHN_Q) - len(JOHN_Q) // 2, replace=False)]
    hits += pointer_test(s, n=2000, seed=rep)["p"] < 0.05
T2["power_half_planted"] = hits / 100
null_hits = 0
for rep in range(100):
    s = [alls[i] for i in rgp.choice(len(alls), len(JOHN_Q), replace=False)]
    null_hits += pointer_test(s, n=2000, seed=1000 + rep)["p"] < 0.05
T2["false_positive_rate_random_sets"] = null_hits / 100
R["T2"] = T2

# ---------------------------------------------------------------- T3 prologue alignment
CONCEPTS = ["beginning", "word", "God", "life", "light", "darkness", "world", "dwelt", "glory", "grace_truth", "moses_law", "see_God"]
def gnorm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(ch for ch in w if not unicodedata.combining(ch))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
GLEX = [("beginning", r"^αρχη"), ("word", r"^(λογο|λογω|λογου|λογε|ρημα|ρηματ)"), ("God", r"^(θεο|θεω|θεε|κυρι)"),
        ("life", r"^(ζωη|ζωησ|ζων|ζωσ|ζησ|ζησε|ζη)$"), ("light", r"^(φωσ|φωτ)"), ("darkness", r"^σκοτ"), ("world", r"^κοσμ"),
        ("dwelt", r"^(σκην|κατεσκην|κατασκην|εσκην)"), ("glory", r"^(δοξα|δοξη|δεδοξ|εδοξ)"),
        ("grace_truth", r"^(χαρι|αληθ|ελεο|ελεει)"), ("moses_law", r"^(μωυσ|μωσ|νομο|νομω|νομου)"),
        ("see_God", r"^(ειδον|ειδεν|ιδε|ιδων|ιδειν|οψ|ωφθ|οφθ|εωρα|εωρακ|θεασ|εθεασ|ορα|ορω|ορασ)")]
ALEX = [("beginning", r"^[ודבלמ]{0,3}(קדמינ|לקדמינ|שירוי|ריש)"), ("word", r"^[ודבלמ]{0,3}(מימר|ממר|פתגמ|דבור|דיבור|דביר)"),
        ("God", r"^[ודבלמ]{0,3}(יי|ייי|אלה|אלהא|אלהי|אלהכ)$"), ("life", r"^[ודבלמ]{0,3}(חיי|חיינ|חיא|חי)$"),
        ("light", r"^[ודבלמ]{0,3}נהור"), ("darkness", r"^[ודבלמ]{0,3}(חשוכ|חשכ)"), ("world", r"^[ודבלמ]{0,3}(עלמ|עלמא)"),
        ("dwelt", r"^[ודבלמ]{0,3}(שכינ|משכנ|אשרי|שרי)"), ("glory", r"^[ודבלמ]{0,3}(יקר|איקר)"),
        ("grace_truth", r"^[ודבלמ]{0,3}(חסד|טיבו|קשוט|קושט|חנ|רחמ)"), ("moses_law", r"^[ודבלמ]{0,3}(משה|אוריית|אורית)$"),
        ("see_God", r"^[ודבלמ]{0,3}(חמא|חמי|חזי|חזא|חזו|אתגלי|יחזונ|יחמונ)")]
ELEX = [("beginning", r"^beginning"), ("word", r"^words?$"), ("God", r"^(god|lord)$"), ("life", r"^(life|live|living|alive|lives)$"),
        ("light", r"^lights?$"), ("darkness", r"^dark"), ("world", r"^worlds?$"), ("dwelt", r"^(dwell|dwelt|dwelling|shekinah|shekina|tent|tabernacle)"),
        ("glory", r"^glor"), ("grace_truth", r"^(grace|favour|favor|truth|true|kindness|mercy|merciful)$"), ("moses_law", r"^(moses|law)$"),
        ("see_God", r"^(see|saw|seen|sees|revealed|behold|beheld)$")]
def en_tokens(s): return [w.lower() for w in re.findall(r"[A-Za-z]+", NEN.clean(s))]
def concept_seq(toks, lex):
    seq = []
    for w in toks:
        for c, rx in lex:
            if re.match(rx, w): seq.append(c); break
    return seq
def first_order(seq):
    o = []
    for c in seq:
        if c not in o: o.append(c)
    return o
def lcs(a, b):
    m = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            m[i + 1][j + 1] = m[i][j] + 1 if a[i] == b[j] else max(m[i][j + 1], m[i + 1][j])
    return m[-1][-1]
def score(toks, lex, order=CONCEPTS): return lcs(first_order([c for c in concept_seq(toks, lex) if c in order]), order)
# corpora: chapter -> tokens
def aram_chapters(t):
    ch = collections.defaultdict(list)
    for b in TORAH:
        raw = load_targum(targum_titles(b)[t])
        for (c, v) in sorted(raw): ch[(b, c)] += (en_tokens if t == "Neofiti" else tokens)(raw[(c, v)])
    return ch
LXXF = {"Genesis": "01.Genesis", "Exodus": "02.Exodus", "Leviticus": "03.Leviticus", "Numbers": "04.Numeri", "Deuteronomy": "05.Deuteronomium"}
def lxx_chapters():
    ch = collections.defaultdict(list)
    for b, f in LXXF.items():
        for l in open(os.path.join(SRC, "lxx-swete", "data", f + ".txt"), encoding="utf-8"):
            p = l.split()
            if len(p) < 2: continue
            _, c, v = p[0].split(".")
            w = gnorm(p[1])
            if w: ch[(b, int(c))].append(w)
    return ch
CORP = {"Neofiti (English tr.)": (aram_chapters("Neofiti"), ELEX), "PsJonathan": (aram_chapters("PsJonathan"), ALEX), "Onkelos": (aram_chapters("Onkelos"), ALEX), "LXX": (lxx_chapters(), GLEX)}
# John 1:1-18 itself (sanity: lexicon finds John's own order)
jn = [gnorm(l.split()[3]) for l in open(glob.glob(os.path.join(SRC, "sblgnt", "*-Jn-morphgnt.txt"))[0], encoding="utf-8")
      if l[2:4] == "01" and int(l[4:6]) <= 18]
T3 = {"john_prologue_self_score": score(jn, GLEX), "john_prologue_first_order": first_order(concept_seq(jn, GLEX))}
rg3 = np.random.default_rng(39)
for name, (ch, lex) in CORP.items():
    tgt = ch[("Genesis", 1)] + ch[("Exodus", 33)] + ch[("Exodus", 34)]
    s0 = score(tgt, lex); L0 = len(tgt)
    keys = list(ch); null = []
    while len(null) < 10000:
        a, b = keys[rg3.integers(len(keys))], keys[rg3.integers(len(keys))]
        if a == b: continue
        L = len(ch[a]) + len(ch[b])
        if abs(L - L0) > 0.25 * L0: continue
        null.append(score(ch[a] + ch[b], lex))
    null = np.array(null)
    p = (1 + np.sum(null >= s0)) / (len(null) + 1)
    # positive control: Genesis overlay subsequence ranks Gen 1 among single chapters
    sub = ["beginning", "God", "light", "darkness"]
    sc = {k: score(v, lex, sub) for k, v in ch.items()}
    rank = sum(x > sc[("Genesis", 1)] for x in sc.values()) + 1
    T3[name] = dict(target_score=s0, target_first_order=first_order(concept_seq(tgt, lex)), target_tokens=L0,
                    null_mean=round(float(null.mean()), 2), null_sd=round(float(null.std()), 2),
                    z=round(float((s0 - null.mean()) / max(null.std(), 1e-9)), 2), p=round(float(p), 4),
                    control_gen1_overlay_score=sc[("Genesis", 1)], control_gen1_rank=rank, control_chapters=len(sc),
                    control_ties_at_or_above=int(sum(x >= sc[("Genesis", 1)] for x in sc.values())))
    PV.append((f"T3 prologue order vs {name} Gen1+Exod33-34", p))
R["T3"] = T3

# ---------------------------------------------------------------- T4 sound echo
GCL = {"π": "P", "β": "P", "φ": "P", "τ": "T", "δ": "T", "θ": "T", "κ": "K", "γ": "K", "χ": "K", "σ": "S", "ζ": "S",
       "λ": "L", "ρ": "R", "μ": "M", "ν": "N"}
def gskel(w):
    w = gnorm(w); out = []
    for i, ch in enumerate(w):
        if ch == "ξ": out += ["K", "S"]
        elif ch == "ψ": out += ["P", "S"]
        elif ch == "γ" and i + 1 < len(w) and w[i + 1] in "γκχξ": out.append("N")
        elif ch in GCL: out.append(GCL[ch])
    return "".join(out)
ACL = {"ב": "P", "פ": "P", "ת": "T", "ט": "T", "ד": "T", "כ": "K", "ג": "K", "ק": "K", "ס": "S", "ש": "S", "ז": "S",
       "צ": "S", "ל": "L", "ר": "R", "מ": "M", "נ": "N"}
def askel(w):
    w = heb_letters(w).translate(FINAL); out = []
    for i, ch in enumerate(w):
        if ch in "וי" and i > 0: continue
        if ch in ACL: out.append(ACL[ch])
    return "".join(out)
def slcs(a, b): return lcs(list(a), list(b))
# Greek inflectional endings removed from the lemma before skeletonising (so -ος, -ον do not add an S/N)
def gstem(lem):
    w = gnorm(lem)
    for e in ("ομαι", "εω", "οω", "αω", "ια", "ος", "ον", "ης", "ησ", "ασ", "οσ", "η", "α", "ω", "υσ", "ισ", "ευσ"):
        if w.endswith(e) and len(w) > len(e) + 2: return w[: -len(e)]
    return w
# John's key words and the Targum word for the same idea (the word that renders the Hebrew of the same idea in
# Onkelos/Neofiti); Aramaic given as the bare noun/verb stem without the emphatic -א, prefixes or suffixes.
PAIRS = [("σκηνοω", "שכינ", "dwell / Shekinah (Jn 1:14)"), ("λογος", "מימר", "word / Memra"), ("αρχη", "קדמ", "beginning"),
         ("ζωη", "חי", "life"), ("φως", "נהור", "light"), ("σκοτια", "חשוכ", "darkness"), ("κοσμος", "עלמ", "world"),
         ("δοξα", "יקר", "glory"), ("χαρις", "חסד", "grace"), ("αληθεια", "קושט", "truth"), ("θεος", "אלה", "God"),
         ("κυριος", "רבונ", "lord"), ("πνευμα", "רוח", "spirit"), ("σαρξ", "בסר", "flesh"), ("υιος", "בר", "son"),
         ("πατηρ", "אב", "father"), ("μαρτυρια", "סהדו", "witness"), ("ονομα", "שמ", "name"), ("πληρωμα", "מלי", "fullness"),
         ("αμνος", "אמר", "lamb"), ("αρτος", "לחמ", "bread"), ("υδωρ", "מי", "water"), ("οδος", "ארח", "way"),
         ("αμπελος", "גופנ", "vine"), ("θυρα", "תרע", "door"), ("ποιμην", "רעי", "shepherd"), ("ζητεω", "בעי", "seek"),
         ("μενω", "שרי", "abide/dwell"), ("θεαομαι", "חזי", "behold"), ("γινωσκω", "ידע", "know"), ("πιστευω", "הימנ", "believe"),
         ("αγαπη", "רחמ", "love"), ("ωρα", "שעת", "hour"), ("σημειον", "את", "sign"), ("εντολη", "תפקיד", "commandment"),
         ("βασιλεια", "מלכו", "kingdom")]
# (σκηνή / משכנא 'tabernacle' is the same root family as σκηνόω / שכינתא, so it is reported separately, not counted)
EXTRA4 = [("σκηνη", "משכנ", "tent / tabernacle (same family as dwell)")]
CTRL4 = [("σαββατον", "שבת"), ("ισραηλ", "ישראל"), ("σατανας", "סטנ"), ("γολγοθα", "גלגלת"), ("βηθσαιδα", "ביתצידא"),
         ("ναζωραιος", "נצרי"), ("καφαρναουμ", "כפרנחומ"), ("γαββαθα", "גבתא"), ("ιορδανης", "ירדנ"), ("βηθανια", "ביתעני"),
         ("ζεβεδαιος", "זבדי"), ("φαρισαιος", "פרישא"), ("σαμαρεια", "שמרינ"), ("μαρθα", "מרתא"), ("ιερουσαλημ", "ירושלמ"),
         ("μεσσιας", "משיח"), ("πασχα", "פסח"), ("ραββι", "רבי"), ("κηφας", "כיפא"), ("σιλωαμ", "שילוח")]
def echo(g, a, k=3): return slcs(gskel(gstem(g)), askel(a)) >= k
pe = [echo(g, a) for g, a, _ in PAIRS]
ce = [echo(g, a) for g, a in CTRL4]
ce2 = [slcs(gskel(gstem(g)), askel(a)) >= min(3, len(askel(a))) for g, a in CTRL4]
rg4 = np.random.default_rng(39)
obs4 = sum(pe); perm = []
A = [a for _, a, _ in PAIRS]
for _ in range(10000):
    Ap = rg4.permutation(A); perm.append(sum(echo(g, a) for (g, _, _), a in zip(PAIRS, Ap)))
perm = np.array(perm); p4 = (1 + np.sum(perm >= obs4)) / 10001
# null 2: John's content lemmas x random Onkelos words
jlem = sorted({gnorm(l.split()[6]) for l in open(glob.glob(os.path.join(SRC, "sblgnt", "*-Jn-morphgnt.txt"))[0], encoding="utf-8")
               if l.split()[1][0] in "NVA"})
onk = []
for b in TORAH:
    for s in load_targum(f"Onkelos_{b}").values(): onk += tokens(s)
onk = sorted(set(onk))
# strip the emphatic -א and common proclitics, as was done by hand for the PAIRS
def astem(w):
    w = re.sub(r"^[ודבל]{1,2}(?=...)", "", w); return re.sub(r"(א|יא|ין|יה|תא)$", "", w) if len(w) > 3 else w
onk_st = [astem(w) for w in onk]
gl = [len(gskel(gstem(g))) for g, _, _ in PAIRS]; al = [len(askel(a)) for _, a, _ in PAIRS]
r2 = []
jl_by = collections.defaultdict(list); [jl_by[len(gskel(gstem(w)))].append(w) for w in jlem]
on_by = collections.defaultdict(list); [on_by[len(askel(w))].append(w) for w in onk_st]
for _ in range(20000):
    i = rg4.integers(len(PAIRS)); G = jl_by.get(gl[i]) or jlem; Aw = on_by.get(al[i]) or onk_st
    r2.append(echo(G[rg4.integers(len(G))], Aw[rg4.integers(len(Aw))]))
rate2 = float(np.mean(r2))
# binomial tail for the observed count under rate2 (exact)
from math import comb
n4 = len(PAIRS)
p4b = sum(comb(n4, k) * rate2 ** k * (1 - rate2) ** (n4 - k) for k in range(obs4, n4 + 1))
T4 = dict(pairs={d: dict(greek=g, aramaic=a, g_skel=gskel(gstem(g)), a_skel=askel(a), lcs=slcs(gskel(gstem(g)), askel(a)), echo=bool(e))
                 for (g, a, d), e in zip(PAIRS, pe)},
          n_pairs=n4, echoes=int(obs4), echo_list=[d for (g, a, d), e in zip(PAIRS, pe) if e],
          permutation_null_mean=round(float(perm.mean()), 2), p_permutation=round(float(p4), 4),
          random_pair_rate=round(rate2, 4), expected_echoes_random=round(rate2 * n4, 2), p_binomial_random=round(float(p4b), 4),
          control_names_loanwords={g: dict(g_skel=gskel(gstem(g)), a_skel=askel(a), echo3=bool(e), echo_min=bool(e2)) for (g, a), e, e2 in zip(CTRL4, ce, ce2)},
          control_rate_3=round(float(np.mean(ce)), 3), control_rate_full=round(float(np.mean(ce2)), 3),
          skn_single_pair_rarity="share of random John-lemma x Onkelos-word pairs with the same skeleton lengths that echo: see random_pair_rate")
# how rare is S-K-N specifically: share of Onkelos stems containing S..K..N and of John lemmas containing S..K..N
def has(sk, pat): return slcs(sk, pat) == len(pat)
T4["extra_same_family"] = {d: dict(g_skel=gskel(gstem(g)), a_skel=askel(a), echo=bool(echo(g, a))) for g, a, d in EXTRA4}
T4["share_john_lemmas_with_SKN"] = round(float(np.mean([has(gskel(gstem(w)), "SKN") for w in jlem])), 4)
T4["share_onkelos_stems_with_SKN"] = round(float(np.mean([has(askel(w), "SKN") for w in onk_st])), 4)
PV.append(("T4 Greek-Aramaic consonant echoes beyond permutation", p4))
PV.append(("T4 echoes beyond random-pair rate", p4b))
R["T4"] = T4

# ---------------------------------------------------------------- BH correction
ps = np.array([p for _, p in PV]); m = len(ps); order = np.argsort(ps)
q = np.empty(m); prev = 1.0
for rank, i in reversed(list(enumerate(order, 1))):
    prev = min(prev, ps[i] * m / rank); q[i] = prev
R["tests"] = [dict(test=t, p=round(float(p), 4), q_BH=round(float(qq), 4), survives=bool(qq < 0.05)) for (t, p), qq in zip(PV, q)]
R["n_tests"] = m
json.dump(R, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for t in R["tests"]: print(f"{t['p']:.4f} {t['q_BH']:.4f} {'*' if t['survives'] else ' '} {t['test']}")
