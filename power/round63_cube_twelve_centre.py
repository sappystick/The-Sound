#!/usr/bin/env python3
"""Round 63. The cube, the twelve and the centre mapped across the sacred and related corpora in the repo.
Greek: LXX (Swete), NT (SBLGNT), Philo, Josephus, Corpus Hermeticum, Clement, Irenaeus, Ignatius, Hermas, Eusebius,
Orphica, Plato's Timaeus. Hebrew: WLC (consonants).
Motifs (normalised word forms): TWELVE dodek-; CUBE/SQUARE kyb-, tetragon-; CENTRE the forms of mesos ('in the
middle'; not mesites, mesembria, Messias). Hebrew: twelve (shnem/shtem asar); square (ravua); centre (betokh/tokh).
Output: rates per 10,000 words per corpus, and the Bible chapters where all three motifs meet.
Usage: python3 power/round63_cube_twelve_centre.py
"""
import collections, glob, json, os, re, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); T = os.path.join(ROOT, "sources/texts")
def bare(t): t = unicodedata.normalize("NFD", t.lower()); return re.sub(r"[^α-ω]", "", "".join(c for c in t if not unicodedata.combining(c)).replace("ς", "σ"))
MESOS = {"μεσοσ", "μεσου", "μεσω", "μεσον", "μεση", "μεσησ", "μεσοι", "μεσων", "μεσα", "μεσοισ", "μεσασ", "μεσαισ", "αναμεσον", "μεσαι"}
def motif(w):
    if w.startswith("δωδεκ"): return "twelve"
    if w.startswith(("κυβ", "τετραγων")): return "cube/square"
    if w in MESOS: return "centre"
    return None
def xml_words(paths):
    for p in paths:
        t = re.sub(r"<[^>]+>", " ", open(p, encoding="utf-8").read())
        for w in t.split():
            b = bare(w)
            if b: yield b
CORPORA = {"Philo": glob.glob(os.path.join(T, "f1k/data/tlg0018/*/*grc*.xml")), "Josephus": glob.glob(os.path.join(T, "perseus/data/tlg0526/*/*grc*.xml")),
           "Corpus Hermeticum": glob.glob(os.path.join(T, "f1k/data/tlg1286/*/*grc*.xml")), "Clement of Alexandria": glob.glob(os.path.join(T, "f1k/data/tlg0555/*/*grc*.xml")),
           "Irenaeus": glob.glob(os.path.join(T, "f1k/data/tlg1447/*/*grc*.xml")), "Ignatius": glob.glob(os.path.join(T, "f1k/data/tlg1443/*/*grc*.xml")),
           "Hermas": glob.glob(os.path.join(T, "f1k/data/tlg1139/*/*grc*.xml")), "Eusebius": glob.glob(os.path.join(T, "f1k/data/tlg2018/*/*grc*.xml")),
           "Orphica": glob.glob(os.path.join(T, "f1k/data/tlg0579/*/*grc*.xml")), "Plato, Timaeus": glob.glob(os.path.join(T, "perseus/data/tlg0059/tlg031/*grc*.xml"))}
rates = {}
def tally(name, words):
    c = collections.Counter(); n = 0
    for w in words:
        n += 1; m = motif(w)
        if m: c[m] += 1
    if n: rates[name] = dict(words=n, **{k: round(1e4 * c[k] / n, 2) for k in ("twelve", "cube/square", "centre")})
# Bible, per chapter
chap = collections.defaultdict(collections.Counter); nwords = collections.Counter()
for f in sorted(glob.glob(os.path.join(T, "lxx-swete/data/*.txt"))):
    b = os.path.basename(f)[3:-4]
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2:
            w = bare(p[1]); key = ("OT (LXX)", b, p[0].split(".")[1]); nwords["OT (LXX)"] += 1
            m = motif(w)
            if m: chap[key][m] += 1
for f in sorted(glob.glob(os.path.join(T, "sblgnt/*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for l in open(f, encoding="utf-8"):
        p = l.split(); w = bare(p[3]); key = ("NT", b, str(int(p[0][2:4]))); nwords["NT"] += 1
        m = motif(w)
        if m: chap[key][m] += 1
for corp in ("OT (LXX)", "NT"):
    tot = collections.Counter()
    for k, c in chap.items():
        if k[0] == corp: tot.update(c)
    rates[corp] = dict(words=nwords[corp], **{m: round(1e4 * tot[m] / nwords[corp], 2) for m in ("twelve", "cube/square", "centre")})
for name, paths in CORPORA.items():
    if paths: tally(name, xml_words(paths))
# Hebrew Bible
heb = collections.Counter(); hn = 0; hchap = collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(os.path.join(T, "morphhb/wlc/*.xml"))):
    t = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<verse osisID="([^.]+)\.(\d+)\.\d+">(.*?)</verse>', t, re.S):
        ws = [re.sub(r"[^א-ת]", "", re.sub(r"<[^>]+>", "", w)) for w in re.findall(r"<w[^>]*>(.*?)</w>", m.group(3))]
        for i, w in enumerate(ws):
            hn += 1; nx = ws[i + 1] if i + 1 < len(ws) else ""
            if w in ("שנים", "שתים", "שני", "שתי") and nx in ("עשר", "עשרה"): heb["twelve"] += 1; hchap[(m.group(1), m.group(2))]["twelve"] += 1
            if w in ("רבוע", "רבועה", "מרבע", "רבעים", "רבעיו"): heb["cube/square"] += 1; hchap[(m.group(1), m.group(2))]["cube/square"] += 1
            if w in ("בתוך", "תוך", "מתוך", "לתוך", "בתוכו", "בתוכם", "בתוכה", "בתוככם"): heb["centre"] += 1; hchap[(m.group(1), m.group(2))]["centre"] += 1
rates["Hebrew Bible (WLC)"] = dict(words=hn, **{k: round(1e4 * heb[k] / hn, 2) for k in ("twelve", "cube/square", "centre")})
meet = sorted([(f"{k[0]} {k[1]} {k[2]}", dict(c)) for k, c in chap.items() if all(c[m] for m in ("twelve", "cube/square", "centre"))], key=lambda x: -sum(x[1].values()))
hmeet = sorted([(f"{k[0]} {k[1]}", dict(c)) for k, c in hchap.items() if all(c[m] for m in ("twelve", "cube/square", "centre"))], key=lambda x: -sum(x[1].values()))
out = dict(rates_per_10k=rates, greek_bible_chapters_with_all_three=meet, hebrew_chapters_with_all_three=hmeet)
json.dump(out, open(os.path.join(HERE, "round63_results.json"), "w"), ensure_ascii=False, indent=1)
for k, v in sorted(rates.items(), key=lambda kv: -(kv[1]["twelve"] + kv[1]["cube/square"] + kv[1]["centre"])): print(f"{k:<24} {v}")
print("Greek chapters with all three:", meet); print("Hebrew chapters with all three:", hmeet)
