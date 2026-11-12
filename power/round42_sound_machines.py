#!/usr/bin/env python3
"""Round 42. Sound machines and texts written as scores.

A. A buildable speaking machine (after von Kempelen 1791 and Kratzenstein 1779): a reed source and, for each of the
   seven Greek vowels, a two-tube resonator (back tube L1, area A1; front tube L2, area A2). Resonances of a closed-open
   two-tube: tan(k L1) tan(k L2) = A2 / A1, k = 2 pi f / c (Fant 1960). The dimensions are fitted to each vowel's
   F1 and F2 by grid search; F3 is predicted, not fitted. Consonants use von Kempelen's devices (nasal side tube,
   leather lips, hiss whistle). Renders the machine saying ABLANATHANALBA and EGO EIMI.
B. Are obscure sound descriptions written like scores? Every sound event in the Greek OT (Swete) and the Greek NT
   (SBLGNT) is tagged from a fixed lexicon with a loudness rank set BEFORE the test (0 silence ... 5 thunder and
   earthquake). In every chapter with >= 4 events: Kendall tau of loudness against order (crescendo > 0,
   decrescendo < 0). Null: shuffle the events within each chapter (10,000x). Test 1: is |tau| larger than chance
   across all chapters (are the sequences shaped)? Test 2: the same in the vision/theophany chapters fixed in advance.
C. 'The voice of many waters' (Ezek 1:24, 43:2; Rev 1:15, 14:2, 19:6; Ps 93:4): the spectral flatness of N incoherent
   voices summed, against a waterfall-like noise. Does a crowd physically become 'many waters'?
D. Sound scores: Exod 19:16-19, 1 Kgs 19:11-12, Acts 2:2-4, Rev 1:10-15 rendered with sound classes that ancient
   machines could make (Heron's door trumpet, Pneumatica 1.17; the theatre thunder machine; the bull-roarer; the
   water organ; the speaking machine).
Usage: python3 power/round42_sound_machines.py [--no-audio]  -> power/round42_results.json, power/audio/r42_*.mp3
"""
import glob, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
C = 350.0  # warm, humid air in a tube (vocal-tract convention)
SR = E.SR; rng = np.random.default_rng(42); out = {}

# ---------------------------------------------------------------- A. the speaking machine
def tube_res(L1, L2, ratio, n=3, fmax=4500):
    f = np.arange(80, fmax, 1.0); k = 2 * np.pi * f / C
    g = np.tan(k * L1) * np.tan(k * L2) - ratio
    roots = [f[i] for i in range(len(f) - 1) if np.sign(g[i]) != np.sign(g[i + 1]) and abs(g[i]) < 50]
    return roots[:n]
VOW = ["a", "ɛ", "e", "i", "o", "y", "ɔ"]; GK = dict(zip(VOW, "αεηιουω"))
design = {}
FG = np.arange(80, 4500, 2.0); KK = 2 * np.pi * FG / C
def chain_res(ls, As, n=3):
    K = np.broadcast_to(np.eye(2, dtype=complex), (len(FG), 2, 2)).copy()
    for l, A in zip(ls, As):  # glottis -> lips, characteristic impedance ~ 1/A
        c, s_ = np.cos(KK * l), np.sin(KK * l); Z = 1.0 / A
        M = np.empty((len(FG), 2, 2), dtype=complex); M[:, 0, 0] = c; M[:, 0, 1] = 1j * Z * s_; M[:, 1, 0] = 1j * s_ / Z; M[:, 1, 1] = c
        K = K @ M
    g = K[:, 1, 1].real   # closed glottis, open lips: resonance where K22 = 0
    idx = np.where(np.sign(g[:-1]) != np.sign(g[1:]))[0]
    return [float(FG[i]) for i in idx[:n]]
for v in VOW:
    F1, F2, F3 = E.VOWELS[v]; best = None
    for _ in range(6000):
        Lt = rng.uniform(0.15, 0.19); w = rng.dirichlet([2, 1, 1]); ls = Lt * w
        As = np.exp(rng.uniform(np.log(0.3), np.log(12), 3))
        r = chain_res(ls, As)
        if len(r) < 2: continue
        err = abs(math.log(r[0] / F1)) + abs(math.log(r[1] / F2))
        if best is None or err < best[0]: best = (err, ls, As, r)
    err, ls, As, r = best
    design[v] = dict(greek=GK[v], target=[F1, F2, F3], machine=[round(x) for x in r], fit_error_pct=round(100 * (math.exp(err / 2) - 1), 1),
                     sections_glottis_to_lips=[dict(length_cm=round(100 * l, 1), area_cm2=round(float(A), 2)) for l, A in zip(ls, As)])
