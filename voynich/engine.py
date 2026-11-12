#!/usr/bin/env python3
"""Voynich multi-angle engine. The Sound project, round 66.

The question put to it: is the Voynich Manuscript a plaintext alchemical recipe (e.g. for making gold), a ciphered
natural language, or a constructed / generated system? We DO NOT claim a decoding. We measure its known anomalies
against controls and label every result V (verified here) / K (known in scholarship) / N (negative) / Reading.

Corpora:
  VOY-P  Voynich paragraph text   (Takahashi EVA, loci type P)       - the running "text"
  VOY-L  Voynich label words      (Takahashi EVA, loci type L)       - words next to pictures
  GEBER  pseudo-Geber, Summa Perfectionis (Latin) - the era's "how to make gold" alchemy
  MAPPAE Mappae Clavicula (Latin) - a medieval recipe collection
  VULG   Latin Vulgate            - natural-language Latin of ~ the right register
  GRK    Greek New Testament (SBLGNT) - natural language, different script
  HEB    Hebrew Bible (WLC consonants) - natural language, abjad
  KANON  our constructed language (round 65) - a known generative slot-grammar system
  SLOT   a 3-slot random generator tuned to Voynich's prefix/core/suffix inventories (a null "grille")
  RAND   order-0 random text from Voynich's letter frequencies - the pure-chance floor

Angles: 1 entropy signature, 2 slot-grammar rigidity, 3 repetition, 4 labels-vs-text, 5 line-as-unit (LAAFU),
        6 the alchemy/recipe test, 7 the constructed-system test (does a generative grammar reproduce all anomalies?).
Usage: python3 voynich/engine.py
"""
import collections, glob, json, math, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); T = os.path.join(ROOT, "sources/texts")
rng = np.random.default_rng(66); out = {}

# ------------------------------------------------------------------ corpora as list-of-lines, each line a list of words
def voy():
    P, L, lines_P = [], [], []
    for ln in open(os.path.join(T, "voynich/alephmembeth_voynich/analysis/takahashi_original.txt"), encoding="utf-8"):
        m = re.match(r"<f\d+[rv]\d*\.([A-Z])[a-z]?\d*\.\d+;H>\s*(.*)", ln)
        if not m: continue
        typ, body = m.group(1), m.group(2)
        body = re.sub(r"[-=]$", "", body.strip())
        words = [re.sub(r"[!*%]", "", w) for w in body.split(".")]   # !,* = uncertain/illegible markers
        words = [w for w in words if w and re.search(r"[a-zA-Z]", w)]
        if not words: continue
        if typ == "P": P += words; lines_P.append(words)
        elif typ == "L": L += words
    return P, L, lines_P

def latin_words(path, lo=40000):
    t = open(path, encoding="utf-8", errors="ignore").read().lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    ws = [w for w in t.split() if 2 <= len(w) <= 20]
    # drop OCR junk lines by keeping words with a vowel
    ws = [w for w in ws if re.search(r"[aeiou]", w)]
    return ws[:lo]

def vulg_words(lo=40000):
    d = json.load(open(os.path.join(T, "versions/formats/json/Vulgate.json")))
    ws = []
    for b in d["books"]:
        for ch in b["chapters"]:
            for v in ch["verses"]:
                ws += re.sub(r"[^a-z ]", " ", v["text"].lower()).split()
                if len(ws) > lo: return ws[:lo]
    return ws[:lo]

def grk_words(lo=40000):
    import unicodedata
    ws = []
    for f in sorted(glob.glob(os.path.join(T, "sblgnt/*-morphgnt.txt"))):
        for l in open(f, encoding="utf-8"):
            w = unicodedata.normalize("NFD", l.split()[3].lower()); w = "".join(c for c in w if not unicodedata.combining(c))
            ws.append(re.sub(r"[^a-zα-ω]", "", w))
            if len(ws) > lo: return [w for w in ws if w][:lo]
    return [w for w in ws if w][:lo]

