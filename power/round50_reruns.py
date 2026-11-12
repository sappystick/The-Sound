#!/usr/bin/env python3
"""Round 50. The pre-registered reruns (robustness/PREREG_R50.md, commit 9912dff), Psalm 24 with Second Temple vowels,
other units of measure, and other texts that fit the mold.
Usage: python3 power/round50_reruns.py
"""
import glob, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
rng = np.random.default_rng(50); SR = E.SR; out = {}; T = os.path.join(ROOT, "sources/texts")
def bare(t): t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if not unicodedata.combining(c)).replace("ς", "σ")
SIMS = np.sort(rng.random((400000, 7)), axis=1)[:, 3]
def p_mid(x): return float((np.abs(SIMS - 0.5) <= abs(x - 0.5)).mean())

# ---------------------------------------------------------------- R1
def ms_lines(ms):
    """cumulative manuscript line count at the start and end of every John verse"""
    seq = []
    for l in open(os.path.join(T, "cntr/class 1", f"{ms}.txt"), encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) < 2 or not p[0].startswith("43"): continue
        seq.append(((int(p[0][2:5]), int(p[0][5:8])), len(re.findall(r"[/|\\]", p[1]))))
    return seq
R1 = {}
for ms in ("01", "03"):
    seq = ms_lines(ms); tot = sum(n for _, n in seq); c = 0; pos = None
    for ref, n in seq:
        if ref == (10, 11): pos = (c + n / 2) / tot
        c += n
    R1[ms] = dict(lines_in_John=tot, verses=len(seq), position=round(pos, 4) if pos is not None else None, p=round(p_mid(pos), 4) if pos is not None else None)
V = {}
for l in open(glob.glob(os.path.join(T, "sblgnt/*-Jn-morphgnt.txt"))[0], encoding="utf-8"):
    p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(re.sub(r"[^α-ω]", "", bare(p[3])))
refs = list(V)
def pos_by(f):
    sizes = [f(V[r]) for r in refs]; cum = np.cumsum([0] + sizes); i = refs.index((10, 11)); x = (cum[i] + cum[i + 1]) / 2 / cum[-1]
    return dict(position=round(float(x), 4), p=round(p_mid(x), 4))
R1["words (secondary)"] = pos_by(len); R1["letters (secondary)"] = pos_by(lambda ws: sum(len(w) for w in ws)); R1["verses (secondary)"] = pos_by(lambda ws: 1)
VOW = set("αεηιουω"); LONGV = set("ηω")
def morae(ws):  # vowel-length weighted: long vowels and diphthongs 2, short 1 (a 'time' measure)
    m = 0
    for w in ws:
        i = 0
        while i < len(w):
            if w[i] in VOW:
                if w[i:i + 2] in ("αι", "ει", "οι", "υι", "αυ", "ευ", "ηυ", "ου"): m += 2; i += 2; continue
                m += 2 if w[i] in LONGV else 1
            i += 1
    return m
R1["morae / spoken time (secondary)"] = pos_by(morae)
R1["pass"] = all(R1[m]["p"] is not None and R1[m]["p"] < 0.05 for m in ("01", "03"))
out["R1"] = R1

# ---------------------------------------------------------------- R2
rev = []
for l in open(glob.glob(os.path.join(T, "sblgnt/*-Re-morphgnt.txt"))[0], encoding="utf-8"):
    p = l.split()
    if bare(p[6]) == "μεσοσ": rev.append(f"{int(p[0][2:4])}:{int(p[0][4:6])}")
RV = {}
for l in open(glob.glob(os.path.join(T, "sblgnt/*-Re-morphgnt.txt"))[0], encoding="utf-8"):
    p = l.split(); RV.setdefault(f"{int(p[0][2:4])}:{int(p[0][4:6])}", []).append(p[3])
LABEL = {  # rule: yes if the one IN the middle is Jesus / the Lamb / one like a son of man (PREREG_R50 R2)
 "1:13": (1, "one like a son of man in the middle of the lampstands"), "2:1": (1, "he who walks in the middle of the seven lampstands"),
 "4:6": (0, "four living creatures in the middle of the throne"), "5:6": (1, "a Lamb standing in the middle of the throne"),
 "6:6": (0, "a voice in the middle of the four living creatures"), "7:17": (1, "the Lamb in the middle of the throne"),
 "22:2": (0, "the tree of life in the middle of the street"), "8:13": (0, "an eagle flying in mid-heaven"), "14:6": (0, "an angel flying in mid-heaven"), "19:17": (0, "birds flying in mid-heaven")}
