#!/usr/bin/env python3
"""Round 61. Every area in and around the Great Pyramid set against every biblical area: best counterpart by shape
(proportions), size (under 4 attested cubits) and function, each scored against random rooms.
Pyramid values: Petrie 1883 (inches, verified) or standard published values (marked approx).
Score for a pair: shape error = mean |log ratio difference| of the sorted proportions; size error = min over cubits of
|log(pyramid / (biblical x cubit))| for the largest dimension. Combined = shape + size. Local p = share of 5,000 random
copies of the real area with its shape kept and its size scaled log-uniformly by x0.5-x2 whose best combined score is as good.
Usage: python3 power/round61_pyramid_map.py
"""
import itertools, json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); IN = 0.0254; rng = np.random.default_rng(61)
PYR = {  # metres; (dims, source, function)
 "King's Chamber": ([412.4 * IN, 206.3 * IN, 230.1 * IN], "Petrie", "innermost sealed chamber; the coffer"),
 "Coffer (inside)": ([78.06 * IN, 26.81 * IN, 34.42 * IN], "Petrie", "a lidded stone box in the inner chamber"),
 "Coffer (outside)": ([89.62 * IN, 38.50 * IN, 41.31 * IN], "Petrie", "a lidded stone box in the inner chamber"),
 "Antechamber": ([116.3 * IN, 65.2 * IN, 149.4 * IN], "Petrie", "the small chamber before the inner room; 3 portcullis slabs"),
 "Queen's Chamber": ([226.5 * IN, 205.7 * IN, 184.4 * IN], "Petrie", "the middle chamber, gabled roof; a corbelled niche"),
 "Grand Gallery": ([46.7, 8.6, 2.06], "approx (Petrie; Lehner 1997)", "the great ascending hall; 7 corbel courses"),
 "Subterranean chamber": ([14.05, 8.26, 3.5], "approx (Petrie; Lehner)", "the unfinished rock-cut chamber below"),
 "Queen's niche": ([4.67, 1.57, 1.04], "approx", "a corbelled niche, 5 steps narrowing upward"),
 "Base": ([230.36, 230.36], "Petrie (9068.8 in)", "the square foundation, oriented to the cardinal points"),
 "Height and base": ([230.36, 146.6], "Petrie (9068.8; 5776.0 in)", "the whole building"),
 "Khufu boat (pit S)": ([43.4, 5.9], "approx (reassembled ship)", "a cedar ship buried beside the pyramid"),
 "Queens' pyramids (G1a)": ([46.0, 46.0], "approx", "three smaller pyramids to the east"),
}
BIB = {
 "ark of the covenant": ([2.5, 1.5, 1.5], "the box in the Holy of Holies"), "table of showbread": ([2, 1, 1.5], "table in the Holy Place"),
 "altar of burnt offering": ([5, 5, 3], "altar in the court"), "incense altar": ([1, 1, 2], "altar before the veil"),
 "tabernacle Holy Place": ([20, 10, 10], "outer room"), "tabernacle Holy of Holies": ([10, 10, 10], "inner room"),
 "tabernacle court": ([100, 50], "the enclosure"), "Solomon's house": ([60, 20, 30], "the whole temple"),
 "Solomon's Holy Place": ([40, 20, 30], "the great hall"), "Solomon's Holy of Holies": ([20, 20, 20], "the inner cube"),
 "Solomon's porch": ([20, 10], "the entrance hall"), "Solomon's side chambers": ([5, 6, 7], "3 storeys around the house"),
 "bronze sea": ([10, 10, 5], "the great basin"), "bronze stand": ([4, 4, 3], "ten wheeled stands"), "pillar Jachin/Boaz": ([18, 3.82, 3.82], "the two bronze pillars (12 round = 3.82 across)"),
 "Noah's ark": ([300, 50, 30], "the ship"), "Ezekiel temple": ([100, 100], "the house"), "Ezekiel outer wall": ([500, 500], "the outer square"),
 "Ezekiel gate": ([50, 25], "each of six gates"), "Ezekiel chamber": ([6, 6], "the gate cells"), "Herod's Temple Mount": ([500, 500], "Mishnah Middot 2:1"),
 "Herod's house": ([100, 100, 100], "Middot 4:6"), "New Jerusalem wall (height)": ([144], "Rev 21:17"),
}
UNITS = {"common 0.445": 0.445, "long 0.52": 0.52, "royal 0.5236": 0.5236, "18-inch 0.457": 0.4572}
def shape(ds): ds = sorted(ds, reverse=True); return [ds[0] / x for x in ds[1:]]
def score(p, b):
    if len(p) != len(b): return None
    sp, sb = shape(p), shape(b)
    se = float(np.mean([abs(math.log(x / y)) for x, y in zip(sp, sb)])) if sp else 0.0
    zs = [(abs(math.log(max(p) / (max(b) * cu))), u) for u, cu in UNITS.items()]; ze, u = min(zs)
    return se, ze, u
