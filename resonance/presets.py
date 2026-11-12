#!/usr/bin/env python3
"""The preset list: one configuration per tradition and target, all built with design() and then adjusted by hand.
Writes presets.json (the list verify.py tests and the web app loads)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); from resonance import design
P = []
def add(name, cfg, **kw):
    for k, v in kw.items():
        if isinstance(v, dict): cfg[k].update(v)
        else: cfg[k] = v
    cfg["name"] = name; P.append(cfg)
add("Prologue breath: Koine vowels in Solomon's cube, 6 breaths a minute", design("resonance_breathing", "headphones", "koine", 12, "debir"))
add("Seven-vowel square, dawn (PGM XIII), alpha to theta", design("deep_relaxation", "headphones", "pgm_seven", 14, "debir", order="pgm_square:dawn"))
add("Psalm of descent: Hebrew vowels, theta to delta, for sleep", design("sleep_onset", "headphones", "hebrew", 20, "tabernacle"))
add("Abba: Aramaic vowels, theta meditation", design("meditation_theta", "headphones", "aramaic", 15, "hekal"), drone=dict(tuning="greek_enharmonic"))
add("Ankh: Egyptian three vowels in the King's Chamber, 6 breaths a minute", design("resonance_breathing", "headphones", "egyptian", 12, "kings_chamber"), drone=dict(tuning="harmonic_series"))
add("Me of Sumer: four vowels, Babylonian tuning rotation 5, hypogeum 111 Hz", design("meditation_theta", "headphones", "sumerian", 15, "hypogeum"), drone=dict(tuning="babylonian_heptatonic", rotation=5))
add("World soul: Timaeus partials, alert beta", design("alert_beta", "speakers", "attic", 8, "debir", tuning="timaeus_world_soul"))
add("Forty: 40 Hz monaural pulse for bone conduction (Coptic vowels)", design("focus_gamma40", "bone_conduction", "coptic", 10, "debir"), voice=dict(on=True), breath=dict(guide=True, per_min=6.0, inhale_exhale=[4, 6], path=None))
add("Bone-conduction calm: Hebrew vowels, isochronic alpha", design("resonance_breathing", "bone_conduction", "hebrew", 12, "debir"))
add("Chant only: Koine seven vowels, no beat", design("chant_only", "speakers", "pgm_seven", 10, "debir", order="pgm_square:north"))
json.dump(dict(presets=P), open(os.path.join(HERE, "presets.json"), "w"), ensure_ascii=False, indent=1); print(len(P), "presets")
