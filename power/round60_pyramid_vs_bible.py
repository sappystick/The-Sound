#!/usr/bin/env python3
"""Round 60. Do the Great Pyramid's internal dimensions map onto the biblical sacred measurements?
Pyramid: Petrie, The Pyramids and Temples of Gizeh (1883), inches (OCR checked in sources/texts/petrie).
Bible: the stated dimensions collected in rounds 55-59 (cubits).
Tests (with nulls, because many numbers and free units make matches easy):
  T1 lengths: a pyramid length 'matches' a biblical length if they agree within 1% under any of 5 cubits
     (common 0.445, 18-inch 0.457, long 0.52, Egyptian royal 0.5236, Smyth's 'sacred' 25 pyramid inches 0.635 m).
     Null: 20,000 synthetic pyramids, each dimension replaced by a log-uniform random length over the same range.
  T2 shapes (unit-free): the ratios within each room/object (e.g. King's Chamber length:width) against the ratios
     within each biblical object, within 1%. Null: random rooms with log-uniform sides.
  T3 the famous claims: King's Chamber = 20 x 10 royal cubits (as the Holy Place 20 x 10); coffer volume = ark volume
     (Piazzi Smyth 1864).
Usage: python3 power/round60_pyramid_vs_bible.py
"""
import itertools, json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); IN = 0.0254; rng = np.random.default_rng(60)
PYR = {  # inches (Petrie 1883); 'approx' where the OCR or the source rounds
 "King's Chamber": [412.4, 206.3, 230.1], "Queen's Chamber": [226.5, 205.7, 184.4], "Antechamber": [116.3, 65.2, 149.4],
 "Coffer outside": [89.62, 38.50, 41.31], "Coffer inside": [78.06, 26.81, 34.42], "Ascending passage": [1546.8],
 "Grand Gallery (approx)": [1815.0, 339.0, 82.4], "Subterranean chamber (approx)": [553.0, 325.0], "Pyramid base and height": [9068.8, 5776.0]}
BIB = {"ark": [2.5, 1.5, 1.5], "mercy seat": [2.5, 1.5], "table": [2, 1, 1.5], "altar of burnt offering": [5, 5, 3], "incense altar": [1, 1, 2],
       "court": [100, 50, 5], "board": [10, 1.5], "linen curtain": [28, 4], "goat-hair curtain": [30, 4], "Holy Place (tabernacle)": [20, 10, 10],
       "Holy of Holies (tabernacle)": [10, 10, 10], "Solomon's house": [60, 20, 30], "Solomon's Holy of Holies": [20, 20, 20], "porch": [20, 10],
       "cherub": [10, 5], "bronze sea": [10, 5, 30], "pillar": [18, 12, 5], "stand": [4, 4, 3], "Solomon's altar": [20, 20, 10],
       "Solomon's side chambers": [5, 6, 7], "Noah's ark": [300, 50, 30], "Ezekiel temple": [100, 100], "Ezekiel nave": [40, 20],
       "Ezekiel gate": [50, 25], "Ezekiel chamber": [6, 6], "Ezekiel hearth": [12, 12], "Herod's house": [100, 100, 100]}
UNITS = {"common 0.445": 0.445, "18-inch 0.457": 0.4572, "long 0.52": 0.52, "Egyptian royal 0.5236": 0.5236, "Smyth sacred 0.635": 0.635}
pyr_m = [(room, d * IN) for room, ds in PYR.items() for d in ds]
bib_c = sorted({c for ds in BIB.values() for c in ds})
def n_matches(lengths, tol=0.01):
    hits = []
    for room, L in lengths:
        m = [(c, u) for c in bib_c for u, cu in UNITS.items() if abs(L / (c * cu) - 1) <= tol]
        if m: hits.append((room, round(L, 3), m[:4]))
    return hits
obs = n_matches(pyr_m)
lo, hi = math.log(min(L for _, L in pyr_m)), math.log(max(L for _, L in pyr_m))
null = np.array([len(n_matches([(r, math.exp(rng.uniform(lo, hi))) for r, _ in pyr_m])) for _ in range(20000)])
out = {"T1_lengths": dict(pyramid_dimensions=len(pyr_m), matched=len(obs), null_mean=round(float(null.mean()), 2), p=round(float((null >= len(obs)).mean()), 4),
                          matches=[dict(room=r, metres=L, biblical_cubits_and_unit=[f"{c} cubits x {u}" for c, u in m]) for r, L, m in obs])}
def ratios(ds): return [max(a, b) / min(a, b) for a, b in itertools.combinations(ds, 2)]
bib_r = sorted({round(r, 4) for ds in BIB.values() for r in ratios(ds)})
def shape_matches(rooms, tol=0.01):
    return [(room, round(r, 3), [b for b in bib_r if abs(r / b - 1) <= tol]) for room, ds in rooms.items() for r in ratios(ds) if any(abs(r / b - 1) <= tol for b in bib_r)]
rooms = {k: v for k, v in PYR.items() if len(v) > 1}; sobs = shape_matches(rooms); nr = sum(len(ratios(v)) for v in rooms.values())
snull = np.array([len(shape_matches({k: list(np.exp(rng.uniform(math.log(20), math.log(2000), len(v)))) for k, v in rooms.items()})) for _ in range(20000)])
out["T2_shapes"] = dict(pyramid_ratios=nr, matched=len(sobs), null_mean=round(float(snull.mean()), 2), p=round(float((snull >= len(sobs)).mean()), 4),
                        matches=[dict(room=r, ratio=x, biblical=b) for r, x, b in sobs])
RC = 20.62  # Petrie's royal cubit, inches
kc = PYR["King's Chamber"]; vol_coffer = 78.06 * 26.81 * 34.42 * IN ** 3
ark_vol = {u: round(2.5 * 1.5 * 1.5 * cu ** 3, 3) for u, cu in UNITS.items()}
out["T3_famous_claims"] = dict(
    kings_chamber_in_royal_cubits=[round(d / RC, 2) for d in kc], kings_note="20.00 x 10.00 x 11.16: the plan is exactly 20 x 10 royal cubits (K: Petrie), the numbers of the tabernacle's Holy Place (20 x 10); its height is not 10",
    queens_chamber_in_royal_cubits=[round(d / RC, 2) for d in PYR["Queen's Chamber"]],
    coffer_inside_volume_m3=round(vol_coffer, 3), ark_outside_volume_m3_by_unit=ark_vol,
    coffer_outside_volume_m3=round(89.62 * 38.50 * 41.31 * IN ** 3, 3),
    coffer_note="Smyth's equality needs his own 'sacred cubit' and an ark interior; with any attested cubit the ark is 0.37-0.81 m3 against the coffer's 1.18 m3 inside")
json.dump(out, open(os.path.join(HERE, "round60_results.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("matches",)} for k, v in out.items()}, ensure_ascii=False, indent=1))
for m in out["T1_lengths"]["matches"]: print(m)
for m in out["T2_shapes"]["matches"]: print(m)
