#!/usr/bin/env python3
"""The Voynich's back-to-back repeated words, examined one by one, and its labels that point elsewhere or nowhere.
R1 which words repeat, how long they are, where they sit (section, line position), compared with all words
R2 is there a hidden number sequence? spacing between successive repeats (vs random positions), lengths of the
   repeated words in order (autocorrelation, periodicity, entropy vs shuffles), near-repeats (one letter apart)
R3 do repeats straddle line breaks, or sit at line starts/ends?
L1 labels: where do labels that are NOT in their own page's text occur? If pharmaceutical labels turn up on HERBAL
   pages more than the herbal share of the text predicts, the labels are cross-references (jar -> plant entry).
L2 labels that occur nowhere in the text: listed and characterised.
Usage: python3 repeats.py <IT2a-n.txt>"""
import collections, json, math, os, re, sys
import numpy as np
VP = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(80)
SEC = {"H": "herbal", "A": "astronomical", "Z": "zodiac", "B": "biological", "C": "cosmological", "P": "pharmaceutical", "S": "stars/recipes", "T": "text only"}
toks, labels, pages_text, cur, sec = [], [], collections.defaultdict(list), None, None
for l in open(VP, encoding="utf-8", errors="replace"):
    m = re.match(r"<(f\w+)>\s+<!(.*)>", l)
    if m: cur = m.group(1); sec = dict(re.findall(r"\$(\w)=(\w+)", m.group(2))).get("I", "?"); continue
    m = re.match(r"<(f\w+)\.(\d+),(.)(\w)(\w*)>\s+(.*)", l)
    if not m or cur is None: continue
    tx = re.sub(r"<[^>]*>", "", m.group(6)); tx = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", tx); tx = re.sub(r"\{[^}]*\}", "", tx)
    ws = [w for w in re.split(r"[.,]", tx.replace("!", "").replace("%", "")) if re.fullmatch(r"[a-z]+", w)]
    if m.group(4) == "P":
        for k, w in enumerate(ws): toks.append(dict(w=w, page=cur, sec=sec, line=f"{cur}.{m.group(2)}", pos=k, n=len(ws)))
        pages_text[cur] += ws
    elif m.group(4) == "L":
        for w in ws: labels.append(dict(w=w, page=cur, sec=sec))
W = [t["w"] for t in toks]; N = len(W); cnt = collections.Counter(W); out = {}
# R1
rep = [i for i in range(1, N) if W[i] == W[i - 1]]
same_line = [i for i in rep if toks[i]["line"] == toks[i - 1]["line"]]; across = [i for i in rep if toks[i]["line"] != toks[i - 1]["line"]]
exp = sum((c / N) ** 2 for c in cnt.values())
rc = collections.Counter(W[i] for i in rep)
lens_rep = [len(W[i]) for i in rep]; lens_all = [len(w) for w in W]
by_sec = {}
for s in SEC:
    idx = [i for i in range(1, N) if toks[i]["sec"] == s and toks[i - 1]["sec"] == s]
    if len(idx) < 200: continue
    sw = [W[i] for i in idx]; c = collections.Counter(sw); e = sum((v / len(sw)) ** 2 for v in c.values()); o = sum(1 for i in idx if W[i] == W[i - 1]) / len(idx)
    by_sec[SEC[s]] = dict(rate=round(o, 4), expected=round(e, 4), ratio=round(o / e, 2))
out["R1"] = dict(tokens=N, repeats=len(rep), rate=round(len(rep) / N, 4), expected_from_word_frequencies=round(exp, 4), ratio=round(len(rep) / N / exp, 2),
                 within_line=len(same_line), across_line_break=len(across), most_repeated=rc.most_common(15), by_section=by_sec,
                 mean_length_repeated=round(float(np.mean(lens_rep)), 2), mean_length_all=round(float(np.mean(lens_all)), 2),
                 share_of_repeats_that_are_top20_words=round(sum(1 for i in rep if W[i] in dict(cnt.most_common(20))) / len(rep), 3))
# R2 hidden sequence tests
gaps = np.diff(rep)
null_gaps_cv = []
for _ in range(2000):
    r = np.sort(rng.choice(np.arange(1, N), len(rep), replace=False)); g = np.diff(r); null_gaps_cv.append(g.std() / g.mean())
