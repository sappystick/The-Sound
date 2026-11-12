#!/usr/bin/env python3
"""Round 87b - leaf/branch ARRANGEMENT geometry of the Voynich plants, and whether the drawing could be a code.

Reuses the morphometry pipeline (morph.py) to get each plant's skeleton, then extracts the stem and the leaf/branch
attachment nodes along it: count, left/right side, height, spacing. This is real botany (phyllotaxis: alternate vs
opposite vs whorled leaf arrangement). We:
  P1  per-plant arrangement: n_nodes, left/right split, alternation, spacing regularity (CV).
  P2  the user's f3v observation: report its numbers and ask if its arrangement is UNUSUALLY regular vs the population
      and vs a drawn-at-random null.  (Honest note: regular opposite/decussate leaves are ordinary botany; a
      molecular/DNA/compound reading is chronologically impossible for a 1404-1438 manuscript - those concepts are
      post-1800/1950. We test the geometry, not the anachronism.)
  P3  the 'drawing is the code' hypothesis: across pages, do leaf-counts form a non-random sequence (entropy,
      repetition), and does leaf-count correlate with any TEXT quantity on the page? If the geometry carried the
      message, it should be structured and/or linked to the text.
Usage: python3 mysteries/voynich/phyllotaxis.py
"""
import collections, json, math, os, re
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("morph", os.path.join(HERE, "morph.py")); M = importlib.util.module_from_spec(spec)
import sys; sys.argv = ["morph", "--import"];
try: spec.loader.exec_module(M)
except SystemExit: pass
ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts"); ZL = os.path.join(T, "voynich/ZL3b-n.txt")
rng = np.random.default_rng(87)

def text_counts():
    cur = None; sec = None; tc = collections.defaultdict(lambda: dict(words=0, lines=0))
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h: cur = h.group(1); sec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I"); continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*][PT]\d*>\s*(.*)", ln)
        if m and sec == "H":
            tc[m.group(1)]["words"] += len([w for w in re.split(r"[.\s]+", m.group(2)) if re.search(r"[a-zA-Z]", M.clean(w) if hasattr(M, "clean") else w)])
            tc[m.group(1)]["lines"] += 1
    return tc

def arrangement(sk, stem_x):
    nbrs = sum(np.roll(np.roll(sk, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0))
    bp = (sk == 1) & (nbrs >= 3)
    ys, xs = np.where(bp)
    if len(ys) == 0: return None
    nodes = sorted([(y, ("R" if x >= stem_x else "L")) for y, x in zip(ys, xs)])
    # merge nodes within 5 px vertically (one leaf junction)
    merged = []
    for y, side in nodes:
        if merged and y - merged[-1][0] < 6: continue
        merged.append((y, side))
    sides = [s for _, s in merged]; heights = [y for y, _ in merged]
    L = sides.count("L"); R = sides.count("R")
    alt = sum(1 for a, b in zip(sides, sides[1:]) if a != b) / max(1, len(sides) - 1)
    gaps = np.diff(heights) if len(heights) > 1 else np.array([0])
    reg = float(np.std(gaps) / (np.mean(gaps) + 1e-9)) if len(gaps) and np.mean(gaps) > 0 else 0
    return dict(nodes=len(merged), left=L, right=R, alternation=round(alt, 2), spacing_cv=round(reg, 2))

def main():
    sec, svc, tpage = M.load(); tc = text_counts()
    herb = [f for f in sec if sec[f] == "H" and f in svc]
    plants = {}
    for f in herb:
        fp = os.path.join(M.CACHE, f + ".jpg")
        if not os.path.exists(fp): continue
        try: a = np.asarray(Image.open(fp).convert("L"), float) / 255
        except Exception: continue
        keep, frac = M.segment(a)
        ys, xs = np.where(keep)
        if len(xs) < 80: continue
        sk = M.zhang_suen(keep)
        stem_x = np.bincount(xs, minlength=keep.shape[1]).argmax()   # column with most ink = stem
        arr = arrangement(sk, stem_x)
        if arr: plants[f] = arr
    out = dict(plants_analyzed=len(plants))
    nodes = {f: p["nodes"] for f, p in plants.items()}
    # P1 population
    arr_pop = dict(mean_nodes=round(float(np.mean(list(nodes.values()))), 2),
                   mean_alternation=round(float(np.mean([p["alternation"] for p in plants.values()])), 2),
                   mean_spacing_cv=round(float(np.mean([p["spacing_cv"] for p in plants.values()])), 2),
                   opposite_like=sum(1 for p in plants.values() if abs(p["left"] - p["right"]) <= 1 and p["nodes"] >= 4),
                   alternate_like=sum(1 for p in plants.values() if p["alternation"] >= 0.7 and p["nodes"] >= 4))
    out["P1_population_arrangement"] = arr_pop
    # P2 f3v
    if "f3v" in plants:
        p = plants["f3v"]; reg_rank = float(np.mean([plants[f]["spacing_cv"] >= p["spacing_cv"] for f in plants]))
        out["P2_f3v"] = dict(measured=p, interpretation=(
            f"f3v shows {p['left']} nodes left / {p['right']} right, alternation {p['alternation']}, spacing CV {p['spacing_cv']}. "
            f"Its spacing is more regular than {round(100*(1-reg_rank))}% of plants." if p['spacing_cv'] else ""),
            honest_note=("Regular opposite/decussate leaf pairs are a common real botanical arrangement and a common "
                "stylisation in medieval herbals. A DNA/molecule/compound reading is not possible: those are post-1800 "
                "(molecular structure) and post-1950 (DNA) concepts, centuries after this vellum (1404-1438). We report "
                "the geometry; the molecular interpretation is ruled out by chronology, not by the drawing."))
    # P3 is the drawing a code?
    seq = [nodes[f] for f in sorted(nodes)]
    cnt = collections.Counter(seq); Hn = -sum(v/len(seq)*math.log2(v/len(seq)) for v in cnt.values())
    maxH = math.log2(len(cnt)) if len(cnt) > 1 else 1
    # correlate leaf-count with text words on the page
    common = [f for f in plants if f in tc and tc[f]["words"] > 0]
    if len(common) >= 20:
        x = np.array([nodes[f] for f in common]); y = np.array([tc[f]["words"] for f in common])
        r = float(np.corrcoef(x, y)[0, 1]); rl = float(np.corrcoef(x, [tc[f]["lines"] for f in common])[0, 1])
    else: r = rl = float("nan")
    out["P3_drawing_as_code"] = dict(leaf_count_entropy_bits=round(Hn, 2), max_entropy=round(maxH, 2),
        entropy_ratio=round(Hn/maxH, 2) if maxH else None,
        leafcount_vs_text_words_r=round(r, 3), leafcount_vs_text_lines_r=round(rl, 3),
        reading=("If the drawing were a code, leaf-counts should be structured (low-entropy sequence) and/or linked to "
                 "the text. High entropy + near-zero text correlation = the leaf geometry does not carry a recoverable "
                 "message tied to the page."))
    json.dump(out, open(os.path.join(HERE, "phyllotaxis_results.json"), "w"), indent=1)
    print("plants analyzed:", len(plants))
    print("P1 arrangement:", json.dumps(arr_pop))
    if "P2_f3v" in out: print("P2 f3v:", json.dumps(out["P2_f3v"]["measured"]), "|", out["P2_f3v"]["interpretation"])
    print("P3 code test:", json.dumps({k: v for k, v in out["P3_drawing_as_code"].items() if k != "reading"}))

if __name__ == "__main__": main()
