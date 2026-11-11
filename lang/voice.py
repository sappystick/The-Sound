#!/usr/bin/env python3
"""Speak Sala, with the fourth dimension: a melody for each stance.

Voice: the project's neural voice (Piper, Greek model: its sounds p t k m n s l w j h + a e i o u cover Sala exactly),
shifted to an adult male vocal tract; the melody is imposed with Praat from the table below.
Stress: the first syllable of every root (+2.5 semitones, slightly louder). Grammar words are unstressed.
MELODY (the stance word at the end of a sentence selects it; the plain statement has none):
"""
import json, os, re, subprocess, sys
from fractions import Fraction
import numpy as np
import parselmouth
from parselmouth.praat import call
from scipy.io import wavfile
from scipy.signal import resample_poly
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "voice")); sys.path.insert(0, HERE)
import koine_voice as K
import sala as S
E = K.E
#            base shift (st), range x, rate x, gain dB, final contour over the last two syllables (st), description
MELODY = {None: dict(base=0, rng=1.0, rate=1.0, gain=0, final=(-1, -4), name="statement", shape="level, falling at the end"),
          "ka": dict(base=0.5, rng=1.0, rate=1.0, gain=0, final=(1, 6), name="question", shape="rising at the end"),
          "pu": dict(base=1, rng=0.9, rate=0.97, gain=-1, final=(-2, 2), name="request", shape="soft, dipping then lifting"),
          "hi": dict(base=2.5, rng=1.6, rate=1.03, gain=1.5, final=(4, 0), name="joy", shape="high and wide, a lift then a fall"),
          "he": dict(base=-3, rng=0.55, rate=0.84, gain=-3, final=(-2, -5), name="sorrow", shape="low, narrow and slow, sinking"),
          "wa": dict(base=3.5, rng=0.8, rate=1.14, gain=4, final=(3, 3), name="urgent", shape="high, fast and loud, staying high")}
BASE_HZ = 108; st = lambda x: 2 ** (x / 12)
IPA = {"y": "j"}
def phon(word, kind):
    if kind == "name": return [IPA.get(c, c) for c in re.sub(r"[^a-z]", "", word.lower().replace("c", "k").replace("x", "ks"))], []
    syl = S.syllables(word.lower()); stress = [i == 0 and kind in ("root", "num") for i in range(len(syl))]; out = []
    for s_, strs in zip(syl, stress): out += (["ˈ"] if strs else []) + [IPA.get(s_[0], s_[0]), s_[1]]
    return out, stress
def render_sentence(voice, toks, stance):
    """toks: [(kind, text)] for one sentence (stance word included as its last token). -> audio @ voice.sr, word times"""
    m = MELODY[stance]; ls = 1.18 / m["rate"]; words = []
    for k, v in toks:
        w = S.number_word(v) if k == "num" else v; ph, stress = phon(w, k); nsyl = max(1, len(S.syllables(w.lower())) if k != "name" else len(re.findall(r"[aeiou]+", w.lower())) or 1)
        words.append(dict(w=w, ph=ph, stress=stress or [True] + [False] * (nsyl - 1), n=nsyl))
    def seq(ws):
        out = []
        for i, w in enumerate(ws): out += w["ph"] + ([" "] if i < len(ws) - 1 else [])
        return out
    full = seq(words) + (["?"] if stance == "ka" else ["."]); a = voice.synth(full, ls); sr = voice.sr; dur = len(a) / sr
    ends = [len(voice.synth(seq(words[:k]), ls)) / sr for k in range(1, len(words))] + [dur]; ends = list(np.maximum.accumulate(np.minimum(ends, dur))); starts = [0.0] + ends[:-1]
    total = sum(w["n"] for w in words); si = 0; pts = []; gain = np.zeros(len(a))
    for wi, w in enumerate(words):
        for j in range(w["n"]):
            t0 = starts[wi] + (ends[wi] - starts[wi]) * j / w["n"]; t1 = starts[wi] + (ends[wi] - starts[wi]) * (j + 1) / w["n"]; frac = si / max(1, total - 1); si += 1
            v = m["base"] - 1.5 * frac + (2.5 * m["rng"] if w["stress"][j] else 0)
            left = total - si                       # syllables after this one
            if left == 1: v += m["final"][0]
            if left == 0: v += m["final"][1]
            pts.append(((t0 + t1) / 2, BASE_HZ * st(v))); gain[int(t0 * sr):int(t1 * sr)] = m["gain"] + (1.5 if w["stress"][j] else 0)
    snd = parselmouth.Sound(a, sampling_frequency=sr); snd = call(snd, "Change gender", 75, 600, 0.86, 0, 1, 1)
    man = call(snd, "To Manipulation", 0.01, 75, 600); pt = call("Create PitchTier", "p", 0, snd.duration)
    for t, hz in pts: call(pt, "Add point", min(max(t, 0.001), snd.duration - 0.001), hz)
    call([pt, man], "Replace pitch tier"); out = call(man, "Get resynthesis (overlap-add)").values[0]
    k = max(1, int(0.03 * sr)); g = np.convolve(gain[:len(out)] if len(gain) >= len(out) else np.pad(gain, (0, len(out) - len(gain))), np.ones(k) / k, mode="same")
    return out * (10 ** (g / 20)), [dict(s=round(s_, 3), e=round(e_, 3)) for s_, e_ in zip(starts, ends)]
def speak(voice, text, path, space="house_church"):
    """Render a text (one or more sentences) to mp3; returns per-word timings across the whole file."""
    ratio = Fraction(E.SR, voice.sr).limit_denominator(1000); chunks, times, t = [], [], 0.0
    for toks, parsed in zip(S.sentences(text), S.parse(text)):
        a, wt = render_sentence(voice, toks, parsed["stance"]); a = resample_poly(a, ratio.numerator, ratio.denominator)
        times += [dict(s=round(t + x["s"], 3), e=round(t + x["e"], 3)) for x in wt]; chunks += [a, np.zeros(int(0.45 * E.SR))]; t += len(a) / E.SR + 0.45
    y = np.concatenate(chunks); y = y / (np.abs(y).max() + 1e-9) * 0.9; y = E.reverb(y, space)
    wav = path[:-4] + ".wav"; wavfile.write(wav, E.SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-b:a", "64k", path], check=True); os.remove(wav)
    return dict(dur=round(len(y) / E.SR, 2), words=times)
if __name__ == "__main__":
    # demo: the same sentence in all six melodies, with the measured pitch
    v = K.Voice(sys.argv[1]); out = os.path.join(HERE, "audio"); os.makedirs(out, exist_ok=True); res = {}
    base = S.render("mi sa see ke yu")
    for stance in (None, "ka", "pu", "hi", "he", "wa"):
        text = base + (" " + stance if stance else ""); p = os.path.join(out, f"melody_{stance or 'plain'}.mp3"); info = speak(v, text, p, space="dry")
        sr, y = wavfile.read(subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, p[:-4] + "_t.wav"], check=True) and p[:-4] + "_t.wav"); os.remove(p[:-4] + "_t.wav")
        f0 = [f for _, f in K.measure_f0(y.astype(float) / 32768, sr) if f > 0]
        res[stance or "plain"] = dict(text=text, dur=info["dur"], median_hz=round(float(np.median(f0)), 1), low=round(float(np.percentile(f0, 5)), 1), high=round(float(np.percentile(f0, 95)), 1), **{k: MELODY[stance][k] for k in ("name", "shape")})
        print(res[stance or "plain"])
    json.dump(res, open(os.path.join(HERE, "melody_check.json"), "w"), indent=1)
