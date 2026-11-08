#!/usr/bin/env python3
"""Round 22: steps 1-3 of the REPORT path.

1a. P75 LINES: do P75's line breaks fall at clause ends (SBLGNT punctuation) more than random breaks at word boundaries?
    How often does a line split a word?
1b. QUIET FAREWELL beyond pronouns: noise share of 13:31-17:26 against the rest of John, with and without pronouns.
2a. SEPARATION ARC WITH CONTROLS: the same automatic word families (separate / gather / complete) in John, Matthew,
    Mark, Luke; order test in each.
2b. CENTRE MOTIF CATALOGUE (fixed list): the letter-centre window (±2 verses) of every Hebrew book; is any motif
    (heaven+earth, water, light, house of YHWH / temple, gate, tree, life, name) commoner there than in random windows?
3.  MYTH PASS: a fixed motif list (descent to the dead, death, mourning, three days, life-water/food, rising, substitute,
    seven gates) coded by keyword in John, Mark, the Homeric Hymn to Demeter (Persephone), Plutarch's On Isis and
    Osiris, Inana's Descent (English); controls: Homeric Hymns to Apollo and Hermes, Genesis 37-50 (Joseph).
Usage: python3 round22.py <sblgnt> <lxx-swete/data> <morphhb/wlc> <cntr class 1> <greek dir> <sumer txt> <KJV.csv>
"""
import collections, csv, difflib, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC, CN, GR, LIT, KJV = sys.argv[1:8]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(22); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
SB = collections.OrderedDict()
for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"):
    p = l.split(); SB.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append((nrm(p[4]), bool(re.search(r"[,.·;:]$", p[3])), p[3]))
print("1a. P75 LINE BREAKS")
real_at = real_n = split = 0; nullshare = []
breaks_all = []
for l in open(os.path.join(CN, "P75.txt"), encoding="utf-8"):
    m = re.match(r"^43(\d{3})(\d{3})\s+(.*)$", l.rstrip("\n"))
    if not m: continue
    ref = (int(m.group(1)), int(m.group(2)))
    if ref not in SB: continue
    toks = m.group(3).split(); words = []; brk_before = []
    for tok in toks:
        if re.search(r"[α-ω]/[α-ω]|[α-ω]/\^|\^/[α-ω]", tok): split += 1
        w = re.sub(r"[^α-ως]", "", tok.replace("ς", "σ"))
        if w: words.append(w); brk_before.append(tok.startswith("/") or tok.startswith("\\"))
    sbw = [w for w, _, _ in SB[ref]]; punct = [pc for _, pc, _ in SB[ref]]
    sm = difflib.SequenceMatcher(a=words, b=sbw, autojunk=False); amap = {}
    for a0, b0, n in sm.get_matching_blocks():
        for i in range(n): amap[a0 + i] = b0 + i
    bounds = [i for i in range(1, len(words)) if i - 1 in amap]
    for i in bounds:
        at = punct[amap[i - 1]]
        breaks_all.append((brk_before[i], at))
B = np.array([b for b, _ in breaks_all]); A = np.array([a for _, a in breaks_all])
real = A[B].mean(); null = [A[rng.permutation(len(B))[:B.sum()]].mean() for _ in range(2000)]
print(f"   line breaks between words: {B.sum()}; at a clause end {real:.1%}; random word boundaries {np.mean(null):.1%}; p = {np.mean(np.array(null) >= real):.4f}")
print(f"   line breaks that split a word: {split} (scribes divide words freely)")
out["p75_lines"] = dict(breaks=int(B.sum()), at_clause=float(real), random=float(np.mean(null)), split_words=split)
print("\n1b. QUIET FAREWELL beyond pronouns")
OBS = {"p", "b", "t", "d", "k", "g", "pʰ", "tʰ", "kʰ", "f", "v", "θ", "ð", "s", "z", "x", "ɣ", "ç", "ʝ", "h", "ps", "ks", "β", "φ", "dz", "ts"}
PRON = set("εγω μου μοι με εμου εμοι εμε συ σου σοι σε ημεισ ημων ημιν ημασ υμεισ υμων υμιν υμασ".split()); cache = {}
def ph(raw):
    k = unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw.lower()))
    if k not in cache:
        try: cache[k] = [p for s in E.parse_greek(k, "koine")[0] for p in s["ph"]]
        except Exception: cache[k] = []
    return cache[k]
