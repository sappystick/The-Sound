#!/usr/bin/env python3
"""Round 88 - IS THERE ANYTHING LEFT TO DECIPHER? A reference-free test for latent/lost content.

The investigation's blind spot: every test so far compared the Voynich to KNOWN systems (languages, herbals, ciphers,
plants). A unique or lost system matches none of them, which looks like 'empty' but need not be. This test uses no
external key. It asks whether the text carries LONG-RANGE INFORMATION that our best local generator does NOT produce.
  - A purely local process (Markov / slot+copy / section-conditioned generator) has mutual information I(d) between
    positions d apart that decays to ~0 within a few words.
  - Meaningful text (topics, structure, cross-reference) keeps I(d) positive at long range (Montemurro & Zanette 2013
    reported such long-range structure in the Voynich).
If the Voynich's I(d) stays above our generator's at long range, there is latent structure the generator can't explain
= real information worth deciphering (even if unique/lost). If it matches the generator, nothing is left.

Method: reduce each word to a symbol (top-K words + 'other'); estimate I(d) between symbols d apart, bias-corrected by
subtracting the shuffled-text I(d). Compare: VOY-P, section-conditioned GENERATOR, LATIN (real language), and the
section-SHUFFLED Voynich (destroys long-range, keeps local).
Usage: python3 mysteries/voynich/longrange.py
"""
import collections, json, math, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
ZL = os.path.join(T, "voynich/ZL3b-n.txt"); rng = np.random.default_rng(88)
def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@=\-]", "", w).strip()

def voy_stream():
    cur = sec = None; pageseq = []  # list of (page, [words]) herbal+bio+pharma+stars running text in reading order
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h: cur = h.group(1); sec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I"); continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*][PT]\d*>\s*(.*)", ln)
        if not m or not sec: continue
        ws = [clean(w) for w in re.split(r"[.\s]+", m.group(2)) if clean(w) and re.search(r"[a-zA-Z]", clean(w))]
        if ws:
            if pageseq and pageseq[-1][0] == cur: pageseq[-1][1].extend(ws)
            else: pageseq.append((cur, ws))
    return pageseq

PS = voy_stream()
VOY = [w for _, ws in PS for w in ws]

def latin_stream(lo=40000):
    t = re.sub(r"[^a-z\s]", " ", open(os.path.join(T, "alchemy/geberisphilosoph00gebe.txt"), encoding="utf-8", errors="ignore").read().lower())
    return [w for w in t.split() if 2 <= len(w) <= 20 and re.search(r"[aeiou]", w)][:lo]

def gen_stream():
    # section-conditioned local generator: per-section word pool, draw iid within each page (local, no long-range)
    pools = collections.defaultdict(collections.Counter); cur = sec = None
    secof = {}
    for p, ws in PS: secof[p] = None
    # rebuild section per page
    cur = sec = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h: cur = h.group(1); sec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I")
        if cur in secof: secof[cur] = sec
    for p, ws in PS:
        for w in ws: pools[secof[p]][w] += 1
    out = []
    for p, ws in PS:
        c = pools[secof[p]]; ks, vs = zip(*c.items()); vs = np.array(vs) / sum(vs)
        prev = None
        for _ in ws:
            if prev is not None and rng.random() < 0.08: out.append(prev)   # mild local copy
            else: prev = ks[rng.choice(len(ks), p=vs)]; out.append(prev)
    return out

def reduce(words, K=40):
    top = [w for w, _ in collections.Counter(words).most_common(K)]
    idx = {w: i for i, w in enumerate(top)}
    return np.array([idx.get(w, K) for w in words]), K + 1

def I_of_d(sym, n, dists):
    N = len(sym); pi = np.bincount(sym, minlength=n) / N
    Hi = -np.sum(pi[pi > 0] * np.log2(pi[pi > 0]))
    res = {}
    for d in dists:
        a = sym[:-d]; b = sym[d:]
        joint = np.zeros((n, n)); np.add.at(joint, (a, b), 1); joint /= joint.sum()
        pa = joint.sum(1); pb = joint.sum(0); mask = joint > 0
        I = np.sum(joint[mask] * np.log2(joint[mask] / (pa[a[:0]].size and 1 or 1)))  # placeholder
        # proper MI
        I = 0.0
        aa, bb = np.where(mask)
        I = float(np.sum(joint[aa, bb] * np.log2(joint[aa, bb] / (pa[aa] * pb[bb] + 1e-18))))
        res[d] = I
    return res, Hi

DISTS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
def curve(words, label):
    sym, n = reduce(words)
    obs, Hi = I_of_d(sym, n, DISTS)
    # shuffle baseline (bias floor): average of 8 shuffles
    floor = {d: 0.0 for d in DISTS}
    for _ in range(8):
        s = sym.copy(); rng.shuffle(s); f, _ = I_of_d(s, n, DISTS)
        for d in DISTS: floor[d] += f[d] / 8
    net = {d: round(max(0.0, obs[d] - floor[d]), 5) for d in DISTS}
    return dict(label=label, words=len(words), H1=round(Hi, 2), I_net=net,
                long_range_bits=round(sum(net[d] for d in DISTS if d >= 21), 5))

out = dict(distances=DISTS, curves={})
for words, lab in [(VOY, "VOY-P"), (gen_stream(), "GENERATOR"), (latin_stream(), "LATIN"), (list(rng.permutation(VOY)), "VOY-SHUFFLED")]:
    out["curves"][lab] = curve(words, lab)
voy_lr = out["curves"]["VOY-P"]["long_range_bits"]; gen_lr = out["curves"]["GENERATOR"]["long_range_bits"]
lat_lr = out["curves"]["LATIN"]["long_range_bits"]
out["verdict"] = dict(
    voynich_long_range_bits=voy_lr, generator_long_range_bits=gen_lr, latin_long_range_bits=lat_lr,
    voynich_exceeds_generator=bool(voy_lr > gen_lr * 1.5),
    reading=("Voynich carries long-range information BEYOND the local generator (latent structure = something to "
             "decipher)" if voy_lr > gen_lr * 1.5 else
             "Voynich long-range information is explained by the local generator (little latent content beyond the process)"))
json.dump(out, open(os.path.join(HERE, "longrange_results.json"), "w"), indent=1)
print(f"{'label':<14}{'H1':>6}" + "".join(f"  I(d={d})" for d in DISTS[-5:]) + "   LR>=21")
for lab in ("VOY-P", "GENERATOR", "LATIN", "VOY-SHUFFLED"):
    c = out["curves"][lab]; print(f"{lab:<14}{c['H1']:>6}" + "".join(f"{c['I_net'][d]:>9.4f}" for d in DISTS[-5:]) + f"{c['long_range_bits']:>9.4f}")
print("\nVERDICT:", out["verdict"]["reading"])