def heb_words(lo=40000):
    ws = []
    for f in sorted(glob.glob(os.path.join(T, "morphhb/wlc/*.xml"))):
        for m in re.finditer(r"<w[^>]*>(.*?)</w>", open(f, encoding="utf-8").read()):
            w = re.sub(r"[^א-ת]", "", re.sub(r"<[^>]+>", "", m.group(1)))
            if w: ws.append(w)
            if len(ws) > lo: return ws[:lo]
    return ws[:lo]

def kanon_words(n=6000):
    """generate KANON-style words: 1-3 syllables consonant+vowel, optional cadence vowel."""
    C, V = "ktpbdglmnrsh", "aeyiouw"
    ws = []
    for _ in range(n):
        s = int(rng.integers(1, 4)); w = "".join(C[rng.integers(12)] + V[rng.integers(7)] for _ in range(s))
        if rng.random() < 0.3: w += V[rng.integers(7)]
        ws.append(w)
    return ws

print("loading...", file=sys.stderr)
VP, VL, VP_lines = voy()
CORP = {"VOY-P": VP, "VOY-L": VL,
        "GEBER": latin_words(os.path.join(T, "alchemy/geberisphilosoph00gebe.txt")),
        "MAPPAE": latin_words(os.path.join(T, "alchemy/mappae_clavicula.txt")),
        "VULG": vulg_words(), "GRK": grk_words(), "HEB": heb_words(), "KANON": kanon_words()}
# RAND null from Voynich letter frequencies, with Voynich word-length distribution
vchars = [c for w in VP for c in w]; vfreq = collections.Counter(vchars)
alpha, probs = zip(*[(c, n / len(vchars)) for c, n in vfreq.items()])
vlen = collections.Counter(len(w) for w in VP); lk, lp = zip(*[(k, n) for k, n in vlen.items()]); lp = np.array(lp) / sum(lp)
def rand_words(n=6000):
    out = []
    for _ in range(n):
        L = int(rng.choice(lk, p=lp)); out.append("".join(rng.choice(alpha, p=probs) for _ in range(max(1, L))))
    return out
CORP["RAND"] = rand_words()
out["corpus_sizes"] = {k: dict(words=len(v), types=len(set(v)), chars=sum(len(w) for w in v)) for k, v in CORP.items()}

# ------------------------------------------------------------------ Angle 1: entropy signature
def entropies(words):
    stream = " ".join(words)
    uni = collections.Counter(stream); N = len(stream)
    h1 = -sum(n / N * math.log2(n / N) for n in uni.values())
    bi = collections.Counter(zip(stream, stream[1:]))
    h2 = 0.0
    for (a, b), n in bi.items():
        p_ab = n / (N - 1); p_a = uni[a] / N
        h2 += p_ab * math.log2(p_a / p_ab)
    # within-word conditional entropy (resets at boundaries) - the slot-rigidity signal
    bw = collections.Counter(); uw = collections.Counter()
    for w in words:
        for c in w: uw[c] += 1
        for a, b in zip(w, w[1:]): bw[(a, b)] += 1
    Nw = sum(uw.values()); Nb = sum(bw.values())
    h2w = 0.0
    for (a, b), n in bw.items():
        p_ab = n / Nb; p_a = uw[a] / Nw
        h2w += p_ab * math.log2(p_a / p_ab)
    return dict(h1=round(h1, 3), h2=round(h2, 3), h2_within_word=round(h2w, 3), alphabet=len(uni) - 1)
out["A1_entropy"] = {k: entropies(v) for k, v in CORP.items()}

