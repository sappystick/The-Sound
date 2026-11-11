#!/usr/bin/env python3
"""Round 39 lens "coptic": the buried library (Nag Hammadi and other Coptic texts) read against John.

Usage:
  python3 round39/coptic/coptic.py sources/texts/coptic_scriptorium sources/texts/coptic_scriptorium_tt \
      sources/texts/sblgnt round39/coptic/results.json

Data: Coptic SCRIPTORIUM annotated corpora (lemma, part of speech, Greek-loan tags). Sahidic NT and OT from
the TreeTagger (*.tt) files; all other texts from CoNLL-U. Greek NT from MorphGNT (SBLGNT).
Tokens = SCRIPTORIUM "norm" units (morphemes: article, pronoun, verb, noun ...), the same segmentation everywhere.

Hypotheses, measures and decision rules (written before running):

T1  Vocabulary lean. For each non-canonical Coptic text T (Thomas, Pistis Sophia, Mysteries of John, Book of
    Bartholomew, Acts of Pilate, Dormition of John, magical papyri, Shenoute pooled) compute Burrows' Delta
    on the 250 most frequent lemmas of the four Sahidic gospels (z-scores from 2000-token chunks of the whole
    reference pool) against each gospel. Gospels are size-matched: every gospel is represented by random
    contiguous samples of the length of the smallest gospel (100 draws, Delta averaged).
    lean(T) = mean Delta(T, Mt/Mk/Lk) - Delta(T, Jn)   (> 0 means T is nearer John).
    Null: random contiguous chunks of len(T) from a pool of other Sahidic text (OT, Romans-Jude except
    1-3 John, Revelation, and non-canonical literature that is not a target: Apophthegmata, saints' lives,
    homilies). p = share of 400 null chunks with lean >= observed (one-sided, toward John), and the
    two-sided rank. Positive controls: Sahidic 1 John must lean John; Sahidic Acts must be nearest Luke.
    Decision: lean toward John counts if BH q < 0.05.
T2a Loanword share. Share of content tokens (N, V, ADJ, ADV, VSTAT; proper names excluded) whose lemma is a
    Greek loan (lemma ever tagged Greek anywhere in SCRIPTORIUM). John against the Synoptics.
    Null: random contiguous chunks of John's length from the three Synoptics concatenated (circular), 2000 draws.
T2b Translation layer, lemma-controlled (new). Align MorphGNT verses to Sahidic verses. A Greek content token
    (noun, verb, adjective; capitalised proper names excluded) is "kept" if a Greek-loan Coptic lemma with
    the same first three consonants appears in the same Coptic verse. Expected kept count for John = sum over
    John's tokens of the Synoptic keep-rate of that same Greek lemma (lemmas found in both). Null: permute
    gospel labels within each lemma (5000 permutations). Positive control: Greek proper names are kept at
    ~100%; keep-rate of a translated word (logos -> shaje) is ~0.
    Key-term table: logos, zoe, phos, aletheia, kosmos, pneuma, doxa, agape/agapao, pisteuo, meno, skotia, charis,
    martyria, kosmos, ego eimi, with the Coptic rendering found by Dice association in aligned verses.
T3  "I am" + predicate. Pattern: surface ANOK, then (<=2 particles) the copula PE, then article/possessive +
    noun (predicate noun) or article + relative (predicate relative). Rate per 10,000 tokens with exact
    Poisson 95% CI. Test John against the pooled Synoptics (exact conditional binomial, one-sided), and
    each non-canonical text against the pooled Synoptics (two-sided). Positive control: recall of the Greek
    ego eimi + nominative predicate verses of John (MorphGNT) by the Coptic pattern.
All tests are pooled for Benjamini-Hochberg (q = 0.05). Seeds fixed.
"""
import sys, os, re, glob, json, math, subprocess
from collections import Counter, defaultdict
import numpy as np

SEED = 39
CONTENT = {"N", "V", "VSTAT", "ADJ", "ADV", "VIMP"}

# ------------------------------------------------------------------ loading
NORM_RE = re.compile(r'<norm [^>]*>')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
VERSE_RE = re.compile(r'<verse_n verse_n="([^"]*)"')


def load_tt(path):
    """Return list of tokens: dict(norm, lemma, pos, greek, verse)."""
    toks = []
    verse = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("<verse_n"):
                m = VERSE_RE.match(line)
                verse = m.group(1) if m else None
            elif line.startswith("<norm "):
                a = dict(ATTR_RE.findall(line))
                toks.append({"norm": a.get("norm", ""), "lemma": a.get("lemma", ""), "pos": a.get("pos", ""),
                             "greek": a.get("lang") == "Greek", "verse": verse})
    return toks


