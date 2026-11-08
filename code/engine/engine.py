#!/usr/bin/env python3
"""
Ancient Sound Engine
====================
Reconstructs and synthesizes how a Greek or Hebrew word (or phrase) most
plausibly *sounded* in antiquity -- its phonemes, its pitch melody, its
duration pattern -- and how it would have been delivered in different
settings (ordinary speech, public declamation, liturgical chant, temple
ritual with instruments).  It also renders the same word on reconstructed
period instruments and on a new instrument, the *phonaulos*, a reed pipe
whose resonator follows the word's own vowel formants so the instrument
"speaks" the word without a human voice.

Everything is synthesized from first principles (formant synthesis +
additive/physical-model instruments); there are no samples.  See
RESEARCH.md for the evidence behind every rule and what is uncertain.

Usage
-----
  python3 engine.py --text "λόγος" --lang greek --era koine --mode chant
  python3 engine.py --text "שָׁלוֹם" --lang hebrew --mode ritual --ensemble temple
  python3 engine.py --phonemes "ˈa b a" --mode chant     # any language via IPA tokens
  python3 engine.py --demo                                  # render the demo set
"""
import argparse, json, math, os, sys, unicodedata
import numpy as np
from scipy.signal import lfilter, butter, fftconvolve
from scipy.io import wavfile

SR = 44100
RNG = np.random.default_rng(7)

# ---------------------------------------------------------------------------
# 1. PHONEME INVENTORY  (adult male voice formant targets, Hz)
# ---------------------------------------------------------------------------
VOWELS = {  # symbol: (F1, F2, F3)
    "i": (270, 2290, 3010), "y": (270, 1850, 2250), "e": (400, 2100, 2700),
    "ɛ": (550, 1850, 2600), "a": (730, 1250, 2500), "ɑ": (700, 1100, 2450),
    "ɔ": (570, 840, 2410),  "o": (450, 800, 2400),  "u": (300, 870, 2240),
    "ə": (500, 1500, 2500),
}
# consonant: kind, extra params
#  kind: stop(voiced?), fric(voiced?, center, bw), nasal, liquid, trill, h, glottal, approx
CONS = {
    "p": ("stop", False, 900),  "b": ("stop", True, 900),
    "t": ("stop", False, 3500), "d": ("stop", True, 3500),
    "k": ("stop", False, 1800), "g": ("stop", True, 1800),
    "q": ("stop", False, 1200), "tˤ": ("stop", False, 2800),
    "pʰ": ("asp", False, 900), "tʰ": ("asp", False, 3500), "kʰ": ("asp", False, 1800),
    "f": ("fric", False, 5000, 4000), "v": ("fric", True, 4000, 3000),
    "θ": ("fric", False, 6000, 4000), "ð": ("fric", True, 5000, 3000),
    "s": ("fric", False, 6500, 2500), "z": ("fric", True, 6000, 2500),
    "sˤ": ("fric", False, 5200, 2500), "ʃ": ("fric", False, 3200, 1800),
    "x": ("fric", False, 1600, 1200), "ɣ": ("fric", True, 1500, 1200),
    "χ": ("fric", False, 1200, 900),
    "ħ": ("fric", False, 1100, 1400), "ʕ": ("pharyngeal", True),
    "h": ("h",), "ʔ": ("glottal",),
    "m": ("nasal", (250, 1100, 2300)), "n": ("nasal", (250, 1600, 2600)),
    "ŋ": ("nasal", (250, 2000, 2700)),
    "l": ("liquid", (360, 1100, 2700)), "r": ("trill", (450, 1300, 1700)),
    "r̥": ("trill_vl", (450, 1300, 1700)),
    "w": ("approx", (300, 700, 2300)), "j": ("approx", (280, 2200, 2900)),
}
ALIASES = {"ps": ["p", "s"], "ks": ["k", "s"], "zd": ["z", "d"], "ts": ["t", "s"]}

# ---------------------------------------------------------------------------
# 2. GREEK  (polytonic Unicode -> phonemes + prosody)
# ---------------------------------------------------------------------------
ACUTE, GRAVE, CIRC = "́", "̀", "͂"
ROUGH, SMOOTH, IOTA_SUB, DIAER = "̔", "̓", "ͅ", "̈"
GK_VOWELS = set("αεηιουω")

GK_ATTIC = {  # Classical Attic, 5th c. BCE (W.S. Allen, Vox Graeca)
    "α": "a", "ε": "e", "η": "ɛː", "ι": "i", "ο": "o", "υ": "y", "ω": "ɔː",
    "ει": "eː", "ου": "oː", "αι": "a i", "οι": "o i", "υι": "y i",
    "αυ": "a u", "ευ": "e u", "ηυ": "ɛː u",
    "β": "b", "γ": "g", "δ": "d", "ζ": "zd", "θ": "tʰ", "κ": "k", "λ": "l",
    "μ": "m", "ν": "n", "ξ": "ks", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
    "τ": "t", "φ": "pʰ", "χ": "kʰ", "ψ": "ps",
}
GK_KOINE = {  # Koine c. 1st c. CE (Allen; Teodorsson; Buth's reconstruction)
    "α": "a", "ε": "ɛ", "η": "e", "ι": "i", "ο": "o", "υ": "y", "ω": "o",
    "ει": "iː", "ου": "uː", "αι": "ɛ", "οι": "y", "υι": "y",
    "αυ": "a v", "ευ": "ɛ v", "ηυ": "e v",
    "β": "v", "γ": "ɣ", "δ": "ð", "ζ": "z", "θ": "θ", "κ": "k", "λ": "l",
    "μ": "m", "ν": "n", "ξ": "ks", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
    "τ": "t", "φ": "pʰ", "χ": "kʰ", "ψ": "ps",
}
GK_KOINE["θ"] = "tʰ"
# Late Koine (c. 2nd-4th c. CE and after): aspirates have become fricatives
GK_KOINE_LATE = dict(GK_KOINE, **{"θ": "θ", "φ": "f", "χ": "x", "η": "i", "ηυ": "i v", "υ": "i", "οι": "i"})  # iotacism


