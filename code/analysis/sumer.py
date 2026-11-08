#!/usr/bin/env python3
"""Sumerian literature (Black, Cunningham, Robson, Zolyomi, The Literature of Ancient Sumer, OUP 2004; English
translations of c. 70 compositions, c. 2100-1700 BC) set beside John and the Hebrew Bible in English (KJV, public domain).
The book's text is not stored in the repository (copyright); only counts and short references are.

 1. MOTIFS (fixed list) per 10,000 words in the Sumerian compositions and in English John, Genesis, Psalms and the
    Synoptics: water of life, food/plant/bread of life, three days and three nights, shepherd, sheepfold, word
    (that creates or decrees), light, darkness, breath, life, garden, tree, fish/net, temple, door/gate, 'I am'.
 2. WHICH COMPOSITIONS carry which motifs (the strongest links per motif), with the lines.
 3. 'I AM' SELF-PRAISE: first-person 'I am' chains in the royal and divine praise poems (Sulgi, Inana, Lipit-Estar)
    against John and the Psalms.
 4. INDEPENDENT: refrain density (lines repeated within a composition), the sign of oral performance, in Sumerian
    poems against John and the Psalms (KJV verses).
Usage: python3 sumer.py <literature txt> <KJV.csv>
"""
import collections, csv, json, os, re, sys
import numpy as np
LIT, KJV = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
T = open(LIT, encoding="utf-8", errors="ignore").read()
toc = T[T.find("CONTENTS"): T.find("CONTENTS") + 9000]
titles = [re.sub(r"\s+", " ", m.group(1)).strip() for m in (re.match(r"\s+([A-Z][^\n]{4,60}?)\s+(\d{1,3})\s*$", ln) for ln in toc.split("\n")) if m]
titles = [t for t in titles if not t.isupper() and "Further reading" not in t and "List of" not in t and "How to" not in t and "Chronological" not in t]
body = T[T.find("CONTENTS") + 9000:]
starts = []
for t in titles:
    m = None
    for mm in re.finditer(r"\n\s*" + re.escape(t) + r"\s*\n", body): m = mm; break
    if m: starts.append((m.start(), t))
starts.sort(); COMP = collections.OrderedDict()
for (a, t), nxt in zip(starts, starts[1:] + [(len(body), None)]):
    seg = body[a:nxt[0]]; lines = [re.sub(r"^\s*\d+\s+", "", l).strip() for l in seg.split("\n")]
    COMP[t] = [l for l in lines if len(l.split()) >= 3]
print(f"{len(COMP)} compositions located; {sum(len(' '.join(v).split()) for v in COMP.values()):,} words")
K = collections.defaultdict(list)
for r in csv.DictReader(open(KJV, encoding="utf-8")): K[r["Book"]].append(r["Text"])
ENG = {"John (KJV)": K["John"], "Genesis (KJV)": K["Genesis"], "Psalms (KJV)": K["Psalms"], "Matthew, Mark, Luke (KJV)": K["Matthew"] + K["Mark"] + K["Luke"]}
MOT = {"water of life / living water": r"water of life|living water|waters? of life|life-giving water", "food / plant / bread of life": r"(food|plant|bread|grass) of life|life-giving plant",
       "three days and three nights": r"three days and three nights", "shepherd": r"shepherd", "sheepfold / fold": r"sheepfold|\bfolds?\b|\bpens?\b",
       "word (decree)": r"\bword\b|\bwords\b", "light": r"\blight\b", "darkness": r"\bdark(ness)?\b", "breath": r"\bbreath", "life": r"\blife\b",
       "garden": r"\bgardens?\b", "tree": r"\btrees?\b", "fish / net": r"\bfish|\bnets?\b", "temple": r"\btemples?\b", "door / gate": r"\bdoors?\b|\bgates?\b", "'I am'": r"\bI am\b"}
def rates(text):
    n = len(text.split()); return {k: 1e4 * len(re.findall(p, text, flags=re.I if k != "'I am'" else 0)) / n for k, p in MOT.items()}
sumer_all = " ".join(" ".join(v) for v in COMP.values())
R = {"Sumerian literature": rates(sumer_all)}; R.update({k: rates(" ".join(v)) for k, v in ENG.items()})
print(f"\n1. MOTIFS per 10,000 words\n{'motif':32s}" + "".join(f"{k[:14]:>16s}" for k in R))
for m in MOT: print(f"{m:32s}" + "".join(f"{R[k][m]:16.1f}" for k in R))
out["rates"] = R
print("\n2. WHERE THE SHARED MOTIFS SIT IN SUMERIAN LITERATURE")
for m in ("water of life / living water", "food / plant / bread of life", "three days and three nights", "shepherd", "'I am'", "word (decree)"):
    hits = [(t, len(re.findall(MOT[m], " ".join(v), flags=re.I if m != "'I am'" else 0))) for t, v in COMP.items()]
    hits = sorted([h for h in hits if h[1]], key=lambda h: -h[1])[:5]
    print(f"   {m:30s} " + "; ".join(f"{t} ({n})" for t, n in hits))
    out.setdefault("where", {})[m] = hits
for t in COMP:
    if t.startswith("Inana’s descent") or t.startswith("Inana's descent"):
        txt = " ".join(COMP[t])
        for pat in (r"three days and three nights", r"(food|plant) of life", r"water of life"):
            for mm in list(re.finditer(pat, txt, flags=re.I))[:2]: print(f"   Inana's descent: …{txt[max(0, mm.start() - 110): mm.end() + 90]}…")
print("\n3. 'I AM' SELF-PRAISE (per 1,000 words)")
for t in [t for t in COMP if re.search(r"praise poem|exaltation|hymn to Inana", t)]:
    txt = " ".join(COMP[t]); n = len(txt.split()); print(f"   {t:40s} 'I am' {1000 * len(re.findall(r'\bI am\b', txt)) / n:5.1f}   first-person 'I' {1000 * len(re.findall(r'\bI\b', txt)) / n:5.1f}")
for k in ("John (KJV)", "Psalms (KJV)"):
    txt = " ".join(ENG[k]); n = len(txt.split()); print(f"   {k:40s} 'I am' {1000 * len(re.findall(r'\bI am\b', txt)) / n:5.1f}   first-person 'I' {1000 * len(re.findall(r'\bI\b', txt)) / n:5.1f}")
print("\n4. REFRAINS (share of lines whose 6-word opening recurs inside the same composition / book)")
def refrain(lines):
    keys = [" ".join(re.findall(r"[a-z']+", l.lower())[:6]) for l in lines]; keys = [k for k in keys if len(k.split()) == 6]; c = collections.Counter(keys)
    return np.mean([c[k] > 1 for k in keys]) if keys else 0
sr = [refrain(v) for v in COMP.values() if len(v) > 40]
print(f"   Sumerian compositions: mean {np.mean(sr):.1%} (median {np.median(sr):.1%}); most refrain-heavy: " + ", ".join(f"{t} {refrain(v):.0%}" for t, v in sorted(COMP.items(), key=lambda kv: -refrain(kv[1]))[:4]))
for k, v in ENG.items(): print(f"   {k:28s} {refrain(v):.1%}")
json.dump(out, open(os.path.join(HERE, "sumer_results.json"), "w"), indent=1)
