#!/usr/bin/env python3
"""Position resonance: connections at ANY fractional position, at several scales (no centre or mirror assumed).

Wherever two places share a rare phrase (two content stems in a row, found in at most 12 places in the whole
Greek Bible), we record its fractional position in each unit: pA in unit A, pB in unit B.  A 'connection' is
any (pA, pB) pairing, e.g. 7/16 in one book with 2/16 in another, that recurs more than chance allows.

Null: every unit's text is rotated by a random offset (positions mod 1).  This keeps all local clustering of
vocabulary and destroys only absolute placement, so a surviving cell means the PLACEMENT itself is meaningful.

Tests (each with Benjamini-Hochberg correction):
  MACRO (books)     A 16 x 16 grid of (pA, pB) for John against every book; hot cells are listed with their phrases.
                    Positive controls: Kings/Chronicles, Matthew/Mark and 2 Samuel/Psalms must light up.
  MESO (chapters)   The same grid at chapter scale for John's chapters against all chapters (8 x 8 cells).
  MICRO (verses)    For verses joined by a rare phrase: does the phrase sit at the same fraction of both verses
                    more than chance?  Same for letters: position of the phrase in letters within the verse.
  SAME-PLACE, MIRROR, RATIO  Global tendencies: |pA - pB|, |pA - (1 - pB)| and the distance of pA/pB to a simple
                    ratio a/b (b up to 8), all against the rotation null.
Usage: python3 position_resonance.py <sblgnt dir> <lxx-swete/data>
"""
import collections, glob, math, os, re, sys, json, unicodedata
import numpy as np
SBL, LXX = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(16); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ εαν αν οσ ουτοσ τουτο παντα πασ".split())
TOK = []    # (book, ch, vs, stem, letters_before_in_verse)
def add(book, rows):
    for c, v, raw in rows:
        w = nrm(raw)
        if w: TOK.append((book, c, v, w[:5] if (w not in STOP and len(w) > 3) else None, len(w)))
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    add(b, [(p[0].split(".")[1], p[0].split(".")[2], p[1]) for p in (l.split(maxsplit=1) for l in open(f, encoding="utf-8")) if len(p) == 2])
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    add(b, [(str(int(l[2:4])), str(int(l[4:6])), l.split()[3]) for l in open(f, encoding="utf-8")])
# positions: within book, within chapter, within verse (words and letters)
book_len = collections.Counter(t[0] for t in TOK); chap_len = collections.Counter((t[0], t[1]) for t in TOK); verse_tok = collections.defaultdict(list)
pos_b, pos_c, pos_v, pos_vl = [], [], [], []; cb = collections.Counter(); cc = collections.Counter()
for i, t in enumerate(TOK): verse_tok[(t[0], t[1], t[2])].append(i)
vstart = {}
for k, idx in verse_tok.items():
    L = sum(TOK[i][4] for i in idx); acc = 0
    for j, i in enumerate(idx): vstart[i] = (j / max(1, len(idx) - 1), acc / max(1, L)); acc += TOK[i][4]
for i, t in enumerate(TOK):
    pos_b.append(cb[t[0]] / book_len[t[0]]); cb[t[0]] += 1
    pos_c.append(cc[(t[0], t[1])] / chap_len[(t[0], t[1])]); cc[(t[0], t[1])] += 1
pos_b, pos_c = np.array(pos_b), np.array(pos_c)
# rare phrases: consecutive content stems (stop words skipped)
cont = [i for i, t in enumerate(TOK) if t[3]]
occ = collections.defaultdict(list)
for a, b in zip(cont, cont[1:]):
    if TOK[a][0] == TOK[b][0] and b - a <= 3: occ[(TOK[a][3], TOK[b][3])].append(a)
