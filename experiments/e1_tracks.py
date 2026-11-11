#!/usr/bin/env python3
"""E1 recitation tracks: the Lord's Prayer (Matthew 6:9-13) and John 1:1-5 in reconstructed Koine, one phrase per breath,
at chant pace (with a 1.5 s breath gap) and the Lord's Prayer at normal speaking pace (control). Participants recite along.
Usage: python3 e1_tracks.py <sblgnt> <greek voice .onnx>"""
import os, subprocess, sys
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "code", "voice")); import koine_voice as K
E = K.E; V = K.assign_speakers(K.load_john(sys.argv[1])); voice = K.Voice(sys.argv[2])
import glob, collections, re
M = collections.OrderedDict()
for l in open(glob.glob(os.path.join(sys.argv[1], "*-Mt-*"))[0], encoding="utf-8"):
    p = l.split(); M.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=re.sub(r"[⸀⸁⸂⸃⸄⸅]", "", p[3]), w=K.nrm(p[4]), lem=K.nrm(p[6]), pos=p[1], parse=p[2], spk="narrator"))
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
for name, src, refs, scale, gap in (("e1_lords_prayer_chant", M, [(6, v) for v in range(9, 14)], 1.6, 1.5), ("e1_lords_prayer_normal", M, [(6, v) for v in range(9, 14)], 0.95, 0.3), ("e1_john_prologue_chant", V, [(1, v) for v in range(1, 6)], 1.6, 1.5)):
    K.VC["base_length_scale"] = scale; K.PAUSE.update({",": gap, "·": gap, ";": gap, ".": gap})
    y, words = K.render_passage(voice, src, refs, delivery=False, space="house_church", verse_gap=gap)
    w = os.path.join(HERE, "audio", name + ".wav"); wavfile.write(w, E.SR, (np.clip(y, -1, 1) * 32767).astype(np.int16)); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-b:a", "96k", w[:-4] + ".mp3"], check=True); os.remove(w)
    phrases = sum(1 for x in words if re.search(r"[,.;·]$", x["word"])); dur = len(y) / E.SR
    print(f"{name}: {dur:.1f} s, {phrases} phrases -> {60 * phrases / dur:.1f} breaths per minute if one breath per phrase")
