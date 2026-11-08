#!/usr/bin/env python3
"""Three physical readings of the scripts, each tested against chance.

A. LETTERS AS PICTURES.  Every Hebrew and Greek letter descends from an Egyptian hieroglyph via the
   Proto-Sinaitic script (Serabit el-Khadim, c. 1850 BCE).  Origins follow Gardiner (1916) and
   Hamilton, *The Origins of the West Semitic Alphabet in Egyptian Scripts* (2006); disputed ones are
   marked '?'.  Genesis 1:1 and John 1:1 are read as picture sequences and their picture categories
   compared with every verse of similar length (percentile).
B. BREATH LETTERS.  Hebrew roots written only with throat sounds and glides (alef, he, het, ayin,
   waw, yod): the letters of YHWH and EHYEH ('I am', Exod 3:14).  Do their meanings cluster around
   being / life / breath more than other roots?  Fisher exact test on Strong's primitive roots.
C. SOUND AND MEANING.  Do words for light / day / white use brighter (front) vowels than words for
   darkness / night / black, across Egyptian (Coptic), Hebrew, Aramaic, Greek, Ge'ez, Akkadian?
Usage: python3 letters_breath.py <morphhb/wlc> <HebrewStrong.xml> <sblgnt>
"""
import collections, glob, json, math, os, random, re, sys, unicodedata
from scipy.stats import fisher_exact, binomtest

WLC, STRONG, NT = sys.argv[1], sys.argv[2], sys.argv[3]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "letters_breath_results.json")
res = {}

# ---------------------------------------------------------------- A. letters as pictures
HEB = {  # letter: (name, picture, Gardiner sign, category)
    "א": ("alef", "ox head", "F1", "animal"), "ב": ("bet", "house", "O1", "house"),
    "ג": ("gimel", "throw-stick?", "T14", "tool"), "ד": ("dalet", "door?", "O31", "house"),
    "ה": ("he", "man with raised arms (jubilation)", "A28", "body"), "ו": ("waw", "peg / mace", "T3", "tool"),
    "ז": ("zayin", "weapon?", "?", "tool"), "ח": ("het", "courtyard / fence?", "O4", "house"),
    "ט": ("tet", "wheel / good?", "?", "uncertain"), "י": ("yod", "arm and hand", "D36", "body"),
    "כ": ("kaf", "palm of hand", "D46", "body"), "ך": ("kaf", "palm of hand", "D46", "body"),
    "ל": ("lamed", "shepherd's crook / goad", "S39", "tool"), "מ": ("mem", "water", "N35", "water"),
    "ם": ("mem", "water", "N35", "water"), "נ": ("nun", "snake", "I10", "animal"), "ן": ("nun", "snake", "I10", "animal"),
    "ס": ("samekh", "djed pillar?", "R11", "uncertain"), "ע": ("ayin", "eye", "D4", "body"),
    "פ": ("pe", "mouth", "D21", "body"), "ף": ("pe", "mouth", "D21", "body"),
    "צ": ("tsade", "plant?", "M22", "uncertain"), "ץ": ("tsade", "plant?", "M22", "uncertain"),
    "ק": ("qof", "skein / monkey?", "V24", "uncertain"), "ר": ("resh", "head", "D1", "body"),
    "ש": ("shin", "tooth? / bow?", "?", "body"), "ת": ("taw", "mark, cross", "Z9", "sign"),
}
GRK2HEB = {"α": "א", "β": "ב", "γ": "ג", "δ": "ד", "ε": "ה", "ζ": "ז", "η": "ח", "θ": "ט", "ι": "י", "κ": "כ",
           "λ": "ל", "μ": "מ", "ν": "נ", "ξ": "ס", "ο": "ע", "π": "פ", "ρ": "ר", "σ": "ש", "ς": "ש", "τ": "ת",
           "υ": "ו", "ω": "ע"}  # phi, chi, psi are Greek additions with no Semitic source
CATS = ["body", "house", "water", "animal", "tool", "sign", "uncertain", "greek-added"]


def heb_cons(word):
    return [c for c in unicodedata.normalize("NFD", word) if c in HEB]


def grk_letters(word):
    w = unicodedata.normalize("NFD", word.lower())
    return [c for c in w if "α" <= c <= "ω" or c == "ς"]


