#!/usr/bin/env python3
"""The high-priest thread: John's seamless tunic, the breastplate stones, the robe of the cosmos.

Sources: Swete LXX, SBLGNT, Josephus' Antiquities (Perseus, Greek), Philo (First1KGreek, Greek).
 1. 'Robe to the feet' (poderes) and the high priest in the Greek OT and the NT.
 2. The twelve stones: Exodus 28:17-20 (Greek) against Revelation 21:19-20 and Ezekiel 28:13 (Eden).
 3. Josephus and Philo: the seamless tunic, the robe as the cosmos, the Logos as high priest, the garment
    that must not be torn (Lev 21:10), matched against John 19:23-24.
 4. Wisdom 18: the midnight Word (18:14-16) and Aaron's robe 'on which was the whole world' (18:24) in one
    chapter.
Usage: python3 high_priest.py <sblgnt dir> <lxx-swete/data> <josephus Ant xml> <philo data dir>
"""
import collections, glob, json, os, re, sys, unicodedata
SBL, LXX, JOS, PHILO = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω ]", "", w.replace("ς", "σ"))
LX = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); LX.setdefault(f"{b} {r[1]}:{r[2]}", []).append(p[1].strip())
NT = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for l in open(f, encoding="utf-8"):
        p = l.split(); NT.setdefault(f"{b} {int(p[0][2:4])}:{int(p[0][4:6])}", []).append((p[3], nrm(p[6])))
def lx(ref): return " ".join(LX.get(ref, []))
def nt(ref): return " ".join(t for t, _ in NT.get(ref, []))

print("1. 'ROBE TO THE FEET' (poderes) AND THE HIGH PRIEST")
pod_lxx = [r for r, ws in LX.items() if any(nrm(w).startswith("ποδηρ") for w in ws)]
pod_nt = [r for r, ws in NT.items() if any(l.startswith("ποδηρ") for _, l in ws)]
print("   Greek OT:", ", ".join(pod_lxx)); print("   NT:", ", ".join(pod_nt), "->", nt(pod_nt[0]) if pod_nt else "")
hp = collections.Counter(r.split()[0] for r, ws in NT.items() for _, l in ws if l == "αρχιερευσ")
print("   'high priest' in the NT by book:", dict(hp.most_common()))
print("   John 19:23-24:", nt("Jn 19:23"), nt("Jn 19:24"))
out["poderes"] = dict(lxx=pod_lxx, nt=pod_nt, high_priest_by_book=dict(hp))

print("\n2. THE TWELVE STONES")
STONE = {"σαρδιον": "sardius", "τοπαζιον": "topaz", "σμαραγδοσ": "emerald", "ανθραξ": "carbuncle", "σαπφ": "sapphire", "ιασπισ": "jasper",
         "λιγυριον": "ligure", "αχατησ": "agate", "αμεθυστοσ": "amethyst", "χρυσολιθοσ": "chrysolite", "βηρυλλιον": "beryl", "βηρυλλοσ": "beryl", "ονυχιον": "onyx",
         "χαλκηδων": "chalcedony", "σαρδονυξ": "sardonyx", "χρυσοπρασοσ": "chrysoprase", "υακινθοσ": "jacinth"}
def stones(text):
    seq = []
    for w in text.split():
        k = nrm(w).strip()
        for s, e in STONE.items():
            if k.startswith(s[:6] if len(s) > 5 else s) and e not in seq: seq.append(e)
    return seq
ex = stones(" ".join(lx(f"Exodus 28:{v}") for v in range(17, 21))) or stones(" ".join(lx(f"Exodus 36:{v}") for v in range(17, 21)))
re21 = stones(" ".join(nt(f"Re 21:{v}") for v in (19, 20)))
ez = stones(lx("Ezechiel 28:13"))
print("   Exodus 28:17-20 (breastplate):", ex); print("   Revelation 21:19-20 (city foundations):", re21); print("   Ezekiel 28:13 (in Eden, the garden of God):", ez)
sh = [s for s in re21 if s in ex]; print(f"   Revelation shares {len(sh)} of 12 with the breastplate; Ezekiel 28:13 shares {len([s for s in ez if s in ex])} of {len(ez)}")
print("   Ezekiel 28:13 (Greek):", lx("Ezechiel 28:13")[:400])
out["stones"] = dict(exodus=ex, revelation=re21, ezekiel28=ez, shared_rev=sh)

