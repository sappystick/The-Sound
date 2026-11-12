#!/usr/bin/env python3
"""Antikythera Mechanism: the planetary period relations, tested.

A period relation (s, y) says: s synodic cycles of a planet take y years. Freeth et al. 2021 (Sci. Rep. 11:5821)
read two of them in the Front Cover Inscription (Venus (289, 462), Saturn (427, 442); numbers first identified in
the Almagest 7.1 2016 edition) and reconstructed the rest: Mercury (1513, 480), Mars (133, 284), Jupiter (315, 344).
The gears need prime factors below 100 ("factorizable").
Tests, all against modern mean motions (J2000 rates, the same table as KANON's phase stamps):
  1 ACCURACY      each relation's error in days per synodic cycle and in degrees per century
  2 RARITY        among ALL relations with y <= 500 years, how many factorizable ones are at least as accurate?
                  (is the chosen relation the best a designer could have found, or just a good one?)
  3 BABYLONIAN    can each relation be written as a small integer combination of the Babylonian relations
                  (Goal-Year Texts and Astronomical Cuneiform Texts) the Greeks inherited?
  4 SHARED PRIMES the economy criterion: do the chosen relations share prime factors more than chance would give?
Usage: python3 periods.py"""
import itertools, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
N = {"Sun": 0.98564736, "Mercury": 4.09233445, "Venus": 1.60213034, "Mars": 0.52402068, "Jupiter": 0.08308529, "Saturn": 0.03349791}   # deg/day, J2000 mean
YEAR = 360 / N["Sun"]                                                                     # tropical-ish year in days (365.2422)
def synodic(p): return 360 / abs(N[p] - N["Sun"])                                         # days
CHOSEN = {"Mercury": (1513, 480), "Venus": (289, 462), "Mars": (133, 284), "Jupiter": (315, 344), "Saturn": (427, 442)}
SOURCE = {"Venus": "read in the FCI", "Saturn": "read in the FCI", "Mercury": "reconstructed", "Mars": "reconstructed", "Jupiter": "reconstructed"}
BABYLON = {   # (synodic cycles, years): Goal-Year Text and ACT relations (Steele; Aaboe; as listed by Freeth et al., Supp. Tables S3-S4)
 "Mercury": [(145, 46), (2673, 848)], "Venus": [(5, 8), (720, 1151)], "Mars": [(22, 47), (37, 79), (133, 284)],
 "Jupiter": [(65, 71), (76, 83), (391, 427)], "Saturn": [(57, 59), (256, 265)]}
def primes(n):
    f, d = [], 2
    while d * d <= n:
        while n % d == 0: f.append(d); n //= d
        d += 1
    return f + ([n] if n > 1 else [])
def factorizable(s, y): return max(primes(s) + primes(y) + [1]) < 100
def err(p, s, y):
    """Error of (s, y): days per synodic cycle, and degrees per century of synodic phase."""
    T = y * YEAR / s; d = T - synodic(p); phase = 360 * 36525 * (1 / synodic(p) - 1 / T)
    return d, phase
