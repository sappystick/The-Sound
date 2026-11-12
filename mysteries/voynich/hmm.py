#!/usr/bin/env python3
"""Round 89 - Move 1: extract and characterise the latent state behind the Voynich (round 88 showed it exists).

Fit discrete Hidden Markov Models (scaled Baum-Welch, from scratch) on Voynich-P pages (words reduced to top-K
symbols). Train on EVEN folios, score HELD-OUT ODD folios. If held-out likelihood keeps improving as we add states,
the text supports a real latent dimension (content), not just the iid section pool. Then, for the best model:
  - Viterbi-decode the state path; measure its long-range mutual information (does the latent state carry the round-88
    signal the iid generator could not?);
  - map states to sections (are states just sections, or finer sub-topics?);
  - test whether the state SEQUENCE is structured beyond a Markov chain (reused motifs) vs a random walk.
Compounding the model: we go from 'section-conditioned generator' to 'section-conditioned + N-state latent drift' and
measure N and what the states are.
Usage: python3 mysteries/voynich/hmm.py
"""
import collections, json, math, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
ZL = os.path.join(T, "voynich/ZL3b-n.txt"); rng = np.random.default_rng(89)
def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@=\-]", "", w).strip()
def parse():
    pages = {}; cur = sec = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h: cur = h.group(1); sec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I"); pages.setdefault(cur, [sec, []]); continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*][PT]\d*>\s*(.*)", ln)
        if not m or not sec: continue
        pages[cur][1] += [clean(w) for w in re.split(r"[.\s]+", m.group(2)) if clean(w) and re.search(r"[a-zA-Z]", clean(w))]
    return {f: (s, w) for f, (s, w) in pages.items() if len(w) >= 20}
PAGES = parse(); folios = sorted(PAGES, key=lambda f: (int(re.match(r"f(\d+)", f).group(1)), f))
even, odd = folios[::2], folios[1::2]
Ksym = 60
top = [w for w, _ in collections.Counter(w for f in even for w in PAGES[f][1]).most_common(Ksym)]
sidx = {w: i for i, w in enumerate(top)}; V = Ksym + 1
def seq(f): return np.array([sidx.get(w, Ksym) for w in PAGES[f][1]], np.int64)

class HMM:
    def __init__(s, N, V): s.N, s.V = N, V; s.A = rng.dirichlet(np.ones(N), N); s.B = rng.dirichlet(np.ones(V) * 0.5, N); s.pi = rng.dirichlet(np.ones(N))
    def fb(s, o):
        T = len(o); al = np.zeros((T, s.N)); c = np.zeros(T)
        al[0] = s.pi * s.B[:, o[0]]; c[0] = al[0].sum() + 1e-300; al[0] /= c[0]
        for t in range(1, T): al[t] = (al[t-1] @ s.A) * s.B[:, o[t]]; c[t] = al[t].sum() + 1e-300; al[t] /= c[t]
        be = np.zeros((T, s.N)); be[-1] = 1
        for t in range(T-2, -1, -1): be[t] = (s.A @ (s.B[:, o[t+1]] * be[t+1])) / c[t+1]
        return al, be, c
    def train(s, seqs, iters=25):
        for _ in range(iters):
            A = np.zeros((s.N, s.N)); B = np.zeros((s.N, s.V)); pi = np.zeros(s.N); ll = 0
            for o in seqs:
                al, be, c = s.fb(o); ll += np.log(c).sum(); T = len(o)
                g = al * be; g /= g.sum(1, keepdims=True) + 1e-300
                pi += g[0]
                for t in range(T-1):
                    xi = (al[t][:, None] * s.A * s.B[:, o[t+1]][None, :] * be[t+1][None, :])
                    A += xi / (xi.sum() + 1e-300)
                for t in range(T): B[:, o[t]] += g[t]
            s.A = A / (A.sum(1, keepdims=True) + 1e-300); s.B = B / (B.sum(1, keepdims=True) + 1e-300); s.pi = pi / pi.sum()
        return s
    def ll(s, o): return np.log(s.fb(o)[2]).sum()
    def viterbi(s, o):
        T = len(o); d = np.zeros((T, s.N)); psi = np.zeros((T, s.N), int)
        d[0] = np.log(s.pi + 1e-300) + np.log(s.B[:, o[0]] + 1e-300)
        lA = np.log(s.A + 1e-300)
        for t in range(1, T):
            m = d[t-1][:, None] + lA; psi[t] = m.argmax(0); d[t] = m.max(0) + np.log(s.B[:, o[t]] + 1e-300)
        path = [int(d[-1].argmax())]
        for t in range(T-1, 0, -1): path.append(int(psi[t][path[-1]]))
        return path[::-1]

