#!/usr/bin/env python3
"""The whole Greek Bible, chapter by chapter, measured independently and regrouped by shape.

Corpus: Swete's Septuagint (with the deuterocanonical books) + SBLGNT, in Greek, so every chapter is
measured with the same tools.  Chapters under 100 words are skipped.
Per chapter (no outside information):
  sound   : syllables, mean vowel brightness, share of [o] vowels
  breath  : mean breath length (syllables between punctuation), pace change after the centre,
            mirror of breath lengths around the centre
  ring    : repeated words mirrored around the centre, as a z-score against 30 shuffles of word order
  chain   : staircase rate (a clause hands a word to the next)
  numbers : word count, syllable count and letter-value (isopsephy) total; divisibility by 7
  content : shares of light, water, breath, voice, sight vocabulary; 'I am'; divine names
Then:  (1) the numbers tests over all chapters; (2) a shape map (PCA + k-means on the standardized
features) that groups chapters by shape, ignoring canonical order; (3) book-level rings (chapter k vs
chapter n+1-k), with the known Daniel 2-7 ring as a check; (4) frame rings across the NT and the whole
Bible; (5) nearest Old Testament chapter for each Revelation chapter.
Usage: python3 bible_map.py <sblgnt dir> <lxx-swete/data>
"""
import collections, csv, glob, json, math, os, random, re, sys, unicodedata
import numpy as np
from scipy.stats import binomtest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL, LXX = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(8)
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
scache = {}
def sylinfo(raw):
    k = nrm(raw)
    if k not in scache:
        try: sy = E.parse_greek(k, "koine")[0]
        except Exception: sy = [{"nuc": ["a"]}]
        nuc = [s["nuc"][0].rstrip("ː") if s["nuc"] else "ə" for s in sy] or ["a"]
        scache[k] = (len(nuc), sum(E.VOWELS.get(n, (0, 1500, 0))[1] for n in nuc) / len(nuc), sum(n == "o" for n in nuc))
    return scache[k]
VAL = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800]))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
LEX = {"light": ("φωσ", "φωτ", "λυχν", "λαμπ"), "water": ("υδωρ", "υδατ", "θαλασσ", "ποταμ", "πηγ"), "breath": ("πνευμ", "πνοη", "ανεμ"),
       "voice": ("φωνη", "φωνησ", "λαλ", "λογο", "ρημα", "ειπ", "λεγ"), "sight": ("ιδ", "ειδ", "ορα", "θεα", "βλεπ", "οφθαλμ", "δοξα")}
GROUP = {}
for g, names in {"Law": "Genesis Exodus Leviticus Numeri Deuteronomium", "History": "Josue Judices Ruth Regnorum_I Regnorum_II Regnorum_III Regnorum_IV Paralipomenon_I Paralipomenon_II Esdras_A Esdras_B Esther Judith Tobias Machabaeorum_i Machabaeorum_ii Machabaeorum_iii Machabaeorum_iv",
                 "Poetry & Wisdom": "Psalmi Odae Proverbia Canticum Job Sapientia_Salomonis Ecclesiasticus Psalmi_Salomonis",
                 "Prophets": "Osee Amos Michaeas Joel Abdias Jonas Nahum Habacuc Sophonias Aggaeus Zacharias Malachias Isaias Jeremias Baruch Threni_seu_Lamentationes Epistula_Jeremiae Ezechiel Susanna_Theodotionis_versio Daniel_Theodotionis_versio Bel_et_Draco_Theodotionis_versio",
                 "Gospels": "Mt Mk Lk Jn", "Acts & Letters": "Ac Ro 1Co 2Co Ga Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud", "Revelation": "Re"}.items():
    for n in names.split(): GROUP[n] = g
chapters = collections.OrderedDict()   # (book, ch) -> list of raw tokens with trailing punctuation
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for line in open(f, encoding="utf-8"):
        p = line.split(maxsplit=1)
        if len(p) == 2: chapters.setdefault((b, p[0].split(".")[1]), []).append(p[1].strip())
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for line in open(f, encoding="utf-8"):
        p = line.split(); chapters.setdefault((b, str(int(p[0][2:4]))), []).append(p[3])
print(f"{len(chapters)} chapters in the Greek Bible")

