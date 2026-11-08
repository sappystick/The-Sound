#!/usr/bin/env python3
"""Extract the interpretative (spaced, accented) Greek text of PGM I and PGM VI+II from E. Chronopoulou,
'Edition of the Greek Magical Papyri (PGM) I and VI+II' (doctoral thesis, Universitat Pompeu Fabra, 2017).
The thesis prints, on facing pages, a diplomatic transcript (unspaced capitals with lunate sigma) and an
interpretative edition; only the latter is kept. The extracted text is NOT stored in this repository (the thesis
is under copyright); only statistics derived from it are.
Usage: python3 pgm_extract.py <tec.txt from pdftotext -layout> <out.txt>
"""
import re, sys
pages = open(sys.argv[1], encoding="utf-8").read().split("\f")
RANGES = {"PGM I": range(47, 83), "PGM VI+II": range(208, 241)}
ACC = re.compile(r"[ἀ-῿ΆΈ-ΊΌΎ-ΐά-ίό-ώ]")
out = []
for name, rg in RANGES.items():
    lines = []
    for n in rg:
        for line in pages[n - 1].split("\n"):
            s = re.sub(r"^\s*(Col\.\s*[IVX]+)?\s*\d*\s*", "", line).rstrip()
            toks = s.split()
            greek = [t for t in toks if re.search(r"[Ͱ-Ͽἀ-῿]", t)]
            if len(greek) >= 2 and ACC.search(s) and "ϲ" not in s: lines.append(s)
    text = " ".join(lines)
    text = re.sub(r"-\s+", "", text)                      # rejoin words broken at line ends
    text = text.replace("µ", "μ").replace("ϲ", "σ")
    text = re.sub(r"[\[\]⟦⟧<>{}()̣]", "", text)            # editorial brackets and under-dots
    out.append(f"### {name}\n{text}\n")
    print(name, len(text.split()), "words")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
