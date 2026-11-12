#!/usr/bin/env python3
"""Real-channel test for spoken KANON: 40 random programs with error-correction tails, sent through telephone band
limits, noise and real speech codecs (via ffmpeg), in the studio channel and the phone channel.
Writes channels_results.json. Usage: python3 channels.py"""
import json, os, random, subprocess, sys, tempfile
import numpy as np
from scipy.signal import butter, sosfiltfilt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); import kanon as K
T = tempfile.mkdtemp(); R = random.Random(5); progs = [K.random_program(R) for _ in range(40)]; nr = np.random.default_rng(5)
def phone(y): return sosfiltfilt(butter(6, [300 / (K.FS / 2), 3400 / (K.FS / 2)], btype="band", output="sos"), y)
def codec(y, args, ext):
    a, b, c = os.path.join(T, "in.wav"), os.path.join(T, "c." + ext), os.path.join(T, "out.wav"); K.save_wav(a, y / np.abs(y).max() * 0.9)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a] + args + [b], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", b, "-ar", str(K.FS), "-ac", "1", c], check=True); return K.load_wav(c)
noisy = lambda y, snr: y + nr.standard_normal(len(y)) * y.std() / 10 ** (snr / 20)
CH = [("telephone band 300-3400 Hz", phone), ("telephone band + noise at 10 dB SNR", lambda y: noisy(phone(y), 10)),
      ("GSM full-rate 13 kbit/s (mobile voice)", lambda y: codec(y, ["-ar", "8000", "-ac", "1", "-c:a", "libgsm"], "gsm")),
      ("G.726 ADPCM 32 kbit/s (DECT, VoIP)", lambda y: codec(y, ["-ar", "8000", "-ac", "1", "-c:a", "g726", "-b:a", "32k"], "g726.wav")),
      ("Opus 16 kbit/s (internet voice)", lambda y: codec(y, ["-c:a", "libopus", "-b:a", "16k"], "opus")),
      ("Opus 8 kbit/s", lambda y: codec(y, ["-c:a", "libopus", "-b:a", "8k"], "opus"))]
out = {}
for name, ch in CH:
    for prof in ("studio", "phone"):
        ok = fix = bad = 0
        for p in progs:
            t = K.add_ecc(p); d = K.decode(ch(K.encode(t, channel=prof)), channel=prof); fixed, rep = K.correct(d); want = K.norm_text(p)
            ok += K.strip_checksums(d) == want; fix += fixed == want
            bad += fixed != want and not any(r["status"].startswith(("uncorr", "no tail")) for r in rep) and fixed.count("|") == want.count("|")
        out[f"{name} | {prof}"] = dict(exact_as_heard=ok, exact_after_correction=fix, wrong_without_flag=bad, of=len(progs))
        print(f"{name:40s} {prof:7s} heard {ok:2d}/40  corrected {fix:2d}/40  wrong-unflagged {bad}")
json.dump(out, open(os.path.join(HERE, "channels_results.json"), "w"), indent=1)
