#!/usr/bin/env python3
"""Order tests: can sound and wording recover the order of the text, and does John work as a map of the whole?

Every test ignores the medieval chapter/verse numbers except where they are the thing being tested.
 1. SYLLABLES per book (spoken length, as the texts were written: without word spaces, which does not change
    syllable counts).
 2. NATURAL SEAMS in the continuous text. At every verse start, compare the ~150 words before with the ~150
    after: (a) by SOUND only (vowel brightness, o-share, word length, breath-pause rate); (b) by WORDING
    (stem overlap, the 'TextTiling' idea). Do the chapter starts (Langton, c. 1205) fall at seams more often
    than other verse starts?  Null: chapter starts would sit at the 50th percentile.
 3. CAN SOUND RECOVER A KNOWN ORDER?  For every book of 5+ chapters: is the real chapter order smoother
    (smaller steps between neighbours) than 2,000 shuffles?  This calibrates every order claim below.
 4. ANCIENT BOOK ORDERS: smoothness of each attested order (codices B, S, A; Hebrew Bible; Talmud Bava Batra
    14b; P46 for Paul) against random orders of the same books.
 5. KNOWN DISPUTED ORDERS: John 5/6 transposition; John 14:31 -> 18:1; Jeremiah LXX vs Hebrew order.
 6. JOHN AS A MAP: (a) John's own day-and-night curve (light words minus night/darkness words) laid over
    each book; (b) the whole canon's curve under each ancient order laid against John's; (c) the order a
    computer finds to fit John best, to show how easy (and how meaningless) a fitted order is.
Usage: python3 order_tests.py <sblgnt dir> <lxx-swete/data>
"""
import collections, glob, json, math, os, random, re, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL, LXX = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(21); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
sc = {}
def syl(k):
    if k not in sc:
        try: sy = E.parse_greek(k, "koine")[0]
        except Exception: sy = []
        nuc = [s["nuc"][0].rstrip("ː") if s["nuc"] else "ə" for s in sy] or ["a"]
        sc[k] = (len(nuc), sum(E.VOWELS.get(n, (0, 1500, 0))[1] for n in nuc) / len(nuc), sum(n == "o" for n in nuc) / len(nuc))
    return sc[k]
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
LIGHT = ("φωσ", "φωτ", "λυχν", "λαμπ", "πρωι", "ορθρ", "ηλιο")
DARK = ("σκοτ", "νυκτ", "νυξ", "εσπερ", "οψια", "γνοφ")

# ---------------------------------------------------------------- load: book -> list of verses (ch, vs, words)
BOOKS = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    vv = collections.OrderedDict()
    for line in open(f, encoding="utf-8"):
        p = line.split(maxsplit=1)
        if len(p) == 2:
            r = p[0].split("."); vv.setdefault((r[1], r[2]), []).append(p[1].strip())
    BOOKS[b] = [(c, v, ws) for (c, v), ws in vv.items()]
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]; vv = collections.OrderedDict()
    for line in open(f, encoding="utf-8"):
        p = line.split(); vv.setdefault((str(int(p[0][2:4])), str(int(p[0][4:6]))), []).append(p[3])
    BOOKS[b] = [(c, v, ws) for (c, v), ws in vv.items()]

# per-verse summaries: syllables, sound sums, stems, light/dark
V = {}
for b, verses in BOOKS.items():
    rows = []
    for c, v, raw in verses:
        S = br = o = pauses = nw = li = dk = 0; stems = collections.Counter()
        for t in raw:
            k = nrm(t)
            if not k: continue
            n, bri, osh = syl(k); S += n; br += bri * n; o += osh * n; nw += 1
            pauses += bool(re.search(r"[,.·;:]$", t))
            if k not in STOP and len(k) > 3: stems[k[:6]] += 1
            li += k.startswith(LIGHT); dk += k.startswith(DARK)
        if nw: rows.append(dict(ch=c, vs=v, S=S, br=br, o=o, p=pauses, nw=nw, stems=stems, li=li, dk=dk))
    V[b] = rows
print("loaded", len(V), "books,", sum(len(r) for r in V.values()), "verses")

# ---------------------------------------------------------------- 1. syllables per book
print("\n1. SPOKEN LENGTH (syllables) per book")
syl_book = {b: sum(r["S"] for r in rows) for b, rows in V.items()}
for b, s in sorted(syl_book.items(), key=lambda x: -x[1])[:8]: print(f"   {b:28s} {s:,}")
print(f"   ... whole Greek Bible: {sum(syl_book.values()):,} syllables; John {syl_book['Jn']:,}")
out["syllables_per_book"] = syl_book

