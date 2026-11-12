#!/usr/bin/env python3
"""Voynich herbal pages against a real medieval Latin herbal: Macer Floridus, De viribus herbarum (11th c., 77 chapters,
one plant each, hexameter lines; text from la.wikisource, public domain). The same measures on both, entry = one plant:
  M1 entry length (words)                       M2 how vocabulary spreads across entries (entry-specific words, dispersion)
  M3 the plant-name effect (does each entry have its own keyword; is it in the entry's first line?)
  M4 line-position dependence (excess mutual information, as V2)   M5 immediate repetition of the same word
Latin is inflected, so Macer is also measured with crude stems (first 5 letters). Voynich herbal = pages with $I=H.
Usage: python3 herbal.py <IT2a-n.txt> <macer html>"""
import collections, html, json, math, os, re, sys
import numpy as np
VP, MP = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(77)
# ---------- Voynich herbal pages: list of entries, each a list of lines (word lists)
V, cur, herb = [], None, False
for l in open(VP, encoding="utf-8", errors="replace"):
    m = re.match(r"<(f\w+)>\s+<!(.*)>", l)
    if m: herb = "$I=H" in m.group(2); V.append([]) if herb else None; continue
    m = re.match(r"<(f\w+)\.(\d+),(.)(\w)(\w*)>\s+(.*)", l)
    if not m or not herb or m.group(4) != "P": continue
    txt = re.sub(r"<[^>]*>", "", m.group(6)); txt = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", txt); txt = re.sub(r"\{[^}]*\}", "", txt)
    ws = [w for w in re.split(r"[.,]", txt.replace("!", "").replace("%", "")) if re.fullmatch(r"[a-z]+", w)]
    if ws: V[-1].append(ws)
V = [e for e in V if sum(len(x) for x in e) >= 20]
# ---------- Macer chapters
t = open(MP, encoding="utf-8").read(); body = html.unescape(re.sub(r"<[^>]+>", "\n", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)))
L = [l.strip() for l in body.split("\n") if l.strip()]; start = next(k for k, l in enumerate(L) if l.startswith("I.") and "Artemisia" in l and k > 200)
M, name = [], []
for l in L[start:]:
    if re.match(r"^[IVXLC]+\.\s+\S", l): M.append([]); name.append(l.split(None, 1)[1].strip(". ")); continue
    if l in ("[", "]", "recensere") or re.fullmatch(r"\d+", l) or not M: continue
    if l.startswith("Toggle") or l.startswith("Fontes"): break
    ws = re.findall(r"[a-zà-ÿ]+", l.lower().replace("j", "i").replace("v", "u"))
    if ws: M[-1].append(ws)
M = [e for e in M if e]; MS = [[[w[:5] for w in ln] for ln in e] for e in M]
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
    lines = [ln for e in E for ln in e if len(ln) >= 3]; obs = mi(lines); flat = [w for ln in lines for w in ln]; lens = [len(ln) for ln in lines]; nul = []
    for _ in range(100):
        f = list(rng.permutation(flat)); LL, j = [], 0
        for m_ in lens: LL.append(f[j:j + m_]); j += m_
        nul.append(mi(LL))
    rep = sum(1 for x in ent for a, b in zip(x, x[1:]) if a == b) / sum(len(x) - 1 for x in ent)
    return dict(entries=k, words=sum(n), M1_words_per_entry_median=float(np.median(n)), M1_cv=round(float(np.std(n) / np.mean(n)), 2), M1_words_per_line=round(len(flat) / len(lines), 2),
                M2_types_in_one_entry_only=round(types_one_entry, 3), M2_median_dispersion_D=round(D, 3), M2_share_of_tokens_entry_specific=round(tok_specific, 3),
                M3_entries_with_own_keyword=round(own / len(top), 3), M3_keyword_in_first_line=round(first_line / len(top), 3), M3_examples=top[:8],
                M4_line_position_excess_MI=round(obs - float(np.mean(nul)), 4), M5_immediate_repetition_rate=round(rep, 4))
def truncate(E, n=79):
    out = []
    for e in E:
        lines, k = [], 0
        for ln in e:
            if k >= n: break
            lines.append(ln[: n - k]); k += len(ln)
        out.append(lines)
    return out
R = dict(voynich_herbal=measures(V), macer_words=measures(M), macer_stems=measures(MS), macer_truncated_to_79_words=measures(truncate(M)),
         macer_stems_truncated_to_79=measures(truncate(MS)), macer_plant_names=name[:8])
json.dump(R, open(os.path.join(HERE, "herbal_results.json"), "w"), indent=1, ensure_ascii=False)
keys = [k for k in R["voynich_herbal"] if k.startswith("M") or k in ("entries", "words")]
cols = ["voynich_herbal", "macer_words", "macer_stems", "macer_truncated_to_79_words", "macer_stems_truncated_to_79"]
print(f"{'measure':38s}" + "".join(f"{c[:16]:>17s}" for c in cols))
for k in keys: print(f"{k:38s}" + "".join(f"{str(R[c][k])[:16]:>17s}" for c in cols))