def parse_greek(text, era):
    """Return list of words; each word = list of syllable-units:
       {"ph": [phonemes], "accent": None|'acute'|'grave'|'circ', "long": bool}"""
    table = GK_ATTIC if era == "attic" else (GK_KOINE_LATE if era == "koine-late" else GK_KOINE)
    words = []
    for raw in text.split():
        nfd = unicodedata.normalize("NFD", raw.lower())
        # cluster: base char + combining marks
        cl = []
        for ch in nfd:
            if unicodedata.combining(ch) and cl:
                cl[-1][1].add(ch)
            elif ch.isalpha():
                cl.append([ch, set()])
        units, i = [], 0  # units = list of (kind, phonemes, marks)
        while i < len(cl):
            ch, marks = cl[i]
            nxt = cl[i + 1] if i + 1 < len(cl) else None
            if ch in GK_VOWELS:
                if nxt and nxt[0] in "ιυ" and DIAER not in nxt[1] and (ch + nxt[0]) in table:
                    allm = marks | nxt[1]
                    units.append(("V", table[ch + nxt[0]], allm, True))
                    i += 2
                    continue
                ph = table[ch]
                long_ = ("ː" in ph) or (CIRC in marks) or (IOTA_SUB in marks)
                if IOTA_SUB in marks and era == "attic":
                    ph = ph.replace("ː", "") + "ː i" if "ː" not in ph else ph + " i"
                units.append(("V", ph, marks, long_))
            else:
                if ch == "γ" and nxt and nxt[0] in "γκξχ":
                    units.append(("C", "ŋ", marks, False))
                else:
                    ph = table.get(ch, "")
                    if ch == "ρ" and ROUGH in marks and era == "attic":
                        ph = "r̥"
                    if ph:
                        units.append(("C", ph, marks, False))
            i += 1
        # rough breathing -> h (Attic only; lost by Koine)
        if era == "attic" and units and units[0][0] == "V" and ROUGH in units[0][2]:
            units.insert(0, ("C", "h", set(), False))
        # Koine: σ before voiced consonant -> z
        out = []
        for k, (kind, ph, marks, lg) in enumerate(units):
            if era.startswith("koine") and ph == "s" and k + 1 < len(units) and units[k + 1][1] in ("m", "v", "ð", "ɣ", "b", "d", "g"):
                ph = "z"
            out.append((kind, ph, marks, lg))
        sy = syllabify(out, greek=True, era=era)
        for x in sy:  # Koine: grave = stress, except on light monosyllables (καὶ, πρὸς, τὸν) which lean on the next word
            if x["accent"] == "gravek": x["accent"] = None if len(sy) == 1 else "acute"
        words.append(sy)
    return words


def syllabify(units, greek=True, era="koine"):
    """Group units into syllables (onset consonants attach to following vowel)."""
    sylls, onset = [], []
    for kind, ph, marks, lg in units:
        toks = expand(ph)
        if kind == "C":
            onset += toks
        else:
            acc = None
            if ACUTE in marks: acc = "acute"
            elif CIRC in marks: acc = "circ"
            elif GRAVE in marks: acc = "gravek" if era.startswith("koine") else "grave"  # stress accent: grave = acute
            sylls.append({"ph": onset + toks, "accent": acc, "long": lg, "nuc": toks})
            onset = []
    if onset:
        if sylls: sylls[-1]["ph"] += onset
        else: sylls.append({"ph": onset, "accent": None, "long": False, "nuc": []})
    # move all-but-last onset consonant to previous syllable coda (simple rule)
    for k in range(1, len(sylls)):
        ph = sylls[k]["ph"]
        nuc0 = ph.index(sylls[k]["nuc"][0]) if sylls[k]["nuc"] else len(ph)
        ons = ph[:nuc0]
        if len(ons) >= 2 and not (ons[-1] in ("r", "l") and len(ons) == 2):
            move = ons[:-1]
            sylls[k - 1]["ph"] += move
            sylls[k]["ph"] = ph[len(move):]
    return sylls


def expand(ph):
    out = []
    for t in ph.split():
        long_ = t.endswith("ː")
        base = t[:-1] if long_ else t
        if base in ALIASES:
            out += ALIASES[base]
        else:
            out.append(base + ("ː" if long_ else ""))
    return out

# ---------------------------------------------------------------------------
# 3. HEBREW  (pointed Unicode -> phonemes + stress)
# ---------------------------------------------------------------------------
HB_VOWEL = {"ְ": "ə", "ֱ": "ɛ̆", "ֲ": "ă", "ֳ": "ɔ̆", "ִ": "i",
            "ֵ": "eː", "ֶ": "ɛ", "ַ": "a", "ָ": "aː", "ֹ": "oː",
            "ֺ": "oː", "ֻ": "u", "ׇ": "ɔ"}
DAGESH, SHIN_DOT, SIN_DOT, METEG = "ּ", "ׁ", "ׂ", "ֽ"
HB_CONS = {"א": "ʔ", "ב": ("b", "v"), "ג": ("g", "ɣ"), "ד": ("d", "ð"), "ה": "h",
           "ו": "w", "ז": "z", "ח": "ħ", "ט": "tˤ", "י": "j", "כ": ("k", "x"),
           "ך": ("k", "x"), "ל": "l", "מ": "m", "ם": "m", "נ": "n", "ן": "n",
           "ס": "s", "ע": "ʕ", "פ": ("p", "f"), "ף": ("p", "f"), "צ": "sˤ",
           "ץ": "sˤ", "ק": "q", "ר": "r", "ש": "ʃ", "ת": ("t", "θ")}


def parse_hebrew(text, era):
    words = []
    for raw in text.replace("־", " ").split():
        cl = []
        for ch in raw:
            if "א" <= ch <= "ת":
                cl.append([ch, set()])
            elif cl and unicodedata.combining(ch):
                cl[-1][1].add(ch)
        units, stress_idx = [], None
        for i, (ch, m) in enumerate(cl):
            last = i == len(cl) - 1
            vowel = next((HB_VOWEL[x] for x in m if x in HB_VOWEL), None)
            if vowel == "aː" and era == "tiberian": vowel = "ɔː"
            cant = any("֑" <= x <= "֯" for x in m)
            # matres lectionis / vowel letters
            if ch == "ו" and DAGESH in m and vowel is None and i > 0:
                units.append(("V", "uː", cant)); continue
            if ch == "ו" and "ֹ" in m and i > 0 and vowel == "oː" and not any(x in m for x in ("ְ", "ַ", "ָ")):
                units.append(("V", "oː", cant)); continue
            if ch == "י" and vowel is None and units and units[-1][0] == "V" and units[-1][1] in ("i", "eː", "ɛ"):
                if units[-1][1] == "i": units[-1] = ("V", "iː", units[-1][2])
                continue
            nxt = cl[i + 1] if i + 1 < len(cl) else None
            if ch == "א" and vowel is None and i > 0 and not (nxt and nxt[0] == "ו" and ("ֹ" in nxt[1] or DAGESH in nxt[1])):
                continue
            if ch == "ה" and last and vowel is None and DAGESH not in m: continue
            c = HB_CONS[ch]
            if isinstance(c, tuple):
                c = c[0] if DAGESH in m else c[1]
            if ch == "ש": c = "s" if SIN_DOT in m else "ʃ"
            # furtive patah: vowel precedes final guttural
            if last and vowel == "a" and ch in "חעה":
                units.append(("V", "ă", False)); units.append(("C", c, False)); continue  # furtive patah: never stressed
            gem = DAGESH in m and i > 0 and vowel is not None and units and units[-1][0] == "V" and ch not in "בגדכפת"
            if gem: units.append(("C", c, False))
            units.append(("C", c, False))
            if vowel == "ə":
                # vocal sheva at word start or after another consonant cluster; silent otherwise
                prev_v = units[-2][0] == "V" if len(units) >= 2 else False
                if i == 0 or (len(units) >= 2 and units[-2][0] == "C" and not gem):
                    units.append(("V", "ə", cant))
                continue
            if vowel: units.append(("V", vowel, cant))
        # stress: syllable carrying a cantillation mark, else final (milra)
        sylls, onset = [], []
        for kind, ph, cant in units:
            if kind == "C": onset.append(ph)
            else:
                red = "\u0306" in ph; ph = ph.replace("\u0306", "")  # hataf (half) vowel
                sylls.append({"ph": onset + [ph], "nuc": [ph], "long": ph.endswith("ː"), "reduced": red,
                              "accent": "stress" if cant else None})
                onset = []
        if onset and sylls: sylls[-1]["ph"] += onset
        elif onset: sylls.append({"ph": onset, "nuc": [], "long": False, "accent": None})
        if not any(s["accent"] for s in sylls):
            cand = [s for s in sylls if s["nuc"] and s["nuc"][0] != "ə" and not s.get("reduced")]
            # segolate nouns (ḥesed, ḥošek, ʔemet is NOT one): short final ɛ after a full vowel
            # -> penultimate stress (milʕel); otherwise final stress (milraʕ)
            if len(cand) >= 2 and cand[-1]["nuc"][0] == "ɛ" and cand[-2]["nuc"][0] in ("ɛ", "a", "oː", "eː") \
                    and sylls.index(cand[-2]) == sylls.index(cand[-1]) - 1:
                cand[-2]["accent"] = "stress"
            elif cand: cand[-1]["accent"] = "stress"
        words.append(sylls)
    return words


