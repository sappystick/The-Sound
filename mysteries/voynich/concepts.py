#!/usr/bin/env python3
"""Round 90 - Move (grown): concept-cluster discovery on the content-word layer found in round 89.

Round 89 found a content-word layer: ~specific bursty words that recur in local sub-topic clusters, carrying the
long-range information no generative model reproduces. This round asks the decisive next question: do those content
words organise into COHERENT CONCEPT GROUPS (words that co-occur in the same local bursts), and - critically - are
those groups genuinely FINER than the illustration sections, or do they just reproduce the section labels we already
have?

Method (all from scratch; numpy only):
  1. Content-word set: words with freq>=MINF and burstiness (cv^2 of gaps) > BTHRESH  (the round-89 clustered layer).
  2. Co-occurrence: slide a window of W tokens over the real token stream; count content-word pairs co-occurring
     within the window. Convert to PPMI (positive pointwise mutual information) - frequency-normalised association.
  3. Community detection: weighted label propagation (deterministic seed) on the PPMI graph -> concept groups.
  4. Quality: modularity Q of the discovered partition vs a random same-sized partition (is it a real partition?).
  5. THE HONEST TEST - is it finer than sections?
       (a) MI(group; section) / H(group): how much of a group's identity is just its section. Low => new structure.
       (b) within-section token shuffle null: shuffle content tokens WITHIN each section, rebuild the graph, redetect.
           If Q stays as high, the groups are section-driven (nothing new). If Q drops, the real graph has
           sub-section local co-occurrence = concept groups finer than sections (the payoff).
  6. Interpretability: print the member words of the largest groups and their dominant section.
Usage: python3 mysteries/voynich/concepts.py
"""
import collections, json, math, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
ZL = os.path.join(T, "voynich/ZL3b-n.txt"); rng = np.random.default_rng(90)

def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@=\-]", "", w).strip()

def stream():
    """Return token list with per-token section label, in reading order."""
    toks = []; cur = sec = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h: cur = h.group(1); sec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I"); continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*][PT]\d*>\s*(.*)", ln)
        if not m or not sec: continue
        for w in re.split(r"[.\s]+", m.group(2)):
            c = clean(w)
            if c and re.search(r"[a-zA-Z]", c): toks.append((c, sec))
    return toks

TOK = stream()
words = [w for w, _ in TOK]; secs = [s for _, s in TOK]
N = len(words)

# ---- 1. content-word set: frequent AND bursty (the round-89 clustered layer) ----
MINF = 20; BTHRESH = 2.0
freq = collections.Counter(words)
pos = collections.defaultdict(list)
for i, w in enumerate(words): pos[w].append(i)
def burst(w):
    p = pos[w]
    if len(p) < 3: return 0.0
    g = np.diff(p)
    return float(np.var(g) / (np.mean(g) ** 2 + 1e-9))
content = sorted([w for w in freq if freq[w] >= MINF and burst(w) > BTHRESH], key=lambda w: -burst(w))
cidx = {w: i for i, w in enumerate(content)}; nc = len(content)

# dominant section of each content word
csec = {}
for w in content:
    c = collections.Counter(secs[i] for i in pos[w]); csec[w] = c.most_common(1)[0][0]

# ---- 2. windowed co-occurrence -> PPMI ----
W = 10
def cooc(word_seq):
    co = np.zeros((nc, nc)); marg = np.zeros(nc); total = 0
    # count content tokens in a sliding window
    buf = collections.deque()
    for i, w in enumerate(word_seq):
        ci = cidx.get(w)
        # drop out-of-window
        while buf and buf[0][1] <= i - W: buf.popleft()
        if ci is not None:
            for cj, _ in buf:
                co[ci, cj] += 1; co[cj, ci] += 1
            buf.append((ci, i))
    marg = co.sum(1); total = marg.sum()
    if total == 0: return co
    # PPMI
    P = co / total; pm = marg / total
    with np.errstate(divide="ignore", invalid="ignore"):
        ppmi = np.log2(P / (pm[:, None] * pm[None, :] + 1e-18) + 1e-18)
    ppmi[~np.isfinite(ppmi)] = 0; ppmi[ppmi < 0] = 0; np.fill_diagonal(ppmi, 0)
    return ppmi