from scipy.stats import mannwhitneyu
for drop in (False, True):
    def chunks(sel):
        toks = [r for k, v in SB.items() if sel(k) for (w, _, r) in v if not (drop and w in PRON)]
        res = []
        for i in range(0, len(toks) - 150, 300):
            p_ = [x for t in toks[i:i + 300] for x in ph(t)]; res.append(sum(x in OBS for x in p_) / max(1, len(p_)))
        return res
    f = chunks(lambda k: (13, 31) <= k <= (17, 26)); o = chunks(lambda k: not ((13, 31) <= k <= (17, 26)))
    print(f"   {'pronouns removed' if drop else 'all words      '}: farewell {np.mean(f):.3f} vs rest {np.mean(o):.3f}  p = {mannwhitneyu(f, o, alternative='less').pvalue:.4f}")
print("\n2a. SEPARATION -> GATHER -> COMPLETE, same automatic families in each Gospel")
SEP = ("σχισ", "σχιζ", "εσχισ", "σκορπι", "εσκορπ", "διασκορπ", "διεσκορπ", "χωρισ"); GAT = ("συναγαγ", "συναγει", "συνηγαγ", "συναγουσ", "συνηχθ", "επισυναγ")
COM = ("τελεω", "τετελ", "τελειω", "ετελει", "τετελειω", "ετελεσ", "τελεσ")
def inv(x): return sum(1 for i in range(len(x)) for j in range(i + 1, len(x)) if x[i] > x[j])
for code in ("Jn", "Mt", "Mk", "Lk"):
    ws = [nrm(l.split()[4]) for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8")]
    ev = [(0 if w.startswith(SEP) else 1 if w.startswith(GAT) else 2) for w in ws if w.startswith(SEP + GAT + COM)]
    r = inv(ev); nl = [inv(list(rng.permutation(ev))) for _ in range(5000)]
    print(f"   {code}: events {len(ev):3d}  inversions {r} (random median {int(np.median(nl))})  p = {np.mean(np.array(nl) <= r):.3f}")
print("\n2b. CENTRE MOTIF CATALOGUE (Hebrew letter-centres, window of 5 verses)")
def cons(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת").translate(str.maketrans("ךםןףץ", "כמנפצ"))
BK = {}
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    x = open(f, encoding="utf-8").read(); vs = []
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S):
        ws = [cons(p) for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2)) for p in w.split("/")]; vs.append((m.group(1), [w for w in ws if w]))
    if len(vs) > 20: BK[os.path.basename(f)[:-4]] = vs
MOT = {"heaven and earth": lambda ws: "שמימ" in ws and "ארצ" in ws, "water": lambda ws: "מימ" in ws, "light": lambda ws: "אור" in ws,
       "house of YHWH / temple": lambda ws: "היכל" in ws or any(a == "בית" and b == "יהוה" for a, b in zip(ws, ws[1:])), "gate": lambda ws: "שער" in ws,
       "tree": lambda ws: "עצ" in ws, "life": lambda ws: "חיימ" in ws, "name of YHWH": lambda ws: any(a == "שמ" and b == "יהוה" for a, b in zip(ws, ws[1:]))}
def centre(vs):
    L = [sum(len(w) for w in ws) for _, ws in vs]; T = sum(L); acc = 0
    for i, l in enumerate(L):
        if acc + l > T / 2: return i
        acc += l
rows = []
for lab, f in MOT.items():
    hit = sum(f([w for _, ws in vs[max(0, centre(vs) - 2): centre(vs) + 3] for w in ws]) for vs in BK.values())
    null = [sum(f([w for _, ws in vs[i - 2: i + 3] for w in ws]) for vs in BK.values() for i in [rng.integers(2, len(vs) - 3)]) for _ in range(1000)]
    p = np.mean(np.array(null) >= hit); rows.append((p, lab, hit, np.mean(null)))