cv = gaps.std() / gaps.mean()
seq = np.array(lens_rep, float)
def ac1(x): x = x - x.mean(); return float((x[:-1] * x[1:]).sum() / ((x * x).sum() + 1e-12))
null_ac = [ac1(rng.permutation(seq)) for _ in range(5000)]
def maxpeak(x):
    x = x - x.mean(); p = np.abs(np.fft.rfft(x)) ** 2; return float(p[1:].max() / p[1:].mean())
null_pk = [maxpeak(rng.permutation(seq)) for _ in range(2000)]
near = sum(1 for i in range(1, N) if W[i] != W[i - 1] and len(W[i]) == len(W[i - 1]) and sum(a != b for a, b in zip(W[i], W[i - 1])) == 1)
near_null = []
for _ in range(20):
    P = list(rng.permutation(W)); near_null.append(sum(1 for i in range(1, N) if P[i] != P[i - 1] and len(P[i]) == len(P[i - 1]) and sum(a != b for a, b in zip(P[i], P[i - 1])) == 1))
out["R2"] = dict(gap_cv=round(float(cv), 3), gap_cv_random_positions=round(float(np.mean(null_gaps_cv)), 3), p_gaps_more_clustered=round(float(np.mean(np.array(null_gaps_cv) >= cv)), 4),
                 lengths_sequence_first_40=lens_rep[:40], lag1_autocorrelation=round(ac1(seq), 3), p_autocorr=round(float(np.mean(np.abs(null_ac) >= abs(ac1(seq)))), 4),
                 strongest_periodicity_peak=round(maxpeak(seq), 2), p_periodicity=round(float(np.mean(np.array(null_pk) >= maxpeak(seq))), 4),
                 near_repeats_one_letter_apart=near, near_repeats_if_words_shuffled=round(float(np.mean(near_null)), 1))
# R3 positions
pos = collections.Counter("first" if toks[i]["pos"] == 0 else ("last" if toks[i]["pos"] == toks[i]["n"] - 1 else "middle") for i in same_line)
pos_all = collections.Counter("first" if t["pos"] == 0 else ("last" if t["pos"] == t["n"] - 1 else "middle") for t in toks)
out["R3"] = dict(second_copy_position=dict(pos), all_words_position={k: round(v / N, 3) for k, v in pos_all.items()},
                 second_copy_share={k: round(v / len(same_line), 3) for k, v in pos.items()})
# L1 / L2 labels
text_page_of = collections.defaultdict(set)
for p, ws in pages_text.items():
    for w in set(ws): text_page_of[w].add(p)
page_sec = {t["page"]: t["sec"] for t in toks}; sec_share = collections.Counter(page_sec[p] for p in pages_text for _ in pages_text[p])
tot = sum(sec_share.values())
el = [lb for lb in labels if lb["w"] not in set(pages_text.get(lb["page"], []))]
where = collections.Counter(); weight = collections.Counter()
for lb in el:
    ps = text_page_of.get(lb["w"], set())
    for p in ps: where[(lb["sec"], page_sec[p])] += 1 / len(ps)
lab_rows = {}
for s in sorted({lb["sec"] for lb in labels}):
    tot_s = sum(v for (a, b), v in where.items() if a == s)
    if tot_s < 5: continue
    lab_rows[SEC.get(s, s)] = {SEC.get(b, b): dict(observed=round(v / tot_s, 3), text_share=round(sec_share[b] / tot, 3), ratio=round((v / tot_s) / (sec_share[b] / tot), 2))
                               for (a, b), v in where.items() if a == s and v / tot_s >= 0.03}
nowhere = [lb for lb in labels if lb["w"] not in text_page_of]
first = collections.Counter(lb["w"][0] for lb in nowhere); first_all = collections.Counter(w[0] for w in W)
out["L"] = dict(labels=len(labels), not_in_own_page=len(el), in_text_nowhere=len(nowhere), nowhere_by_section=dict(collections.Counter(SEC.get(lb["sec"], lb["sec"]) for lb in nowhere)),
                cross_reference_targets=lab_rows, nowhere_initial_letters=first.most_common(6), text_initial_letters=[(k, round(v / N, 3)) for k, v in first_all.most_common(6)],
                nowhere_examples=[f"{lb['page']}:{lb['w']}" for lb in nowhere[:25]], nowhere_mean_length=round(float(np.mean([len(lb["w"]) for lb in nowhere])), 2))
json.dump(out, open(os.path.join(HERE, "repeats_results.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:6000])