def load_conllu(path):
    toks = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line or line[0] == "#" or line == "\n":
                continue
            c = line.rstrip("\n").split("\t")
            if len(c) < 10 or not c[0].isdigit():
                continue
            toks.append({"norm": c[1], "lemma": c[2], "pos": c[4], "greek": "OrigLang=grc" in c[9],
                         "verse": None})
    return toks


NT_BOOKS = {"40": "Mt", "41": "Mk", "42": "Lk", "43": "Jn", "44": "Ac", "62": "1Jn", "63": "2Jn", "64": "3Jn",
            "66": "Re"}


def chap_key(fn):
    b = os.path.basename(fn)[:-3]
    parts = b.split("_")
    ch = parts[-1]
    try:
        chn = int(ch)
    except ValueError:
        chn = 0
    return parts[0], "_".join(parts[1:-1]), chn


def load_bible(ttdir):
    """Return dict book_code -> list of (chapter, tokens)."""
    books = defaultdict(list)
    for fn in glob.glob(os.path.join(ttdir, "*.tt")):
        num, name, ch = chap_key(fn)
        toks = load_tt(fn)
        # some chapter files run on into the next chapter (Sahidica John 7 file holds 7:1-53 + 8:12-59,
        # the Sahidic text having no 7:53-8:11): a drop in verse number starts the next chapter
        cur, last = ch, 0
        for t in toks:
            try:
                v = int(t["verse"])
            except (TypeError, ValueError):
                v = None
            if v is not None:
                if v < last:
                    cur += 1
                last = v
            t["ch"] = cur
        books[(num, name)].append((ch, toks))
    for k in books:
        books[k].sort(key=lambda x: x[0])
    return books


TARGETS = {  # label: folder glob under coptic_scriptorium (CoNLL-U)
    "Thomas (NHC II,2)": "thomas-gospel",
    "Pistis Sophia": "pistis-sophia",
    "Mysteries of John": "mysteries-john",
    "Book of Bartholomew": "book-bartholomew",
    "Acts of Pilate": "acts-pilate",
    "Dormition of John": "dormition-john",
    "Magical papyri": "magical-papyri",
    "Shenoute (pooled)": "shenoute-*",
}
# Non-target literature that may enter the null pool (treebank duplicates left out on purpose).
POOL_LIT = ["AP", "life-*", "proclus-homilies", "pseudo-*", "martyrdom-victor", "helias", "mercurius",
            "theodosius-alexandria", "john-constantinople", "lament-mary", "pachomius-instructions",
            "besa-letters", "johannes-canons", "abraham"]


def load_folder(root, pattern):
    toks = []
    for d in sorted(glob.glob(os.path.join(root, pattern))):
        for fn in sorted(glob.glob(os.path.join(d, "*_CONLLU", "*.conllu"))):
            if os.path.getsize(fn) > 100:
                toks.extend(load_conllu(fn))
    return toks


# ------------------------------------------------------------------ helpers
def is_content(t):
    return t["pos"] in CONTENT


def bh(pvals):
    p = np.array(pvals, float)
    n = len(p)
    o = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank in range(n, 0, -1):
        i = o[rank - 1]
        prev = min(prev, p[i] * n / rank)
        q[i] = prev
    return q


def pois_cdf(k, mu):
    if k < 0:
        return 0.0
    s, term = 0.0, math.exp(-mu)
    s = term
    for i in range(1, k + 1):
        term *= mu / i
        s += term
    return min(1.0, s)


def pois_ci(k, alpha=0.05):
    def solve(f, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else solve(lambda m: 1 - pois_cdf(k - 1, m) < alpha / 2, 0.0, k + 50)
    hi = solve(lambda m: pois_cdf(k, m) > alpha / 2, k, k * 3 + 50)
    return lo, hi


def binom_tail_ge(x, n, p):
    """P(X >= x), X ~ Bin(n,p)."""
    if x <= 0:
        return 1.0
    lp, lq = math.log(p), math.log1p(-p)
    tot = 0.0
    for k in range(x, n + 1):
        tot += math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * lp + (n - k) * lq)
    return min(1.0, tot)


def binom_two_sided(x, n, p):
    lo = 1 - binom_tail_ge(x + 1, n, p)
    hi = binom_tail_ge(x, n, p)
    return min(1.0, 2 * min(lo, hi))


# ------------------------------------------------------------------ T1 vocabulary lean
def lemma_seq(toks):
    return [t["lemma"] for t in toks if t["pos"] != "NPROP" and t["lemma"]]


def freq_vec(seq, idx):
    """seq: list of lemmas or an int array already mapped (len(idx) = out-of-feature bin)."""
    if isinstance(seq, np.ndarray):
        a = seq
    else:
        a = np.array([idx.get(l, len(idx)) for l in seq], int)
    v = np.bincount(a, minlength=len(idx) + 1)[:len(idx)].astype(float)
    return v / max(1, len(a))


