#!/usr/bin/env python3
"""Round 47. Palestinian Aramaic of the period, and the ancient ways of writing sound.

A. Aramaic corpora, nearest first to Jesus' Galilean Aramaic:
     Qumran Aramaic (Dead Sea Scrolls words marked Aramaic; 2nd c. BC - 1st c. AD; ETCBC/Abegg, CC BY-NC: counts only)
     Biblical Aramaic (WLC, Daniel/Ezra, morph code A; 6th-2nd c. BC)
     Targum Neofiti (Palestinian targum, Pentateuch) and Targum Onkelos (Judean/Babylonian literary)
     Jerusalem Talmud (Galilean Aramaic, 4th-5th c.; sample: Berakhot, Shabbat, Taanit, Sanhedrin 1-5)
     Syriac New Testament (Peshitta; Eastern Aramaic, a translation from the Greek)
   For each Aramaic word kept in the Greek Gospels, the exact consonantal form (with and without the usual
   prefixes w-, d-, l-, b-) is counted per 100,000 words in each corpus: which dialect attests the Gospel forms?
B. Ancient ways of writing sound (primary texts read this round, quoted in the write-up): Mishnah Arakhin 2:3-6,
   Rosh Hashanah 4:9 (rhythm as ratios), Tamid 3:8 and 7:3, Arakhin 10b-11a (the magrepha), Josephus Ant. 7.305-306,
   the War Scroll's inscribed trumpets (1QM, from the scroll data), the psalm superscription terms (WLC).
C. Physics: (1) Tamid 3:8, Temple sounds 'heard in Jericho' (about 22 km, 1,000 m lower): the source power needed at
   each frequency, with ISO 9613-type air absorption, spherical spreading and, at night, an inversion duct (cylindrical
   beyond 1 km). (2) The magrepha as ten pipes in a one-cubit box, each sounding ten harmonics: pipe lengths for the
   planetary heptachord + 3, and whether they fit in a cubit.
Usage: python3 power/round47_aramaic_and_ancient_sound.py
"""
import collections, glob, json, math, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "round39", "yetzirah_calendar")); import tfread
out = {}; T = os.path.join(ROOT, "sources/texts")
HEB = re.compile(r"[א-ת]+")
FINAL = str.maketrans("ךםןףץ", "כמנפצ")
def norm(w): return re.sub(r"[^א-ת]", "", w).translate(FINAL)
def sefaria_words(path, lang="he"):
    d = json.load(open(path, encoding="utf-8")); ws = []
    for v in d.get("versions", []):
        if v["language"] != lang: continue
        def flat(x): return " ".join(flat(y) for y in x) if isinstance(x, list) else str(x)
        t = re.sub(r"<[^>]+>", " ", flat(v["text"])); ws += [norm(w) for w in HEB.findall(re.sub(r"[֑-ׇ]", "", t))]
        break
    return [w for w in ws if w]
C = {}
# Qumran Aramaic
tf = os.path.join(T, "dss/tf/1.9/")
lang = tfread.read_feature(tf + "lang.tf"); gl = tfread.read_feature(tf + "glyph.tf"); sl = tfread.read_oslots(tf + "oslots.tf", 1430241)
qa, qh = [], []
for wn in range(1606869, 2107864):   # word nodes (language is marked on the word's signs)
    if wn not in sl: continue
    g = norm(gl.get(wn, ""))
    if not g: continue
    (qa if lang.get(sl[wn][0]) == "a" else qh).append(g)
C["Qumran Aramaic (DSS)"] = qa; C["Qumran Hebrew (DSS, control)"] = qh
# Biblical Aramaic
ba = []
for b in ("Dan", "Ezra", "Jer", "Gen"):
    t = open(os.path.join(T, f"morphhb/wlc/{b}.xml"), encoding="utf-8").read()
    for m in re.finditer(r'<w[^>]*morph="A[^"]*"[^>]*>(.*?)</w>', t): ba.append(norm(re.sub(r"<[^>]+>", "", m.group(1))))