rows.sort(); m_ = len(rows)
for i, (p, lab, hit, mu) in enumerate(rows): print(f"   {lab:24s} centres {hit:2d} of {len(BK)}  random {mu:4.1f}  p = {p:.3f}{'  *' if p <= 0.05 * (i + 1) / m_ else ''}")
print("\n3. MYTH PASS (fixed motif list; 1 = present)")
def xml(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    return " ".join(nrm(t) for t in re.sub(r"<[^>]+>", " ", x).split())
GM = {"descent to the dead": r"\bαδ(ου|ησ|ην|η)\b|υποχθον|ερεβ|νεκυ", "death": r"\bθανατ|απεθαν|τεθνη|νεκρ", "mourning / weeping": r"κλαι|εκλαυσ|πενθ|θρην|οδυρ",
      "three days": r"τρισιν ημεραισ|τριτη ημερα|τριων ημερων|τρισ ημερ", "water / food of life": r"υδωρ ζων|υδατοσ ζωντοσ|αρτοσ τησ ζωησ|νεκταρ|αμβροσι",
      "rising / return": r"αναστασ|ανεστη|εγειρ|ηγερθη|επανηλθ|ανηλθεν|ανοδ", "substitute (one for another)": r"υπερ του λαου|αντι πολλων|ανθ εαυτ|αντιλυτρ|αντ αυτησ|αντ αυτου", "seven gates": r"επτα πυλ"}
EM = {"descent to the dead": r"underworld|nether world|land of no return", "death": r"\bdeath|\bdead\b|corpse|\bdied\b", "mourning / weeping": r"lament|wept|weep|mourn",
      "three days": r"three days", "water / food of life": r"life-giving|water of life|bread of life|living water", "rising / return": r"\barise|\brose\b|\breturn",
      "substitute (one for another)": r"substitute|in (her|his) place|die for the people", "seven gates": r"seven gates"}
TX = {}
TX["John (Greek)"] = (" ".join(w for v in SB.values() for w, _, _ in v), GM)
TX["Mark (Greek)"] = (" ".join(nrm(l.split()[4]) for l in open(glob.glob(os.path.join(SBL, "*-Mk-*"))[0], encoding="utf-8")), GM)
TX["Hymn to Demeter (Persephone)"] = (" ".join(xml(f) for f in glob.glob(os.path.join(GR, "perseus/data/tlg0013/tlg002/*grc*.xml"))), GM)
TX["Plutarch, Isis and Osiris"] = (" ".join(xml(f) for f in glob.glob(os.path.join(GR, "perseus/data/tlg0007/tlg089/*grc*.xml"))), GM)
lt = open(LIT, encoding="utf-8", errors="ignore").read(); a = lt.find("The brisk linear narrative"); TX["Inana's Descent (English)"] = (lt[a:a + 40000], EM)
TX["control: Hymn to Apollo"] = (" ".join(xml(f) for f in glob.glob(os.path.join(GR, "perseus/data/tlg0013/tlg003/*grc*.xml"))), GM)
TX["control: Hymn to Hermes"] = (" ".join(xml(f) for f in glob.glob(os.path.join(GR, "perseus/data/tlg0013/tlg004/*grc*.xml"))), GM)
gen = " ".join(nrm(l.split(maxsplit=1)[1]) for l in open(glob.glob(os.path.join(LXX, "*Genesis.txt"))[0], encoding="utf-8") if len(l.split(maxsplit=1)) == 2 and 37 <= int(l.split(".")[1]) <= 50)
TX["control: Genesis 37-50 (Joseph)"] = (gen, GM)
prof = {}
print(f"   {'text':32s} " + " ".join(f"{k[:9]:>9s}" for k in GM))
for lab, (txt, lex) in TX.items():
    if not txt.strip(): continue
    prof[lab] = [int(bool(re.search(lex[k], txt, flags=re.I))) for k in GM]; print(f"   {lab:32s} " + " ".join(f"{v:9d}" for v in prof[lab]))
J = np.array(prof["John (Greek)"])
for lab, v in prof.items():
    if lab != "John (Greek)": v = np.array(v); print(f"   shared with John: {lab:32s} {int((J & v).sum())} of {int(J.sum())} John motifs (Jaccard {(J & v).sum() / max(1, (J | v).sum()):.2f})")
out["myth"] = prof
json.dump(out, open(os.path.join(HERE, "round22_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