def best(p):
    cands = [(s[0] + s[1], s[0], s[1], s[2], k) for k, (b, _) in BIB.items() if (s := score(p, b))]
    return min(cands) if cands else None
rows = []
for area, (ds, src, fn) in PYR.items():
    bb = best(ds)
    if bb is None: continue
    tot, se, ze, unit, k = bb
    nul = []
    for _ in range(5000):
        k_ = math.exp(rng.uniform(math.log(0.5), math.log(2))); r = [d * k_ for d in ds]; x = best(r); nul.append(x[0] if x else 9)   # shape kept, size random
    p_local = float((np.array(nul) <= tot).mean())
    b_dims = BIB[k][0]; cu = UNITS[unit]
    rows.append(dict(area=area, dims_m=[round(d, 2) for d in ds], source=src, function=fn, best_biblical=k, biblical_cubits=b_dims,
                     unit=unit, biblical_m=[round(x * cu, 2) for x in b_dims], shape_error_pct=round(100 * (math.exp(se) - 1), 1),
                     size_error_pct=round(100 * (math.exp(ze) - 1), 1), local_p=round(p_local, 3)))
FUNC = [("King's Chamber", "Holy of Holies / Solomon's porch", "the innermost chamber holding the box; its plan equals Solomon's porch (round 60)"),
        ("Coffer", "ark of the covenant", "a lidded box in the innermost room (not equal in size, round 60)"),
        ("Antechamber with 3 portcullis slabs", "the veil (and the two screens)", "barriers between the outer and the inner room"),
        ("Grand Gallery, 7 corbel courses", "the menorah (7) / the 15 steps (ascent)", "a sevenfold ascending structure"),
        ("Queen's Chamber (middle)", "Holy Place", "the middle room on the way inward"),
        ("Subterranean chamber", "the depths beneath (e.g. the rock under the altar)", "the rock-cut room below"),
        ("Base square, cardinal orientation", "the court / Temple Mount 500 x 500 / Ezekiel's 500 square", "the square sacred precinct oriented to the directions"),
        ("Khufu's cedar ship", "Noah's ark", "a great wooden vessel tied to the sacred building"),
        ("Three queens' pyramids", "the three storeys of side chambers / the three courts", "a set of three"),
        ("Relieving chambers (5 above the King's Chamber)", "Solomon's side-chamber storeys (3) / the five bars", "stacked compartments")]
out = dict(pairs=rows, functional_links=[dict(pyramid=a, bible=b, link=c) for a, b, c in FUNC],
           n_local_p_below_005=sum(r["local_p"] < 0.05 for r in rows), n_areas=len(rows),
           expected_by_chance=round(0.05 * len(rows), 1))
json.dump(out, open(os.path.join(HERE, "round61_results.json"), "w"), ensure_ascii=False, indent=1)
for r in sorted(rows, key=lambda r: r["local_p"]):
    print(f'{r["area"]:<24} -> {r["best_biblical"]:<26} {str(r["biblical_cubits"]):<16} {r["unit"]:<14} shape {r["shape_error_pct"]:>5}%  size {r["size_error_pct"]:>5}%  p {r["local_p"]}')
print(out["n_local_p_below_005"], "of", out["n_areas"], "beat chance at 0.05; expected", out["expected_by_chance"])
