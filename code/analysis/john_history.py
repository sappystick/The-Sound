#!/usr/bin/env python3
"""The historical John: primary testimonies checked in Greek, an authorship test, date cross-checks, and a
timeline tree written as data (john_timeline.json).

 1. TESTIMONIES (Greek, located and printed): Josephus on John the Baptist (Ant. 18.116-119); in Eusebius'
    Church History: Papias on 'John the Elder' (3.39), Irenaeus on John at Ephesus (5.8.4; 3.23.3), Polycrates
    on John 'who became a priest, wearing the petalon' (3.31.3; 5.24.3), Clement's 'spiritual gospel' (6.14.7),
    Dionysius of Alexandria on two Johns and two tombs at Ephesus (7.25), the exile to Patmos (3.18).
 2. AUTHORSHIP: Burrows' Delta on the 100 most frequent words, John against 1 John, Revelation, the Synoptics,
    Acts and Paul (2 and 3 John are too short for Delta; reported by shared vocabulary only).  Dionysius of
    Alexandria argued c. 250 AD from style that Revelation is not by the Gospel's author: tested here.
 3. DATES: John 2:20 '46 years' from Herod's start on the temple (Josephus, Ant. 15.380: his 18th year =
    20/19 BC) against Luke 3:1 (15th year of Tiberius = AD 28/29); Passover full moons of AD 30 and 33.
Usage: python3 john_history.py <sblgnt> <josephus Ant xml> <eusebius HE xml>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, JOS, EUS = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω ]", "", w.replace("ς", "σ"))
def secs(path):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    res, book, ch = [], "?", "?"
    for tag, attrs, body in re.findall(r"<(div|milestone)([^>]*)>([^<]*(?:<(?!div|milestone)[^<]*)*)", x):
        n = re.search(r'n="([^"]+)"', attrs); st = re.search(r'subtype="([^"]+)"|unit="([^"]+)"', attrs)
        kind = (st.group(1) or st.group(2)) if st else ""
        if n:
            if kind == "book": book = n.group(1)
            elif kind == "chapter": ch = n.group(1)
            else: res.append((f"{book}.{ch}.{n.group(1)}", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))))
    return res
print("1. TESTIMONIES")
J = secs(JOS)
def flat(path):   # whole text with [book.chapter.section] markers kept, split into marked pieces
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<note.*?</note>", " ", x, flags=re.S)
    x = re.sub(r'<(?:div|milestone)[^>]*subtype="(book|chapter|section)"[^>]*n="([^"]+)"[^>]*>', lambda m: f" @@{m.group(1)}={m.group(2)}@@ ", x)
    x = re.sub(r'<(?:div|milestone)[^>]*n="([^"]+)"[^>]*subtype="(book|chapter|section)"[^>]*>', lambda m: f" @@{m.group(2)}={m.group(1)}@@ ", x)
    x = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)); res, cur = [], {"book": "?", "chapter": "?", "section": "?"}
    for piece in re.split(r"(@@\w+=[^@]+@@)", x):
        m = re.match(r"@@(\w+)=([^@]+)@@", piece)
        if m: cur[m.group(1)] = m.group(2)
        elif piece.strip(): res.append((f"{cur['book']}.{cur['chapter']}.{cur['section']}", piece))
    return res
EU = flat(EUS)
def find(corpus, pats, label, width=500):
    for ref, txt in corpus:
        n = nrm(txt)
        if all(re.search(p, n) for p in pats):
            i = re.search(pats[0], n).start(); s = txt[max(0, i - 80): i + width]
            print(f"   [{label} | {ref}] {s.strip()}\n"); return dict(ref=ref, text=s.strip())
    print(f"   [{label}] not found\n"); return None
T = {}
T["Josephus on the Baptist"] = find(J, [r"ιωαννου του επικαλουμενου βαπτιστου"], "Josephus, Antiquities")
T["Josephus: Machaerus"] = find(J, [r"μαχαιρουντα", r"ιωανν|πεμφθεισ"], "Josephus, Antiquities", 250)
T["Josephus: temple begun in Herod's 18th year"] = find(J, [r"οκτωκαιδεκατ", r"ναον|ιερον|ναου"], "Josephus, Antiquities", 300)
T["Papias: John the Elder"] = find(EU, [r"ο πρεσβυτεροσ ιωαννησ"], "Eusebius, Church History", 600)
T["Irenaeus: John at Ephesus"] = find(EU, [r"επι το στηθοσ", r"εφεσω"], "Eusebius, Church History")
T["Polycrates: the petalon"] = find(EU, [r"πεταλον"], "Eusebius, Church History")
T["Clement: spiritual gospel"] = find(EU, [r"πνευματικον ποιησαι ευαγγελιον"], "Eusebius, Church History")
T["Dionysius: two tombs"] = find(EU, [r"δυο", r"μνημα|μνηματα", r"εφεσω"], "Eusebius, Church History", 600)
T["Patmos under Domitian"] = find(EU, [r"πατμον"], "Eusebius, Church History", 400)
T["John until Trajan"] = find(EU, [r"τραιανου"], "Eusebius, Church History", 300)
out["testimonies"] = T

print("2. AUTHORSHIP (Burrows' Delta; smaller = more alike)")
NT = {}
for f in glob.glob(os.path.join(SBL, "*-morphgnt.txt")):
    b = os.path.basename(f).split("-")[1]; NT[b] = [nrm(l.split()[4]).strip() for l in open(f, encoding="utf-8")]
groups = {"John": ["Jn"], "1 John": ["1Jn"], "Revelation": ["Re"], "Matthew": ["Mt"], "Mark": ["Mk"], "Luke": ["Lk"], "Acts": ["Ac"], "Paul (Ro, 1-2Co, Ga)": ["Ro", "1Co", "2Co", "Ga"], "Hebrews": ["Heb"]}
docs = {k: [w for b in v for w in NT[b] if w] for k, v in groups.items()}
mfw = [w for w, _ in collections.Counter(w for d in docs.values() for w in d).most_common(100)]
Z = {k: np.array([d.count(w) / len(d) for w in mfw]) for k, d in docs.items()}
M = np.vstack(list(Z.values())); mu, sd = M.mean(0), M.std(0) + 1e-12
Zs = {k: (v - mu) / sd for k, v in Z.items()}
delta = {a: {b: round(float(np.mean(np.abs(Zs[a] - Zs[b]))), 3) for b in Zs if b != a} for a in Zs}
for a in ("John", "1 John", "Revelation"):
    print(f"   {a:12s} nearest: " + ", ".join(f"{b} {v}" for b, v in sorted(delta[a].items(), key=lambda x: x[1])[:5]))
small = {k: set(NT[k]) for k in ("2Jn", "3Jn")}
for k, s in small.items():
    sh = {g: round(len(s & set(docs[g])) / len(s), 3) for g in ("John", "1 John", "Revelation", "Luke")}
    print(f"   {k}: share of its words also used in: {sh}")
out["delta"] = delta

print("\n3. DATE CROSS-CHECKS")
start = -19.5; print(f"   temple begun 20/19 BC + 46 years (John 2:20) = AD {start + 46 + 1:.1f} (no year 0) -> AD 27/28")
print("   15th year of Tiberius (Luke 3:1): Tiberius succeeded Aug. 14 AD -> AD 28/29; with co-regency count from AD 12 -> AD 26/27")
print("   Nisan 14 on a Friday (John's day of Preparation): 7 April AD 30 or 3 April AD 33 (astronomical tables; Humphreys & Waddington 1983)")
out["dates"] = dict(john_2_20="AD 27/28", luke_3_1="AD 28/29 (or 26/27)", passover_friday=["7 Apr AD 30", "3 Apr AD 33"])
json.dump(out, open(os.path.join(HERE, "john_history_results.json"), "w"), ensure_ascii=False, indent=1)