def parse_phonemes(text):
    """Space-separated IPA tokens; prefix a vowel with ˈ for stress; '|' separates words."""
    words = []
    for w in text.split("|"):
        sylls, onset = [], []
        for t in w.split():
            st = t.startswith("ˈ"); t = t.lstrip("ˈ")
            if t.rstrip("ː") in VOWELS:
                sylls.append({"ph": onset + [t], "nuc": [t], "long": t.endswith("ː"),
                              "accent": "stress" if st else None}); onset = []
            else:
                onset += ALIASES.get(t, [t])
        if onset and sylls: sylls[-1]["ph"] += onset
        if sylls and not any(s["accent"] for s in sylls): sylls[0]["accent"] = "stress"
        words.append(sylls)
    return words

# ---------------------------------------------------------------------------
# 4. PROSODY + DELIVERY  ->  timed segment score
# ---------------------------------------------------------------------------
MODES = {  # vowel-duration scale, consonant scale, pitch range scale, vibrato
    "speech":  dict(v=1.0, c=1.0, rng=1.0, vib=0.0,  gap=0.08),
    "declaim": dict(v=1.5, c=1.2, rng=1.35, vib=0.0, gap=0.20),
    "chant":   dict(v=2.6, c=1.3, rng=1.0, vib=0.25, gap=0.35),
    "ritual":  dict(v=3.4, c=1.5, rng=1.0, vib=0.35, gap=0.55),
}
# Feelings: acoustic cues listeners use to recognise emotion in voice and music
# (Juslin & Laukka 2003 review of 104 voice + 41 music studies; Scherer 2003).
#   tempo: duration x   shift: semitones   rng: pitch-range x   breath: aspiration
#   vib/vrate: vibrato depth/rate   bright: 1 = bright, lower = soft/dark
#   amp: loudness   swell: crescendo through the word   fall: semitone droop at word end
#   glide: pitch smoothing ms   group / space: suggested voices and room
FEELINGS = {
    "neutral": dict(tempo=1.0, shift=0, rng=1.0, breath=0.0, vib=0.0, vrate=5.3, bright=1.0, amp=1.0, swell=0, fall=0, glide=25),
    "love":    dict(tempo=1.35, shift=-1, rng=0.7, breath=0.10, vib=0.15, vrate=4.5, bright=0.45, amp=0.75, swell=0.2, fall=0.5, glide=60),
    "beauty":  dict(tempo=1.2, shift=1, rng=1.1, breath=0.04, vib=0.35, vrate=5.0, bright=0.75, amp=0.9, swell=0.15, fall=0, glide=45),
    "awe":     dict(tempo=1.6, shift=-3, rng=0.6, breath=0.06, vib=0.2, vrate=4.8, bright=0.55, amp=0.8, swell=0.3, fall=0, glide=50, space="temple"),
    "joy":     dict(tempo=0.85, shift=3, rng=1.5, breath=0.02, vib=0.3, vrate=6.0, bright=1.0, amp=1.0, swell=0, fall=-0.5, glide=20),
    "epic":    dict(tempo=1.4, shift=0, rng=1.4, breath=0.0, vib=0.45, vrate=5.5, bright=1.0, amp=1.0, swell=0.5, fall=0, glide=35, group=6, space="basilica"),
    "lament":  dict(tempo=1.5, shift=-2, rng=0.8, breath=0.12, vib=0.25, vrate=4.0, bright=0.4, amp=0.7, swell=0, fall=2.0, glide=70),
}
# Living chant traditions: scale, accompaniment and ornament style
TRADITIONS = {
    "byzantine": dict(genus="byzantine", ensemble="byzantine", orn="turn"),      # ison drone, 72-moria tuning
    "coptic":    dict(genus="diatonic", ensemble="coptic", orn="final_melisma"), # cymbal + triangle, long melismas
    "ethiopian": dict(genus="tezeta", ensemble="ethiopian", orn="turn"),         # kebero drum, tsenatsel sistrum
    "yemenite":  dict(genus="tense", ensemble="none", orn="narrow"),             # narrow-range Torah reading
}
# Tunings: ratios above the tonic.  Archytas's tetrachords (4th c. BCE, preserved by Ptolemy)
GENERA = {
    "diatonic":   [1, 28/27, 32/27, 4/3, 3/2, 14/9, 16/9, 2],
    "chromatic":  [1, 28/27, 9/8, 4/3, 3/2, 14/9, 27/16, 2],
    "enharmonic": [1, 28/27, 16/15, 4/3, 3/2, 14/9, 8/5, 2],
    # Ptolemy's 'tense diatonic' (= just major-type), useful for Hebrew recitation
    "tense":      [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2],
    # Byzantine diatonic (Patriarchal Commission 1881): steps of 12-10-8 moria, 72 per octave
    "byzantine":  [2 ** (m / 72) for m in (0, 12, 22, 30, 42, 54, 64, 72)],
    # Ethiopian qenet 'tezeta' (major-type pentatonic)
    "tezeta":     [1, 9/8, 5/4, 3/2, 5/3, 2],
}


