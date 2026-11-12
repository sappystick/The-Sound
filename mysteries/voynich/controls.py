#!/usr/bin/env python3
"""Further controls for the Voynich herbal comparison (round 77).
C1 a PROSE herbal: Platearius, Circa instans (12th c., Salerno), from the 1582 Lyon print (archive.org
   BIUSante_pharma_res012103, OCR). Entries are split at the opening formula every chapter uses
   ("X calida/frigida est et sicca/humida ..."); print lines are prose wraps (so line position should be uninformative).
C2 a RECIPE book: Apicius, De re coquinaria, books 1-5 (The Latin Library); one recipe = one entry.
C3 the Voynich PHARMACEUTICAL pages ($I=P): do the labels beside the drawings name things the page text talks about?
   Compared with real headings: Macer's chapter titles and Circa instans's entry names, inside their own entry.
OCR normalisation for 1582 type: long s read as f is mapped to s; u/v and i/j merged; line-end hyphens joined.
Usage: python3 controls.py <IT2a-n.txt> <macer html> <circa ocr txt> <apicius html dir>"""
import collections, glob, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from textmeasures import measures, words
VP, MP, CP, AD = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__))
def latin(ws): return [w.replace("j", "i").replace("v", "u") for w in ws]
# ---------- C1 Circa instans
raw = open(CP, encoding="utf-8", errors="replace").read().split("\n")
end = max(i for i, l in enumerate(raw) if "Finit" in l and "lateari" in l) if any("Finit" in l and "lateari" in l for l in raw) else len(raw)
lines = raw[43000:end]; txt, joined = [], ""
for l in lines:
    l = l.strip()
    if not l: continue
    l = l.replace("ſ", "s")
    if joined: l = joined + l; joined = ""
    if l.endswith(("¬", "-")): joined = l[:-1]; continue
    txt.append(l)
STOP = re.compile(r"(Contra|Cotra|Ad|Item|Et|Nota|Si|Cum|In|Valet|Syrup|Horae|Cbii|Quia|Vel|Aliter)", re.I)
def chapter_start(l):
    """A chapter opens with the simple's name (often with its dropped capital split off) and, within the first four
    words, its quality: calida / frigida ... (OCR of 1582 type)."""
    toks = l.split()
    return bool(toks) and l[0].isupper() and not STOP.match(l) and any(re.match(r"(calid|frigid)", t_, re.I) for t_ in toks[:4]) and \
        any(re.match(r"(e[fs][tl]|&|Sc|funt|sunt|in)$", t_.strip(":,."), re.I) for t_ in toks[1:6])
C, cur = [], None
for l in txt:
    if chapter_start(l): cur = []; C.append(cur)
    if cur is None: continue
    ws = latin([w.lower().replace("f", "s") for w in re.findall(r"[A-Za-z]+", l) if len(w) > 1 or w.lower() in "aeo"])
    if ws: cur.append(ws)
C = [e for e in C if sum(len(x) for x in e) >= 20]
# ---------- C2 Apicius
A = []
for f in sorted(glob.glob(os.path.join(AD, "apicius*.html"))):
    t = html.unescape(re.sub(r"<[^>]+>", "\n", open(f, encoding="utf-8", errors="replace").read()))
    for l in [x.strip() for x in t.split("\n") if x.strip()]:
        if re.match(r"^\d+\.\s+[A-Z]", l): A.append([]); continue
        if A and not re.match(r"^[IVXL]+\.\s", l):
            ws = latin(re.findall(r"[a-z]+", l.lower()))
            if ws: A[-1].append(ws)
A = [e for e in A if sum(len(x) for x in e) >= 15]
# ---------- Voynich herbal (as round 76) and pharmaceutical pages with labels
def voy(kind):
    pages, cur, ok = [], None, False
    for l in open(VP, encoding="utf-8", errors="replace"):
        m = re.match(r"<(f\w+)>\s+<!(.*)>", l)
        if m: ok = f"$I={kind}" in m.group(2); cur = dict(page=m.group(1), text=[], labels=[]) if ok else None; pages.append(cur) if ok else None; continue
        m = re.match(r"<(f\w+)\.(\d+),(.)(\w)(\w*)>\s+(.*)", l)
        if not m or cur is None: continue
        t_ = re.sub(r"<[^>]*>", "", m.group(6)); t_ = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", t_); t_ = re.sub(r"\{[^}]*\}", "", t_)
        ws = [w for w in re.split(r"[.,]", t_.replace("!", "").replace("%", "")) if re.fullmatch(r"[a-z]+", w)]
        if not ws: continue
        if m.group(4) == "P": cur["text"].append(ws)
        elif m.group(4) == "L": cur["labels"] += ws
    return pages
VH = [p["text"] for p in voy("H") if sum(len(x) for x in p["text"]) >= 20]
PH = voy("P")
def truncate(E, n=79):
    out = []
    for e in E:
        lines_, k = [], 0
        for ln in e:
            if k >= n: break
            lines_.append(ln[: n - k]); k += len(ln)
        out.append(lines_)
    return out
