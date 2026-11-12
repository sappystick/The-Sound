#!/usr/bin/env python3
"""Round 92 C: low-rate channels (PREREG_92.md). Five candidate hidden sequences, each tested for ORDER against
1,000 within-page shuffles (bigram conditional entropy; lower = more ordered), Holm over 5; plus repeated 4-grams of
line-initial glyphs across pages (an acrostic signature).
Usage: python3 mysteries/voynich/channels.py"""
import collections, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zl import load
HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(921); NS = 1000
V = load(); PG = [p for p in V.values() if p["lines"]]
GAL = "ktpf"
seqs = {
    "first glyph of each line": [[l[0][0] for l in p["lines"]] for p in PG],
    "last glyph of each line": [[l[-1][-1] for l in p["lines"]] for p in PG],
    "first word of each paragraph": [[pa[0] for pa in p["paras"]] for p in PG],
    "gallows glyph of each line (first, or '-')": [[next((c for w in l for c in w if c in GAL), "-") for l in p["lines"]] for p in PG],
    "every 7th word": [[w for i, w in enumerate([w for l in p["lines"] for w in l]) if i % 7 == 6] for p in PG],
}
def cond_H(S):
    big = collections.Counter(); uni = collections.Counter()
    for s in S:
        for a, b in zip(s, s[1:]): big[(a, b)] += 1; uni[a] += 1
    n = sum(big.values())
    return -sum(c / n * math.log2(c / uni[a]) for (a, b), c in big.items()) if n else float("nan")
def shuf(S): return [list(rng.permutation(s)) if len(s) > 1 else s for s in S]
R = {}; ps = {}
for name, S in seqs.items():
    S = [s for s in S if len(s) >= 2]; obs = cond_H(S); null = np.array([cond_H(shuf(S)) for _ in range(NS)])
    p = float((np.sum(null <= obs) + 1) / (NS + 1)); ps[name] = p
    R[name] = dict(pages=len(S), symbols=sum(len(s) for s in S), cond_entropy=round(obs, 4), null_mean=round(float(null.mean()), 4), null_1pct=round(float(np.percentile(null, 1)), 4), p_more_ordered=round(p, 4))
    print(f"{name:42s} H {obs:.4f}  null {null.mean():.4f}  p {p:.4f}")
order = sorted(ps, key=ps.get); holm = {}
for i, k in enumerate(order):
    holm[k] = ps[k] <= 0.01 / (len(order) - i)
    if not holm[k]:
        for k2 in order[i + 1:]: holm[k2] = False
        break
for k in R: R[k]["carries_order_after_holm"] = bool(holm.get(k, False))
# acrostic: repeated 4-grams of line-initial glyphs across different pages
def rep4(S):
    where = collections.defaultdict(set)
    for i, s in enumerate(S):
        for j in range(len(s) - 3): where["".join(s[j:j + 4])].add(i)
    return sum(1 for g, pg in where.items() if len(pg) >= 3)
S = [s for s in seqs["first glyph of each line"] if len(s) >= 4]; obs = rep4(S); null = np.array([rep4(shuf(S)) for _ in range(300)])
R["acrostic: line-initial 4-grams on >= 3 pages"] = dict(observed=obs, null_mean=round(float(null.mean()), 1), p=round(float((np.sum(null >= obs) + 1) / 301), 4))
print("acrostic 4-grams on >=3 pages:", R["acrostic: line-initial 4-grams on >= 3 pages"])
R["decision"] = {k: ("CARRIES ORDER" if R[k]["carries_order_after_holm"] else "NO HIDDEN CHANNEL") for k in seqs}
json.dump(R, open(os.path.join(HERE, "channels_results.json"), "w"), indent=1, ensure_ascii=False)
print(R["decision"])

# EXPLORATORY confound control (not pre-registered): paragraphs open with a gallows glyph, and a within-page shuffle
# destroys that. Here only the non-opening lines are shuffled, within their own paragraph; opening lines stay put.
# If the order survives, it is not just "paragraph openings are special".
def para_blocks(p):
    blocks, cur = [], []
    for l, st in zip(p["lines"], p["starts"]):
        if st and cur: blocks.append(cur); cur = []
        cur.append(l)
    if cur: blocks.append(cur)
    return blocks
def shuf_keep_openings(B):
    out = []
    for blk in B:
        rest = [blk[i] for i in rng.permutation(len(blk) - 1) + 1] if len(blk) > 2 else blk[1:]
        out.append([blk[0]] + rest)
    return out
BL = [para_blocks(p) for p in PG]
def seq_from(blocks, f): return [[f(l) for blk in pb for l in blk] for pb in blocks]
for name, f in (("first glyph of each line", lambda l: l[0][0]), ("gallows glyph of each line (first, or '-')", lambda l: next((c for w in l for c in w if c in GAL), "-"))):
    obs = cond_H([s for s in seq_from(BL, f) if len(s) >= 2])
    null = np.array([cond_H([s for s in seq_from([shuf_keep_openings(pb) for pb in BL], f) if len(s) >= 2]) for _ in range(NS)])
    p = float((np.sum(null <= obs) + 1) / (NS + 1))
    R[name]["EXPLORATORY_keep_paragraph_openings"] = dict(null_mean=round(float(null.mean()), 4), p=round(p, 4))
    print(f"[expl] {name:42s} keeping openings fixed: H {obs:.4f} null {null.mean():.4f} p {p:.4f}")
# what drives it: glyph distribution of opening vs other lines
op = collections.Counter(l[0][0] for p in PG for l, st in zip(p["lines"], p["starts"]) if st); ot = collections.Counter(l[0][0] for p in PG for l, st in zip(p["lines"], p["starts"]) if not st)
R["line_initial_glyph_opening_vs_other"] = dict(opening=dict(op.most_common(6)), other=dict(ot.most_common(6)))
print(R["line_initial_glyph_opening_vs_other"])
json.dump(R, open(os.path.join(HERE, "channels_results.json"), "w"), indent=1, ensure_ascii=False)