def build_score(words, lang, era, mode, base_f0=118.0, genus="diatonic", feelings=None, orn=None):
    M = MODES[mode]
    melodic = mode in ("chant", "ritual")
    scale = GENERA[genus]
    nsteps = len(scale) - 1
    def deg(d):  # scale degree (can exceed one octave / go negative)
        o, r = divmod(d, nsteps); return base_f0 * scale[r] * (2 ** o)
    segs, notes, t = [], [], 0.05
    recite = min(range(nsteps), key=lambda i: abs(scale[i] - 1.5))  # reciting tone = fifth above tonic
    feelings = feelings or ["neutral"] * len(words)
    nwords = len(words)
    for wi, sylls in enumerate(words):
        acc_i = next((k for k, s in enumerate(sylls) if s["accent"] in ("acute", "circ", "stress")), None)
        final_word = wi == nwords - 1
        fname = feelings[wi] if wi < len(feelings) else "neutral"
        FE = FEELINGS[fname]
        for si, s in enumerate(sylls):
            # ---- pitch targets for the nucleus ------------------------------
            if melodic:
                if acc_i is None or si < acc_i: d = [recite]
                elif si == acc_i:
                    d = [recite + 2, recite + 1] if s["accent"] == "circ" else (
                        [recite + 2] if lang == "greek" else [recite + 1, recite + 2, recite + 1])
                else: d = [recite - 1]
                if orn == "turn" and si == acc_i:
                    d = [recite + 1, recite + 2, recite + 1, recite + 2] if s["accent"] != "circ" else [recite + 2, recite + 3, recite + 2, recite + 1]
                if orn == "narrow":  # Yemenite-style reading: stays within a third
                    d = [min(max(x, recite - 1), recite + 1) for x in d]
                if final_word and si == len(sylls) - 1:
                    d = d[:1] + ([0] if si != acc_i else [recite, 0])
                    if orn == "final_melisma":  # long descending melisma on the last vowel
                        d = [recite + 2, recite + 1, recite + 2, recite, recite + 1, recite - 1, recite - 2, 0]
                pts = [deg(x) for x in d]
            else:
                hi = base_f0 * 2 ** ((7 if (lang == "greek" and era == "attic") else 3.5) * M["rng"] / 12)
                lo = base_f0 * 2 ** (-2 * M["rng"] / 12)
                decl = 2 ** (-1.5 * (wi / max(1, nwords)) / 12)  # phrase declination
                f = base_f0 * decl
                if s["accent"] == "acute":
                    pts = [f, hi * decl] if s["long"] else [hi * decl]
                elif s["accent"] == "circ":
                    pts = [hi * decl, lo * decl]
                elif s["accent"] == "stress":
                    pts = [f * 2 ** (1 / 12), hi * decl, f]
                elif acc_i is not None and si == acc_i + 1:
                    pts = [base_f0 * decl * 1.06, lo * decl]  # post-accentual fall
                else:
                    pts = [f]
                if final_word and si == len(sylls) - 1:
                    pts = pts + [lo * decl * 0.97]
            # ---- feeling: pitch level, range and end-of-word droop ------------
            pts = [base_f0 * 2 ** ((FE["shift"] + FE["rng"] * 12 * math.log2(p / base_f0)) / 12) for p in pts]
            if si == len(sylls) - 1 and FE["fall"]:
                pts = pts + [pts[-1] * 2 ** (-FE["fall"] / 12)]
            stressed = s["accent"] in ("stress",) or (s["accent"] in ("acute", "circ") and era.startswith("koine"))
            # ---- timed segments --------------------------------------------
            nuc_set = False
            for p in s["ph"]:
                base = p.rstrip("ː"); long_ = p.endswith("ː")
                if base in VOWELS and not nuc_set:
                    dur = (0.17 if (long_ or s["long"]) else 0.095) * M["v"] * FE["tempo"]
                    if stressed: dur *= 1.25
                    if len(pts) > 3: dur *= 1 + 0.25 * (len(pts) - 3)  # melisma needs time
                    amp = 1.0 if (stressed or s["accent"] in ("acute", "circ")) else 0.8
                    amp *= FE["amp"] * (1 + FE["swell"] * si / max(1, len(sylls) - 1))
                    segs.append(dict(t=t, d=dur, ph=base, kind="V", F=VOWELS[base], amp=amp, f0=pts, fe=fname))
                    notes.append(dict(t=t, d=dur, f0=pts, amp=amp, syl="".join(s["ph"]),
                                      accent=s["accent"]))
                    nuc_set = True
                elif base in VOWELS:  # second vowel of a diphthong
                    dur = 0.07 * M["v"] * FE["tempo"]
                    segs.append(dict(t=t, d=dur, ph=base, kind="V", F=VOWELS[base], amp=0.85 * FE["amp"], f0=[pts[-1]], fe=fname))
                    notes[-1]["d"] += dur
                else:
                    info = CONS.get(base)
                    if info is None: continue
                    k = info[0]
                    dur = {"stop": 0.075, "asp": 0.11, "fric": 0.10, "pharyngeal": 0.09, "h": 0.07,
                           "glottal": 0.06, "nasal": 0.075, "liquid": 0.065, "trill": 0.08,
                           "trill_vl": 0.09, "approx": 0.06}[k] * M["c"] * (1 + (FE["tempo"] - 1) * 0.5)
                    segs.append(dict(t=t, d=dur, ph=base, kind=k, info=info, fe=fname))
                t += dur
                continue
            # nothing else
        t += M["gap"] * 0.4
    return segs, notes, t + 0.4

# ---------------------------------------------------------------------------
# 5. SIGNAL GENERATION
# ---------------------------------------------------------------------------
def resonator_coeffs(F, B):
    T = 1 / SR
    C = -math.exp(-2 * math.pi * B * T)
    Bc = 2 * math.exp(-math.pi * B * T) * math.cos(2 * math.pi * F * T)
    A = 1 - Bc - C
    return [A], [1, -Bc, -C]


def formant_filter(src, F1, F2, F3, block=220):
    """Time-varying cascade of formant resonators (Klatt-style)."""
    out = np.zeros_like(src)
    bws = (70, 100, 140)
    zis = [np.zeros(2) for _ in range(4)]
    for s in range(0, len(src), block):
        e = min(len(src), s + block); x = src[s:e]
        for j, (F, B) in enumerate(zip((F1[s], F2[s], F3[s], 3500.0), bws + (220,))):
            b, a = resonator_coeffs(max(80.0, F), B)
            x, zis[j] = lfilter(b, a, x, zi=zis[j])
        out[s:e] = x
    return out


def glottal_source(f0, vib=0.0, jitter=0.004, kind="voice", vrate=5.3, bright=None):
    n = len(f0)
    vph = 2 * np.pi * np.cumsum(np.broadcast_to(vrate, (n,))) / SR
    f = f0 * (1 + vib * 0.012 * np.sin(vph)) * (1 + jitter * RNG.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)))
    ph = np.cumsum(f / SR) % 1.0
    if kind == "voice":  # Rosenberg pulse derivative
        g = np.where(ph < 0.4, 0.5 * (1 - np.cos(np.pi * ph / 0.4)),
                     np.where(ph < 0.56, np.cos(np.pi * (ph - 0.4) / 0.32), 0.0))
        src = np.diff(g, prepend=0)
    else:  # reed: narrow pulse, buzzy, rich in harmonics (aulos-like)
        src = np.diff((ph < 0.22).astype(float), prepend=0) * 0.6
    if bright is not None:  # soft/dark voice: tilt the spectrum down (less high-frequency energy)
        b, a = butter(1, 700 / (SR / 2)); dark = lfilter(b, a, src)
        dark *= np.max(np.abs(src)) / (np.max(np.abs(dark)) + 1e-9)
        src = bright * src + (1 - bright) * dark
    return src / (np.max(np.abs(src)) + 1e-9)