def ratio(p): return YEAR / synodic(p)              # synodic cycles per year
out = {}
for p, (s, y) in CHOSEN.items():
    d, ph = err(p, s, y)
    # all (s', y') with y' <= 500 at the best s' for that y'
    cand = []
    for yy in range(1, 501):
        ss = round(yy * ratio(p))
        if ss < 1: continue
        dd, pp = err(p, ss, yy); cand.append((abs(pp), ss, yy, factorizable(ss, yy)))
    better_any = sum(1 for c in cand if c[0] < abs(ph) and math.gcd(c[1], c[2]) == 1)
    better_fact = [c for c in cand if c[0] <= abs(ph) * 1.0000001 and c[3] and math.gcd(c[1], c[2]) == 1]
    rank_fact = sorted({(round(c[0], 6), c[1], c[2]) for c in cand if c[3] and math.gcd(c[1], c[2]) == 1})
    pos = next((k for k, c in enumerate(rank_fact) if (c[1], c[2]) == (s // math.gcd(s, y), y // math.gcd(s, y))), None)
    # Babylonian combinations with small integer coefficients (including differences)
    combos = []
    B = BABYLON[p]
    for co in itertools.product(range(-12, 13), repeat=len(B)):
        if not any(co): continue
        ss = sum(c * b[0] for c, b in zip(co, B)); yy = sum(c * b[1] for c, b in zip(co, B))
        if ss > 0 and yy > 0 and ss * y == yy * s: combos.append((sum(abs(c) for c in co), co))
    combos.sort()
    out[p] = dict(relation=(s, y), source=SOURCE[p], factors=(primes(s), primes(y)), modern_synodic_days=round(synodic(p), 4), relation_synodic_days=round(y * YEAR / s, 4),
                  error_days_per_cycle=round(d, 4), error_deg_per_century=round(ph, 3), coprime_relations_y_le_500_more_accurate=better_any,
                  rank_among_factorizable_y_le_500=(pos + 1) if pos is not None else None, factorizable_candidates=len(rank_fact),
                  best_factorizable=[(c[1], c[2], c[0]) for c in rank_fact[:3]],
                  babylonian_combination=dict(zip([f"{b}" for b in B], combos[0][1])) if combos else None)
# shared primes (economy): count prime factors <100 shared between chosen synodic numbers vs random factorizable choices
import random
R = random.Random(1); chosen_primes = [set(primes(CHOSEN[p][0])) for p in CHOSEN]
def shared(ps): return sum(1 for a, b in itertools.combinations(ps, 2) if a & b)
obs = shared(chosen_primes); pools = {}
for p in CHOSEN:
    pools[p] = [set(primes(round(yy * ratio(p)))) for yy in range(100, 501) if factorizable(round(yy * ratio(p)), yy) and abs(err(p, round(yy * ratio(p)), yy)[1]) < 5]
null = [shared([R.choice(pools[p]) for p in CHOSEN]) for _ in range(20000)]
out["economy"] = dict(planet_pairs_sharing_a_prime_in_synodic_count=obs, null_mean=round(sum(null) / len(null), 2), p_at_least_as_many=round(sum(x >= obs for x in null) / len(null), 4),
                      pools="factorizable relations with 100 <= y <= 500 and error under 5 deg/century")
# 5 CONTROL: how often is a random accurate, factorizable relation ALSO a small Babylonian combination?
def small_combo(p, s, y, maxc=12):
    B = BABYLON[p]; best = None
    for co in itertools.product(range(-maxc, maxc + 1), repeat=len(B)):
        if not any(co): continue
        ss = sum(c * b[0] for c, b in zip(co, B)); yy = sum(c * b[1] for c, b in zip(co, B))
        if ss > 0 and yy > 0 and ss * y == yy * s:
            w = sum(abs(c) for c in co); best = w if best is None or w < best else best
    return best
ctrl = {}
for p, (s, y) in CHOSEN.items():
    w_obs = small_combo(p, s, y); pool = []
    for yy in range(100, 501):
        ss = round(yy * ratio(p))
        if factorizable(ss, yy) and math.gcd(ss, yy) == 1 and abs(err(p, ss, yy)[1]) < 6: pool.append((ss, yy))
    ws = [small_combo(p, a, b) for a, b in pool]
    hit = [w for w in ws if w is not None and w <= w_obs]
    ctrl[p] = dict(combination_weight=w_obs, comparable_relations=len(pool), share_that_are_as_simple_combinations=round(len(hit) / len(pool), 3))
out["babylonian_control"] = ctrl
json.dump(out, open(os.path.join(HERE, "periods_results.json"), "w"), indent=1)
for p, r in out.items():
    if p in ("economy", "babylonian_control"): print(p.upper(), r); continue
    print(f"{p:8s} {r['relation']} ({r['source']}) factors {r['factors']}: {r['relation_synodic_days']} d vs modern {r['modern_synodic_days']} d -> {r['error_deg_per_century']:+.3f} deg/century"
          f" | rank among {r['factorizable_candidates']} factorizable (y<=500): {r['rank_among_factorizable_y_le_500']} | best: {r['best_factorizable'][:2]} | Babylonian combination: {r['babylonian_combination']}")
