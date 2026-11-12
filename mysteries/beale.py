#!/usr/bin/env python3
"""Beale ciphers: validate the pipeline on cipher 2 (Declaration of Independence key), reproduce Gillogly's alphabet
runs in cipher 1, and test every KJV chapter start as a key for ciphers 1 and 3, scored by English quadgram
likelihood against a wrong-key null. Data: beale.json (ciphertexts from the 1885 pamphlet via Wikisource, public
domain; Declaration text from Wikisource). Usage: python3 beale.py beale.json <dir containing KJV.csv>"""
import json, math, re, csv, random, collections, sys
D = json.load(open(sys.argv[1])); B2, B1, B3 = D["ciphers"]; DOI = D["doi"]
V = sys.argv[2]
kjv = [(r["Book"], int(r["Chapter"]), r["Text"]) for r in csv.DictReader(open(V + "/KJV.csv", encoding="utf-8"))]
# English quadgram model from the KJV (period-appropriate English)
txt = re.sub(r"[^a-z]", "", " ".join(r[2] for r in kjv).lower()); Q = collections.Counter(txt[i:i + 4] for i in range(len(txt) - 3)); TOT = sum(Q.values())
floor = math.log10(0.01 / TOT)
def score(s):
    s = re.sub(r"[^a-z]", "", s); n = len(s) - 3
    return sum(math.log10(Q[s[i:i + 4]] / TOT) if Q[s[i:i + 4]] else floor for i in range(n)) / max(1, n)
def decode(c, words): return "".join(words[n - 1][0].lower() if 0 < n <= len(words) else "" for n in c)
out = {}
out["B2_with_DoI"] = score(decode(B2, DOI))
R = random.Random(1)
def randkey(n): return [R.choice("abcdefghijklmnopqrstuvwxyz") * 1 for _ in range(n)]
# null: B2 decoded with English word lists that are NOT its key (random KJV slices)
words_all = re.findall(r"[A-Za-z]+", " ".join(r[2] for r in kjv))
null = [score(decode(B2, words_all[s:s + 1400])) for s in (R.randrange(0, len(words_all) - 1400) for _ in range(300))]
out["B2_with_random_KJV_slices_mean"] = sum(null) / len(null); out["B2_null_max"] = max(null)
out["B1_with_DoI"] = score(decode(B1, DOI)); out["B3_with_DoI"] = score(decode(B3, DOI))
# Gillogly: alphabetical runs in B1 decoded with the DoI
d1 = decode(B1, DOI); best = []
i = 0
while i < len(d1):
    j = i
    while j + 1 < len(d1) and ord(d1[j + 1]) - ord(d1[j]) in (0, 1): j += 1
    if j - i + 1 >= 8: best.append((i, d1[i:j + 1]))
    i = j + 1
out["B1_DoI_alphabet_runs_8plus"] = best
# expected number of such runs in random letters with the same frequencies
def runs(s, L=8):
    k = i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and ord(s[j + 1]) - ord(s[j]) in (0, 1): j += 1
        k += j - i + 1 >= L; i = j + 1
    return k
sim = [runs("".join(R.sample(d1, len(d1)))) for _ in range(2000)]
out["alphabet_runs_in_shuffled_B1_mean"] = sum(sim) / len(sim); out["shuffled_with_any_run_share"] = sum(x > 0 for x in sim) / len(sim)
# candidate keys: the KJV starting at every chapter
starts = []; wi = 0; last = None
for b, ch, tx in kjv:
    if (b, ch) != last: starts.append((f"{b} {ch}", wi)); last = (b, ch)
    wi += len(re.findall(r"[A-Za-z]+", tx))
res = {}
for label, c in (("B1", B1), ("B3", B3)):
    need = max(c); sc = [(score(decode(c, words_all[w:w + need])), name) for name, w in starts if w + need <= len(words_all)]
    sc.sort(reverse=True); res[label] = dict(tested=len(sc), best=sc[:5], median=sc[len(sc) // 2][0])
out["KJV_chapter_keys"] = res
json.dump(out, open("beale_results.json", "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str)[:3500])