def bandnoise(n, center, bw):
    lo = max(60, center - bw / 2) / (SR / 2); hi = min(0.98, (center + bw / 2) / (SR / 2))
    b, a = butter(2, [lo, hi], btype="band")
    return lfilter(b, a, RNG.standard_normal(n))


def smooth(x, ms=8):
    k = max(1, int(SR * ms / 1000)); w = np.ones(k) / k
    return np.convolve(x, w, mode="same")


def render_voice(segs, total, mode, source="voice"):
    n = int(total * SR)
    tt = np.arange(n) / SR
    # knots for formants and f0
    fk_t, fk = [], []
    f0_t, f0_v = [], []
    for s in segs:
        if s["kind"] == "V":
            fk_t.append(s["t"] + s["d"] / 2); fk.append(s["F"])
            pts = s["f0"]
            for j, p in enumerate(pts):
                f0_t.append(s["t"] + s["d"] * (j + 0.5) / len(pts)); f0_v.append(p)
        elif len(s.get("info", ())) > 1 and isinstance(s["info"][1], tuple):
            fk_t.append(s["t"] + s["d"] / 2); fk.append(s["info"][1])
    if not fk: return np.zeros(n)
    fk = np.array(fk)
    F = [np.interp(tt, fk_t, fk[:, j]) for j in range(3)]
    glide = max(FEELINGS[s.get("fe", "neutral")]["glide"] for s in segs)
    f0 = smooth(np.interp(tt, f0_t, f0_v), glide)
    vamp = np.zeros(n); asp = np.zeros(n); fric = np.zeros(n)
    fb = np.zeros(n); fv = np.full(n, MODES[mode]["vib"]); fr = np.full(n, 5.3); fbr = np.ones(n)
    for s in segs:  # feeling parameters as time-varying control signals
        a, b = int(s["t"] * SR), min(n, int((s["t"] + s["d"]) * SR))
        FE = FEELINGS[s.get("fe", "neutral")]
        fb[a:b] = FE["breath"]; fv[a:b] = MODES[mode]["vib"] + FE["vib"]; fr[a:b] = FE["vrate"]; fbr[a:b] = FE["bright"]
    fb, fv, fr, fbr = (smooth(x, 40) for x in (fb, fv, fr, fbr))
    for s in segs:
        a, b = int(s["t"] * SR), min(n, int((s["t"] + s["d"]) * SR))
        L = b - a
        if L <= 0: continue
        k = s["kind"]
        if k == "V": vamp[a:b] = s["amp"]
        elif k in ("nasal",): vamp[a:b] = 0.45
        elif k in ("liquid", "approx"): vamp[a:b] = 0.6
        elif k == "trill":
            vamp[a:b] = 0.55 * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 26 * np.arange(L) / SR)))
        elif k == "trill_vl":
            asp[a:b] = 0.25 * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 26 * np.arange(L) / SR)))
        elif k == "h": asp[a:b] = 0.35
        elif k == "pharyngeal": vamp[a:b] = 0.5; asp[a:b] = 0.15
        elif k == "glottal": pass
        elif k == "fric":
            _, voiced, c, bw = s["info"]
            env = np.hanning(L) ** 0.5
            fric[a:b] += bandnoise(L, c, bw) * env * (0.10 if voiced else 0.16)
            if voiced: vamp[a:b] = 0.35
        elif k in ("stop", "asp"):
            voiced, c = s["info"][1], s["info"][2]
            if voiced: vamp[a:a + int(L * 0.6)] = 0.15  # voice bar
            bl = int(0.012 * SR); bs = b - bl
            fric[bs:b] += bandnoise(bl, c, c * 0.8) * np.exp(-np.linspace(0, 5, bl)) * 0.35
            if k == "asp":  # aspiration after release, continues into vowel onset
                al = int(0.05 * SR); asp[b:min(n, b + al)] = 0.35 * np.linspace(1, 0, min(al, n - b))
    vamp = smooth(vamp, 12); asp = smooth(asp, 6)
    src = glottal_source(f0, vib=fv, kind=source, vrate=fr, bright=fbr if source == "voice" else None)
    noise = RNG.standard_normal(n) * 0.25
    breath = (0.03 if source == "voice" else 0.07) + fb
    exc = src * vamp + noise * (asp + breath * vamp)
    y = formant_filter(exc, *F)
    y = y / (np.max(np.abs(y)) + 1e-9)
    if source != "voice":
        return y * 0.9
    return y + fric * (np.max(np.abs(y)) / (np.max(np.abs(fric)) + 1e-9)) * 0.22 if np.any(fric) else y

# ---- Instruments --------------------------------------------------------------
def env_adsr(L, a=0.02, r=0.08):
    e = np.ones(L); A = min(L, int(a * SR)); R = min(L - A, int(r * SR))
    e[:A] = np.linspace(0, 1, A)
    if R > 0: e[L - R:] = np.linspace(1, 0, R)
    return e


def contour(pts, L):
    if len(pts) == 1: return np.full(L, pts[0])
    return smooth(np.interp(np.arange(L), np.linspace(0, L - 1, len(pts)), pts), 20)


def additive(f, amps, L, inharm=0.0, decays=None, phase_noise=True):
    t = np.arange(L) / SR
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(L)
    for k, a in enumerate(amps, 1):
        if a == 0: continue
        if f.max() * k * (1 + inharm * k * k) > SR / 2.2: break
        d = np.exp(-t * decays[k - 1]) if decays is not None else 1.0
        y += a * d * np.sin(ph * k * (1 + inharm * k * k) + (RNG.uniform(0, 6.28) if phase_noise else 0))
    return y


def inst_aulos(note, L, drone=None):
    f = contour(note["f0"], L) * (1 + 0.006 * np.sin(2 * np.pi * 5.0 * np.arange(L) / SR))
    amps = [1, .55, .75, .35, .5, .25, .3, .15, .18, .1, .1, .06]  # double-reed, odd-strong
    y = additive(f, amps, L)
    y += 0.04 * bandnoise(L, 2500, 2000)  # reed/breath noise
    b, a = resonator_coeffs(1400, 400); y = y + 0.6 * lfilter(b, a, y)  # nasal 'buzz' resonance
    return y * env_adsr(L, 0.035, 0.06)


def inst_string(note, L, bright=1.0, decay=2.5):
    f0 = note["f0"][0]
    LL = int(SR * max(decay, note["d"]))
    amps = [1 / k ** (1.0 / bright) * abs(math.sin(k * math.pi * 0.18)) for k in range(1, 20)]
    decs = [decay ** -1 * (1 + 0.6 * k) for k in range(1, 20)]
    y = additive(np.full(LL, f0), amps, LL, inharm=0.0002, decays=decs)
    y[: int(0.004 * SR)] += RNG.standard_normal(int(0.004 * SR)) * 0.3
    return y


def inst_hydraulis(note, L):
    f = contour(note["f0"], L) * (1 + 0.003 * np.sin(2 * np.pi * 3.1 * np.arange(L) / SR))
    y = additive(f, [1, .5, .33, .25, .2, .1, .08], L) + additive(f * 2.0, [.4, .2, .1], L)
    ch = int(0.03 * SR); y[:ch] += bandnoise(ch, 3000, 3000) * np.linspace(.5, 0, ch)
    return y * env_adsr(L, 0.05, 0.1)


