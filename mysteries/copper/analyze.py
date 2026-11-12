#!/usr/bin/env python3
"""Copper Scroll (3Q15) tests on Milik's 1960 translation (entries.py).
T1 POSITION   all seven Greek groups fall in entries 1-17 (columns I-IV) of 64: exact chance.
T2 ORDER      Greek numerals are written largest value first (e.g. 75 = ΟΕ, not ΕΟ). Are the groups in numeral order?
T3 VALUES     do the groups' letter values equal their own entry's amount, or any amount in the scroll? Null: random
              Greek letter groups of the same lengths.
T4 NUMBERS    the amounts: totals, repeated values and round numbers, against a smooth (log-uniform) null.
T5 PLACES     securely identified places as KLIMATA codes (speakable, self-repairing place codes, round 71).
Usage: python3 analyze.py"""
import itertools, json, math, os, random, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "lang4d", "fields")); sys.path.insert(0, os.path.join(HERE, "..", "..", "lang4d"))
from entries import ENTRIES
GV = dict(zip("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800]))
R = random.Random(15); out = {}
G = [(e["n"], e["greek"], e["talents"]) for e in ENTRIES if e["greek"]]
# T1
k, n, first = len(G), len(ENTRIES), max(g[0] for g in G)
out["T1_position"] = dict(entries=[g[0] for g in G], all_within_first=first, p_exact=math.comb(first, k) / math.comb(n, k),
                          note="probability that 7 of 64 entries chosen at random all fall within the first 17")
# T2
desc = [g[1] for g in G if all(GV[a] >= GV[b] for a, b in zip(g[1], g[1][1:]))]
p_desc = math.prod(1 / math.factorial(len(g[1])) for g in G)   # chance a random ordering of each group is descending
sim = []
for _ in range(100000): sim.append(sum(1 for g in G if (lambda s: all(GV[a] >= GV[b] for a, b in zip(s, s[1:])))(R.sample(g[1], len(g[1])))))
out["T2_numeral_order"] = dict(groups=[g[1] for g in G], in_descending_numeral_order=desc, count=len(desc), expected_if_random_order=round(sum(1 / math.factorial(len(g[1])) for g in G), 2),
                               p_as_many_or_fewer=round(sum(x <= len(desc) for x in sim) / len(sim), 3), note="standard numerals would be ALL descending (7 of 7)")
# T3
vals = {g[1]: sum(GV[c] for c in g[1]) for g in G}; amounts = sorted({e["talents"] for e in ENTRIES if e["talents"]} | {609, 100, 65, 300})
own = [(g[1], vals[g[1]], g[2]) for g in G]; hits = [(gk, v) for gk, v in vals.items() if v in amounts]
letters = list(GV)
def rand_hits():
    h = 0
    for g in G:
        v = sum(GV[R.choice(letters)] for _ in g[1])
        h += v in amounts
    return h
sim = [rand_hits() for _ in range(100000)]
out["T3_values"] = dict(values=vals, own_entry_amounts={g[1]: g[2] for g in G}, equal_to_own_amount=[o for o in own if o[1] == o[2]],
                        equal_to_some_amount_in_scroll=hits, p_this_many_hits_by_chance=round(sum(x >= len(hits) for x in sim) / len(sim), 3))
# T4
am = [e["talents"] for e in ENTRIES if e["talents"]]; cnt = collections.Counter(am)
rep = {v: c for v, c in cnt.items() if c > 1}; nrep = sum(c - 1 for c in rep.values())
lo, hi = min(am), max(am)
def null_rep():
    xs = [round(math.exp(R.uniform(math.log(lo), math.log(hi)))) for _ in am]; c = collections.Counter(xs); return sum(v - 1 for v in c.values() if v > 1)
sim = [null_rep() for _ in range(20000)]
mult10 = sum(1 for a in am if a == int(a) and int(a) % 10 == 0)
out["T4_numbers"] = dict(entries_with_talents=len(am), total_talents=round(sum(am), 2), largest=sorted(am)[-5:], repeated_values=rep, repeats=nrep,
                         null_mean_repeats=round(sum(sim) / len(sim), 2), p_repeats=round(sum(x >= nrep for x in sim) / len(sim), 4),
                         multiples_of_10=f"{mult10}/{len(am)}", depths=collections.Counter(e["depth_cubits"] for e in ENTRIES if e["depth_cubits"]))
# T5
import geocode as GC, skins as S, kanon as K
SITES = {  # securely identified places named in the scroll (approximate coordinates)
 "Mount Garizin (entry 61)": (32.1997, 35.2730), "Bet-Shan, fountain (62)": (32.5005, 35.4983), "Pool of Siloah (51)": (31.7706, 35.2353),
 "Hand of Absalom (50)": (31.7766, 35.2388), "Gorge of ha-Qedron (37)": (31.7720, 35.2400), "Kephar Nebo, Mount Nebo (44)": (31.7676, 35.7253),
 "Bet Horon (42)": (31.8860, 35.1300), "Jericho, road to Sekaka (26)": (31.8710, 35.4440), "Valley of Achor, el-Buqeia (1, proposed)": (31.7250, 35.4150),
 "Khirbet Qumran, where the scroll was found": (31.7410, 35.4590)}
out["T5_places"] = {name: dict(latlon=ll, code=GC.text(GC.encode(*ll), parity=True), spoken=GC.english(GC.encode(*ll))) for name, ll in SITES.items()}
json.dump(out, open(os.path.join(HERE, "copper_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "T5_places"}, ensure_ascii=False, indent=1, default=str))
for k, v in out["T5_places"].items(): print(f"   {k:44s} {v['spoken']}")