rare = {k: v for k, v in occ.items() if 2 <= len(v) <= 12 and len({TOK[i][0] for i in v}) >= 2}
PA, PB, BA, BB, IA, IB = [], [], [], [], [], []
for k, v in rare.items():
    for x in range(len(v)):
        for y in range(x + 1, len(v)):
            i, j = v[x], v[y]
            if TOK[i][0] != TOK[j][0]: IA.append(i); IB.append(j)
IA, IB = np.array(IA), np.array(IB)
books = sorted(book_len); bid = {b: n for n, b in enumerate(books)}
BA = np.array([bid[TOK[i][0]] for i in IA]); BB = np.array([bid[TOK[j][0]] for j in IB])
print(f"{len(rare):,} rare phrases shared across books -> {len(IA):,} cross-book occurrence pairs")

def grid_test(sel, posA, posB, unitA, unitB, nunits, G, R=400, label=""):
    """sel: mask of pairs; positions in [0,1); units for rotation. Returns list of (z, p, cellA, cellB, count)."""
    a, b, ua, ub = posA[sel], posB[sel], unitA[sel], unitB[sel]
    obs = np.zeros((G, G)); np.add.at(obs, (np.minimum((a * G).astype(int), G - 1), np.minimum((b * G).astype(int), G - 1)), 1)
    null = np.zeros((R, G, G))
    for r in range(R):
        off = rng.random(nunits); aa = (a + off[ua]) % 1; bb = (b + off[ub]) % 1
        np.add.at(null[r], (np.minimum((aa * G).astype(int), G - 1), np.minimum((bb * G).astype(int), G - 1)), 1)
    p = ((null >= obs).sum(0) + 1) / (R + 1); mu, sd = null.mean(0), null.std(0) + 1e-9
    return obs, p, (obs - mu) / sd
def bh(pvals, q=0.10):
    flat = np.sort(pvals.ravel()); m = len(flat); ok = [flat[i] for i in range(m) if flat[i] <= q * (i + 1) / m]
    return max(ok) if ok else -1

# ---- controls: known parallels should light up
print("\nCONTROLS (parallel texts must produce hot cells)")
for A, B in (("Regnorum_III", "Paralipomenon_II"), ("Mt", "Mk"), ("Regnorum_II", "Psalmi")):
    sel = ((BA == bid[A]) & (BB == bid[B])) | ((BA == bid[B]) & (BB == bid[A]))
    pa = np.where(BA[sel] == bid[A], pos_b[IA[sel]], pos_b[IB[sel]]); pb = np.where(BA[sel] == bid[A], pos_b[IB[sel]], pos_b[IA[sel]])
    ua = np.zeros(sel.sum(), int); ub = np.ones(sel.sum(), int)
    obs, p, z = grid_test(np.ones(sel.sum(), bool), pa, pb, ua, ub, 2, 8)
    cut = bh(p); hot = [(i, j, int(obs[i, j])) for i in range(8) for j in range(8) if p[i, j] <= cut]
    print(f"   {A} ~ {B}: {sel.sum()} pairs; hot cells (eighths, A->B): {hot[:8]}{' ...' if len(hot) > 8 else ''}  ({len(hot)} survive correction)")
    out.setdefault("controls", {})[f"{A}~{B}"] = hot

# ---- MACRO: John against every book, 16 x 16
print("\nMACRO: John against every book (16 x 16 grid of positions; corrected over all books and cells)")
J = bid["Jn"]; allp, cells = [], []
for B in books:
    if B == "Jn": continue
    sel = ((BA == J) & (BB == bid[B])) | ((BA == bid[B]) & (BB == J))
    if sel.sum() < 30: continue
    pj = np.where(BA[sel] == J, pos_b[IA[sel]], pos_b[IB[sel]]); po = np.where(BA[sel] == J, pos_b[IB[sel]], pos_b[IA[sel]])
    obs, p, z = grid_test(np.ones(sel.sum(), bool), pj, po, np.zeros(sel.sum(), int), np.ones(sel.sum(), int), 2, 16, R=300)
    for i in range(16):
        for j in range(16):
            if obs[i, j] >= 3: allp.append(p[i, j]); cells.append((B, i, j, int(obs[i, j]), float(z[i, j]), sel))