def t1(gospels, targets, controls, pool_seq, rng, nfeat=250, ndraw=100, nnull=400):
    allg = sum((gospels[g] for g in gospels), [])
    feats = [l for l, _ in Counter(allg).most_common(nfeat)]
    idx = {l: i for i, l in enumerate(feats)}
    enc = lambda s: np.array([idx.get(l, nfeat) for l in s], int)
    gosp = {g: enc(s) for g, s in gospels.items()}
    pool = enc(pool_seq)
    ref = np.concatenate([np.concatenate(list(gosp.values())), pool])
    C = np.array([freq_vec(ref[i:i + 2000], idx) for i in range(0, len(ref) - 2000, 2000)])
    mu, sd = C.mean(0), C.std(0) + 1e-9
    m = min(len(s) for s in gosp.values())
    gsamp = {}
    for g, s in gosp.items():
        zs = []
        for _ in range(ndraw):
            st = int(rng.integers(0, len(s) - m + 1))
            zs.append((freq_vec(s[st:st + m], idx) - mu) / sd)
        gsamp[g] = np.array(zs)

    def deltas(a):
        z = (freq_vec(a, idx) - mu) / sd
        return {g: float(np.mean(np.abs(gsamp[g] - z[None, :]).mean(1))) for g in gsamp}

    def lean(d):
        return (d["Mt"] + d["Mk"] + d["Lk"]) / 3 - d["Jn"]

    out = {"n_features": nfeat, "gospel_sample_tokens": m, "gospel_tokens": {g: len(s) for g, s in gosp.items()},
           "note": "lean_to_john = mean Delta to Mt/Mk/Lk minus Delta to Jn; relative_lean_z = same for each gospel, as z against the null chunks"}
    res = {}
    for name, seq in list(targets.items()) + list(controls.items()):
        a = enc(seq)
        d = deltas(a)
        L = lean(d)
        n = len(a)
        nulls, nearest_null, gl_null = [], Counter(), defaultdict(list)
        for _ in range(nnull):
            st = int(rng.integers(0, len(pool) - n))
            dn = deltas(pool[st:st + n])
            nulls.append(lean(dn))
            nearest_null[min(dn, key=dn.get)] += 1
            for g in dn:
                gl_null[g].append(np.mean([dn[h] for h in dn if h != g]) - dn[g])
        nulls = np.array(nulls)
        rel = {}
        for g in d:
            obs = np.mean([d[h] for h in d if h != g]) - d[g]
            arr = np.array(gl_null[g])
            rel[g] = float((obs - arr.mean()) / arr.std())
        p_one = float((1 + np.sum(nulls >= L)) / (nnull + 1))
        p_two = float(min(1.0, 2 * min((1 + np.sum(nulls >= L)) / (nnull + 1), (1 + np.sum(nulls <= L)) / (nnull + 1))))
        res[name] = {"tokens": n, "delta": d, "nearest": min(d, key=d.get), "farthest": max(d, key=d.get),
                     "lean_to_john": L, "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
                     "z": float((L - nulls.mean()) / nulls.std()), "p_one_sided_john": p_one, "p_two_sided": p_two,
                     "null_nearest_share": {k: v / nnull for k, v in nearest_null.items()},
                     "relative_lean_z": rel, "relatively_nearest": max(rel, key=rel.get),
                     "relatively_farthest": min(rel, key=rel.get),
                     "role": "control" if name in controls else "target"}
    out["texts"] = res
    return out


# ------------------------------------------------------------------ T2 loanwords
def loan_share(toks, greek_lex):
    c = [t for t in toks if is_content(t)]
    k = sum(1 for t in c if t["lemma"] in greek_lex)
    return k, len(c)


def t2a(gtoks, greek_lex, rng, ndraw=2000):
    out = {}
    for g, toks in gtoks.items():
        k, n = loan_share(toks, greek_lex)
        out[g] = {"loan_content": k, "content": n, "share": k / n}
    # Greek function words share too (de, gar, alla ...): descriptive
    for g, toks in gtoks.items():
        nonc = [t for t in toks if not is_content(t) and t["pos"] != "NPROP"]
        out[g]["loan_share_function_words"] = sum(1 for t in nonc if t["lemma"] in greek_lex) / len(nonc)
    syn = gtoks["Mt"] + gtoks["Mk"] + gtoks["Lk"]
    flags = np.array([1 if t["lemma"] in greek_lex else 0 for t in syn if is_content(t)])
    nj = out["Jn"]["content"]
    ext = np.concatenate([flags, flags[:nj]])
    starts = rng.integers(0, len(flags), ndraw)
    cs = np.concatenate([[0], np.cumsum(ext)])
    shares = (cs[starts + nj] - cs[starts]) / nj
    sj = out["Jn"]["share"]
    out["test_john_vs_synoptic_chunks"] = {
        "john_share": sj, "null_mean": float(shares.mean()), "null_sd": float(shares.std()),
        "null_2.5_97.5": [float(np.percentile(shares, 2.5)), float(np.percentile(shares, 97.5))],
        "p_two_sided": float(min(1, 2 * min((1 + np.sum(shares >= sj)) / (ndraw + 1),
                                            (1 + np.sum(shares <= sj)) / (ndraw + 1))))}
    return out


