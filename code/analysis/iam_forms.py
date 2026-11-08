#!/usr/bin/env python3
"""The form of 'I am' (ego eimi) across Greek corpora: what follows it?
Classes: 'I am + the + noun' (John's 'I am the bread / light / door / way'); 'I am + name or title without article'
(the Isis-hymn form 'I am Isis, ruler of every land'; the Hermetica's 'I am Poimandres'); 'I am + Lord / God' (the
Septuagint's 'I am the Lord'); absolute 'I am' (end of clause: 'before Abraham was, I am'); other.
The Isis aretalogies (Kyme, Andros, Ios) could not be fetched in this session (sites outside the network allowance);
their published form is 'ego Isis eimi he tyrannos pases choras' (name first, then a title).
Usage: python3 iam_forms.py <sblgnt> <lxx-swete/data> <greek dir> <pgm.txt>
"""
import collections, glob, os, re, sys, unicodedata
SBL, LXX, GR, PGM = sys.argv[1:5]
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def raw_xml(p):
    x = open(p, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); return re.sub(r"<[^>]+>", " ", x).split()
C = {"John": [l.split()[3] for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8")],
     "Matthew, Mark, Luke": [l.split()[3] for c in ("Mt", "Mk", "Lk") for l in open(glob.glob(os.path.join(SBL, f"*-{c}-*"))[0], encoding="utf-8")],
     "Septuagint": [t for f in glob.glob(os.path.join(LXX, "*.txt")) for l in open(f, encoding="utf-8") for p in [l.split(maxsplit=1)] if len(p) == 2 for t in p[1].split()],
     "Corpus Hermeticum": [t for f in glob.glob(os.path.join(GR, "f1k/data/tlg1286/tlg*/*grc*.xml")) for t in raw_xml(f)],
     "Philo": [t for f in glob.glob(os.path.join(GR, "f1k/data/tlg0018/tlg*/*grc*.xml")) for t in raw_xml(f)],
     "Josephus": [t for f in glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml")) for t in raw_xml(f)],
     "Magical Papyri (PGM I, II)": open(PGM, encoding="utf-8").read().split() if os.path.exists(PGM) else []}
ART = {"ο", "η", "το", "οι"}; DIV = {"κυριοσ", "θεοσ", "ο", "κυριε"}
for lab, toks in C.items():
    ws = [nrm(t) for t in toks]; c = collections.Counter(); ex = collections.defaultdict(list)
    for i in range(len(ws) - 2):
        a, b = ws[i], ws[i + 1]
        if (a == "εγω" and b == "ειμι") or (a == "ειμι" and b == "εγω"):
            nxt = [w for w in ws[i + 2:i + 5] if w]; ends = bool(re.search(r"[.,;·]$", toks[i + 1]))
            if ends or not nxt: k = "absolute 'I am'"
            elif nxt[0] in ART and len(nxt) > 1 and nxt[1] in ("κυριοσ", "θεοσ"): k = "'I am the Lord/God'"
            elif nxt[0] in ("κυριοσ", "θεοσ"): k = "'I am the Lord/God'"
            elif nxt[0] in ART: k = "'I am the + noun'"
            elif toks[i + 2][:1].isupper(): k = "'I am + Name' (Isis form)"
            else: k = "other"
            c[k] += 1
            if len(ex[k]) < 3: ex[k].append(" ".join(toks[i:i + 5]))
        if a == "εγω" and i + 2 < len(ws) and toks[i + 1][:1].isupper() and ws[i + 2] == "ειμι":
            c["'I, Name, am' (Isis form)"] += 1; ex["'I, Name, am' (Isis form)"].append(" ".join(toks[i:i + 5]))
    tot = sum(c.values()) or 1
    print(f"{lab:28s} total {tot:4d}: " + "; ".join(f"{k} {v} ({v / tot:.0%})" for k, v in c.most_common()))
    for k in ("'I am the + noun'", "'I am + Name' (Isis form)", "'I, Name, am' (Isis form)"):
        if ex[k]: print(f"      e.g. {k}: " + " | ".join(ex[k]))