# ---------------------------------------------------------------- 2. natural seams
def sound_vec(rows):
    S = sum(r["S"] for r in rows); nw = sum(r["nw"] for r in rows)
    return np.array([sum(r["br"] for r in rows) / S, sum(r["o"] for r in rows) / S, S / nw, sum(r["p"] for r in rows) / nw])
def cos(a, b):
    num = sum(v * b.get(k, 0) for k, v in a.items())
    return num / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())) + 1e-9)
allsound = np.array([sound_vec([r]) for rows in V.values() for r in rows if r["nw"] >= 5]); SD = allsound.std(0)
N = 150
seam = {}
for b, rows in V.items():
    cand = []
    for j in range(1, len(rows)):
        back, w = [], 0
        for r in reversed(rows[:j]):
            back.append(r); w += r["nw"]
            if w >= N: break
        fwd, w2 = [], 0
        for r in rows[j:]:
            fwd.append(r); w2 += r["nw"]
            if w2 >= N: break
        if w < N or w2 < N: continue
        snd = float(np.linalg.norm((sound_vec(back) - sound_vec(fwd)) / SD))
        A = sum((r["stems"] for r in back), collections.Counter()); B = sum((r["stems"] for r in fwd), collections.Counter())
        cand.append((j, rows[j]["ch"], rows[j]["vs"], snd, 1 - cos(A, B), rows[j]["vs"] == "1" and rows[j]["ch"] != rows[j - 1]["ch"]))
    if len(cand) > 20: seam[b] = cand
def pct(vals, x): return sum(v < x for v in vals) / len(vals)
print("\n2. NATURAL SEAMS: where do the medieval chapter starts fall among all verse starts? (50% = no better than any verse)")
res2 = {}
for idx, lab in ((3, "sound only"), (4, "wording")):
    P = []
    for b, cand in seam.items():
        vals = [c[idx] for c in cand]; P += [pct(vals, c[idx]) for c in cand if c[5]]
    m = float(np.mean(P)); z = (m - .5) / math.sqrt(1 / 12 / len(P))
    res2[lab] = dict(chapter_starts=len(P), mean_percentile=round(m, 3), z=round(z, 1))
    print(f"   {lab:11s}: {len(P)} chapter starts sit on average at the {m:.0%} percentile of seam strength (z = {z:.1f})")
# John: strongest wording seams
jc = sorted(seam["Jn"], key=lambda c: -c[4]); top = jc[:20]
print("   John's 20 strongest wording seams:", ", ".join(f"{c[1]}:{c[2]}" + ("*" if c[5] else "") for c in sorted(top)), "(* = a chapter start)")
res2["john_top_seams"] = [f"{c[1]}:{c[2]}" for c in sorted(top)]; res2["john_top_at_chapter_start"] = sum(c[5] for c in top)
res2["john_chapter_starts_share"] = round(sum(c[5] for c in seam["Jn"]) / len(seam["Jn"]), 3)
# misplaced chapter starts (wording seam in the bottom 10% of the book) and strong seams with no chapter start (top 2%)
NTB = [b for b in V if b[0].isdigit() or b in ("Mt", "Mk", "Lk", "Jn", "Ac", "Ro", "Ga", "Eph", "Php", "Col", "Tit", "Phm", "Heb", "Jas", "Jud", "Re")]
weak, strong = [], []
for b, cand in seam.items():
    vals = [c[4] for c in cand]
    for c in cand:
        p_ = pct(vals, c[4])
        if c[5] and p_ < .10: weak.append((b, f"{c[1]}:{c[2]}", round(p_, 2)))
        if not c[5] and p_ > .98 and b in NTB: strong.append((b, f"{c[1]}:{c[2]}", round(p_, 3)))
print(f"   chapter starts that cut through a unit (bottom 10% of their book): {len(weak)} of {sum(len([c for c in cs if c[5]]) for cs in seam.values())}")
print("      New Testament ones:", ", ".join(f"{b} {r}" for b, r, _ in weak if b in NTB))
print("   strongest New Testament seams with no chapter start (top 2%):", ", ".join(f"{b} {r}" for b, r, _ in strong))
res2["weak_chapter_starts"] = weak; res2["strong_unmarked_seams_NT"] = strong
out["seams"] = res2

# ---------------------------------------------------------------- 3. recover known chapter order
def chap_units(b):
    d = collections.OrderedDict()
    for r in V[b]: d.setdefault(r["ch"], []).append(r)
    return [(c, rows) for c, rows in d.items() if sum(r["nw"] for r in rows) >= 50]