cut = bh(np.array(allp)); hits = [c for c, pp in zip(cells, allp) if pp <= cut]
print(f"   cells tested: {len(allp)}; surviving correction: {len(hits)}")
macro = []
for B, i, j, n, z, sel in sorted(hits, key=lambda c: -c[4])[:25]:
    # phrases in that cell
    idxA = np.where(BA[sel] == J, IA[sel], IB[sel]); idxB = np.where(BA[sel] == J, IB[sel], IA[sel])
    m = [(a, b) for a, b in zip(idxA, idxB) if int(pos_b[a] * 16) == i and int(pos_b[b] * 16) == j][:3]
    ex = "; ".join(f"Jn {TOK[a][1]}:{TOK[a][2]} ~ {B} {TOK[b][1]}:{TOK[b][2]} ({TOK[a][3]}-)" for a, b in m)
    macro.append(dict(book=B, john_sixteenth=i, other_sixteenth=j, n=n, z=round(z, 1), examples=ex))
    print(f"   John {i:2d}/16 ~ {B:22s} {j:2d}/16   n={n:2d} z={z:4.1f}   e.g. {ex}")
out["macro"] = macro

# ---- SAME-PLACE / MIRROR / RATIO (global, all book pairs)
print("\nGLOBAL TENDENCIES across all book pairs (against the rotation null)")
a, b = pos_b[IA], pos_b[IB]
def stats(a, b):
    same = np.mean(np.minimum(abs(a - b), 1 - abs(a - b))); mir = np.mean(abs(a - (1 - b)))
    r = np.maximum(a, b) / np.maximum(np.minimum(a, b), 1e-3); fr = np.array([x / y for y in range(1, 9) for x in range(y, 9 * y) if x / y <= 8])
    rat = np.mean(np.min(abs(r[:, None] - fr[None, :]) / fr[None, :], axis=1)) if len(r) < 200000 else np.nan
    return same, mir, rat
sub = rng.choice(len(a), min(len(a), 60000), replace=False); a_s, b_s, ua, ub = a[sub], b[sub], BA[sub], BB[sub]
real = stats(a_s, b_s); nulls = []
for _ in range(100):
    off = rng.random(len(books)); nulls.append(stats((a_s + off[ua]) % 1, (b_s + off[ub]) % 1))
nulls = np.array(nulls)
for k, lab in enumerate(("same place |pA-pB|", "mirror |pA-(1-pB)|", "simple ratio pA/pB")):
    print(f"   {lab:22s} observed {real[k]:.4f}; null {nulls[:, k].mean():.4f}; share of null as small: {np.mean(nulls[:, k] <= real[k]):.2f}")
out["global"] = dict(observed=list(map(float, real)), null=nulls.mean(0).tolist())

# ---- MICRO: position within the verse (words and letters)
print("\nMICRO: does a shared rare phrase sit at the same fraction of both verses?")
qa = np.array([vstart[i][0] for i in IA]); qb = np.array([vstart[j][0] for j in IB]); la = np.array([vstart[i][1] for i in IA]); lb = np.array([vstart[j][1] for j in IB])
for lab, x, y in (("by words", qa, qb), ("by letters", la, lb)):
    d = np.mean(abs(x - y)); nd = [np.mean(abs(x - rng.permutation(y))) for _ in range(300)]
    print(f"   {lab:10s} mean |qA - qB| = {d:.4f}; random pairing {np.mean(nd):.4f}; p = {np.mean(np.array(nd) <= d):.3f}")
    out[f"micro_{lab}"] = dict(obs=float(d), null=float(np.mean(nd)))
json.dump(out, open(os.path.join(HERE, "position_resonance_results.json"), "w"), ensure_ascii=False, indent=1, default=str)

