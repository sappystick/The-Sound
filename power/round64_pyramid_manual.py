#!/usr/bin/env python3
"""Round 64. Thought experiment, taken as true: the Bible is the operating manual of the Great Pyramid.
The manual is the one rite in which one person enters the innermost chamber: the Day of Atonement (Lev 16; Mishnah
Yoma; Tamid 3:8 - all checked on Sefaria). Each step is mapped to a place in the pyramid (MAPPING), and its physical
effect there is calculated (CALC): the King's Chamber's acoustics (round 40), the chamber with its two shafts as a
Helmholtz resonator, how far the voice carries out through the shafts, and whether the ritual's counts match the
pyramid's counts beyond chance. Then the 'activation sequence' is rendered in the King's Chamber.
The divine name is not pronounced: the render uses the Mishnah's own substitution 'ana hashem' ('Please, O Name').
Usage: python3 power/round64_pyramid_manual.py
"""
import json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter, butter
from scipy.io import wavfile
SR = E.SR; C = 343.0; rng = np.random.default_rng(64); out = {}
KC = (10.47, 5.24, 5.84); V = KC[0] * KC[1] * KC[2]; S = 2 * (KC[0] * KC[1] + KC[0] * KC[2] + KC[1] * KC[2])
R40 = json.load(open(os.path.join(HERE, "round40_results.json")))["spaces"]["kings_chamber"]
MANUAL = [
 ("Separation, 7 days before", "Mishnah Yoma 1:1", "outside the pyramid", "preparation"),
 ("Five immersions, ten washings", "Yoma 3:3", "the well shaft and the subterranean chamber (the water below)", "MAPPING: purification at the lowest level first"),
 ("White linen garments", "Lev 16:4", "the entrance (north face)", "the player enters in linen, no gold"),
 ("Spoken confession: 'Please, O Name ...'", "Yoma 3:8", "the descending passage", "the first voice"),
 ("Incense and coals carried west through the sanctuary to the veil", "Lev 16:12; Yoma 5:1", "the ascending passage past the 3 granite plugs, then the Grand Gallery (7 corbels)", "the ascent"),
 ("Through the veil", "Lev 16:12", "the antechamber's 3 portcullis slabs", "the barrier before the inner room"),
 ("Incense on the coals: the cloud covers the ark's cover", "Lev 16:13", "the King's Chamber, at the coffer", "CALC: the cloud fills %.0f m3" % V),
 ("Blood: one upward, seven downward, counted aloud", "Lev 16:14; Yoma 5:3", "at the coffer", "eight measured strokes"),
 ("The Name spoken; the people bow and answer 'Blessed be the name of the glory of his kingdom for ever'", "Yoma 6:2; Tamid 3:8", "the King's Chamber -> out through the two shafts", "CALC: the voice in the chamber and outside, below"),
 ("The scapegoat sent to the wilderness", "Lev 16:21-22; Yoma 6:4", "out by the descending passage", "removal outward"),
]
out["manual"] = [dict(step=a, text=b, pyramid=c, note=d) for a, b, c, d in MANUAL]
# CALC 1: the voice in the King's Chamber
out["voice_in_kings_chamber"] = dict(favoured_note_Hz=R40["preferred_note_Hz"], favoured_note=R40["preferred_note"], rt_s=R40["rt_s"],
    levels_dB_at_2m={k: v for k, v in R40["levels_dB_at_2m"].items() if "voice" in k or "shout" in k or "chant" in k},
    thresholds="a shout (94 dB) passes the 90 dB level at which loud low tones stimulate the balance organ")
# CALC 2: the chamber plus its two shafts as a Helmholtz resonator (shafts about 0.2 x 0.2 m; north about 71 m, south about 53 m; approx)
A = 0.20 * 0.20; Ls = (71.0, 53.0)
fh = C / (2 * math.pi) * math.sqrt(sum(A / (V * (L + 1.7 * math.sqrt(A / math.pi))) for L in Ls))
out["helmholtz"] = dict(chamber_volume_m3=round(V, 1), shafts="2, about 0.20 x 0.20 m, about 71 and 53 m long (approx)", f_Hz=round(fh, 3), period_s=round(1 / fh, 1),
    note="infrasonic: the chamber 'breathes' through its shafts about once every %.0f s (cf. Noah's ark, round 57)" % (1 / fh))
# CALC 3: the voice heard outside through the shafts
def outside(L_in_dB, r, duct_loss_dB_per_m=0.15):
    I = 10 ** (L_in_dB / 10) * 1e-12; P = I / 4 * A * 2; Lw = 10 * math.log10(P / 1e-12) - duct_loss_dB_per_m * np.mean(Ls)
    return round(Lw - 20 * math.log10(r) - 8, 1)
