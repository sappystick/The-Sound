#!/usr/bin/env python3
"""E5 stimuli: Origen's claim that a sacred formula loses force in translation.

Eight formulas, each in three versions:
  ORIGINAL   the formula in the sound the Greek-speaking churches used (Koine voice v2, evidence rules only)
  SCRAMBLED  the same syllables in a different order, same voice and settings (controls for 'foreign-sounding')
  TRANSLATED the English meaning (a male English neural voice)
All are loudness-matched and placed in the same small hall. Main comparison: ORIGINAL vs SCRAMBLED (same voice);
secondary: ORIGINAL vs TRANSLATED (different voice, so read with care).
Usage: python3 e5_stimuli.py <greek voice .onnx> <english voice .onnx>   -> experiments/e5_app/audio/*.mp3, stimuli.json
"""
import json, os, subprocess, sys
from fractions import Fraction
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "code", "voice"))
import koine_voice as K
E = K.E; GV, EV = sys.argv[1:3]; OUT = os.path.join(HERE, "e5_app", "audio"); os.makedirs(OUT, exist_ok=True)
ITEMS = [("amen", "Ἀμήν.", "Truly.", "Hebrew word, kept in Greek"), ("talitha", "Ταλιθα κουμ.", "Little girl, arise.", "Aramaic, Mark 5:41"),
         ("ephphatha", "Εφφαθα.", "Be opened.", "Aramaic, Mark 7:34"), ("abba", "Αββα ὁ πατήρ.", "Father, father.", "Aramaic and Greek, Mark 14:36"),
         ("egoeimi", "Ἐγώ εἰμι.", "I am.", "Greek, John 18:6"), ("sabaoth", "Κύριε Σαβαώθ.", "Lord of hosts.", "Hebrew title, kept in Greek (Origen's example)"),
         ("adonai", "Ἀδωναΐ.", "My Lord.", "Hebrew title (Origen's example)"), ("kyrie", "Κύριε ἐλέησον.", "Lord, have mercy.", "Greek liturgy")]
def permute(sylls, seed):
    """a different order of the same syllables: rotate by one; if that equals the original (e.g. 'abba'), reverse"""
    if len(sylls) < 2: return sylls
    for cand in (sylls[1:] + sylls[:1], sylls[::-1], sylls[2:] + sylls[:2]):
        if [s["ph"] for s in cand] != [s["ph"] for s in sylls]: return cand
    return sylls
gv = K.Voice(GV)
from piper import PiperVoice
from piper.config import SynthesisConfig
ev = PiperVoice.load(EV)
def finish(y, sr, path):
    if sr != E.SR: r = Fraction(E.SR, sr).limit_denominator(1000); y = resample_poly(y, r.numerator, r.denominator)
    y = np.concatenate([np.zeros(int(0.15 * E.SR)), y, np.zeros(int(0.2 * E.SR))]); rms = np.sqrt(np.mean(y[np.abs(y) > 0.01 * np.abs(y).max()] ** 2)); y = y / rms * 0.08
    y = E.reverb(y, "house_church"); y = y / max(1.0, np.abs(y).max() / 0.95)
    w = path[:-4] + ".wav"; wavfile.write(w, E.SR, (np.clip(y, -1, 1) * 32767).astype(np.int16)); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-ac", "1", "-b:a", "96k", path], check=True); os.remove(w)
    return round(len(y) / E.SR, 2)
meta = []
for k, (iid, greek, eng, note) in enumerate(ITEMS):
    words = [dict(raw=w, sylls=K.word_ipa(w), spk="narrator", moods=[], rules=[]) for w in greek.split()]
    a, _, _ = K.render_group(gv, [dict(x) for x in words], delivery=False); d1 = finish(a, gv.sr, os.path.join(OUT, f"{iid}_original.mp3"))
    allsyl = [s for w in words for s in w["sylls"]]; perm = permute(allsyl, k); sw = [dict(raw="x" + (greek[-1] if greek[-1] in ".;" else ""), sylls=perm, spk="narrator", moods=[], rules=[])]
    b, _, _ = K.render_group(gv, sw, delivery=False); d2 = finish(b, gv.sr, os.path.join(OUT, f"{iid}_scrambled.mp3"))
    c = np.concatenate([np.asarray(ch.audio_float_array, float) for ch in ev.synthesize(eng, SynthesisConfig(length_scale=1.1))]); d3 = finish(c, ev.config.sample_rate, os.path.join(OUT, f"{iid}_translated.mp3"))
    meta.append(dict(id=iid, original=greek, translation=eng, note=note, scrambled_ipa=" ".join("".join(s["ph"]) for s in perm), original_ipa=" ".join("".join(s["ph"]) for s in allsyl), dur=[d1, d2, d3]))
    print(iid, meta[-1]["original_ipa"], "|", meta[-1]["scrambled_ipa"], "|", eng, meta[-1]["dur"], flush=True)
json.dump(meta, open(os.path.join(HERE, "e5_app", "stimuli.json"), "w"), ensure_ascii=False, indent=1)