C["Biblical Aramaic"] = [w for w in ba if w]
C["Targum Onkelos"] = [w for f in sorted(glob.glob(os.path.join(T, "targum/Onkelos_*.json"))) for w in sefaria_words(f)]
C["Jerusalem Talmud (Galilean, sample)"] = [w for f in sorted(glob.glob(os.path.join(T, "sefaria/r47/Y_*.json"))) for w in sefaria_words(f)]
SY2HE = dict(zip("ܐܒܓܕܗܘܙܚܛܝܟܠܡܢܣܥܦܨܩܪܫܬ", "אבגדהוזחטיכלמנסעפצקרשת"))
syr = []
for f in glob.glob(os.path.join(T, "syrnt/plain/0.1/*.txt")):
    for l in open(f, encoding="utf-8"): syr += ["".join(SY2HE.get(c, "") for c in w) for w in l.split()]
C["Syriac NT (Peshitta)"] = [w for w in syr if w]
out["corpus_words"] = {k: len(v) for k, v in C.items()}
FORMS = {  # Gospel Aramaism: candidate consonantal forms (Aramaic spellings proposed in the literature)
 "talitha (Mk 5:41)": ["טליתא", "טליא", "טלייתא"], "koum (Mk 5:41)": ["קום", "קומי"],
 "ephphatha (Mk 7:34)": ["אתפתח", "אפתח", "אתפתחי"], "abba (Mk 14:36)": ["אבא"],
 "eloi / elahi (Mk 15:34)": ["אלהי"], "eli (Mt 27:46)": ["אלי"], "lema (Mk 15:34)": ["למא", "למה"],
 "sabachthani (Mk 15:34)": ["שבקתני", "שבקתנא", "שבקני"], "rabbouni (Jn 20:16)": ["רבוני", "רבוני", "רבני"],
 "golgotha (Jn 19:17)": ["גלגלתא", "גולגלתא"], "gabbatha (Jn 19:13)": ["גבתא", "גבהתא"], "kepha (Jn 1:42)": ["כיפא", "כפא"],
 "messias (Jn 1:41)": ["משיחא"], "mammon (Mt 6:24)": ["ממונא", "ממון"], "raka (Mt 5:22)": ["ריקא", "ריקה"],
 "maranatha (1 Cor 16:22)": ["מרנא", "מרן"], "korban (Mk 7:11)": ["קרבן", "קורבן"], "hosanna (Jn 12:13)": ["הושענא", "הושע"],
 "I am: ana hu": ["אנה", "אנא"], "amen": ["אמן"], "bar (son)": ["בר"], "abba/father emphatic 'abuna'": ["אבונא", "אבון"],
}
PREF = ("ו", "ד", "ל", "ב", "וד", "ול")
res = {}
for k, forms in FORMS.items():
    row = {}
    for cname, ws in C.items():
        cnt = collections.Counter(ws); n = len(ws)
        exact = sum(cnt[f.translate(FINAL)] for f in forms)
        withp = exact + sum(cnt[p + f.translate(FINAL)] for f in forms for p in PREF)
        row[cname] = dict(exact=exact, with_prefix=withp, per_100k=round(1e5 * withp / max(1, n), 1))
    res[k] = row
out["A_aramaisms"] = res

# ---------------------------------------------------------------- B. War Scroll trumpets and psalm superscriptions
lines = tfread.dss_lines(tf, ["1QM"])
trumpet_lines = [dict(frag=f, line=l, has_write="כתב" in "".join(w).translate(FINAL) or "יכתובו" in "".join(w), words=len(w))
                 for s, f, l, w in lines if any("חצוצר" in x for x in w)]
out["B_war_scroll"] = dict(lines_with_trumpets=len(trumpet_lines), of_which_with_writing_verb=sum(t["has_write"] for t in trumpet_lines),
                           refs=[f'{t["frag"]}:{t["line"]}' for t in trumpet_lines][:60],
                           note="1QM 2-3, 7-9: trumpets named for their purpose with words written on them; signals specified as long or sharp blasts (counts only; CC BY-NC)")