def inst_brass(f_start, f_end, L, bright=1.0, scoop=True):
    f = np.linspace(f_start, f_end, L)
    if scoop:
        s = min(L, int(0.08 * SR)); f[:s] *= np.linspace(0.85, 1.0, s)
    t = np.arange(L) / SR
    e = env_adsr(L, 0.06, 0.15)
    y = np.zeros(L); ph = 2 * np.pi * np.cumsum(f) / SR
    for k in range(1, 16):
        if f_start * k > SR / 2.3: break
        y += (e ** (1 + 0.35 * k / bright)) * np.sin(k * ph) / k ** 0.7
    y += 0.03 * RNG.standard_normal(L) * e
    return y


def shofar_calls(order=("tekiah", "shevarim", "teruah", "tekiah")):
    base = 233.0  # ram's horn: two usable partials, roughly a fifth apart
    parts = []
    for c in order:
        if c == "tekiah":
            L = int(1.6 * SR)
            y = np.concatenate([inst_brass(base, base, int(.25 * SR)), inst_brass(base * 1.5, base * 1.48, L)])
        elif c == "shevarim":
            y = np.concatenate([np.concatenate([inst_brass(base, base, int(.08 * SR), scoop=False),
                                               inst_brass(base * 1.5, base * 1.5, int(.42 * SR)),
                                               np.zeros(int(.12 * SR))]) for _ in range(3)])
        else:  # teruah: nine rapid staccato blasts
            y = np.concatenate([np.concatenate([inst_brass(base * 1.5, base * 1.5, int(.11 * SR), scoop=False),
                                               np.zeros(int(.06 * SR))]) for _ in range(9)])
        parts += [y, np.zeros(int(.35 * SR))]
    return np.concatenate(parts)


def inst_drum(L=None, pitch=95):
    L = int(0.6 * SR)
    t = np.arange(L) / SR
    f = pitch * (1 + 0.5 * np.exp(-t * 30))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    y += 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.59) / SR) * np.exp(-t * 14)
    y += bandnoise(L, 2500, 3000) * np.exp(-t * 60) * 0.5  # jingles/hand slap
    return y


def inst_sistrum(L=None):
    """Tsenatsel / sistrum: metal discs on rods, shaken in short bursts (Egypt -> Ethiopian liturgy)."""
    L = int(0.45 * SR); t = np.arange(L) / SR
    y = np.zeros(L)
    for k in range(4):  # four rattles per shake
        a = int(k * 0.06 * SR); seg = L - a
        y[a:] += (bandnoise(seg, 6500, 3000) + 0.5 * bandnoise(seg, 3800, 600)) * np.exp(-np.arange(seg) / SR * 35)
    return y


def inst_triangle():
    L = int(1.5 * SR); t = np.arange(L) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) / (i + 1)
               for i, (f, d) in enumerate(((1650, 2.0), (4120, 3.0), (6390, 4.5), (8800, 6.0))))


def inst_cymbal():
    L = int(2.0 * SR); t = np.arange(L) / SR
    return (bandnoise(L, 7000, 8000) * 0.6 + bandnoise(L, 3500, 2000) * 0.4) * np.exp(-t * 2.5)


# Rooms modeled from their recorded dimensions (metres) as standing-wave (modal) resonators
MODAL_ROOMS = {
    "holy_of_holies": ((8.9, 8.9, 8.9), 3.0),      # 20-cubit cube (1 Kgs 6:20), cubit 0.445 m; gold-overlaid cedar + veil
    "holy_place":     ((17.8, 8.9, 13.35), 4.5),   # 40 x 20 x 30 cubits (1 Kgs 6:2, 6:17)
    "kings_chamber":  ((10.47, 5.24, 5.84), 6.0),  # Great Pyramid, red granite
}


def modal_ir(dims, rt, fmax=320.0, src=(0.31, 0.43, 0.37), mic=(0.68, 0.59, 0.44)):
    """Impulse response: every room mode below fmax as a decaying sinusoid (amplitude set by
    where the singer and listener stand), plus a diffuse reverberant tail above it."""
    import itertools
    Lx, Ly, Lz = dims; c = 343.0
    L = int(rt * 1.2 * SR); t = np.arange(L) / SR
    low = np.zeros(L)
    nmax = [int(2 * fmax * d / c) + 1 for d in dims]
    for nx, ny, nz in itertools.product(*(range(n + 1) for n in nmax)):
        if nx == ny == nz == 0: continue
        f = c / 2 * math.sqrt((nx / Lx) ** 2 + (ny / Ly) ** 2 + (nz / Lz) ** 2)
        if f > fmax: continue
        amp = 1.0
        for n, a, b in zip((nx, ny, nz), src, mic): amp *= math.cos(n * math.pi * a) * math.cos(n * math.pi * b)
        low += amp * np.exp(-t * 6.91 / rt) * np.cos(2 * np.pi * f * t)
    tail = RNG.standard_normal(L) * np.exp(-t * 6.91 / rt)
    b, a = butter(2, fmax / (SR / 2), btype="high"); tail = lfilter(b, a, tail)
    b, a = butter(1, 4000 / (SR / 2)); tail = lfilter(b, a, tail)
    low /= np.max(np.abs(low)) + 1e-9; tail /= np.max(np.abs(tail)) + 1e-9
    return 0.7 * low + 0.3 * tail


def reverb(y, space):
    if space in MODAL_ROOMS:
        ir = modal_ir(*MODAL_ROOMS[space])
        wet = fftconvolve(y, ir); wet /= np.max(np.abs(wet)) + 1e-9
        out = np.zeros(len(wet)); out[: len(y)] = y / (np.max(np.abs(y)) + 1e-9)
        return 0.45 * out + 0.55 * wet
    # house_church: Dura-Europos-sized room with ~60 people (~1 s, per the chat's model);
    # basilica: large stone church (Hagia Sophia measured >10 s by Stanford's Icons of Sound)
    rt = {"dry": 0, "house_church": 1.0, "theater": 1.1, "synagogue": 1.7, "temple": 3.2,
          "cave": 4.5, "basilica": 9.0}[space]
    if rt == 0: return y
    L = int(rt * SR)
    t = np.arange(L) / SR
    ir = RNG.standard_normal(L) * np.exp(-t * 6.91 / rt)
    b, a = butter(1, 3500 / (SR / 2)); ir = lfilter(b, a, ir)
    ir[0] = 0
    for d, g in ((0.017, .5), (0.031, .35), (0.047, .3)):  # early reflections off stone
        ir[int(d * SR)] += g * 8
    wet = fftconvolve(y, ir)[: len(y) + L]
    wet /= np.max(np.abs(wet)) + 1e-9
    out = np.zeros(len(wet)); out[: len(y)] = y / (np.max(np.abs(y)) + 1e-9)
    mix = {"house_church": .15, "theater": .2, "synagogue": .3, "temple": .42, "cave": .5, "basilica": .6}[space]
    return (1 - mix) * out + mix * wet


