#!/usr/bin/env python3
"""Test a list of configurations. Each one is rendered, and the audio is then MEASURED, so nothing is taken on trust.

Checks for each configuration
  beat         binaural: R - L cancels every shared layer and leaves only the two carrier tones, whose spacing is
               measured in 8-second windows. Monaural or isochronic: the envelope rate of the mono mix in a band
               around the carrier.
  breath       rate of the slow loudness swell of the whole mix, compared with the configured pace.
  voice        f0 of the voice stem, compared with the root; share of voice energy that falls on out-breaths.
  bone         simulated bone conduction (each ear hears the other at -5 dB): how much interaural difference
               survives. This shows why binaural is switched off for that device.
  safety       RMS and peak level, clipping, fades, beat limit, carrier inside the device band.
Usage: python3 verify.py <list.json | presets.json> [seconds per test, default 90] [out report.json]"""
import json, os, sys
import numpy as np
from scipy.signal import hilbert, butter, sosfiltfilt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from resonance import render, evidence_card, SR, path_curve
def win_peaks(x, fc, span=40, w=8.0):
    """Two strongest spectral peaks near fc in each window: (time, spacing)."""
    out = []; L = int(w * SR)
    for s in range(0, len(x) - L, L):
        seg = x[s:s + L] * np.hanning(L); N = 1 << 21; sp = np.abs(np.fft.rfft(seg, N)); f = np.fft.rfftfreq(N, 1 / SR); m = (f > fc - span) & (f < fc + span)
        fs, ss = f[m], sp[m]; i = np.argmax(ss); f1 = fs[i]; ss2 = ss.copy(); ss2[np.abs(fs - f1) < 0.3] = 0; f2 = fs[np.argmax(ss2)]
        out.append(((s + L / 2) / SR, abs(f2 - f1)))
    return out
def env_rate(x, fc, lo, hi, w=8.0, bw=None):
    bw = bw or max(30, 2.5 * hi); sos = butter(4, [max(20, fc - bw) / (SR / 2), (fc + bw) / (SR / 2)], btype="band", output="sos")
    e = np.abs(hilbert(sosfiltfilt(sos, x))); out = []; L = int(w * SR)
    for s in range(0, len(e) - L, L):
        seg = e[s:s + L] - e[s:s + L].mean(); N = 1 << 20; sp = np.abs(np.fft.rfft(seg * np.hanning(L), N)); f = np.fft.rfftfreq(N, 1 / SR); m = (f > lo) & (f < hi)
        out.append(((s + L / 2) / SR, float(f[m][np.argmax(sp[m])])))
    return out
def breath_rate(x):
    fr = int(0.05 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(fr) / fr, "valid")[::fr]); e = e - np.convolve(e, np.ones(200) / 200, "same")
    N = 1 << 16; sp = np.abs(np.fft.rfft(e * np.hanning(len(e)), N)); f = np.fft.rfftfreq(N, 0.05); m = (f > 0.04) & (f < 0.5); return float(f[m][np.argmax(sp[m])] * 60)
