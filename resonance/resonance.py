#!/usr/bin/env python3
"""RESONANCE: a configurable sound engine built on the project's data points.

A configuration (JSON) names, for each layer, what it is made from. Every choice traces back to datapoints.json, and
every rendered file comes with an evidence card: which parts rest on measurement, established science, mixed results,
reconstruction or symbolism.

LAYERS
  entrainment  a beat at a chosen rate, which can glide: binaural (headphones only), monaural, or isochronic pulses.
               The carrier is tuned to the drone's scale, so the beat tone is part of the harmony.
  breath       a paced breathing cycle (rate, inhale:exhale ratio, which can glide). The drone swells on the in-breath.
  voice        a chanted vowel on every out-breath, from the inventory of a chosen ancient language, closing on a hum.
               The pitch is the root.
  drone        a chord from a tuning: Pythagorean, Babylonian heptatonic rotation, Archytas' genera, Timaeus world-soul,
               harmonic series, or just intonation.
  root         a frequency in Hz, or the strongest resonance of a described room (e.g. Solomon's cube sanctuary).
  room         reverberation from that room's computed modes.
DEVICE RULES  headphones: binaural allowed (carrier 200-900 Hz, beat at most 30 Hz).
              bone_conduction: the two ears are not separate (interaural attenuation about 0-10 dB), so binaural becomes
              monaural; nothing below 250 Hz.
              speakers: binaural becomes isochronic.
SAFETY        average level fixed at -20 dBFS, peaks below -1 dBFS, fades in and out, beat limited to 45 Hz.

Python:  from resonance import design, render;  cfg = design("deep_relaxation", device="headphones", language="hebrew")
CLI:     python3 resonance.py config.json out.wav      or      python3 resonance.py --design focus_gamma40 bone_conduction koine 3 out.wav"""
import copy, json, math, os, sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as VE
SR = VE.SR; DP = json.load(open(os.path.join(HERE, "datapoints.json"), encoding="utf-8"))
DEFAULT = dict(name="untitled", minutes=10.0, device="headphones", seed=1,
               entrainment=dict(mode="binaural", path=[[0, 10.0], [1, 8.0]], carrier="auto", level_db=-14.0),
               breath=dict(per_min=6.0, inhale_exhale=[4, 6], path=None, guide=True),
               voice=dict(language="koine", vowels="auto", order="cycle", hum_end=True, level_db=-7.0, on=True),
               drone=dict(tuning="pythagorean", rotation=1, level_db=-10.0, on=True),
               root=dict(source="room:debir", hz=110.0), room=dict(name="debir", wet=0.35, rt=3.0),
               safety=dict(target_rms_db=-20.0, fade_s=8.0))
TARGETS = {   # target state -> breath, beat path, mode; evidence for each piece
 "resonance_breathing": dict(breath=6.0, ratio=[4, 6], beat=[[0, 10.0], [1, 10.0]], mode="isochronic", ent_db=-22,
     evidence=dict(breath="ESTABLISHED: 6 breaths a minute raises heart-rate variability", beat="MIXED: a faint 10 Hz (alpha) pulse")),
 "deep_relaxation": dict(breath=6.0, breath_end=5.0, ratio=[4, 6], beat=[[0, 10.0], [0.6, 7.0], [1, 6.0]], mode="binaural", ent_db=-14,
     evidence=dict(breath="ESTABLISHED: slow, exhale-weighted breathing", beat="MIXED: alpha-to-theta glide; brain entrainment by beats is inconsistent")),
 "sleep_onset": dict(breath=6.0, breath_end=4.5, ratio=[4, 7], beat=[[0, 7.0], [0.5, 4.0], [1, 2.0]], mode="binaural", ent_db=-15,
     evidence=dict(breath="ESTABLISHED: slow breathing calms autonomic arousal", beat="MIXED: theta-to-delta glide")),
 "meditation_theta": dict(breath=6.0, ratio=[4, 6], beat=[[0, 8.0], [0.3, 6.0], [1, 6.0]], mode="binaural", ent_db=-14,
     evidence=dict(breath="ESTABLISHED", beat="MIXED: 6 Hz theta")),
 "focus_gamma40": dict(breath=None, ratio=[2, 3], beat=[[0, 40.0], [1, 40.0]], mode="monaural", ent_db=-12,
     evidence=dict(breath="(no breath guide)", beat="ESTABLISHED: the auditory cortex follows 40 Hz modulation; PRELIMINARY: any effect on focus or memory")),
 "alert_beta": dict(breath=10.0, ratio=[2, 3], beat=[[0, 14.0], [1, 18.0]], mode="isochronic", ent_db=-15,
     evidence=dict(breath="ESTABLISHED: a 10-per-minute pace is close to normal", beat="MIXED: beta")),
 "chant_only": dict(breath=6.0, ratio=[4, 6], beat=None, mode="none", ent_db=-60,
     evidence=dict(breath="ESTABLISHED", beat="(no beat: voice, drone and room only)")),
}
def db(x): return 10 ** (x / 20)
def merge(a, b):
    out = copy.deepcopy(a)
    for k, v in (b or {}).items(): out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out