def place(buf, y, t):
    a = int(t * SR)
    if a >= len(buf): return
    b = min(len(buf), a + len(y)); buf[a:b] += y[: b - a]


def norm(y, peak=0.9):
    return y / (np.max(np.abs(y)) + 1e-9) * peak

# ---------------------------------------------------------------------------
# 6. ENSEMBLES  (what accompanies the voice in a given setting)
# ---------------------------------------------------------------------------
ENSEMBLES = {
    "none": [],
    "greek_temple": ["aulos", "kithara", "drone"],          # paean / hymn at a sanctuary
    "greek_theater": ["aulos", "drum"],                      # chorus with aulos & tympanon
    "christian_early": ["drone"],                            # unaccompanied, assembly hums ison
    "byzantine": ["drone"],
    "temple": ["kinnor", "nevel", "halil", "cymbal", "shofar"],  # Second Temple Levitical service
    "synagogue": ["drone"],                                  # unaccompanied cantillation
    "hydraulis": ["hydraulis"],
    "phonaulos": ["phonaulos"],
    "coptic": ["cymbal_beat", "triangle"],     # Coptic liturgy: hand cymbals and triangle
    "ethiopian": ["drum", "sistrum"],          # kebero drum + tsenatsel (sistrum)
    "egyptian_temple": ["sistrum", "drone"],   # sistrum of Hathor/Isis over a held tone
}


def render(words, lang, era, mode, ensemble="none", space=None, base_f0=118.0, genus=None, voice=True, group=1,
           feelings=None, tradition=None):
    TR = TRADITIONS.get(tradition, {})
    genus = genus or TR.get("genus") or ("diatonic" if lang == "greek" else "tense")
    if TR and ensemble == "none": ensemble = TR["ensemble"]
    feelings = feelings or ["neutral"] * len(words)
    group = max([group] + [FEELINGS[f].get("group", 1) for f in feelings])
    if space is None:
        fs = [FEELINGS[f]["space"] for f in feelings if "space" in FEELINGS[f]]
        if fs: space = max(set(fs), key=fs.count)
    segs, notes, total = build_score(words, lang, era, mode, base_f0, genus, feelings, TR.get("orn"))
    extra = 3.5 if ensemble == "temple" and "shofar" in ENSEMBLES[ensemble] else 0
    extra += 9.0 if space == "basilica" else (MODAL_ROOMS[space][1] if space in MODAL_ROOMS else 0)
    n = int((total + 3.0 + extra) * SR)
    mix = np.zeros(n)
    if voice:
        v = render_voice(segs, total, mode)
        place(mix, norm(v, 1.0), 0)
        # group voice ("we beheld his glory"): extra speakers, each slightly
        # different in pitch, vocal-tract length and timing, as in unison speech
        for k in range(1, group):
            pf = 2 ** (RNG.uniform(-2.5, 2.5) / 12) * (1.9 if k % 3 == 0 else 1.0)  # some higher voices
            tract = RNG.uniform(0.94, 1.12) * (1.15 if k % 3 == 0 else 1.0)
            sg = [dict(s, F=tuple(f * tract for f in s["F"]), f0=[p * pf for p in s["f0"]]) if s["kind"] == "V" else s
                  for s in segs]
            vk = render_voice(sg, total, mode)
            place(mix, norm(vk, 0.8), RNG.uniform(0.0, 0.06))
    tonic = base_f0
    layers = ENSEMBLES[ensemble]
    for inst in layers:
        lay = np.zeros(n)
        if inst == "aulos":   # heterophony: aulos doubles the melody an octave up
            for nt in notes:
                L = int(nt["d"] * SR); nn = dict(nt, f0=[p * 2 for p in nt["f0"]])
                place(lay, inst_aulos(nn, L), nt["t"])
            mix += 0.35 * norm(lay)
        elif inst == "halil":
            for nt in notes:
                L = int(nt["d"] * SR); place(lay, inst_aulos(dict(nt, f0=[p * 2 for p in nt["f0"]]), L), nt["t"])
            mix += 0.25 * norm(lay)
        elif inst in ("kithara", "kinnor"):  # struck on each syllable onset
            for nt in notes:
                place(lay, inst_string(dict(nt, f0=[nt["f0"][0] * (2 if inst == "kinnor" else 1)]), 0,
                                       bright=1.3 if inst == "kinnor" else 1.0), nt["t"])
            mix += 0.4 * norm(lay)
        elif inst == "nevel":  # larger harp: sustained low tonic+fifth strokes on accented syllables
            for nt in notes:
                if nt["accent"]:
                    for r in (0.5, 0.75):
                        place(lay, inst_string(dict(nt, f0=[tonic * r * 2]), 0, decay=4.0), nt["t"])
            mix += 0.35 * norm(lay)
        elif inst == "drone":  # ison: sustained tonic (the Byzantine 'ison' / aulos drone pipe)
            L = int((total + 0.5) * SR)
            y = additive(np.full(L, tonic), [1, .4, .25, .15, .1], L) * env_adsr(L, .6, 1.0)
            place(lay, y, 0); mix += 0.18 * norm(lay)
        elif inst == "drum":
            for nt in notes:
                if nt["accent"]: place(lay, inst_drum(), nt["t"])
            mix += 0.35 * norm(lay)
        elif inst == "cymbal_beat":
            for nt in notes:
                if nt["accent"]: place(lay, inst_cymbal()[: int(0.5 * SR)] * np.exp(-np.arange(int(0.5 * SR)) / SR * 6), nt["t"])
            mix += 0.18 * norm(lay)
        elif inst == "triangle":
            for nt in notes:
                if nt["accent"]: place(lay, inst_triangle(), nt["t"] + 0.02)
            mix += 0.12 * norm(lay)
        elif inst == "sistrum":
            for nt in notes:
                if nt["accent"]: place(lay, inst_sistrum(), nt["t"])
            mix += 0.2 * norm(lay)
        elif inst == "cymbal":  # cymbals marked the beginning of the Levitical song (2 Chr 5:13, m.Tamid 7:3)
            place(lay, inst_cymbal(), 0.0); mix += 0.2 * norm(lay)
        elif inst == "shofar":
            place(lay, shofar_calls(), total + 0.3); mix += 0.55 * norm(lay)
        elif inst == "hydraulis":
            for nt in notes:
                L = int(nt["d"] * SR); place(lay, inst_hydraulis(nt, L), nt["t"])
            mix += 0.6 * norm(lay)
        elif inst == "phonaulos":
            y = render_voice(segs, total, mode, source="reed")
            place(lay, y, 0); mix += 0.9 * norm(lay)
    space = space or {"speech": "dry", "declaim": "theater", "chant": "synagogue", "ritual": "temple"}[mode]
    out = reverb(mix, space)
    # trim trailing silence
    nz = np.where(np.abs(out) > 1e-3)[0]
    out = out[: nz[-1] + int(0.2 * SR)] if len(nz) else out
    return norm(out), segs, notes, total


