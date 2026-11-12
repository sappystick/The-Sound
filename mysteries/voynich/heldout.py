#!/usr/bin/env python3
"""Held-out test of the explanations still standing after round 78. Every model is fitted on the EVEN pages and generates
text with the exact shape of the ODD pages (same sections, same lines, same words per line). Each output is scored against
the real odd pages on all the measures of rounds 75-78.
  B0 baseline         words drawn independently from each section's word frequencies
  B1 self-citation    (after Timm & Schinner 2020) each word is, with fitted probabilities, a copy of a recent word, a
                      one-letter variant of a recent word (taken from the vocabulary), or a fresh draw; line-first and
                      line-last words come from the section's line-initial / line-final distributions
  B2 verbose cipher   real Latin herbal prose and verse (Macer + Circa) cut into 2-letter chunks, each chunk type mapped
                      by frequency rank to a Voynich word type (fitted on the even pages), wrapped into the odd pages' lines
Measures: name rate, repetition and its ratio to frequency expectation, near-repeats against shuffle, line-position MI,
page-specific tokens, words per line, and whether the section can be predicted from the words (vocabulary follows pictures).
Usage: python3 heldout.py <IT2a-n.txt> <macer html> <circa ocr>"""
import collections, html, json, math, os, re, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from textmeasures import measures
VP, MP, CP = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); R = random.Random(82); rng = np.random.default_rng(82)
pages, cur = [], None
for l in open(VP, encoding="utf-8", errors="replace"):
    m = re.match(r"<(f\w+)>\s+<!(.*)>", l)
    if m: cur = dict(page=m.group(1), sec=dict(re.findall(r"\$(\w)=(\w+)", m.group(2))).get("I", "?"), lines=[]); pages.append(cur); continue
    m = re.match(r"<(f\w+)\.(\d+),(.)(\w)(\w*)>\s+(.*)", l)
    if not m or cur is None or m.group(4) != "P": continue
    tx = re.sub(r"<[^>]*>", "", m.group(6)); tx = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", tx); tx = re.sub(r"\{[^}]*\}", "", tx)
    ws = [w for w in re.split(r"[.,]", tx.replace("!", "").replace("%", "")) if re.fullmatch(r"[a-z]+", w)]
    if ws: cur["lines"].append(ws)
pages = [p for p in pages if sum(len(x) for x in p["lines"]) >= 20]
train, test = pages[0::2], pages[1::2]
def toks(P): return [w for p in P for ln in p["lines"] for w in ln]
# ---- fit
sec_uni, sec_first, sec_last = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
for p in train:
    for ln in p["lines"]:
        sec_uni[p["sec"]].update(ln); sec_first[p["sec"]][ln[0]] += 1; sec_last[p["sec"]][ln[-1]] += 1
vocab = collections.Counter(toks(train)); V = list(vocab)
by_shape = collections.defaultdict(list)
for w in V:
    for i in range(len(w)): by_shape[w[:i] + "_" + w[i + 1:]].append(w)
def neighbours(w): return [x for i in range(len(w)) for x in by_shape[w[:i] + "_" + w[i + 1:]] if x != w]
def draw(c): ks, vs = zip(*c.items()); return R.choices(ks, vs)[0]
copy = edit = n = 0
for p in train:
    seq = [w for ln in p["lines"] for w in ln]
    for i, w in enumerate(seq):
        if i < 3: continue
        prev = seq[max(0, i - 10):i]; n += 1
        if w in prev: copy += 1
        elif any(w in neighbours(x) for x in prev[-3:]): edit += 1
pc, pe = copy / n, edit / n
def gen_B0(p): return [[draw(sec_uni[p["sec"]]) for _ in ln] for ln in p["lines"]]
def gen_B1(p):
    out, hist = [], []
    for ln in p["lines"]:
        new = []
        for k in range(len(ln)):
            if k == 0: w = draw(sec_first[p["sec"]])
            elif k == len(ln) - 1: w = draw(sec_last[p["sec"]])
            else:
                r = R.random()
                if r < pc and hist: w = R.choice(hist[-10:])
                elif r < pc + pe and hist and neighbours(hist[-1]): w = R.choice(neighbours(hist[-1]))
                else: w = draw(sec_uni[p["sec"]])
            new.append(w); hist.append(w)
        out.append(new)
    return out
# B2: Latin plaintext chunks -> Voynich words by frequency rank
t = open(MP, encoding="utf-8").read(); body = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)))
latin = re.findall(r"[a-z]+", body.lower()) + re.findall(r"[a-z]+", open(CP, encoding="utf-8", errors="replace").read().lower()[1500000:2600000])
chunks = [w[i:i + 2] for w in latin for i in range(0, len(w), 2)]
crank = [c for c, _ in collections.Counter(chunks).most_common()]; vrank = [w for w, _ in vocab.most_common()]
cmap = {c: vrank[i % len(vrank)] for i, c in enumerate(crank)}
pos = [R.randrange(len(chunks) - 5000)]
def gen_B2(p):
    i = R.randrange(len(chunks) - 2000); out = []
    for ln in p["lines"]:
        out.append([cmap[chunks[i + k]] for k in range(len(ln))]); i += len(ln)
    return out
