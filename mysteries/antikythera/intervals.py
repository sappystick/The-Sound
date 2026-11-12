#!/usr/bin/env python3
"""Antikythera Front Cover Inscription: the synodic phase intervals, checked against real planetary motion.

Orbits: Keplerian, coplanar (inclinations ignored: they barely change timing), J2000 elements, propagated over 300 years
centred on 150 BC. For every synodic cycle we time: conjunctions, oppositions, stations (geocentric motion reverses) and,
for Mercury and Venus, greatest elongations. That gives the real distribution (min, median, max) of each interval.
FCI numbers (Anastasiou, Bitsakis, Jones, Moussas, Tselikas, Zafeiropoulou, Almagest 7.1, 2016, lines 5-41):
  Venus  superior conj -> greatest evening elongation 224 d; greatest elongation -> inferior conj 68 d;
         inferior conj -> greatest morning elongation 68 d; morning station -> greatest morning elongation 49 d (?)
  Mars   evening station -> conj 349 d; conj -> morning station 349 d; retrograde 82 d
  Jupiter evening station -> conj 139 d; conj -> morning station 139 d; 8 d pause at each station; retrograde 104 d
  Saturn  only an 8 d pause survives
Unplaced fragments with unidentified numerals: "64" (or ...64) and "324 or 224".
Usage: python3 intervals.py"""
import json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
EL = {  # a (AU), e, longitude of perihelion (deg), mean longitude at J2000 (deg), mean motion (deg/day)
 "Mercury": (0.38710, 0.20563, 77.456, 252.251, 4.09233445), "Venus": (0.72333, 0.00677, 131.53, 181.980, 1.60213034),
 "Earth": (1.00000, 0.01671, 102.937, 100.464, 0.98560910), "Mars": (1.52368, 0.09340, 336.04, 355.433, 0.52403840),
 "Jupiter": (5.20260, 0.04849, 14.75, 34.351, 0.08308529), "Saturn": (9.55491, 0.05551, 92.43, 50.077, 0.03344414)}
def pos(p, t):
    a, e, w, L0, n = EL[p]; M = np.radians((L0 + n * t - w) % 360); E = M.copy()
    for _ in range(8): E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2)); r = a * (1 - e * np.cos(E)); th = nu + np.radians(w)
    return r * np.cos(th), r * np.sin(th)
DT = 0.05; t = np.arange(-(2000 + 150 + 150) * 365.25, -(2000 + 150 - 150) * 365.25, DT)   # 300 years around 150 BC (days from J2000)
xe, ye = pos("Earth", t); sun = np.degrees(np.arctan2(-ye, -xe))
def unwrap(x): return np.degrees(np.unwrap(np.radians(x)))
def events(p):
    x, y = pos(p, t); lam = np.degrees(np.arctan2(y - ye, x - xe)); elong = (lam - sun + 180) % 360 - 180      # planet - sun, -180..180
    lamu = unwrap(lam); v = np.gradient(lamu, DT)
    st = np.where(np.diff(np.sign(v)) != 0)[0]                                       # stations
    conj = np.where((np.diff(np.sign(elong)) != 0) & (np.abs(elong[:-1]) < 90))[0]      # conjunctions
    opp = np.where((np.diff(np.sign(elong)) != 0) & (np.abs(elong[:-1]) > 90))[0]       # oppositions (superior planets)
    ge = np.where(np.diff(np.sign(np.gradient(np.abs(elong), DT))) < 0)[0]             # greatest elongations (local max of |elong|)
    ev = sorted([(i * DT, "station_retro_start" if v[i + 1] < 0 else "station_direct_start") for i in st] +
                [(i * DT, ("inferior_conj" if v[i] < 0 else "superior_conj") if p in ("Mercury", "Venus") else "conj") for i in conj] +
                [(i * DT, "opposition") for i in opp] +
                ([(i * DT, "ge_evening" if elong[i] > 0 else "ge_morning") for i in ge] if p in ("Mercury", "Venus") else []))
    return ev
def intervals(ev, a, b, after_first=True):
    """durations from each event a to the next event b."""
    out = []
    for k, (ti, ki) in enumerate(ev):
        if ki != a: continue
        nxt = next((tj for tj, kj in ev[k + 1:] if kj == b), None)
        if nxt is not None: out.append(nxt - ti)
    return np.array(out)
