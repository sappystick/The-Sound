#!/usr/bin/env python3
"""The Voynich's possible keys.
K1 f49v: a single letter stands at the start of each text line. Does it relate to its line (equal to the line's first
   glyph; present in the line; tied to the line's length)? Null: letters shuffled among lines.
K2 f57v: a 17-glyph sequence written four times in a ring. Is its ORDER derived from the text (are ring-neighbour glyphs
   frequent text bigrams; does the order follow glyph frequency)? Null: the 17 glyphs in random order.
K3 zodiac (12 pages, about 30 star-labels each, read in order around the rings): do neighbouring labels share forms
   more than chance (a counted sequence?), and do labels at the SAME position on different months resemble each other
   (as day names or numbers would)? Nulls: label order shuffled within each page.
Usage: python3 keys.py <IT2a-n.txt>"""
import collections, json, os, re, sys
import numpy as np
VP = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(81)
LOC = []
for l in open(VP, encoding="utf-8", errors="replace"):
    m = re.match(r"<(f\w+?)\.(\d+),(.)(\w)(\w*)>\s+(.*)", l)
    if m: LOC.append((m.group(1), int(m.group(2)), m.group(4) + m.group(5), re.sub(r"<[^>]*>", " ", m.group(6))))
def words(s): s = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", s); return [w for w in re.split(r"[.,\s]", s.replace("!", "").replace("%", "")) if re.fullmatch(r"[a-z]+", w)]
text_words = [w for p, n, t, s in LOC if t.startswith("P") for w in words(s)]
out = {}
# K1
f49 = sorted([x for x in LOC if x[0] == "f49v"], key=lambda x: x[1]); pairs = []
for a, b in zip(f49, f49[1:]):
    if a[2].startswith("L") and b[2].startswith("P"):
        ws = words(b[3]); letter = a[3].strip()
        if ws and re.fullmatch(r"[a-z]", letter): pairs.append((letter, ws))
def k1_stats(P):
    first = sum(1 for le, ws in P if ws[0][0] == le) / len(P); inline = sum(1 for le, ws in P if any(le in w for w in ws)) / len(P)
    return first, inline
obs = k1_stats(pairs); null = [k1_stats(list(zip(rng.permutation([p[0] for p in pairs]), [p[1] for p in pairs]))) for _ in range(5000)]
out["K1_f49v"] = dict(pairs=len(pairs), letters="".join(p[0] for p in pairs), letter_equals_first_glyph=round(obs[0], 3), null_first=round(float(np.mean([n[0] for n in null])), 3),
                      p_first=round(float(np.mean([n[0] >= obs[0] for n in null])), 4), letter_in_line=round(obs[1], 3), null_in_line=round(float(np.mean([n[1] for n in null])), 3),
                      p_in_line=round(float(np.mean([n[1] >= obs[1] for n in null])), 4))
# K2
ring = [g for g in next(s for p, n, t, s in LOC if p == "f57v" and n == 3).split() if g not in ("<->",)]
seq = [g for g in ring[:17]]
glyph_text = "".join(text_words); bigram = collections.Counter(glyph_text[i:i + 2] for i in range(len(glyph_text) - 1)); gfreq = collections.Counter(glyph_text)
def ring_score(order):
    return sum(np.log1p(bigram[a + b]) for a, b in zip(order, order[1:]) if "?" not in (a, b))
real = ring_score(seq); null = [ring_score(list(rng.permutation(seq))) for _ in range(20000)]
known = [g for g in seq if g != "?"]; ranks = [gfreq[g] for g in known]
from itertools import combinations
conc = sum(1 for (i, a), (j, b) in combinations(enumerate(ranks), 2) if (a - b) * (i - j) < 0) - sum(1 for (i, a), (j, b) in combinations(enumerate(ranks), 2) if (a - b) * (i - j) > 0)
out["K2_f57v"] = dict(sequence=" ".join(seq), glyph_text_frequency={g: gfreq[g] for g in dict.fromkeys(known)}, neighbour_bigram_score=round(float(real), 2),
                      null_mean=round(float(np.mean(null)), 2), p_neighbours_more_text_like=round(float(np.mean(np.array(null) >= real)), 4),
                      kendall_concordance_order_vs_frequency=conc, note="positive = earlier glyphs more frequent")
# K3
zod = collections.OrderedDict()
for p, n, t, s in LOC:
    if t == "Lz": zod.setdefault(p, []).append((words(s) or ["?"])[0])
def sim(a, b):
    k = 0
    while k < min(len(a), len(b)) and a[k] == b[k]: k += 1
    return k / max(len(a), len(b))
def adj(pages): return float(np.mean([sim(a, b) for L in pages.values() for a, b in zip(L, L[1:])]))
def cross(pages):
    Ls = list(pages.values()); m = min(len(L) for L in Ls); s = []
    for i in range(len(Ls)):
        for j in range(i + 1, len(Ls)):
            s += [sim(Ls[i][k], Ls[j][k]) for k in range(m)]
    return float(np.mean(s))
obs_adj, obs_cross = adj(zod), cross(zod)
nulls = [{p: list(rng.permutation(L)) for p, L in zod.items()} for _ in range(2000)]
na = [adj(x) for x in nulls]; nc = [cross(x) for x in nulls]
out["K3_zodiac"] = dict(labels_per_page={p: len(L) for p, L in zod.items()}, total=sum(len(L) for L in zod.values()),
                        neighbour_similarity=round(obs_adj, 3), null=round(float(np.mean(na)), 3), p_neighbours=round(float(np.mean(np.array(na) >= obs_adj)), 4),
                        same_position_across_months=round(obs_cross, 3), null_cross=round(float(np.mean(nc)), 3), p_same_position=round(float(np.mean(np.array(nc) >= obs_cross)), 4),
                        first_labels_each_page=[L[0] for L in zod.values()], prefix_ot_or_ok=round(float(np.mean([w[:2] in ("ot", "ok") for L in zod.values() for w in L])), 3))
json.dump(out, open(os.path.join(HERE, "keys_results.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
