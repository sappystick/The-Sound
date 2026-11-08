#!/usr/bin/env python3
"""Verse-by-verse symmetry inside every chapter, and likeness between chapters.

Units: Greek NT verses measured in syllables and in letters (letters = the unspaced uncial text); Hebrew Bible
verses measured in CONSONANTS only (the unpointed original, vowel points and accents removed).
Per chapter (8+ verses):
  MIRROR-LENGTH : correlation of verse i with verse n+1-i in length (a ring of long and short lines).
  MIRROR-WORDS  : content words (weighted by rarity; the commonest 3% dropped) shared by verse i and verse n+1-i (a chiasm / inclusio), against the same
                  verses in shuffled order.
  CYCLE         : the strongest repeating period (2 = couplets, 3 = triplets...) in verse lengths
                  (autocorrelation), against shuffles.
  Null for each: 500 shuffles of the chapter's own verses. Reported: how many chapters pass p < .05 against
  the 5% expected, and the strongest chapters after Benjamini-Hochberg correction (q < .10).
ACROSS CHAPTERS: each chapter's verse-length curve is resampled to 12 points; pairs of chapters in DIFFERENT
  books whose curves correlate highest are listed (the 'likeness' of shapes), with the chance level.
Positive control: Psalm 8 (a known inclusio) must show MIRROR-WORDS.
Usage: python3 verse_symmetry.py <sblgnt dir> <morphhb/wlc dir>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, WLC = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(11); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
sc = {}
def syl(k):
    if not k: return 0
    if k not in sc:
        try: sc[k] = max(1, len(E.parse_greek(k, "koine")[0]))
        except Exception: sc[k] = 1
    return sc[k]
def cons(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת")
CH = collections.OrderedDict()          # (corpus, book, ch) -> list of (len_syll_or_cons, len_letters, stems)
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]; vs = collections.OrderedDict()
    for l in open(f, encoding="utf-8"):
        p = l.split(); key = (int(p[0][2:4]), int(p[0][4:6])); w = nrm(p[4]); lem = nrm(p[6])
        e = vs.setdefault(key, [0, 0, set()]); e[0] += syl(w); e[1] += len(w)
        if len(lem) > 3: e[2].add(lem[:6])
    for (c, v), e in vs.items(): CH.setdefault(("NT", b, c), []).append(tuple(e))
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    b = os.path.basename(f)[:-4]; x = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)">(.*?)</verse>', x, re.S):
        ws = [w for w in re.findall(r'<w [^>]*lemma="([^"]*)"[^>]*>([^<]+)</w>', m.group(3))]
        letters = sum(len(cons(t)) for _, t in ws); stems = {re.sub(r"[^0-9]", "", lm.split("/")[-1]) for lm, _ in ws if re.sub(r"[^0-9]", "", lm.split("/")[-1])}
        CH.setdefault(("OT", b, int(m.group(1))), []).append((letters, letters, stems))
DF = collections.Counter(s for vs in CH.values() for v in vs for s in v[2]); NV = sum(len(v) for v in CH.values())
def mirror_len(L):
    n = len(L); a, b = L[: n // 2], L[::-1][: n // 2]
    return float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else 0.0
IDF = {w: math.log(NV / c) for w, c in DF.items()}; COMMON = {w for w, c in DF.items() if c > 0.03 * NV}   # drop function words only
def mirror_words(S):
    n = len(S); return sum(sum(IDF[w] for w in (S[i] & S[n - 1 - i]) - COMMON) for i in range(n // 2))
def inclusio(S):   # the frame only: first verse against last verse
    return sum(IDF[w] for w in (S[0] & S[-1]) - COMMON)
def cycle(L):
    x = np.array(L, float) - np.mean(L); d = (x * x).sum() or 1
    ac = [float((x[:-k] * x[k:]).sum() / d) for k in range(2, min(6, len(L) // 2) + 1)]
    k = int(np.argmax(ac)); return ac[k], k + 2
# corpus null for the frame: overlap of random verse pairs from the same corpus
POOL = {c: [v[2] for k, vs in CH.items() if k[0] == c for v in vs] for c in ("NT", "OT")}
FRAME_NULL = {c: np.sort([sum(IDF[w] for w in (POOL[c][a] & POOL[c][b]) - COMMON) for a, b in rng.integers(0, len(POOL[c]), (40000, 2)) if a != b]) for c in POOL}
def frame_p(S, inc, R=2000):
    """frame (best of 3 candidate first/last pairs) against the best of 3 random pairs from the SAME chapter"""
    n = len(S); hits = 0
    for _ in range(R):
        best3 = max(sum(IDF[w] for w in (S[a] & S[b]) - COMMON) for a, b in (rng.choice(n, 2, replace=False) for _ in range(3)))
        hits += best3 >= inc
    return (hits + 1) / (R + 1)
res = {}
for key, vs in CH.items():
    if len(vs) < 8: continue
    L = np.array([v[0] for v in vs], float); S = [v[2] for v in vs]
    def best(f, X): return max(f(X), f(X[1:]), f(X[:-1]))        # axis may shift by one verse (headings, closing lines)
    ml, mw, (cy, per) = best(mirror_len, L), best(mirror_words, S), cycle(L); inc = best(inclusio, S)
    nml = nmw = ncy = ninc = 0; R = 500
    for _ in range(R):
        idx = rng.permutation(len(vs)); Ls = L[idx]; Ss = [S[i] for i in idx]
        nml += best(mirror_len, Ls) >= ml; nmw += best(mirror_words, Ss) >= mw; ncy += cycle(Ls)[0] >= cy; ninc += best(inclusio, Ss) >= inc
    res[key] = dict(n=len(vs), mirror_len=round(ml, 3), p_len=(nml + 1) / (R + 1), mirror_words=mw, p_words=(nmw + 1) / (R + 1), cycle=round(cy, 3), period=per, p_cycle=(ncy + 1) / (R + 1), inclusio=round(inc, 2), p_inclusio=frame_p(S, inc))
def bh(items, field, q=0.10):
    ps = sorted(items, key=lambda kv: kv[1][field]); m = len(ps); keep = []
    for i, (k, v) in enumerate(ps, 1):
        if v[field] <= q * i / m: keep = ps[:i]
    return keep
for corpus in ("NT", "OT"):
    items = [(k, v) for k, v in res.items() if k[0] == corpus]
    print(f"\n{corpus}: {len(items)} chapters ({'syllables' if corpus == 'NT' else 'unpointed consonants'})")
    for field, lab in (("p_len", "MIRROR-LENGTH"), ("p_words", "MIRROR-WORDS"), ("p_cycle", "CYCLE"), ("p_inclusio", "INCLUSIO")):
        k = sum(v[field] < .05 for _, v in items); top = bh(items, field)
        print(f"   {lab:14s} {k} chapters pass p<.05 (expected {0.05 * len(items):.0f}); after correction: {len(top)}: " + ", ".join(f"{a[1]} {a[2]}" for a, _ in top[:15]))
    out[corpus] = {f"{k[1]} {k[2]}": v for k, v in items}
print("\ncontrol Psalm 8:", res[("OT", "Ps", 8)])
print("John's chapters with INCLUSIO p<.05:", [f"Jn {k[2]} (p {v['p_inclusio']:.3f})" for k, v in res.items() if k[1] == "Jn" and v["p_inclusio"] < .05])
print("John's chapters with MIRROR-WORDS p<.05:", [f"Jn {k[2]} (p {v['p_words']:.3f})" for k, v in res.items() if k[1] == "Jn" and v["p_words"] < .05])
print("John's chapters with MIRROR-LENGTH p<.05:", [f"Jn {k[2]} (p {v['p_len']:.3f})" for k, v in res.items() if k[1] == "Jn" and v["p_len"] < .05])
# across chapters
keys = [k for k in res if res[k]["n"] >= 12]
curves = np.array([np.interp(np.linspace(0, 1, 12), np.linspace(0, 1, len(CH[k])), (lambda L: (L - L.mean()) / (L.std() + 1e-9))(np.array([v[0] for v in CH[k]], float))) for k in keys])
C = np.corrcoef(curves); iu = np.triu_indices(len(keys), 1)
pairs = sorted(((C[i, j], i, j) for i, j in zip(*iu) if keys[i][1] != keys[j][1]), reverse=True)[:12]
null = [abs(np.corrcoef(rng.permutation(curves[rng.integers(len(keys))]), curves[rng.integers(len(keys))])[0, 1]) for _ in range(20000)]
print(f"\nACROSS CHAPTERS: {len(keys)} chapters; strongest shape twins (r; chance 99.99th percentile = {np.percentile(null, 99.99):.2f}):")
for r, i, j in pairs: print(f"   {keys[i][1]} {keys[i][2]} ~ {keys[j][1]} {keys[j][2]}  r = {r:.3f}")
jn = [i for i, k in enumerate(keys) if k[1] == "Jn"]
print("John's chapters' nearest shape twins outside John:")
for i in jn[:21]:
    j = max((j for j in range(len(keys)) if keys[j][1] != "Jn"), key=lambda j: C[i, j]); print(f"   Jn {keys[i][2]:2d} ~ {keys[j][1]} {keys[j][2]} (r {C[i, j]:.2f})", end=";")
print()
out["twins"] = [(f"{keys[i][1]} {keys[i][2]}", f"{keys[j][1]} {keys[j][2]}", round(float(r), 3)) for r, i, j in pairs]
json.dump(out, open(os.path.join(HERE, "verse_symmetry_results.json"), "w"), indent=1, default=str)
