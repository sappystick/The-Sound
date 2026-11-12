#!/usr/bin/env python3
"""Every data point the sound engine can use, with where it comes from and how strong the evidence is.

Evidence levels (used everywhere in the engine and its reports):
  MEASURED      computed in this project from the texts or from physics (reproducible here)
  ESTABLISHED   replicated findings in published science
  MIXED         published, but results disagree or effects are small
  PRELIMINARY   one or a few small studies, or animal work
  RECONSTRUCTED scholarly reconstruction of an ancient fact; uncertain by nature
  SYMBOLIC      a number or pattern taken from the texts for structure only; no physical claim
Writes datapoints.json."""
import json, math, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def J(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
# adult-male formant targets (F1, F2, F3) for vowel qualities: the same table as the project voice engine
FMT = {"i": (270, 2290, 3010), "y": (270, 1850, 2250), "e": (400, 2100, 2700), "ɛ": (550, 1850, 2600), "a": (730, 1250, 2500), "ɑ": (700, 1100, 2450),
       "ɔ": (570, 840, 2410), "o": (450, 800, 2400), "u": (300, 870, 2240), "ə": (500, 1500, 2500), "m": (250, 1100, 2300)}
LANG = {
 "sumerian": dict(name="Sumerian (c. 3000-2000 BCE)", vowels=["a", "e", "i", "u"], evidence="RECONSTRUCTED",
     note="Four vowels inferred from cuneiform spelling; an /o/ and vowel length are debated. Sound values are not recoverable beyond vowel quality.", sample_words=["an (sky)", "ki (earth)", "dingir (god)", "me (divine powers)", "nam-til (life)"]),
 "akkadian": dict(name="Akkadian (Babylonian)", vowels=["a", "e", "i", "u"], evidence="RECONSTRUCTED", note="Four qualities, short and long.", sample_words=["šamû (heavens)", "balāṭu (life)", "šiptu (incantation)"]),
 "egyptian": dict(name="Middle Egyptian (reconstructed)", vowels=["a", "i", "u"], evidence="RECONSTRUCTED",
     note="Hieroglyphs write no vowels; a three-vowel system is reconstructed from Coptic, Akkadian transcriptions and Greek renderings.", sample_words=["ankh (life)", "ma'at (order)", "heka (magic)"]),
 "coptic": dict(name="Sahidic Coptic (latest Egyptian)", vowels=["a", "e", "ɛ", "i", "o", "ɔ", "u"], evidence="RECONSTRUCTED", note="Alphabet from Greek: alpha, epsilon, eta, iota, omicron, omega, ou.", sample_words=["ōnh (life)", "noute (god)"]),
 "hebrew": dict(name="Biblical Hebrew (Tiberian vocalisation)", vowels=["i", "e", "ɛ", "a", "ɔ", "o", "u"], evidence="RECONSTRUCTED", note="Seven qualities of the Tiberian Masoretes (c. 900 CE), the vowel points in the WLC.", sample_words=["chayyim (life)", "ruach (breath)", "qol (voice)", "shalom"]),
 "aramaic": dict(name="Galilean / Western Aramaic (Jesus' language)", vowels=["a", "e", "i", "o", "u"], evidence="RECONSTRUCTED", note="As in the project's Aramaic shadow layer; Mark's four retained sayings.", sample_words=["abba", "talitha koum", "ephphatha", "eloi eloi lema sabachthani"]),
 "koine": dict(name="Koine Greek (1st century, the Gospels)", vowels=["a", "e", "i", "y", "o", "u"], evidence="RECONSTRUCTED", note="After the vowel mergers: eta and iota both /i/, omicron and omega both /o/; this project's voice engine.", sample_words=["zōē (life)", "phōs (light)", "logos", "egō eimi"]),
 "attic": dict(name="Classical Attic Greek (5th c. BCE)", vowels=["a", "e", "ɛ", "i", "o", "ɔ", "u", "y"], evidence="RECONSTRUCTED", note="Before the mergers: eta /ɛː/, omega /ɔː/."),
 "pgm_seven": dict(name="The seven Greek vowels of the magical papyri (α ε η ι ο υ ω)", vowels=["a", "e", "ɛ", "i", "o", "y", "ɔ"], letters="αεηιουω", evidence="MEASURED",
     note="Order of PGM XIII and Demetrius' report of Egyptian priests hymning with the seven vowels. Rendered and measured in experiments E3 and E7."),
}
TUNING = {
 "pythagorean": dict(ratios=[1, 9/8, 81/64, 4/3, 3/2, 27/16, 243/128], evidence="RECONSTRUCTED", note="Chain of 3:2 fifths; the tuning described in the Timaeus and in Greek harmonic theory."),
 "timaeus_world_soul": dict(ratios=[1, 2, 3, 4, 8, 9, 27], as_partials=True, evidence="SYMBOLIC", note="Plato's two series 1-2-4-8 and 1-3-9-27, used directly as partial numbers of a drone (power/audio/timaeus_scale.mp3)."),
 "babylonian_heptatonic": dict(ratios=[1, 9/8, 81/64, 4/3, 3/2, 27/16, 243/128], rotations=7, evidence="RECONSTRUCTED",
     note="Cuneiform tablets CBS 10996 and UET VII 74 name seven tunings of a nine-string instrument, obtained by retuning fifths and fourths. The seven are rotations of one diatonic scale; which name is which rotation is still disputed, so the engine offers rotations 1-7 without names.",
     names_on_tablets=["išartum", "kitmum", "embūbum", "pītum", "nīd qablim", "nīš GABA.RI", "qablītum"]),
 "greek_enharmonic": dict(ratios=[1, 28/27, 16/15, 4/3, 3/2, 14/9, 8/5], evidence="RECONSTRUCTED", note="Archytas' enharmonic tetrachord (28:27, 36:35, 5:4), twice, a fifth apart."),
 "greek_chromatic": dict(ratios=[1, 28/27, 9/8, 4/3, 3/2, 14/9, 27/16], evidence="RECONSTRUCTED", note="Archytas' chromatic tetrachord (28:27, 243:224, 32:27)."),
 "harmonic_series": dict(ratios=list(range(1, 17)), as_partials=True, evidence="MEASURED", note="Natural overtones. E3 found that α, ε and η on a held note place their formants on exact harmonics."),
 "just_major": dict(ratios=[1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8], evidence="ESTABLISHED", note="Comparison tuning (small-number ratios)."),
}
c = 343.0
def cube_modes(L, fmax=300):
    out = {}
    for n in itertools.product(range(0, 25), repeat=3):
        if n == (0, 0, 0): continue
        f = round(c / 2 * math.sqrt(sum((k / l) ** 2 for k, l in zip(n, L))), 1)
        if f <= fmax: out[f] = out.get(f, 0) + 1
    return sorted(out.items())
ROOMS = {}
for key, name, dims, unit, ev, note in [
    ("tabernacle", "Tabernacle most holy place, 10-cubit cube (Exodus 26)", (10, 10, 10), 0.445, "MEASURED", "Room modes computed from the stated dimensions (cubit 0.445 m)."),
    ("debir", "Solomon's inner sanctuary, 20-cubit cube (1 Kings 6:20)", (20, 20, 20), 0.445, "MEASURED", "A cube packs its modes onto few frequencies (round 37: 15 against 56 for an ordinary room)."),
    ("hekal", "Solomon's temple hall, 40 x 20 x 30 cubits", (40, 20, 30), 0.445, "MEASURED", ""),
    ("kings_chamber", "King's Chamber, Great Pyramid", (10.47, 5.24, 5.84), 1.0, "MEASURED", "Granite room; dimensions as surveyed."),
    ("hypogeum", "Ħal Saflieni Hypogeum 'Oracle Room' (Malta)", (5.0, 3.0, 2.6), 1.0, "PRELIMINARY", "Approximate dimensions; acoustic studies report a strong resonance near 110-114 Hz (Cook, Pajot & Leuchter 2008, a small study that also reported EEG changes at 110 Hz).")]:
    L = [d * unit for d in dims]; M = cube_modes(L); band = [(f, k) for f, k in M if 70 <= f <= 180]
    ROOMS[key] = dict(name=name, dims_m=[round(x, 2) for x in L], modes=M[:30], modes_voice=[m for m in M if 80 <= m[0] <= 180], strongest_70_180=sorted(band, key=lambda x: -x[1])[:6], evidence=ev, note=note)
e3 = J("experiments/e3_e4_results.json") if os.path.exists(os.path.join(ROOT, "experiments/e3_e4_results.json")) else {}
r40 = J("round40/results.json") if os.path.exists(os.path.join(ROOT, "round40/results.json")) else {}
BREATH = {
 "resonance_6": dict(per_min=6.0, inhale_exhale=[4, 6], evidence="ESTABLISHED", note="About 6 breaths a minute (0.1 Hz) maximises heart-rate variability: resonance-frequency breathing (Lehrer & Vaschillo; many trials). Bernardi et al. 2001 (BMJ) found the rosary and a yoga mantra both slow breathing to this rate."),
 "john_slow": dict(per_min=3.5, inhale_exhale=[5, 12], evidence="MEASURED", note="Slowest pacing in the project's reconstructed delivery of John (rounds 34-35)."),
 "john_fast": dict(per_min=12.7, inhale_exhale=[2, 2.7], evidence="MEASURED", note="Fastest pacing in the reconstructed John."),
 "psalm_half_verse": dict(per_min=(r40.get("breath", {}).get("Ps", {}) or {}).get("breaths_per_min", 23.3), inhale_exhale=[1, 1.6], evidence="MEASURED", note="One breath per Psalm half-verse (split at the atnach) at 4.5 syllables a second (round 40). Sung slowly, the same units fall to 6-10 a minute."),
 "natural": dict(per_min=12.0, inhale_exhale=[2, 3], evidence="ESTABLISHED", note="Ordinary resting rate (12-20 a minute)."),
}
BANDS = {
 "delta": dict(range=[0.5, 4], associated="deep sleep (EEG)", evidence="MIXED"),
 "theta": dict(range=[4, 8], associated="drowsiness, meditation, memory (EEG)", evidence="MIXED"),
 "alpha": dict(range=[8, 13], associated="relaxed wakefulness, eyes closed (EEG)", evidence="MIXED"),
 "beta": dict(range=[13, 30], associated="active thinking (EEG)", evidence="MIXED"),
 "gamma40": dict(range=[38, 42], associated="the 40 Hz auditory steady-state response: the auditory cortex reliably follows 40 Hz modulation (Galambos et al. 1981). Effects on memory or disease are preliminary (mouse work by Tsai's group; small human trials).", evidence="ESTABLISHED (cortical response) / PRELIMINARY (benefit)"),
}
FACTS = [
 dict(fact="Binaural beats are made in the brainstem (superior olivary complex) from two slightly different tones, one per ear. They need separate ears: headphones.", evidence="ESTABLISHED"),
 dict(fact="Binaural beats are heard best with carriers near 400-500 Hz and vanish above about 1,000-1,500 Hz; beats faster than about 30 Hz stop sounding like beats.", evidence="ESTABLISHED", source="Licklider et al. 1950; Perrott & Nelson 1969"),
 dict(fact="Whether binaural beats entrain brain rhythms is inconsistent across EEG studies; effects on mood, anxiety or attention are small and mixed.", evidence="MIXED", source="Garcia-Argibay et al. 2019 meta-analysis; Ingendoh et al. 2023 systematic review"),
 dict(fact="Monaural and isochronic beats (the beat already in the sound) drive larger steady-state brain responses than binaural beats.", evidence="ESTABLISHED", source="e.g. Schwarz & Taylor 2005"),
 dict(fact="Bone conduction reaches both inner ears almost equally (interaural attenuation about 0-10 dB), so a binaural beat leaks across and becomes partly an ordinary beat. Use monaural or isochronic modes on bone-conduction headphones.", evidence="ESTABLISHED", source="audiology: interaural attenuation for bone conduction"),
 dict(fact="Consumer bone-conduction headphones reproduce little below about 250-300 Hz; carriers and drones should sit above that.", evidence="ESTABLISHED"),
 dict(fact="Slow breathing near 6 a minute raises heart-rate variability and baroreflex sensitivity.", evidence="ESTABLISHED"),
 dict(fact="Humming raises nasal nitric oxide about fifteen-fold compared with quiet breathing.", evidence="ESTABLISHED", source="Weitzberg & Lundberg 2002"),
 dict(fact="Chanting on the out-breath lengthens exhalation, which slows breathing without instruction.", evidence="ESTABLISHED"),
 dict(fact="Safe listening: keep average level moderate (about 60-70 dB), with breaks; WHO guidance is under 80 dB for 40 hours a week.", evidence="ESTABLISHED"),
]
SYMBOLIC = dict(seven=dict(value=7, from_="seven vowels, seven directions of PGM XIII, seven 'voice of the LORD' (Ps 29)"), ten=dict(value=10, from_="ten 'and God said' (Gen 1)"),
                four=dict(value=4, from_="John's four voice-drawn parts (C24)"), three_sixty_five=dict(value=365, from_="Abrasax = Meithras = Neilos"), forty=dict(value=40, from_="forty days; also the 40 Hz response"))
OUT = dict(levels=["MEASURED", "ESTABLISHED", "MIXED", "PRELIMINARY", "RECONSTRUCTED", "SYMBOLIC"], formants=FMT, languages=LANG, tunings=TUNING, rooms=ROOMS, breath=BREATH, bands=BANDS, facts=FACTS, symbolic=SYMBOLIC,
           project_findings=dict(
               voice_outline="John's four parts are drawn by narration vs speech (C24, p 2.3e-4); replicated in round 40 with translators' quotes, farewell at 13:32-33",
               vowel_harmonics=(e3.get("E3") or {}) and "α ε η formants land on exact harmonics on a held note (E3)",
               cube_modes="cube sanctuaries resonate on few strong notes (E4, round 40)",
               aramaic_at_healing="Mark keeps Jesus' Aramaic at healing, prayer and death"))
ROOMS["hypogeum"]["reported_hz"] = 111.0
json.dump(OUT, open(os.path.join(HERE, "datapoints.json"), "w"), ensure_ascii=False, indent=1)
print("datapoints.json:", {k: len(v) if hasattr(v, "__len__") else v for k, v in OUT.items()})
for k, r in ROOMS.items(): print(f"   {k:14s} strongest 70-180 Hz modes {r['strongest_70_180'][:3]}")