def analysis(words, segs, notes, lang, era, mode):
    def cents(f, ref): return round(1200 * math.log2(f / ref), 1)
    ref = notes[0]["f0"][0] if notes else 1
    return {
        "language": lang, "era": era, "mode": mode,
        "syllables": [[{"phonemes": s["ph"], "accent": s["accent"], "long": s["long"]} for s in w] for w in words],
        "ipa": " ".join("".join(".".join("".join(s["ph"]) for s in w).split()) for w in words),
        "melody": [{"t": round(n["t"], 3), "dur": round(n["d"], 3), "hz": [round(p, 1) for p in n["f0"]],
                    "cents_from_first": [cents(p, ref) for p in n["f0"]], "accent": n["accent"]} for n in notes],
    }


def ipa_string(words):
    out = []
    for w in words:
        parts = []
        for s in w:
            mark = "ˈ" if s["accent"] in ("acute", "circ", "stress") else ""
            parts.append(mark + "".join(s["ph"]))
        out.append(".".join(parts))
    return " ".join(out)


def split_feelings(text, phonemes=False):
    """'λόγος{awe} ἀγάπη{love}' -> ('λόγος ἀγάπη', ['awe', 'love']).  A bare {feeling} at the
    very start applies to every word that has no tag of its own."""
    import re
    default = "neutral"
    m = re.match(r"^\s*\{(\w+)\}\s*", text)
    if m: default = m.group(1); text = text[m.end():]
    sep = "|" if phonemes else None
    toks = text.split(sep) if sep else text.replace("־", " ").split()
    clean, fl = [], []
    for tk in toks:
        mm = re.search(r"\{(\w+)\}", tk)
        fl.append(mm.group(1) if mm else default)
        clean.append(re.sub(r"\{\w+\}", "", tk))
    for f in fl:
        if f not in FEELINGS: raise SystemExit(f"unknown feeling '{f}'; choose from {', '.join(FEELINGS)}")
    return ("|" if sep else " ").join(clean), fl


def make(text, lang, era, mode, ensemble, out, space=None, genus=None, phonemes=False, voice=True, base_f0=118.0, group=1,
         tradition=None):
    text, feelings = split_feelings(text, phonemes)
    if phonemes: words = parse_phonemes(text)
    elif lang == "greek": words = parse_greek(text, era)
    else: words = parse_hebrew(text, era)
    y, segs, notes, total = render(words, lang, era, mode, ensemble, space, base_f0, genus, voice, group,
                                   feelings[:len(words)], tradition)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    wavfile.write(out, SR, (y * 32767).astype(np.int16))
    meta = analysis(words, segs, notes, lang, era, mode)
    meta["ipa"] = ipa_string(words); meta["text"] = text; meta["ensemble"] = ensemble
    meta["feelings"] = feelings; meta["tradition"] = tradition
    with open(os.path.splitext(out)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta

# ---------------------------------------------------------------------------
# 7. DEMO SET
# ---------------------------------------------------------------------------
DEMO = [
    # (slug, text, lang, era, gloss)
    ("logos", "λόγος", "greek", None, "word, reason"),
    ("agape", "ἀγάπη", "greek", None, "love"),
    ("pneuma", "πνεῦμα", "greek", None, "breath, spirit"),
    ("phos", "φῶς", "greek", None, "light"),
    ("kyrie_eleison", "Κύριε ἐλέησον", "greek", None, "Lord, have mercy"),
    ("amen_gk", "ἀμήν", "greek", None, "amen"),
    ("shalom", "שָׁלוֹם", "hebrew", "second-temple", "peace, wholeness"),
    ("ruach", "רוּחַ", "hebrew", "second-temple", "breath, wind, spirit"),
    ("qadosh", "קָדוֹשׁ קָדוֹשׁ קָדוֹשׁ", "hebrew", "second-temple", "holy, holy, holy (Isa 6:3)"),
    ("shema", "שְׁמַע יִשְׂרָאֵל", "hebrew", "second-temple", "Hear, O Israel (Deut 6:4)"),
    ("amen_hb", "אָמֵן", "hebrew", "second-temple", "amen, firm, so be it"),
    ("hallelujah", "הַלְלוּ יָהּ", "hebrew", "second-temple", "praise Yah"),
]


def demo(root):
    index = []
    for slug, text, lang, era, gloss in DEMO:
        if lang == "greek":
            variants = [("attic_speech", "attic", "speech", "none"),
                        ("koine_speech", "koine", "speech", "none"),
                        ("koine_declaim", "koine", "declaim", "none"),
                        ("koine_chant", "koine", "chant", "christian_early"),
                        ("attic_ritual", "attic", "ritual", "greek_temple"),
                        ("phonaulos", "koine", "chant", "phonaulos")]
        else:
            variants = [("speech", era, "speech", "none"),
                        ("tiberian_speech", "tiberian", "speech", "none"),
                        ("chant", era, "chant", "synagogue"),
                        ("temple_ritual", era, "ritual", "temple"),
                        ("phonaulos", era, "chant", "phonaulos")]
        for tag, e, mode, ens in variants:
            path = os.path.join(root, slug, f"{slug}_{tag}.wav")
            m = make(text, lang, e, mode, ens, path, voice=(ens != "phonaulos"))
            index.append(dict(word=text, gloss=gloss, variant=tag, file=os.path.relpath(path, root), ipa=m["ipa"]))
            print(f"{slug:14s} {tag:16s} {m['ipa']}")
    with open(os.path.join(root, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", help="Greek/Hebrew text; tag words with feelings, e.g. 'λόγος{awe}'. Feelings: " + ", ".join(FEELINGS)); ap.add_argument("--phonemes", action="store_true", help="treat --text as IPA tokens")
    ap.add_argument("--lang", choices=["greek", "hebrew"], default="greek")
    ap.add_argument("--era", default=None, help="greek: attic|koine|koine-late   hebrew: second-temple|tiberian")
    ap.add_argument("--mode", choices=list(MODES), default="speech")
    ap.add_argument("--ensemble", choices=list(ENSEMBLES), default="none")
    ap.add_argument("--space", choices=["dry", "house_church", "theater", "synagogue", "temple", "cave", "basilica"] + list(MODAL_ROOMS))
    ap.add_argument("--tradition", choices=list(TRADITIONS), help="living chant style to sing in")
    ap.add_argument("--group", type=int, default=1, help="number of voices (group recitation)")
    ap.add_argument("--genus", choices=list(GENERA))
    ap.add_argument("--pitch", type=float, default=118.0, help="tonic / speaking pitch in Hz")
    ap.add_argument("--no-voice", action="store_true")
    ap.add_argument("--out", default="out.wav")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        demo(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")); sys.exit()
    if not a.text: ap.error("--text is required (or --demo)")
    era = a.era or ("koine" if a.lang == "greek" else "second-temple")
    m = make(a.text, a.lang, era, a.mode, a.ensemble, a.out, a.space, a.genus, a.phonemes,
             not a.no_voice and a.ensemble != "phonaulos", a.pitch, a.group, a.tradition)
    print(json.dumps({k: m[k] for k in ("text", "ipa", "language", "era", "mode", "ensemble")}, ensure_ascii=False))
    print("wrote", a.out)
