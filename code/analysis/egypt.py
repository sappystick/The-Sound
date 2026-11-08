#!/usr/bin/env python3
"""Egyptian texts (public domain, Project Gutenberg): The Egyptian Book of the Dead (Le Page Renouf, ebook 69566) and
Egyptian Literature (anthology, ebook 28282), against John (KJV) and Sulgi / Isis (rounds 18, 20).
'I am' forms: what follows 'I am' (the / a / name / he); the nouns after 'I am the'; whether John's seven images
(bread, light, door/gate, shepherd, resurrection, way, vine) occur as 'I am the …' in the Egyptian texts; motif rates.
Usage: python3 egypt.py <pg69566.txt> <pg28282.txt> <KJV.csv>"""
import collections, csv, re, sys
BOD, LIT, KJV = sys.argv[1:4]
def body(p):
    t = open(p, encoding="utf-8", errors="ignore").read(); a = t.find("*** START"); b = t.find("*** END"); return t[a:b]
J = " ".join(r["Text"] for r in csv.DictReader(open(KJV, encoding="utf-8")) if r["Book"] == "John")
T = {"Book of the Dead": body(BOD), "Egyptian Literature": body(LIT), "John (KJV)": J}
IMG = ["bread", "light", "door", "gate", "shepherd", "resurrection", "way", "vine", "life", "truth"]
for lab, t in T.items():
    n = len(t.split()); iam = re.findall(r"\bI am (the|a|an|he|[A-Z][a-z]+|[a-z]+)\b", t)
    c = collections.Counter("Name" if (w[0].isupper() and w not in ("I",)) else w.lower() for w in iam)
    nouns = collections.Counter(m.group(1).lower() for m in re.finditer(r"\bI am the ((?:[A-Za-z]+ ){0,2}?[A-Za-z]+?)\b(?: of| who| which|,|\.|;|$)", t))
    imgs = {w: len(re.findall(rf"\bI am the (?:\w+ )?{w}\b", t, flags=re.I)) for w in IMG}
    print(f"{lab:22s} words {n:7d}  'I am' {len(iam):4d} ({1000 * len(iam) / n:.1f}/1000)  forms: {dict(c.most_common(6))}")
    print(f"   'I am the …' commonest: {[w for w, _ in nouns.most_common(14)]}")
    print(f"   John's images as 'I am the (…) X': { {k: v for k, v in imgs.items() if v} }")
    for w in ("light", "way", "door", "gate", "bread", "water"): 
        ex = [re.sub(r"\s+", " ", t[max(0, m.start() - 40): m.end() + 60]) for m in re.finditer(rf"\bI am (the )?(\w+ )?{w}\b", t, flags=re.I)][:2]
        if ex and lab != "John (KJV)": print(f"      e.g. {w}: " + " | ".join(ex))