train = [seq(f) for f in even]; test = [seq(f) for f in odd]
out = {"folios": len(folios), "symbols": V, "model_selection": {}}
best = None
for N in (1, 2, 4, 8, 12, 16):
    h = HMM(N, V).train(train, iters=20 if N <= 8 else 14)
    hll = sum(h.ll(o) for o in test); ntok = sum(len(o) for o in test)
    perplexity = math.exp(-hll / ntok)
    out["model_selection"][N] = dict(heldout_perplexity=round(perplexity, 3), heldout_bits_per_word=round(-hll / ntok / math.log(2), 3))
    if best is None or perplexity < best[1]: best = (h, perplexity, N)
H, _, N = best
out["best_N_states"] = N
# analyse the best model on ALL pages
states = {f: H.viterbi(seq(f)) for f in folios}
# long-range MI of the STATE path (does latent state carry the round-88 signal?)
allstates = np.array([st for f in folios for st in states[f]])
def Id(sym, n, dists):
    N_ = len(sym); r = {}
    for d in dists:
        a, b = sym[:-d], sym[d:]; j = np.zeros((n, n)); np.add.at(j, (a, b), 1); j /= j.sum()
        pa, pb = j.sum(1), j.sum(0); aa, bb = np.where(j > 0)
        r[d] = float(np.sum(j[aa, bb] * np.log2(j[aa, bb] / (pa[aa] * pb[bb] + 1e-18))))
    return r
D = [1, 5, 21, 55, 144]
st_I = Id(allstates, N, D)
sh = allstates.copy(); rng.shuffle(sh); st_I_sh = Id(sh, N, D)
out["state_long_range_MI"] = dict(observed={d: round(st_I[d], 4) for d in D}, shuffled={d: round(st_I_sh[d], 4) for d in D},
    long_range_net=round(sum(max(0, st_I[d] - st_I_sh[d]) for d in D if d >= 21), 4),
    reading="if the state path has long-range MI above its shuffle, the latent state (not the words) carries the organisation")
# states vs sections
sec_state = collections.defaultdict(collections.Counter)
for f in folios:
    for st in states[f]: sec_state[PAGES[f][0]][st] += 1
out["state_by_section"] = {s: {int(k): round(v / sum(c.values()), 2) for k, v in c.most_common(4)} for s, c in sec_state.items()}
# is the state SEQUENCE structured beyond a Markov chain? compare 2-gram vs 3-gram predictability gain
def kgram_bits(paths, k):
    ctx = collections.defaultdict(collections.Counter)
    for p in paths:
        for i in range(len(p) - k): ctx[tuple(p[i:i+k])][p[i+k]] += 1
    bits = n = 0
    for p in paths:
        for i in range(len(p) - k):
            c = ctx[tuple(p[i:i+k])]; tot = sum(c.values()); bits += -math.log2(c[p[i+k]] / tot); n += 1
    return bits / max(1, n)
paths = [states[f] for f in folios]
out["state_sequence_structure"] = dict(bits_order1=round(kgram_bits(paths, 1), 3), bits_order2=round(kgram_bits(paths, 2), 3),
    bits_order3=round(kgram_bits(paths, 3), 3),
    reading="falling bits from order1->3 = the state sequence has higher-order structure (reused motifs), not a memoryless walk")

# CAPSTONE: generate text from the fitted latent-drift model; does it reproduce round-88 word-level long-range MI?
def sample_page(H, L):
    st = rng.choice(H.N, p=H.pi); outsym = []
    for _ in range(L):
        outsym.append(rng.choice(H.V, p=H.B[st])); st = rng.choice(H.N, p=H.A[st])
    return outsym
gen = [x for f in folios for x in sample_page(H, len(PAGES[f][1]))]
real = np.array([sidx.get(w, Ksym) for f in folios for w in PAGES[f][1]])
D2=[1,5,21,55,144]
def net_lr(sym):
    sym=np.asarray(sym); o=Id(sym,V,D2); sh=sym.copy(); rng.shuffle(sh); f=Id(sh,V,D2)
    return round(sum(max(0,o[d]-f[d]) for d in D2 if d>=21),4)
out["CAPSTONE_drift_explains_round88"]=dict(
    real_words_long_range=net_lr(real), hmm_generated_long_range=net_lr(gen),
    iid_generator_was=0.020, reading=("if HMM-generated approx real, the latent-drift model fully reproduces the "
      "round-88 long-range signal -> the organisation is slow drift, not hidden content; residual = possible content"))

json.dump(out, open(os.path.join(HERE, "hmm_results.json"), "w"), indent=1)
print("held-out perplexity by #states:", {k: v["heldout_perplexity"] for k, v in out["model_selection"].items()})
print("best N states:", N)
print("state long-range net MI:", out["state_long_range_MI"]["long_range_net"], "(words' was 0.041; shuffle floor ~0)")
print("state by section:", json.dumps(out["state_by_section"]))
print("state seq bits order1/2/3:", out["state_sequence_structure"]["bits_order1"], out["state_sequence_structure"]["bits_order2"], out["state_sequence_structure"]["bits_order3"])
print("CAPSTONE:", out["CAPSTONE_drift_explains_round88"])
