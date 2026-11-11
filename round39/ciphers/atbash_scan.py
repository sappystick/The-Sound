"""Part 1. ATBASH / ALBAM discovery scan of the Hebrew Bible, with random-cipher nulls.

Hypothesis (stated before running): the two ancient substitution ciphers (atbash: א<->ת, ב<->ש, ...;
albam: א<->ל, ב<->מ, ...) were used deliberately in a few places (known: Jer 25:26, 51:41 ששך = בבל;
Jer 51:1 לב קמי = כשדים). If so, atbash should produce more "thematic hits" than arbitrary
letter-substitution ciphers, at least in Jeremiah.

Unit: every word stem (consonants, final forms normalised, prefixed conjunction/article/
prepositions stripped) of >= 3 letters, and every pair of adjacent stems joined (for לב קמי).
Hit: cipher(unit) is a proper noun or gentilic form attested in the Bible (morph Np / Ng) AND that
form occurs elsewhere in the same chapter (the decoded name is on the scene). Primary statistic:
"rare hits" = hits whose source unit occurs <= 2 times in the whole Bible (coined cipher words are
rare; common words that happen to transform into a name are not cipher candidates).
Null: 20000 random fixed-point-free involutions of the 22 letters (same structure as atbash/albam,
which are both 11 swaps) and 5000 random permutations. p = (1 + #null >= observed)/(N+1).
Decision: a cipher "works" in a book if its rare-hit count beats the random-cipher distribution at
BH q <= 0.05 across all tests of the round. Positive control: the three Jeremiah decodings must be
found.

Usage: python3 atbash_scan.py <wlc_dir> <out_json>
"""
import json
import sys
from collections import Counter, defaultdict

import numpy as np

import textlib as T

A = T.HEB_ALPHA


def cipher_table(perm):
    return str.maketrans(A, "".join(A[i] for i in perm))


ATBASH = list(range(21, -1, -1))
ALBAM = [(i + 11) % 22 for i in range(22)]


def random_involution(rng):
    idx = rng.permutation(22)
    perm = [0] * 22
    for k in range(0, 22, 2):
        a, b = idx[k], idx[k + 1]
        perm[a], perm[b] = b, a
    return perm