def dist_fns(units):
    snd = [sound_vec(rows) / SD for _, rows in units]
    st = [sum((r["stems"] for r in rows), collections.Counter()) for _, rows in units]
    n = len(units); Ds = np.zeros((n, n)); Dw = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            Ds[i, j] = Ds[j, i] = np.linalg.norm(snd[i] - snd[j]); Dw[i, j] = Dw[j, i] = 1 - cos(st[i], st[j])
    return Ds, Dw
def smooth(D, order): return sum(D[a, b] for a, b in zip(order, order[1:]))
def perm_p(D, order, R=2000):
    real = smooth(D, order); idx = list(order); cnt = 0
    for _ in range(R):
        rng.shuffle(idx); cnt += smooth(D, idx) <= real
    return cnt / R
print("\n3. CAN SOUND OR WORDING RECOVER A KNOWN CHAPTER ORDER? (real order smoother than 95% of 2,000 shuffles)")
res3 = {"sound": [], "wording": []}
for b in V:
    units = chap_units(b)
    if len(units) < 5: continue
    Ds, Dw = dist_fns(units); o = list(range(len(units)))
    res3["sound"].append((b, perm_p(Ds, o))); res3["wording"].append((b, perm_p(Dw, o)))
for k in ("sound", "wording"):
    hits = sum(p < .05 for _, p in res3[k]); n = len(res3[k])
    print(f"   {k:8s}: real order beats chance in {hits} of {n} books (expected by luck {0.05 * n:.1f})")
out["recover_order"] = {k: dict(hits=sum(p < .05 for _, p in v), n=len(v), books=v) for k, v in res3.items()}

# ---------------------------------------------------------------- 4. ancient book orders
def book_units(names): return [(b, V[b]) for b in names]
TW = "Osee Amos Michaeas Joel Abdias Jonas Nahum Habacuc Sophonias Aggaeus Zacharias Malachias".split()
TW_H = "Osee Joel Amos Abdias Jonas Michaeas Nahum Habacuc Sophonias Aggaeus Zacharias Malachias".split()
LAW = "Genesis Exodus Leviticus Numeri Deuteronomium".split(); KG = "Regnorum_I Regnorum_II Regnorum_III Regnorum_IV".split()
DAN = "Daniel_Theodotionis_versio"
OT = {
 "Codex Vaticanus (B)": LAW + ["Josue", "Judices", "Ruth"] + KG + ["Paralipomenon_I", "Paralipomenon_II", "Esdras_A", "Esdras_B", "Psalmi", "Proverbia", "Canticum", "Job", "Sapientia_Salomonis", "Ecclesiasticus", "Esther", "Judith", "Tobias"] + TW + ["Isaias", "Jeremias", "Baruch", "Threni_seu_Lamentationes", "Epistula_Jeremiae", "Ezechiel", DAN],
 "Codex Alexandrinus (A)": LAW + ["Josue", "Judices", "Ruth"] + KG + ["Paralipomenon_I", "Paralipomenon_II"] + TW + ["Isaias", "Jeremias", "Baruch", "Threni_seu_Lamentationes", "Epistula_Jeremiae", "Ezechiel", DAN, "Esther", "Tobias", "Judith", "Esdras_A", "Esdras_B", "Machabaeorum_i", "Machabaeorum_ii", "Machabaeorum_iii", "Machabaeorum_iv", "Psalmi", "Odae", "Job", "Proverbia", "Canticum", "Sapientia_Salomonis", "Ecclesiasticus", "Psalmi_Salomonis"],
 "Hebrew Bible (Leningrad / printed)": LAW + ["Josue", "Judices"] + KG + ["Isaias", "Jeremias", "Ezechiel"] + TW_H + ["Psalmi", "Proverbia", "Job", "Canticum", "Ruth", "Threni_seu_Lamentationes", "Esther", DAN, "Esdras_B", "Paralipomenon_I", "Paralipomenon_II"],
 "Talmud, Bava Batra 14b": LAW + ["Josue", "Judices"] + KG + ["Jeremias", "Ezechiel", "Isaias"] + TW_H + ["Ruth", "Psalmi", "Job", "Proverbia", "Canticum", "Threni_seu_Lamentationes", DAN, "Esther", "Esdras_B", "Paralipomenon_I", "Paralipomenon_II"],
}
HEB = set(OT["Hebrew Bible (Leningrad / printed)"])
GOS = ["Mt", "Mk", "Lk", "Jn"]; PAUL = "Ro 1Co 2Co Ga Eph Php Col 1Th 2Th".split(); PAST = "1Ti 2Ti Tit Phm".split(); CATH = "Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud".split()
NT = {"Modern / Latin": GOS + ["Ac"] + PAUL + PAST + ["Heb"] + CATH + ["Re"],
      "Codex Alexandrinus (A) / Vaticanus (B)": GOS + ["Ac"] + CATH + PAUL + ["Heb"] + PAST + ["Re"],
      "Codex Sinaiticus": GOS + PAUL + ["Heb"] + PAST + ["Ac"] + CATH + ["Re"],
      "Western Gospel order (Bezae, W)": ["Mt", "Jn", "Lk", "Mk", "Ac"] + PAUL + PAST + ["Heb"] + CATH + ["Re"]}
