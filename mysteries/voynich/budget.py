#!/usr/bin/env python3
"""Round 92 I: information budget (PREREG_92.md). Train on even pages, score odd pages, same pipeline for every text.
Word models: (a) unigram, (b) Witten-Bell interpolated bigram; unseen words are spelled by a Witten-Bell character
5-gram trained on the even pages, so no text gets a free pass on new words. (c) the same with words replaced by roots
(Voynich only). Bits per page = tokens on the page x bits per word under (b).
Usage: python3 mysteries/voynich/budget.py <macer html> <sblgnt dir> <BSB.csv>"""
import collections, csv, glob, html, json, math, os, re, sys, unicodedata
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zl import load, split
HERE = os.path.dirname(os.path.abspath(__file__)); MAC, SBL, BSB = sys.argv[1:4]
class CharWB:
    def __init__(s, words, N=5):
        s.N = N; s.c = [collections.defaultdict(collections.Counter) for _ in range(N)]; s.V = set("$")
        for w in words:
            t = "^" * (N - 1) + w + "$"; s.V |= set(w)
            for i in range(N - 1, len(t)):
                for k in range(N): s.c[k][t[i - k:i]][t[i]] += 1
    def p(s, h, ch):
        pr = 1 / (len(s.V) + 1)
        for k in range(s.N):
            ctx = h[len(h) - k:] if k else ""; C = s.c[k].get(ctx)
            if not C: continue
            n = sum(C.values()); t = len(C); lam = n / (n + t); pr = lam * C[ch] / n + (1 - lam) * pr
        return pr
    def bits(s, w):
        t = "^" * (s.N - 1) + w + "$"; return -sum(math.log2(s.p(t[i - s.N + 1:i], t[i])) for i in range(s.N - 1, len(t)))
def evaluate(train, test):
    """train/test: lists of pages, each a list of words."""
    tw = [w for p in train for w in p]; uni = collections.Counter(tw); N = len(tw); big = collections.defaultdict(collections.Counter)
    for p in train:
        for a, b in zip(p, p[1:]): big[a][b] += 1
    ch = CharWB(list(uni.elements())); T = len(uni)
    def p_uni(w):   # Witten-Bell: mass T/(N+T) to unseen words, spelled by the character model
        return (uni[w] + T * 2 ** -ch.bits(w)) / (N + T)
    def p_bi(v, w):
        C = big.get(v)
        if not C: return p_uni(w)
        n = sum(C.values()); t = len(C); lam = n / (n + t); return lam * C[w] / n + (1 - lam) * p_uni(w)
    hu = hb = 0.0; n = 0; per_page = []
    for p in test:
        pb = 0.0
        for i, w in enumerate(p):
            u = -math.log2(p_uni(w)); b = -math.log2(p_bi(p[i - 1], w)) if i else u; hu += u; hb += b; pb += b; n += 1
        per_page.append(pb)
    return dict(tokens=n, bits_per_word_unigram=round(hu / n, 3), bits_per_word_bigram=round(hb / n, 3), context_gain=round((hu - hb) / n, 3),
                mean_tokens_per_page=round(n / len(test), 1), bits_per_page=round(float(np.mean(per_page)), 1), oov_rate=round(sum(1 for p in test for w in p if w not in uni) / n, 3))
def pages_of(words, size): return [words[i:i + size] for i in range(0, len(words) - size + 1, size)]
V = load(); vp = [[w for l in p["lines"] for w in l] for p in V.values() if p["lines"]]
size = int(np.median([len(p) for p in vp]))
def eo(P): return P[0::2], P[1::2]
R = {"page_size_for_controls": size}
R["Voynich (all paragraph text)"] = evaluate(*eo(vp))
R["Voynich roots only"] = evaluate(*eo([[split(w)[1] or "_" for w in p] for p in vp]))
for L in ("A", "B"):
    R[f"Voynich language {L}"] = evaluate(*eo([[w for l in p["lines"] for w in l] for p in V.values() if p["lines"] and p["L"] == L]))
t = open(MAC, encoding="utf-8").read(); body = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)))
mac = re.findall(r"[a-z]+", body.lower())
def nrm(w): w = unicodedata.normalize("NFD", w.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in w if not unicodedata.combining(c)).replace("ς", "σ"))
gj = [nrm(l.split()[5]) for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8")]; gj = [w for w in gj if w]
ej = [w for r in csv.DictReader(open(BSB, encoding="utf-8")) if r["Book"] == "John" for w in re.findall(r"[a-z]+", r["Text"].lower())]
for name, ws in (("Latin herbal (Macer)", mac), ("Greek John", gj), ("English John", ej)):
    R[name] = evaluate(*eo(pages_of(ws, size)))
for k, v in R.items():
    if isinstance(v, dict): print(f"{k:30s} bits/word uni {v['bits_per_word_unigram']:6.2f}  bigram {v['bits_per_word_bigram']:6.2f}  context gain {v['context_gain']:5.2f}  OOV {v['oov_rate']:.2f}  bits/page {v['bits_per_page']:7.1f} ({v['mean_tokens_per_page']} tok)")
json.dump(R, open(os.path.join(HERE, "budget_results.json"), "w"), indent=1, ensure_ascii=False)