def design(target, device="headphones", language="koine", minutes=10.0, room="debir", tuning="pythagorean", order="cycle"):
    T = TARGETS[target]; cfg = merge(DEFAULT, dict(name=f"{target} / {language} / {room} / {device}", minutes=minutes, device=device))
    cfg["breath"] = dict(per_min=T["breath"] or 12.0, inhale_exhale=T["ratio"], guide=T["breath"] is not None,
                         path=[[0, T["breath"]], [1, T.get("breath_end", T["breath"])]] if T["breath"] else None)
    cfg["entrainment"].update(mode=T["mode"], path=T["beat"] or [[0, 0], [1, 0]], level_db=T["ent_db"])
    cfg["voice"].update(language=language, order=order, on=T["breath"] is not None)
    cfg["drone"]["tuning"] = tuning; cfg["room"]["name"] = room; cfg["root"]["source"] = f"room:{room}" if room in DP["rooms"] else "hz"
    cfg["target"] = target; cfg["target_evidence"] = T["evidence"]; return cfg
# ------------------------------------------------------------------------------------------------ resolution
def scale(tuning, rotation=1):
    t = DP["tunings"][tuning]; r = t["ratios"]
    if t.get("as_partials"): return r, True
    k = (rotation - 1) % len(r); rot = [x / r[k] if x >= r[k] else 2 * x / r[k] for x in r[k:] + r[:k]]; return sorted(rot), False
def resolve(cfg):
    """Apply device rules and pick root and carrier. Returns (resolved config, warnings)."""
    c = merge(DEFAULT, cfg); W = []; dev = c["device"]; e = c["entrainment"]
    src = c["root"]["source"]
    if src.startswith("room:"):
        rm = DP["rooms"][src[5:]]
        if rm.get("reported_hz"): c["root"]["hz"] = rm["reported_hz"]; c["root"]["why"] = f"reported resonance of {rm['name']}"
        else:
            f, k = max([m for m in rm.get("modes_voice", []) if 90 <= m[0] <= 140] or [(110.0, 0)], key=lambda m: (m[1], -abs(m[0] - 115)))
            c["root"]["hz"] = f; c["root"]["why"] = f"strongest mode of {rm['name']} between 90 and 140 Hz ({k} modes coincide at {f} Hz)"
    else: c["root"]["why"] = "set by hand"
    while c["root"]["hz"] < 55: c["root"]["hz"] *= 2; W.append("root moved up an octave into the voice range")
    root = c["root"]["hz"]; sc, partials = scale(c["drone"]["tuning"], c["drone"].get("rotation", 1)); c["_scale"] = sc; c["_partials"] = partials
    if dev == "bone_conduction" and e["mode"] == "binaural":
        e["mode"] = "monaural"; W.append("bone conduction: the two ears are not isolated (interaural attenuation about 0-10 dB), so binaural was switched to monaural (the beat is put into the sound itself)")
    if dev == "speakers" and e["mode"] == "binaural":
        e["mode"] = "isochronic"; W.append("speakers: binaural beats need one tone per ear, so binaural was switched to isochronic pulses")
    beats = [b for _, b in e["path"]]
    if max(beats) > 45: e["path"] = [[t, min(45.0, b)] for t, b in e["path"]]; W.append("beat limited to 45 Hz")
    if e["mode"] == "binaural" and max(beats) > 30: W.append("binaural beats above about 30 Hz are not heard as beats; monaural is the stronger choice for 40 Hz")
    lo, hi = (300, 650) if dev == "bone_conduction" else (200, 900) if e["mode"] == "binaural" else (200, 1200)
    if e["carrier"] == "auto":
        cands = [root * r * 2 ** o for r in (sc if not partials else [1, 3 / 2, 4 / 3]) for o in range(1, 6) if lo <= root * r * 2 ** o <= hi]
        e["carrier"] = round(min(cands, key=lambda f: abs(f - (420 if dev != "bone_conduction" else 450))), 2) if cands else 420.0
        e["carrier_why"] = "a degree of the drone's own scale, moved by octaves into the device's best band"
    elif not (lo <= e["carrier"] <= hi): W.append(f"carrier {e['carrier']} Hz is outside the best band for this device ({lo}-{hi} Hz)")
    c["_min_hz"] = 250.0 if dev == "bone_conduction" else 40.0
    if dev == "bone_conduction" and c["voice"]["on"] and root < 250: W.append(f"bone conduction: the voice's fundamental ({root:.0f} Hz) is felt weakly; its vowel formants (300-2,500 Hz) carry")
    lang = DP["languages"][c["voice"]["language"]]; v = c["voice"]["vowels"]; c["_vowels"] = lang["vowels"] if v == "auto" else v
    return c, W