PAUL_ORD = {"Modern": "Ro 1Co 2Co Ga Eph Php Col 1Th Heb".split(), "P46 (c. 200)": "Ro Heb 1Co 2Co Eph Ga Php Col 1Th".split()}
def order_test(orders, label):
    names = sorted(set.intersection(*[set(o) for o in orders.values()]))
    units = book_units(names); Ds, Dw = dist_fns(units); ix = {b: i for i, (b, _) in enumerate(units)}
    print(f"   {label} ({len(names)} books shared by all orders)")
    r = {}
    for lab, o in orders.items():
        oo = [ix[b] for b in o if b in ix]
        ps, pw = perm_p(Ds, oo, 4000), perm_p(Dw, oo, 4000)
        r[lab] = dict(sound_p=ps, wording_p=pw); print(f"      {lab:40s} smoother than random: sound p = {ps:.3f}, wording p = {pw:.3f}")
    return r
print("\n4. ANCIENT BOOK ORDERS: is each attested order smoother than random orders of the same books? (low p = flows better)")
out["book_orders"] = dict(OT=order_test(OT, "Old Testament"), OT_hebrew_books=order_test({k: [b for b in v if b in HEB] for k, v in OT.items()}, "Old Testament, Hebrew-canon books only"),
                          NT=order_test(NT, "New Testament"), Paul=order_test(PAUL_ORD, "Paul's letters"))

# ---------------------------------------------------------------- 5. disputed orders
print("\n5. DISPUTED ORDERS (score = total step size; smaller = smoother)")
units = chap_units("Jn"); Ds, Dw = dist_fns(units); ci = {c: i for i, (c, _) in enumerate(units)}
def seg(D, chs): return round(float(smooth(D, [ci[c] for c in chs])), 3)
r5 = {}
for lab, a, b in (("John 4-5-6-7 (as written) vs 4-6-5-7 (proposed swap)", ["4", "5", "6", "7"], ["4", "6", "5", "7"]),
                  ("John 14->15 (as written) vs 14->18 ('Rise, let us go' then 'he went out')", ["14", "15"], ["14", "18"])):
    r5[lab] = dict(as_written=dict(sound=seg(Ds, a), wording=seg(Dw, a)), alternative=dict(sound=seg(Ds, b), wording=seg(Dw, b)))
    print(f"   {lab}: sound {seg(Ds, a)} vs {seg(Ds, b)}; wording {seg(Dw, a)} vs {seg(Dw, b)}")
# Jeremiah: Swete prints the Greek order; Hebrew order moves the nations oracles (Greek 25:14-31) to the end
ju = chap_units("Jeremias"); Ds, Dw = dist_fns(ju); jix = {c: i for i, (c, _) in enumerate(ju)}
greek = [str(i) for i in range(1, 53)]
hebrew = [str(i) for i in range(1, 26)] + ["32"] + [str(i) for i in range(33, 52)] + [str(i) for i in range(26, 32)] + ["52"]
for lab, o in (("Jeremiah, Greek order", greek), ("Jeremiah, Hebrew order", hebrew)):
    oo = [jix[c] for c in o if c in jix]
    ps, pw = perm_p(Ds, oo), perm_p(Dw, oo); r5[lab] = dict(sound=round(float(smooth(Ds, oo)), 2), wording=round(float(smooth(Dw, oo)), 2), sound_p=ps, wording_p=pw)
    print(f"   {lab:24s} sound {smooth(Ds, oo):.2f} (p {ps:.3f}); wording {smooth(Dw, oo):.2f} (p {pw:.3f})")
out["disputed"] = r5

