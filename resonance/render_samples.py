#!/usr/bin/env python3
"""Render a 90-second sample of every preset to samples/NN.mp3, plus its evidence card (samples/NN.json).
MP3 is written as true stereo (no joint-stereo coding), so the binaural difference between the ears is kept intact."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); from resonance import render, evidence_card, write_wav
P = json.load(open(os.path.join(HERE, "presets.json"), encoding="utf-8"))["presets"]; os.makedirs(os.path.join(HERE, "samples"), exist_ok=True)
for i, cfg in enumerate(P, 1):
    y, st, c, W = render(cfg, 90); w = os.path.join(HERE, "samples", f"{i:02d}.wav"); write_wav(w, y)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-c:a", "libmp3lame", "-b:a", "128k", "-joint_stereo", "0", w[:-4] + ".mp3"], check=True); os.remove(w)
    json.dump(evidence_card(c, W), open(w[:-4] + ".json", "w"), ensure_ascii=False, indent=1); print(i, cfg["name"])
