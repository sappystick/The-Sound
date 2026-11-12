#!/usr/bin/env python3
"""Round 55. Pre-registered (robustness/PREREG_R55.md, commit 6b18240): T1 string-ratio cuts in performed time,
T2 'Amen, amen' at paragraph joints; exploratory E1 sacred dimensions as instrument ratios, E2 non-lexical passages.
Usage: python3 power/round55_performance.py
"""
import glob, json, math, os, re, sys, unicodedata
from fractions import Fraction as Fr
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); T = os.path.join(ROOT, "sources/texts")
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
rng = np.random.default_rng(55); out = {"preregistration": "robustness/PREREG_R55.md (commit 6b18240)"}
def bare(t): t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if not unicodedata.combining(c))
V = {}
for l in open(os.path.join(T, "sblgnt/64-Jn-morphgnt.txt"), encoding="utf-8"):
    r = (int(l[2:4]), int(l[4:6]))
    if r <= (20, 31): V.setdefault(r, []).append(l.split()[3])
refs = list(V); PAUSE = {".": 0.8, ";": 0.8, "·": 0.6, ",": 0.3}
sec = {}
for r, ws in V.items():
    _, _, t = E.build_score(E.parse_greek(" ".join(ws), "koine"), "greek", "koine", "declaim"); sec[r] = t + sum(PAUSE.get(w[-1], 0) for w in ws)
cum = np.cumsum([0] + [sec[r] for r in refs]); TOT = cum[-1]
# T1
F = np.array([1 / 9, 1 / 4, 1 / 3, 1 / 2, 2 / 3, 3 / 4, 8 / 9])
cuts = [(1, 16), (13, 33), (18, 1)]; c = np.array([cum[refs.index(x)] / TOT for x in cuts])
D = float(np.mean(np.abs(c[:, None] - F[None, :]).min(1)))
nul = np.sort(rng.random((400000, 3)), axis=1); Dn = np.abs(nul[:, :, None] - F[None, None, :]).min(2).mean(1)
p1 = float((Dn <= D).mean())
out["T1"] = dict(cut_positions=dict(zip([f"{a}:{b}" for a, b in cuts], [round(float(x), 4) for x in c])),
                 nearest_ratio=[str(Fr(float(F[np.abs(x - F).argmin()])).limit_denominator(9)) for x in c], D=round(D, 4), p=round(p1, 4),
                 performed_minutes=round(TOT / 60, 1),
                 movement_minutes=[round((cum[refs.index(b)] - cum[refs.index(a)]) / 60, 1) for a, b in zip([(1, 1)] + cuts, cuts + [refs[-1]])])
# T2
xml = open(os.path.join(T, "sblgnt-logos/data/sblgnt/xml/John.xml"), encoding="utf-8").read()
joint, cur, newp = set(), None, False
for m in re.finditer(r'<p>|<verse-number id="John (\d+):(\d+)">', xml):
    if m.group(0) == "<p>": newp = True
    else:
        cur = (int(m.group(1)), int(m.group(2)))
        if newp: joint.add(cur); newp = False
cue = [r for r, ws in V.items() if any(bare(ws[i]).strip(".,;·") == "αμην" and bare(ws[i + 1]).strip(".,;·") == "αμην" for i in range(len(ws) - 1))]
k = sum(r in joint for r in cue); n = len(cue); base = sum(r in joint for r in refs) / len(refs)
p2 = sum(math.comb(n, j) * base ** j * (1 - base) ** (n - j) for j in range(k, n + 1))
out["T2"] = dict(cue_verses=n, at_joints=k, share=round(k / n, 3), base_rate=round(base, 3), p=round(p2, 4), joints=len([r for r in refs if r in joint]))
ps = {"T1": p1, "T2": p2}; o = sorted(ps, key=ps.get); h = {o[0]: min(1, 2 * ps[o[0]])}; h[o[1]] = min(1, max(h[o[0]], ps[o[1]]))
out["holm"] = {k_: round(v, 4) for k_, v in h.items()}; out["pass"] = [k_ for k_, v in h.items() if v < 0.05]

