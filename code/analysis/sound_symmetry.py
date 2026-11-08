#!/usr/bin/env python3
"""Does the SOUND of John 1:1-18 mirror around its center (1:12b)?

Each syllable gets its reconstructed Koine vowel (engine.parse_greek) and three sound values:
  brightness = F2 of the vowel (front i/e high, back o/u low)
  openness   = F1 of the vowel (a high, i/u low)
  peak       = 1 if the syllable carries the word accent
Test (fixed in advance): mirror correlation r(d) between the sequence before and after a
center, smoothed over 15 syllables, summed over all distances.  Compared with the same
statistic at every other possible center (>= 100 syllables on each side).
Also: the "loops" (repeated words) and their positions in spoken time.
Usage: python3 sound_symmetry.py <sblgnt dir>
"""
import collections, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E

rows = [l.split() for l in open(os.path.join(sys.argv[1], "64-Jn-morphgnt.txt"), encoding="utf-8")]
rows = [r for r in rows if r[0][:4] == "0401" and int(r[0][4:]) <= 18]
syl, word_start = [], []
for r in rows:
    v = int(r[0][4:]); word, lemma = r[4], r[6]
    sy = E.parse_greek(word, "koine")[0]
    word_start.append((len(syl), v, word, lemma))
    for s in sy:
        nuc = s["nuc"][0].rstrip("ː") if s["nuc"] else "ə"
        F1, F2, _ = E.VOWELS[nuc]
        syl.append(dict(v=v, F1=F1, F2=F2, peak=1 if s["accent"] in ("acute", "circ") else 0, nuc=nuc))
N = len(syl)
# center: first word of 1:12b (ἔδωκεν)
c = next(i for i, v, w, l in word_start if v == 12 and l == "δίδωμι")
print(f"syllables: {N}; center 1:12b starts at syllable {c} ({c / N:.4f})")


def smooth(x, k=15):
    return np.convolve(x, np.ones(k) / k, mode="same")


def mirror(x, ctr, dmax):
    a = x[ctr - dmax:ctr][::-1]; b = x[ctr:ctr + dmax]
    return float(np.corrcoef(a, b)[0, 1])


out = {"N": N, "center": c}
for key in ("F2", "F1", "peak"):
    x = smooth(np.array([s[key] for s in syl], float))
    dmax = 120
    real = mirror(x, c, dmax)
    others = [mirror(x, k, dmax) for k in range(dmax, N - dmax) if abs(k - c) > 20]
    pct = float(np.mean(np.array(others) >= real))
    # word-shuffle null: same words in random order, center kept at the same syllable
    rng = np.random.default_rng(1); sh = []
    wl = [[s[key] for s in syl[word_start[j][0]:(word_start[j + 1][0] if j + 1 < len(word_start) else N)]]
          for j in range(len(word_start))]
    for _ in range(5000):
        perm = rng.permutation(len(wl)); seq = np.array([v for j in perm for v in wl[j]], float)
        sh.append(mirror(smooth(seq), c, dmax))
    p_sh = float(np.mean(np.array(sh) >= real))
    out[key] = dict(r=round(real, 3), other_centers_at_least_as_mirrored=round(pct, 3), n_other_centers=len(others),
                    shuffle_p=round(p_sh, 4))
    print(f"{key:5s} mirror r at 1:12b = {real:+.3f}; other centers >= : {pct:.0%} of {len(others)}; word-shuffle p = {p_sh:.3f}")

# ups and downs: brightness by verse (the wave the ear follows)
byv = collections.defaultdict(list)
for s in syl: byv[s["v"]].append(s)
wave = [(v, round(float(np.mean([s["F2"] for s in ss])), 0), round(float(np.mean([s["nuc"] == "o" for s in ss])), 2),
         round(float(np.mean([s["peak"] for s in ss])), 2), len(ss)) for v, ss in sorted(byv.items())]
print("\nverse  meanF2  o-share  accent-density  syllables")
for w in wave: print(f"  1:{w[0]:<3d} {w[1]:6.0f}  {w[2]:.2f}     {w[3]:.2f}          {w[4]}")
out["wave"] = wave

# loops: content lemmas used >= 2 times, their first/last spoken positions, and how
# symmetric their outermost pair is around the center
STOP = {"ὁ", "καί", "δέ", "ἐν", "αὐτός", "οὗτος", "εἰμί", "ὅς", "ἵνα", "ὅτι", "οὐ", "πρός", "διά", "εἰς", "ἐκ",
        "οὐδέ", "μή", "γίνομαι", "ἐγώ", "ὅσος", "ἀλλά", "πᾶς", "εἷς", "ἀπό", "ἀντί", "οὐδείς", "κατά", "τις", "ἐκεῖνος",
        "λέγω", "ἔρχομαι", "λαμβάνω", "ὤν", "γάρ", "ἡμεῖς", "σύ", "ἄνθρωπος", "παρά", "περί", "ἔμπροσθεν"}
pos = collections.defaultdict(list)
for i, v, w, l in word_start: pos[l].append((i, v))
loops = []
for l, ps in pos.items():
    if len(ps) >= 2 and l not in STOP:
        a, b = ps[0][0], ps[-1][0]
        da, db = c - a, b - c
        sym = (min(abs(da), abs(db)) / max(abs(da), abs(db))) if (da > 0 and db > 0) else 0.0
        loops.append(dict(lemma=l, count=len(ps), first=f"1:{ps[0][1]}", last=f"1:{ps[-1][1]}",
                          first_pos=round(a / N, 3), last_pos=round(b / N, 3), around_center_symmetry=round(sym, 2)))
loops.sort(key=lambda d: -d["around_center_symmetry"])
# baseline: for every repeated word (any word, including function words), how symmetric is
# ANY pair of its uses around the center?  Share of pairs reaching >= 0.95
allpairs = []
for l, ps in pos.items():
    for x1 in range(len(ps)):
        for x2 in range(x1 + 1, len(ps)):
            da, db = c - ps[x1][0], ps[x2][0] - c
            if da > 0 and db > 0: allpairs.append(min(da, db) / max(da, db))
base = float(np.mean(np.array(allpairs) >= 0.95))
print(f"baseline: {base:.1%} of all {len(allpairs)} straddling word pairs are >= 0.95 symmetric around the center")
out["loop_baseline_share_ge_0.95"] = round(base, 3)
print("\nloops (repeated content words) sorted by symmetry of first/last use around the center:")
for d in loops: print("  ", d)
out["loops"] = loops
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound_symmetry_results.json"), "w"),
          ensure_ascii=False, indent=1)
