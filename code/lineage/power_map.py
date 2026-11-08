#!/usr/bin/env python3
"""The connected map.
1. Stated power: for records whose source says what makes the rite effective, tally the
   categories by era (what each tradition itself names as the source of power).
2. Network: every normalised category (time, place, direction, posture, voice, materials,
   elements, power) is a node; two nodes are linked when they occur in the same record.
   Hubs (weighted degree), bridges (betweenness) and reach (how many traditions use a node).
"""
import collections, itertools, json, os
import networkx as nx
from records import R
from test_handover import tokens, FIELDS

ORDER = ["Egypt", "Hebrew Bible", "Second Temple Judaism (Qumran, Philo, Josephus)", "Mishnah (Second Temple practice)",
         "Greco-Roman mysteries", "Early church", "Islam", "Living tradition"]
short = lambda t: t.split(" (")[0]
pw = collections.defaultdict(collections.Counter); nrec = collections.Counter()
for d in R:
    if d["power"]:
        nrec[d["tradition"]] += 1
        for c in [x.strip() for x in d["power"].split(";") if x.strip()]: pw[d["tradition"]][c] += 1
print("STATED SOURCE OF POWER, by tradition (records stating it):")
for t in ORDER:
    if t in pw: print(f"  {short(t):24s} n={nrec[t]:2d}  " + ", ".join(f"{k} {v}" for k, v in pw[t].most_common()))

G = nx.Graph(); reach = collections.defaultdict(set)
for d in R:
    toks = set()
    for ft in FIELDS:
        toks |= {f"{ft}:{x}" for x in tokens(d, ft)}
    toks |= {f"element:{x.strip()}" for x in d["elements"].split(";") if x.strip() and not x.strip().startswith("(")}
    toks |= {f"power:{x.strip()}" for x in d["power"].split(";") if x.strip()}
    for x in toks: reach[x].add(short(d["tradition"]))
    for a, b in itertools.combinations(sorted(toks), 2):
        G.add_edge(a, b, weight=G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1)
deg = dict(G.degree(weight="weight"))
btw = nx.betweenness_centrality(G, weight=lambda u, v, e: 1 / e["weight"])
rows = sorted(G.nodes, key=lambda n: -deg[n])
print(f"\nNETWORK: {G.number_of_nodes()} categories, {G.number_of_edges()} links")
print(f"{'category':26s} {'strength':>8s} {'bridge':>7s} {'traditions':>10s}")
for n in rows[:22]:
    print(f"{n:26s} {deg[n]:8d} {btw[n]:7.3f} {len(reach[n]):10d}")
comms = nx.algorithms.community.greedy_modularity_communities(G, weight="weight")
print("\nCLUSTERS (categories that travel together):")
for i, c in enumerate(comms):
    print(f"  {i + 1}: " + ", ".join(sorted(c, key=lambda n: -deg[n])[:10]))
# which power categories link most strongly to which practices?
print("\nPOWER -> strongest linked practice categories:")
for p in sorted([n for n in G if n.startswith("power:")], key=lambda n: -deg[n]):
    nb = sorted(G[p].items(), key=lambda kv: -kv[1]["weight"])[:5]
    print(f"  {p:22s} " + ", ".join(f"{k}({v['weight']})" for k, v in nb))
json.dump(dict(stated_power={short(t): dict(pw[t]) for t in pw},
               hubs=[dict(node=n, strength=deg[n], bridge=round(btw[n], 3), traditions=sorted(reach[n])) for n in rows],
               clusters=[sorted(c) for c in comms]),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "power_map.json"), "w"), indent=1, ensure_ascii=False)
