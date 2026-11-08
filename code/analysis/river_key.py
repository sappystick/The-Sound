#!/usr/bin/env python3
"""The river thread (153, Ezekiel 47, Tabernacles) and John's key applied to the whole New Testament.

A. RIVER THREAD
   1. Which Greek-OT chapter is nearest in wording to John 21:1-14 (the 153 fish), to John 7:37-39
      ('rivers of living water') and to John 19:31-37 (blood and water)?  Rank of Ezekiel 47 and Zechariah 14
      among all ~1,150 OT chapters (rare-word overlap, inverse frequency weights).
   2. 'Living water' (hydor zon) in the Greek OT and NT.
   3. Is the 17/153 match in Ezekiel 47:10 a fluke?  Every Hebrew verse in the Bible is scanned for a
      morpheme worth 17 and one worth 153 in the same verse; and how many fishing verses there are.
   4. Greek letter values of the fishing words in John 21 (fish, net) against 153.
   5. Tabernacles: the Mishnah's water rite from Siloam and the lamps that lit every courtyard
      (Mishnah Sukkah 4:9, 5:2-3), against John 7:37-39, 8:12, 9:5-7.
B. THE SELF IN JOHN: 'not from myself' (ap' emautou / aph' heautou), 'I must decrease', the grain of wheat,
   the breath handed over (19:30) and breathed back (20:22), counted against the other Gospels.
C. JOHN'S KEY ON THE WHOLE NEW TESTAMENT: per book, rates of John's decoding devices, and every
   'pointer word' (used once in the NT, 1-3 times in the Greek OT), which links a verse to one OT passage.
   Writes analysis/nt_pointers.csv.
Usage: python3 river_key.py <sblgnt dir> <lxx-swete/data> <morphhb/wlc> <mishnah sukkah merged.json>
"""
import collections, csv, glob, json, math, os, re, sys, unicodedata
SBL, LXX, WLC, SUK = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
NT = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    code = os.path.basename(f).split("-")[1]
    NT[code] = [dict(ref=(int(l[2:4]), int(l[4:6])), text=l.split()[3], w=nrm(l.split()[4]), lem=nrm(l.split()[6])) for l in open(f, encoding="utf-8")]
LXXW = []   # (book, ch, vs, normalized word, raw)
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2:
            r = p[0].split("."); LXXW.append((b, r[1], r[2], nrm(p[1]), p[1].strip()))
st = lambda w: w[:6]
df = collections.Counter(); chap = collections.defaultdict(collections.Counter)
for b, c, v, w, _ in LXXW:
    if w and w not in STOP and len(w) > 3: chap[(b, c)][st(w)] += 1
for k, cnt in chap.items():
    for s in cnt: df[s] += 1
Nch = len(chap)
def nearest(tokens, label, watch):
    q = {st(t["w"]) for t in tokens if t["w"] not in STOP and len(t["w"]) > 3}
    score = {k: sum(math.log(Nch / df[s]) for s in q if s in cnt) / math.sqrt(len(cnt)) for k, cnt in chap.items() if sum(cnt.values()) >= 80}
    rank = sorted(score, key=lambda k: -score[k])
    print(f"   {label}: nearest OT chapters: " + ", ".join(f"{b} {c}" for b, c in rank[:6]))
    res = {"top": [f"{b} {c}" for b, c in rank[:10]]}
    for w_ in watch:
        if w_ in score: r = rank.index(w_) + 1; res[f"{w_[0]} {w_[1]}"] = r; print(f"      rank of {w_[0]} {w_[1]}: {r} of {len(rank)}")
    return res
def span(code, a, b): return [t for t in NT[code] if a <= t["ref"] <= b]

print("A1. RIVER THREAD: nearest Greek-OT chapters by shared rare words")
W = [("Ezechiel", "47"), ("Zacharias", "14"), ("Genesis", "2"), ("Joel", "3"), ("Isaias", "55"), ("Isaias", "12")]
out["nearest"] = {"Jn 21:1-14 (153 fish)": nearest(span("Jn", (21, 1), (21, 14)), "John 21:1-14 (the 153 fish)", W),
                  "Jn 7:37-39": nearest(span("Jn", (7, 37), (7, 39)), "John 7:37-39 (rivers of living water)", W),
                  "Jn 19:31-37": nearest(span("Jn", (19, 31), (19, 37)), "John 19:31-37 (blood and water)", W),
                  "Jn 4:7-15": nearest(span("Jn", (4, 7), (4, 15)), "John 4:7-15 (the well, living water)", W)}

print("\nA2. 'LIVING WATER' in the Greek OT and the NT")
lw = []
for i in range(len(LXXW) - 1):
    if LXXW[i][3].startswith("υδ") and LXXW[i + 1][3].startswith("ζω"): lw.append(f"{LXXW[i][0]} {LXXW[i][1]}:{LXXW[i][2]}")
