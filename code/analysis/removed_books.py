#!/usr/bin/env python3
"""Where do the books outside the Protestant canon sit among the books of the Greek Bible?

Corpus: Swete's Septuagint (CC BY-SA, via nathans/lxx-swete) + SBLGNT (MorphGNT).
Two measures, fixed before looking at the results:
  style   = Burrows' Delta on the 150 most frequent words (function-word profile)
  content = TF-IDF cosine on the remaining vocabulary (shared distinctive words)
Test: is a removed book's nearest canonical neighbour in the section where the
ancient Greek Bible placed it?  Baseline: the same question for canonical books.
Usage: python3 -I removed_books.py <lxx-swete/data> <sblgnt dir>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np

LXX, NT = sys.argv[1], sys.argv[2]


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    w = re.sub(r"[^α-ως]", "", w)
    return w.replace("ς", "σ")


books = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    name = os.path.basename(f)[3:-4]
    ws = []
    for line in open(f, encoding="utf-8"):
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            w = norm(parts[1])
            if w: ws.append(w)
    books[name] = ws
nt_names = {}
prologue = []
for f in sorted(glob.glob(os.path.join(NT, "*-morphgnt.txt"))):
    name = "NT_" + os.path.basename(f).split("-")[1]
    ws = []
    for line in open(f, encoding="utf-8"):
        c = line.split()
        w = norm(c[5]); ws.append(w)
        if name == "NT_Jn" and c[0][:4] == "0401" and int(c[0][4:]) <= 18: prologue.append(w)
    books[name] = ws

# Drop Old Greek duplicates of Daniel-group books (keep Theodotion, the text the church read)
for k in ("Susanna_translatio_Graeca", "Daniel_translatio_Graeca", "Bel_et_Draco_translatio_Graeca"):
    books.pop(k, None)

SECTION = {  # traditional placement (LXX order as in Swete), by section
    "Law": ["Genesis", "Exodus", "Leviticus", "Numeri", "Deuteronomium"],
    "History": ["Josue", "Judices", "Ruth", "Regnorum_I", "Regnorum_II", "Regnorum_III", "Regnorum_IV",
                "Paralipomenon_I", "Paralipomenon_II", "Esdras_A", "Esdras_B", "Esther", "Judith", "Tobias",
                "Machabaeorum_i", "Machabaeorum_ii", "Machabaeorum_iii", "Machabaeorum_iv"],
    "Poetry/Wisdom": ["Psalmi", "Odae", "Proverbia", "Canticum", "Job", "Sapientia_Salomonis", "Ecclesiasticus",
                      "Psalmi_Salomonis"],
    "Prophets": ["Osee", "Amos", "Michaeas", "Joel", "Abdias", "Jonas", "Nahum", "Habacuc", "Sophonias", "Aggaeus",
                 "Zacharias", "Malachias", "Isaias", "Jeremias", "Baruch", "Threni_seu_Lamentationes",
                 "Epistula_Jeremiae", "Ezechiel", "Susanna_Theodotionis_versio", "Daniel_Theodotionis_versio",
                 "Bel_et_Draco_Theodotionis_versio"],
}
REMOVED = ["Esdras_A", "Judith", "Tobias", "Machabaeorum_i", "Machabaeorum_ii", "Machabaeorum_iii",
           "Machabaeorum_iv", "Odae", "Sapientia_Salomonis", "Ecclesiasticus", "Psalmi_Salomonis", "Baruch",
           "Epistula_Jeremiae", "Susanna_Theodotionis_versio", "Bel_et_Draco_Theodotionis_versio"]
SEC = {b: s for s, bs in SECTION.items() for b in bs}
for b in books:
    if b.startswith("NT_"): SEC[b] = "NT"
names = list(books)
CANON_OT = [b for b in names if b in SEC and SEC[b] != "NT" and b not in REMOVED]

# ---------- style: Burrows' Delta --------------------------------------------
tot = collections.Counter(w for b in names for w in books[b])
mfw = [w for w, _ in tot.most_common(150)]
F = np.array([[collections.Counter(books[b])[w] / len(books[b]) for w in mfw] for b in names])
Z = (F - F.mean(0)) / (F.std(0) + 1e-12)
delta = np.abs(Z[:, None, :] - Z[None, :, :]).mean(2)

# ---------- content: TF-IDF cosine (excluding the 150 MFW) --------------------
df = collections.Counter()
for b in names: df.update(set(books[b]))
N = len(names)
vocab = [w for w in df if w not in set(mfw) and df[w] >= 2]
vi = {w: i for i, w in enumerate(vocab)}


def tfidf(ws):
    v = np.zeros(len(vocab)); c = collections.Counter(ws)
    for w, k in c.items():
        if w in vi: v[vi[w]] = (1 + math.log(k)) * math.log(N / df[w])
    return v / (np.linalg.norm(v) + 1e-12)


T = np.array([tfidf(books[b]) for b in names])
cos = T @ T.T


def nearest(b, pool, mat, smaller_is_closer):
    i = names.index(b)
    cand = [(mat[i, names.index(c)], c) for c in pool if c != b]
    return sorted(cand, reverse=not smaller_is_closer)


def label(b): return b.replace("_Theodotionis_versio", "").replace("NT_", "NT ")


out = {"removed": {}, "baseline": {}}
# canonical OT baseline: is nearest canonical neighbour in same section?
for name_, mat, small in (("style", delta, True), ("content", cos, False)):
    hits = sum(SEC[nearest(b, CANON_OT, mat, small)[0][1]] == SEC[b] for b in CANON_OT)
    out["baseline"][name_] = f"{hits}/{len(CANON_OT)}"
print("Baseline (canonical OT books whose nearest canonical neighbour is in their own section):", out["baseline"])
print()
for b in REMOVED:
    st = nearest(b, CANON_OT, delta, True)[:3]
    co = nearest(b, CANON_OT, cos, False)[:3]
    ntc = nearest(b, [x for x in names if x.startswith("NT_")], cos, False)[:3]
    ok_s = SEC[st[0][1]] == SEC[b]; ok_c = SEC[co[0][1]] == SEC[b]
    out["removed"][b] = dict(placed=SEC[b], style=[(label(c), round(float(v), 3)) for v, c in st],
                             content=[(label(c), round(float(v), 3)) for v, c in co],
                             nt=[(label(c), round(float(v), 3)) for v, c in ntc], words=len(books[b]),
                             style_match=bool(ok_s), content_match=bool(ok_c))
    print(f"{label(b):22s} [{SEC[b]:13s}] {len(books[b]):6d}w  style: {', '.join(label(c) for _, c in st):45s} "
          f"content: {', '.join(label(c) for _, c in co):45s} NT: {', '.join(label(c) for _, c in ntc)}"
          f"  {'S' if ok_s else '-'}{'C' if ok_c else '-'}")
rs = sum(v["style_match"] for v in out["removed"].values()); rc = sum(v["content_match"] for v in out["removed"].values())
print(f"\nRemoved books whose nearest canonical neighbour is in their traditional section: style {rs}/{len(REMOVED)}, content {rc}/{len(REMOVED)}")

# ---------- John's prologue against every OT book (canonical + removed) ----------
pv = tfidf(prologue)
ot_all = [b for b in names if not b.startswith("NT_")]
rank = sorted(((float(pv @ T[names.index(b)]), b) for b in ot_all), reverse=True)
print("\nOT books closest to John 1:1-18 by distinctive vocabulary:")
for k, (v, b) in enumerate(rank[:10], 1):
    print(f"  {k:2d}. {label(b):25s} {v:.3f} {'(removed)' if b in REMOVED else ''}")
out["prologue_rank"] = [(label(b), round(v, 3), b in REMOVED) for v, b in rank]

# rare words the prologue shares with each removed book (word in <= 6 books of the whole corpus)
print("\nRare prologue words shared with removed books (word occurs in <=6 books overall):")
pset = set(prologue)
rare = {}
for b in REMOVED:
    sh = sorted(w for w in pset & set(books[b]) if df[w] <= 6)
    if sh: rare[label(b)] = sh; print(f"  {label(b):22s} {' '.join(sh)}")
out["prologue_rare_shared"] = rare

# famous link words: where do they occur?
for w in ["απαυγασμα", "κατεσκηνωσεν", "κατεσκηνωσα", "σκηνωσον", "μονογενησ", "μονογενη", "λογοσ"]:
    occ = [label(b) for b in names if w in books[b]]
    print(f"  {w:14s} in {len(occ):2d} books: {', '.join(occ[:12])}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "removed_books_results.json"), "w"),
          ensure_ascii=False, indent=1)