def features(toks):
    words = [nrm(t) for t in toks]; idx = [i for i, w in enumerate(words) if w]; words = [words[i] for i in idx]; toks = [toks[i] for i in idx]
    info = [sylinfo(t) for t in toks]; S = [x[0] for x in info]; T = sum(S)
    bright = sum(x[1] * x[0] for x in info) / T; oshare = sum(x[2] for x in info) / T
    # breath groups
    groups, cur, gstart, acc = [], 0, [], 0
    for t, s in zip(toks, S):
        if cur == 0: gstart.append(acc)
        cur += s; acc += s
        if re.search(r"[,.·;:]$", t): groups.append(cur); cur = 0
    if cur: groups.append(cur)
    c = max(range(len(gstart)), key=lambda i: -abs(gstart[i] - T / 2)) if False else min(range(len(gstart)), key=lambda i: abs(gstart[i] - T / 2))
    pre, post = groups[:c], groups[c:]
    pace = (sum(post) / len(post)) / (sum(pre) / len(pre)) if pre and post else 1
    k = min(c, len(groups) - c - 1); mirror = 0.0
    if k >= 3:
        a, b = np.array(groups[c - k:c][::-1], float), np.array(groups[c + 1:c + 1 + k], float)
        if a.std() > 0 and b.std() > 0: mirror = float(np.corrcoef(a, b)[0, 1])
    # lexical ring z-score
    def ringscore(ws, Ss):
        tt = sum(Ss); pos, ac = collections.defaultdict(list), 0
        for w, s in zip(ws, Ss):
            if w not in STOP and len(w) > 3: pos[w[:6]].append(ac / tt)
            ac += s
        return sum(1 for v in pos.values() if len(v) >= 2 and v[-1] - v[0] > .2 and abs((v[0] + v[-1]) / 2 - .5) < .03)
    real = ringscore(words, S); sh = []
    pairs = list(zip(words, S))
    for _ in range(30):
        rng.shuffle(pairs); sh.append(ringscore([p[0] for p in pairs], [p[1] for p in pairs]))
    ring_z = (real - np.mean(sh)) / (np.std(sh) + 1e-9)
    # staircase
    clauses, cur2 = [], []
    for t, w in zip(toks, words):
        cur2.append(w)
        if re.search(r"[,.·;:]$", t): clauses.append(cur2); cur2 = []
    if cur2: clauses.append(cur2)
    links = sum(1 for a, b in zip(clauses, clauses[1:]) if {x[:5] for x in a[-3:] if x not in STOP and len(x) > 3} & {x[:5] for x in b[:4] if x not in STOP and len(x) > 3})
    stair = links / max(1, len(clauses) - 1)
    iso = sum(VAL.get(ch, 0) for w in words for ch in w)
    lex = {k_: sum(1 for w in words if w.startswith(v)) / len(words) for k_, v in LEX.items()}
    iam = sum(1 for a, b in zip(words, words[1:]) if a == "εγω" and b == "ειμι")
    divine = sum(1 for w in words if w.startswith(("θεο", "κυρι"))) / len(words)
    return dict(words=len(words), syllables=T, brightness=round(bright, 1), o_share=round(oshare, 3), breath_mean=round(T / len(groups), 2),
                pace_change=round(pace, 3), breath_mirror=round(mirror, 3), ring_z=round(float(ring_z), 2), staircase=round(stair, 3),
                isopsephy=iso, w7=len(words) % 7 == 0, s7=T % 7 == 0, i7=iso % 7 == 0, iam=iam, divine=round(divine, 4),
                **{k_: round(v, 4) for k_, v in lex.items()}), set(w[:6] for w in words if w not in STOP and len(w) > 3)

rows, vocab = [], {}
for (b, c), toks in chapters.items():
    if len(toks) < 100: continue
    f, v = features(toks); rows.append(dict(book=b, chapter=c, group=GROUP.get(b, "Other"), **f)); vocab[(b, c)] = v
print(f"{len(rows)} chapters measured")

# (1) numbers in letters ------------------------------------------------------------------------
print("\n(1) NUMBERS: chapters whose counts are divisible by 7 (chance = 14.3%)")
num = {}
for key, lab in (("w7", "word count"), ("s7", "syllable count"), ("i7", "letter-value total")):
    k = sum(r[key] for r in rows); bt = binomtest(k, len(rows), 1 / 7)
    num[lab] = dict(k=k, n=len(rows), share=round(k / len(rows), 4), p=bt.pvalue)
    print(f"   {lab:18s} {k} of {len(rows)} = {k / len(rows):.1%}; two-sided p = {bt.pvalue:.2f}")

# (2) shape map: PCA + k-means --------------------------------------------------------------------
FE = ["brightness", "o_share", "breath_mean", "pace_change", "breath_mirror", "ring_z", "staircase", "divine", "light", "water", "breath", "voice", "sight"]
X = np.array([[r[f] for f in FE] for r in rows], float); X = (X - X.mean(0)) / (X.std(0) + 1e-9)
U, Sv, Vt = np.linalg.svd(X, full_matrices=False); PC = X @ Vt[:2].T
print(f"\n(2) SHAPE MAP: first two components explain {100 * (Sv[:2] ** 2).sum() / (Sv ** 2).sum():.0f}% of variation")
for i in range(2):
    load = sorted(zip(FE, Vt[i]), key=lambda x: -abs(x[1]))[:4]; print(f"   component {i + 1}: " + ", ".join(f"{f} {w:+.2f}" for f, w in load))
K = 6; cent = X[rng.sample(range(len(X)), K)]
for _ in range(60):
    lab = np.argmin(((X[:, None, :] - cent[None]) ** 2).sum(2), 1)
    cent = np.array([X[lab == k].mean(0) if (lab == k).any() else cent[k] for k in range(K)])
