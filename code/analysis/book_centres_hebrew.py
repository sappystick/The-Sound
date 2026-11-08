#!/usr/bin/env python3
"""Midpoints of Hebrew books (Westminster Leningrad Codex) by words, letters and verses.
Checks the Greek spoken-time centres found for Genesis (28:6, before Jacob's ladder 28:10-17) and the
Song of Songs (5:1) against the Hebrew text.  Usage: python3 book_centres_hebrew.py <morphhb/wlc> Gen Song ..."""
import re, sys, os, json
WLC = sys.argv[1]; out = {}
for bk in sys.argv[2:]:
    x = open(os.path.join(WLC, f"{bk}.xml"), encoding="utf-8").read()
    vs = [(m.group(1), len(re.findall(r"<w ", m.group(2))), len(re.findall(r"[א-ת]", "".join(re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2))))))
          for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S)]
    out[bk] = {}
    for idx, lab in ((1, "words"), (2, "letters")):
        T = sum(v[idx] for v in vs); acc = 0
        for v in vs:
            if acc + v[idx] > T / 2: out[bk][lab] = v[0]; break
            acc += v[idx]
    out[bk]["verses"] = vs[len(vs) // 2][0]
    print(bk, out[bk])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "book_centres_hebrew_results.json"), "w"), indent=1)
