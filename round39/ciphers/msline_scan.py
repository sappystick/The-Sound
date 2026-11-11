"""Part 3. Manuscript-line acrostics and telestichs in John: P66, P75, Sinaiticus (01), Vaticanus (03).

Hypothesis (expected negative): a scribe hid words in the first letters (acrostic) or last letters
(telestich) of the physical lines of John. Lines and columns come from the CNTR transcriptions
('/' line break, '\\' page break, '|' column break). Letters not visible on the manuscript (followed
by '^', words supplied with '~', lines lost '&') are '?', which no word can cross.
Measure: number of dictionary words (SBLGNT forms + lemmas, accents removed, all sigmas = σ) of
length >= 4 (and, separately, >= 5) read downwards inside one column, in the line-initial string and
in the line-final string. Null: shuffle the order of all lines of the manuscript's John 1000 times
and re-cut into the same column sizes (keeps the letter frequencies of line starts and ends);
p = (1 + #null >= observed)/(N+1). 4 manuscripts x 2 strings x 2 lengths = 16 tests.
Positive control for the reader: the same counter applied to an implanted acrostic (the word
ΙΗΣΟΥΣ forced into the first letters of six consecutive lines of a shuffled copy) must count it.

Usage: python3 msline_scan.py <cntr_class1_dir> <sblgnt_dir> <out_json>
"""
import json
import os
import sys

import numpy as np

import textlib as T


def count_words(cols, lex, minlen, maxlen=10, keep=None):
    c = 0
    for col in cols:
        s = "".join(col)
        n = len(s)
        for L in range(minlen, maxlen + 1):
            for i in range(n - L + 1):
                w = s[i:i + L]
                if w in lex:
                    c += 1
                    if keep is not None:
                        keep.append(w)
    return c


def main(cntr, sbl, out_json):
    _, lex = T.load_sblgnt(sbl)
    lex = {w for w in lex if len(w) >= 4}
    rng = np.random.default_rng(39003)
    res = {"lexicon_size_len4plus": len(lex), "manuscripts": {}}
    tests = []
    for ms in ("P66", "P75", "01", "03"):
        cols = T.load_cntr_lines(os.path.join(cntr, ms + ".txt"), columns=True)
        lines = [l for c in cols for l in c]
        sizes = [len(c) for c in cols]
        first = [l[0] for l in lines]
        last = [l[-1] for l in lines]
        out = dict(n_lines=len(lines), n_columns=len(cols),
                   unknown_first=sum(1 for x in first if x == "?"),
                   unknown_last=sum(1 for x in last if x == "?"))

        def recut(seq):
            o, k = [], 0
            for s in sizes:
                o.append(seq[k:k + s])
                k += s
            return o
        for nm, seq in (("acrostic_first_letters", first), ("telestich_last_letters", last)):
            for minlen in (4, 5):
                found = []
                obs = count_words(recut(seq), lex, minlen, keep=found)
                null = np.zeros(1000)
                for i in range(1000):
                    null[i] = count_words(recut(list(rng.permutation(seq))), lex, minlen)
                p = float((1 + (null >= obs).sum()) / 1001)
                key = "%s_len%d" % (nm, minlen)
                out[key] = dict(obs=obs, null_mean=float(null.mean()), null_sd=float(null.std()),
                                p=p, ratio=float(obs / null.mean()) if null.mean() else None,
                                words=sorted(set(found), key=len, reverse=True)[:15])
                tests.append(dict(test="John %s %s len>=%d" % (ms, nm, minlen), p=p,
                                  family="msline"))
        # positive control: implant ιησουσ in a shuffled copy at a random column start
        sh = list(rng.permutation(first))
        cs = recut(sh)
        big = [i for i, c in enumerate(cols) if len(c) >= 8]
        ci = big[0]
        cs[ci][:6] = list("ιησουσ")
        kept = []
        count_words(cs, {"ιησουσ"}, 6, 6, keep=kept)
        out["implant_control_found"] = len(kept) >= 1
        res["manuscripts"][ms] = out
        print(ms, "done", file=sys.stderr)
    res["tests"] = tests
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