hits = [(r, LABEL.get(r, (None, " ".join(RV[r])))) for r in rev]
unl = [r for r, (y, _) in hits if y is None]
yes = sum(1 for _, (y, _) in hits if y == 1); n = len(hits); base = 5 / 26
p2 = sum(math.comb(n, k) * base ** k * (1 - base) ** (n - k) for k in range(yes, n + 1))
out["R2"] = dict(occurrences=n, yes=yes, base_rate=round(base, 3), p=round(p2, 4), unlabelled=unl, labels=[(r, y, d) for r, (y, d) in hits], **{"pass": p2 < 0.05 and not unl})

# ---------------------------------------------------------------- R3
spec = __import__("importlib.util").util.spec_from_file_location
src = open(os.path.join(HERE, "round42_sound_machines.py"), encoding="utf-8").read()
lex_block = src[src.index("def nrm(w):"):src.index("chapters = {}")]
ns = {"re": re, "unicodedata": unicodedata}; exec(lex_block, ns); tag, nrm = ns["tag"], ns["nrm"]
chap = {}
for f in sorted(glob.glob(os.path.join(T, "lxx-swete/data/*.txt"))):
    b = os.path.basename(f)[3:-4]
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: chap.setdefault(("OT", b, p[0].split(".")[1]), []).append(nrm(p[1]))
for f in sorted(glob.glob(os.path.join(T, "sblgnt/*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for l in open(f, encoding="utf-8"):
        p = l.split(); chap.setdefault(("NT", b, str(int(p[0][2:4]))), []).append(nrm(p[3]))
NEW = [("OT", "Ezechiel", c) for c in ("9", "37", "40")] + [("OT", "Daniel_Theodotionis_versio", c) for c in ("8", "12")] + \
      [("OT", "Zacharias", c) for c in ("1", "2", "4", "6")] + [("OT", "Joel", "2"), ("OT", "Habacuc", "3")] + [("OT", "Isaias", c) for c in ("24", "29", "66")] + \
      [("NT", "Re", c) for c in ("5", "6", "7", "9", "12", "13", "15", "17", "18", "20", "21", "22")] + [("NT", "Ac", "9"), ("NT", "Ac", "10")]
def tau(x):
    n = len(x); s = sum(np.sign(x[j] - x[i]) for i in range(n) for j in range(i + 1, n)); return s / (n * (n - 1) / 2)
inc = []
for k in NEW:
    ev = tag(chap.get(k, []))
    if len(ev) >= 4 and len({r for _, r in ev}) > 1: inc.append((k, np.array([r for _, r in ev]), [c for c, _ in ev]))
o3 = float(np.mean([tau(a) for _, a, _ in inc])) if inc else float("nan")
n3 = np.array([np.mean([tau(rng.permutation(a)) for _, a, _ in inc]) for _ in range(5000)]) if inc else np.array([0])
p3 = float((n3 >= o3).mean() + 1 / 5000)
out["R3"] = dict(chapters_included=len(inc), mean_signed_tau=round(o3, 3), null_mean=round(float(n3.mean()), 3), p_one_sided=round(p3, 4),
                 detail=[(" ".join(k), round(tau(a), 2), ev) for k, a, ev in inc], **{"pass": o3 > 0 and p3 < 0.05})

# ---------------------------------------------------------------- R4
ORDER = list("ωυοιηεα"); MESE, PAR, LIC = ORDER.index("ι"), ORDER.index("ε"), ORDER.index("ο")
ACC = {}
def last_note(words):
    for w in reversed(words):
        if w not in ACC:
            r = []
            for pw in E.parse_greek(w, "koine"):
                sy = [x for x in pw if x.get("nuc")]; a = next((i for i, x in enumerate(sy) if x["accent"] in ("acute", "grave", "circ")), None)
                for i, x in enumerate(sy):
                    r += [MESE] if (a is None or i < a) else ([PAR, MESE] if (i == a and x["accent"] == "circ") else ([PAR] if i == a else [LIC]))
            ACC[w] = r
        if ACC[w]: return ACC[w][-1]
    return None
LV = {}
for f in sorted(glob.glob(os.path.join(T, "lxx-swete/data/*.txt"))):
    b = os.path.basename(f)[3:-4]
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: LV.setdefault((b, p[0]), []).append(p[1].strip())
isI, cad = [], []
for k, ws in LV.items():
    b = [bare(w).strip(".,;·") for w in ws]
    isI.append(any(b[i] == "εγω" and b[i + 1].startswith("ειμι") for i in range(len(b) - 1))); cad.append(last_note(ws))
isI = np.array(isI); cad = np.array([c if c is not None else -1 for c in cad])
a4 = int((cad[isI] == MESE).sum()); n4 = int(isI.sum()); base4 = float((cad[~isI] == MESE).mean())
p4 = sum(math.comb(n4, k) * base4 ** k * (1 - base4) ** (n4 - k) for k in range(a4, n4 + 1))
out["R4"] = dict(i_am_verses=n4, on_mese=a4, rate=round(a4 / max(1, n4), 3), base_rate=round(base4, 3), p=round(p4, 4), **{"pass": p4 < 0.05})

# Holm across R1 (max p of 01/03), R2, R3, R4
ps = {"R1": max(R1["01"]["p"], R1["03"]["p"]), "R2": out["R2"]["p"], "R3": p3, "R4": p4}
order = sorted(ps, key=ps.get); holm = {}; prev = 0
for i, k in enumerate(order):
    v = min(1.0, max(prev, (4 - i) * ps[k])); holm[k] = round(v, 4); prev = v
out["holm"] = dict(raw={k: round(v, 4) for k, v in ps.items()}, adjusted=holm, survive=[k for k, v in holm.items() if v < 0.05])

# ---------------------------------------------------------------- S5 (secondary)
r46 = open(os.path.join(HERE, "round46_letters_accent_language.py"), encoding="utf-8").read()
blk = r46[r46.index("SYR_V = set"):r46.index("res_B = {}")]
ns2 = {"re": re, "np": np, "math": math, "os": os, "rng": rng, "ROOT": ROOT, "bare": bare, "glob": glob,
       "verses": lambda code: {(int(l.split()[0][2:4]), int(l.split()[0][4:6])): None for l in []}}
def verses_g(code):
    W = {}
    for l in open(glob.glob(os.path.join(T, f"sblgnt/*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); W.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(p[3])
    return W
ns2["verses"] = verses_g; exec(blk, ns2)
did_src = r46[r46.index("def did("):r46.index('res_B["john_power_sayings_DiD"]')]; exec(did_src, ns2)
S5 = {}
for code, book in (("Mt", "Matthew"), ("Lk", "Luke")):
    W = verses_g(code)
    power = {r for r, ws in W.items() for i in range(len(ws) - 1) if bare(ws[i]).strip(".,;·") == "αμην" and bare(ws[i + 1]).startswith("λεγ")}
    S5[code] = ns2["did"](ns2["zscores"](ns2["greek_vs"](code), "greek"), ns2["zscores"](ns2["syriac_vs"](book), "syriac"), power)
out["S5_secondary"] = S5

# ---------------------------------------------------------------- Psalm 24 with Second Temple vowels
R41 = json.load(open(os.path.join(HERE, "round41_results.json")))["instrument"]["heptachord_lyre"]
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
STR = {s["vowel"]: s for s in R41}
V2GK = {"a": "α", "ɑ": "α", "e": "η", "ɛ": "ε", "i": "ι", "o": "ο", "ɔ": "α", "u": "υ", "ə": "ε", "y": "υ"}   # qamets -> long a
V2TUBE = {"a": "a", "ɑ": "a", "e": "e", "ɛ": "ɛ", "i": "i", "o": "o", "ɔ": "a", "u": "o", "ə": "ɛ", "y": "y"}
ps = open(os.path.join(T, "morphhb/wlc/Ps.xml"), encoding="utf-8").read()
def verse(v):
    m = re.search(rf'<verse osisID="Ps\.24\.{v}">(.*?)</verse>', ps, re.S)
    return " ".join(w for w in (re.sub(r"[֑-ֽ֯׀׃/]", "", re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<w[^>]*>(.*?)</w>", m.group(1))) if w)
def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, b in zip(freqs, bws): bb, aa = E.resonator_coeffs(f, b); y += lfilter(bb, aa, x)
    return y
def pluck(f0, n):
    tt = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 30):
        if k * f0 > 8000: break
        y += np.sin(2 * np.pi * k * f0 * tt) * abs(math.sin(k * math.pi * 0.2)) / k * np.exp(-tt * (1.2 + 0.5 * k))
    return y
def play(text, beat=0.36):
    seq, o = [], []
    for w in E.parse_hebrew(text, "tiberian"):
        for s in w:
            if not s.get("nuc"): continue
            v = s["nuc"][0].rstrip("ː"); g = V2GK.get(v, "α"); st = STR[g]
            long_ = v == "ɔ" or s.get("long") or s["nuc"][0].endswith("ː")
            n = int(beat * (0.5 if v == "ə" else (2 if long_ else 1)) * SR)
            tone = pluck(st["Hz"], n); sp = resonate(tone, R42[V2TUBE.get(v, "a")]["machine"])
            o.append(0.45 * tone / (np.abs(tone).max() + 1e-9) + 0.55 * sp / (np.abs(sp).max() + 1e-9)); seq.append(st["string"])
        o.append(np.zeros(int(0.1 * SR)))
    return np.concatenate(o), seq
YEV = 0.30
def blast(d): return E.inst_brass(233.0, 233.0, int(d * SR), bright=1.3)
def gap(s): return np.zeros(int(s * SR))
nm = E.norm
parts = [nm(np.concatenate([blast(9 * YEV), gap(0.25)] + [np.concatenate([blast(YEV * 0.8), gap(YEV * 0.2)]) for _ in range(3)] + [gap(0.25), blast(9 * YEV)])), gap(0.6), nm(E.inst_cymbal(), 0.8), gap(0.8)]
allseq = []
for a, b in [(1, 2), (3, 6), (7, 10)]:
    y, s = play(" ".join(verse(v) for v in range(a, b + 1))); allseq += s; parts += [nm(y), gap(0.5), nm(blast(9 * YEV)), gap(2.0)]
y = E.reverb(nm(np.concatenate(parts)), "temple")
wav = os.path.join(HERE, "audio", "r50_tamid_psalm24_lyre_second_temple.wav"); wavfile.write(wav, SR, (nm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
out["psalm24_second_temple"] = dict(file=os.path.relpath(mp3, ROOT), string_shares={s["string"]: round(allseq.count(s["string"]) / len(allseq), 3) for s in R41},
    rule="qamets = long a (Moon string); shewa = short e; other vowels as Tiberian (sources: Origen's Secunda and LXX transcriptions, which write qamets as alpha)")

# ---------------------------------------------------------------- what also fits the mold
def find(path, kws, span=600):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(path, encoding="utf-8").read())); b = bare(t); hits = []
    for kw in kws:
        i = b.find(kw)
        if i >= 0: hits.append((kw, t[max(0, i - span // 2):i + span // 2]))
    return hits
mold = {}
jos = glob.glob(os.path.join(T, "perseus/data/tlg0526/tlg001/*grc*.xml"))
if jos: mold["Josephus, Antiquities 3 (the menorah)"] = find(jos[0], ["λυχνους επτα", "των πλανητων"], 700)[:2]
war = glob.glob(os.path.join(T, "perseus/data/tlg0526/tlg004/*grc*.xml"))
if war: mold["Josephus, War 5.217"] = find(war[0], ["οι μεν γαρ επτα λυχνοι", "επτα λυχνοι"], 500)[:1]
phil = [f for f in glob.glob(os.path.join(T, "f1k/data/tlg0018/*/*.xml"))]
ph = []
for f in phil:
    h = find(f, ["μεσος των εξ", "ο ηλιοσ μεσοσ", "μεσον των επτα", "ηλιον μεσον"], 700)
    if h: ph.append((os.path.basename(f), h[0]))
mold["Philo (sun in the middle of the seven)"] = ph[:3]
wl = open(os.path.join(T, "morphhb/wlc/Gen.xml"), encoding="utf-8").read()
gen = []
for v in [f"Gen.1.{i}" for i in range(1, 32)] + ["Gen.2.1", "Gen.2.2", "Gen.2.3"]:
    m = re.search(rf'<verse osisID="{v}">(.*?)</verse>', wl, re.S); gen.append((v, len(re.findall(r"<w[^>]*>", m.group(1)))))
cum = np.cumsum([0] + [n for _, n in gen]); idx = {v: i for i, (v, _) in enumerate(gen)}
d4 = (cum[idx["Gen.1.14"]] + cum[idx["Gen.1.19"] + 1]) / 2 / cum[-1]
mold["Genesis 1:1-2:3, day 4 (sun, moon, stars) by words"] = dict(position=round(float(d4), 3), p=round(p_mid(float(d4)), 3))
mold["Chaldean planetary order"] = "Saturn, Jupiter, Mars, SUN, Venus, Mercury, Moon: the Sun is 4th of 7, the middle (Ptolemy, Almagest 9.1; the order behind Nicomachus' strings)"
out["mold"] = mold
json.dump(out, open(os.path.join(HERE, "round50_results.json"), "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
for k in ("R1", "R2", "R4", "holm", "S5_secondary", "psalm24_second_temple"): print(k, json.dumps(out[k], ensure_ascii=False, default=str)[:900])
print("R3", {k: v for k, v in out["R3"].items() if k != "detail"}); print([d[:2] for d in out["R3"]["detail"]])
for k, v in mold.items(): print("MOLD", k, json.dumps(v, ensure_ascii=False, default=str)[:700])
