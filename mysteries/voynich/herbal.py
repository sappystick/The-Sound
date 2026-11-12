#!/usr/bin/env python3
"""Voynich herbal pages against a real medieval Latin herbal: Macer Floridus, De viribus herbarum (11th c., 77 chapters,
one plant each, hexameter lines; text from la.wikisource, public domain). The same measures on both, entry = one plant:
  M1 entry length (words)                       M2 how vocabulary spreads across entries (entry-specific words, dispersion)
  M3 the plant-name effect (does each entry have its own keyword; is it in the entry's first line?)
  M4 line-position dependence (excess mutual information, as V2)   M5 immediate repetition of the same word
Latin is inflected, so Macer is also measured with crude stems (first 5 letters). Voynich herbal = pages with $I=H.
Usage: python3 herbal.py <IT2a-n.txt> <macer html>"""
import collections, html, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
from textmeasures import words, measures
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