# ------------------------------------------------------------------ Angle 2: slot-grammar rigidity
def rigidity(words):
    # type-level successor branching within words; low = rigid slots
    succ = collections.defaultdict(set)
    for w in set(words):
        for a, b in zip(w, w[1:]): succ[a].add(b)
    mean_branch = np.mean([len(s) for s in succ.values()]) if succ else 0
    # prefix/suffix concentration: mass covered by the top-8 word-initial and word-final bigrams
    pre = collections.Counter(w[:2] for w in words if len(w) >= 2)
    suf = collections.Counter(w[-2:] for w in words if len(w) >= 2)
    top_pre = sum(n for _, n in pre.most_common(8)) / max(1, sum(pre.values()))
    top_suf = sum(n for _, n in suf.most_common(8)) / max(1, sum(suf.values()))
    return dict(mean_within_word_branching=round(float(mean_branch), 2), top8_prefix_mass=round(top_pre, 3), top8_suffix_mass=round(top_suf, 3))
out["A2_slot_rigidity"] = {k: rigidity(v) for k, v in CORP.items()}

# ------------------------------------------------------------------ Angle 3: repetition
def repetition(words):
    adj = sum(1 for a, b in zip(words, words[1:]) if a == b)
    runs3 = 0; i = 0
    while i < len(words) - 2:
        if words[i] == words[i+1] == words[i+2]: runs3 += 1; i += 3
        else: i += 1
    # near-repeats: adjacent words differing by 1 edit
    def ed1(a, b):
        if abs(len(a) - len(b)) > 1: return False
        if len(a) == len(b): return sum(x != y for x, y in zip(a, b)) == 1
        s, l = (a, b) if len(a) < len(b) else (b, a)
        for i in range(len(l)):
            if l[:i] + l[i+1:] == s: return True
        return False
    near = sum(1 for a, b in zip(words, words[1:]) if a != b and ed1(a, b))
    return dict(adjacent_equal_per_1000=round(1000 * adj / len(words), 2), triple_runs=runs3,
                adjacent_edit1_per_1000=round(1000 * near / len(words), 2))
out["A3_repetition"] = {k: repetition(v) for k, v in CORP.items()}

# ------------------------------------------------------------------ Angle 4: labels vs text (the user's ask)
def dist_initial(words):
    c = collections.Counter(w[0] for w in words if w); N = sum(c.values()); return {k: v / N for k, v in c.items()}
def kl(p, q):
    keys = set(p) | set(q); return sum(p.get(k, 0) * math.log2(p.get(k, 1e-9) / max(q.get(k, 1e-9), 1e-9)) for k in keys if p.get(k, 0) > 0)
pi_P, pi_L = dist_initial(VP), dist_initial(VL)
label_set, text_set = set(VL), set(VP)
excl = [w for w in VL if w not in text_set]
# length and suffix comparison
lenP, lenL = np.mean([len(w) for w in VP]), np.mean([len(w) for w in VL])
out["A4_labels_vs_text"] = dict(
    n_labels=len(VL), n_label_types=len(label_set),
    label_initial_KL_from_text_bits=round(kl(pi_L, pi_P), 3),
    label_exclusive_vocab_share=round(len(excl) / len(VL), 3),
    label_exclusive_types_share=round(len({w for w in excl}) / len(label_set), 3),
    mean_len_text=round(float(lenP), 2), mean_len_label=round(float(lenL), 2),
    top_label_initials=collections.Counter(w[0] for w in VL).most_common(6),
    top_text_initials=collections.Counter(w[0] for w in VP).most_common(6),
    note="labels = words written next to pictures (loci type L); text = running paragraphs (type P)")

# ------------------------------------------------------------------ Angle 5: line as a unit (LAAFU)
first = collections.Counter(l[0][0] for l in VP_lines if l and l[0])
last = collections.Counter(l[-1][-1] for l in VP_lines if l and l[-1])
mid = collections.Counter(w[0] for l in VP_lines for w in l[1:-1] if w)
def norm(c): N = sum(c.values()); return {k: v / N for k, v in c.items()}
out["A5_line_as_unit"] = dict(
    line_first_initial_KL_from_mid_bits=round(kl(norm(first), norm(mid)), 3),
    line_last_final_glyph_top=collections.Counter(l[-1][-1] for l in VP_lines if l).most_common(5),
    line_first_initial_top=first.most_common(5), mid_word_initial_top=mid.most_common(5),
    note="Currier's LAAFU: if line-position changes glyph distributions, the line is a structural unit - abnormal for prose")