out["voice_outside"] = {src: {f"{r} m from a shaft mouth": outside(L, r) for r in (10, 50, 200)} for src, L in (("loud voice 87 dB inside", 87.0), ("shout 94 dB inside", 94.0))}
out["voice_outside"]["note"] = "night ambient about 20 dB: the shout is audible within about 50 m of the shaft mouths, not at Jericho (round 47)"
# CALC 4: do the ritual's counts match the pyramid's counts beyond chance?
ritual = {"days of separation": 7, "immersions": 5, "washings": 10, "sprinklings down": 7, "sprinkling up": 1, "goats": 2, "confessions": 3, "linen garments": 4, "gold garments": 8}
pyramid = {"granite plugs": 3, "portcullis slabs": 3, "Grand Gallery corbels": 7, "relieving chambers": 5, "King's Chamber roof beams": 9, "air shafts": 4, "chambers": 3, "coffer": 1}
def matches(r, p): return sum(1 for a in r.values() if a in set(p.values()))
obs = matches(ritual, pyramid)
nul = [matches({k: int(rng.integers(1, 11)) for k in ritual}, pyramid) for _ in range(20000)]
out["count_matches"] = dict(ritual=ritual, pyramid=pyramid, ritual_numbers_found_in_pyramid=obs, null_mean=round(float(np.mean(nul)), 2), p=round(float((np.array(nul) >= obs).mean()), 3),
    pairs=[f"{a} {v} = {b}" for a, v in ritual.items() for b, w in pyramid.items() if v == w])
# RENDER: the activation sequence in the King's Chamber
def bell(f, d=0.6):
    n = int(d * SR); t = np.arange(n) / SR; return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * (3 + r)) for r, a in ((1, 1), (2.76, .5), (5.4, .3)))
f0 = R40["preferred_note_Hz"]
T = 70.0; mix = np.zeros(int(T * SR)); P = lambda y, t0, g: E.place(mix, g * E.norm(y), t0)
for i in range(40): P(bell(rng.uniform(2200, 4200)), 0.5 + i * 0.16 + rng.uniform(0, 0.04), 0.05)     # walking in (bells at the hem)
n = int(10 * SR); tt = np.arange(n) / SR; smoke = lfilter(*butter(2, [300 / (SR / 2), 1200 / (SR / 2)], btype="band"), rng.standard_normal(n)) * np.minimum(1, tt / 3) * np.minimum(1, (10 - tt) / 3)
P(smoke, 8.0, 0.15)                                                                                    # the incense cloud (breath noise)
for k, t0 in enumerate([19.0] + [20.6 + 0.9 * j for j in range(7)]):                                  # one upward, seven downward
    n = int(0.25 * SR); tap = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 40); P(lfilter(*butter(2, 2500 / (SR / 2)), tap), t0, 0.35 if k == 0 else 0.25)
for text, t0, g, grp in (("אָנָּא הַשֵּׁם", 29.0, 0.9, 1), ("אָנָּא הַשֵּׁם כַּפֶּר נָא", 34.0, 0.9, 1)):
    w = E.parse_hebrew(text, "tiberian"); y, *_ = E.render(w, "hebrew", "tiberian", "ritual", "none", None, f0, None, True, grp); P(y, t0, g)
w = E.parse_hebrew("בָּרוּךְ שֵׁם כְּבוֹד מַלְכוּתוֹ לְעוֹלָם וָעֶד", "tiberian"); y, *_ = E.render(w, "hebrew", "tiberian", "chant", "none", None, f0 * 0.75, None, True, 12)
y = lfilter(*butter(2, 500 / (SR / 2)), y); P(y, 46.0, 0.35)                                            # the people's answer, heard faintly from outside through the shafts
tt = np.arange(len(mix)) / SR; mix += 0.04 * np.sin(2 * np.pi * f0 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * fh * tt))   # the chamber's note, breathing at the Helmholtz rate
y = E.reverb(E.norm(mix), "kings_chamber")
wav = os.path.join(HERE, "audio", "r64_kings_chamber_activation.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav)
out["render"] = dict(file=os.path.relpath(mp3, ROOT), sequence=["0.5 s walking in: the bells at the hem", "8 s the incense cloud", "19 s one upward, seven downward",
    "29 s 'ana hashem' ('Please, O Name') on the chamber's note, %.0f Hz" % f0, "34 s 'ana hashem kapper na' ('Please, O Name, grant atonement')",
    "46 s the people's answer from outside, heard through the shafts", "throughout: the chamber's note, breathing at its Helmholtz rate"])
json.dump(out, open(os.path.join(HERE, "round64_results.json"), "w"), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k != "manual"}, ensure_ascii=False, indent=1, default=float))
