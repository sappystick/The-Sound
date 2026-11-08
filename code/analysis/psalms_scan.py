#!/usr/bin/env python3
"""All 150 Psalms, Hebrew (Westminster Leningrad Codex): are they built around a central verse,
counted in WORDS or in SYLLABLES?

Rule (fixed before running): for each psalm and each inner verse k, take that verse as the central line
(the Psalm 92 type) and measure |material before - material after| / total.  The best such verse gives
the psalm's centring exactness r.  Null: the same verses in shuffled order (1,000 shuffles per psalm), which
keeps verse lengths but destroys design.  A psalm counts as 'centred beyond chance' when its real r is
smaller than 95% of shuffles.  Run separately for words and for syllables, with and without verse 1 when
verse 1 opens with a heading word.
Usage: python3 psalms_scan.py <morphhb/wlc dir>
"""
import collections, json, os, random, re, sys, unicodedata
from scipy.stats import binomtest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
xml = open(os.path.join(sys.argv[1], "Ps.xml"), encoding="utf-8").read()
HEAD = ("למנצח", "מזמור", "לדוד", "שיר", "משכיל", "מכתם", "תפלה", "לשלמה", "לאסף", "לבני", "שגיון", "הללויה", "לידותון", "לעבד", "למשה", "להימן", "לאיתן")
def cons(w): return "".join(c for c in unicodedata.normalize("NFD", w) if "א" <= c <= "ת")
cache = {}
def hsyl(w):
    if w not in cache:
        try: cache[w] = max(1, sum(len(x) for x in E.parse_hebrew(w, "second-temple")))
        except Exception: cache[w] = max(1, len(re.findall("[ְ-ׇֻ]", w)))
    return cache[w]
ps = collections.defaultdict(list)
for m in re.finditer(r'<verse osisID="Ps\.(\d+)\.(\d+)">(.*?)</verse>', xml, re.S):
    ws = [w.replace("/", "") for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(3))]
    ps[int(m.group(1))].append((int(m.group(2)), ws))
def best(lengths):
    T = sum(lengths); bestr, bk = 9, None; acc = 0
    for k in range(1, len(lengths) - 1):
        r = abs(acc - (T - acc - lengths[k])) / T
        if r < bestr: bestr, bk = r, k
        acc += lengths[k - 0] if False else 0
        acc = sum(lengths[:k + 1]) if False else acc
    # straightforward recomputation
    bestr, bk = 9, None
    for k in range(1, len(lengths) - 1):
        before = sum(lengths[:k]); after = T - before - lengths[k]; r = abs(before - after) / T
        if r < bestr: bestr, bk = r, k
    return bestr, bk
rng = random.Random(150); R = 1000
results = {}
for variant in ("full", "no_heading"):
    for unit in ("words", "syllables"):
        sig, rows = 0, []
        for n in range(1, 151):
            vv = ps[n]
            if variant == "no_heading" and vv and cons(vv[0][1][0]) in HEAD: vv = vv[1:]
            if len(vv) < 5: continue
            L = [len(ws) if unit == "words" else sum(hsyl(w) for w in ws) for _, ws in vv]
            r, k = best(L); cnt = 0
            for _ in range(R):
                s = L[:]; rng.shuffle(s); cnt += best(s)[0] <= r
            p = cnt / R; sig += p < 0.05
            rows.append(dict(psalm=n, verses=len(L), central_verse=vv[k][0], exactness=round(r, 4), p=p,
                             diff=round(r * sum(L), 1), total=sum(L)))
        bt = binomtest(sig, len(rows), 0.05, alternative="greater")
        results[f"{variant}_{unit}"] = dict(n=len(rows), significant=sig, expected=round(0.05 * len(rows), 1), p=bt.pvalue, rows=rows)
        print(f"{variant:10s} {unit:9s}: {sig} of {len(rows)} psalms centred beyond chance (expected {0.05 * len(rows):.1f}); binomial p = {bt.pvalue:.4f}")
# psalms centred in both units, full text
w = {r["psalm"]: r for r in results["full_words"]["rows"]}; s = {r["psalm"]: r for r in results["full_syllables"]["rows"]}
both = [n for n in w if w[n]["p"] < .05 and n in s and s[n]["p"] < .05]
print("\ncentred beyond chance by words (full text), strongest first:")
for r in sorted([r for r in results["full_words"]["rows"] if r["p"] < .05], key=lambda r: r["p"])[:25]:
    print(f"   Ps {r['psalm']:3d} central verse {r['central_verse']:2d} of {r['verses']:2d}  words before/after differ by {r['diff']:.0f} of {r['total']}  p={r['p']:.3f}"
          + ("  [also by syllables]" if r["psalm"] in both else ""))
print("psalms centred by both words and syllables:", both)
json.dump(results, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "psalms_scan_results.json"), "w"), indent=1)
