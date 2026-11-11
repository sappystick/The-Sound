#!/usr/bin/env python3
"""Round 62. If the building instructions carried a code, what could it spell? Each proposed decoding is tested
against chance.
T1 elements: does a stated number of an object equal the atomic number of its own material (gold 79, silver 47,
   copper 29, tin 50 (bronze), carbon 6 (wood), iron 26)? Null: materials shuffled across objects.
T2 constants: within-object ratios near pi, phi, sqrt2, sqrt3, e (within 1%), against random pairs from the same
   pool of numbers.
T3 pi in the bronze sea (1 Kgs 7:23): the ketiv qwh (111) / qere qw (106) gives 3 x 111/106 = 3.14151. How often does
   ANY ketiv/qere pair in the Hebrew Bible (WLC) give a ratio that close to pi/3?
T4 electrical: the ark as a capacitor (gold / acacia / gold): capacitance and stored energy.
T5 magnetic: the metals of the sanctuary; the exclusion of iron.
T6 geometric: the solids and plane figures named, and Plato's element-solids (Timaeus 55d-56b).
T7 geographic: orientation and the camp.
Usage: python3 power/round62_code_tests.py
"""
import glob, itertools, json, math, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); rng = np.random.default_rng(62); out = {}
# objects: (stated integers, materials)
OBJ = {"ark": ([2, 1, 1, 4], ["C", "Au"]), "mercy seat": ([2, 1], ["Au"]), "cherubim (tabernacle)": ([2], ["Au"]), "table": ([2, 1, 1, 12], ["C", "Au"]),
       "menorah": ([7, 6, 3, 1], ["Au"]), "incense altar": ([1, 1, 2, 4], ["C", "Au"]), "altar of burnt offering": ([5, 5, 3, 4], ["C", "Cu", "Sn"]),
       "boards": ([48, 10, 1, 2], ["C", "Au"]), "silver sockets": ([100, 96, 4], ["Ag"]), "gold clasps": ([50], ["Au"]), "bronze clasps": ([50], ["Cu", "Sn"]),
       "pillar hooks": ([60], ["Ag"]), "laver": ([1], ["Cu", "Sn"]), "bronze sea": ([10, 5, 30, 12, 2000], ["Cu", "Sn"]),
       "Jachin and Boaz": ([18, 12, 5, 200, 4], ["Cu", "Sn"]), "bronze stands": ([10, 4, 4, 3, 40], ["Cu", "Sn"]), "Solomon's cherubim": ([10, 5, 2], ["C", "Au"])}
Z = {"Au": 79, "Ag": 47, "Cu": 29, "Sn": 50, "C": 6, "Fe": 26}
def hits(objs): return sum(1 for nums, mats in objs.values() for n in nums for m in mats if n == Z[m])
h_obs = hits(OBJ); mats = [m for _, ms in OBJ.values() for m in ms]
null = []
for _ in range(20000):
    perm = list(rng.permutation(mats)); it = iter(perm); sh = {k: (v[0], [next(it) for _ in v[1]]) for k, v in OBJ.items()}; null.append(hits(sh))
out["T1_elements"] = dict(hits=h_obs, which=[f"{k}: {n} = {m}" for k, (nums, ms) in OBJ.items() for n in nums for m in ms if n == Z[m]],
                          null_mean=round(float(np.mean(null)), 2), p=round(float((np.array(null) >= h_obs).mean()), 4))
# T2 constants
DIMS = [[2.5, 1.5, 1.5], [2.5, 1.5], [2, 1, 1.5], [5, 5, 3], [1, 1, 2], [100, 50, 5], [10, 1.5], [28, 4], [30, 4], [20, 10, 10], [10, 10, 10],
        [60, 20, 30], [20, 20, 20], [20, 10], [10, 5], [10, 5, 30], [18, 12, 5], [4, 4, 3], [20, 20, 10], [5, 6, 7], [300, 50, 30], [50, 25], [40, 20], [12, 12]]
CONST = {"pi": math.pi, "phi": (1 + 5 ** .5) / 2, "sqrt2": 2 ** .5, "sqrt3": 3 ** .5, "e": math.e}
def near(rs, tol=0.01): return {k: [round(r, 4) for r in rs if abs(r / v - 1) <= tol] for k, v in CONST.items()}
rs = [max(a, b) / min(a, b) for d in DIMS for a, b in itertools.combinations(d, 2)]
obs = near(rs); pool = [x for d in DIMS for x in d]
nl = {k: [] for k in CONST}
for _ in range(5000):
    rr = []
    for d in DIMS:
        s = rng.choice(pool, len(d)); rr += [max(a, b) / min(a, b) for a, b in itertools.combinations(s, 2)]
    for k, v in near(rr).items(): nl[k].append(len(v))