# ======================================================================================================
# VERSION 2 (calibrated): one link per chapter pair; null = chapter order shuffled inside each book
print("\n" + "=" * 90 + "\nVERSION 2: one link per chapter pair; null = chapters reshuffled inside each book")
chap_of = [(t[0], t[1]) for t in TOK]
book_chaps = collections.OrderedDict()
for k in chap_len: book_chaps.setdefault(k[0], []).append(k)
def chapter_positions(order):
    """order: book -> list of chapter keys; returns dict chapter -> (start fraction, length fraction)"""
    d = {}
    for b, chs in order.items():
        acc = 0
        for c in chs: d[c] = (acc / book_len[b], chap_len[c] / book_len[b]); acc += chap_len[c]
    return d
links = collections.defaultdict(list)
for i, j in zip(IA, IB):
    links[(chap_of[i], chap_of[j])].append((pos_c[i], pos_c[j]))
L = [(a, b, float(np.mean([x for x, _ in v])), float(np.mean([y for _, y in v]))) for (a, b), v in links.items()]
print(f"   {len(L):,} chapter-pair links (from {len(IA):,} phrase pairs)")
def place(order, sel):
    cp = chapter_positions(order)
    return np.array([cp[a][0] + qa * cp[a][1] for a, b, qa, qb in sel]), np.array([cp[b][0] + qb * cp[b][1] for a, b, qa, qb in sel])
def grid2(sel, G, R=300):
    a, b = place(book_chaps, sel); obs = np.zeros((G, G)); np.add.at(obs, (np.minimum((a * G).astype(int), G - 1), np.minimum((b * G).astype(int), G - 1)), 1)
    null = np.zeros((R, G, G))
    for r in range(R):
        order = {bk: list(np.array(chs, dtype=object)[rng.permutation(len(chs))]) for bk, chs in book_chaps.items()}
        order = {bk: [tuple(x) for x in v] for bk, v in order.items()}
        aa, bb = place(order, sel); np.add.at(null[r], (np.minimum((aa * G).astype(int), G - 1), np.minimum((bb * G).astype(int), G - 1)), 1)
    return obs, ((null >= obs).sum(0) + 1) / (R + 1), (obs - null.mean(0)) / (null.std(0) + 1e-9)
print("   CONTROLS")
for A, B in (("Regnorum_III", "Paralipomenon_II"), ("Regnorum_IV", "Paralipomenon_II"), ("Mt", "Mk"), ("Regnorum_II", "Psalmi")):
    sel = [(a, b, qa, qb) if a[0] == A else (b, a, qb, qa) for a, b, qa, qb in L if {a[0], b[0]} == {A, B}]
    obs, p, z = grid2(sel, 8); cut = bh(p); hot = [(i, j, int(obs[i, j])) for i in range(8) for j in range(8) if p[i, j] <= cut]
    print(f"      {A} ~ {B}: {len(sel)} links; hot cells (eighths A,B,n): {hot[:10]} ({len(hot)} survive)")
    out.setdefault("controls_v2", {})[f"{A}~{B}"] = hot
print("   JOHN against every book (8 x 8; corrected over all cells)")
allp, cells = [], []
for B in books:
    if B == "Jn": continue
    sel = [(a, b, qa, qb) if a[0] == "Jn" else (b, a, qb, qa) for a, b, qa, qb in L if {a[0], b[0]} == {"Jn", B}]
    if len(sel) < 15: continue
    obs, p, z = grid2(sel, 8, R=200)
    for i in range(8):
        for j in range(8):
            if obs[i, j] >= 3: allp.append(p[i, j]); cells.append((B, i, j, int(obs[i, j]), float(z[i, j]), sel))
