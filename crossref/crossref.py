#!/usr/bin/env python3
"""Cross-reference the lenses across every source: rate per 10,000 words of each lens's key Greek words in each
corpus, and the lens profile of John against them. Output: crossref/crossref.csv.
Usage: python3 crossref.py <texts dir from sources/fetch_sources.sh>
"""
import collections, csv, glob, os, re, sys, unicodedata
T = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def xml(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    return [w for w in (nrm(t) for t in re.sub(r"<[^>]+>", " ", x).split()) if w]
LENS = {"light": ("φωσ", "φωτ", "λαμπ", "λυχν", "αυγ"), "water": ("υδωρ", "υδατ", "ποταμ", "πηγ", "θαλασσ"), "breath / spirit": ("πνευμ", "πνοη", "πνε", "ψυχ"),
        "word / ratio": ("λογο", "λογω", "λογον", "αναλογ"), "number": ("αριθμ", "μοναδ", "δυαδ", "τριαδ", "εβδομ", "δεκαδ"), "geometry / measure": ("μετρ", "κυκλ", "σφαιρ", "τριγων", "τετραγων", "γωνι"),
        "harmony / music": ("αρμον", "μουσικ", "ωδη", "υμν", "φωνη", "ηχ"), "temple / priest": ("ναο", "ιερε", "αρχιερ", "σκην", "θυσια"), "stones / materials": ("λιθ", "χρυσ", "αργυρ", "χαλκ", "ξυλ"),
        "healing / purity": ("θεραπ", "ιασ", "ιατρ", "υγι", "καθαρ", "αγν"), "life": ("ζωη", "ζων", "ζω"), "time / heavens": ("ωρα", "ουραν", "αστερ", "ηλιο", "σεληνη", "νυξ", "νυκτ")}
C = {}
def add(name, files):
    ws = [w for f in files for w in xml(f)]
    if ws: C[name] = ws
C["John"] = [nrm(l.split()[4]) for l in open(glob.glob(os.path.join(T, "sblgnt", "*-Jn-*"))[0], encoding="utf-8")]
C["Synoptics"] = [nrm(l.split()[4]) for f in glob.glob(os.path.join(T, "sblgnt", "*-M[tk]-*")) + glob.glob(os.path.join(T, "sblgnt", "*-Lk-*")) for l in open(f, encoding="utf-8")]
for lab, pat in (("Philo", "f1k/data/tlg0018"), ("Corpus Hermeticum", "f1k/data/tlg1286"), ("Eusebius", "f1k/data/tlg2018/tlg002"), ("Irenaeus", "f1k/data/tlg1447"),
                 ("Josephus", "perseus/data/tlg0526/tlg001"), ("Homeric Hymns", "perseus/data/tlg0013"), ("Plato, Timaeus", "perseus/data/tlg0059/tlg031"),
                 ("Euclid", "perseus/data/tlg1799"), ("Hippocrates", "perseus/data/tlg0627"), ("Aristotle", "perseus/data/tlg0086")):
    add(lab, glob.glob(os.path.join(T, pat, "**", "*grc*.xml"), recursive=True))
rows = []
for name, ws in C.items():
    n = len(ws); row = {"corpus": name, "words": n}
    for lens, pre in LENS.items(): row[lens] = round(1e4 * sum(w.startswith(pre) for w in ws) / n, 1)
    rows.append(row)
with open(os.path.join(HERE, "crossref.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"{'corpus':18s} {'words':>8s} " + " ".join(f"{k[:9]:>9s}" for k in LENS))
for r in rows: print(f"{r['corpus']:18s} {r['words']:8d} " + " ".join(f"{r[k]:9.1f}" for k in LENS))
