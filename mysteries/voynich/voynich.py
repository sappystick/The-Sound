#!/usr/bin/env python3
"""Voynich manuscript: two structure tests with this project's methods and controls.
Data: the IVTFF interlinear transliteration (Zandbergen, voynich.nu, IT2a-n.txt), not redistributed here.
V1 DO THE WORDS FOLLOW THE PICTURES?  Each page is labelled with its illustration type ($I: herbal, astronomical, zodiac,
   biological, cosmological, pharmaceutical, stars/recipes, text-only), its Currier language ($L) and its scribe's hand ($H).
   Inside every group of pages sharing the SAME hand and language, can a page's illustration type be predicted from its
   words alone (leave-one-out, nearest centroid on TF-IDF)? Null: illustration labels shuffled inside the group.
   Meaningful text about plants vs stars should pass; a generator whose output depends only on the scribe should fail.
V2 ARE LINES UNITS?  How much does a word's identity depend on its position in the line (first / middle / last)?
   Measured as excess mutual information over a within-text shuffle. Controls: Greek John re-flowed into lines of the same
   lengths (natural language, arbitrary line breaks); KJV with one verse per line (meaningful units).
Usage: python3 voynich.py <IT2a-n.txt> <sblgnt dir> <KJV.csv>"""
import collections, csv, glob, json, math, os, re, sys, unicodedata
import numpy as np
P, SBL, KJV = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(76)
pages, lines, cur = collections.OrderedDict(), [], None
for l in open(P, encoding="utf-8", errors="replace"):
    m = re.match(r"<(f\w+)>\s+<!(.*)>", l)
    if m: cur = m.group(1); meta = dict(re.findall(r"\$(\w)=(\w+)", m.group(2))); pages[cur] = dict(meta=meta, words=[]); continue
    m = re.match(r"<(f\w+)\.(\d+),(.)(\w)(\w*)>\s+(.*)", l)
    if not m or cur is None: continue
    txt = m.group(6); txt = re.sub(r"<[^>]*>", "", txt); txt = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", txt); txt = re.sub(r"\{[^}]*\}", "", txt)
    ws = [w for w in re.split(r"[.,]", txt.replace("!", "").replace("%", "")) if re.fullmatch(r"[a-z]+", w)]
    pages[cur]["words"] += ws
    if m.group(4) == "P" and len(ws) >= 3: lines.append(ws)
R = {}
# ---------------- V1
use = {k: v for k, v in pages.items() if len(v["words"]) >= 40 and all(x in v["meta"] for x in "ILH")}
vocab = collections.Counter(w for v in use.values() for w in set(v["words"])); V = [w for w, c in vocab.items() if c >= 3]; vi = {w: i for i, w in enumerate(V)}
N = len(use); idf = np.log(N / np.array([vocab[w] for w in V]))
X = np.zeros((N, len(V)))
for r, v in enumerate(use.values()):
    for w in v["words"]:
        if w in vi: X[r, vi[w]] += 1
X = X * idf; X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
meta = [v["meta"] for v in use.values()]
GAP = 0      # pages within +-GAP of the test page (in manuscript order) are left out of training
def loo_acc(idx, labels):
    ok = 0
    for j, i in enumerate(idx):
        cents = {}
        for lab in set(labels):
            mem = [ii for jj, ii in enumerate(idx) if labels[jj] == lab and abs(ii - i) > GAP]
            if mem: c = X[mem].mean(0); cents[lab] = c / (np.linalg.norm(c) + 1e-12)
        pred = max(cents, key=lambda lab: X[i] @ cents[lab]); ok += pred == labels[j]
    return ok / len(idx)
groups = collections.defaultdict(list)
for r, m in enumerate(meta): groups[(m["L"], m["H"])].append(r)
v1 = []; pooled_obs = pooled_n = 0; pooled_null = np.zeros(1000)
for g, idx in groups.items():
    labs = [meta[i]["I"] for i in idx]; cnt = collections.Counter(labs); keep = [i for i in idx if cnt[meta[i]["I"]] >= 3]
    if len(set(meta[i]["I"] for i in keep)) < 2: continue
    labs = [meta[i]["I"] for i in keep]; obs = loo_acc(keep, labs)
    null = np.array([loo_acc(keep, list(rng.permutation(labs))) for _ in range(1000)])
    v1.append(dict(language=g[0], hand=g[1], pages=len(keep), types=dict(collections.Counter(labs)), accuracy=round(obs, 3), null_mean=round(float(null.mean()), 3), p=round(float((np.sum(null >= obs) + 1) / 1001), 4)))
    pooled_obs += obs * len(keep); pooled_n += len(keep); pooled_null += null * len(keep)
