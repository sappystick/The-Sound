"""Part 4. Equidistant letter sequences (ELS, "Bible codes"): a calibration with honest controls.

Background: Witztum, Rips & Rosenberg (1994, Statistical Science 9:429-438) claimed ELS of rabbis'
names near their dates in Genesis; McKay, Bar-Natan, Bar-Hillel & Kalai (1999, Statistical Science
14:150-173, "Solving the Bible Code Puzzle") showed the result came from choices in the data (name
spellings, dates) and obtained an equally strong result in War and Peace. The popular "תורה at skip
50" (attributed to R. Weissmandl; Drosnin 1997, Satinover 1997) is the claim tested here.

Tests (fixed before running):
 A. Weissmandl pattern. For every one of the 39 books: is there an ELS of תורה, read forward or
    backward, at skip exactly 50, whose earliest letter lies within the first 400 letters of the
    book (Weissmandl's Deuteronomy reading starts at 1:5)? Count Torah books vs others. Then the same question for every 4-letter
    word form of the Hebrew Bible (a vocabulary null): how many words "start a book at skip 50"?
 B. Rate. For a fixed target set (תורה יהוה אלהים ישראל משיח ישוע שלום ירושלמ ברית כהנ), count ELS
    (both directions, |skip| 2..100) in Genesis, in 100 letter-shuffled Genesis copies, and in a
    control text of equal length (Isaiah + Jeremiah, first N letters). Also the expectation from
    letter frequencies: E = sum_d (N-(k-1)d) * prod p(letter). Genesis "has codes" only if its count
    exceeds the shuffled copies.
Consonantal WLC text (ketiv), final letters normalised. Note WRR used the Koren text; WLC differs in
a few dozen letters in Genesis, which does not matter for a rate calibration.

Usage: python3 els_calibration.py <wlc_dir> <out_json>
"""
import json
import sys
from collections import Counter

import numpy as np

import textlib as T

A = T.HEB_ALPHA
TARGETS = ["תורה", "יהוה", "אלהימ", "ישראל", "משיח", "ישוע", "שלומ", "ירושלמ", "ברית", "כהנ"]


def enc(s):
    return np.array([A.index(c) for c in s], dtype=np.int8)


def count_els(arr, word, dmin=2, dmax=100):
    w = enc(word)
    k = len(w)
    N = len(arr)
    tot = 0
    for d in range(dmin, dmax + 1):
        L = N - (k - 1) * d
        if L <= 0:
            break
        m = arr[0:L] == w[0]
        for j in range(1, k):
            m &= arr[j * d:j * d + L] == w[j]
        tot += int(m.sum())
    return tot


def count_both(arr, word, dmin=2, dmax=100):
    c = count_els(arr, word, dmin, dmax)
    rw = word[::-1]
    if rw != word:
        c += count_els(arr, rw, dmin, dmax)
    return c


def expected(arr, word, dmin=2, dmax=100):
    N = len(arr)
    fr = np.bincount(arr, minlength=22) / N
    pr = float(np.prod([fr[A.index(c)] for c in word]))
    k = len(word)
    e = sum(max(0, N - (k - 1) * d) for d in range(dmin, dmax + 1)) * pr
    rw = word[::-1]
    return 2 * e if rw != word else e


W = 400


def starts_at_skip(arr, word, d=50, window=W):
    """Positions < window where `word` or its reverse is spelled at skip d (text order), i.e. an
    ELS of the word at skip +d or -d whose earliest letter lies in the first `window` letters."""
    hits = []
    for ww in {word, word[::-1]}:
        w = enc(ww)
        for i in range(min(window, len(arr) - (len(w) - 1) * d)):
            if all(arr[i + j * d] == w[j] for j in range(len(w))):
                hits.append((i, "forward" if ww == word else "backward"))
    return hits