# E1 sacred dimensions (cubits, as stated in the text)
SACRED = {"ark (Exod 25:10)": [2.5, 1.5, 1.5], "mercy seat (25:17)": [2.5, 1.5], "table (25:23)": [2, 1, 1.5], "altar of burnt offering (27:1)": [5, 5, 3],
          "incense altar (30:2)": [1, 1, 2], "tabernacle court (27:18)": [100, 50, 5], "tabernacle board (26:16)": [10, 1.5], "linen curtain (26:2)": [28, 4],
          "goat-hair curtain (26:8)": [30, 4], "Solomon's house (1 Kgs 6:2)": [60, 20, 30], "holy of holies (6:20)": [20, 20, 20], "porch (6:3)": [20, 10],
          "cherub (6:23-24)": [10, 5], "bronze sea (7:23)": [10, 5, 30], "pillar (7:15-16)": [18, 12, 5], "stand (7:27)": [4, 4, 3], "Solomon's altar (2 Chr 4:1)": [20, 20, 10],
          "Noah's ark (Gen 6:15)": [300, 50, 30]}
SECULAR = {"Og's bed (Deut 3:11)": [9, 4], "House of the Forest of Lebanon (1 Kgs 7:2)": [100, 50, 30], "Hall of Pillars (7:6)": [50, 30],
           "Nebuchadnezzar's statue (Dan 3:1)": [60, 6], "flying scroll (Zech 5:2)": [20, 10]}
CONS = [Fr(1), Fr(2), Fr(3, 2), Fr(4, 3), Fr(5, 4), Fr(5, 3), Fr(6, 5)]
def ratios(d): return [Fr(max(a, b)).limit_denominator(4) / Fr(min(a, b)).limit_denominator(4) for i, a in enumerate(d) for b in d[i + 1:]]
def share(objs): rs = [r for d in objs.values() for r in ratios(d)]; return sum(r in CONS for r in rs), len(rs)
s_k, s_n = share(SACRED); x_k, x_n = share(SECULAR)
pool = [v for d in list(SACRED.values()) + list(SECULAR.values()) for v in d]
nl = []
for _ in range(20000):
    a, b = rng.choice(pool, 2, replace=False); nl.append(Fr(max(a, b)).limit_denominator(4) / Fr(min(a, b)).limit_denominator(4) in CONS)
null_rate = float(np.mean(nl))
p_e1 = sum(math.comb(s_n, j) * null_rate ** j * (1 - null_rate) ** (s_n - j) for j in range(s_k, s_n + 1))
out["E1_sacred_dimensions"] = dict(sacred=f"{s_k}/{s_n}", sacred_share=round(s_k / s_n, 3), secular=f"{x_k}/{x_n}", null_pool_rate=round(null_rate, 3), p_sacred_vs_pool=round(p_e1, 4),
    detail={k_: [str(r) for r in ratios(d)] for k_, d in SACRED.items()})
# E2 non-lexical passages
def heb_verses():
    for f in sorted(glob.glob(os.path.join(T, "morphhb/wlc/*.xml"))):
        t = open(f, encoding="utf-8").read()
        for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', t, re.S):
            ws = [re.sub(r"[^א-ת]", "", re.sub(r"<[^>]+>", "", w)) for w in re.findall(r"<w[^>]*>(.*?)</w>", m.group(2))]
            yield m.group(1), [w for w in ws if w]
def rep_score(ws):
    if len(ws) < 8: return None
    big = list(zip(ws, ws[1:])); return round(1 - (len(set(ws)) / len(ws) + len(set(big)) / len(big)) / 2, 3)
H = sorted(((s, r) for r, ws in heb_verses() if (s := rep_score(ws)) is not None), reverse=True)
rank = {r: i + 1 for i, (_, r) in enumerate(H)}
G = {}
for f in sorted(glob.glob(os.path.join(T, "sblgnt/*-morphgnt.txt"))):
    for l in open(f, encoding="utf-8"):
        p = l.split(); G.setdefault(os.path.basename(f).split("-")[1] + " " + f"{int(p[0][2:4])}:{int(p[0][4:6])}", []).append(re.sub(r"[^α-ω]", "", bare(p[3])))
Gs = sorted(((s, r) for r, ws in G.items() if (s := rep_score(ws)) is not None), reverse=True)
out["E2_nonlexical"] = dict(hebrew_verses=len(H), isa_28_10_rank=rank.get("Isa.28.10"), isa_28_13_rank=rank.get("Isa.28.13"),
    hebrew_top15=[(r, s) for s, r in H[:15]], greek_nt_top15=[(r, s) for s, r in Gs[:15]], john_top5=[(r, s) for s, r in Gs if r.startswith("Jn ")][:5])
json.dump(out, open(os.path.join(HERE, "round55_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:5000])