def main(wlc_dir, out_json):
    verses = T.load_wlc(wlc_dir)
    # unit occurrences: (form, verse_index, is_pair)
    chap_of = []
    chap_forms = defaultdict(Counter)  # chapter key -> Counter of stems (singles)
    target = set()  # proper nouns / gentilics
    units = []  # (form, vi, kind, display)
    for vi, v in enumerate(verses):
        ck = (v["book"], v["ch"])
        chap_of.append(ck)
        stems = [w["stem"] for w in v["words"]]
        for w in v["words"]:
            chap_forms[ck][w["stem"]] += 1
            m = w["morph"]
            if ("Np" in m or "Ng" in m) and len(w["stem"]) >= 3:
                target.add(w["stem"])
        for k, s in enumerate(stems):
            if len(s) >= 3:
                units.append((s, vi, "single"))
            if k + 1 < len(stems) and len(s) >= 2 and len(stems[k + 1]) >= 2:
                units.append((s + stems[k + 1], vi, "pair"))
    freq = Counter(u[0] for u in units)
    # unique forms -> list of (vi)
    occ = defaultdict(list)
    for f, vi, kind in units:
        occ[f].append(vi)
    forms = list(occ.keys())
    rare = {f for f in forms if freq[f] <= 2}
    print("verses", len(verses), "units", len(units), "unique", len(forms), "targets", len(target),
          file=sys.stderr)

    books = T.HEB_BOOKS

    target_list = sorted(target)
    cands = []

    def score(perm, keep=False):
        # f -> c(f) in target  <=>  f = c^-1(t); invert the cipher and look targets up
        inv = [0] * 22
        for i, j in enumerate(perm):
            inv[j] = i
        itab = cipher_table(inv)
        per_book_all = Counter()
        per_book_rare = Counter()
        hits = []
        cands.clear()
        for g in target_list:
            f = g.translate(itab)
            if f == g or f not in occ:
                continue
            for vi in occ[f]:
                ck = chap_of[vi]
                n_in_chap = chap_forms[ck].get(g, 0)
                if n_in_chap == 0:
                    continue
                b = ck[0]
                per_book_all[b] += 1
                if keep and freq[f] <= 5:
                    v = verses[vi]
                    cands.append(dict(ref="%s %d:%d" % (v["book"], v["ch"], v["v"]), source=f,
                                      decoded=g, source_freq=freq[f], decoded_in_chapter=n_in_chap))
                if f in rare:
                    per_book_rare[b] += 1
                    if keep:
                        v = verses[vi]
                        hits.append(dict(ref="%s %d:%d" % (v["book"], v["ch"], v["v"]), source=f,
                                         decoded=g, source_freq=freq[f], decoded_in_chapter=n_in_chap))
        return per_book_all, per_book_rare, hits

    res = {}
    obs = {}
    for name, perm in (("atbash", ATBASH), ("albam", ALBAM)):
        a, r, hits = score(perm, keep=True)
        obs[name] = (a, r)
        res[name] = dict(total_all=sum(a.values()), total_rare=sum(r.values()),
                         per_book_rare=dict(r), per_book_all=dict(a), rare_hits=hits,
                         candidates_freq_le5=list(cands))
    # positive controls
    ctrl = {"Jer 25:26": ("ששכ", "בבל"), "Jer 51:41": ("ששכ", "בבל"), "Jer 51:1": ("לבקמי", "כשדימ")}
    found = {}
    for ref, (src, dec) in ctrl.items():
        found[ref] = any(h["ref"] == ref and h["source"] == src and h["decoded"] == dec
                         for h in res["atbash"]["rare_hits"])
    res["positive_controls_found"] = found

    rng = np.random.default_rng(39001)
    null = {}
    for kind, n in (("involution", 20000), ("permutation", 5000)):
        tot_r = np.zeros(n)
        tot_a = np.zeros(n)
        pb = np.zeros((n, len(books)))
        for i in range(n):
            perm = random_involution(rng) if kind == "involution" else list(rng.permutation(22))
            a, r, _ = score(perm)
            tot_r[i] = sum(r.values())
            tot_a[i] = sum(a.values())
            pb[i] = [r.get(b, 0) for b in books]
            if i % 5000 == 0:
                print(kind, i, file=sys.stderr)
        null[kind] = (tot_r, tot_a, pb)
    tests = []
    for name in ("atbash", "albam"):
        a, r = obs[name]
        for kind in ("involution", "permutation"):
            tot_r, tot_a, pb = null[kind]
            n = len(tot_r)
            o = sum(r.values())
            res[name]["null_" + kind] = dict(
                n=n, rare_mean=float(tot_r.mean()), rare_sd=float(tot_r.std()),
                rare_p=float((1 + (tot_r >= o).sum()) / (n + 1)),
                all_mean=float(tot_a.mean()), all_obs=sum(a.values()),
                all_p=float((1 + (tot_a >= sum(a.values())).sum()) / (n + 1)),
                rare_quantiles=[float(x) for x in np.quantile(tot_r, [0.5, 0.9, 0.99])])
        # per-book vs involution null (primary)
        tot_r, tot_a, pb = null["involution"]
        n = len(tot_r)
        per = {}
        for j, b in enumerate(books):
            ob = r.get(b, 0)
            p = float((1 + (pb[:, j] >= ob).sum()) / (n + 1))
            per[b] = dict(obs=ob, null_mean=float(pb[:, j].mean()), p=p)
            tests.append(dict(test="%s rare hits in %s vs random involutions" % (name, b), p=p,
                              family="cipher_book", known=(name == "atbash" and b == "Jer")))
        res[name]["per_book_vs_involution"] = per
        tests.append(dict(test="%s total rare hits vs random involutions" % name,
                          p=res[name]["null_involution"]["rare_p"], family="cipher_total"))
        tests.append(dict(test="%s total rare hits vs random permutations" % name,
                          p=res[name]["null_permutation"]["rare_p"], family="cipher_total"))
    # where does atbash rank among random involutions in Jeremiah
    j = books.index("Jer")
    res["jeremiah_rank"] = {nm: float((null["involution"][2][:, j] >= obs[nm][1].get("Jer", 0)).mean())
                            for nm in ("atbash", "albam")}
    # best random cipher anywhere: how many rare hits do the top 1% random ciphers produce
    res["tests"] = tests
    res["n_units"] = len(units)
    res["n_unique_forms"] = len(forms)
    res["n_targets"] = len(target)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