# ------------------------------------------------------------------------------------------------ signals
def path_curve(path, n):
    t = np.linspace(0, 1, n); P = np.array(path, float); return np.interp(t, P[:, 0], P[:, 1])
def breath_cycles(c, n):
    """List of (start, inhale_len, exhale_len) in samples, following the breath path."""
    b = c["breath"]; path = b.get("path") or [[0, b["per_min"]], [1, b["per_min"]]]; ri, re_ = b["inhale_exhale"]; out = []; s = int(c["safety"]["fade_s"] * SR * 0.5)
    while s < n:
        rate = float(np.interp(s / n, *zip(*path))); per = 60.0 / rate * SR; li = int(per * ri / (ri + re_)); le = int(per - li); out.append((s, li, le)); s += li + le
    return out
def breath_env(cycles, n):
    B = np.zeros(n)
    for s, li, le in cycles:
        a = np.sin(np.linspace(0, np.pi / 2, li)) ** 2; d = np.cos(np.linspace(0, np.pi / 2, le)) ** 2
        seg = np.concatenate([a, d])[: max(0, n - s)]; B[s: s + len(seg)] = seg
    return B
def vowel_order(c, k):
    vs = c["_vowels"]; o = c["voice"]["order"]
    if o.startswith("pgm_square:"):    # PGM XIII square: a rising triangle (1..7 repetitions) from a direction's start vowel
        starts = dict(dawn=0, earth=1, west=2, south=3, cosmos=4, sky=5, north=6); s = starts[o.split(":")[1]]; seq = [vs[(s + i) % len(vs)] for i in range(len(vs)) for _ in range(i + 1)]
        return [seq[i % len(seq)] for i in range(k)]
    return [vs[i % len(vs)] for i in range(k)]
def lowcut(y, f):
    return sosfilt(butter(2, f / (SR / 2), btype="high", output="sos"), y) if f > 30 else y