ntlw = [f"{c} {b[i]['ref'][0]}:{b[i]['ref'][1]}" for c, b in NT.items() for i in range(len(b) - 1) if b[i]["lem"] == "υδωρ" and b[i + 1]["lem"] == "ζαω"]
print("   Greek OT:", ", ".join(lw)); print("   NT:", ", ".join(ntlw))
z14 = " ".join(x[4] for x in LXXW if x[0] == "Zacharias" and x[1] == "14" and x[2] in ("7", "8", "16"))
print("   Zechariah 14:7-8, 16 (Greek):", z14)
out["living_water"] = dict(lxx=lw, nt=ntlw)

print("\nA3. IS THE 17 / 153 PAIR IN EZEKIEL 47:10 A FLUKE?  (Hebrew Bible, every verse, by morpheme)")
HV = dict(zip("אבגדהוזחטיכלמנסעפצקרשתךםןףץ", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 20, 40, 50, 80, 90]))
def cons(s): return "".join(c for c in unicodedata.normalize("NFD", s) if c in HV)
verses = []
for f in glob.glob(os.path.join(WLC, "*.xml")):
    x = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S):
        morphs = []
        for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2)):
            parts = w.split("/"); morphs += [cons(p) for p in parts]
            morphs.append(cons(w.replace("/", "")))
        verses.append((m.group(1), [p for p in morphs if p]))
val = lambda s: sum(HV[c] for c in s)
both = [v for v, ms in verses if any(val(p) == 17 for p in ms) and any(val(p) == 153 for p in ms)]
w153 = collections.Counter(p for _, ms in verses for p in ms if val(p) == 153)
fishing = [v for v, ms in verses if any(p in ("דוגים", "דיגים", "דגים", "דגה", "דג") for p in ms)]
print(f"   verses with a word worth 17 AND a word worth 153: {len(both)} of {len(verses):,}: {both[:12]}")
print(f"   distinct words worth 153: {len(w153)}; commonest: {w153.most_common(6)}")
print(f"   verses that mention fish: {len(fishing)}; of these with the 17/153 pair: {[v for v in fishing if v in both]}")
out["gematria_scan"] = dict(both=both, n_verses=len(verses), words153=w153.most_common(20), fishing=len(fishing), fishing_with_pair=[v for v in fishing if v in both])

print("\nA4. GREEK LETTER VALUES of John 21's fishing words")
GV = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800]))
gv = lambda s: sum(GV.get(c, 0) for c in nrm(s))
iso = {}
for w in ("ἰχθύες", "ἰχθύων", "τὸ δίκτυον", "δίκτυον", "ἰχθύς", "Σίμων Πέτρος", "μεγάλων", "ἑκατὸν πεντήκοντα τριῶν"):
    v_ = gv(w); iso[w] = v_; print(f"   {w:26s} = {v_:5d}  {'= ' + str(v_ // 153) + ' x 153' if v_ % 153 == 0 else ''}")
# how often is a John word a multiple of 153 anyway?
jw = {t["w"] for t in NT["Jn"]}; mult = sorted(w for w in jw if gv(w) % 153 == 0 and gv(w) > 0)
print(f"   distinct words in John whose value is a multiple of 153: {len(mult)} of {len(jw)} ({len(mult) / len(jw):.1%}; chance 1/153 = 0.65%): {mult[:15]}")
out["isopsephy"] = dict(values=iso, john_multiples=mult, share=round(len(mult) / len(jw), 4))

print("\nA5. TABERNACLES: the Mishnah's rites and John 7-9")
suk = json.load(open(SUK, encoding="utf-8"))["text"]
print("   Mishnah Sukkah 4:9 (water libation):", suk[3][8][:140], "...")
print("   Mishnah Sukkah 5:3 (lamps):", suk[4][2][-90:])
print("   Siloam (השלוח) named in the water rite:", "השלוח" in cons(suk[3][8]) or "שלוח" in cons(suk[3][8]))
jsil = sorted({t["ref"] for t in NT["Jn"] if t["lem"].startswith("σιλωαμ")}); light_iam = [(8, 12), (9, 5)]
print(f"   John: 'rivers of living water' 7:37-38 on the last great day of the feast; 'I am the light of the world' 8:12 and 9:5; Siloam = 'Sent' {jsil}")
out["tabernacles"] = dict(sukkah_4_9=suk[3][8], sukkah_5_3=suk[4][2], john_siloam=jsil)

# ================================================================ B. the self
print("\nB. THE SELF IN JOHN")
def count_pairs(code, a_pat, b_pat):
    b = NT[code]; return [f"{b[i]['ref'][0]}:{b[i]['ref'][1]}" for i in range(len(b) - 1) if re.fullmatch(a_pat, b[i]["w"]) and re.fullmatch(b_pat, b[i + 1]["w"])]
selfr = {}
for code in ("Mt", "Mk", "Lk", "Jn"):
    h = count_pairs(code, r"απ|αφ|απο", r"(εμαυτου|εαυτου|σεαυτου)"); selfr[code] = h
    print(f"   'from myself / from himself' (ap' emautou / aph' heautou) in {code}: {len(h)}  {', '.join(h) if code == 'Jn' else ''}")
