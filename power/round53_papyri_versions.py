#!/usr/bin/env python3
"""Round 53. Pre-registered (robustness/PREREG_R53.md, commit abfcfd8): John 10:11 at the centre of John 1:1-20:31 in
the Peshitta and the Sahidic (H2, words/tokens) and in P66 and P75 (H3, letters with reconstruction of lacunae).
Usage: python3 power/round53_papyri_versions.py
"""
import glob, json, os, re, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); T = os.path.join(ROOT, "sources/texts")
rng = np.random.default_rng(53); SIMS = np.sort(rng.random((400000, 7)), axis=1)[:, 3]
def p_mid(x): return float((np.abs(SIMS - 0.5) <= abs(x - 0.5)).mean())
END = (20, 31)
def position(units):  # units: ordered list of (ref, size)
    units = [(r, s) for r, s in units if r <= END]; tot = sum(s for _, s in units); c = 0; x = None; centre = None
    for r, s in units:
        if r == (10, 11): x = (c + s / 2) / tot
        if centre is None and c + s >= tot / 2: centre = f"{r[0]}:{r[1]}"
        c += s
    return dict(position=round(x, 4), p=round(p_mid(x), 4), total=round(tot, 1), centre_verse=centre)
out = {"preregistration": "robustness/PREREG_R53.md (commit abfcfd8)"}

# H2a Syriac
syr, ch = [], 0
for l in open(os.path.join(T, "syrnt/plain/0.1/John.txt"), encoding="utf-8"):
    l = l.strip(); m = re.match(r"^John (\d+)$", l)
    if m: ch = int(m.group(1)); continue
    m = re.match(r"^(\d+) (.*)$", l)
    if m and ch: syr.append(((ch, int(m.group(1))), m.group(2).split()))
out["H2_syriac_words"] = position([(r, len(w)) for r, w in syr])
out["syriac_letters (secondary)"] = position([(r, sum(len(re.sub(r"[^ܐ-ܯ]", "", x)) for x in w)) for r, w in syr])
# H2b Sahidic
NORM = re.compile(r'norm="([^"]*)"'); VN = re.compile(r'<verse_n verse_n="([^"]*)"')
cop = {}
for fn in sorted(glob.glob(os.path.join(T, "coptic_scriptorium_tt/43_John_*.tt")), key=lambda f: int(re.search(r"_(\d+)\.tt$", f).group(1))):
    chn = int(re.search(r"_(\d+)\.tt$", fn).group(1)); cur, last, v = chn, 0, None
    for line in open(fn, encoding="utf-8"):
        if line.startswith("<verse_n"):
            m = VN.match(line)
            try:
                nv = int(m.group(1)) if m else None
            except ValueError: nv = None
            if nv is not None:
                if nv < last: cur += 1
                last = nv; v = nv
        elif line.startswith("<norm ") and v is not None:
            m = NORM.search(line)
            if m: cop.setdefault((cur, v), []).append(m.group(1))
copl = sorted(cop.items())
out["H2_sahidic_tokens"] = position([(r, len(t)) for r, t in copl])
out["sahidic_letters (secondary)"] = position([(r, sum(len(x) for x in t)) for r, t in copl])
out["H2_pass"] = out["H2_syriac_words"]["p"] < 0.05 and out["H2_sahidic_tokens"]["p"] < 0.05

# H3 papyri with reconstruction
def bare(t): t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if not unicodedata.combining(c))
SBL = {}
for l in open(os.path.join(T, "sblgnt/64-Jn-morphgnt.txt"), encoding="utf-8"):
    r = (int(l[2:4]), int(l[4:6])); SBL[r] = SBL.get(r, 0) + len(re.sub(r"[^α-ω]", "", bare(l.split()[3]).replace("ς", "σ")))
def papyrus(ms):
    own, preserved = {}, set()
    for l in open(os.path.join(T, "cntr/class 1", f"{ms}.txt"), encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) < 2 or not p[0].startswith("43"): continue
        r = (int(p[0][2:5]), int(p[0][5:8])); s = p[1]
        s = re.sub(r"x\{[^}]*\}", "", s); s = re.sub(r"[abc]\{[^}]*\}", "", s)   # keep the corrected reading once
        if "^" not in s and "~" not in s and r in SBL: preserved.add(r)
        own[r] = len(re.sub(r"[^α-ωϲ]", "", bare(s)))
    ratio = sum(own[r] for r in preserved) / max(1, sum(SBL[r] for r in preserved))
    units = [(r, own[r] if r in preserved else SBL[r] * ratio) for r in sorted(SBL)]
    mass = sum(s for r, s in units if r <= END); own_mass = sum(s for r, s in units if r <= END and r in preserved)
    res = position(units); res.update(preserved_verses=len([r for r in preserved if r <= END]), coverage=round(own_mass / mass, 3), letter_ratio=round(ratio, 3),
                                      last_preserved=f"{max(preserved)[0]}:{max(preserved)[1]}" if preserved else None)
    return res
out["H3_P66"] = papyrus("P66"); out["H3_P75"] = papyrus("P75")
out["H3_pass"] = out["H3_P66"]["p"] < 0.05 and out["H3_P75"]["p"] < 0.05
ps = {"H2": max(out["H2_syriac_words"]["p"], out["H2_sahidic_tokens"]["p"]), "H3": max(out["H3_P66"]["p"], out["H3_P75"]["p"])}
o = sorted(ps, key=ps.get); holm = {o[0]: min(1, 2 * ps[o[0]])}; holm[o[1]] = min(1, max(holm[o[0]], ps[o[1]]))
out["holm"] = dict(raw=ps, adjusted={k: round(v, 4) for k, v in holm.items()})
json.dump(out, open(os.path.join(HERE, "round53_results.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