def strip(xml):
    xml = re.sub(r"<note.*?</note>", " ", xml, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
def sections(path):
    x = open(path, encoding="utf-8").read(); parts = re.split(r'(<div[^>]*subtype="section"[^>]*n="[^"]+"|<milestone[^>]*unit="section"[^>]*n="[^"]+")', x)
    res = []; cur = "0"
    for p in parts:
        m = re.search(r'n="([^"]+)"', p) if p.startswith("<") and ("section" in p) else None
        if m: cur = m.group(1)
        else: res.append((cur, strip(p)))
    return res
print("\n3. JOSEPHUS AND PHILO")
jos = sections(JOS); philo = []
TITLE = {}
for d in sorted(glob.glob(os.path.join(PHILO, "tlg0*"))):
    f = glob.glob(os.path.join(d, "*grc*.xml"))
    if not f: continue
    t = re.search(r"<ti:title[^>]*>([^<]*)", open(os.path.join(d, "__cts__.xml"), encoding="utf-8").read()); TITLE[os.path.basename(d)] = t.group(1) if t else d
    philo += [(TITLE[os.path.basename(d)] + " " + n, s) for n, s in sections(f[0])]
def search(corpus, must, label, maxn=8, width=320):
    hits = []
    for loc, txt in corpus:
        n = nrm(txt)
        if all(re.search(m, n) for m in must):
            i = re.search(must[0], n).start(); hits.append((loc, txt[max(0, i - 60): i + width]))
    print(f"   {label}: {len(hits)} passages")
    for loc, s in hits[:maxn]: print(f"      [{loc}] {s.strip()}")
    return [(l, s) for l, s in hits]
r3 = {}
r3["josephus_seamless"] = search(jos, [r"ουκ εκ δυοιν περιτμηματων"], "Josephus: the high priest's robe 'not of two pieces' (Ant. 3.161)", width=420)
r3["josephus_cosmos"] = search(jos, [r"ζωδιακ|ζωδι"], "Josephus: zodiac in the priestly garments")
r3["philo_cosmos_robe"] = search(philo, [r"ποδηρ", r"κοσμ"], "Philo: the robe to the feet and the cosmos")
r3["philo_logos_highpriest"] = search(philo, [r"αρχιερευσ λογοσ|λογοσ αρχιερευσ|αρχιερεα λογον|λογον αρχιερεα|ο αρχιερευσ λογοσ"], "Philo: the Logos called high priest")
r3["philo_not_tear"] = search(philo, [r"διαρρηξ|διαρρηγν", r"λογ"], "Philo: the garment not to be torn, with the Logos")
r3["philo_stones_zodiac"] = search(philo, [r"λιθ", r"ζωδι"], "Philo: stones and the zodiac")
out["josephus_philo"] = {k: v[:12] for k, v in r3.items()}

print("\n4. WISDOM 18 (Swete's file numbers chapter 18 as 19 from 18:? onward; both are checked)")
for ref in ("Sapientia_Salomonis 19:15", "Sapientia_Salomonis 19:16", "Sapientia_Salomonis 19:24", "Sapientia_Salomonis 18:24", "Sapientia_Salomonis 18:15"):
    if ref in LX: print(f"   [{ref}] {lx(ref)}")
out["wisdom18"] = {r: lx(r) for r in ("Sapientia_Salomonis 19:15", "Sapientia_Salomonis 19:24", "Sapientia_Salomonis 18:24")}
json.dump(out, open(os.path.join(HERE, "high_priest_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