GR2CO = dict(zip("αβγδεζηθικλμνξοπρσςτυφχψω", "ⲁⲃⲅⲇⲉⲍⲏⲑⲓⲕⲗⲙⲛⲝⲟⲡⲣⲥⲥⲧⲩⲫⲭⲯⲱ"))
CO_VOW = set("ⲁⲉⲏⲓⲟⲩⲱ")
import unicodedata


def strip_gr(w):
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(ch for ch in w if not unicodedata.combining(ch))


def skel_co(w):
    # Greek has no letter h: a hori in a loan is a rough breathing (initial or after a prefix), so drop it
    return "".join(ch for ch in w if ch not in CO_VOW and ch != "ϩ")


def skel_gr(lemma):
    w = "".join(GR2CO.get(ch, "") for ch in strip_gr(lemma))
    return "".join(ch for ch in w if ch not in CO_VOW)


def vnorm(w):
    """Full form with itacism merged: eta/ei/upsilon(not in ou) -> iota, omega -> omicron; no leading hori."""
    w = w.lstrip("ϩ").replace("ⲟⲩ", "U").replace("ⲉⲓ", "ⲓ").replace("ⲏ", "ⲓ").replace("ⲩ", "ⲓ").replace("ⲱ", "ⲟ")
    return w


def gr_full(lemma):
    return vnorm("".join(GR2CO.get(ch, "") for ch in strip_gr(lemma)))


def loan_match(glemma, cop_lemmas):
    """True if a Coptic (Greek-loan) lemma renders the Greek lemma by form.
    Skeleton rule: first min(3, len) consonants equal and skeleton lengths within 2 of each other; for
    skeletons of length <= 2 the full itacism-normalised form must share its first 3 letters."""
    sk = skel_gr(glemma)
    gf = gr_full(glemma)
    for c in cop_lemmas:
        cs = skel_co(c)
        if len(sk) >= 3:
            if cs[:3] == sk[:3] and abs(len(cs) - len(sk)) <= 2:
                return True
        else:
            cf = vnorm(c)
            if len(gf) >= 3 and cf[:3] == gf[:3] and cs[:len(sk)] == sk:
                return True
    return False


def morphgnt(path):
    """dict (chap, verse) -> list of (pos, parse, word, lemma)."""
    vs = defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            ref, pos, parse, text, word, norm, lemma = line.split()
            vs[(int(ref[2:4]), int(ref[4:6]))].append((pos, parse, norm, lemma))
    return vs


def coptic_verses(chapters):
    vs = defaultdict(list)
    for ch, toks in chapters:
        for t in toks:
            try:
                v = int(t["verse"])
            except (TypeError, ValueError):
                continue
            vs[(t.get("ch", ch), v)].append(t)
    return vs


def align_keep(gk_verses, co_verses, greek_lex, prop_lex, rng=None):
    """List of (lemma, kept, is_proper, key) for Greek content tokens in verses present in both.
    With rng: each Greek verse is paired with a random Coptic verse of the same book (negative control)."""
    rows = []
    ckeys = sorted(co_verses)
    for key, gtoks in gk_verses.items():
        ct = co_verses.get(key)
        if not ct:
            continue
        if rng is not None:
            ct = co_verses[ckeys[int(rng.integers(0, len(ckeys)))]]
        loans = set(t["lemma"] for t in ct if t["lemma"] in greek_lex)
        names = set(t["lemma"] for t in ct if t["pos"] == "NPROP")
        for pos, parse, norm, lemma in gtoks:
            if pos not in ("N-", "V-", "A-"):
                continue
            if lemma in ("εἰμί",):
                continue
            proper = lemma[0].isupper()
            kept = loan_match(lemma, (names | loans) if proper else loans)
            rows.append((lemma, kept, proper, key))
    return rows


