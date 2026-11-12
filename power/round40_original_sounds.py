#!/usr/bin/env python3
"""Round 40. The original words of power as physical sound: calculated in the spaces where they were spoken.

For each utterance (original wording; Aramaic, Hebrew, Koine Greek, Greek magical names, reconstructed Egyptian):
  1. Phonemes from the engine (Greek/Hebrew parsers; Aramaic and Egyptian as hand-set IPA, labelled).
     Measures: syllables, chant duration, voiced share, sibilant/noise share, vowel brightness (mean F2).
  2. Overtone melody: when chanted on a room's preferred note, which harmonic each vowel brightens (F2/f0, as in E3).
For each space (ancient dimensions, labelled by certainty):
  3. Room modes below 320 Hz, the 'preferred note' (the most strongly stacked mode in 85-180 Hz),
     mode bandwidth B = 2.2 / RT, and the share of modes a sung note excites against a pop (impulse) or hiss.
  4. Sound level reached: direct + reverberant field, Lp = Lw + 10 log10(Q/(4 pi r^2) + 4/R), R = S a/(1-a),
     with a from Sabine RT = 0.161 V / (S a). Sources: chant, loud voice, shout, shofar, 120 trumpets (2 Chr 5:12).
  5. Thresholds that sound can physically cross (from the literature, labelled): vestibular (saccule) response to
     loud low tones about 90 dB SPL (Todd & Cody 2000), discomfort 110 dB, pain 130 dB, wine glass ~100 dB tuned,
     masonry damage needs ~165+ dB (blast-overpressure order, ~3.5 kPa).
  6. Renders: selected utterances in their own space (engine, modal rooms added for this round).
Usage: python3 power/round40_original_sounds.py   (writes power/round40_results.json, power/audio/r40_*.mp3)
"""
import itertools, json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
C = 343.0; out = {}

# ---------------------------------------------------------------- utterances (original wording)
# kind: greek / hebrew (engine parsers) or ipa (hand-set, reconstruction labelled in 'basis')
U = [
 ("talitha_koum", "Mark 5:41", "ταλιθα κουμ", "ipa", "tˤ a l ˈi θ a | ˈq u m", "Aramaic ṭəlīṯā qūm; Western Aramaic vowels (Dalman)", "raising the dead girl"),
 ("ephphatha", "Mark 7:34", "εφφαθα", "ipa", "ʔ ɛ f ˈf a θ a", "as transliterated in Greek; Aramaic ʾeppattaḥ/ʾetpəṯaḥ debated", "opening deaf ears, with a sigh"),
 ("abba", "Mark 14:36", "αββα", "ipa", "ˈa b b a", "Aramaic ʾabbā", "prayer in Gethsemane"),
 ("eloi", "Mark 15:34", "ελωι ελωι λεμα σαβαχθανι", "ipa", "ʔ e l ˈo i | ʔ e l ˈo i | l ə ˈm a | ʃ ə v a q ˈt a n i", "Aramaic ʾĕlāhî ... šəḇaqtanî", "cry at death, 'with a loud voice'"),
 ("lazarus", "John 11:43", "Λάζαρε, δεῦρο ἔξω.", "greek", None, "Koine (engine)", "raising Lazarus, 'cried with a loud voice'"),
 ("ego_eimi", "John 18:6", "ἐγώ εἰμι.", "greek", None, "Koine (engine)", "soldiers 'went backward and fell to the ground'"),
 ("tetelestai", "John 19:30", "τετέλεσται.", "greek", None, "Koine (engine)", "last word; 'gave up the spirit'"),
 ("amen_amen", "John 1:51 etc.", "ἀμὴν ἀμὴν λέγω ὑμῖν", "greek", None, "Koine (engine)", "John's solemn opening (25 times)"),
 ("yehi_or", "Genesis 1:3", "יְהִי אוֹר", "hebrew", None, "Tiberian-type (engine)", "creation by speech"),
 ("ehyeh", "Exodus 3:14", "אֶהְיֶה אֲשֶׁר אֶהְיֶה", "hebrew", None, "Tiberian-type (engine)", "the name at the bush"),
 ("shema", "Deuteronomy 6:4", "שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד", "hebrew", None, "Tiberian-type (engine)", "the confession"),
 ("qadosh", "Isaiah 6:3", "קָדוֹשׁ קָדוֹשׁ קָדוֹשׁ", "hebrew", None, "Tiberian-type (engine)", "seraphim; 'the posts of the door moved at the voice'"),
 ("terua", "Joshua 6:20", "תְּרוּעָה גְדוֹלָה", "hebrew", None, "Tiberian-type (engine)", "the great shout at Jericho"),
 ("seven_vowels", "Demetrius, On Style 71; PGM XIII", "αεηιουω", "ipa", "ˈa | ˈɛ | ˈe | ˈi | ˈo | ˈy | ˈɔ", "Koine-era values of the seven letters", "hymn of the Egyptian priests"),
 ("iao", "PGM (89 times)", "ΙΑΩ", "ipa", "i ˈa ɔ", "Greek vowels of the divine name", "the most frequent magical name"),
 ("ablanathanalba", "PGM (16 times)", "ΑΒΛΑΝΑΘΑΝΑΛΒΑ", "ipa", "a b l a n a θ ˈa n a l b a", "Koine", "palindrome name"),
 ("abrasax", "PGM (34 times); = 365", "ΑΒΡΑΣΑΞ", "ipa", "a b r a ˈs a k s", "Koine", "the year-god"),
 ("djed_medu", "Pyramid Texts rubric", "ḏd mdw", "ipa", "ʤ ˈe d | m ˈe d u", "Egyptian 'words to be said'; vowels reconstructed from Coptic (Loprieno 1995) - uncertain", "rubric opening every spell"),
 ("ankh_wedja_seneb", "Egyptian formula", "ʿnḫ wḏꜣ snb", "ipa", "ʕ ˈa n a x | w ˈa ʤ a ʔ | s ˈa n a b", "Egyptian 'life, prosperity, health'; vocalised by convention - uncertain", "blessing on the king"),
 ("heka", "Egyptian", "ḥkꜣ", "ipa", "ħ ˈi k a ʔ", "Egyptian 'magic, word-power' (Coptic hik); vowel uncertain", "the god and force of effective speech"),
 ("amun", "Egyptian / PGM 'AMOUN' (14)", "jmn", "ipa", "ʔ a m ˈu n", "Coptic Amoun; PGM spelling", "the hidden one"),
]
E.ALIASES.setdefault("ʤ", ["d", "ʒ"])
if "ʒ" not in E.CONS: E.CONS["ʒ"] = ("fric", True, 3000, 1800)

