#!/usr/bin/env python3
"""Antikythera FCI: reading the misfits. Which numbers are free and which are remainders; does the Mars misfit point to an
epoch; and is the "8-day pause" a stationarity threshold that also explains Mars's impossible 82-day retrograde?
Orbits: Keplerian, coplanar, JPL mean elements with linear rates (Standish, J2000 frame), 700 BC - AD 1, 0.05-day steps.
Usage: python3 residuals.py"""
import json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
# a, e, e_rate/cy, varpi, varpi_rate/cy, L0, L_rate/cy  (JPL approximate elements, J2000 ecliptic)
J = {"Earth": (1.00000261, 0.01671123, -0.00004392, 102.93768193, 0.32327364, 100.46457166, 35999.37244981),
     "Venus": (0.72333566, 0.00677672, -0.00004107, 131.60246718, 0.00268329, 181.97909950, 58517.81538729),
     "Mars": (1.52371034, 0.09339410, 0.00007882, -23.94362959, 0.44441088, -4.55343205, 19140.30268499),
     "Jupiter": (5.20288700, 0.04838624, -0.00013253, 14.72847983, 0.21252668, 34.39644051, 3034.74612775),
     "Saturn": (9.53667594, 0.05386179, -0.00050991, 92.59887831, -0.41897216, 49.95424423, 1222.49362201)}
DT = 0.05; Y0, Y1 = -700, 1                                     # astronomical years -699 = 700 BC
t = np.arange((Y0 - 2000) * 365.25, (Y1 - 2000) * 365.25, DT); T = t / 36525
def pos(p):
    a, e0, de, w0, dw, L0, dL = J[p]; e = e0 + de * T; w = np.radians(w0 + dw * T); M = np.radians(L0 + dL * T) - w; E = M.copy()
    for _ in range(8): E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2)); r = a * (1 - e * np.cos(E)); th = nu + w
    return r * np.cos(th), r * np.sin(th)
xe, ye = pos("Earth"); sun = np.degrees(np.arctan2(-ye, -xe))
def year(td): y = 2000 + td / 365.25; return f"{int(round(1 - y))} BC" if y < 0.5 else f"AD {int(round(y))}"
def trop(lon, td): return (lon + 1.3969 * (td / 36525)) % 360           # J2000 longitude -> approximate tropical longitude of date
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
_G = {}
def geo(p):
    if p in _G: return _G[p]
    x, y = pos(p); lam = np.degrees(np.unwrap(np.arctan2(y - ye, x - xe))); v = np.gradient(lam, DT)
    el = (np.degrees(np.arctan2(y - ye, x - xe)) - sun + 180) % 360 - 180; _G[p] = (lam, v, el); return _G[p]
out = {}
# ---------------------------------------------------------------- 1. free numbers and remainders
out["remainders"] = {"Venus": "68 = 584/2 - 224", "Mars": "82 = 780 - 2 x 349", "Jupiter": "104 = 398 - 2 x 139 - 2 x 8",
                     "note": "in every section the inexact number is the one obtained by subtraction from the synodic period"}
# ---------------------------------------------------------------- 2. which real Mars cycles reproduce 349 / 349 / 82?
def superior_cycles(p):
    lam, v, el = geo(p); s = np.where(np.diff(np.sign(v)) != 0)[0]; conj = np.where((np.diff(np.sign(el)) != 0) & (np.abs(el[:-1]) < 90))[0]
    direct_starts = [i for i in s if v[i + 1] > 0]; retro_starts = [i for i in s if v[i + 1] < 0]; cyc = []
    for i in direct_starts:
        c = next((j for j in conj if j > i), None); m = next((j for j in retro_starts if j > i), None)
        if c is None or m is None or c > m: continue
        n = next((j for j in direct_starts if j > m), None)
        if n is None: continue
        cyc.append(dict(start=float(i * DT + t[0]), es_c=(c - i) * DT, c_ms=(m - c) * DT, retro=(n - m) * DT, conj_lon=trop(float(sun[c]), float(c * DT + t[0])), opp_lon=trop(float(lam[(m + n) // 2] % 360), float(c * DT + t[0]))))
    return cyc
mars = superior_cycles("Mars")
for c in mars: c["score"] = math.sqrt(((c["es_c"] - 349) ** 2 + (c["c_ms"] - 349) ** 2 + (c["retro"] - 82) ** 2) / 3)
best = sorted(mars, key=lambda c: c["score"])[:10]
out["mars_best_cycles"] = [dict(date=year(c["start"]), es_conj=round(c["es_c"], 1), conj_ms=round(c["c_ms"], 1), retrograde=round(c["retro"], 1), rms=round(c["score"], 1),
                                retrograde_in=SIGNS[int(c["opp_lon"] // 30)], opposition_longitude=round(c["opp_lon"], 1)) for c in best]
both = [c for c in mars if abs(c["es_c"] - 349) <= 4 and abs(c["c_ms"] - 349) <= 4]
out["mars_cycles_with_both_halves_349_pm4"] = dict(count=len(both), of=len(mars), retro_signs=sorted({SIGNS[int(c["opp_lon"] // 30)] for c in both}),
                                                     retrograde_range=(round(min(c["retro"] for c in both), 1), round(max(c["retro"] for c in both), 1)) if both else None)
jup = superior_cycles("Jupiter")
# ---------------------------------------------------------------- 3. the 8-day pause as a speed threshold
def pause_days(p, thr):
    lam, v, el = geo(p); slow = np.abs(v) < thr; e = np.diff(slow.astype(np.int8)); st = np.where(e == 1)[0]; en = np.where(e == -1)[0]
    if len(en) and len(st) and en[0] < st[0]: en = en[1:]
    n = min(len(st), len(en)); d = (en[:n] - st[:n]) * DT
    return float(np.median(d[1:-1])), lam, v
thr_table = {}
for p in ("Mars", "Jupiter", "Saturn"):
    lo, hi = 1e-4, 0.5
    for _ in range(40):
        mid = (lo + hi) / 2; d, _, _ = pause_days(p, mid)
        lo, hi = (mid, hi) if d < 8 else (lo, mid)
    d, lam, v = pause_days(p, mid)
    thr_table[p] = dict(speed_threshold_arcmin_per_day=round(mid * 60, 2), pause_days=round(d, 1))
common = float(np.median([v_["speed_threshold_arcmin_per_day"] for v_ in thr_table.values()])) / 60
def phases_at(p, thr):
    lam, v, el = geo(p); fast_retro = v < -thr; slow = np.abs(v) < thr
    # durations of contiguous retrograde-moving runs and of each pause
    def runs(mask):
        e = np.diff(mask.astype(np.int8)); st = np.where(e == 1)[0]; en = np.where(e == -1)[0]
        if len(en) and len(st) and en[0] < st[0]: en = en[1:]
        n = min(len(st), len(en)); return list((en[:n] - st[:n]) * DT)
    return float(np.median(runs(fast_retro)[1:-1])), float(np.median(runs(slow)[1:-1]))
out["pause_threshold"] = dict(per_planet=thr_table, common_threshold_arcmin_per_day=round(common * 60, 2),
    at_common_threshold={p: dict(zip(("retrograde_moving_days", "pause_days"), [round(x, 1) for x in phases_at(p, common)])) for p in ("Mars", "Jupiter", "Saturn")})
mr, mp = phases_at("Mars", common)
out["mars_82_explained?"] = dict(retrograde_moving=round(mr, 1), plus_two_pauses=round(mr + 2 * mp, 1), inscribed=82)
json.dump(out, open(os.path.join(HERE, "residuals_results.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