def pooled(gap):
    global GAP; GAP = gap; o = n_ = 0; nul = np.zeros(300)
    for g, idx in groups.items():
        labs = [meta[i]["I"] for i in idx]; cnt = collections.Counter(labs); keep = [i for i in idx if cnt[meta[i]["I"]] >= 3]
        if len(set(meta[i]["I"] for i in keep)) < 2: continue
        labs = [meta[i]["I"] for i in keep]; o += loo_acc(keep, labs) * len(keep); n_ += len(keep)
        nul += np.array([loo_acc(keep, list(rng.permutation(labs))) for _ in range(300)]) * len(keep)
    GAP = 0; return dict(gap_pages=gap, pooled_accuracy=round(o / n_, 3), null_mean=round(float(nul.mean() / n_), 3), p=round(float((np.sum(nul / n_ >= o / n_) + 1) / 301), 4))
R["V1_robustness_neighbours_excluded"] = [pooled(g) for g in (5, 10)]
R["V1_words_follow_pictures_within_hand_and_language"] = dict(groups=v1, pooled_accuracy=round(pooled_obs / pooled_n, 3), pooled_null_mean=round(float(pooled_null.mean() / pooled_n), 3),
                                                             pooled_p=round(float((np.sum(pooled_null / pooled_n >= pooled_obs / pooled_n) + 1) / 1001), 4))
# ---------------- V2
def excess_mi(lines_, minf=5, shuffles=200):
    def mi(L):
        c = collections.Counter(); wc = collections.Counter(); pc = collections.Counter()
        for ws in L:
            for k, w in enumerate(ws):
                pos = 0 if k == 0 else (2 if k == len(ws) - 1 else 1); c[(w, pos)] += 1; wc[w] += 1; pc[pos] += 1
        keep = {w for w, n in wc.items() if n >= minf}; T = sum(n for (w, p), n in c.items() if w in keep)
        wk = {w: wc[w] for w in keep}; pk = collections.Counter()
        for (w, p), n in c.items():
            if w in keep: pk[p] += n
        H = -sum(n / T * math.log2(n / T) for n in pk.values())
        return sum(n / T * math.log2((n / T) / ((wk[w] / T) * (pk[p] / T))) for (w, p), n in c.items() if w in keep) / H
    obs = mi(lines_); flat = [w for ws in lines_ for w in ws]; lens = [len(ws) for ws in lines_]; nulls = []
    for _ in range(shuffles):
        f = list(rng.permutation(flat)); L, k = [], 0
        for n in lens: L.append(f[k:k + n]); k += n
        nulls.append(mi(L))
    return dict(normalized_MI=round(obs, 4), shuffled_mean=round(float(np.mean(nulls)), 4), excess=round(obs - float(np.mean(nulls)), 4), lines=len(lines_))
def nrm(w): w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in w if not unicodedata.combining(c)).replace("ς", "σ"))
john = [nrm(l.split()[5]) for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8")]
lens = [len(ws) for ws in lines]; jl, k = [], 0
for n in (lens * 3):
    if k + n > len(john): break
    jl.append(john[k:k + n]); k += n
kjv = [re.findall(r"[a-z]+", r["Text"].lower()) for r in csv.DictReader(open(KJV, encoding="utf-8")) if r["Book"] in ("Genesis", "Exodus", "Psalms", "Proverbs")]
R["V2_line_position"] = dict(voynich_paragraph_lines=excess_mi(lines), john_reflowed_same_line_lengths=excess_mi(jl), kjv_one_verse_per_line=excess_mi(kjv))
R["V2_first_and_last_words"] = dict(
    voynich_line_initial_top=collections.Counter(ws[0] for ws in lines).most_common(6), voynich_line_final_top=collections.Counter(ws[-1] for ws in lines).most_common(6))
json.dump(R, open(os.path.join(HERE, "voynich_results.json"), "w"), indent=1, default=str)
v = R["V1_words_follow_pictures_within_hand_and_language"]
for g in v["groups"]: print(f"V1 language {g['language']} hand {g['hand']}: {g['pages']} pages {g['types']} accuracy {g['accuracy']} vs null {g['null_mean']}  p {g['p']}")
print(f"V1 pooled accuracy {v['pooled_accuracy']} vs null {v['pooled_null_mean']}  p {v['pooled_p']}")
for r in R["V1_robustness_neighbours_excluded"]: print("V1 robustness:", r)
for k_, x in R["V2_line_position"].items(): print("V2", k_, x)
print("V2", R["V2_first_and_last_words"])