def words_of(kind, text, ipa):
    if kind == "greek": return E.parse_greek(text, "koine")
    if kind == "hebrew": return E.parse_hebrew(text, "tiberian")
    return E.parse_phonemes(ipa)

NOISE = {"s", "z", "ʃ", "ʒ", "f", "θ", "x", "χ", "ħ", "h", "sˤ", "v", "ð", "ɣ"}
STOP = {"p", "b", "t", "d", "k", "g", "q", "tˤ", "pʰ", "tʰ", "kʰ", "ʔ"}
def measures(words):
    ph = [p for w in words for s in w for p in s["ph"]]
    vow = [p.rstrip("ː") for p in ph if p.rstrip("ː") in E.VOWELS]
    cons = [p for p in ph if p.rstrip("ː") not in E.VOWELS]
    voiced = len(vow) + sum(1 for p in cons if p in ("m", "n", "ŋ", "l", "r", "w", "j", "b", "d", "g", "v", "z", "ð", "ɣ", "ʕ", "ʒ"))
    nsyl = sum(len(w) for w in words)
    return dict(phonemes=" ".join(ph), syllables=nsyl, vowels=vow,
                voiced_share=round(voiced / max(1, len(ph)), 3),
                noise_share=round(sum(p in NOISE for p in cons) / max(1, len(ph)), 3),
                stop_share=round(sum(p in STOP for p in cons) / max(1, len(ph)), 3),
                mean_F2=round(float(np.mean([E.VOWELS[v][1] for v in vow])) if vow else 0, 0),
                chant_seconds=round(nsyl * 0.42 + 0.35 * len(words), 1))

def overtone_melody(vowels, f0):
    return [dict(v=v, F1_harm=round(E.VOWELS[v][0] / f0), F2_harm=round(E.VOWELS[v][1] / f0)) for v in vowels]

# ---------------------------------------------------------------- spaces
# name: dims (m), RT (s, estimate from materials), certainty / basis
S = {
 "holy_of_holies_solomon": ((8.9, 8.9, 8.9), 3.0, "1 Kgs 6:20, 20-cubit cube @0.445 m; cedar overlaid with gold, veil"),
 "holy_place_solomon": ((17.8, 8.9, 13.35), 4.5, "1 Kgs 6:2,17 (40 x 20 x 30 cubits)"),
 "tabernacle_holy_of_holies": ((4.45, 4.45, 4.45), 1.2, "10-cubit cube inferred from Exod 26; curtains (absorptive)"),
 "kings_chamber": ((10.47, 5.24, 5.84), 6.0, "Great Pyramid, red granite; Petrie survey"),
 "queens_chamber": ((5.75, 5.23, 5.46), 4.0, "Great Pyramid, limestone; gabled roof 4.69-6.23 m, mean height used"),
 "rock_tomb_bethany_type": ((3.0, 3.0, 2.0), 1.5, "typical Judean kokhim burial chamber (Hachlili 2005); Lazarus' tomb dimensions unknown"),
 "galilee_synagogue_hall": ((20.0, 15.0, 7.0), 1.7, "Gamla/Capernaum-size hall, approximate"),
}
REPORTED = {  # measured resonances reported in the literature (not computed here)
 "Newgrange passage tomb": "110 Hz (Jahn, Devereux & Ibison 1996, J. Acoust. Soc. Am. 99:649)",
 "Six British/Irish megalithic chambers": "95-120 Hz, clustered at 110-112 Hz (same study)",
 "Hal Saflieni Hypogeum, Oracle Room (Malta)": "about 110-114 Hz reported (Debertolis et al. 2015); 110 Hz tones shift frontal EEG asymmetry (Cook, Pajot & Leuchter 2008, Time and Mind 1:95)",
}