def f0_est(v):
    a = v[len(v) // 3: len(v) // 3 + SR]
    if np.abs(a).max() < 1e-6: a = v[np.argmax(np.abs(v)) - SR // 2: np.argmax(np.abs(v)) + SR // 2]
    ac = np.correlate(a[:8000], a[:16000], "valid")[::-1] if False else np.fft.irfft(np.abs(np.fft.rfft(a, 1 << 16)) ** 2)[:SR // 40]
    lo = SR // 500; k = lo + np.argmax(ac[lo:]); return SR / k
def check(cfg, seconds):
    y, st, c, W = render(cfg, seconds); n = len(y); e = c["entrainment"]; res = dict(name=c["name"], device=c["device"], mode=e["mode"], warnings=W, checks=[])
    def add(name, want, got, ok, note=""): res["checks"].append(dict(check=name, expected=want, measured=got, passed=bool(ok), note=note))
    sl = slice(int(c["safety"]["fade_s"] * SR), n - int(c["safety"]["fade_s"] * SR)); target = path_curve(e["path"], n)
    if e["mode"] == "binaural":
        pk = win_peaks((y[:, 1] - y[:, 0])[sl], e["carrier"]); t0 = c["safety"]["fade_s"]
        err = [abs(b - target[int((t + t0) * SR)]) for t, b in pk]; add("binaural beat (R-L spacing)", f"{target[sl.start]:.2f} -> {target[sl.stop - 1]:.2f} Hz", f"{pk[0][1]:.2f} -> {pk[-1][1]:.2f} Hz", max(err) < 0.6, f"max error {max(err):.2f} Hz over {len(pk)} windows")
        keep = {}
        for att in (10, 5, 0):
            g = 10 ** (-att / 20); bc = np.stack([y[:, 0] + g * y[:, 1], y[:, 1] + g * y[:, 0]], 1); keep[att] = np.std(bc[:, 1] - bc[:, 0]) / np.std(y[:, 1] - y[:, 0])
        add("bone-conduction simulation", "interaural difference shrinks as crosstalk rises", ", ".join(f"{v:.0%} left at {k} dB" for k, v in keep.items()), keep[0] < 0.01, "why binaural is switched to monaural on bone-conduction devices")
    elif e["mode"] in ("monaural", "isochronic"):
        hi = max(b for _, b in e["path"]) * 1.6 + 1; lo = max(0.3, min(b for _, b in e["path"]) * 0.5)
        er = env_rate((y[:, 0] + y[:, 1])[sl], e["carrier"], lo, hi, bw=max(b for _, b in e["path"]) * 1.2 + 3); t0 = c["safety"]["fade_s"]
        err = [abs(b - target[int((t + t0) * SR)]) for t, b in er]; add(f"{e['mode']} beat (envelope rate)", f"{target[sl.start]:.2f} -> {target[sl.stop - 1]:.2f} Hz", f"{er[0][1]:.2f} -> {er[-1][1]:.2f} Hz", np.median(err) < 0.8, f"median error {np.median(err):.2f} Hz")
        add("identical ears", "L = R", f"max |L-R| {np.abs(y[:, 0] - y[:, 1]).max():.1e}", np.abs(y[:, 0] - y[:, 1]).max() < 1e-9)
    if c["breath"]["guide"]:
        p = c["breath"].get("path") or [[0, c["breath"]["per_min"]]] * 2; want = np.mean([b for _, b in p]); got = breath_rate((y[:, 0] + y[:, 1])[sl])
        add("breath pace (loudness swell)", f"{want:.2f} per min (mean of path)", f"{got:.2f} per min", abs(got - want) < 0.25 * want + 0.3)
    if c["voice"]["on"] and np.abs(st["voice"]).max() > 0:
        f = f0_est(st["voice"]); r = c["root"]["hz"]; ratio = f / r; oct_ = 2 ** round(np.log2(ratio))
        add("voice pitch = root", f"{r:.1f} Hz (or an octave)", f"{f:.1f} Hz", abs(ratio / oct_ - 1) < 0.03)
        ex = np.zeros(n, bool)
        for s, li, le in c["_cycles"]: ex[int((s + li) * SR): int((s + li + le) * SR)] = True
        share = float((st["voice"][ex] ** 2).sum() / ((st["voice"] ** 2).sum() + 1e-12)); add("voice on out-breaths", "> 95% of voice energy", f"{share:.1%}", share > 0.95)
    rms = 20 * np.log10(np.sqrt(np.mean(y ** 2))); pk = 20 * np.log10(np.abs(y).max()); fi = 20 * np.log10(np.sqrt(np.mean(y[:SR // 2] ** 2)) + 1e-12)
    add("average level", f"{c['safety']['target_rms_db']} dBFS (or lower after limiting)", f"{rms:.1f} dBFS", rms <= c["safety"]["target_rms_db"] + 0.1)
    add("peak / clipping", "< -1 dBFS", f"{pk:.2f} dBFS", pk <= -0.99); add("fade-in", "first 0.5 s quiet (< -45 dBFS)", f"{fi:.1f} dBFS", fi < -45)
    lo, hi = (300, 650) if c["device"] == "bone_conduction" else (200, 900) if e["mode"] == "binaural" else (200, 1200)
    if e["mode"] != "none": add("carrier in device band", f"{lo}-{hi} Hz", f"{e['carrier']} Hz", lo <= e["carrier"] <= hi)
    if c["device"] == "bone_conduction":
        sp = np.abs(np.fft.rfft(y[:, 0][sl][: 1 << 20])); f = np.fft.rfftfreq(min(1 << 20, sl.stop - sl.start), 1 / SR); low = (sp[f < 200] ** 2).sum() / (sp ** 2).sum()
        add("little energy below 200 Hz (bone conduction)", "< 5%", f"{low:.1%}", low < 0.05)
    res["card"] = evidence_card(c, W); res["passed"] = all(x["passed"] for x in res["checks"]); return res
if __name__ == "__main__":
    L = json.load(open(sys.argv[1], encoding="utf-8")); L = L["presets"] if isinstance(L, dict) else L; secs = float(sys.argv[2]) if len(sys.argv) > 2 else 90
    outp = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "verify_report.json"); R = []
    for cfg in L:
        r = check(cfg, secs); R.append(r); print(("PASS " if r["passed"] else "FAIL ") + r["name"])
        for x in r["checks"]: print(f"     {'ok ' if x['passed'] else 'NO '} {x['check']:40s} want {str(x['expected']):34s} got {x['measured']}")
        for w in r["warnings"]: print("     !", w)
    json.dump(R, open(outp, "w"), ensure_ascii=False, indent=1, default=str); print(f"{sum(r['passed'] for r in R)} of {len(R)} configurations pass every check")
