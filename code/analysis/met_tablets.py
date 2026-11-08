#!/usr/bin/env python3
"""Cuneiform Texts in the Metropolitan Museum of Art I (OCR of the user's scan; text not stored).
Lists the genres, then the passages that touch the project's threads: temples and their builders (Gudea, Ur-Nammu,
Sulgi), 'heaven and earth' temple names (Duranki / Eduranki, 'bond of heaven and earth'), the sevenfold prostration
of the Amarna letters, and the letters to Egypt.  Usage: python3 met_tablets.py <ocr text of the whole volume>"""
import re, sys, collections
t = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
gen = collections.Counter(m.group(1).strip() for m in re.finditer(r"MMA [\d.]+[^\n]*?\s((?:Receipt|Account|Loan|Royal letter|Letter|List|Contract|Brick inscription|Cone|Delivery|Record|Votive|Sale|Lawsuit)[^\n:,]{0,20})", t))
print("genres (first words of the catalogue headings):", gen.most_common(12))
for lab, pat in (("temple-building", r"built (the|her|his) [^\n]{0,40}"), ("bond of heaven and earth", r"[Dd]uranki|[Ee]duranki|heaven and earth"),
                 ("sevenfold prostration", r"7 times and 7 times|seven times"), ("Egypt", r"king of (the land of )?E[^\n]{0,4}gypt")):
    hits = [re.sub(r"\s+", " ", t[max(0, m.start() - 60): m.end() + 60]) for m in re.finditer(pat, t)]
    print(f"\n{lab}: {len(hits)}"); [print("   …" + h + "…") for h in hits[:4]]