out["T2_constants"] = {k: dict(observed=len(obs[k]), values=obs[k], null_mean=round(float(np.mean(nl[k])), 2), p=round(float((np.array(nl[k]) >= len(obs[k])).mean()), 4)) for k in CONST}
out["T2_constants"]["ark_note"] = "the ark's 2.5:1.5 = 5:3 = 1.667, 3.0% from phi: consecutive Fibonacci numbers, as small integers often are"
# T3 pi via ketiv/qere
GEM = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400])); GEM.update({"ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90})
def gem(w): return sum(GEM.get(c, 0) for c in w)
pairs = []
for f in glob.glob(os.path.join(ROOT, "sources/texts/morphhb/wlc/*.xml")):
    t = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<w type="x-ketiv"[^>]*>(.*?)</w><note type="variant"><catchWord>.*?</catchWord><rdg type="x-qere">(.*?)</rdg>', t, re.S):
        k = re.sub(r"[^א-ת]", "", m.group(1)); q = re.sub(r"[^א-ת]", "", re.sub(r"<[^>]+>", "", m.group(2)))
        if k and q and k != q: pairs.append((os.path.basename(f)[:-4], k, q, gem(k), gem(q)))
target = math.pi / 3; err_obs = abs((111 / 106) / target - 1) * 1.0001
close = [(b, k, q, a, c, round(3 * a / c, 5)) for b, k, q, a, c in pairs if c and (abs((a / c) / target - 1) <= err_obs or abs((c / a) / target - 1) <= err_obs)]
any_close = [(b, k, q, a, c) for b, k, q, a, c in pairs if c and any(abs((a / c) * mult / math.pi - 1) <= err_obs or abs((c / a) * mult / math.pi - 1) <= err_obs for mult in range(1, 11))]
out["T3_pi"] = dict(ketiv_qere_pairs=len(pairs), bronze_sea=dict(ketiv="קוה 111", qere="קו 106", value=round(3 * 111 / 106, 6), pi=round(math.pi, 6), relative_error=f"{err_obs:.2e}"),
    pairs_as_close_with_multiplier_3=len(close), close_pairs=[f"{b}: {k} ({a}) / {q} ({c}) -> {v}" for b, k, q, a, c, v in close], distinct_close_pairs=sorted({(k, q) for _, k, q, _, _, _ in close}), pairs_as_close_with_any_multiplier_1_to_10=len(any_close),
    expected_with_any_multiplier=round(len(pairs) * 10 * 2 * 2 * err_obs * (1 / 0.6), 2),
    note="the expected count assumes ratios spread over roughly 0.6 of a unit around each target; the bronze sea is the one case in a verse about a circle")
# T4 capacitor
A = 2 * (2.5 * 1.5 + 2.5 * 1.5 + 1.5 * 1.5) * 0.445 ** 2; eps0 = 8.854e-12
cap = {f"{d * 100:.0f} cm acacia": dict(nF=round(eps0 * 2.5 * A / d * 1e9, 2), J_at_10kV=round(0.5 * eps0 * 2.5 * A / d * 1e8, 3), J_at_50kV=round(0.5 * eps0 * 2.5 * A / d * 2.5e9, 2)) for d in (0.01, 0.02, 0.05)}
out["T4_electrical"] = dict(surface_m2=round(A, 2), dielectric="dry acacia, relative permittivity about 2.5", capacitance=cap,
    comparison="a static shock is about 0.001 J; an electric fence pulse up to about 5 J; a defibrillator 150-360 J",
    note="no charging source is described; with 2 cm of wood, 50 kV stores about 5 J, painful to dangerous but not the 'device' of popular claims")
# T5 magnetic
out["T5_magnetic"] = dict(metals=["gold (diamagnetic)", "silver (diamagnetic)", "bronze = copper + tin (diamagnetic / weakly paramagnetic)"],
    iron="absent from the tabernacle's furnishings; excluded from altar stones ('if you wield your tool on it you profane it', Exod 20:25; Deut 27:5) and from the temple site: 'no hammer or axe or any iron tool was heard in the House while it was being built' (1 Kgs 6:7)",
    calc="every named metal has magnetic susceptibility below 1e-5 in magnitude: the sanctuary is magnetically inert")
# T6 geometric (and Plato)
tim = glob.glob(os.path.join(ROOT, "sources/texts/perseus/data/tlg0059/tlg031/*grc*.xml")); cube_line = ""
if tim:
    tt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(tim[0], encoding="utf-8").read())); i = tt.find("κυβικ"); cube_line = tt[max(0, i - 120):i + 200]
out["T6_geometric"] = dict(cubes=["tabernacle Holy of Holies 10", "Solomon's Holy of Holies 20", "Herod's house 100", "New Jerusalem 12,000 stadia"],
    squares=["altars", "breastpiece (a span, doubled)", "Ezekiel's temple 100 and 500", "Herod's Temple Mount 500", "Ezekiel's hearth 12"], double_squares=["Holy Place 20 x 10", "porch 20 x 10", "court 100 x 50", "table 2 x 1"],
    plato="Timaeus 55d-56a gives each element a solid: earth = the cube, fire = tetrahedron, air = octahedron, water = icosahedron",
    timaeus_text=cube_line)
# T7 geographic
out["T7_geographic"] = dict(orientation="the tabernacle's entrance faces east (Exod 27:13); the glory enters Ezekiel's temple from the east (Ezek 43:2)",
    camp="Num 2: twelve tribes, three on each side of the tabernacle; the breastpiece: twelve stones in four rows of three (Exod 28:17-21)",
    note="the breastpiece is a 4 x 3 grid of the twelve tribes; the camp is a 4 x 3 arrangement of the same twelve around the centre")
out["T3_pi"]["bronze_sea_as_written"] = dict(ketiv="וקוה 117 (with the conjunction 'and')", qere="וקו 112", value=round(3 * 117 / 112, 5),
    note="the pi value needs the conjunction removed; the same 111/106 ratio also occurs in Daniel's Aramaic 'Most High' (x7) and in 'his words' (222/212), none about circles")
json.dump(out, open(os.path.join(HERE, "round62_results.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("T6_geometric",)}, ensure_ascii=False, indent=1)[:4500]); print(out["T6_geometric"]["timaeus_text"])