G = cooc(words)

# ---- 3. Newman spectral community detection (deterministic; finds its own resolution) ----
def modularity(A, lab):
    m = A.sum() / 2
    if m == 0: return 0.0
    k = A.sum(1); Q = 0.0
    for c in set(lab):
        idx = np.where(lab == c)[0]
        Q += A[np.ix_(idx, idx)].sum() / (2 * m) - (k[idx].sum() / (2 * m)) ** 2
    return float(Q)

def newman(A):
    n = A.shape[0]; m = A.sum() / 2
    if m == 0: return np.zeros(n, int)
    k = A.sum(1); B = A - np.outer(k, k) / (2 * m); groups = []
    def split(idx):
        Bg = B[np.ix_(idx, idx)].copy(); Bg -= np.diag(Bg.sum(1))
        w, V = np.linalg.eigh(Bg); lead = V[:, -1]
        if w[-1] <= 1e-9: groups.append(idx); return
        s = np.where(lead > 0, 1.0, -1.0)
        if (s > 0).all() or (s < 0).all(): groups.append(idx); return
        if (s @ Bg @ s) / (4 * m) <= 1e-9: groups.append(idx); return
        split(idx[s > 0]); split(idx[s < 0])
    split(np.arange(n))
    lab = np.zeros(n, int)
    for c, g in enumerate(groups): lab[g] = c
    return lab

lab = newman(G)
Q_real = modularity(G, lab)
ngroups = len(set(lab))
sizes = sorted(collections.Counter(lab).values(), reverse=True)

# ---- 4. random-partition null (is Q_real a real partition?) ----
Qr = []
for s in range(30):
    rp = np.random.default_rng(s).permutation(lab)  # same group sizes, shuffled membership
    Qr.append(modularity(G, rp))
Qr = np.array(Qr)

# ---- 5a. MI(group; section) / H(group) ----
def mi_hx(lab, sec_of):
    g = lab; se = np.array([sec_of[content[i]] for i in range(nc)])
    sel = np.unique(se); gl = np.unique(g)
    joint = np.zeros((len(gl), len(sel)))
    for i in range(nc): joint[np.where(gl == g[i])[0][0], np.where(sel == se[i])[0][0]] += 1
    joint /= joint.sum(); pg = joint.sum(1); ps = joint.sum(0)
    MI = 0.0
    for a in range(len(gl)):
        for b in range(len(sel)):
            if joint[a, b] > 0: MI += joint[a, b] * math.log2(joint[a, b] / (pg[a] * ps[b] + 1e-18))
    Hg = -np.sum(pg[pg > 0] * np.log2(pg[pg > 0]))
    return float(MI), float(Hg)
MI, Hg = mi_hx(lab, csec)

# ---- 5b. finer-than-sections test: discovered Q vs the SECTION partition's Q on the same graph ----
# assign each content word to its dominant section, measure that partition's modularity on the real co-occurrence graph
seclist = sorted(set(csec.values())); secmap = {s: i for i, s in enumerate(seclist)}
seclab = np.array([secmap[csec[content[i]]] for i in range(nc)])
Q_section = modularity(G, seclab)

# ---- helper: build a section-conditioned iid generator stream (the round-87/88 null model) ----
pools = collections.defaultdict(list)
for w, s in TOK: pools[s].append(w)
secruns = []; run_s = secs[0]; run_n = 0
for s in secs:
    if s == run_s: run_n += 1
    else: secruns.append((run_s, run_n)); run_s = s; run_n = 1
secruns.append((run_s, run_n))
def gen_stream(seed):
    r = np.random.default_rng(seed); out = []
    for s, n in secruns:
        if pools[s]: out.extend(list(r.choice(pools[s], size=n)))
    return out

# ---- 5c. sub-structure WITHIN a section, with a PROPER GENERATOR ENSEMBLE as the null ----
# Newman finds positive modularity on almost any frequency-heterogeneous graph, so the honest null is not a random
# PARTITION but the section-conditioned iid GENERATOR: run it many times and ask whether the REAL within-section Q
# sits above the generator's spread. Only then is the sub-structure content the null model cannot make.
def section_Q(graph, section):
    idx = np.array([i for i in range(nc) if csec[content[i]] == section])
    if len(idx) < 8: return None, None, None
    sub = graph[np.ix_(idx, idx)]; sl = newman(sub); return modularity(sub, sl), sl, idx