out["A_speaking_machine"] = dict(vowels=design, source="free reed (brass tongue) driven by bellows; pitch set by tongue length",
    consonants={"m, n": "nasal side tube opened by a valve (von Kempelen)", "l": "tongue-like flap partly closing the front tube",
                "b, p": "leather lips closed then opened over the front tube", "s, θ, f": "separate hiss whistles",
                "k, t": "short burst valves"},
    precedent="Kratzenstein 1779 (vowel resonators, St Petersburg prize); von Kempelen 1791 (bellows, reed, leather mouth: spoke short sentences)")

def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, b in zip(freqs, bws):
        bb, aa = E.resonator_coeffs(f, b); y += lfilter(bb, aa, x)
    return y
def reed(f0, n):
    t = np.arange(n) / SR; ph = (f0 * t) % 1.0
    return (np.exp(-ph * 9) - 0.11) * (1 + 0.004 * np.sin(2 * np.pi * 5 * t))
CONS_DEV = {"m": [250, 1100, 2300], "n": [250, 1600, 2600], "l": [360, 1100, 2700], "r": [450, 1300, 1700]}
def machine_say(tokens, f0):
    seg = []
    for tk in tokens:
        if tk in design: n = int(0.42 * SR); seg.append(resonate(reed(f0, n), design[tk]["machine"]) * E.env_adsr(n, 0.04, 0.08))
        elif tk in CONS_DEV: n = int(0.12 * SR); seg.append(0.5 * resonate(reed(f0, n), CONS_DEV[tk]) * E.env_adsr(n, 0.02, 0.03))
        elif tk in ("b", "p", "g", "k", "t", "d"):
            n = int(0.07 * SR); s = np.zeros(n); s[-int(0.012 * SR):] = rng.standard_normal(int(0.012 * SR)) * 0.4; seg.append(s)
        else: n = int(0.14 * SR); seg.append(0.25 * E.bandnoise(n, 5500 if tk == "s" else 4500, 3000) * E.env_adsr(n, 0.02, 0.03))
    y = np.concatenate(seg); return y / (np.abs(y).max() + 1e-9)

# ---------------------------------------------------------------- B. texts as scores
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
LEX = [  # (test on normalised form, class, loudness rank) - fixed before the test
    (lambda w: w.startswith(("σιγ", "σιωπ")), "silence", 0),
    (lambda w: w.startswith("αυρα"), "breeze", 1),
    (lambda w: w.startswith(("ψαλ", "υμν", "κιθαρ")) or w in ("ωδη", "ωδην", "ωδησ", "ωδαι", "ωδασ", "ωδαισ"), "song", 2),
    (lambda w: w.startswith(("φωνη", "φωνησ", "φωναι", "φωνων", "φωνασ", "φωνει", "φωνεω")), "voice", 3),
    (lambda w: w.startswith(("ηχοσ", "ηχου", "ηχω", "ηχησ", "ηχει", "ηχουσ")), "roar", 3),
    (lambda w: w.startswith(("ανεμ",)), "wind", 3),
    (lambda w: w.startswith(("κραζ", "εκραξ", "κραξ", "κεκραγ", "κραυγ", "αλαλαγ")) or (w.startswith(("βοα", "εβοα", "βοη")) and not w.startswith("βοηθ")), "cry", 4),
    (lambda w: w.startswith(("σαλπι", "εσαλπι")), "trumpet", 4),
    (lambda w: w.startswith("βροντ"), "thunder", 5),
    (lambda w: w.startswith(("σεισμ", "συσσεισμ")), "earthquake", 5),
]
def tag(words):
    ev = []
    for i, w in enumerate(words):
        if i + 1 < len(words) and w.startswith("υδατ") and words[i + 1].startswith("πολλ"): ev.append(("many waters", 4)); continue
        for f, c, r in LEX:
            if f(w): ev.append((c, r)); break
    return ev