def t2b(rows_by_g, rng, nperm=5000):
    out = {}
    for g, rows in rows_by_g.items():
        com = [r for r in rows if not r[2]]
        prop = [r for r in rows if r[2]]
        out[g] = {"greek_content_tokens": len(com), "kept": sum(r[1] for r in com),
                  "keep_rate": sum(r[1] for r in com) / max(1, len(com)),
                  "proper_names_tokens": len(prop),
                  "proper_names_keep_rate_positive_control": sum(r[1] for r in prop) / max(1, len(prop))}
    # lemma-controlled test
    syn_rows = [r for g in ("Mt", "Mk", "Lk") for r in rows_by_g[g] if not r[2]]
    jn_rows = [r for r in rows_by_g["Jn"] if not r[2]]
    syn_by = defaultdict(list)
    for r in syn_rows:
        syn_by[r[0]].append(r[1])
    jn_by = defaultdict(list)
    for r in jn_rows:
        jn_by[r[0]].append(r[1])
    shared = [l for l in jn_by if l in syn_by]
    obs = sum(sum(jn_by[l]) for l in shared)
    exp = sum(len(jn_by[l]) * np.mean(syn_by[l]) for l in shared)
    nj = sum(len(jn_by[l]) for l in shared)
    # permutation within lemma
    arrs = [(np.array(jn_by[l] + syn_by[l], int), len(jn_by[l])) for l in shared]
    perm = np.zeros(nperm)
    for i in range(nperm):
        s = 0
        for a, k in arrs:
            if a.min() == a.max():
                s += a[0] * k
            else:
                s += rng.permutation(a)[:k].sum()
        perm[i] = s
    out["lemma_controlled"] = {
        "shared_lemmas": len(shared), "john_tokens_on_shared": nj, "john_kept_observed": int(obs),
        "john_kept_expected_from_synoptic_rates": float(exp), "ratio_obs_exp": float(obs / exp),
        "perm_mean": float(perm.mean()),
        "p_two_sided": float(min(1, 2 * min((1 + np.sum(perm >= obs)) / (nperm + 1),
                                            (1 + np.sum(perm <= obs)) / (nperm + 1))))}
    # which lemmas drive it: largest John-minus-Synoptic differences (n>=5 each)
    diffs = []
    for l in shared:
        if len(jn_by[l]) >= 5 and len(syn_by[l]) >= 5:
            diffs.append((l, len(jn_by[l]), float(np.mean(jn_by[l])), len(syn_by[l]), float(np.mean(syn_by[l]))))
    diffs.sort(key=lambda x: -(x[2] - x[4]) * min(x[1], x[3]) ** 0.5)
    out["lemma_controlled"]["top_john_keeps_more"] = diffs[:12]
    out["lemma_controlled"]["top_john_translates_more"] = diffs[::-1][:12]
    return out


KEY_TERMS = ["λόγος", "ζωή", "φῶς", "ἀλήθεια", "ἀληθινός", "κόσμος", "πνεῦμα", "δόξα", "δοξάζω", "ἀγάπη",
             "ἀγαπάω", "πιστεύω", "μένω", "σκοτία", "χάρις", "μαρτυρία", "μαρτυρέω", "ἐντολή", "νόμος", "σάρξ",
             "ψυχή", "κρίσις", "παράκλητος", "βασιλεία", "ἄρτος", "ποιμήν", "θύρα", "ἄμπελος", "ὁδός",
             "ἀνάστασις"]


def key_terms(gk_by_g, co_by_g, rows_by_g):
    out = {}
    for term in KEY_TERMS:
        row = {}
        for g in ("Jn", "Mt", "Mk", "Lk"):
            rr = [r for r in rows_by_g[g] if r[0] == term]
            row[g] = {"n": len(rr), "kept": sum(r[1] for r in rr)}
        # Coptic rendering in John (or all four if rare): Dice association over aligned verses
        gv = [k for k, toks in gk_by_g["Jn"].items() if any(t[3] == term for t in toks) and k in co_by_g["Jn"]]
        pool_g = ["Jn"] if len(gv) >= 5 else ["Jn", "Mt", "Mk", "Lk"]
        nG = 0
        co_cnt, co_all = Counter(), Counter()
        for g in pool_g:
            for k, ct in co_by_g[g].items():
                lem = set(t["lemma"] for t in ct if is_content(t))
                co_all.update(lem)
                gl = set(t[3] for t in gk_by_g[g].get(k, []))
                if term in gl:
                    nG += 1
                    co_cnt.update(lem)
        best = sorted(((2 * c / (nG + co_all[l]), l, c) for l, c in co_cnt.items()), reverse=True)[:3]
        row["coptic_rendering_dice"] = [{"lemma": l, "dice": round(d, 3), "co_verses": c} for d, l, c in best]
        row["verses_with_term"] = nG
        out[term] = row
    return out


# ------------------------------------------------------------------ T3 I am + predicate
ART = {"ART", "PPOS"}
SKIP = {"PTC", "CONJ"}