def modes(dims, fmax=320.0):
    Lx, Ly, Lz = dims; res = []
    nmax = [int(2 * fmax * d / C) + 1 for d in dims]
    for n in itertools.product(*(range(m + 1) for m in nmax)):
        if n == (0, 0, 0): continue
        f = C / 2 * math.sqrt((n[0] / Lx) ** 2 + (n[1] / Ly) ** 2 + (n[2] / Lz) ** 2)
        if f <= fmax: res.append(f)
    return sorted(res)

def preferred(fs, B, lo=85, hi=180):
    best = max(np.arange(lo, hi, 0.5), key=lambda f: sum(abs(m - f) < B / 2 for m in fs))
    return float(best), int(sum(abs(m - best) < B / 2 for m in fs))

def excite_share(fs, f0, B):  # share of modes within B/2 of any harmonic of f0
    return sum(any(abs(m - h * f0) < B / 2 for h in range(1, 6)) for m in fs) / len(fs)

SRC = {"chant (0.1 mW)": 80, "loud voice (1 mW)": 90, "shout (5 mW)": 97, "shofar (0.3 W)": 115, "120 trumpets + singers (2 Chr 5:12)": 136}
THR = [("vestibular (saccule) response, loud low tones", 90, "Todd & Cody 2000; Todd et al. 2008"),
       ("discomfort", 110, "standard audiology"), ("wine glass shatters, exactly tuned", 100, "demonstrations, sustained"),
       ("pain", 130, "standard"), ("masonry damage (blast-type overpressure ~3.5 kPa)", 165, "blast engineering order of magnitude")]

def level(dims, rt, Lw, r=2.0, Q=2.0):
    Lx, Ly, Lz = dims; V = Lx * Ly * Lz; Sa = 2 * (Lx * Ly + Lx * Lz + Ly * Lz)
    a = min(0.99, 0.161 * V / (Sa * rt)); R = Sa * a / (1 - a)
    return Lw + 10 * math.log10(Q / (4 * math.pi * r * r) + 4 / R), a

rooms = {}
for name, (dims, rt, basis) in S.items():
    fs = modes(dims); B = 2.2 / rt; f0, stack = preferred(fs, B)
    lv = {}
    for s, Lw in SRC.items():
        L, a = level(dims, rt, Lw); lv[s] = round(L, 1)
    rooms[name] = dict(dims_m=dims, rt_s=rt, basis=basis, modes_below_320=len(fs), bandwidth_Hz=round(B, 2),
                       preferred_note_Hz=f0, modes_stacked=stack,
                       mean_absorption=round(a, 3),
                       sung_note_excites_share=round(excite_share(fs, f0, B), 3), pop_or_hiss_excites_share=1.0,
                       levels_dB_at_2m=lv,
                       thresholds_crossed={s: [t[0] for t in THR if L >= t[1]] for s, L in lv.items()})