# ------------------------------------------------------------------ Angle 6: the alchemy / recipe test
def section_repeat_profile(words, win=50):
    # procedural texts repeat a small set of 'operation' words densely; measure burstiness of the top-20 words
    top = set(w for w, _ in collections.Counter(words).most_common(20))
    hits = np.array([1 if w in top else 0 for w in words])
    dens = [hits[i:i+win].mean() for i in range(0, len(hits) - win, win)]
    return dict(top20_token_share=round(float(hits.mean()), 3), burstiness_cv=round(float(np.std(dens) / (np.mean(dens) + 1e-9)), 3))
out["A6_recipe_profile"] = {k: section_repeat_profile(v) for k, v in {"VOY-P": VP, "GEBER": CORP["GEBER"], "MAPPAE": CORP["MAPPAE"], "VULG": CORP["VULG"]}.items()}

# ------------------------------------------------------------------ Angle 7: the constructed-system test
# which model reproduces the FULL Voynich anomaly signature (low h2 AND low branching AND high repetition)?
def signature(k):
    e, s, r = out["A1_entropy"][k], out["A2_slot_rigidity"][k], out["A3_repetition"][k]
    return dict(h2=e["h2"], within_word_branching=s["mean_within_word_branching"], adj_repeat_per_1000=r["adjacent_equal_per_1000"])
voy_sig = signature("VOY-P")
def dist_to_voy(k):
    s = signature(k)
    return round(math.sqrt(((s["h2"]-voy_sig["h2"])/0.5)**2 + ((s["within_word_branching"]-voy_sig["within_word_branching"])/1.0)**2 + ((s["adj_repeat_per_1000"]-voy_sig["adj_repeat_per_1000"])/3.0)**2), 2)
out["A7_which_model_fits"] = dict(voynich_signature=voy_sig,
    distance_to_voynich={k: dist_to_voy(k) for k in CORP if k != "VOY-P"},
    note="z-scaled distance of (h2, within-word branching, adjacent-repeat rate) to Voynich-P; smallest = best model of the anomaly cluster")

json.dump(out, open(os.path.join(HERE, "results.json"), "w"), ensure_ascii=False, indent=1)
# print compact tables
cols = list(CORP)
print("\nA1 ENTROPY (bits)            " + "".join(f"{k:>8}" for k in cols))
for metric in ("h1", "h2", "h2_within_word"):
    print(f"  {metric:<24}" + "".join(f"{out['A1_entropy'][k][metric]:>8}" for k in cols))
print("\nA2 RIGIDITY                  " + "".join(f"{k:>8}" for k in cols))
for metric in ("mean_within_word_branching", "top8_prefix_mass", "top8_suffix_mass"):
    print(f"  {metric:<24}" + "".join(f"{out['A2_slot_rigidity'][k][metric]:>8}" for k in cols))
print("\nA3 REPETITION                " + "".join(f"{k:>8}" for k in cols))
for metric in ("adjacent_equal_per_1000", "triple_runs", "adjacent_edit1_per_1000"):
    print(f"  {metric:<24}" + "".join(f"{out['A3_repetition'][k][metric]:>8}" for k in cols))
print("\nA4 LABELS:", json.dumps(out["A4_labels_vs_text"], ensure_ascii=False)[:400])
print("\nA5 LINE:", json.dumps(out["A5_line_as_unit"], ensure_ascii=False)[:300])
print("\nA6 RECIPE:", json.dumps(out["A6_recipe_profile"], ensure_ascii=False))
print("\nA7 FIT:", json.dumps(out["A7_which_model_fits"], ensure_ascii=False))