def iam(toks):
    """Count ANOK PE + predicate. Returns dict counts and list of hit indices."""
    noun, rel, bare = 0, 0, 0
    hits = []
    n = len(toks)
    for i, t in enumerate(toks):
        if t["norm"] != "ⲁⲛⲟⲕ":
            continue
        j = i + 1
        while j < n and j - i <= 3 and toks[j]["pos"] in SKIP:
            j += 1
        if j >= n or toks[j]["pos"] != "COP":
            continue
        k = j + 1
        while k < n and k - j <= 2 and toks[k]["pos"] in SKIP:
            k += 1
        kind = "bare"
        if k < n and toks[k]["pos"] in ART:
            nxt = toks[k + 1:k + 4]
            if nxt and nxt[0]["pos"] in ("CREL",):
                kind = "rel"
            elif any(x["pos"] in ("N", "NPROP") for x in nxt[:2]):
                kind = "noun"
            elif nxt and nxt[0]["pos"] in ("PINT", "PDEM"):
                kind = "bare"
        elif k < n and toks[k]["pos"] in ("N", "NPROP"):
            kind = "noun"
        if kind == "noun":
            noun += 1
        elif kind == "rel":
            rel += 1
        else:
            bare += 1
        hits.append((i, kind, t.get("verse")))
    return {"noun": noun, "rel": rel, "bare": bare, "tokens": n}, hits


def greek_iam(gk):
    """Verses of a MorphGNT book with ego + eimi(1S pres) + nominative article/noun within 3 words."""
    out = set()
    for key, toks in gk.items():
        for i, (pos, parse, norm, lemma) in enumerate(toks):
            if lemma == "ἐγώ" and parse[4] == "N":
                win = toks[i + 1:i + 3]
                for j, w in enumerate(win):
                    if w[3] == "εἰμί" and w[1][0] == "1":
                        after = toks[i + 2 + j:i + 2 + j + 3]
                        if any(a[0] in ("RA", "N-") and a[1][4] == "N" for a in after):
                            out.add(key)
    return out