both_v = [r for r in selfr["Jn"] if r in ("8:28",)]
print("   John 8:28 joins the two: 'then you will know that I AM, and that I do nothing from myself'")
deaths = {c: sorted({t["lem"] for t in span(c, (27, 45), (27, 56)) if t["lem"] in ("εκπνεω", "αφιημι", "παραδιδωμι", "πνευμα")}) if c == "Mt" else None for c in ("Mt",)}
moment = {"Mt 27:50": " ".join(t["text"] for t in span("Mt", (27, 50), (27, 50))), "Mk 15:37": " ".join(t["text"] for t in span("Mk", (15, 37), (15, 37))),
          "Lk 23:46": " ".join(t["text"] for t in span("Lk", (23, 46), (23, 46))), "Jn 19:30": " ".join(t["text"] for t in span("Jn", (19, 30), (19, 30))),
          "Jn 20:22": " ".join(t["text"] for t in span("Jn", (20, 22), (20, 22)))}
for k, v in moment.items(): print(f"   {k}: {v}")
TOT = sum(1 for t in NT["Jn"] if t["w"]); pos = {}
acc = 0
for t in NT["Jn"]:
    pos.setdefault(t["ref"], acc / TOT); acc += 1
PATH = [("3:8", "the wind blows where it wills: so is everyone born of the Spirit"), ("3:30", "he must increase, I must decrease"),
        ("5:19", "the Son can do nothing from himself"), ("8:28", "I AM ... I do nothing from myself"), ("12:24", "unless a grain of wheat falls and dies"),
        ("12:25", "whoever loves his life loses it"), ("13:5", "he began to wash the disciples' feet"), ("15:4", "abide in me, and I in you"),
        ("17:21", "that they may all be one, as you are in me and I in you"), ("19:30", "he bowed his head and handed over the spirit (breath)"),
        ("20:22", "he breathed on them: receive the Holy Spirit")]
print("   the path of the self in John, with its place in John's spoken length:")
for r, txt in PATH:
    c, v = map(int, r.split(":")); print(f"      {r:6s} {pos[(c, v)]:.2f}  {txt}")
out["self"] = dict(from_myself=selfr, moments=moment, path=[(r, round(pos[tuple(map(int, r.split(':')))], 3), t) for r, t in PATH])

# ================================================================ C. John's key on the whole NT
print("\nC. JOHN'S KEY ON THE WHOLE NEW TESTAMENT")
lem_count = collections.Counter(t["lem"] for b in NT.values() for t in b)
lxx_by_stem = collections.defaultdict(list)
for b, c, v, w, _ in LXXW:
    if len(w) > 4: lxx_by_stem[w[:6]].append(f"{b} {c}:{v}")
rows = []; per_book = {}
for code, b in NT.items():
    n = len(b); seen = set(); k = 0
    for t in b:
        if lem_count[t["lem"]] == 1 and len(t["lem"]) > 4 and t["lem"] not in seen:
            locs = lxx_by_stem.get(t["lem"][:6], [])
            if 1 <= len(locs) <= 3:
                seen.add(t["lem"]); k += 1; rows.append(dict(book=code, ref=f"{t['ref'][0]}:{t['ref'][1]}", word=t["text"], lemma=t["lem"], lxx="; ".join(locs)))
    dev = len(count_pairs(code, r"τουτο", r"δε")) and sum(1 for i in range(len(b) - 2) if b[i]["w"] == "τουτο" and b[i + 1]["w"] == "δε" and b[i + 2]["w"] in ("ειπεν", "ελεγεν"))
    sig = sum(1 for t in b if t["w"] == "σημαινων"); gl = sum(1 for t in b if re.fullmatch(r"(μεθ)?ερμηνευ\w*", t["w"]))
    per_book[code] = dict(words=n, pointers=k, pointers_per10k=round(1e4 * k / n, 1), asides=dev + sig, glosses=gl)
with open(os.path.join(HERE, "nt_pointers.csv"), "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=["book", "ref", "word", "lemma", "lxx"]); wr.writeheader(); wr.writerows(rows)
print(f"   {len(rows)} pointer words found across the NT (written to nt_pointers.csv)")
for code, d in sorted(per_book.items(), key=lambda x: -x[1]["pointers_per10k"])[:10]:
    print(f"      {code:4s} {d['pointers']:3d} pointers ({d['pointers_per10k']:5.1f} per 10,000 words), narrator asides {d['asides']}, glosses {d['glosses']}")
print("   John's own pointers:", "; ".join(f"{r['ref']} {r['word']} -> {r['lxx']}" for r in rows if r["book"] == "Jn"))
out["nt_key"] = dict(per_book=per_book, john=[r for r in rows if r["book"] == "Jn"], n=len(rows))
json.dump(out, open(os.path.join(HERE, "river_key_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