clusters = []
for k in range(K):
    mem = [rows[i] for i in range(len(rows)) if lab[i] == k]; g = collections.Counter(m["group"] for m in mem)
    prof = sorted(zip(FE, cent[k]), key=lambda x: -abs(x[1]))[:3]
    ex = ", ".join(f"{m['book']} {m['chapter']}" for m in sorted(mem, key=lambda m: ((X[rows.index(m)] - cent[k]) ** 2).sum())[:5])
    clusters.append(dict(k=k, n=len(mem), groups=dict(g.most_common()), profile=[(f, round(float(v), 2)) for f, v in prof], examples=ex))
    print(f"   shape family {k + 1}: {len(mem)} chapters; marked by " + ", ".join(f"{f} {v:+.1f}" for f, v in prof) + f"; mostly {g.most_common(3)}; e.g. {ex}")
for i, r in enumerate(rows): r["pc1"], r["pc2"], r["family"] = round(float(PC[i, 0]), 3), round(float(PC[i, 1]), 3), int(lab[i]) + 1

# (3) book-level rings ---------------------------------------------------------------------------
def jac(a, b): return len(a & b) / max(1, len(a | b))
def ring(keys):
    n = len(keys); return np.mean([jac(vocab[keys[i]], vocab[keys[n - 1 - i]]) for i in range(n // 2)])
print("\n(3) BOOK RINGS: is chapter k most like chapter n+1-k? (500 shuffles of chapter order)")
books = collections.OrderedDict()
for r in rows: books.setdefault(r["book"], []).append((r["book"], r["chapter"]))
bring = {}
for b, keys in books.items():
    if len(keys) < 5: continue
    real = ring(keys); cnt = 0
    for _ in range(500):
        s = keys[:]; rng.shuffle(s); cnt += ring(s) >= real
    bring[b] = cnt / 500
sig = sorted((p, b) for b, p in bring.items() if p < 0.05)
print(f"   {len(sig)} of {len(bring)} books ringed beyond chance (expected {0.05 * len(bring):.1f}): {sig}")
dk = [("Daniel_Theodotionis_versio", str(c)) for c in range(2, 8)]
if all(k in vocab for k in dk):
    real = ring(dk); cnt = sum(ring(rng.sample(dk, 6)) >= real for _ in range(2000)) / 2000
    print(f"   check: Daniel 2-7 (known ring 2-7, 3-6, 4-5): p = {cnt:.3f}")
    bring["Daniel 2-7 check"] = cnt

# (4) frame rings across NT and the whole Bible ---------------------------------------------------
print("\n(4) FRAME RINGS: first and last chapters of a collection vs random chapter pairs")
order = [k for k in vocab]
def frame(keys, m=5):
    return np.mean([jac(vocab[keys[i]], vocab[keys[-1 - i]]) for i in range(m)])
allpairs = [jac(vocab[a], vocab[b]) for a, b in (rng.sample(order, 2) for _ in range(20000))]
for lab_, keys in (("Whole Greek Bible (Genesis 1-5 vs Revelation 18-22)", order), ("New Testament (Matthew 1-5 vs Revelation 18-22)", [k for k in order if GROUP.get(k[0]) in ("Gospels", "Acts & Letters", "Revelation")])):
    f_ = frame(keys); pr = np.mean(np.array(allpairs) >= f_)
    print(f"   {lab_}: mean similarity {f_:.3f}; random chapter pairs as similar: {pr:.1%}")
g1r = [(("Genesis", str(a)), ("Re", str(b))) for a, b in ((1, 22), (2, 22), (3, 22), (1, 21), (2, 21))]
print("   Genesis 1-3 vs Revelation 21-22: " + ", ".join(f"Gen {a[1]}~Rev {b[1]} {jac(vocab[a], vocab[b]):.3f} (top {np.mean(np.array(allpairs) >= jac(vocab[a], vocab[b])):.1%})" for a, b in g1r))

# (5) Revelation's nearest Old Testament chapters --------------------------------------------------
print("\n(5) REVELATION: nearest Old Testament chapter by shared vocabulary")
ot = [k for k in order if GROUP.get(k[0]) in ("Law", "History", "Poetry & Wisdom", "Prophets")]
near = {}
for k in [k for k in order if k[0] == "Re"]:
    best = max(ot, key=lambda o: jac(vocab[k], vocab[o])); near[k[1]] = f"{best[0]} {best[1]}"
print("   " + "; ".join(f"Rev {c} -> {v}" for c, v in near.items()))
nb = collections.Counter(v.split()[0] for v in near.values()); print("   books:", nb.most_common())

with open(os.path.join(HERE, "bible_chapters.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(dict(numbers=num, clusters=clusters, book_rings=bring, revelation_nearest=near, features=FE,
               loadings=[[(f, round(float(x), 3)) for f, x in zip(FE, Vt[i])] for i in range(2)]),
          open(os.path.join(HERE, "bible_map_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
