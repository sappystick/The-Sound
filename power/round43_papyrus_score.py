#!/usr/bin/env python3
"""Round 43. The papyrus as a score.

Sources read this round: P.Oxy. XV 1786 (Grenfell & Hunt 1922: Christian hymn, late 3rd c., Oxyrhynchus, Greek vocal
notes written above each text line, with signs for length, slur, rest and beat); Clement, Protrepticus 1.5 (the Logos
plays the cosmos and the human as a 'many-voiced instrument': lyre for harmony, aulos for breath, temple for word);
Berakhot 3b (David's lyre played at midnight by the north wind); Odes of Solomon 6, 7, 14, 26 (harp of the Spirit).

A. Is the papyrus laid out by sound? Where P66, P75, 01 and 03 split a word at a line end, does the split fall at a
   spoken syllable boundary (maximal onset: the next line starts with a consonant cluster that can begin a Greek
   word)? Null: random split positions in the same words.
B. Letters as notes. In Greek vocal notation the notes ARE letters. Read every syllable's vowel letter as its Alypius
   note (approximate Lydian table, round 41) and measure the melody (share of steps <= 2 semitones). Is any text's
   letter-melody smoother than its own syllables shuffled? Texts: John, Mark, Revelation (NT); Psalms, Odes, Genesis (LXX).
C. The self-playing lyre (Berakhot 3b; Odes 6). Wind across a string sheds vortices at f = St * v / d (St ~ 0.2) and
   locks onto the nearest string harmonic: which harmonics does a night wind play on the planetary heptachord?
D. A two-line score of P66 John 1:1-5 in the layout of P.Oxy. 1786: notes above syllables. Melody by the ancient
   accent rule (accented syllable highest, the rise before, the fall after; a circumflex takes two notes), length by
   vowel quantity, a rest at each papyrus line end, sacred names held long (READING: in 1786 the same overline marks
   a long note). Played by the round-42 speaking machine. A second version reads the vowel letters as notes.
Usage: python3 power/round43_papyrus_score.py [--no-audio]
"""
import glob, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
rng = np.random.default_rng(43); SR = E.SR; out = {}
VOW = set("αεηιουω"); DIPH = {"αι", "ει", "οι", "υι", "αυ", "ευ", "ηυ", "ου"}
def bare(t):
    t = unicodedata.normalize("NFD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    return t.replace("ς", "σ")

# ---------------------------------------------------------------- A. syllabic line division
NT = {}
for f in sorted(glob.glob(os.path.join(ROOT, "sources/texts/sblgnt/*-morphgnt.txt"))):
    for l in open(f, encoding="utf-8"): w = re.sub(r"[^α-ω]", "", bare(l.split()[3])); NT[w] = 1
ONSETS = {""}
for w in NT:
    m = re.match(r"[^αεηιουω]*", w).group(0); ONSETS.add(m)
def nuclei(w):
    s, i = [], 0
    while i < len(w):
        if w[i] in VOW:
            if w[i:i + 2] in DIPH: s.append((i, 2)); i += 2
            else: s.append((i, 1)); i += 1
        else: i += 1
    return s
def max_onset_splits(w):
    """legal syllable boundaries by maximal onset"""
    nu = nuclei(w); ok = set()
    for (a, la), (b, _) in zip(nu, nu[1:]):
        gap = w[a + la:b]
        for k in range(len(gap) + 1):
            if gap[k:] in ONSETS: ok.add(a + la + k); break
    return ok
res_A = {}
for ms in ("P66", "P75", "01", "03"):
    f = os.path.join(ROOT, "sources/texts/cntr/class 1", f"{ms}.txt")
    if not os.path.exists(f): continue
    hit = n = 0; rnd = []
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) < 2 or not p[0].startswith("43"): continue   # John only
        for tok in p[1].split():
            t = re.sub(r"[^α-ωϲ/]", "", bare(tok).replace("ϲ", "σ"))
            if "/" not in t.strip("/"): continue
            k = t.strip("/").index("/"); w = t.replace("/", "")
            if k <= 0 or k >= len(w) or len(nuclei(w)) < 2: continue
            legal = max_onset_splits(w); n += 1; hit += k in legal
            rnd.append(len(legal) / (len(w) - 1))
    if n: res_A[ms] = dict(word_splits=n, at_syllable_boundary=round(hit / n, 3), random_split_expected=round(float(np.mean(rnd)), 3),
                          p_binomial=float(f"{sum(math.comb(n, j) * np.mean(rnd) ** j * (1 - np.mean(rnd)) ** (n - j) for j in range(hit, n + 1)):.2e}"))
out["A_line_division"] = res_A