# ---- measures
def rep_ratio(P):
    seqs = [[w for ln in p["lines"] for w in ln] for p in P]; ws = [w for s in seqs for w in s]; c = collections.Counter(ws); N = len(ws)
    obs = sum(1 for s in seqs for a, b in zip(s, s[1:]) if a == b) / sum(len(s) - 1 for s in seqs); return obs / sum((v / N) ** 2 for v in c.values())
def near_ratio(P):
    seqs = [[w for ln in p["lines"] for w in ln] for p in P]
    def nr(S): return sum(1 for s in S for a, b in zip(s, s[1:]) if a != b and len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1)
    flat = [w for s in seqs for w in s]; nulls = []
    for _ in range(10):
        f = list(rng.permutation(flat)); S, k = [], 0
        for s in seqs: S.append(f[k:k + len(s)]); k += len(s)
        nulls.append(nr(S))
    return nr(seqs) / max(1, np.mean(nulls))
def section_signal(P):
    labs = [p["sec"] for p in P]; vv = collections.Counter(w for p in P for ln in p["lines"] for w in set(ln)); W = [w for w, c in vv.items() if c >= 3]; wi = {w: i for i, w in enumerate(W)}
    X = np.zeros((len(P), len(W)))
    for r, p in enumerate(P):
        for ln in p["lines"]:
            for w in ln:
                if w in wi: X[r, wi[w]] += 1
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    def acc(L):
        ok = 0
        for i in range(len(P)):
            cents = {s: X[[j for j in range(len(P)) if L[j] == s and j != i]].mean(0) for s in set(L) if sum(1 for j in range(len(P)) if L[j] == s and j != i)}
            ok += max(cents, key=lambda s: X[i] @ cents[s]) == L[i]
        return ok / len(P)
    a = acc(labs); b = np.mean([acc(list(rng.permutation(labs))) for _ in range(10)]); return a - b
def score(P):
    m = measures([p["lines"] for p in P])
    return dict(name_rate=m["M3_entries_with_own_keyword"], repetition=m["M5_immediate_repetition_rate"], repetition_ratio=round(rep_ratio(P), 2), near_repeat_ratio=round(near_ratio(P), 2),
                line_MI=m["M4_line_position_excess_MI"], page_specific=m["M2_share_of_tokens_entry_specific"], words_per_line=m["M1_words_per_line"], section_signal=round(section_signal(P), 3))
# B1-tuned: shrink the copy/edit probabilities until the TRAINING half's repetition and near-repeat ratios are matched
# (tuned only on even pages, then scored on the odd pages)
def quick(P): return (rep_ratio(P), near_ratio(P))
tr_rep, tr_near = quick(train); best = None; pc0, pe0 = pc, pe
for fc in (0.1, 0.2, 0.35, 0.5, 0.75, 1.0):
    for fe in (0.1, 0.25, 0.5, 1.0):
        pc, pe = pc0 * fc, pe0 * fe; R.seed(7)
        r, nn = quick([dict(page=p["page"], sec=p["sec"], lines=gen_B1(p)) for p in train])
        d = ((r - tr_rep) / 0.5) ** 2 + ((nn - tr_near) / 0.3) ** 2
        if best is None or d < best[0]: best = (d, fc, fe)
TUNED = (pc0 * best[1], pe0 * best[2]); pc, pe = pc0, pe0
def gen_B1t(p):
    global pc, pe
    pc, pe = TUNED; out = gen_B1(p); pc, pe = pc0, pe0; return out
res = {"REAL odd pages": score(test)}
for name, g in (("B0 baseline", gen_B0), ("B1 self-citation", gen_B1), ("B1t self-cit. tuned", gen_B1t), ("B2 verbose cipher", gen_B2)):
    res[name] = score([dict(page=p["page"], sec=p["sec"], lines=g(p)) for p in test])
real = res["REAL odd pages"]; SCALE = dict(name_rate=0.1, repetition=0.003, repetition_ratio=0.5, near_repeat_ratio=0.3, line_MI=0.05, page_specific=0.1, words_per_line=1, section_signal=0.1)
for k, r in res.items(): r["distance"] = round(math.sqrt(sum(((r[m] - real[m]) / s) ** 2 for m, s in SCALE.items())), 2)
res["fitted"] = dict(copy_prob=round(pc, 3), edit_prob=round(pe, 3), tuned_copy=round(TUNED[0], 4), tuned_edit=round(TUNED[1], 4), train_pages=len(train), test_pages=len(test))
json.dump(res, open(os.path.join(HERE, "heldout_results.json"), "w"), indent=1)
cols = list(SCALE) + ["distance"]
print(f"{'':20s}" + "".join(f"{c[:11]:>12s}" for c in cols))
for k, r in res.items():
    if k != "fitted": print(f"{k:20s}" + "".join(f"{r[c]:12.4f}" if isinstance(r[c], float) else f"{r[c]:>12}" for c in cols))
print("fitted:", res["fitted"])