# ---------------------------------------------------------------- 6. John as a map: the day-and-night curve
K = 20
def curve(rows_seq, k=K):
    S = sum(r["S"] for r in rows_seq); bins = np.zeros(k); acc = 0
    for r in rows_seq:
        i = min(k - 1, int(k * acc / S)); bins[i] += r["li"] - r["dk"]; acc += r["S"]
    sm = np.convolve(bins, [1, 2, 1], "same") / 4
    return sm
john = curve(V["Jn"])
def corr(a, b): return float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else 0.0
print("\n6. JOHN AS A MAP: the light-minus-darkness curve")
print("   John, 20 slices of spoken time:", " ".join(f"{x:+.1f}" for x in john))
lm = [(r["ch"], r["vs"]) for r in V["Jn"] if r["dk"]]
print("   John's night/darkness verses:", ", ".join(f"{c}:{v}" for c, v in lm))
# (a) overlay on each book: correlation with John's curve; null by circularly shifting the book's curve
r6 = {}
for b, rows in V.items():
    if b == "Jn" or sum(r["li"] + r["dk"] for r in rows) < 8: continue
    c = curve(rows); real = corr(john, c)
    null = [corr(john, np.roll(c, s)) for s in range(1, K)] + [corr(john, c[rng.sample(range(K), K)]) for _ in range(300)]
    r6[b] = dict(r=round(real, 3), p=round(sum(x >= real for x in null) / len(null), 3))
best = sorted(r6.items(), key=lambda x: -x[1]["r"])[:10]
print(f"   books with enough light/dark words: {len(r6)}; whose curve matches John's beyond chance (p<.05): {sum(v['p'] < .05 for v in r6.values())} (luck ~{0.05 * len(r6):.1f})")
for b, v in best: print(f"      {b:28s} r = {v['r']:+.2f}  p = {v['p']:.3f}")
out["john_overlay_books"] = r6
# (b) whole canon under each ancient order vs John's curve
def canon_curve(order): return curve([r for b in order for r in V[b]])
FULL = {"Vaticanus OT + Modern NT": OT["Codex Vaticanus (B)"] + NT["Modern / Latin"],
        "Alexandrinus OT + Alexandrinus NT": OT["Codex Alexandrinus (A)"] + NT["Codex Alexandrinus (A) / Vaticanus (B)"],
        "Hebrew order + Modern NT": OT["Hebrew Bible (Leningrad / printed)"] + NT["Modern / Latin"],
        "Hebrew order + Sinaiticus NT": OT["Hebrew Bible (Leningrad / printed)"] + NT["Codex Sinaiticus"]}
print("   whole canon laid against John's curve (random book orders give the p):")
r6b = {}
for lab, o in FULL.items():
    real = corr(john, canon_curve(o)); null = []
    for _ in range(500):
        oo = o[:]; rng.shuffle(oo); null.append(corr(john, canon_curve(oo)))
    r6b[lab] = dict(r=round(real, 3), p=round(sum(x >= real for x in null) / len(null), 3)); print(f"      {lab:36s} r = {real:+.2f}  p = {r6b[lab]['p']:.3f}")
out["canon_vs_john"] = r6b
# (c) fitted order: hill-climb a book order to match John's curve (shows the danger of fitting)
names = NT["Modern / Latin"]; cur = names[:]; score = corr(john, canon_curve(cur))
for it in range(4000):
    i, j = rng.sample(range(len(cur)), 2); cand = cur[:]; cand[i], cand[j] = cand[j], cand[i]; s = corr(john, canon_curve(cand))
    if s > score: cur, score = cand, s
rand_best = []
for _ in range(5):   # fit the same NT to a random template curve, to show any shape can be fitted
    tmpl = np.convolve(np.array([rng.gauss(0, 1) for _ in range(K)]), [1, 2, 1], "same"); c2 = names[:]; s2 = corr(tmpl, canon_curve(c2))
    for it in range(4000):
        i, j = rng.sample(range(len(c2)), 2); cand = c2[:]; cand[i], cand[j] = cand[j], cand[i]; s = corr(tmpl, canon_curve(cand))
        if s > s2: c2, s2 = cand, s
    rand_best.append(round(s2, 3))
print(f"   NT books re-ordered by computer to fit John's curve: r = {score:+.2f}; order: {' '.join(cur)}")
print(f"   the same search fitting the NT to 5 RANDOM curves reached r = {rand_best}")
out["fitted_nt_order"] = dict(r=round(score, 3), order=cur, random_template_r=rand_best, modern_r=round(corr(john, canon_curve(names)), 3))
json.dump(out, open(os.path.join(HERE, "order_tests_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