def summary(x): return dict(n=len(x), min=round(float(x.min()), 1), median=round(float(np.median(x)), 1), max=round(float(x.max()), 1)) if len(x) else None
R = {}
INF = {"superior conj -> greatest evening elongation": ("superior_conj", "ge_evening"), "greatest evening elongation -> inferior conj": ("ge_evening", "inferior_conj"),
       "inferior conj -> greatest morning elongation": ("inferior_conj", "ge_morning"), "morning station (direct start) -> greatest morning elongation": ("station_direct_start", "ge_morning"),
       "evening station (retro start) -> inferior conj": ("station_retro_start", "inferior_conj"), "inferior conj -> morning station": ("inferior_conj", "station_direct_start"),
       "superior conj -> evening station": ("superior_conj", "station_retro_start"), "retrograde (station to station)": ("station_retro_start", "station_direct_start"),
       "greatest morning elongation -> superior conj": ("ge_morning", "superior_conj")}
SUP = {"evening station (direct start) -> conj": ("station_direct_start", "conj"), "conj -> morning station (retro start)": ("conj", "station_retro_start"),
       "retrograde (station to station)": ("station_retro_start", "station_direct_start"), "morning station -> opposition": ("station_retro_start", "opposition"),
       "direct motion (station to station)": ("station_direct_start", "station_retro_start")}
for p in EL:
    if p == "Earth": continue
    ev = events(p); table = INF if p in ("Mercury", "Venus") else SUP
    R[p] = {name: summary(intervals(ev, a, b)) for name, (a, b) in table.items()}
FCI = [("Venus", "superior conj -> greatest evening elongation", 224), ("Venus", "greatest evening elongation -> inferior conj", 68), ("Venus", "inferior conj -> greatest morning elongation", 68),
       ("Venus", "morning station (direct start) -> greatest morning elongation", 49), ("Mars", "evening station (direct start) -> conj", 349), ("Mars", "conj -> morning station (retro start)", 349),
       ("Mars", "retrograde (station to station)", 82), ("Jupiter", "evening station (direct start) -> conj", 139), ("Jupiter", "conj -> morning station (retro start)", 139),
       ("Jupiter", "retrograde (station to station)", 104 + 16)]
check = []
for p, name, val in FCI:
    s = R[p][name]; inside = s["min"] <= val <= s["max"]
    check.append(dict(planet=p, interval=name, inscribed=val, real=s, within_real_range=inside, minus_median=round(val - s["median"], 1)))
R["FCI_check"] = check
# Saturn prediction with the inscription's own scheme (as for Jupiter): retrograde motion R + two 8-day pauses, equal direct halves
sat = R["Saturn"]; retro = sat["retrograde (station to station)"]["median"]; syn = 378
R["Saturn_prediction"] = dict(real_retrograde_median=retro, real_direct_half_median=sat["evening station (direct start) -> conj"]["median"],
                              inscription_scheme=f"2 x {round((syn - retro) / 2)} + 2 x 8 + {round(retro - 16)} = {2 * round((syn - retro) / 2) + 16 + round(retro - 16)}",
                              predicted_direct_halves=round((syn - retro) / 2), predicted_retrograde_motion_days=round(retro - 16))
# unplaced numerals: which phase intervals (any planet) fall within 3 days of 64, 224, 324?
hits = {}
for target in (64, 224, 324):
    hits[target] = [f"{p}: {name} (median {s['median']}, range {s['min']}-{s['max']})" for p in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn") for name, s in R[p].items() if s and s["min"] - 3 <= target <= s["max"] + 3]
R["unplaced_numerals"] = hits
json.dump(R, open(os.path.join(HERE, "intervals_results.json"), "w"), indent=1)
for c in check: print(f"{c['planet']:8s} {c['interval']:62s} inscribed {c['inscribed']:4d}  real {c['real']['min']}-{c['real']['max']} (median {c['real']['median']})  {'within range' if c['within_real_range'] else 'OUTSIDE real range'}")
print("SATURN prediction:", R["Saturn_prediction"])
for k, v in hits.items(): print(f"unplaced numeral {k}:", v or "no phase interval matches")
