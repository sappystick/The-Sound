"""Part 2. Acrostic detector: Hebrew Bible (verse and half-verse initials), Greek OT (Swete LXX),
Greek NT (SBLGNT), and Greek name acrostics, with the Sibylline Oracles 8.217-250 as Greek control.

Hypotheses and rules (fixed before running):
A. Alphabetic chain score of a chapter = the longest chain of units (verses, or half-verses split at
   athnach / 'ole) whose initial letters walk up the alphabet: each next letter is +1, or +2 (one
   letter missing, e.g. waw in Ps 25/34, nun in Ps 145), with the pe/ayin order allowed either way
   (Lam 2-4); consecutive chain units at most G=9 units apart (Ps 119 has 8 verses per letter).
   Psalm superscriptions: the first unit of a Psalm may use the initial of any of its first 3 words
   (applied to every Psalm, and kept with the unit when shuffled).
   Null: shuffle the units of the chapter (letters stay with their unit); p = (1+#>=obs)/(N+1),
   200 shuffles, extended to 20000 when p < 0.05. One test per chapter per unit type.
   Positive controls (scholarship): Ps 9-10, 25, 34, 37, 111, 112, 119, 145; Lam 1-4; Prov 31:10-31;
   Nahum 1:2-8 (partial). Negative control: Lam 5 (22 verses, not alphabetic).
B. Greek: the same detector with the 24-letter alphabet on LXX and NT chapters (verse initials).
C. Name acrostics: count runs of consecutive verse initials (within a book) spelling
   ΙΧΘΥΣ, ΙΗΣΟΥΣ, ΧΡΙΣΤΟΣ, ΙΩΑΝΝΗΣ, ΘΕΟΣ, ΚΥΡΙΟΣ, ΛΟΓΟΣ, ΣΩΤΗΡ in LXX, NT and the Sibylline Oracles
   (line initials). Null: 500 within-book shuffles of verse (line) order. Positive control: the
   34-line acrostic ΙΗΣΟΥΣ ΧΡΕΙΣΤΟΣ ΘΕΟΥ ΥΙΟΣ ΣΩΤΗΡ ΣΤΑΥΡΟΣ (Sib. Or. 8.217-250), read from
   Constantine's Oration to the Saints 18 (Heikel 1902) where all 34 lines are quoted.
D. Vertical words: dictionary words (SBLGNT forms+lemmas, length >= 5) read as consecutive verse
   initials in the NT and LXX, against 200 within-book verse shuffles.

Usage: python3 acrostic_scan.py <texts_dir> <out_json>
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

import textlib as T

G = 9


def _chain(sets, gap):
    n = len(sets)
    best = [dict() for _ in range(n)]  # unit -> {letter: chain length ending here}
    top = 0
    for i in range(n):
        bi = best[i]
        lo = max(0, i - gap)
        for a in sets[i]:
            L = 1
            for j in range(lo, i):
                for b, lb in best[j].items():
                    d = a - b
                    if (d == 1 or d == 2) and lb + 1 > L:
                        L = lb + 1
            if L > bi.get(a, 0):
                bi[a] = L
            if L > top:
                top = L
    return top


def chain_score(sets, nalpha, swap_pair=None, gap=G):
    """Longest alphabet-walking chain (see docstring). With swap_pair=(i, j) the chain is also
    scored on the alphabet with letters i and j in reversed order (pe before ayin), max taken."""
    s = _chain(sets, gap)
    if swap_pair is not None:
        i, j = swap_pair
        m = {i: j, j: i}
        sw = [tuple(m.get(x, x) for x in u) for u in sets]
        s = max(s, _chain(sw, gap))
    return s


def perm_p(sets, nalpha, swap, rng, n0=200, nmax=20000):
    obs = chain_score(sets, nalpha, swap)
    ge = 0
    n = 0
    sets = list(sets)
    target = n0
    while n < target:
        idx = rng.permutation(len(sets))
        s = [sets[k] for k in idx]
        if chain_score(s, nalpha, swap) >= obs:
            ge += 1
        n += 1
        if n == target and target < nmax and (1 + ge) / (n + 1) < 0.05 and ge < 20:
            target = nmax
    return obs, (1 + ge) / (n + 1), n


def heb_units(verses):
    """chapter -> (verse_units, half_units); each unit = tuple of candidate letter indices."""
    idx = {c: i for i, c in enumerate(T.HEB_ALPHA)}
    ch = defaultdict(lambda: ([], [], []))
    for v in verses:
        ws = [w for w in v["words"] if w["cons"]]
        if not ws:
            continue
        key = (v["book"], v["ch"])
        first_words = ws[:3] if (v["book"] == "Ps" and v["v"] == 1) else ws[:1]
        cand = tuple(sorted({idx[w["cons"][0]] for w in first_words}))
        ch[key][0].append(cand)
        ch[key][2].append(v["v"])
        # half-verses: split after the word carrying athnach (or 'ole in poetic books)
        halves = [[]]
        for w in ws:
            halves[-1].append(w)
            if w["athnach"] or (w["ole"] and v["book"] in ("Ps", "Prov", "Job")):
                halves.append([])
        halves = [h for h in halves if h]
        for hi, h in enumerate(halves):
            if hi == 0:
                ch[key][1].append(cand)
            else:
                ch[key][1].append((idx[h[0]["cons"][0]],))
    return ch


def bh(ps, q=0.05):
    ps = np.asarray(ps, float)
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        prev = min(prev, ps[i] * m / rank)
        adj[i] = prev
    return adj


def greek_initials(verses):
    gi = {c: i for i, c in enumerate(T.GRK_ALPHA)}
    chap = defaultdict(list)
    books = defaultdict(list)
    for b, c, v, ws in verses:
        w = "".join(ws)
        if not w:
            continue
        chap[(b, c)].append((gi[w[0]],))
        books[b].append(w[0])
    return chap, books


NAMES = ["ιχθυσ", "ιησουσ", "χριστοσ", "ιωαννησ", "θεοσ", "κυριοσ", "λογοσ", "σωτηρ"]


def count_names(book_seqs):
    out = {}
    for nm in NAMES:
        c = 0
        for s in book_seqs:
            st = 0
            while True:
                k = s.find(nm, st)
                if k < 0:
                    break
                c += 1
                st = k + 1
        out[nm] = c
    return out


def vertical_words(seqs, lex, minlen=5, maxlen=9):
    c = 0
    found = []
    for s in seqs:
        for L in range(minlen, maxlen + 1):
            for i in range(len(s) - L + 1):
                if s[i:i + L] in lex:
                    c += 1
                    if found is not None and len(found) < 50:
                        found.append(s[i:i + L])
    return c, found


def main(texts, out_json):
    rng = np.random.default_rng(39002)
    res = {"hebrew": {}, "greek": {}}
    tests = []
    # ---------------- Hebrew
    verses = T.load_wlc(os.path.join(texts, "morphhb/wlc"))
    ch = heb_units(verses)
    swap = (15, 16)  # ayin, pe
    rows = []
    for key, (vu, hu, vnums) in ch.items():
        for mode, units in (("verse", vu), ("half", hu)):
            if len(units) < 8:
                continue
            obs, p, n = perm_p(units, 22, swap, rng)
            rows.append(dict(book=key[0], ch=key[1], mode=mode, n_units=len(units), score=obs, p=p,
                             n_perm=n))
    # extra: Prov 31:10-31 alone, Ps 9+10 joined, Nahum 1:2-10 (published controls as segments)
    def seg(book, c, v0, v1):
        out = []
        for v in verses:
            if v["book"] == book and v["ch"] == c and v0 <= v["v"] <= v1:
                out.append((T.HEB_ALPHA.index(v["words"][0]["cons"][0]),))
        return out
    segs = {"Prov 31:10-31": seg("Prov", 31, 10, 31),
            "Ps 9-10 joined": [u for k in (("Ps", 9), ("Ps", 10)) for u in ch[k][0]],
            "Nah 1:2-10": seg("Nah", 1, 2, 10)}
    seg_rows = {}
    for nm, units in segs.items():
        obs, p, n = perm_p(units, 22, swap, rng)
        seg_rows[nm] = dict(score=obs, p=p, n_perm=n, n_units=len(units))
    res["hebrew"]["segments"] = seg_rows
    adj = bh([r["p"] for r in rows])
    for r, a in zip(rows, adj):
        r["q_within_family"] = float(a)
    controls = {("Ps", 9), ("Ps", 10), ("Ps", 25), ("Ps", 34), ("Ps", 37), ("Ps", 111), ("Ps", 112),
                ("Ps", 119), ("Ps", 145), ("Lam", 1), ("Lam", 2), ("Lam", 3), ("Lam", 4),
                ("Prov", 31), ("Nah", 1)}
    res["hebrew"]["controls"] = sorted(
        [r for r in rows if (r["book"], r["ch"]) in controls] +
        [dict(r, book="Lam", ch=5) for r in rows if r["book"] == "Lam" and r["ch"] == 5][:0],
        key=lambda r: (r["book"], r["ch"], r["mode"]))
    res["hebrew"]["lam5"] = [r for r in rows if r["book"] == "Lam" and r["ch"] == 5]
    res["hebrew"]["top"] = sorted(rows, key=lambda r: (r["p"], -r["score"]))[:40]
    res["hebrew"]["n_tests"] = len(rows)
    res["hebrew"]["significant_q05"] = [dict(book=r["book"], ch=r["ch"], mode=r["mode"], score=r["score"],
                                             p=r["p"], known=(r["book"], r["ch"]) in controls)
                                        for r in rows if r["q_within_family"] <= 0.05]
    for r in rows:
        tests.append(dict(test="Hebrew acrostic %s %d (%s)" % (r["book"], r["ch"], r["mode"]),
                          p=r["p"], family="acrostic_hebrew",
                          known=(r["book"], r["ch"]) in controls))
    print("hebrew done", file=sys.stderr)
    # ---------------- Greek alphabetic chains
    nt, lex = load_nt = T.load_sblgnt(os.path.join(texts, "sblgnt"))
    lxx = T.load_lxx(os.path.join(texts, "lxx-swete/data"))
    for corpus, vs in (("NT", nt), ("LXX", lxx)):
        chap, books = greek_initials(vs)
        grows = []
        for key, units in chap.items():
            if len(units) < 8:
                continue
            obs, p, n = perm_p(units, 24, None, rng, n0=100)
            grows.append(dict(book=key[0], ch=key[1], n_units=len(units), score=obs, p=p, n_perm=n))
        adj = bh([r["p"] for r in grows])
        for r, a in zip(grows, adj):
            r["q_within_family"] = float(a)
            tests.append(dict(test="Greek alphabetic acrostic %s %s %d" % (corpus, r["book"], r["ch"]),
                              p=r["p"], family="acrostic_greek",
                              known=("Threni" in r["book"])))  # Swete prints Hebrew letter names
        res["greek"][corpus + "_alphabetic"] = dict(
            n_tests=len(grows), top=sorted(grows, key=lambda r: r["p"])[:10],
            max_score=max(r["score"] for r in grows),
            significant_q05=[r for r in grows if r["q_within_family"] <= 0.05])
        # names and vertical words
        seqs = ["".join(s) for s in books.values()]
        obs_names = count_names(seqs)
        obs_vw, found = vertical_words(seqs, lex)
        nnull = 300
        null_names = defaultdict(list)
        null_vw = []
        for i in range(nnull):
            sh = ["".join(rng.permutation(list(s))) for s in seqs]
            cn = count_names(sh)
            for k, v in cn.items():
                null_names[k].append(v)
            null_vw.append(vertical_words(sh, lex)[0])
        nm_out = {}
        for k in NAMES:
            arr = np.array(null_names[k])
            p = float((1 + (arr >= obs_names[k]).sum()) / (nnull + 1))
            nm_out[k] = dict(obs=obs_names[k], null_mean=float(arr.mean()), p=p)
            tests.append(dict(test="name acrostic %s in %s" % (k, corpus), p=p, family="acrostic_name"))
        arr = np.array(null_vw)
        pv = float((1 + (arr >= obs_vw).sum()) / (nnull + 1))
        tests.append(dict(test="vertical dictionary words (len>=5) in %s verse initials" % corpus,
                          p=pv, family="acrostic_vertical"))
        res["greek"][corpus + "_names"] = nm_out
        res["greek"][corpus + "_vertical_words"] = dict(obs=obs_vw, null_mean=float(arr.mean()),
                                                        null_sd=float(arr.std()), p=pv,
                                                        examples=found[:30])
        print(corpus, "done", file=sys.stderr)
    # ---------------- Sibylline Oracles (Geffcken) and Constantine's quotation
    sib = T.load_sibyl(os.path.join(texts, "f1k_sibyl/repo/data/tlg1551/tlg001/tlg1551.tlg001.1st1K-grc1.xml"))
    sbooks = defaultdict(list)
    for b, n, t in sib:
        g = T.grk_plain(t)
        if g:
            sbooks[b].append(g[0])
    seqs = ["".join(v) for v in sbooks.values()]
    con = T.load_constantine_acrostic(os.path.join(
        texts, "f1k/data/tlg2018/tlg021/tlg2018.tlg021.1st1K-grc1.xml"))
    con_init = "".join(T.grk_plain(l)[0] for l in con)
    restored = False
    if con_init.startswith("δ") and T.grk_plain(con[0]).startswith("δρωσει"):
        con_init = "ι" + con_init[1:]  # OCR lost the initial Iota (drop capital); Geffcken 8.217 reads Ἱδρώσει
        restored = True
    full = "ιησουσχρειστοσθεουυιοσσωτηρσταυροσ"
    res["sibyl"] = dict(n_lines=len(sib), constantine_lines=len(con), constantine_initials=con_init,
                        constantine_initial_restored=restored, matches_full_acrostic=(con_init == full))
    # null for the control: 34-line runs of shuffled Sibylline line initials matching the phrase
    # p is analytic-ish: count matches of the first 6 letters (ιησουσ) in shuffles
    obs_names = count_names(seqs)
    null_names = defaultdict(list)
    for i in range(500):
        sh = ["".join(rng.permutation(list(s))) for s in seqs]
        for k, v in count_names(sh).items():
            null_names[k].append(v)
    sres = {}
    for k in NAMES:
        arr = np.array(null_names[k])
        p = float((1 + (arr >= obs_names[k]).sum()) / 501)
        sres[k] = dict(obs=obs_names[k], null_mean=float(arr.mean()), p=p)
    res["sibyl"]["names_geffcken_text"] = sres
    # probability of the full 34-letter acrostic by chance, from Sibylline letter frequencies
    allinit = "".join(seqs)
    fr = {c: allinit.count(c) / len(allinit) for c in set(allinit)}
    logp = sum(np.log10(fr.get(c, 1e-9)) for c in full)
    res["sibyl"]["full_acrostic_log10_prob_per_position"] = float(logp)
    res["sibyl"]["expected_chance_occurrences_in_corpus"] = float(len(allinit) * 10 ** logp)
    tests.append(dict(test="Sibyl 8 IHSOUS name acrostic (Geffcken lines) vs shuffled lines",
                      p=sres["ιησουσ"]["p"], family="acrostic_name", known=True))
    res["tests"] = tests
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
