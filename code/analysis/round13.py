#!/usr/bin/env python3
"""Round 13: separation traced across the sources, against gathering into one.

Fixed word families (Greek):
  SEPARATE: chorizo, diachorizo, aphorizo, schizo / schisma, skorpizo / diaskorpizo, diaireo, merizo, apodiorizo
  GATHER:   synago, episynago, syllego, henotes (unity), henoo / henosis, homothymadon (with one mind)
Hebrew: badal (separate) and yachad (together / the Community's own name) in the Dead Sea Scrolls and the Hebrew Bible.
Rates per 10,000 words in John, the Synoptics, Paul, Genesis 1-11, the whole Septuagint, Philo, the Hermetica,
Plato's Timaeus and Josephus; the share of SEPARATE in (SEPARATE + GATHER) for each.
Then three contrasts: Genesis 1 creation by separating; Philo's 'Logos the Cutter' (logos tomeus); the Community
Rule's separation; and John's own sequence (who separates, who gathers).
Usage: python3 round13.py <sblgnt> <lxx-swete/data> <morphhb/wlc> <greek dir> <dss_scrolls.json>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC, GR, DSS = sys.argv[1:6]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def hc(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת").translate(str.maketrans("ךםןףץ", "כמנפצ"))
SEP = ("χωρισ", "χωριζ", "εχωρισ", "κεχωρισ", "διαχωρ", "διεχωρ", "αφορι", "αφωρι", "σχισ", "εσχισ", "σκορπι", "εσκορπ", "διασκορπ", "διεσκορπ", "διαιρε", "διειλ", "διελ", "μεριζ", "εμερισ", "μεμερισ", "αποδιορ", "σχισμ")
GAT = ("συναγ", "συνηγ", "συνηχθ", "επισυναγ", "συλλεγ", "συνελεξ", "ενοτησ", "ενοτητ", "ενωσισ", "ενωσεω", "ηνωμεν", "ενουσ", "ομοθυμαδ")
def xml(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    return [w for w in (nrm(t) for t in re.sub(r"<[^>]+>", " ", x).split()) if w]
NT = {os.path.basename(f).split("-")[1]: [((int(l[2:4]), int(l[4:6])), nrm(l.split()[4]), l.split()[3]) for l in open(f, encoding="utf-8")] for f in glob.glob(os.path.join(SBL, "*-morphgnt.txt"))}
def lxx(book=None, chs=None):
    ws = []
    for f in glob.glob(os.path.join(LXX, "*.txt")):
        b = os.path.basename(f)[3:-4]
        if (book and b != book) or b.endswith("translatio_Graeca"): continue
        for l in open(f, encoding="utf-8"):
            p = l.split(maxsplit=1)
            if len(p) == 2 and (chs is None or int(p[0].split(".")[1]) in chs): ws += [nrm(t) for t in p[1].split()]
    return [w for w in ws if w]
C = {"John": [w for _, w, _ in NT["Jn"]], "Matthew, Mark, Luke": [w for b in ("Mt", "Mk", "Lk") for _, w, _ in NT[b]], "Paul (Ro, 1-2Co, Ga, Eph)": [w for b in ("Ro", "1Co", "2Co", "Ga", "Eph") for _, w, _ in NT[b]],
     "Genesis 1-11": lxx("Genesis", set(range(1, 12))), "Septuagint (all)": lxx(), "Philo": [w for f in glob.glob(os.path.join(GR, "f1k/data/tlg0018/tlg*/*grc*.xml")) for w in xml(f)],
     "Corpus Hermeticum": [w for f in glob.glob(os.path.join(GR, "f1k/data/tlg1286/tlg*/*grc*.xml")) for w in xml(f)], "Plato, Timaeus": [w for f in glob.glob(os.path.join(GR, "perseus/data/tlg0059/tlg031/*grc*.xml")) for w in xml(f)],
     "Josephus": [w for f in glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml")) for w in xml(f)]}
print("SEPARATE against GATHER (per 10,000 words; share = SEPARATE / (SEPARATE + GATHER))")
rows = {}
for k, ws in C.items():
    s = sum(w.startswith(SEP) for w in ws); g = sum(w.startswith(GAT) for w in ws); rows[k] = dict(sep=1e4 * s / len(ws), gat=1e4 * g / len(ws), share=s / max(1, s + g))
    print(f"   {k:28s} separate {rows[k]['sep']:5.1f}   gather {rows[k]['gat']:5.1f}   share separating {rows[k]['share']:.2f}")
out["rates"] = rows
print("\nCONTRAST 1. Genesis 1: creation by separating (diachorizo)")
g1 = [(int(p[0].split(".")[2]), p[1].strip()) for p in (l.split(maxsplit=1) for l in open(glob.glob(os.path.join(LXX, "*Genesis.txt"))[0], encoding="utf-8")) if len(p) == 2 and p[0].split(".")[1] == "1"]
sepv = sorted({v for v, t in g1 if nrm(t).startswith(("διαχωρ", "διεχωρ"))}); print(f"   verses: Genesis 1:{', 1:'.join(map(str, sepv))}  (light from darkness; waters from waters; day from night)")
print("\nCONTRAST 2. Philo's Logos 'the Cutter' (tomeus)")
ph = " ".join(C["Philo"]); tom = len(re.findall(r"\bτομευ", ph)); lt = len(re.findall(r"λογ\w* τομε|τομε\w* λογ|τομει τω λογω|τω τομει|λογον τομεα|λογω τω τομει", ph))
idx = ph.find("τομευσ"); print(f"   'tomeus' (cutter) in Philo: {tom} times; joined to logos: {lt}.  e.g. …{ph[max(0, idx - 120): idx + 80]}…")
print("\nCONTRAST 3. The Community Rule: separate (badal) and 'together / the Community' (yachad)")
dss = json.load(open(DSS)); qs = [hc(w) for w in dss["1QS"] if w.strip()]; allq = [hc(w) for s in dss.values() for w in s if w.strip()]
hb = [hc(p) for f in glob.glob(os.path.join(WLC, "*.xml")) for w in re.findall(r"<w [^>]*>([^<]+)</w>", open(f, encoding="utf-8").read()) for p in w.split("/")]
def rate(ws, pre): return 1e4 * sum(1 for w in ws if any(w.startswith(p) for p in pre)) / len(ws)
for lab, ws in (("1QS", qs), ("all Scrolls", allq), ("Hebrew Bible", hb)):
    print(f"   {lab:13s} badal (separate) {rate(ws, ('בדל', 'הבדל', 'יבדל', 'נבדל', 'להבדל', 'יבדילו')):5.1f}   yachad (together/the Community) {rate(ws, ('יחד',)):6.1f}   per 10,000")
print("\nJOHN'S OWN SEQUENCE: who separates and who gathers")
for lab, pre in (("separation", SEP), ("gathering", GAT)):
    vs = []
    for (r, w, raw) in NT["Jn"]:
        if w.startswith(pre): vs.append(f"{r[0]}:{r[1]} {raw}")
    print(f"   {lab:10s}: " + "; ".join(vs))
json.dump(out, open(os.path.join(HERE, "round13_results.json"), "w"), ensure_ascii=False, indent=1)
