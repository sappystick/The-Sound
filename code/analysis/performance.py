#!/usr/bin/env python3
"""The four performance tests, plus shape poetry.

T1. PERFORMANCE PROFILE: John against real performance texts (Ezekiel the Tragedian's Exagoge, a Jewish-Greek play,
    probably Alexandrian, 2nd c. BC, preserved in Eusebius, Praeparatio Evangelica 9.28-29; Sophocles' Oedipus the King;
    Euripides' Bacchae; Aeschylus) and narrative / exposition (Matthew-Mark-Luke, Josephus, Philo). Features per 1,000
    words: 'behold', 'here / there / now', motion imperatives ('come', 'go', 'rise'), vocatives (o!), second- and
    first-person pronouns, motion verbs, body / gesture verbs.  Which class is John nearest?
T2. DEIXIS ON MOVEMENT: within John (and the Synoptics), do pointing words fall in the same verses as motion and
    gesture more than chance?  (Correlation per verse, against shuffled pairing.)
T3. ACTOR TEST: needs people; the protocol is written to performance_actor_protocol.md. A text-only proxy: share of John's
    scenes whose place, entrances/exits and posture can be read from the text alone, against Mark.
T4. ACTIONS ON BREATH BOUNDARIES: are motion and body verbs commoner in the first three words of a breath group than
    their share of positions predicts?
S.  SHAPE POETRY: the Hellenistic shape poems (Greek Anthology 15.22 Axe, 15.24 Wings, 15.27 Egg; 15.25-26 Altars) as a
    control for a line-length shape detector (V, Lambda, mirror), then John's prologue (verses; P75 lines).
Usage: python3 performance.py <sblgnt> <greek dir> <cntr class 1 dir>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, GR, CN = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(9); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def xml_words(path, sel=None):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", " ", x, flags=re.S); x = re.sub(r"<(note|bibl|head|speaker)[^>]*>.*?</\1>", " ", x, flags=re.S)
    if sel: x = sel(x)
    return [w for w in (nrm(t) for t in re.sub(r"<[^>]+>", " ", x).split()) if w]
def exagoge(x):
    b = re.search(r'subtype="book"[^>]*n="9"', x); seg = x[b.start():]; m1 = re.search(r'subtype="chapter"[^>]*n="28"', seg); m2 = re.search(r'subtype="chapter"[^>]*n="30"', seg)
    return seg[m1.start(): m2.start()] if m1 and m2 else ""
NT = {os.path.basename(f).split("-")[1]: [((int(l[2:4]), int(l[4:6])), nrm(l.split()[4]), nrm(l.split()[6]), l.split()[3]) for l in open(f, encoding="utf-8")] for f in glob.glob(os.path.join(SBL, "*-morphgnt.txt"))}
C = {"John": [w for _, w, _, _ in NT["Jn"]], "Matthew, Mark, Luke": [w for b in ("Mt", "Mk", "Lk") for _, w, _, _ in NT[b]],
     "Exagoge (Ezekiel the Tragedian)": xml_words(glob.glob(os.path.join(GR, "f1k/data/tlg2018/tlg001/*grc*.xml"))[0], exagoge),
     "Sophocles, Oedipus the King": xml_words(glob.glob(os.path.join(GR, "perseus/data/tlg0011/tlg004/*grc*.xml"))[0]),
     "Euripides, Bacchae": xml_words(glob.glob(os.path.join(GR, "perseus/data/tlg0006/tlg017/*grc*.xml"))[0]),
     "Aeschylus": xml_words(glob.glob(os.path.join(GR, "perseus/data/tlg0085/tlg005/*grc*.xml"))[0]),
     "Josephus (narrative)": xml_words(glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml"))[0])[:60000],
     "Philo (exposition)": [w for f in sorted(glob.glob(os.path.join(GR, "f1k/data/tlg0018/tlg*/*grc*.xml")))[:3] for w in xml_words(f)][:60000]}
FEAT = {"behold": lambda w: w in ("ιδου", "ιδε", "ιδεσθε", "ιδεσθ"), "here / there / now": lambda w: w in ("ωδε", "ενθαδε", "εκει", "ενθαδ", "νυν", "νυνι", "δευρο"),
        "motion imperatives": lambda w: w in ("ελθε", "ερχου", "δευρο", "υπαγε", "εξελθε", "εγειρε", "εγειρεσθε", "αγωμεν", "στηθι", "χωρει", "βαδιζε", "ιθι", "αγε", "δευτε", "πορευου"),
        "vocative o": lambda w: w == "ω", "you (2nd person)": lambda w: w in ("συ", "σε", "σου", "σοι", "υμεισ", "υμασ", "υμων", "υμιν"), "I (1st person)": lambda w: w in ("εγω", "με", "μου", "μοι", "εμε", "εμου", "εμοι"),
        "motion verbs": lambda w: w.startswith(("ερχ", "ηλθ", "ελθ", "εισελ", "εξελ", "αναβ", "καταβ", "πορευ", "βαιν", "εβη", "χωρε", "υπαγ", "απηλθ")),
        "body / gesture": lambda w: w.startswith(("εστη", "ιστη", "καθη", "καθισ", "εκλαυ", "κλαι", "δακρ", "πιπτ", "επεσ", "νιψ", "νιπτ", "αψα", "απτ", "κλιν", "επαρ", "ενεφυσ"))}
print("T1. PERFORMANCE PROFILE (per 1,000 words)")
M = {}
print(f"   {'text':32s} " + " ".join(f"{k[:10]:>10s}" for k in FEAT))
for lab, ws in C.items():
    if len(ws) < 500: print(f"   {lab}: too short ({len(ws)} words)"); continue
    M[lab] = np.array([1000 * sum(f(w) for w in ws) / len(ws) for f in FEAT.values()]); print(f"   {lab:32s} " + " ".join(f"{v:10.1f}" for v in M[lab]) + f"   ({len(ws)} words)")
A = np.vstack(list(M.values())); mu, sd = A.mean(0), A.std(0) + 1e-9; Z = {k: (v - mu) / sd for k, v in M.items()}
drama = [k for k in M if k.startswith(("Exagoge", "Sophocles", "Euripides", "Aeschylus"))]; narr = ["Josephus (narrative)", "Philo (exposition)", "Matthew, Mark, Luke"]
dist = lambda a, b: float(np.linalg.norm(Z[a] - Z[b]))
dd = np.mean([dist("John", k) for k in drama]); dn = np.mean([dist("John", k) for k in narr if k in Z])
print(f"   John's mean distance to the plays {dd:.2f}; to narrative / exposition {dn:.2f};  nearest: " + ", ".join(f"{k} {dist('John', k):.2f}" for k in sorted(Z, key=lambda k: dist("John", k))[1:4]))
out["T1"] = dict(profiles={k: v.round(2).tolist() for k, v in M.items()}, to_drama=dd, to_narrative=dn)
print("\nT2. DEIXIS IN THE SAME VERSES AS MOTION / GESTURE")
def verses(code):
    V = collections.OrderedDict()
    for r, w, l, raw in NT[code]: V.setdefault(r, []).append((w, raw))
    return V
for code in ("Jn", "Mt", "Mk", "Lk"):
    V = verses(code); d = np.array([sum(FEAT["behold"](w) or FEAT["here / there / now"](w) or FEAT["motion imperatives"](w) for w, _ in v) for v in V.values()], float)
    m = np.array([sum(FEAT["motion verbs"](w) or FEAT["body / gesture"](w) for w, _ in v) for v in V.values()], float)
    r = np.corrcoef(d, m)[0, 1]; null = [np.corrcoef(rng.permutation(d), m)[0, 1] for _ in range(2000)]
    print(f"   {code}: r = {r:+.3f}  (shuffled {np.mean(null):+.3f}; p = {np.mean(np.array(null) >= r):.3f})")
    out.setdefault("T2", {})[code] = float(r)
print("\nT3. ACTOR TEST: protocol written to performance_actor_protocol.md (requires performers)")
open(os.path.join(HERE, "performance_actor_protocol.md"), "w").write("""# Actor test protocol (T3)
1. Scenes: John 4:1-42 (well), 9:1-41 (blind man), 11:1-44 (Lazarus), 13:1-20 (footwashing), 18:28-19:16 (Pilate), 20:1-18 (tomb); controls: Mark 2:1-12, 5:21-43.
2. Give 6 performers the Greek (or a literal, word-order-preserving English) with no stage directions, scene titles or commentary.
3. Each performer stages the scene alone: records entrances/exits, positions, postures, gestures, objects, timing marks.
4. Score agreement between performers (Krippendorff's alpha) and agreement with the movement track (movement.py) and deixis (performance.py T2).
5. Prediction if John is performance-written: higher agreement on John scenes than on the Mark controls, and blocking that matches the verb track.
""")
print("\nT4. ACTIONS AT THE START OF BREATH GROUPS")
for code in ("Jn", "Mt", "Mk", "Lk"):
    pos_first = tot_first = act_first = act_all = n_all = 0
    grp = []
    for r, w, l, raw in NT[code]:
        grp.append(w)
        if re.search(r"[,.·;:]$", raw):
            for i, x in enumerate(grp):
                a = FEAT["motion verbs"](x) or FEAT["body / gesture"](x); act_all += a; n_all += 1
                if i < 3: act_first += a; tot_first += 1
            grp = []
    share_first = act_first / max(1, act_all); exp = tot_first / n_all
    print(f"   {code}: {share_first:.1%} of actions fall in the first 3 words of a breath group; positions there are {exp:.1%} of all words; ratio {share_first / exp:.2f}")
    out.setdefault("T4", {})[code] = share_first / exp
print("\nS. SHAPE POETRY (line-length shape detector)")
def shape(L):
    L = np.array(L, float); n = len(L); c = np.abs(np.arange(n) - (n - 1) / 2)
    v = np.corrcoef(L, c)[0, 1]; mir = np.corrcoef(L[: n // 2], L[::-1][: n // 2])[0, 1] if n >= 6 else 0
    return v, mir
def null_shape(L, R=2000):
    vs = [abs(shape(list(rng.permutation(L)))[0]) for _ in range(R)]; return vs
x = open(glob.glob(os.path.join(GR, "perseus/data/tlg7000/tlg001/*grc10.xml"))[0], encoding="utf-8").read()
b = re.search(r'subtype="book"[^>]*n="15"', x); seg = x[b.start():]
for ep, name in (("22", "Simias, Axe"), ("24", "Simias, Wings"), ("27", "Simias, Egg"), ("25", "Dosiadas, Altar"), ("26", "Besantinus, Altar")):
    e = re.search(r'<div[^>]*n="%s"[^>]*>(.*?)</div>' % ep, seg, re.S); lines = [re.sub(r"<[^>]+>", "", l) for l in re.split(r"<l\b[^>]*>", e.group(1))]
    L = [len(re.sub(r"[^Ͱ-Ͽἀ-῿]", "", l)) for l in lines if re.search(r"[Ͱ-Ͽἀ-῿]", l)]
    v, mir = shape(L); p = np.mean(np.array(null_shape(L)) >= abs(v))
    print(f"   {name:20s} lines {len(L):2d}  V/Lambda {v:+.2f} (p {p:.3f})  mirror {mir:+.2f}")
def syl(w):
    try: return max(1, len(E.parse_greek(w, "koine")[0]))
    except Exception: return 1
pv = collections.OrderedDict()
for r, w, l, raw in NT["Jn"]:
    if r[0] == 1 and r[1] <= 18: pv[r] = pv.get(r, 0) + syl(w)
v, mir = shape(list(pv.values())); p = np.mean(np.array(null_shape(list(pv.values()))) >= abs(v))
print(f"   {'John 1:1-18 (verses)':20s} lines {len(pv):2d}  V/Lambda {v:+.2f} (p {p:.3f})  mirror {mir:+.2f}   syllables per verse {list(pv.values())}")
pl, cur = [], 0
for l in open(os.path.join(CN, "P75.txt"), encoding="utf-8"):
    m = re.match(r"^43001(\d{3})\s+(.*)$", l.rstrip("\n"))
    if not m or int(m.group(1)) > 18: continue
    for tok in m.group(2).split():
        if (tok.startswith("/") or tok.startswith("\\")) and cur: pl.append(cur); cur = 0
        w = re.sub(r"[^α-ως]", "", tok.replace("ς", "σ")); cur += len(w)
if len(pl) > 6:
    v, mir = shape(pl); p = np.mean(np.array(null_shape(pl)) >= abs(v)); print(f"   {'P75 prologue lines':20s} lines {len(pl):2d}  V/Lambda {v:+.2f} (p {p:.3f})  mirror {mir:+.2f}")
json.dump(out, open(os.path.join(HERE, "performance_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
