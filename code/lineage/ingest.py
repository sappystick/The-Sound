#!/usr/bin/env python3
"""Grow the instruction dataset automatically from full texts.

Sources (Sefaria public export, storage.googleapis.com/sefaria-export):
  * Mishnah: 17 ritual tractates. Hebrew is public domain; the English (Koren / William Davidson,
    CC BY-NC) is used ONLY for tagging and is not stored.
  * Philo (Yonge translation, public domain): On the Contemplative Life, On the Special Laws.
  * Josephus (Whiston translation, public domain): The War of the Jews, Antiquities.
  * Letter of Aristeas, Book of Jubilees (Charles, public domain).
Every passage is tagged with the categories of test_handover.py (time, place, direction,
repetition, posture, voice, materials) plus practice threads.  A passage counts as an
'instruction' when it carries >= 3 field types.  Confidence = 'auto'.
Usage: python3 ingest.py <cache dir>
"""
import csv, json, os, re, sys, urllib.parse, urllib.request
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    from test_handover import VOCAB, FIELDS

CACHE = sys.argv[1]; os.makedirs(CACHE, exist_ok=True)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
B = "https://storage.googleapis.com/sefaria-export/json/"
MISHNAH = {"Seder Moed": ["Pesachim", "Shekalim", "Yoma", "Sukkah", "Rosh Hashanah", "Taanit", "Ta'anit", "Megillah"],
           "Seder Kodashim": ["Zevachim", "Menachot", "Tamid", "Middot", "Kinnim"],
           "Seder Zeraim": ["Berakhot", "Bikkurim"], "Seder Tahorot": ["Parah", "Mikvaot", "Yadayim"],
           "Seder Nashim": ["Sotah"]}
OTHER = [("Second Temple/Philo/On the Contemplative Life or Suppliants", "Philo, On the Contemplative Life", 30),
         ("Second Temple/Philo/On the Special Laws", "Philo, On the Special Laws", 30),
         ("Second Temple/Josephus/The War of the Jews", "Josephus, Jewish War", 75),
         ("Second Temple/Josephus/The Antiquities of the Jews", "Josephus, Antiquities", 94),
         ("Second Temple/Apocrypha/Letter of Aristeas", "Letter of Aristeas", -150),
         ("Second Temple/Apocrypha/Book of Jubilees", "Jubilees", -150)]
THREADS = {
    "washing": r"immers|wash|bathe|ritual bath|sanctif\w* (his )?hands|purif", "dawn": r"dawn|sunrise|daybreak|morning|cock|first light",
    "incense": r"incense|frankincense", "lamp_light": r"\blamps?\b|candelabrum|menorah|torch", "prostration": r"prostrat|bow(ed)? down|fell on their faces|kneel",
    "sung_praise": r"\bsong|\bsang|\bsing|hymn|psalm|hallel|praise", "instruments": r"trumpet|shofar|cymbal|harp|lyre|flute|pipe",
    "sacred_name": r"\bthe name\b|explicit name|tetragram", "circling": r"circle|circuit|went around|encircl", "plants": r"willow|palm|myrtle|citron|hyssop|cedar",
    "blood_rite": r"\bblood\b", "bread_offering": r"shewbread|loaves|bread|meal offering|showbread", "wine_libation": r"libation|\bwine\b",
    "water_libation": r"water libation|siloam", "linen": r"linen|garments of white", "threshold": r"\bgate|door|entrance|threshold",
    "inner_room": r"holy of holies|sanctuary|inner|sanctum", "orientation": r"\beast|\bwest|toward the|facing", "hours": r"hour|evening|twilight|daily",
    "new_moon": r"new moon", "fasting_abstinence": r"\bfast", "anointing": r"anoint", "silence": r"silen"}


def get(path):
    fn = os.path.join(CACHE, re.sub(r"[^\w]+", "_", path) + ".json")
    if not os.path.exists(fn):
        url = B + urllib.parse.quote(path) + "/merged.json"
        try: urllib.request.urlretrieve(url, fn)
        except Exception as e: print("  skip", path, e); return None
    return json.load(open(fn, encoding="utf-8"))


def walk(node, ref=()):
    if isinstance(node, str): yield ref, node
    elif isinstance(node, list):
        for i, x in enumerate(node, 1): yield from walk(x, ref + (i,))
    elif isinstance(node, dict):
        for k, x in node.items():
            if k in ("Introduction", "Appendix", "Footnotes", "Notes"): continue  # modern editorial matter
            yield from walk(x, ref + ((k,) if k else ()))


def tag(text):
    t = text.lower(); fields = {}
    for ft in FIELDS:
        toks = {tok for tok, pat in VOCAB[ft].items() if re.search(pat, t)}
        if toks: fields[ft] = sorted(toks)
    threads = sorted(k for k, p in THREADS.items() if re.search(p, t))
    return fields, threads


recs = []
for seder, tractates in MISHNAH.items():
    for tr in tractates:
        en = get(f"Mishnah/{seder}/Mishnah {tr}/English"); he = get(f"Mishnah/{seder}/Mishnah {tr}/Hebrew")
        if not en: continue
        hed = {r: s for r, s in walk(he["text"])} if he else {}
        for ref, s in walk(en["text"]):
            s = re.sub(r"<[^>]+>", "", s); fields, threads = tag(s)
            if len(fields) >= 3:
                recs.append(dict(id=f"MA-{tr[:4]}-{'.'.join(map(str, ref))}", tradition="Mishnah (Second Temple practice)", year=200,
                                 source="Mishnah", ref=f"{tr} {'.'.join(map(str, ref))}", hebrew_excerpt=re.sub(r"<[^>]+>", "", hed.get(ref, ""))[:90],
                                 english_excerpt="(Koren CC BY-NC; not stored)", **{f: "; ".join(fields.get(f, [])) for f in FIELDS},
                                 threads="; ".join(threads), confidence="auto", n_fields=len(fields)))
for path, label, year in OTHER:
    d = get(path + "/English")
    if not d: continue
    chunks = []
    for ref, s in walk(d["text"]):
        s = re.sub(r"<[^>]+>", "", s)
        # split very long sections into ~700-character chunks at sentence ends
        parts, cur = [], ""
        for sent in re.split(r"(?<=[.;?!])\s+", s):
            cur += sent + " "
            if len(cur) > 700: parts.append(cur); cur = ""
        if cur.strip(): parts.append(cur)
        for j, part in enumerate(parts, 1): chunks.append((ref + ((f"c{j}",) if len(parts) > 1 else ()), part))
    for ref, s in chunks:
        if len(s) < 60: continue
        fields, threads = tag(s)
        if len(fields) >= 3:
            recs.append(dict(id=f"ST-{re.sub(r'[^A-Za-z]', '', label)[:10]}-{'.'.join(map(str, ref))}", tradition="Second Temple Judaism (Qumran, Philo, Josephus)",
                             year=year, source=label, ref=".".join(map(str, ref)), hebrew_excerpt="", english_excerpt="(not stored)",
                             **{f: "; ".join(fields.get(f, [])) for f in FIELDS}, threads="; ".join(threads), confidence="auto", n_fields=len(fields)))
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "auto_records.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(recs[0].keys())); w.writeheader(); w.writerows(recs)
import collections
print(f"{len(recs)} auto-coded instruction passages")
print(collections.Counter(r["source"] for r in recs).most_common())