def within_section_substructure(section, nboot=25):
    qreal, sl, idx = section_Q(G, section)
    if qreal is None: return None
    qgen = []
    for b in range(nboot):
        gw = gen_stream(5000 + b); Gg = cooc(gw); q, _, _ = section_Q(Gg, section)
        if q is not None: qgen.append(q)
    qgen = np.array(qgen)
    subgroups = collections.defaultdict(list)
    for j, g in enumerate(sl): subgroups[g].append(content[idx[j]])
    big = sorted(subgroups.values(), key=len, reverse=True)[:4]
    thresh = float(np.quantile(qgen, 0.95))
    return dict(section=section, n_words=len(idx), n_subgroups=len(set(sl)),
                Q_real=round(float(qreal), 4), Q_generator_mean=round(float(qgen.mean()), 4),
                Q_generator_sd=round(float(qgen.std()), 4), Q_generator_95pct=round(thresh, 4),
                real_exceeds_generator=bool(qreal > thresh),
                excess_over_generator=round(float(qreal - qgen.mean()), 4),
                example_subgroups=[sorted(g, key=lambda w: -burst(w))[:8] for g in big if len(g) >= 3])
sub_H = within_section_substructure("H"); sub_B = within_section_substructure("B")

# ---- 5d. MORPHOLOGY CONTROL: are the groups semantic concepts, or just affix-families? ----
# Co-occurrence clustering of a slot-grammar text will group morphologically-similar words. Quantify how much.
def affix(w, n=3):
    return (w[:n] if len(w) >= n else w, w[-n:] if len(w) >= n else w)
pref = [affix(w)[0] for w in content]; suf = [affix(w)[1] for w in content]
M = np.zeros((nc, nc))  # morphological adjacency: share a 3-char prefix or suffix
for i in range(nc):
    for j in range(i + 1, nc):
        if pref[i] == pref[j] or suf[i] == suf[j]: M[i, j] = M[j, i] = 1.0
# (a) correlation of co-occurrence weight with morphological sharing, over all pairs
iu = np.triu_indices(nc, 1)
g_flat = G[iu]; m_flat = M[iu]
if g_flat.std() > 0 and m_flat.std() > 0:
    morph_cooc_corr = float(np.corrcoef(g_flat, m_flat)[0, 1])
else:
    morph_cooc_corr = 0.0
# (b) modularity of the DISCOVERED partition scored on the morphology graph (high => groups are affix-coherent)
Q_disc_on_morph = modularity(M, lab)
Q_disc_on_cooc = Q_real
# (c) does co-occurrence grouping EXCEED morphology? within-group mean co-occ for pairs that are NOT affix-related
same = (lab[:, None] == lab[None, :])
nonaffix = (M == 0)
wg_nonaffix = G[np.triu(same & nonaffix, 1)]
cross_nonaffix = G[np.triu((~same) & nonaffix, 1)]
morph = dict(
    morph_cooccurrence_correlation=round(morph_cooc_corr, 3),
    Q_discovered_on_cooccurrence=round(Q_disc_on_cooc, 4),
    Q_discovered_on_morphology=round(Q_disc_on_morph, 4),
    mean_cooc_within_group_nonaffix_pairs=round(float(wg_nonaffix.mean()) if wg_nonaffix.size else 0.0, 4),
    mean_cooc_cross_group_nonaffix_pairs=round(float(cross_nonaffix.mean()) if cross_nonaffix.size else 0.0, 4),
    reading=("morph_cooc_corr and Q_on_morphology measure how affix-driven the groups are; if within-group "
             "co-occurrence exceeds cross-group EVEN for non-affix-sharing word pairs, the grouping carries "
             "association beyond morphology (toward real sub-topics); if not, it is largely affix-family structure"))
grouping_exceeds_morphology = bool(wg_nonaffix.size and cross_nonaffix.size and
                                   wg_nonaffix.mean() > cross_nonaffix.mean() * 1.3)