# ---------------------------------------------------------------- B. letters as notes
MESE = 220.0; ALPHA = "αβγδεζηθικλμνξοπρστυφχψω"; BASES = [32 / 27, 9 / 8, 1.0, 8 / 9, 64 / 81, 3 / 4, 2 / 3, 16 / 27]
def alypius(ch): i = ALPHA.index(ch); t, pos = divmod(i, 3); return MESE * BASES[t] * 2 ** ((2 - pos) / 24)
def semis(f): return 12 * math.log2(f / MESE)
def verses_nt(code):
    V = {}
    for l in open(glob.glob(os.path.join(ROOT, f"sources/texts/sblgnt/*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault(p[0], []).append(re.sub(r"[^α-ω]", "", bare(p[3])))
    return list(V.values())
def verses_lxx(name):
    V = {}
    for l in open(os.path.join(ROOT, f"sources/texts/lxx-swete/data/{name}.txt"), encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: V.setdefault(p[0], []).append(re.sub(r"[^α-ω]", "", bare(p[1])))
    return list(V.values())
def vowel_line(words): return [w[a] for w in words for a, _ in nuclei(w)]
def stepwise(notes):
    s = [semis(alypius(c)) for c in notes]; d = np.abs(np.diff(s)); return float((d <= 2.0).mean()) if len(d) else np.nan
TEXTS = {"John": verses_nt("Jn"), "Mark": verses_nt("Mk"), "Revelation": verses_nt("Re"),
         "Psalms (LXX)": verses_lxx("27.Psalmi"), "Odes (LXX canticles)": verses_lxx("28.Odae"), "Genesis (LXX)": verses_lxx("01.Genesis")}
res_B = {}
for name, vs in TEXTS.items():
    idx = rng.choice(len(vs), min(400, len(vs)), replace=False)
    obs, nul = [], []
    for i in idx:
        nl = vowel_line(vs[i])
        if len(nl) < 8: continue
        obs.append(stepwise(nl)); nul.append(np.mean([stepwise(list(rng.permutation(nl))) for _ in range(20)]))
    obs, nul = np.array(obs), np.array(nul); d = obs - nul
    res_B[name] = dict(verses=len(obs), stepwise_share=round(float(obs.mean()), 4), shuffled=round(float(nul.mean()), 4),
                       diff=round(float(d.mean()), 4), z=round(float(d.mean() / (d.std(ddof=1) / math.sqrt(len(d)))), 2))
out["B_letters_as_notes"] = res_B

# ---------------------------------------------------------------- C. the self-playing lyre
R41 = json.load(open(os.path.join(HERE, "round41_results.json")))["instrument"]["heptachord_lyre"]
aeol = []
for s in R41:
    f0 = s["Hz"]; row = dict(string=s["string"], vowel=s["vowel"], planet=s["planet"], f0=f0)
    for d_mm in (0.8, 1.2):
        row[f"d{d_mm}mm"] = {f"{v} m/s": max(1, round(0.2 * v / (d_mm / 1000) / f0)) for v in (1.5, 3, 5, 8)}
    aeol.append(row)
out["C_aeolian_lyre"] = dict(strings=aeol, rule="vortex shedding f = 0.2 v / d locks onto the nearest string harmonic n = round(f / f0); gut strings 0.8-1.2 mm",
                             texts={"Berakhot 3b": "a lyre hung over David's bed; at midnight the north wind blew on it and it played by itself",
                                    "Odes of Solomon 6:1 (Harris 1909)": "as the hand moves over the harp and the strings speak, so speaks in my members the Spirit of the Lord",
                                    "Clement, Protrepticus 1.5": "the Logos ... tuned the cosmos and man, soul and body, by the Holy Spirit, and plays to God on the many-voiced instrument: 'you are my lyre, aulos and temple'"})

# ---------------------------------------------------------------- D. the two-line score of P66 John 1:1-5
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
FORM = {v: d["machine"] for v, d in R42.items()}
SBL15 = []
for l in open(glob.glob(os.path.join(ROOT, "sources/texts/sblgnt/*-Jn-morphgnt.txt"))[0], encoding="utf-8"):
    p = l.split()
    if p[0] in ("040101", "040102", "040103", "040104", "040105"): SBL15.append(p[3])
P66 = [l.split(maxsplit=1)[1].strip() for l in open(os.path.join(ROOT, "sources/texts/cntr/class 1/P66.txt"), encoding="utf-8") if l[:8] in ("43001001", "43001002", "43001003", "43001004", "43001005")]
p66_words = [re.sub(r"[^α-ω=/]", "", bare(t)) for line in P66 for t in line.split()]
p66_words = [w for w in p66_words if re.sub(r"[=/]", "", w)]
sacred = [("=" in w) for w in p66_words]; linebreak_before = [w.startswith("/") for w in p66_words]
NAMES = {"θν": "θεον", "θσ": "θεοσ", "θυ": "θεου"}
SC = {"e3": 165.0, "g3": 195.6, "a3": 220.0, "c4": 260.7, "d4": 293.3}
def nearest_sign(f): return min(ALPHA, key=lambda c: abs(semis(alypius(c)) - semis(f))).upper()
words = E.parse_greek(" ".join(SBL15), "koine"); score = []
for wi, w in enumerate(words):
    acc = next((i for i, s in enumerate(w) if s["accent"]), None)
    hold = 2.0 if wi < len(sacred) and sacred[wi] else 1.0
    rest = wi < len(linebreak_before) and linebreak_before[wi]
    for si, s in enumerate(w):
        if acc is None: pitches = ["a3"]
        elif si == acc: pitches = ["c4", "a3"] if s["accent"] in ("circ", "circumflex", "perispomenon") else ["c4"]
        elif si < acc: pitches = ["a3"]
        else: pitches = ["g3"]
        L = (2.0 if s.get("long") else 1.0) * hold
        score.append(dict(word=wi, syl="".join(s["ph"]), nuc=s["nuc"][0].rstrip("ː"), pitches=[SC[p] for p in pitches],
                          signs=[nearest_sign(SC[p]) for p in pitches], beats=L, rest_before=rest and si == 0, sacred=hold > 1))
score[-1]["pitches"] = [SC["e3"]]; score[-1]["signs"] = [nearest_sign(SC["e3"])]   # final cadence
note_line = " ".join(("‖ " if s["rest_before"] else "") + "".join(s["signs"]) + ("¯" if s["beats"] >= 2 else "") for s in score)
text_line = " ".join(("‖ " if s["rest_before"] else "") + s["syl"] for s in score)
out["D_score_P66_John_1_1_5"] = dict(note_line=note_line, text_line=text_line, p66_unspaced=" / ".join(P66), syllables=len(score),
    rules="accent rule (pre-classical and Delphic practice: Devine & Stephens 1994; West 1992); vowel quantity; rest at P66 line ends; sacred names x2 (Reading)")
def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, b in zip(freqs, bws): bb, aa = E.resonator_coeffs(f, b); y += lfilter(bb, aa, x)
    return y
def reed(f0, n):
    t = np.arange(n) / SR; ph = (f0 * t) % 1.0; return np.exp(-ph * 9) - 0.11
def nuc_formants(v): return FORM.get(v, FORM.get({"ɑ": "a", "ɛː": "ɛ", "ɔː": "ɔ"}.get(v, "a"), FORM["a"]))
def render(seq, beat=0.32):
    y = []
    for s in seq:
        if s["rest_before"]: y.append(np.zeros(int(0.35 * SR)))
        for i, f in enumerate(s["pitches"]):
            n = int(beat * s["beats"] / len(s["pitches"]) * SR)
            y.append(resonate(reed(f, n), nuc_formants(s["nuc"])) * E.env_adsr(n, 0.03, 0.06))
    y = np.concatenate(y); return E.reverb(y / (np.abs(y).max() + 1e-9), "kings_chamber" if False else "synagogue")
rend = []
if "--no-audio" not in sys.argv:
    for tag, seq in (("accent", score), ("letters_as_notes", [dict(s, pitches=[alypius(next((c for c in bare(s['syl']) if c in VOW), "α")) if False else alypius({"a": "α", "ɛ": "ε", "e": "η", "i": "ι", "o": "ο", "y": "υ", "ɔ": "ω", "u": "ο"}.get(s["nuc"], "α"))]) for s in score])):
        y = render(seq); wav = os.path.join(HERE, "audio", f"r43_p66_john1_{tag}.wav")
        wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16)); mp3 = wav[:-4] + ".mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav); rend.append(os.path.relpath(mp3, ROOT))
    # the self-playing lyre: midnight wind gusting 1.5-5 m/s over the seven strings (0.8 mm gut)
    T = 24; t = np.arange(T * SR) / SR; v = 3.2 + 1.6 * np.sin(2 * np.pi * t / 9.0) + 0.6 * np.sin(2 * np.pi * t / 3.7); y = np.zeros_like(t)
    for s in R41:
        f0 = s["Hz"]; n = np.clip(np.round(0.2 * v / 0.0008 / f0), 1, 24)
        ph = 2 * np.pi * np.cumsum(n * f0) / SR; gate = 0.5 + 0.5 * np.sin(2 * np.pi * t / (5 + rng.uniform(0, 4)) + rng.uniform(0, 6))
        y += np.sin(ph) * gate ** 2 * (1 / np.sqrt(n))
    y = E.reverb(E.norm(y) * np.minimum(1, t / 3) * np.minimum(1, (T - t) / 3), "house_church")
    wav = os.path.join(HERE, "audio", "r43_aeolian_lyre_midnight.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
    mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav); rend.append(os.path.relpath(mp3, ROOT))
out["renders"] = rend
json.dump(out, open(os.path.join(HERE, "round43_results.json"), "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps(out["A_line_division"], indent=0)); print(json.dumps(res_B, indent=0, ensure_ascii=False))
for r in aeol: print(r)
print(note_line[:400]); print(text_line[:400]); print(rend)