def note(f):
    m = 69 + 12 * math.log2(f / 440); n = round(m); N = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{N[n % 12]}{n // 12 - 1}{(m - n) * 100:+.0f}c"
for r in rooms.values(): r["preferred_note"] = note(r["preferred_note_Hz"])
out["spaces"] = rooms; out["reported_resonances"] = REPORTED; out["thresholds"] = THR; out["sources_Lw_dB"] = SRC

# outdoor: Jericho (Josh 6:20) - a shout of a large crowd at the wall
def outdoor(Lw, r): return Lw - 20 * math.log10(r) - 8  # hemispherical free field
crowd = {n: round(outdoor(97 + 10 * math.log10(n), 30), 1) for n in (1, 1000, 40000, 600000)}
crowd_trumpets = round(outdoor(115 + 10 * math.log10(7), 30), 1)
out["jericho_outdoor_dB_at_30m"] = dict(shouts=crowd, seven_shofars=crowd_trumpets,
    note="Josh 6:20; 40,000 (Josh 4:13) and 600,000 (Exod 12:37) as the text's own numbers; incoherent sources add in power")

# ---------------------------------------------------------------- utterances measured
ut = {}
for key, ref, orig, kind, ipa, basis, ctx in U:
    w = words_of(kind, orig, ipa); m = measures(w)
    m.update(ref=ref, original=orig, basis=basis, context=ctx,
             overtone_melody={rn: overtone_melody(m["vowels"], rooms[rn]["preferred_note_Hz"]) for rn in ("kings_chamber", "holy_of_holies_solomon", "rock_tomb_bethany_type")})
    m["vowels"] = " ".join(m["vowels"]); ut[key] = m
out["utterances"] = ut

# null for voiced share: John's narrative verses (engine), same as POWER T5 style
import glob, unicodedata
sbl = glob.glob(os.path.join(ROOT, "sources/texts/sblgnt/64-Jn-morphgnt.txt"))
if sbl:
    verses = {}
    for l in open(sbl[0], encoding="utf-8"):
        p = l.split(); verses.setdefault(p[0][2:6], []).append(p[3])
    rng = np.random.default_rng(40); keys = sorted(verses); vs = []
    for k in rng.choice(keys, 300, replace=False):
        try: vs.append(measures(E.parse_greek(" ".join(verses[k]), "koine")))
        except Exception: pass
    nv = np.array([v["voiced_share"] for v in vs]); nn = np.array([v["noise_share"] for v in vs]); nf = np.array([v["mean_F2"] for v in vs])
    out["null_john_narrative"] = dict(n=len(vs), voiced_mean=round(float(nv.mean()), 3), voiced_sd=round(float(nv.std()), 3),
                                      noise_mean=round(float(nn.mean()), 3), F2_mean=round(float(nf.mean()), 0))
    for k, m in ut.items():
        m["voiced_pct_vs_john"] = round(float((nv >= m["voiced_share"]).mean()), 3)
    # group test: are the power words more voiced than narrative? (permutation on means)
    pw = np.array([m["voiced_share"] for m in ut.values()])
    pool = np.concatenate([pw, nv]); obs = pw.mean() - nv.mean(); cnt = 0
    for _ in range(20000):
        rng.shuffle(pool); cnt += pool[:len(pw)].mean() - pool[len(pw):].mean() >= obs
    out["test_voiced_power_vs_narrative"] = dict(diff=round(float(obs), 3), p=round((cnt + 1) / 20001, 4), n_power=len(pw))

# ---------------------------------------------------------------- renders
E.MODAL_ROOMS.update({k: (v[0], v[1]) for k, v in S.items()})
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
R = [("talitha_koum", "rock_tomb_bethany_type", "declaim"), ("ephphatha", "galilee_synagogue_hall", "declaim"),
     ("lazarus", "rock_tomb_bethany_type", "declaim"), ("ego_eimi", "galilee_synagogue_hall", "declaim"),
     ("qadosh", "holy_of_holies_solomon", "ritual"), ("yehi_or", "holy_of_holies_solomon", "ritual"),
     ("seven_vowels", "kings_chamber", "ritual"), ("djed_medu", "kings_chamber", "ritual"),
     ("ankh_wedja_seneb", "queens_chamber", "ritual"), ("ablanathanalba", "kings_chamber", "chant")]
rend = []
if "--no-audio" not in sys.argv:
    for key, room, mode in R:
        _, ref, orig, kind, ipa, _, _ = next(u for u in U if u[0] == key)
        f0 = rooms[room]["preferred_note_Hz"]
        while f0 > 175: f0 /= 2   # sing the room note in the male range
        wav = os.path.join(HERE, "audio", f"r40_{key}.wav"); mp3 = wav[:-4] + ".mp3"
        try:
            if kind == "ipa": E.make(ipa, "greek", "koine", mode, "none", wav, space=room, phonemes=True, base_f0=f0)
            else: E.make(orig, kind, "koine" if kind == "greek" else "tiberian", mode, "none", wav, space=room, base_f0=f0)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
            rend.append(dict(key=key, room=room, f0=round(f0, 1), file=os.path.relpath(mp3, ROOT)))
        except Exception as e: rend.append(dict(key=key, room=room, error=str(e)[:200]))
out["renders"] = rend
json.dump(out, open(os.path.join(HERE, "round40_results.json"), "w"), ensure_ascii=False, indent=1)
for n, r in rooms.items(): print(n, r["preferred_note_Hz"], r["preferred_note"], r["modes_stacked"], r["sung_note_excites_share"], r["levels_dB_at_2m"])
print(out.get("test_voiced_power_vs_narrative"), out.get("null_john_narrative")); print(out["jericho_outdoor_dB_at_30m"]); print(rend)
for k, m in ut.items(): print(k, m["syllables"], m["voiced_share"], m["noise_share"], m["mean_F2"], m.get("voiced_pct_vs_john"), [x["F2_harm"] for x in m["overtone_melody"]["kings_chamber"]])