ps = open(os.path.join(T, "morphhb/wlc/Ps.xml"), encoding="utf-8").read(); psw = [norm(re.sub(r"<[^>]+>", "", m)) for m in re.findall(r"<w[^>]*>(.*?)</w>", ps)]
TERMS = {"lamenatseah (to the leader)": "למנצח", "selah": "סלה", "neginot (strings)": "בנגינות", "sheminit (the eighth)": "השמינית",
         "gittit": "הגתית", "alamot": "עלמות", "mizmor (psalm, sung with instrument)": "מזמור", "shir hamaalot (song of ascents)": "המעלות",
         "maskil": "משכיל", "miktam": "מכתם", "nehilot (flutes?)": "הנחילות", "higgayon": "הגיון"}
cps = collections.Counter(psw)
out["B_psalm_terms"] = {k: sum(c for w, c in cps.items() if w.endswith(v) or w == v) for k, v in TERMS.items()}

# ---------------------------------------------------------------- C. physics
BANDS = {63: (0.1, 35), 125: (0.4, 22), 250: (1.0, 12), 500: (1.9, 6), 1000: (3.7, 3)}  # air absorption dB/km (10 C, 70%), hearing threshold dB SPL
R = 22000.0; AMBIENT = 20.0
need = {}
for f, (alpha, thr) in BANDS.items():
    a = alpha * R / 1000; target = max(thr, AMBIENT)
    need[f] = dict(spherical_Lw_needed=round(20 * math.log10(R) + 11 + a + target, 1),
                   inversion_Lw_needed=round(20 * math.log10(1000) + 10 * math.log10(R / 1000) + 11 + a + target, 1))
SOURCES = {"the crier Gevini, a great shout": 97, "a shofar": 115, "two silver trumpets": 118, "cymbal crash (peak)": 120, "Levites' choir of 12": 97 + 10.8,
           "120 trumpets (2 Chr 5:12)": 136, "the great gate (heavy bronze doors, a slam)": 125}
out["C_jericho"] = dict(distance_km=22, ambient_night_dB=AMBIENT, needed_Lw_by_band=need, sources_Lw=SOURCES,
    verdict={s: [f for f in BANDS if L >= need[f]["inversion_Lw_needed"]] for s, L in SOURCES.items()},
    note="audible bands under a night inversion duct (spherical spreading to 1 km, cylindrical beyond); with plain spherical spreading nothing listed is audible")
cub = {"common cubit 0.445 m": 0.445, "royal cubit 0.525 m": 0.525}
heptachord = [165.0, 173.8, 195.6, 220.0, 231.8, 260.7, 293.3]
ten = heptachord + [330.0, 347.6, 391.1]  # the next three notes up (Pythagorean)
pipes = [dict(Hz=f, stopped_m=round(343 / (4 * f), 3), open_m=round(343 / (2 * f), 3)) for f in ten]
out["C_magrepha"] = dict(text="Arakhin 11a: one cubit wide, one cubit tall, a handle; hollow, ten holes; each hole ten kinds of tone (Shmuel: 100 in all; the baraita: 100 each, 1,000)",
    reading="ten pipes, each overblown through its harmonics: 10 x 10 = 100 pitches (stopped pipes give odd harmonics only)",
    pipes=pipes, fits={k: all(p["stopped_m"] <= v for p in pipes) for k, v in cub.items()},
    longest_stopped_m=max(p["stopped_m"] for p in pipes),
    distinct_pitches_open_10x10=len({round(12 * math.log2(f * h / 220)) for f in ten for h in range(1, 11)}))
json.dump(out, open(os.path.join(HERE, "round47_results.json"), "w"), ensure_ascii=False, indent=1)
print(out["corpus_words"])
for k, row in res.items(): print(k, {c[:14]: v["per_100k"] for c, v in row.items()})
print(out["B_war_scroll"]["lines_with_trumpets"], out["B_war_scroll"]["of_which_with_writing_verb"]); print(out["B_psalm_terms"])
print(json.dumps(out["C_jericho"]["needed_Lw_by_band"])); print(out["C_jericho"]["verdict"]); print(out["C_magrepha"]["fits"], out["C_magrepha"]["longest_stopped_m"], out["C_magrepha"]["distinct_pitches_open_10x10"])
