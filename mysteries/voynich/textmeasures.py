"""Shared entry and line measures for herbal comparisons (used by herbal.py and controls.py)."""
import collections, math
import numpy as np
rng = np.random.default_rng(77)
def words(e): return [w for ln in e for w in ln]
def measures(E):
    ent = [words(e) for e in E]; n = [len(x) for x in ent]; df = collections.Counter(w for x in ent for w in set(x)); tok = collections.Counter(w for x in ent for w in x)
    k = len(ent)
    # M2 spread
    types_one_entry = sum(1 for w in df if df[w] == 1) / len(df)
    freq = [w for w, c in tok.items() if c >= 10]
    def juilland(w):
        v = np.array([x.count(w) / len(x) for x in ent]); return 1 - (v.std() / (v.mean() + 1e-12)) / math.sqrt(k - 1)
    D = float(np.median([juilland(w) for w in freq])) if freq else float("nan")
    tok_specific = float(np.mean([sum(1 for w in x if df[w] <= 2) / len(x) for x in ent]))
    # M3 plant-name effect: each entry's top TF-IDF word; is it rare elsewhere, and is it in the first line?
    top, first_line, own = [], 0, 0
    for e, x in zip(E, ent):
        c = collections.Counter(x); sc = {w: c[w] * math.log(k / df[w]) for w in c if c[w] >= 2}
        if not sc: continue
        w = max(sc, key=sc.get); top.append(w); own += df[w] <= 3; first_line += w in e[0]
    # M4 line position
    def mi(lines):
        c = collections.Counter(); wc = collections.Counter(); pc = collections.Counter()
        for ws in lines:
            for i, w in enumerate(ws):
                p = 0 if i == 0 else (2 if i == len(ws) - 1 else 1); c[(w, p)] += 1; wc[w] += 1; pc[p] += 1
        keep = {w for w, m_ in wc.items() if m_ >= 5}; T = sum(m_ for (w, p), m_ in c.items() if w in keep); pk = collections.Counter()
        for (w, p), m_ in c.items():
            if w in keep: pk[p] += m_
        Hp = -sum(m_ / T * math.log2(m_ / T) for m_ in pk.values())
        return sum(m_ / T * math.log2((m_ / T) / ((wc[w] / T) * (pk[p] / T))) for (w, p), m_ in c.items() if w in keep) / Hp
    lines = [ln for e in E for ln in e if len(ln) >= 3]
    if not lines: obs = float("nan"); nul = [0.0]
    else:
        obs = mi(lines); flat = [w for ln in lines for w in ln]; lens = [len(ln) for ln in lines]; nul = []
    for _ in (range(100) if lines else []):
        f = list(rng.permutation(flat)); LL, j = [], 0
        for m_ in lens: LL.append(f[j:j + m_]); j += m_
        nul.append(mi(LL))
    rep = sum(1 for x in ent for a, b in zip(x, x[1:]) if a == b) / sum(len(x) - 1 for x in ent)
    return dict(entries=k, words=sum(n), M1_words_per_entry_median=float(np.median(n)), M1_cv=round(float(np.std(n) / np.mean(n)), 2), M1_words_per_line=round(len(flat) / len(lines), 2),
                M2_types_in_one_entry_only=round(types_one_entry, 3), M2_median_dispersion_D=round(D, 3), M2_share_of_tokens_entry_specific=round(tok_specific, 3),
                M3_entries_with_own_keyword=round(own / len(top), 3), M3_keyword_in_first_line=round(first_line / len(top), 3), M3_examples=top[:8],
                M4_line_position_excess_MI=round(obs - float(np.mean(nul)), 4), M5_immediate_repetition_rate=round(rep, 4))