def render(cfg, seconds=None):
    """Returns (stereo float array, stems dict, resolved config, warnings)."""
    c, W = resolve(cfg); n = int((seconds or c["minutes"] * 60) * SR); rng = np.random.default_rng(c["seed"]); t = np.arange(n) / SR; root = c["root"]["hz"]
    stems = {}
    cyc = breath_cycles(c, n); B = breath_env(cyc, n) if c["breath"]["guide"] else np.ones(n) * 0.7
    # drone ---------------------------------------------------------------
    D = np.zeros(n)
    if c["drone"]["on"]:
        sc, partials = c["_scale"], c["_partials"]
        if partials: freqs = [root * r for r in sc if root * r < 2200]; amps = [1 / (1 + 0.35 * i) for i in range(len(freqs))]; harm = 1
        else: freqs = [root / 2, root, root * sc[4 % len(sc)], root * 2, root * 2 * sc[2 % len(sc)]]; amps = [0.6, 1.0, 0.7, 0.45, 0.25]; harm = 6
        for i, (f, a) in enumerate(zip(freqs, amps)):
            while f < c["_min_hz"]: f *= 2
            lfo = 0.75 + 0.25 * np.sin(2 * np.pi * t / (23.0 + 7 * i) + i)
            for h in range(1, harm + 1):
                if f * h > 6000: break
                D += a * lfo * np.sin(2 * np.pi * f * h * t + rng.uniform(0, 6.3)) / h ** 1.6
        D = D / (np.abs(D).max() + 1e-9) * (0.55 + 0.45 * B)
        air = VE.bandnoise(n, 900, 1400); air = air / (np.abs(air).max() + 1e-9)
        inh = np.zeros(n)
        for s, li, le in cyc: inh[s: s + li] = np.sin(np.linspace(0, np.pi, li))[: max(0, n - s)] if c["breath"]["guide"] else 0
        D = D + 0.05 * air * inh
    stems["drone"] = D
    # voice: one vowel per out-breath --------------------------------------
    Vc = np.zeros(n)
    if c["voice"]["on"]:
        F = [np.full(n, DP["formants"]["ə"][j], float) for j in range(3)]; A = np.zeros(n); seq = vowel_order(c, len(cyc))
        for (s, li, le), v in zip(cyc, seq):
            a = s + li; e_ = min(n, a + le)
            if a >= n: break
            L = e_ - a; u = np.linspace(0, 1, L); env = np.minimum(1, u / 0.08) * np.minimum(1, (1 - u) / 0.12) ** 1.5
            fv = DP["formants"][v]; fm = DP["formants"]["m"]; hum = (u > 0.75) if c["voice"]["hum_end"] else np.zeros(L, bool)
            for j in range(3): F[j][a:e_] = np.where(hum, fm[j], fv[j])
            A[a:e_] = env * np.where(hum, 0.55, 1.0)
        for j in range(3): F[j] = VE.smooth(F[j], 40)
        f0 = np.full(n, root) * (1 + 0.004 * np.sin(2 * np.pi * t / 9.0))
        while f0[0] < c["_min_hz"] * 0.5: f0 = f0 * 2
        src = VE.glottal_source(f0, vib=0.25, jitter=0.002); Vc = VE.formant_filter(src, *F) * VE.smooth(A, 20); Vc /= np.abs(Vc).max() + 1e-9
    stems["voice"] = Vc
    # room ------------------------------------------------------------------
    dry = db(c["drone"]["level_db"]) * D + db(c["voice"]["level_db"]) * Vc; mono = dry
    rmn = c["room"]["name"]
    if rmn in DP["rooms"] and c["room"]["wet"] > 0:
        ir = VE.modal_ir(tuple(DP["rooms"][rmn]["dims_m"]), c["room"]["rt"]); wet = fftconvolve(dry, ir)[:n]; wet *= np.std(dry) / (np.std(wet) + 1e-12)
        mono = (1 - c["room"]["wet"]) * dry + c["room"]["wet"] * wet
    mono = lowcut(mono, c["_min_hz"])
    # entrainment -------------------------------------------------------------
    e = c["entrainment"]; fc = e["carrier"]; beat = path_curve(e["path"], n); pb = 2 * np.pi * np.cumsum(beat) / SR; pc = 2 * np.pi * fc * t
    if e["mode"] == "binaural": L_, R_ = np.sin(pc - pb / 2), np.sin(pc + pb / 2)
    elif e["mode"] == "monaural": L_ = R_ = 0.5 * (np.sin(pc - pb / 2) + np.sin(pc + pb / 2))
    elif e["mode"] == "isochronic": g = (0.5 - 0.5 * np.cos(pb)) ** 1.5; L_ = R_ = np.sin(pc) * g
    else: L_ = R_ = np.zeros(n)
    stems["entrain_L"], stems["entrain_R"] = L_, R_
    ga = db(e["level_db"]) * (0.0 if e["mode"] == "none" else 1.0)
    out = np.stack([mono + ga * L_, mono + ga * R_], 1)
    # safety --------------------------------------------------------------
    fade = int(c["safety"]["fade_s"] * SR); fade = min(fade, n // 4); ramp = np.ones(n); ramp[:fade] = np.linspace(0, 1, fade) ** 2; ramp[n - fade:] = np.linspace(1, 0, fade) ** 2
    out *= ramp[:, None]; rms = np.sqrt(np.mean(out ** 2)) + 1e-12; out *= db(c["safety"]["target_rms_db"]) / rms
    pk = np.abs(out).max()
    if pk > db(-1): out *= db(-1) / pk; W.append("peak limiter reduced the overall level to keep peaks below -1 dBFS")
    c["_cycles"] = [(s / SR, li / SR, le / SR) for s, li, le in cyc]
    return out, stems, c, W
def evidence_card(c, W):
    e = c["entrainment"]; lang = DP["languages"][c["voice"]["language"]]; rm = DP["rooms"].get(c["room"]["name"])
    rows = [("device", c["device"], "ESTABLISHED", "device rules (binaural needs isolated ears; bone conduction has little bass)"),
            ("entrainment", f"{e['mode']} beat, path {e['path']} Hz, carrier {e['carrier']} Hz", "ESTABLISHED" if e['mode'] != 'none' and max(b for _, b in e['path']) >= 38 else "MIXED",
             "a 40 Hz response in the auditory cortex is established; effects of slower beats on mind and body are mixed"),
            ("breath", f"{c['breath'].get('path') or c['breath']['per_min']} per minute, in:out {c['breath']['inhale_exhale']}" if c["breath"]["guide"] else "no guide", "ESTABLISHED" if c["breath"]["guide"] else "-", DP["breath"]["resonance_6"]["note"][:120]),
            ("voice", f"{lang['name']}: vowels {' '.join(c['_vowels'])}, order {c['voice']['order']}, hum at the end of each out-breath" if c["voice"]["on"] else "off", lang["evidence"], lang["note"][:140] + " Humming raises nasal nitric oxide (ESTABLISHED)."),
            ("drone", f"{c['drone']['tuning']} rotation {c['drone'].get('rotation', 1)}: ratios {[round(x, 4) for x in c['_scale']]}", DP["tunings"][c["drone"]["tuning"]]["evidence"], DP["tunings"][c["drone"]["tuning"]]["note"][:140]),
            ("root", f"{c['root']['hz']} Hz: {c['root']['why']}", rm["evidence"] if rm and c["root"]["source"].startswith("room:") else "-", (rm or {}).get("note", "")[:140]),
            ("room", f"{c['room']['name']} (wet {c['room']['wet']}, RT {c['room']['rt']} s)", rm["evidence"] if rm else "-", "reverberation from the room's computed modes")]
    if c.get("target_evidence"): rows.append(("target", c.get("target"), "-", "; ".join(f"{k}: {v}" for k, v in c["target_evidence"].items())))
    return dict(name=c["name"], rows=[dict(layer=a, setting=b, evidence=x, basis=d) for a, b, x, d in rows], warnings=W,
                disclaimer="An experimental listening tool, not a medical device. No claim is made that it activates any brain area beyond what the 'evidence' column states. Listen at a moderate level; stop if you feel discomfort. Not for use while driving.")
def write_wav(path, x):
    from scipy.io import wavfile; wavfile.write(path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--design": cfg = design(a[1], a[2], a[3], float(a[4])); outp = a[5]
    else: cfg = json.load(open(a[0])); outp = a[1]
    y, stems, c, W = render(cfg); write_wav(outp, y); card = evidence_card(c, W)
    json.dump(dict(config={k: v for k, v in c.items() if not k.startswith("_")}, card=card), open(outp.rsplit(".", 1)[0] + ".json", "w"), ensure_ascii=False, indent=1)
    for r in card["rows"]: print(f"  {r['layer']:12s} [{r['evidence']:13s}] {r['setting']}")
    for w in W: print("  !", w)