def main(wlc_dir, out_json):
    verses = T.load_wlc(wlc_dir)
    books = {}
    for v in verses:
        books.setdefault(v["book"], []).append("".join(w["cons"] for w in v["words"]))
    text = {b: "".join(vs) for b, vs in books.items()}
    arrs = {b: enc(t) for b, t in text.items()}
    res = {}
    tests = []
    # ---------------- A. Weissmandl pattern
    wa = {}
    for b in T.HEB_BOOKS:
        h = starts_at_skip(arrs[b], "תורה")
        wa[b] = dict(hits=h, any=bool(h))
    res["weissmandl"] = dict(window_letters=W, per_book=wa,
                             books_with_pattern=[b for b in T.HEB_BOOKS if wa[b]["any"]],
                             genesis_first_tav_index=text["Gen"].index("ת"))
    # vocabulary null: all 4-letter forms; fraction having forward skip-50 ELS starting in first
    # 100 letters of Genesis, and the number of books in which each form does so
    vocab = Counter()
    for v in verses:
        for w in v["words"]:
            if len(w["cons"]) == 4:
                vocab[w["cons"]] += 1
    vocab = [w for w, c in vocab.items() if c >= 5]
    g = arrs["Gen"]
    n_gen = sum(1 for w in vocab if starts_at_skip(g, w))
    per_word_books = []
    for w in vocab:
        nb = sum(1 for b in ("Gen", "Exod", "Lev", "Num", "Deut") if starts_at_skip(arrs[b], w))
        per_word_books.append(nb)
    pwb = np.array(per_word_books)
    torah_n = sum(1 for b in ("Gen", "Exod", "Lev", "Num", "Deut") if wa[b]["any"])
    res["weissmandl"]["vocabulary_null"] = dict(
        n_words=len(vocab), frac_words_with_skip50_start_in_Gen=n_gen / len(vocab),
        torah_books_with_torah_pattern=torah_n,
        frac_words_in_ge_that_many_torah_books=float((pwb >= torah_n).mean()),
        distribution=dict(Counter(per_word_books)))
    p_w = float((1 + (pwb >= torah_n).sum()) / (len(pwb) + 1))
    res["weissmandl"]["p_fixed_word_fixed_skip"] = p_w
    # wiggle room (McKay et al.'s point): the word and the skip were chosen after looking.
    # Over all skips 2..100 and all frequent 4-letter words, how many (word, skip) pairs open
    # >= 3 of 5 consecutive books, in the Torah and in control quintets?
    vset = set(vocab)

    def quintet(bks):
        hitcount = Counter()
        for d in range(2, 101):
            for b in bks:
                t = text[b]
                grams = {t[i] + t[i + d] + t[i + 2 * d] + t[i + 3 * d] for i in range(W)}
                found = {x for x in grams if x in vset} | {x[::-1] for x in grams if x[::-1] in vset}
                for x in found:
                    hitcount[(x, d)] += 1
        ge3 = sorted([(x, d, c) for (x, d), c in hitcount.items() if c >= 3], key=lambda z: -z[2])
        return dict(n_pairs_ge3=len(ge3), n_pairs_ge4=sum(1 for z in ge3 if z[2] >= 4),
                    examples=[dict(word=x, skip=d, books=c) for x, d, c in ge3[:12]])
    quints = {"Torah": ["Gen", "Exod", "Lev", "Num", "Deut"],
              "Former prophets": ["Josh", "Judg", "1Sam", "2Sam", "1Kgs"],
              "Latter prophets": ["Isa", "Jer", "Ezek", "Hos", "Joel"],
              "Writings": ["Ps", "Prov", "Job", "Song", "Ruth"]}
    res["weissmandl"]["wiggle_room"] = {k: quintet(v) for k, v in quints.items()}
    nq = [res["weissmandl"]["wiggle_room"][k]["n_pairs_ge3"] for k in quints]
    # search-corrected p: chance that a quintet shows >=1 such pair, estimated from the 3 controls
    res["weissmandl"]["controls_with_any_pair_ge3"] = sum(1 for x in nq[1:] if x > 0)
    tests.append(dict(test="Weissmandl: Torah quintet has more (word,skip) book-opening ELS than control quintets",
                      p=float((1 + sum(1 for x in nq[1:] if x >= nq[0])) / (len(nq[1:]) + 1)),
                      family="els"))
    # ---------------- B. rates
    N = len(g)
    ctrl = np.concatenate([arrs["Isa"], arrs["Jer"]])[:N]
    rng = np.random.default_rng(39004)
    shuf = [rng.permutation(g) for _ in range(100)]
    rate = {}
    for w in TARGETS:
        og = count_both(g, w)
        oc = count_both(ctrl, w)
        sh = np.array([count_both(s, w) for s in shuf])
        p = float((1 + (sh >= og).sum()) / 101)
        rate[w] = dict(genesis=og, isaiah_jeremiah_same_length=oc, shuffled_mean=float(sh.mean()),
                       shuffled_sd=float(sh.std()), expected_from_frequencies=expected(g, w),
                       p_genesis_ge_shuffled=p)
        tests.append(dict(test="ELS count of %s (|skip| 2-100) in Genesis vs letter-shuffled Genesis" % w,
                          p=p, family="els"))
        print(w, rate[w], file=sys.stderr)
    tot_g = sum(r["genesis"] for r in rate.values())
    tot_c = sum(r["isaiah_jeremiah_same_length"] for r in rate.values())
    tot_s = sum(r["shuffled_mean"] for r in rate.values())
    res["rates"] = dict(per_word=rate, total_genesis=tot_g, total_control=tot_c,
                        total_shuffled_mean=tot_s, genesis_letters=int(N))
    res["tests"] = tests
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