cut = bh(np.array(allp)); hits = [c for c, pp in zip(cells, allp) if pp <= cut]
print(f"      cells tested {len(allp)}; surviving correction: {len(hits)}")
v2 = []
for B, i, j, n, z, sel in sorted(hits, key=lambda c: -c[4]):
    a, b = place(book_chaps, sel); ex = [f"Jn {s[0][1]} ~ {B} {s[1][1]}" for s, x, y in zip(sel, a, b) if int(x * 8) == i and int(y * 8) == j][:4]
    v2.append(dict(book=B, john_eighth=i, other_eighth=j, n=n, z=round(z, 1), chapters=ex)); print(f"      John {i}/8 ~ {B:24s} {j}/8  n={n} z={z:.1f}  {', '.join(ex)}")
out["john_v2"] = v2
json.dump(out, open(os.path.join(HERE, "position_resonance_results.json"), "w"), ensure_ascii=False, indent=1, default=str)

# ---- VERSION 3: whole-pattern tests (any shape): order correlation and mutual information of positions
print("\n" + "=" * 90 + "\nVERSION 3: any relation between positions (Spearman rho; mutual information on an 8x8 grid); null = chapter shuffles")
def rank(x): return np.argsort(np.argsort(x))
def mi(a, b, G=8):
    h = np.zeros((G, G)); np.add.at(h, (np.minimum((a * G).astype(int), G - 1), np.minimum((b * G).astype(int), G - 1)), 1); p = h / h.sum()
    pa, pb = p.sum(1, keepdims=True), p.sum(0, keepdims=True); nz = p > 0
    return float((p[nz] * np.log(p[nz] / (pa @ pb)[nz])).sum())
def whole(sel, R=300):
    a, b = place(book_chaps, sel); rho = float(np.corrcoef(rank(a), rank(b))[0, 1]); m = mi(a, b); nr, nm = [], []
    for _ in range(R):
        order = {bk: [chs[k] for k in rng.permutation(len(chs))] for bk, chs in book_chaps.items()}
        aa, bb = place(order, sel); nr.append(abs(np.corrcoef(rank(aa), rank(bb))[0, 1])); nm.append(mi(aa, bb))
    return rho, (np.sum(np.array(nr) >= abs(rho)) + 1) / (R + 1), m, (np.sum(np.array(nm) >= m) + 1) / (R + 1)
print("   CONTROLS")
for A, B in (("Regnorum_III", "Paralipomenon_II"), ("Regnorum_IV", "Paralipomenon_II"), ("Mt", "Mk"), ("Mt", "Lk"), ("Regnorum_II", "Psalmi")):
    sel = [(a, b, qa, qb) if a[0] == A else (b, a, qb, qa) for a, b, qa, qb in L if {a[0], b[0]} == {A, B}]
    r, pr, m, pm = whole(sel); print(f"      {A:16s} ~ {B:16s} links {len(sel):4d}  rho {r:+.2f} (p {pr:.3f})   MI {m:.3f} (p {pm:.3f})")
print("   JOHN against every book (Benjamini-Hochberg over books)")
rows3 = []
for B in books:
    if B == "Jn": continue
    sel = [(a, b, qa, qb) if a[0] == "Jn" else (b, a, qb, qa) for a, b, qa, qb in L if {a[0], b[0]} == {"Jn", B}]
    if len(sel) >= 15: r, pr, m, pm = whole(sel, 200); rows3.append((B, len(sel), r, pr, m, pm))
for field, lab in ((3, "order (rho)"), (5, "any shape (MI)")):
    ps = sorted(rows3, key=lambda x: x[field]); m_ = len(ps); keep = [x for i, x in enumerate(ps, 1) if x[field] <= 0.10 * i / m_]
    keep = ps[:max([i for i, x in enumerate(ps, 1) if x[field] <= 0.10 * i / m_], default=0)]
    print(f"      {lab}: {len(keep)} books survive: " + ", ".join(f"{x[0]} (rho {x[2]:+.2f}, MI p {x[5]:.3f}, rho p {x[3]:.3f})" for x in keep[:12]))
    print(f"         strongest uncorrected: " + ", ".join(f"{x[0]} p={x[field]:.3f}" for x in ps[:6]))
out["v3_john"] = rows3
json.dump(out, open(os.path.join(HERE, "position_resonance_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
