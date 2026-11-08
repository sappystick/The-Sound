#!/usr/bin/env python3
"""John's sound map: noise share verse by verse, against the theme blocks, the speakers and the structure.

 1. MAP: noise share (stops and fricatives against voiced sounds) for every verse, on John's spoken timeline,
    smoothed over 15 verses; the quietest and noisiest stretches.
 2. THEMES: does each theme's density curve (water, light, bread, life, hour, glory, abide, love, world, sent,
    truth, witness, sign, spirit, darkness) rise where John goes quiet?  Correlation with the noise curve,
    against circular shifts of the theme curve (keeps its clustering).  Benjamini-Hochberg over themes.
 3. SPEECH vs NARRATIVE: verses with a first- or second-person verb (speech) against third-person narrative.
 4. STRUCTURE: noise at the prologue's centre (1:12-13), at the 'I am' sayings, at the book's centre (10:24),
    at the seams found earlier (3:22, 6:1, 9:1, 18:1).
 5. THE ARC: does John's noise curve have a shape (falling, rising, U, wave)?  Compared with Matthew, Mark, Luke.
Writes john_noise_map.png (if matplotlib is present) and john_noise_map_results.json.
Usage: python3 john_noise_map.py <sblgnt dir>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(4); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
OBS = {"p", "b", "t", "d", "k", "g", "pʰ", "tʰ", "kʰ", "f", "v", "θ", "ð", "s", "z", "x", "ɣ", "ç", "ʝ", "h", "ps", "ks", "β", "φ", "dz", "ts"}
cache = {}
def phon(raw):
    k = unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw.lower()))
    if k not in cache:
        try: cache[k] = [p for s in E.parse_greek(k, "koine")[0] for p in s["ph"]]
        except Exception: cache[k] = []
    return cache[k]
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def load(code):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); r = (int(p[0][2:4]), int(p[0][4:6])); e = V.setdefault(r, dict(obs=0, n=0, lem=[], person=set()))
        ph = phon(p[3]); e["obs"] += sum(x in OBS for x in ph); e["n"] += len(ph); e["lem"].append(nrm(p[6]))
        if p[1].startswith("V") and p[2][0] in "12": e["person"].add(p[2][0])
    return V
def curve(V, win=15):
    keys = list(V); obs = np.array([V[k]["obs"] for k in keys], float); n = np.array([V[k]["n"] for k in keys], float)
    ker = np.ones(win); sm = np.convolve(obs, ker, "same") / np.maximum(np.convolve(n, ker, "same"), 1)
    pos = np.cumsum(n) / n.sum() - n / (2 * n.sum()); return keys, obs / np.maximum(n, 1), sm, pos
JN = load("Jn"); keys, raw, sm, pos = curve(JN)
overall = sum(v["obs"] for v in JN.values()) / sum(v["n"] for v in JN.values())
print(f"1. MAP: John's noise share {overall:.3f}; smoothed range {sm.min():.3f}-{sm.max():.3f}")
order = np.argsort(sm); qs, ls = [], []
for idx, bucket, lab in ((order, qs, "quietest"), (order[::-1], ls, "noisiest")):
    for i in idx:
        if all(abs(i - j) > 25 for j in bucket): bucket.append(i)
        if len(bucket) == 5: break
    print(f"   {lab} stretches (centre verse, smoothed noise): " + ", ".join(f"{keys[i][0]}:{keys[i][1]} ({sm[i]:.3f})" for i in bucket))
out["quiet"] = [f"{keys[i][0]}:{keys[i][1]}" for i in qs]; out["loud"] = [f"{keys[i][0]}:{keys[i][1]}" for i in ls]

print("\n2. THEMES against the noise curve (negative r = the theme rises where John goes quiet)")
TH = {"water": ["υδωρ"], "light": ["φωσ"], "darkness": ["σκοτια", "σκοτοσ"], "bread": ["αρτοσ"], "life": ["ζωη"], "hour": ["ωρα"], "glory": ["δοξα", "δοξαζω"],
      "abide": ["μενω"], "love": ["αγαπαω", "αγαπη", "φιλεω"], "world": ["κοσμοσ"], "sent": ["πεμπω", "αποστελλω"], "truth": ["αληθεια", "αληθησ", "αληθινοσ"],
      "witness": ["μαρτυρια", "μαρτυρεω"], "sign": ["σημειον"], "spirit": ["πνευμα"], "believe": ["πιστευω"], "Father": ["πατηρ"], "I am (ego eimi)": None}
rows = []
for th, lems in TH.items():
    if lems is None: d = np.array([float(any(a == "εγω" and b == "ειμι" for a, b in zip(JN[k]["lem"], JN[k]["lem"][1:]))) for k in keys])
    else: d = np.array([float(sum(l in lems for l in JN[k]["lem"])) for k in keys])
    ds = np.convolve(d, np.ones(15), "same"); r = np.corrcoef(ds, sm)[0, 1]
    null = [np.corrcoef(np.roll(ds, s), sm)[0, 1] for s in rng.integers(30, len(ds) - 30, 2000)]
    p = (np.sum(np.abs(null) >= abs(r)) + 1) / 2001; rows.append((p, th, r))
rows.sort(); m = len(rows); cut = max([i for i, x in enumerate(rows, 1) if x[0] <= 0.10 * i / m], default=0)
for i, (p, th, r) in enumerate(rows): print(f"   {th:16s} r = {r:+.2f}  p = {p:.3f}{'  *survives correction' if i < cut else ''}")
out["themes"] = {th: dict(r=round(float(r), 3), p=float(p)) for p, th, r in rows}

print("\n3. SPEECH vs NARRATIVE")
sp = [k for k in keys if JN[k]["person"]]; na = [k for k in keys if not JN[k]["person"]]
def share(ks): return sum(JN[k]["obs"] for k in ks) / sum(JN[k]["n"] for k in ks)
real = share(sp) - share(na); allk = list(keys); null = []
for _ in range(2000):
    idx = rng.permutation(len(allk)); a = [allk[i] for i in idx[:len(sp)]]; b = [allk[i] for i in idx[len(sp):]]; null.append(share(a) - share(b))
print(f"   speech verses (1st/2nd person verbs) {share(sp):.3f} vs narrative {share(na):.3f}; difference {real:+.4f}; p = {np.mean(np.abs(null) >= abs(real)):.4f}")
out["speech"] = dict(speech=share(sp), narrative=share(na))

print("\n4. STRUCTURAL POINTS (window of 5 verses; percentile among all John windows, low = quiet)")
w5 = np.convolve([JN[k]["obs"] for k in keys], np.ones(5), "same") / np.maximum(np.convolve([JN[k]["n"] for k in keys], np.ones(5), "same"), 1)
for lab, ref in (("prologue centre 1:12", (1, 12)), ("book centre 10:24", (10, 24)), ("seam 3:22", (3, 22)), ("seam 6:1", (6, 1)), ("seam 9:1", (9, 1)), ("seam 18:1", (18, 1)),
                 ("'I am the bread' 6:35", (6, 35)), ("'I am the light' 8:12", (8, 12)), ("'I am the resurrection' 11:25", (11, 25)), ("'I am the way' 14:6", (14, 6)), ("'It is finished' 19:30", (19, 30)), ("'breathed on them' 20:22", (20, 22))):
    i = keys.index(ref); print(f"   {lab:32s} noise {w5[i]:.3f}  percentile {np.mean(w5 <= w5[i]):.2f}")

print("\n5. THE ARC: average noise by fifths of each Gospel")
arcs = {}
for code in ("Jn", "Mt", "Mk", "Lk"):
    V = load(code) if code != "Jn" else JN; ks, rw, s2, ps = curve(V); o = np.array([V[k]["obs"] for k in ks], float); n = np.array([V[k]["n"] for k in ks], float)
    arcs[code] = [float(o[(ps >= a) & (ps < a + .2)].sum() / n[(ps >= a) & (ps < a + .2)].sum()) for a in np.arange(0, 1, .2)]
    print(f"   {code}: " + "  ".join(f"{x:.3f}" for x in arcs[code]))
out["arcs"] = arcs
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 4.5)); ax.plot(pos, sm, color="#3b6fb6", lw=1.8, label="noise share (15-verse window)")
    ax.axhline(overall, color="#999", lw=.8, ls="--")
    tc = json.load(open(os.path.join(HERE, "theme_shapes_results.json")))["themes"] if os.path.exists(os.path.join(HERE, "theme_shapes_results.json")) else {}
    for th, v in tc.items():
        if th.split(" (")[0] in ("water", "light", "bread", "life", "hour", "glory", "abide", "love", "world"): ax.axvline(v["centre"], color="#d4a017", alpha=.5); ax.text(v["centre"], sm.max(), th.split(" (")[0], rotation=90, va="top", fontsize=8)
    for c in range(1, 22):
        i = next(j for j, k in enumerate(keys) if k[0] == c); ax.text(pos[i], sm.min() - .004, str(c), fontsize=7, ha="center", color="#666")
    ax.set_xlabel("John, spoken time (chapter numbers below)"); ax.set_ylabel("noise share (lower = quieter, more voiced)"); ax.set_title("John's sound map: noise share against the theme blocks")
    ax.legend(loc="lower left", fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(HERE, "john_noise_map.png"), dpi=150); print("\n   chart: john_noise_map.png")
except Exception as e: print("   (no chart:", e, ")")
json.dump(out, open(os.path.join(HERE, "john_noise_map_results.json"), "w"), ensure_ascii=False, indent=1, default=str)

# plain SVG chart (no plotting library needed)
W, H, P = 1100, 360, 50
lo, hi = float(sm.min()) - .005, float(sm.max()) + .005
X = lambda f: P + f * (W - 2 * P); Y = lambda v: H - P - (v - lo) / (hi - lo) * (H - 2 * P)
pts = " ".join(f"{X(f):.1f},{Y(v):.1f}" for f, v in zip(pos, sm))
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="11"><rect width="100%" height="100%" fill="#fff"/>',
       f'<text x="{P}" y="22" font-size="14" font-weight="bold">John\'s sound map: noise share (15-verse window); lower = quieter, more voiced</text>',
       f'<line x1="{P}" x2="{W - P}" y1="{Y(overall):.1f}" y2="{Y(overall):.1f}" stroke="#aaa" stroke-dasharray="4 3"/>']
tc = json.load(open(os.path.join(HERE, "theme_shapes_results.json")))["themes"] if os.path.exists(os.path.join(HERE, "theme_shapes_results.json")) else {}
for th, v in tc.items():
    nm = th.split(" (")[0]
    if nm in ("water", "light", "bread", "life", "hour", "glory", "abide", "love"):
        svg.append(f'<line x1="{X(v["centre"]):.1f}" x2="{X(v["centre"]):.1f}" y1="{P}" y2="{H - P}" stroke="#d4a017" stroke-opacity=".6"/><text x="{X(v["centre"]) + 3:.1f}" y="{P + 12}" fill="#8a5a14">{nm}</text>')
svg.append(f'<polyline points="{pts}" fill="none" stroke="#3b6fb6" stroke-width="2"/>')
for c in range(1, 22):
    i = next(j for j, k in enumerate(keys) if k[0] == c); svg.append(f'<text x="{X(pos[i]):.1f}" y="{H - P + 16}" text-anchor="middle" fill="#666">{c}</text>')
for i in qs[:3]: svg.append(f'<circle cx="{X(pos[i]):.1f}" cy="{Y(sm[i]):.1f}" r="4" fill="#4a9a6a"/><text x="{X(pos[i]) + 6:.1f}" y="{Y(sm[i]) + 4:.1f}" fill="#2d6b45">{keys[i][0]}:{keys[i][1]}</text>')
svg.append(f'<text x="{W / 2}" y="{H - 8}" text-anchor="middle" fill="#444">chapters of John (spoken time); gold lines = theme-block centres</text></svg>')
open(os.path.join(HERE, "john_noise_map.svg"), "w").write("\n".join(svg)); print("   chart: john_noise_map.svg")
