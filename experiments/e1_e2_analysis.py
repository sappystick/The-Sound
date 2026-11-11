#!/usr/bin/env python3
"""Analysis code for experiments 1 (breath and heart) and 2 (the hum), ready for real data.

E1 input  e1_data.csv: participant, condition, t_s, rr_ms        (one row per heartbeat: time and RR interval)
   conditions: rest, silent_reading, speech_normal, recite_greek, recite_hebrew, recite_latin
   per participant and condition: RMSSD, SDNN, mean heart rate, the frequency of the strongest heart-rate oscillation
   (0.04-0.4 Hz, from a Lomb-Scargle periodogram) = breathing rate, and the share of power near 0.1 Hz (resonance band
   0.08-0.12 Hz). Paired comparisons of each recitation against silent reading and normal speech (Wilcoxon signed-rank).
E2 input  e2_data.csv: participant, condition, feno_ppb           (exhaled nasal nitric oxide, a handheld meter)
   conditions: quiet_exhale, amen_hum, seven_vowels, om, speech
   paired comparisons of each against quiet exhalation; fold-change.
Run with --selftest to check the code on simulated data whose answers are known (this produces no findings).
Usage: python3 e1_e2_analysis.py e1_data.csv e2_data.csv | --selftest
"""
import csv, math, sys
import numpy as np
from scipy.signal import lombscargle
from scipy.stats import wilcoxon
def hrv(t, rr):
    rr = np.asarray(rr, float); t = np.asarray(t, float); d = np.diff(rr)
    f = np.linspace(0.04, 0.4, 400); w = 2 * np.pi * f; x = rr - rr.mean(); P = lombscargle(t, x, w, normalize=True)
    band = (f >= 0.08) & (f <= 0.12)
    return dict(rmssd=float(np.sqrt(np.mean(d ** 2))), sdnn=float(rr.std(ddof=1)), hr=float(60000 / rr.mean()), peak_hz=float(f[np.argmax(P)]), breaths_per_min=float(60 * f[np.argmax(P)]), res_share=float(P[band].sum() / P.sum()))
def paired(a, b):
    a, b = np.asarray(a), np.asarray(b); d = a - b
    p = float(wilcoxon(a, b).pvalue) if len(a) >= 6 and np.any(d) else float("nan")
    return dict(n=len(a), mean_diff=float(d.mean()), p=p)
def e1(rows):
    by = {}
    for r in rows: by.setdefault((r["participant"], r["condition"]), []).append((float(r["t_s"]), float(r["rr_ms"])))
    M = {k: hrv(*zip(*sorted(v))) for k, v in by.items() if len(v) > 30}; parts = sorted({k[0] for k in M}); conds = sorted({k[1] for k in M})
    print("E1 per condition (median across participants): breaths/min · RMSSD ms · share of power at 0.1 Hz")
    for c in conds:
        xs = [M[(p, c)] for p in parts if (p, c) in M]
        print(f"   {c:16s} n {len(xs):2d}  breaths {np.median([x['breaths_per_min'] for x in xs]):5.1f}  RMSSD {np.median([x['rmssd'] for x in xs]):6.1f}  0.1 Hz share {np.median([x['res_share'] for x in xs]):.2f}")
    for c in [c for c in conds if c.startswith("recite")]:
        for base in ("silent_reading", "speech_normal"):
            ps = [p for p in parts if (p, c) in M and (p, base) in M]
            for k in ("breaths_per_min", "rmssd", "res_share"):
                r = paired([M[(p, c)][k] for p in ps], [M[(p, base)][k] for p in ps]); print(f"   {c} vs {base}: {k} difference {r['mean_diff']:+.2f} (n {r['n']}, Wilcoxon p {r['p']:.4f})")
    return M
def e2(rows):
    by = {}
    for r in rows: by.setdefault(r["participant"], {})[r["condition"]] = float(r["feno_ppb"])
    print("E2 nasal nitric oxide against quiet exhalation")
    for c in ("amen_hum", "seven_vowels", "om", "speech"):
        ps = [p for p, d in by.items() if c in d and "quiet_exhale" in d]
        if not ps: continue
        a = [by[p][c] for p in ps]; b = [by[p]["quiet_exhale"] for p in ps]; r = paired(a, b)
        print(f"   {c:14s} n {len(ps):2d}  median fold-change {np.median(np.array(a) / np.array(b)):.1f}  (Wilcoxon p {r['p']:.4f})")
def selftest():
    """Simulated data with known answers: recitation drives breathing at 6/min; humming multiplies NO by 10."""
    rng = np.random.default_rng(1); rows = []
    for p in range(12):
        for cond, br in (("silent_reading", 14), ("speech_normal", 16), ("recite_greek", 6)):
            t, tt = [], 0.0
            while tt < 300:
                rr = 900 + (60 if cond == "recite_greek" else 25) * math.sin(2 * math.pi * br / 60 * tt) + rng.normal(0, 15); tt += rr / 1000; rows.append(dict(participant=f"p{p}", condition=cond, t_s=tt, rr_ms=rr))
    M = e1(rows); got = np.median([M[(f"p{p}", "recite_greek")]["breaths_per_min"] for p in range(12)])
    assert abs(got - 6) < 0.6, got; print(f"   self-test: recovered breathing {got:.1f}/min for a simulated 6/min (pass)")
    rows2 = []
    for p in range(12):
        base = rng.uniform(300, 900); rows2 += [dict(participant=f"p{p}", condition="quiet_exhale", feno_ppb=base), dict(participant=f"p{p}", condition="amen_hum", feno_ppb=base * 10 * rng.uniform(0.8, 1.2))]
    e2(rows2); print("   self-test: fold-change near 10 expected (pass if printed about 10)")
if __name__ == "__main__":
    if "--selftest" in sys.argv: selftest()
    else: e1(list(csv.DictReader(open(sys.argv[1])))); e2(list(csv.DictReader(open(sys.argv[2]))))