R = {"circa_instans_prose_herbal": measures(C), "circa_first_79_words": measures(truncate(C)), "apicius_recipes": measures(A), "voynich_herbal": measures(VH)}
R["entries"] = dict(circa=len(C), apicius=len(A), voynich_herbal=len(VH),
                   note="Circa instans has about 270 chapters; the OCR splitter finds fewer, so some entries merge 2-3 simples (this LOWERS the own-keyword share: a conservative control). Apicius recipes are single paragraphs, so its line measures (M1 words per line, M4) do not apply.")
# ---------- C3 labels
all_text = collections.Counter(w for p in voy("H") + PH + voy("B") + voy("S") + voy("C") + voy("A") + voy("Z") + voy("T") for x in p["text"] for w in x)
lab = [(p["page"], w, set(w2 for x in p["text"] for w2 in x)) for p in PH for w in p["labels"]]
in_own = sum(1 for _, w, own in lab if w in own); in_any = sum(1 for _, w, own in lab if all_text[w] > 0)
labcount = collections.Counter(w for _, w, _ in lab)
# chance baseline: random words drawn from OTHER pages' text, used as pseudo-labels on each pharmaceutical page
rng_ = np.random.default_rng(78); other = [(p["page"], w) for p in voy("H") + voy("B") + voy("S") for x in p["text"] for w in x]
base = []
for _ in range(200):
    hit = 0
    for pg, w, own in lab:
        ww = other[rng_.integers(len(other))][1]; hit += ww in own
    base.append(hit / len(lab))
base_len = []
for _ in range(200):     # length-matched baseline: random text words of the same length as each label
    hit = 0
    for pg, w, own in lab:
        pool = [x for _, x in other[:20000] if len(x) == len(w)] or [w]; ww = pool[rng_.integers(len(pool))]; hit += ww in own
    base_len.append(hit / len(lab))
voy_lab = dict(labels=len(lab), distinct=len(labcount), in_own_page_text=round(in_own / len(lab), 3), in_any_text_of_the_manuscript=round(in_any / len(lab), 3),
               label_used_once=round(sum(1 for w, c in labcount.items() if c == 1) / len(labcount), 3),
               chance_random_text_word_in_page_text=round(float(np.mean(base)), 3), chance_length_matched=round(float(np.mean(base_len)), 3),
               p_labels_as_rare_or_rarer_than_length_matched_chance=round(float(np.mean(np.array(base_len) <= in_own / len(lab))), 3),
               mean_label_length_letters=round(float(np.mean([len(w) for _, w, _ in lab])), 2), mean_text_word_length=round(float(np.mean([len(w) for w in all_text.elements()])), 2))
# real headings: Macer titles inside their chapters (stem match, 5 letters); Circa entry names (first word) inside their own entry beyond the first line
t = open(MP, encoding="utf-8").read(); body = html.unescape(re.sub(r"<[^>]+>", "\n", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)))
Ls = [l.strip() for l in body.split("\n") if l.strip()]; st = next(k for k, l in enumerate(Ls) if l.startswith("I.") and "Artemisia" in l and k > 200)
chap, title = [], []
for l in Ls[st:]:
    if re.match(r"^[IVXLC]+\.\s+\S", l): title.append(latin([l.split(None, 1)[1].strip(". ").lower()])[0]); chap.append([]); continue
    if l.startswith("Toggle"): break
    if chap and not re.fullmatch(r"\d+|\[|\]|recensere", l): chap[-1] += latin(re.findall(r"[a-zà-ÿ]+", l.lower()))
mac_in = sum(1 for ti, ch in zip(title, chap) if any(w[:5] == ti.split()[0][:5] for w in ch))
def name_match(w, n):     # the 1582 OCR often drops a chapter's initial capital ("loes" for "aloes"): allow a one-letter offset
    return len(n) >= 3 and (w[:5] == n[:5] or w[1:6] == n[:5] or w[:5] == n[1:6])
circ_in = sum(1 for e in C if e and e[0] and any(name_match(w, e[0][0]) for x in e[1:] for w in x))
R["labels_and_headings"] = dict(voynich_pharmaceutical_labels=voy_lab,
    macer_title_named_in_own_chapter=round(mac_in / len(title), 3), circa_entry_name_repeated_in_own_entry=round(circ_in / len(C), 3))
json.dump(R, open(os.path.join(HERE, "controls_results.json"), "w"), indent=1, ensure_ascii=False)
cols = ["voynich_herbal", "circa_instans_prose_herbal", "circa_first_79_words", "apicius_recipes"]
keys = [k for k in R["voynich_herbal"] if k.startswith("M") and k != "M3_examples"]
print(f"{'measure':38s}" + "".join(f"{c[:18]:>20s}" for c in cols))
for k in ["entries", "words"] + keys: print(f"{k:38s}" + "".join(f"{str(R[c].get(k))[:18]:>20s}" for c in cols))
print("examples:", {c: R[c]["M3_examples"][:6] for c in cols})
print(json.dumps(R["labels_and_headings"], indent=1, ensure_ascii=False))
