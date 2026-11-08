#!/usr/bin/env python3
"""Build an 'earliest witness' text of John: for each verse the oldest surviving manuscript
(P75, then P66, then Vaticanus 03, then Sinaiticus 01), from the CNTR transcriptions.
Then rerun: prologue centre, 'I am' ring, and the 18 unit centres, and compare with SBLGNT.
Usage: python3 earliest_text.py "<cntr>/class 1"
"""
import json, os, random, sys
sys.argv = [sys.argv[0], sys.argv[1]]
import papyri as P   # reuse the loader, cleaner and syllable counter
src = {ms: P.load(ms, 43) for ms in ("P75", "P66", "03", "01")}
verses = sorted(set().union(*[set(v) for v in src.values()]))
rows, used = [], {}
for v in verses:
    for ms in ("P75", "P66", "03", "01"):
        raw = src[ms].get(v)
        if raw and raw.count("^") < len(raw) * 0.2:   # skip verses that are mostly lacuna in that witness
            for w in P.clean_words(raw): rows.append((v, *w))
            used[ms] = used.get(ms, 0) + 1; break
S = [P.syl(r[1]) for r in rows]; T = sum(S)
cum = [0]
for s in S: cum.append(cum[-1] + s)
first = {}
for i, r in enumerate(rows): first.setdefault(r[0], i)
print(f"earliest-witness John: {len(verses)} verses, sources used {used}, {T} syllables")
pro = [i for i, r in enumerate(rows) if r[0] <= (1, 18)]; pt = sum(S[i] for i in pro)
piv = next(i for i in pro if rows[i][0] == (1, 12) and rows[i][1].startswith("εδωκ"))
print(f"prologue centre: {sum(S[i] for i in pro if i < piv) / pt:.4f} ({sum(S[i] for i in pro if i < piv) - pt / 2:+.1f} of {pt})")
SAY = [(6, 35), (8, 12), (10, 7), (10, 11), (11, 25), (14, 6), (15, 1)]
ps = sorted(cum[first[k]] / T for k in SAY)
err = sum(abs((ps[i] - .5) + (ps[6 - i] - .5)) for i in range(3)); rng = random.Random(3)
p = sum(sum(abs((x[i] - .5) + (x[6 - i] - .5)) for i in range(3)) <= err for x in (sorted(rng.random() for _ in range(7)) for _ in range(50000))) / 50000
mid = min(first, key=lambda k: abs(cum[first[k]] - T / 2))
print(f"'I am' ring: middle saying at {ps[3]:.3f}, p = {p:.3f}; Gospel's spoken midpoint at {mid[0]}:{mid[1]}")
UN = [("Prologue", (1, 1), (1, 18)), ("Cana", (2, 1), (2, 11)), ("Samaritan woman", (4, 1), (4, 42)), ("Bethesda", (5, 1), (5, 47)),
      ("Tabernacles", (7, 1), (8, 59)), ("Shepherd (9:41)", (9, 41), (10, 21)), ("Lazarus", (11, 1), (11, 44)), ("Pilate", (18, 28), (19, 16))]
out = {}
for lab, a, b in UN:
    idx = [i for i, r in enumerate(rows) if a <= r[0] <= b]; tt = sum(S[i] for i in idx); acc = 0
    for i in idx:
        if acc + S[i] > tt / 2: c = rows[i][0]; break
        acc += S[i]
    out[lab] = f"{c[0]}:{c[1]}"; print(f"   {lab:18s} centre {c[0]}:{c[1]}")
json.dump(dict(sources=used, syllables=T, ring_middle=ps[3], ring_p=p, midpoint=f"{mid[0]}:{mid[1]}", centres=out),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "earliest_text_results.json"), "w"), indent=1)