def profile(letters, kind):
    c = collections.Counter()
    for ch in letters:
        if kind == "heb": c[HEB[ch][3]] += 1
        else: c[HEB[GRK2HEB[ch]][3] if ch in GRK2HEB else "greek-added"] += 1
    n = sum(c.values()) or 1
    return {k: c[k] / n for k in CATS}, c


# Hebrew Bible verses
verses = {}
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', open(f, encoding="utf-8").read(), re.S):
        words = re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2))
        verses[m.group(1)] = [c for w in words for c in heb_cons(w.replace("/", ""))]
# NT verses
ntv = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(NT, "*-morphgnt.txt"))):
    for line in open(f, encoding="utf-8"):
        p = line.split(); ntv[(os.path.basename(f), p[0])] += grk_letters(p[5])


def test_verse(target, pool, kind, label):
    pt, ct = profile(target, kind)
    L = len(target)
    same = [v for v in pool if abs(len(v) - L) <= max(3, L // 10) and v is not target]
    out = {"letters": L, "comparison_verses": len(same), "categories": {}}
    for k in CATS:
        vals = sorted(profile(v, kind)[0][k] for v in same)
        pct = sum(x < pt[k] for x in vals) / len(vals) + 0.5 * sum(x == pt[k] for x in vals) / len(vals)
        out["categories"][k] = dict(count=ct[k], share=round(pt[k], 3), percentile=round(pct, 3))
    print(f"\n{label}: {L} letters, compared with {len(same)} verses of similar length")
    for k, v in out["categories"].items():
        flag = "  <-- outside 2.5-97.5%" if v["percentile"] < 0.025 or v["percentile"] > 0.975 else ""
        print(f"   {k:12s} n={v['count']:3d} share={v['share']:.2f} percentile={v['percentile']:.3f}{flag}")
    return out


res["A_gen1_1"] = test_verse(verses["Gen.1.1"], list(verses.values()), "heb", "Genesis 1:1 (Hebrew)")
res["A_gen1_1_5"] = None
j11 = ntv[("64-Jn-morphgnt.txt", "040101")]
res["A_john1_1"] = test_verse(j11, list(ntv.values()), "grk", "John 1:1 (Greek)")


def picture(word, kind):
    if kind == "heb": return [f"{HEB[c][1]} ({HEB[c][2]})" for c in heb_cons(word)]
    return [(f"{HEB[GRK2HEB[c]][1]} ({HEB[GRK2HEB[c]][2]})" if c in GRK2HEB else "Greek addition") for c in grk_letters(word)]


NAMES = [("יהוה", "heb", "YHWH"), ("אהיה", "heb", "EHYEH 'I am' (Exod 3:14)"), ("אלהים", "heb", "Elohim"),
         ("אדני", "heb", "Adonai"), ("שדי", "heb", "Shaddai"), ("דבר", "heb", "davar, word"), ("אור", "heb", "or, light"),
         ("מים", "heb", "mayim, water"), ("רוח", "heb", "ruach, breath"), ("λογος", "grk", "logos"), ("θεος", "grk", "theos"),
         ("φως", "grk", "phos, light"), ("ζωη", "grk", "zoe, life"), ("ιαω", "grk", "Iao (magical papyri)")]
res["A_names"] = {}
print("\nNames read as pictures:")
for w, k, lab in NAMES:
    pic = picture(w, k); res["A_names"][lab] = pic
    print(f"   {lab:28s} " + " | ".join(pic))

# ---------------------------------------------------------------- B. breath letters
BREATH = set("אהחעוי")
entries = re.findall(r'<entry id="(H\d+)">(.*?)</entry>', open(STRONG, encoding="utf-8").read(), re.S)
roots = []
for eid, body in entries:
    if "primitive root" not in body: continue
    w = re.search(r"<w [^>]*>([^<]+)</w>", body)
    if not w: continue
    cons = [c for c in unicodedata.normalize("NFD", w.group(1)) if c in HEB]
    cons = ["כ" if c == "ך" else "מ" if c == "ם" else "נ" if c == "ן" else "פ" if c == "ף" else "צ" if c == "ץ" else c for c in cons]
    meaning = re.sub(r"<[^>]+>", "", (re.search(r"<meaning>(.*?)</meaning>", body, re.S) or re.search(r"<usage>(.*?)</usage>", body, re.S) or [None, ""])[1])
    roots.append(dict(id=eid, word=w.group(1), cons="".join(cons), meaning=meaning.strip()))
# field list tightened after the first run (bare "be" matched phrases like "to be suitable"):
FIELD = re.compile(r"\b(exist|existence|live|life|alive|revive|breath|breathe|blow|wind|vapou?r|spirit)", re.I)
breath_roots = [r for r in roots if r["cons"] and set(r["cons"]) <= BREATH]
other = [r for r in roots if r["cons"] and not set(r["cons"]) <= BREATH]
a = sum(bool(FIELD.search(r["meaning"])) for r in breath_roots); b = len(breath_roots) - a
c = sum(bool(FIELD.search(r["meaning"])) for r in other); d = len(other) - c
OR, p = fisher_exact([[a, b], [c, d]], alternative="greater")
# letter-frequency expectation: chance a random 3-letter root is all breath letters, using root letter frequencies
lf = collections.Counter(ch for r in other + breath_roots for ch in r["cons"]); tot = sum(lf.values())
pb = sum(lf[ch] for ch in BREATH) / tot
print(f"\nB. Strong's primitive roots: {len(roots)}; built only from breath letters (א ה ח ע ו י): {len(breath_roots)}"
      f" ({len(breath_roots) / len(roots):.1%}; letter share of breath letters in roots = {pb:.1%})")
print(f"   meaning in the field being/life/breath/voice: breath-only {a}/{len(breath_roots)} ({a / len(breath_roots):.0%}) vs others {c}/{len(other)} ({c / len(other):.0%}); "
      f"odds ratio {OR:.1f}, one-sided Fisher p = {p:.2g}")
for r in breath_roots:
    print(f"   {r['id']:6s} {r['word']:8s} {r['cons']:5s} {r['meaning'][:90]}")
res["B"] = dict(roots=len(roots), breath_only=len(breath_roots), field_breath=[a, len(breath_roots)], field_other=[c, len(other)],
                odds_ratio=OR, p=p, breath_letter_share=pb, list=[(r["id"], r["word"], r["meaning"][:120]) for r in breath_roots])

# ---------------------------------------------------------------- C. sound and meaning
# vowel brightness: i 1.0, e 0.75, a/ə 0.5, o 0.25, u 0.0 (front-to-back); transcriptions in Latin letters
VB = {"i": 1, "ü": 1, "e": .75, "a": .5, "ə": .5, "o": .25, "u": 0}  # y = consonant; Greek upsilon written ü
PAIRS = [  # (language, bright-meaning word, dark-meaning word, concept)
    ("Coptic (Egyptian)", "ouoein", "kake", "light/darkness"), ("Hebrew", "or", "hoshek", "light/darkness"),
    ("Aramaic", "nehora", "heshoka", "light/darkness"), ("Greek", "phos", "skotos", "light/darkness"),
    ("Ge'ez", "berhan", "selmat", "light/darkness"), ("Akkadian", "nuru", "ekletu", "light/darkness"),
    ("Coptic (Egyptian)", "hoou", "oush", "day/night"), ("Hebrew", "yom", "layla", "day/night"),
    ("Aramaic", "yoma", "lelya", "day/night"), ("Greek", "hemera", "nüx", "day/night"),
    ("Ge'ez", "elat", "lelit", "day/night"), ("Akkadian", "umu", "musu", "day/night"),
    ("Coptic (Egyptian)", "ouobsh", "kame", "white/black"), ("Hebrew", "lavan", "shahor", "white/black"),
    ("Aramaic", "hiwar", "ukam", "white/black"), ("Greek", "leukos", "melas", "white/black"),
    ("Ge'ez", "sada", "sallim", "white/black"), ("Akkadian", "pesu", "salmu", "white/black"),
]


def bright(w):
    v = [VB[ch] for ch in w if ch in VB]
    return sum(v) / len(v)


wins = 0; ties = 0; rows = []
for lang, bw, dw, concept in PAIRS:
    sb, sd = bright(bw), bright(dw); wins += sb > sd; ties += sb == sd
    rows.append((lang, concept, bw, round(sb, 2), dw, round(sd, 2))); print(f"   C {lang:18s} {concept:15s} {bw:8s} {sb:.2f}  vs  {dw:8s} {sd:.2f}")
n_ = len(PAIRS) - ties; bt = binomtest(wins, n_, 0.5)
print(f"C. bright-meaning word has the brighter vowels in {wins} of {n_} untied pairs ({ties} ties); two-sided sign test p = {bt.pvalue:.2f}")
res["C"] = dict(pairs=rows, wins=wins, untied=n_, ties=ties, p=bt.pvalue)
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