# ------------------------------------------------------------------ main
def main():
    croot, ttdir, sbl, outp = sys.argv[1:5]
    rng = np.random.default_rng(SEED)
    bible = load_bible(ttdir)
    gnum = {"Mt": "40", "Mk": "41", "Lk": "42", "Jn": "43"}
    by_num = defaultdict(list)
    for (num, name), chs in bible.items():
        by_num[num].extend(chs)
    gch = {g: by_num[n] for g, n in gnum.items()}
    gtoks = {g: [t for _, toks in gch[g] for t in toks] for g in gch}

    targets_t = {k: load_folder(croot, v) for k, v in TARGETS.items()}
    pool_lit = []
    for p in POOL_LIT:
        pool_lit.extend(load_folder(croot, p))
    # Greek-loan lexicon: union of lemmas tagged Greek anywhere loaded
    greek_lex = Counter()
    every = [t for chs in by_num.values() for _, toks in chs for t in toks] + pool_lit + \
        [t for v in targets_t.values() for t in v]
    for t in every:
        if t["greek"] and t["pos"] != "NPROP":
            greek_lex[t["lemma"]] += 1
    greek_lex = set(l for l, c in greek_lex.items() if c >= 1)

    # null pool for T1: OT + NT (not gospels, not Acts, not 1-3 John) + non-target literature
    pool_toks = []
    for num in sorted(by_num):
        if num in ("40", "41", "42", "43", "44", "62", "63", "64"):
            continue
        for _, toks in by_num[num]:
            pool_toks.extend(toks)
    pool_toks.extend(pool_lit)
    controls = {"CONTROL 1-3 John (Sahidic)": lemma_seq([t for n in ("62", "63", "64") for _, tk in by_num[n] for t in tk]),
                "CONTROL Acts (Sahidic)": lemma_seq([t for _, tk in by_num["44"] for t in tk])}
    res = {"seed": SEED}
    try:
        res["scriptorium_commit"] = subprocess.run(["git", "-C", croot, "rev-parse", "HEAD"], capture_output=True,
                                                   text=True).stdout.strip()
    except Exception:
        res["scriptorium_commit"] = None
    res["corpus_sizes_tokens"] = {**{g: len(v) for g, v in gtoks.items()}, **{k: len(v) for k, v in targets_t.items()},
                                  "null_pool": len(pool_toks), "greek_lexicon_lemmas": len(greek_lex)}
    res["john_chapters_present"] = sorted(set(t["ch"] for _, tk in gch["Jn"] for t in tk))
    res["john_verses_present"] = len(set((t["ch"], t["verse"]) for _, tk in gch["Jn"] for t in tk))

    # ---- T1
    gseq = {g: lemma_seq(v) for g, v in gtoks.items()}
    tseq = {k: lemma_seq(v) for k, v in targets_t.items() if len(v) > 500}
    res["T1"] = t1(gseq, tseq, controls, lemma_seq(pool_toks), rng)

    # ---- T2
    res["T2a"] = t2a(gtoks, greek_lex, rng)
    for k, v in targets_t.items():
        kk, n = loan_share(v, greek_lex)
        res["T2a"].setdefault("noncanonical", {})[k] = {"share": kk / max(1, n), "content": n}
    gfile = {"Mt": "61-Mt", "Mk": "62-Mk", "Lk": "63-Lk", "Jn": "64-Jn"}
    gk = {g: morphgnt(os.path.join(sbl, f + "-morphgnt.txt")) for g, f in gfile.items()}
    cv = {g: coptic_verses(gch[g]) for g in gch}
    rows = {g: align_keep(gk[g], cv[g], greek_lex, None) for g in gk}
    res["T2b"] = t2b(rows, rng)
    neg = {g: align_keep(gk[g], cv[g], greek_lex, None, rng=np.random.default_rng(SEED + 1)) for g in gk}
    res["T2b"]["negative_control_shuffled_verses_keep_rate"] = {
        g: sum(r[1] for r in neg[g] if not r[2]) / max(1, sum(1 for r in neg[g] if not r[2])) for g in neg}
    res["T2b"]["negative_control_shuffled_verses_proper_names"] = {
        g: sum(r[1] for r in neg[g] if r[2]) / max(1, sum(1 for r in neg[g] if r[2])) for g in neg}
    res["T2b"]["aligned_verses"] = {g: len(set(r[3] for r in rows[g])) for g in rows}
    res["T2_key_terms"] = key_terms(gk, cv, rows)

    # ---- T2c the "me" homophone: Sahidic ⲙⲉ = truth (noun) and ⲙⲉ = love (verb); Greek has no sound link
    me = {}
    for g in ("Mt", "Mk", "Lk", "Jn"):
        toks = gtoks[g]
        nn = sum(1 for t in toks if t["lemma"] == "ⲙⲉ" and t["pos"] == "N")
        vv = sum(1 for t in toks if t["lemma"] == "ⲙⲉ" and t["pos"] in ("V", "VSTAT", "VIMP"))
        both = sum(1 for k, ct in cv[g].items()
                   if any(t["lemma"] == "ⲙⲉ" and t["pos"] == "N" for t in ct)
                   and any(t["lemma"] == "ⲙⲉ" and t["pos"] != "N" for t in ct))
        gr_truth = sum(1 for k, gt in gk[g].items() for w in gt if w[3] in ("ἀλήθεια", "ἀληθής", "ἀληθινός", "ἀληθῶς"))
        gr_love = sum(1 for k, gt in gk[g].items() for w in gt if w[3] in ("ἀγαπάω", "ἀγάπη", "φιλέω"))
        me[g] = {"me_noun_truth": nn, "me_verb_love": vv, "per_10k_tokens": 1e4 * (nn + vv) / len(toks),
                 "verses_with_both": both, "greek_truth_words": gr_truth, "greek_love_words": gr_love}
    for k, toks in targets_t.items():
        nn = sum(1 for t in toks if t["lemma"] == "ⲙⲉ" and t["pos"] == "N")
        vv = sum(1 for t in toks if t["lemma"] == "ⲙⲉ" and t["pos"] in ("V", "VSTAT", "VIMP"))
        me[k] = {"me_noun_truth": nn, "me_verb_love": vv, "per_10k_tokens": 1e4 * (nn + vv) / max(1, len(toks))}
    jn_me = me["Jn"]["me_noun_truth"] + me["Jn"]["me_verb_love"]
    syn_me = sum(me[g]["me_noun_truth"] + me[g]["me_verb_love"] for g in ("Mt", "Mk", "Lk"))
    synT_all = sum(len(gtoks[g]) for g in ("Mt", "Mk", "Lk"))
    me["test_john_vs_syn"] = {"x": jn_me, "n": jn_me + syn_me,
                              "p_one_sided": binom_tail_ge(jn_me, jn_me + syn_me,
                                                           len(gtoks["Jn"]) / (len(gtoks["Jn"]) + synT_all))}
    res["T2c_me_homophone"] = me

    # ---- T3
    t3 = {}
    allhits = {}
    for name, toks in list(gtoks.items()) + list(targets_t.items()):
        c, h = iam(toks)
        allhits[name] = h
        lo, hi = pois_ci(c["noun"])
        lo2, hi2 = pois_ci(c["noun"] + c["rel"])
        c["noun_per_10k"] = 1e4 * c["noun"] / c["tokens"]
        c["noun_per_10k_ci95"] = [1e4 * lo / c["tokens"], 1e4 * hi / c["tokens"]]
        c["noun_or_rel_per_10k"] = 1e4 * (c["noun"] + c["rel"]) / c["tokens"]
        c["noun_or_rel_per_10k_ci95"] = [1e4 * lo2 / c["tokens"], 1e4 * hi2 / c["tokens"]]
        t3[name] = c
    synN = sum(t3[g]["noun"] for g in ("Mt", "Mk", "Lk"))
    synT = sum(t3[g]["tokens"] for g in ("Mt", "Mk", "Lk"))
    tests3 = {}
    jn = t3["Jn"]
    tests3["Jn_vs_Syn"] = {"x": jn["noun"], "n": jn["noun"] + synN,
                           "p_one_sided": binom_tail_ge(jn["noun"], jn["noun"] + synN, jn["tokens"] / (jn["tokens"] + synT)),
                           "rate_ratio": (jn["noun"] / jn["tokens"]) / (synN / synT)}
    for k in targets_t:
        c = t3[k]
        if c["tokens"] < 500:
            continue
        n = c["noun"] + synN
        p0 = c["tokens"] / (c["tokens"] + synT)
        tests3[k + "_vs_Syn"] = {"x": c["noun"], "n": n, "p_two_sided": binom_two_sided(c["noun"], n, p0),
                                 "rate_ratio": (c["noun"] / c["tokens"]) / (synN / synT)}
        p0j = c["tokens"] / (c["tokens"] + jn["tokens"])
        tests3[k + "_vs_Jn"] = {"x": c["noun"], "n": c["noun"] + jn["noun"],
                                "p_two_sided": binom_two_sided(c["noun"], c["noun"] + jn["noun"], p0j),
                                "rate_ratio": (c["noun"] / c["tokens"]) / (jn["noun"] / jn["tokens"]),
                                "descriptive_only": True}
    # positive control: Greek ego eimi + predicate verses in John
    gverses = greek_iam(gk["Jn"])
    gverses_present = sorted(v for v in gverses if v[0] in res["john_chapters_present"])
    cop_jn = set()
    off = 0
    jn_hits_ref = []
    hidx = {i: (kind, v) for i, kind, v in allhits["Jn"]}
    for _, toks in gch["Jn"]:
        for j in range(len(toks)):
            if off + j in hidx:
                kind, v = hidx[off + j]
                ch = toks[j]["ch"]
                jn_hits_ref.append({"ref": f"{ch}:{v}", "kind": kind})
                if kind in ("noun", "rel"):
                    cop_jn.add((ch, int(v)))
        off += len(toks)
    rec = [v for v in gverses_present if v in cop_jn]
    tests3["positive_control_recall"] = {"greek_verses": [f"{a}:{b}" for a, b in gverses_present],
                                         "recalled": [f"{a}:{b}" for a, b in rec],
                                         "recall": len(rec) / max(1, len(gverses_present)),
                                         "coptic_hits_not_in_greek_set": sorted(f"{a}:{b}" for a, b in cop_jn - set(gverses))}
    res["T3"] = {"counts": t3, "tests": tests3, "john_hits": jn_hits_ref}
    # Thomas hits in context (sayings numbers not annotated; give the Coptic predicate lemma)
    th = targets_t["Thomas (NHC II,2)"]
    res["T3"]["thomas_hits"] = [{"kind": kind, "next": " ".join(x["norm"] for x in th[i:i + 6])}
                                for i, kind, v in allhits["Thomas (NHC II,2)"]]

    # ---- BH across target tests
    plist = []
    for k, v in res["T1"]["texts"].items():
        if v["role"] == "target":
            plist.append(("T1 lean->John " + k, v["p_one_sided_john"]))
    plist.append(("T2a John loan share vs Synoptic chunks", res["T2a"]["test_john_vs_synoptic_chunks"]["p_two_sided"]))
    plist.append(("T2b John keep-rate, lemma-controlled", res["T2b"]["lemma_controlled"]["p_two_sided"]))
    plist.append(("T3 John I-am+noun vs Synoptics", tests3["Jn_vs_Syn"]["p_one_sided"]))
    for k, v in tests3.items():
        if k.endswith("_vs_Syn") and k != "Jn_vs_Syn":
            plist.append(("T3 " + k, v["p_two_sided"]))
    q = bh([p for _, p in plist])
    res["BH"] = [{"test": n, "p": p, "q": float(qq), "pass_q05": bool(qq < 0.05)} for (n, p), qq in zip(plist, q)]
    res["n_tests"] = len(plist)
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: res[k] for k in ("corpus_sizes_tokens", "BH")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
