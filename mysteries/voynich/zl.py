"""Shared loader for the ZL3b-n transliteration (rounds 91+): pages with illustration ($I), language ($L), hand ($H)
and paragraph lines of clean EVA words."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ZL = os.path.join(ROOT, "sources/texts/voynich/ZL3b-n.txt")
PRE = ["qo", "ch", "sh", "ok", "ot", "da", "o", "c", "q", "s", "d", "a"]
SUF = ["aiin", "eedy", "edy", "eey", "iin", "ain", "ody", "chy", "dy", "ey", "ol", "or", "al", "ar", "hy", "in", "y", "n", "l", "r"]
def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@=\-]", "", w).strip()
def load():
    pages = {}; cur = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h:
            d = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))); cur = h.group(1)
            pages[cur] = dict(I=d.get("I"), L=d.get("L"), H=d.get("H"), Q=d.get("Q"), B=d.get("B"), F=d.get("F"), lines=[], paras=[], starts=[]); continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,([@&+*=])P\d*>\s*(.*)", ln)
        if not m or m.group(1) not in pages: continue
        ws = [c for c in (clean(w) for w in re.split(r"[.\s,]+", m.group(3))) if c and re.fullmatch(r"[a-z]+", c)]
        if ws:
            pages[m.group(1)]["lines"].append(ws); pages[m.group(1)]["starts"].append(m.group(2) == "@")
            if m.group(2) == "@": pages[m.group(1)]["paras"].append(ws)
    return pages
def split(w):
    p = next((a for a in PRE if w.startswith(a) and len(w) > len(a)), ""); r = w[len(p):]
    s = next((a for a in SUF if r.endswith(a) and len(r) > len(a)), ""); return p, r[:len(r) - len(s)] if s else r, s
