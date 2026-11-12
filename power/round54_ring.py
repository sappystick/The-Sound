#!/usr/bin/env python3
"""Round 54. Pre-registered (robustness/PREREG_R54.md, commit dfdab0d): are the seven 'I am' sayings a ring around
the centre of John 1:1-20:31? Primary: SBLGNT words. Secondary: 01/03 lines, Sahidic tokens, Peshitta words,
shape-only ring, signs control, full-Gospel control.
Usage: python3 power/round54_ring.py
"""
import glob, json, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); T = os.path.join(ROOT, "sources/texts")
rng = np.random.default_rng(54); NULL = np.sort(rng.random((400000, 7)), axis=1)
IAM = [(6, 35), (8, 12), (10, 7), (10, 11), (11, 25), (14, 6), (15, 1)]
SIGNS = [(2, 9), (4, 50), (5, 8), (6, 11), (6, 19), (9, 7), (11, 43)]
def ring(x, centre=None):
    x = np.asarray(x); c = 0.5 if centre is None else centre
    return (np.abs((x[..., 0] + x[..., 6]) / 2 - c) + np.abs((x[..., 1] + x[..., 5]) / 2 - c) + np.abs((x[..., 2] + x[..., 4]) / 2 - c) + np.abs(x[..., 3] - c)) / 4
R_NULL = ring(NULL); R_NULL_SHAPE = ring(NULL, NULL[:, 3])
def test(units, refs, end=(20, 31)):
    units = [(r, s) for r, s in units if r <= end]; tot = sum(s for _, s in units); c = 0; pos = {}
    for r, s in units:
        pos[r] = (c + s / 2) / tot; c += s
    x = np.array([pos[r] for r in refs]); R = float(ring(x)); Rs = float(ring(x, x[3]))
    return dict(positions=[round(v, 4) for v in x], pair_midpoints=[round((x[i] + x[6 - i]) / 2, 4) for i in range(3)] + [round(x[3], 4)],
                ring_error=round(R, 4), p=round(float((R_NULL <= R).mean()), 4),
                shape_only_error=round(Rs, 4), p_shape_only=round(float((R_NULL_SHAPE <= Rs).mean()), 4))
# units
W = {}
for l in open(os.path.join(T, "sblgnt/64-Jn-morphgnt.txt"), encoding="utf-8"):
    r = (int(l[2:4]), int(l[4:6])); W[r] = W.get(r, 0) + 1
words = list(W.items())
def ms(m):
    out = []
    for l in open(os.path.join(T, "cntr/class 1", f"{m}.txt"), encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2 and p[0].startswith("43"): out.append(((int(p[0][2:5]), int(p[0][5:8])), len(re.findall(r"[/|\\]", p[1]))))
    return out
syr, ch = [], 0
for l in open(os.path.join(T, "syrnt/plain/0.1/John.txt"), encoding="utf-8"):
    l = l.strip(); m = re.match(r"^John (\d+)$", l)
    if m: ch = int(m.group(1)); continue
    m = re.match(r"^(\d+) (.*)$", l)
    if m and ch: syr.append(((ch, int(m.group(1))), len(m.group(2).split())))
NORM = re.compile(r'norm="([^"]*)"'); VN = re.compile(r'<verse_n verse_n="([^"]*)"'); cop = {}
for fn in sorted(glob.glob(os.path.join(T, "coptic_scriptorium_tt/43_John_*.tt")), key=lambda f: int(re.search(r"_(\d+)\.tt$", f).group(1))):
    cur = int(re.search(r"_(\d+)\.tt$", fn).group(1)); last, v = 0, None
    for line in open(fn, encoding="utf-8"):
        if line.startswith("<verse_n"):
            mm = VN.match(line)
            try: nv = int(mm.group(1)) if mm else None
            except ValueError: nv = None
            if nv is not None:
                if nv < last: cur += 1
                last = nv; v = nv
        elif line.startswith("<norm ") and v is not None and NORM.search(line): cop[(cur, v)] = cop.get((cur, v), 0) + 1
out = {"preregistration": "robustness/PREREG_R54.md (commit dfdab0d)"}
out["H4_primary_SBLGNT_words"] = test(words, IAM); out["H4_pass"] = out["H4_primary_SBLGNT_words"]["p"] < 0.05
out["secondary"] = {"Sinaiticus lines": test(ms("01"), IAM), "Vaticanus lines": test(ms("03"), IAM),
                    "Sahidic tokens": test(sorted(cop.items()), IAM), "Peshitta words": test(syr, IAM)}
out["controls"] = {"seven signs (no ring predicted)": test(words, SIGNS), "full Gospel to 21:25": test(words, IAM, end=(21, 25))}
json.dump(out, open(os.path.join(HERE, "round54_results.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
