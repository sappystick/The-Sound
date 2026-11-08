#!/usr/bin/env python3
"""Analyses on the automatically coded passages (an independent 'second coder').

Filter: keep passages that mention at least one RITE thread (not just time/place words), so that
battle narrative in Josephus is excluded.
1. Hub test: rebuild the category network (as power_map.py) from these passages alone; is dawn
   still the hub?  Compared with 1,000 networks in which each category's occurrences are shuffled
   across passages (keeps every category's frequency, breaks co-occurrence).
2. Source profiles: which instruction types and rites each source emphasises.
3. Blood: what blood rites co-occur with, against water rites.
"""
import collections, csv, itertools, json, os, random
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
RITE = {"washing", "incense", "lamp_light", "prostration", "sung_praise", "instruments", "sacred_name", "circling", "plants",
        "blood_rite", "bread_offering", "wine_libation", "water_libation", "linen", "inner_room", "anointing", "fasting_abstinence"}
FT = ["time", "place", "direction", "repetition", "posture", "voice", "materials"]
rows = list(csv.DictReader(open(os.path.join(HERE, "data", "auto_records.csv"), encoding="utf-8")))
keep = [r for r in rows if RITE & set(x.strip() for x in r["threads"].split(";") if x.strip())]
print(f"{len(rows)} auto passages; {len(keep)} mention a rite")
print(collections.Counter(r["source"] for r in keep).most_common())


def toks(r):
    t = {f"{ft}:{x.strip()}" for ft in FT for x in r[ft].split(";") if x.strip()}
    return t | {f"rite:{x.strip()}" for x in r["threads"].split(";") if x.strip() in RITE}


sets = [toks(r) for r in keep]


def network(sets):
    G = nx.Graph()
    for s in sets:
        for a, b in itertools.combinations(sorted(s), 2):
            G.add_edge(a, b, weight=G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1)
    return G


G = network(sets); deg = dict(G.degree(weight="weight"))
btw = nx.betweenness_centrality(G, weight=lambda u, v, e: 1 / e["weight"])
top = sorted(G, key=lambda n: -deg[n])[:15]
print("\nhubs (independent automatic coding):")
for n in top: print(f"   {n:24s} strength {deg[n]:6d}  bridge {btw[n]:.3f}")
rank_dawn = sorted(G, key=lambda n: -deg[n]).index("time:dawn") + 1 if "time:dawn" in G else None
rank_dawn_b = sorted(G, key=lambda n: -btw[n]).index("time:dawn") + 1 if "time:dawn" in G else None
print(f"time:dawn ranks #{rank_dawn} by strength, #{rank_dawn_b} by bridging, of {G.number_of_nodes()}")

# shuffle null for dawn's bridging (keeps frequencies)
occ = collections.defaultdict(list)
for i, s in enumerate(sets):
    for t in s: occ[t].append(i)
rng = random.Random(4); cnt = 0; R = 200
real_b = btw.get("time:dawn", 0)
for _ in range(R):
    sh = [set() for _ in sets]
    for t, idx in occ.items():
        for j in rng.sample(range(len(sets)), len(idx)): sh[j].add(t)
    Gs = network(sh); bs = nx.betweenness_centrality(Gs, weight=lambda u, v, e: 1 / e["weight"])
    cnt += bs.get("time:dawn", 0) >= real_b
print(f"dawn bridging {real_b:.3f}; shuffled networks with as much: {cnt}/{R}")

# source profiles: share of rite passages mentioning each rite
print("\nrite profile by source (share of that source's rite passages):")
prof = {}
for src in sorted({r["source"] for r in keep}):
    rs = [r for r in keep if r["source"] == src]; c = collections.Counter(t for r in rs for t in r["threads"].split("; ") if t in RITE)
    prof[src] = {k: round(v / len(rs), 2) for k, v in c.most_common(6)}
    print(f"   {src:32s} n={len(rs):4d} " + ", ".join(f"{k} {v:.0%}" for k, v in prof[src].items()))

# blood vs water: co-occurring categories
def cooc(rite):
    rs = [s for s in sets if f"rite:{rite}" in s]; c = collections.Counter(t for s in rs for t in s if not t.startswith("rite:" + rite))
    return len(rs), [(k, round(v / len(rs), 2)) for k, v in c.most_common(8)]
for rt in ("blood_rite", "washing"):
    n, top8 = cooc(rt); print(f"\n{rt}: {n} passages; most frequent companions: {top8}")
json.dump(dict(kept=len(keep), hubs=[(n, deg[n], round(btw[n], 3)) for n in top], dawn_rank=[rank_dawn, rank_dawn_b],
               dawn_null=[cnt, R], profiles=prof), open(os.path.join(HERE, "data", "auto_analysis.json"), "w"), indent=1)