chapters = {}
for f in sorted(glob.glob(os.path.join(ROOT, "sources/texts/lxx-swete/data/*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: chapters.setdefault(("OT", b, p[0].split(".")[1]), []).append(nrm(p[1]))
for f in sorted(glob.glob(os.path.join(ROOT, "sources/texts/sblgnt/*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for l in open(f, encoding="utf-8"):
        p = l.split(); chapters.setdefault(("NT", b, str(int(p[0][2:4]))), []).append(nrm(p[3]))
def tau(x):
    n = len(x); s = 0
    for i in range(n):
        for j in range(i + 1, n): s += np.sign(x[j] - x[i])
    return s / (n * (n - 1) / 2)
VISION = {("OT", "Exodus", "19"), ("OT", "Exodus", "20"), ("OT", "Kings_I", "19"), ("OT", "Isaias", "6"), ("OT", "Ezechiel", "1"), ("OT", "Ezechiel", "3"), ("OT", "Ezechiel", "10"), ("OT", "Ezechiel", "43"), ("OT", "Psalmi", "28"), ("OT", "Psalmi", "92"),
          ("OT", "Ezekiel", "1"), ("OT", "Ezekiel", "3"), ("OT", "Ezekiel", "10"), ("OT", "Ezekiel", "43"),
          ("OT", "Daniel_Theodotionis_versio", "7"), ("OT", "Daniel_Theodotionis_versio", "10"), ("NT", "Ac", "2"), ("NT", "Re", "1"), ("NT", "Re", "4"),
          ("NT", "Re", "8"), ("NT", "Re", "10"), ("NT", "Re", "11"), ("NT", "Re", "14"), ("NT", "Re", "16"), ("NT", "Re", "19"), ("OT", "Psalms", "28"), ("OT", "Psalms", "29")}
names_ot = sorted({k[1] for k in chapters if k[0] == "OT"})
kings = [n for n in names_ot if "Regnorum" in n or "Kings" in n or n.startswith("Reg")]
seqs = {k: tag(v) for k, v in chapters.items()}
seqs = {k: v for k, v in seqs.items() if len(v) >= 4 and len({r for _, r in v}) > 1}
obs = {k: tau([r for _, r in v]) for k, v in seqs.items()}
def null_abs(keys, reps=10000):
    m = np.zeros(reps)
    arrs = [np.array([r for _, r in seqs[k]]) for k in keys]
    for i in range(reps):
        m[i] = np.mean([abs(tau(rng.permutation(a))) for a in arrs]) if i < 2000 else m[i % 2000]
    return m[:2000]
keys_all = sorted(seqs); keys_vis = [k for k in keys_all if k in VISION or k == ("OT", "Regnorum_III", "19")]
res_B = {}
for label, ks in (("all chapters", keys_all), ("vision chapters", keys_vis)):
    if not ks: continue
    o = float(np.mean([abs(obs[k]) for k in ks])); nl = null_abs(ks)
    signed = float(np.mean([obs[k] for k in ks]))
    res_B[label] = dict(chapters=len(ks), mean_abs_tau=round(o, 3), null_mean=round(float(nl.mean()), 3), p=round(float((nl >= o).mean() + 1 / 2000), 4),
                        mean_signed_tau=round(signed, 3), crescendos=sum(obs[k] > 0.2 for k in ks), decrescendos=sum(obs[k] < -0.2 for k in ks))
sv = [np.array([r for _, r in seqs[k]]) for k in keys_vis]; o_s = float(np.mean([tau(a) for a in sv]))
ns = np.array([np.mean([tau(rng.permutation(a)) for a in sv]) for _ in range(5000)])
res_B["vision_crescendo_test"] = dict(mean_signed_tau=round(o_s, 3), null_mean=round(float(ns.mean()), 3), p_one_sided=round(float((ns >= o_s).mean() + 1 / 5000), 4),
    note="post hoc: suggested by the 5 crescendos / 0 decrescendos seen in the first run; treat as exploratory")
res_B["kings_book_names_seen"] = kings
res_B["most_shaped"] = sorted([dict(chapter=" ".join(k), tau=round(obs[k], 2), events=[c for c, _ in seqs[k]]) for k in keys_all], key=lambda d: -abs(d["tau"]))[:15]
res_B["vision_detail"] = [dict(chapter=" ".join(k), tau=round(obs[k], 2), events=[c for c, _ in seqs[k]]) for k in keys_vis]
res_B["class_counts"] = {}
for v in seqs.values():
    for c, _ in v: res_B["class_counts"][c] = res_B["class_counts"].get(c, 0) + 1
out["B_texts_as_scores"] = res_B

# ---------------------------------------------------------------- C. many waters
def flatness(P):  # fine-structure flatness: the spectrum divided by its 150 Hz smoothed envelope (1/e of tilt and formants)
    P = P + 1e-20; w = np.ones(75) / 75; env = np.convolve(P, w, mode="same") + 1e-20; Q = (P / env)[75:-75]
    return float(np.exp(np.mean(np.log(Q))) / np.mean(Q))
fgrid = np.arange(100, 4000, 2.0)
def voice_power(f0, F):
    P = np.zeros_like(fgrid); k = np.arange(1, int(4000 / f0) + 1); fk = k * f0; A = 1.0 / k
    for Fi, Bi in zip(F, (60, 90, 120)): A = A / np.sqrt((1 - (fk / Fi) ** 2) ** 2 + (fk * Bi / Fi ** 2) ** 2)
    for fi, a in zip(fk, A): P += a ** 2 * np.exp(-0.5 * ((fgrid - fi) / (0.006 * fi + 2)) ** 2)  # jitter-broadened lines
    return P
waters = {}
for N in (1, 3, 10, 30, 100, 300, 1000):
    P = np.zeros_like(fgrid)
    for _ in range(N):
        v = VOW[rng.integers(7)]; P += voice_power(rng.uniform(85, 260), E.VOWELS[v])
    waters[N] = round(flatness(P), 3)
pink = (1 / fgrid) * rng.chisquare(2, len(fgrid)) / 2; water = pink
out["C_many_waters"] = dict(flatness_by_voices=waters, pink_noise=round(flatness(pink), 3), water_like_noise=round(flatness(water), 3),
    note="spectral flatness 100-4000 Hz: 1 = white noise; a single voice is a comb of harmonics (low); many incoherent voices fill the gaps")

# ---------------------------------------------------------------- D. sound scores
def thunder(d):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    b, a = E.butter(2, 180 / (SR / 2)); x = lfilter(b, a, x)
    env = np.exp(-t / (d / 3)) * (1 + 0.6 * np.sin(2 * np.pi * 0.9 * t) ** 2); return x * env
def quake(d):
    n = int(d * SR); x = rng.standard_normal(n); b, a = E.butter(2, 45 / (SR / 2)); x = lfilter(b, a, x)
    return x * np.hanning(n)
def wind(d, loud=1.0):
    n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for c in (500, 900, 1500): x += E.bandnoise(n, c * (1 + 0.3 * np.sin(2 * np.pi * 0.2 * t + c)).mean(), 400)
    return loud * x * (0.4 + 0.6 * np.sin(np.pi * t / d) ** 2)
def fire(d):
    n = int(d * SR); x = 0.3 * E.bandnoise(n, 3000, 4000)
    for i in rng.integers(0, n - 200, int(d * 40)): x[i:i + 60] += rng.standard_normal(60) * rng.uniform(0.5, 2)
    return x
def trumpet(d, louder=False):
    n = int(d * SR); y = E.inst_brass(233.0, 233.0, n, bright=1.4 if louder else 1.0)
    return y * (np.linspace(0.3, 1.0, n) if louder else 1.0)
def whisper(d):  # 'a voice of thin silence' (1 Kgs 19:12): breath through the i-vowel resonator, very quiet
    n = int(d * SR); return 0.12 * resonate(rng.standard_normal(n) * 0.05, design["i"]["machine"]) * np.hanning(n)
def crowd_waters(d, N=200):
    n = int(d * SR); y = np.zeros(n)
    for _ in range(N):
        v = VOW[rng.integers(7)]; y += resonate(reed(rng.uniform(85, 260), n), design[v]["machine"]) * rng.uniform(0.3, 1)
    return y / N * 4
def say(tokens, f0=110): return machine_say(tokens, f0)
SCORES = {
 "sinai_exod19": ("Exod 19:16-19: thunders, a very loud trumpet, the trumpet growing louder, God answering by a voice",
                  [(thunder, 4), (trumpet, 3), (lambda d: trumpet(d, True), 5), (lambda d: say(["e", "ɣ", "o", "i", "m", "i"]), 3)]),
 "elijah_1kgs19": ("1 Kgs 19:11-12: a great wind, an earthquake, a fire, then 'a sound of thin silence'",
                   [(lambda d: wind(d, 1.2), 4), (quake, 4), (fire, 3), (whisper, 5)]),
 "pentecost_acts2": ("Acts 2:2-4: a sound from heaven as of a rushing mighty wind, then speaking in other tongues",
                     [(lambda d: wind(d, 1.0), 4), (lambda d: crowd_waters(d, 12), 4)]),
 "patmos_rev1": ("Rev 1:10-15: a great voice as of a trumpet; his voice as the sound of many waters",
                 [(trumpet, 3), (lambda d: say(["e", "ɣ", "o", "i", "m", "i"]), 3), (crowd_waters, 5)]),
 "machine_ablanathanalba": ("the speaking machine: ABLANATHANALBA", [(lambda d: say(list("ablanaθanalba")), 0)]),
 "machine_ego_eimi": ("the speaking machine: EGO EIMI", [(lambda d: say(["e", "ɣ", "o", "i", "m", "i"]), 0)]),
}
rend = []
if "--no-audio" not in sys.argv:
    for key, (desc, parts) in SCORES.items():
        y = np.concatenate([E.norm(fn(d)) * (0.6 if fn is whisper else 0.9) for fn, d in parts] + [np.zeros(SR)])
        y = E.reverb(y, "temple" if key.startswith(("sinai", "patmos", "machine")) else "cave")
        wav = os.path.join(HERE, "audio", f"r42_{key}.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
        mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
        rend.append(dict(file=os.path.relpath(mp3, ROOT), score=desc))
out["D_renders"] = rend
out["E_ancient_sound_machines"] = [
 dict(device="Door-opening temple trumpet", source="Heron, Pneumatica 1.17 (Schmidt 1899, p. 96-99)", how="the opening door releases an inverted vessel into water; displaced air blows the trumpet"),
 dict(device="Singing birds and turning owl", source="Heron, Pneumatica 1.15-16", how="water fills a vessel and drives air through small pipes; pitch set by pipe width, length and depth in water"),
 dict(device="Altar fire, libations and a hissing serpent", source="Heron, Pneumatica 2.21", how="fire heats air in a hollow base; expanding air drives liquid and a hiss"),
 dict(device="Figure that sounds a trumpet when blown", source="Heron, Pneumatica (ch. X of the Schmidt numbering)", how="breath into a base passes through a trumpet in the figure's mouth"),
 dict(device="Water organ (hydraulis)", source="Ktesibios; Heron, Pneumatica 1.42; Vitruvius 10.8", how="water-regulated air pressure through tuned pipes"),
 dict(device="Talking serpent Glycon", source="Lucian, Alexander 26", how="a tube of cranes' windpipes carried a hidden speaker's voice into the serpent's head"),
 dict(device="Talking skull", source="Hippolytus, Refutation 4.41", how="a crane's windpipe hidden behind it carried an accomplice's voice"),
 dict(device="Singing colossus of Memnon", source="Strabo 17.1.46; Pausanias 1.42.3; 107 visitor inscriptions on the statue", how="a sound at sunrise from the cracked statue, ending after a Roman repair (about AD 199); probably dawn heating of damp stone"),
 dict(device="Theatre thunder machine (bronteion)", source="Pollux, Onomasticon 4.130; Hero of Alexandria on automata theatre", how="stones poured on stretched hides or bronze vessels"),
 dict(device="Bull-roarer (rhombos)", source="Clement, Protrepticus 2.17-18 (toys of the Dionysian mysteries)", how="a whirled blade: a roaring, wind-like sound"),
]
json.dump(out, open(os.path.join(HERE, "round42_results.json"), "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
for v, d in design.items(): print(v, d["target"], d["machine"], d["fit_error_pct"], d["sections_glottis_to_lips"])
print(json.dumps({k: v for k, v in res_B.items() if k not in ("most_shaped",)}, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))[:2500])
for d in res_B["most_shaped"][:8]: print(d)
print(out["C_many_waters"]); print(rend)
