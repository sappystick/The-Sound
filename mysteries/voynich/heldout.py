#!/usr/bin/env python3
"""Held-out test (rounds 79-81) of the explanations still standing after round 78. Every model is fitted on the EVEN pages and generates
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
# ---- B3: the short-range generator (round 80). Each word, from the 2nd in a line on, is
#   an immediate copy of the previous word (prob q), or a one-glyph substitution of the previous word using the
#   substitution pairs seen between neighbouring words in the training pages (prob e; it may create a new word),
#   or a fresh draw from the section's distribution for that line position (first / middle / last).
# No copying from further back, and never across a line break.
sec_mid = collections.defaultdict(collections.Counter)
for p in train:
    for ln in p["lines"]: sec_mid[p["sec"]].update(ln[1:-1])
SUB = collections.Counter(); nq = ne = nall = 0
for p in train:
    for ln in p["lines"]:
        for a, b in zip(ln, ln[1:]):
            nall += 1
            if a == b: nq += 1
            elif len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1:
                ne += 1; i = next(i for i in range(len(a)) if a[i] != b[i]); SUB[(a[i], b[i])] += 1
Q_FIT, E_FIT = nq / nall, ne / nall
SUBS = collections.defaultdict(list)
for (x, y), c in SUB.items(): SUBS[x].append((y, c))
def mutate(w):
    opts = [(i, y, c) for i, x in enumerate(w) for y, c in SUBS.get(x, [])]
    if not opts: return None
    i, y, _ = R.choices(opts, [c for _, _, c in opts])[0]; return w[:i] + y + w[i + 1:]
B3P = [Q_FIT, E_FIT]
def gen_B3(p):
    q, e = B3P; out = []
    for ln in p["lines"]:
        new = []
        for k in range(len(ln)):
            src = sec_first if k == 0 else (sec_last if k == len(ln) - 1 else sec_mid)
            w = None
            if k > 0:
                r = R.random()
                if r < q: w = new[-1]
                elif r < q + e: w = mutate(new[-1])
            if w is None: w = draw(src[p["sec"]] or sec_uni[p["sec"]])
            new.append(w)
        out.append(new)
    return out
def cheap(P):   # the measures that do not need shuffles of the line-position MI, for tuning on the training half
    ent = [[w for ln in p["lines"] for w in ln] for p in P]; df = collections.Counter(w for x in ent for w in set(x)); k = len(ent); own = top = 0
    for x in ent:
        c = collections.Counter(x); sc = {w: c[w] * math.log(k / df[w]) for w in c if c[w] >= 2}
        if sc: top += 1; own += df[max(sc, key=sc.get)] <= 3
    spec = float(np.mean([sum(1 for w in x if df[w] <= 2) / len(x) for x in ent]))
    return np.array([own / max(1, top), rep_ratio(P), near_ratio(P), spec])
TR = cheap(train); TS = np.array([0.1, 0.5, 0.3, 0.1]); best = None
for fq in (0.5, 0.75, 1.0, 1.25, 1.5):
    for fe in (0.5, 1.0, 1.5, 2.0, 3.0):
        B3P[:] = [Q_FIT * fq, E_FIT * fe]; R.seed(11)
        d = float(np.sum(((cheap([dict(page=p["page"], sec=p["sec"], lines=gen_B3(p)) for p in train]) - TR) / TS) ** 2))
        if best is None or d < best[0]: best = (d, fq, fe)
B3_TUNED = [Q_FIT * best[1], E_FIT * best[2]]
def gen_B3f(p): B3P[:] = [Q_FIT, E_FIT]; return gen_B3(p)
def gen_B3t(p): B3P[:] = B3_TUNED; return gen_B3(p)
# ---- B4: the word-grammar generator (round 81). Like B3, but a share g of the fresh words is BUILT from slots:
# prefix + root + suffix, learned from the training pages (prefixes: the 12 commonest word-initial strings of 1-2
# glyphs; suffixes: the 16 commonest word-final strings of 1-3 glyphs; root: what is left). Prefix and root are drawn
# from the section's slot distributions, the suffix given the root's last glyph, so new word forms appear on every page.
# The line-position draws are softened: with probability 1 - s a first or last word comes from the middle-word list.
ini = collections.Counter(); fin = collections.Counter()
for w, c in vocab.items():
    for k in (1, 2):
        if len(w) > k: ini[w[:k]] += c
    for k in (1, 2, 3):
        if len(w) > k: fin[w[-k:]] += c
PRE = [a for a, _ in ini.most_common(12)]; SUF = [a for a, _ in fin.most_common(16)]
def split(w):
    p = max((a for a in PRE if w.startswith(a) and len(w) > len(a)), key=len, default="")
    r = w[len(p):]; x = max((a for a in SUF if r.endswith(a) and len(r) > len(a)), key=len, default="")
    return p, r[:len(r) - len(x)] if x else r, x
sP = collections.defaultdict(collections.Counter); sR = collections.defaultdict(collections.Counter); sX = collections.defaultdict(collections.Counter)
for p in train:
    for ln in p["lines"]:
        for w in ln:
            a, r, x = split(w); sP[p["sec"]][a] += 1; sR[p["sec"]][r] += 1; sX[r[-1:] if r else a[-1:]][x] += 1
def build(sec):
    a = draw(sP[sec]); r = draw(sR[sec]); key = r[-1:] if r else a[-1:]
    return a + r + (draw(sX[key]) if sX[key] else "")
B4P = [0.3, 0.7]   # g, s
def gen_B4(p):
    q, e = B3_TUNED; g, soft = B4P; out = []
    for ln in p["lines"]:
        new = []
        for k in range(len(ln)):
            w = None
            if k > 0:
                r = R.random()
                if r < q: w = new[-1]
                elif r < q + e: w = mutate(new[-1])
            if w is None:
                if R.random() < g: w = build(p["sec"])
                else:
                    edge = k == 0 or k == len(ln) - 1
                    src = (sec_first if k == 0 else sec_last) if edge and R.random() < soft else sec_mid
                    w = draw(src[p["sec"]] or sec_uni[p["sec"]])
            new.append(w)
        out.append(new)
    return out
def raw_mi(P):
    c = collections.Counter(); wc = collections.Counter(); pc = collections.Counter()
    for pg in P:
        for ws in pg["lines"]:
            if len(ws) < 3: continue
            for i, w in enumerate(ws):
                q_ = 0 if i == 0 else (2 if i == len(ws) - 1 else 1); c[(w, q_)] += 1; wc[w] += 1
    keep = {w for w, m_ in wc.items() if m_ >= 5}; T = sum(m_ for (w, q_), m_ in c.items() if w in keep); pk = collections.Counter()
    for (w, q_), m_ in c.items():
        if w in keep: pk[q_] += m_
    Hp = -sum(m_ / T * math.log2(m_ / T) for m_ in pk.values())
    return sum(m_ / T * math.log2((m_ / T) / ((wc[w] / T) * (pk[q_] / T))) for (w, q_), m_ in c.items() if w in keep) / Hp
def cheap4(P): return np.append(cheap(P), raw_mi(P))
TR4 = cheap4(train); TS4 = np.array([0.1, 0.5, 0.3, 0.1, 0.05]); best4 = None
for g in (0.0, 0.1, 0.2, 0.35, 0.5, 0.7):
    for soft in (0.4, 0.6, 0.8, 1.0):
        B4P[:] = [g, soft]; R.seed(13)
        d = float(np.sum(((cheap4([dict(page=p["page"], sec=p["sec"], lines=gen_B4(p)) for p in train]) - TR4) / TS4) ** 2))
        if best4 is None or d < best4[0]: best4 = (d, g, soft)
B4P[:] = [best4[1], best4[2]]
res = {"REAL odd pages": score(test)}
for name, g in (("B0 baseline", gen_B0), ("B1 self-citation", gen_B1), ("B1t self-cit. tuned", gen_B1t), ("B2 verbose cipher", gen_B2), ("B3 short-range", gen_B3f), ("B3t short-rng tuned", gen_B3t), ("B4 word grammar", gen_B4)):
    res[name] = score([dict(page=p["page"], sec=p["sec"], lines=g(p)) for p in test])
real = res["REAL odd pages"]; SCALE = dict(name_rate=0.1, repetition=0.003, repetition_ratio=0.5, near_repeat_ratio=0.3, line_MI=0.05, page_specific=0.1, words_per_line=1, section_signal=0.1)
for k, r in res.items(): r["distance"] = round(math.sqrt(sum(((r[m] - real[m]) / s) ** 2 for m, s in SCALE.items())), 2)
res["fitted"] = dict(copy_prob=round(pc, 3), edit_prob=round(pe, 3), tuned_copy=round(TUNED[0], 4), tuned_edit=round(TUNED[1], 4), B3_copy_fit=round(Q_FIT, 4), B3_edit_fit=round(E_FIT, 4), B3_tuned=[round(x, 4) for x in B3_TUNED], B4_grammar_share=best4[1], B4_position_softness=best4[2], B4_prefixes=PRE, B4_suffixes=SUF, train_pages=len(train), test_pages=len(test))
json.dump(res, open(os.path.join(HERE, "heldout_results.json"), "w"), indent=1)
cols = list(SCALE) + ["distance"]
print(f"{'':20s}" + "".join(f"{c[:11]:>12s}" for c in cols))
for k, r in res.items():
    if k != "fitted": print(f"{k:20s}" + "".join(f"{r[c]:12.4f}" if isinstance(r[c], float) else f"{r[c]:>12}" for c in cols))
print("fitted:", res["fitted"])

# Replicates (round 81): one generated text per model is noisy, so the two best models are re-generated with
# REPS different seeds and their distances compared as mean and spread.
REPS = int(os.environ.get("REPS", "0"))
if REPS:
    rep = {}
    for name, g in (("B3t short-rng tuned", gen_B3t), ("B4 word grammar", gen_B4)):
        ds = []; per = collections.defaultdict(list)
        for k in range(REPS):
            R.seed(1000 + k); r = score([dict(page=p["page"], sec=p["sec"], lines=g(p)) for p in test])
            ds.append(math.sqrt(sum(((r[m] - real[m]) / s_) ** 2 for m, s_ in SCALE.items())))
            for m in SCALE: per[m].append(r[m])
        rep[name] = dict(distance_mean=round(float(np.mean(ds)), 2), distance_sd=round(float(np.std(ds)), 2), distances=[round(x, 2) for x in ds],
                         measure_means={m: round(float(np.mean(v)), 4) for m, v in per.items()})
        print(f"{name:20s} distance {np.mean(ds):.2f} ± {np.std(ds):.2f}  ", rep[name]["measure_means"])
    res["replicates"] = rep; json.dump(res, open(os.path.join(HERE, "heldout_results.json"), "w"), indent=1)