morph["grouping_exceeds_morphology"] = grouping_exceeds_morphology


# ---- 6. interpret largest groups ----
groups = collections.defaultdict(list)
for i, g in enumerate(lab): groups[g].append(content[i])
big = sorted(groups.values(), key=len, reverse=True)[:6]
def group_desc(ws):
    sc = collections.Counter(csec[w] for w in ws)
    return dict(size=len(ws), words=sorted(ws, key=lambda w: -burst(w))[:12],
                sections=dict(sc), dominant_section=sc.most_common(1)[0][0],
                section_purity=round(sc.most_common(1)[0][1] / len(ws), 2))

out = dict(
    content_words=nc, min_freq=MINF, burst_threshold=BTHRESH, window=W,
    n_groups=ngroups, group_sizes=sizes[:15],
    modularity=dict(real=round(Q_real, 4), random_partition_mean=round(float(Qr.mean()), 4),
                    random_partition_sd=round(float(Qr.std()), 4),
                    real_is_real_partition=bool(Q_real > Qr.mean() + 3 * Qr.std())),
    finer_than_sections=dict(
        n_sections=len(set(csec.values())), n_groups=ngroups,
        MI_group_section=round(MI, 3), H_group=round(Hg, 3),
        fraction_of_group_identity_from_section=round(MI / (Hg + 1e-9), 3),
        Q_discovered=round(Q_real, 4), Q_section_partition=round(Q_section, 4),
        discovered_beats_sections=bool(Q_real > Q_section + 0.01),
        reading=("Q_discovered vs Q_section: if the discovered partition scores higher than assigning words to their "
                 "own section, the groups capture co-occurrence the section labels miss; MI/H says how section-like "
                 "the top-level groups are")),
    within_section_substructure=dict(herbal=sub_H, balneological=sub_B),
    morphology_control=morph,
    example_groups=[group_desc(g) for g in big])

json.dump(out, open(os.path.join(HERE, "concepts_results.json"), "w"), indent=1)
print(f"content words: {nc}   groups: {ngroups}   sizes: {sizes[:10]}")
print(f"modularity real {Q_real:.3f} vs random-partition {Qr.mean():.3f}+/-{Qr.std():.3f} -> real partition: {out['modularity']['real_is_real_partition']}")
print(f"groups vs sections: {len(set(csec.values()))} sections, {ngroups} groups; MI/H(group)={out['finer_than_sections']['fraction_of_group_identity_from_section']}")
print(f"FINER TEST: Q_discovered {Q_real:.3f} vs Q_section-partition {Q_section:.3f} -> discovered beats sections: {out['finer_than_sections']['discovered_beats_sections']}")
for nm, sd in (("herbal(H)", sub_H), ("balneo(B)", sub_B)):
    if sd: print(f"  within {nm}: Q_real {sd['Q_real']:.3f} vs GENERATOR {sd['Q_generator_mean']:.3f}+/-{sd['Q_generator_sd']:.3f} (95pct {sd['Q_generator_95pct']:.3f}) -> real content beyond generator: {sd['real_exceeds_generator']} (excess {sd['excess_over_generator']:+.3f})")
print(f"MORPHOLOGY CONTROL: corr(cooc,affix)={morph['morph_cooccurrence_correlation']}  Q_on_morph={morph['Q_discovered_on_morphology']} vs Q_on_cooc={morph['Q_discovered_on_cooccurrence']}")
print(f"  non-affix pairs: within-group cooc {morph['mean_cooc_within_group_nonaffix_pairs']} vs cross-group {morph['mean_cooc_cross_group_nonaffix_pairs']} -> exceeds morphology: {grouping_exceeds_morphology}")
print("\nexample concept groups (top level):")
for gd in out["example_groups"]:
    print(f"  [{gd['dominant_section']} {int(gd['section_purity']*100)}% pure, n={gd['size']}] {' '.join(gd['words'][:10])}")
for nm, sd in (("H", sub_H), ("B", sub_B)):
    if sd and sd["example_subgroups"]:
        print(f"\nsub-topics within section {nm}:")
        for g in sd["example_subgroups"]: print(f"    {' '.join(g)}")
