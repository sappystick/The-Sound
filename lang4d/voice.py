#!/usr/bin/env python3
"""KANON human-voice front end (v0.1): speech -> KANON text, speaker-adaptive, no trained model.

How a person speaks KANON (the "spoken form"):
  * a syllable = consonant + vowel, run together inside a word:   gia  = "gi" + "'a"   (cadence vowel = glottal onset)
  * pause >= ~0.15 s  = word boundary ;  pause >= ~0.5 s = verse boundary ("breath")
  * "#" (number)  = one hum "mmm" (~0.3 s), then each base-12 digit as consonant+"i"  (digit d -> CONS[d] + i)
  * "=" (seal)    = two short hums, then the seal word
  * "!" and "~" are written marks (prosody flags); they are not recognised from sound in v0.1.
Tuning verse (said once, ~20 s, before any program): the 7 vowels, one hum, the 12 consonants + "a", then "'a".
It plays the role of tuning the strings: the recogniser learns THIS voice's vowel colours and consonant spectra
(nearest-centroid on log-mel features), so it works for any pitch and vocal-tract size.

Validation here uses synthetic voices (the repo's formant engine, scaled to different vocal-tract sizes and pitches,
two speaking rates, with added noise). It has NOT been validated on real human recordings - see WHITEPAPER section 5.
Usage: python3 lang4d/voice.py eval | decode CAL.wav PROG.wav
"""
import json, math, os, sys
import numpy as np
from scipy.signal import resample_poly, find_peaks
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "code", "engine"))
import kanon as K
import engine as E

SR = 16000; HOP = 160; WIN = 400; NMEL = 24
V2IPA = {"a": "a", "e": "ɛ", "y": "e", "i": "i", "o": "o", "u": "y", "w": "ɔ"}      # Koine values of the 7 letters
CLASSES_V = list(K.VOWELS) + ["~hum"]
CLASSES_C = list(K.CONS) + ["'"]                                                      # "'" = glottal onset (cadence)

# ------------------------------------------------------------------ synthetic voices
def _scale_entry(v, s):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v * s
    if isinstance(v, tuple): return tuple(_scale_entry(x, s) for x in v)
    return v

class Voice:
    """A synthetic speaker: pitch, vocal-tract scale (formants x scale), speaking mode, pauses."""
    def __init__(self, f0=120.0, scale=1.0, mode="speech", word_gap=0.32, verse_gap=0.8, seed=0):
        self.f0, self.scale, self.mode, self.word_gap, self.verse_gap = f0, scale, mode, word_gap, verse_gap
        self.rng = np.random.default_rng(seed)

    def _render_word(self, letters):
        toks, i = [], 0
        while i < len(letters):
            c = letters[i]
            if c in K.CONS and i + 1 < len(letters) and letters[i + 1] in K.VOWELS:
                toks += [c, V2IPA[letters[i + 1]]]; i += 2
            elif c in K.VOWELS:
                toks += ["ʔ", V2IPA[c]]; i += 1
            else: raise ValueError(letters)
        words = E.parse_phonemes(" ".join(toks))
        saveV, saveC = dict(E.VOWELS), dict(E.CONS)
        try:
            for k in list(E.VOWELS): E.VOWELS[k] = _scale_entry(E.VOWELS[k], self.scale)
            for k in list(E.CONS): E.CONS[k] = _scale_entry(E.CONS[k], self.scale)
            y, *_ = E.render(words, "greek", "koine", self.mode, "none", None, float(self.f0), "diatonic", True, 1)
        finally:
            E.VOWELS.clear(); E.VOWELS.update(saveV); E.CONS.clear(); E.CONS.update(saveC)
        return resample_poly(y, 160, 441) * 0.9 / (np.abs(y).max() + 1e-9)

    def hum(self, dur):
        n = int(dur * SR); t = np.arange(n) / SR
        f = self.f0 * (1 + 0.012 * np.sin(2 * np.pi * 5 * t)); ph = np.cumsum(f) / SR
        src = sum(np.sin(2 * np.pi * k * ph) / k ** 1.5 for k in range(1, 20)) * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.04)
        from scipy.signal import lfilter
        y = np.zeros(n)
        for F, bw in zip((250, 1100, 2300), (60, 120, 200)):
            b, a = E.resonator_coeffs(F * self.scale, bw); y += lfilter(b, a, src)
        return 0.45 * y / (np.abs(y).max() + 1e-9)

    def pause(self, s): return np.zeros(int(s * SR))

    def say(self, src):
        out = [self.pause(0.25)]
        for vtext in src.replace("\n", " ").split("|"):
            toks = [t.rstrip("!").lstrip("~") for t in vtext.split()]
            for tk in [t for t in toks if t]:
                if tk.startswith("#"):
                    out += [self.hum(0.30), self.pause(0.06), self._render_word("".join(K.CONS[K.DIGITS.index(d)] + "i" for d in tk[1:])), self.pause(self.word_gap)]
                elif tk.startswith("="):
                    out += [self.hum(0.16), self.pause(0.07), self.hum(0.16), self.pause(0.06), self._render_word(tk[1:]), self.pause(self.word_gap)]
                else: out += [self._render_word(tk), self.pause(self.word_gap)]
            out.append(self.pause(self.verse_gap - self.word_gap))
        return np.concatenate(out)

    def tuning(self):
        """the tuning verse; returns audio. Vowels, one hum, 12 consonants + a (twice), glottal a."""
        out = [self.pause(0.3)]
        for v in K.VOWELS: out += [self._render_word(v), self.pause(0.35)]
        out += [self.hum(0.3), self.pause(0.35)]
        for rep in range(2):
            for c in K.CONS: out += [self._render_word(c + "a"), self.pause(0.35)]
        out += [self._render_word("a"), self.pause(0.4)]
        return np.concatenate(out)

def add_noise(y, snr_db, seed=1):
    rng = np.random.default_rng(seed); sig = np.sqrt(np.mean(y[np.abs(y) > 0.02 * np.abs(y).max()] ** 2))
    return y + rng.standard_normal(len(y)) * sig / (10 ** (snr_db / 20))

# ------------------------------------------------------------------ analysis
def _mel_fb(nfft=512):
    f = lambda m: 700 * (10 ** (m / 2595) - 1); m = lambda hz: 2595 * math.log10(1 + hz / 700)
    pts = f(np.linspace(m(80), m(7600), NMEL + 2)); bins = np.fft.rfftfreq(nfft, 1 / SR)
    fb = np.zeros((NMEL, len(bins)))
    for i in range(NMEL):
        lo, c, hi = pts[i], pts[i + 1], pts[i + 2]
        fb[i] = np.clip(np.minimum((bins - lo) / (c - lo), (hi - bins) / (hi - c)), 0, None)
    return fb
FB = _mel_fb()

def analyse(y):
    n = 1 + (len(y) - WIN) // HOP
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    F = y[idx] * np.hanning(WIN)[None, :]
    en = 10 * np.log10(np.mean(y[idx] ** 2, axis=1) + 1e-10)
    X = np.fft.rfft(F, 512, axis=1); P = np.abs(X) ** 2
    mel = 10 * np.log10(P @ FB.T + 1e-9)
    r = np.fft.irfft(np.abs(np.fft.rfft(F, 1024, axis=1)) ** 2, axis=1)[:, :WIN]
    per = np.max(r[:, 40:228], axis=1) / (r[:, 0] + 1e-9)
    return dict(en=en, per=np.clip(per, 0, 1), mel=mel, P=P)

def nuclei(A):
    en, per = A["en"], A["per"]; floor = np.percentile(en, 8)
    ev = en + 30 * (per - 1)
    ev = np.convolve(ev, np.ones(3) / 3, mode="same")
    pk, _ = find_peaks(ev, prominence=5, distance=11, height=ev.max() - 32)
    out = []
    for p in pk:
        lo = p
        while lo > 0 and ev[lo - 1] >= ev[p] - 7 and ev[lo - 1] <= ev[lo] + 1.5: lo -= 1
        hi = p
        while hi < len(ev) - 1 and ev[hi + 1] >= ev[p] - 7 and ev[hi + 1] <= ev[hi] + 1.5: hi += 1
        out.append(dict(pk=int(p), lo=int(lo), hi=int(hi)))
    return out, floor

def _vowel_feat(A, n):
    a, b = n["pk"] - max(1, (n["pk"] - n["lo"]) // 2), n["pk"] + max(1, (n["hi"] - n["pk"]) // 2)
    m = A["mel"][max(a, 0):b + 1].mean(axis=0)
    return m - m.mean()

def _cons_feat(A, lo_frame, hi_frame, floor, nuc_level):
    seg = slice(lo_frame, max(hi_frame, lo_frame + 1))
    en = A["en"][seg]; act = en > floor + 6
    if act.sum() == 0: act = np.ones_like(en, bool)
    w = 10 ** (en / 10) * act; w = w / w.sum()
    mel = 10 * np.log10((w[:, None] * 10 ** (A["mel"][seg] / 10)).sum(axis=0) + 1e-9)
    rel = mel - nuc_level
    voiced = float((A["per"][seg][act] > 0.5).mean()) if act.any() else 0.0
    dur = float(act.sum()) * HOP / SR
    return np.concatenate([rel, [voiced * 12, min(dur, 0.2) * 40]])

def _segment(A, ns, floor):
    """consonant regions, pauses and nucleus levels from the analysis"""
    en = A["en"]; sil = en < floor + 6
    info = []
    for j, n in enumerate(ns):
        prev_end = ns[j - 1]["hi"] if j else 0
        # silent run directly after the previous nucleus
        k = prev_end + 1
        while k < n["lo"] and sil[k]: k += 1
        gap = (k - prev_end - 1) * HOP / SR
        if j == 0: gap = 9.9
        if gap >= 0.16 or j == 0:
            start = k
        else:
            start = prev_end + 1
        end = n["lo"]
        if end - start < 2: start = max(0, end - 3)
        nuc_level = float(np.mean(A["mel"][n["pk"]]))
        info.append(dict(gap=gap, cons=(start, end), level=nuc_level))
    return info

class Recogniser:
    def __init__(self): self.vc = None; self.cc = None; self.cm = None; self.cs = None; self.gap_unit = 0.35

    def tune(self, y):
        A = analyse(y); ns, floor = nuclei(A); info = _segment(A, ns, floor)
        want = 7 + 1 + 24 + 1
        if len(ns) != want: raise ValueError(f"tuning failed: heard {len(ns)} syllables, expected {want} (speak the tuning verse, with clear pauses)")
        vc, cf = {}, {c: [] for c in CLASSES_C}
        for j, n in enumerate(ns):
            if j < 7: vc[CLASSES_V[j]] = _vowel_feat(A, n)
            elif j == 7: vc["~hum"] = _vowel_feat(A, n)
            elif j < 32:
                c = K.CONS[(j - 8) % 12]; cf[c].append(_cons_feat(A, info[j]["cons"][0], info[j]["cons"][1], floor, info[j]["level"]))
            else: cf["'"].append(_cons_feat(A, info[j]["cons"][0], info[j]["cons"][1], floor, info[j]["level"]))
        self.vc = vc
        allf = np.array([f for v in cf.values() for f in v]); self.cm = allf.mean(0); self.cs = allf.std(0) + 1.0
        self.cc = {c: np.mean(np.array(v), axis=0) for c, v in cf.items()}
        gaps = [info[j]["gap"] for j in range(1, len(ns))]; self.gap_unit = float(np.median(gaps))
        return self

    def decode(self, y):
        A = analyse(y); ns, floor = nuclei(A); info = _segment(A, ns, floor)
        syl = []
        for j, n in enumerate(ns):
            vf = _vowel_feat(A, n)
            v = min(self.vc, key=lambda k: float(np.sum((vf - self.vc[k]) ** 2)))
            gap = info[j]["gap"]
            if v == "~hum": syl.append(dict(v="~", c=None, gap=gap, dur=(n["hi"] - n["lo"] + 1) * HOP / SR)); continue
            cf = (_cons_feat(A, info[j]["cons"][0], info[j]["cons"][1], floor, info[j]["level"]) - self.cm) / self.cs
            c = min(self.cc, key=lambda k: float(np.sum((cf - (self.cc[k] - self.cm) / self.cs) ** 2)))
            syl.append(dict(v=v, c=c, gap=gap))
        wg, vg = 0.16, 0.50
        wg_, vg_ = wg, vg
        toks, cur, mode = [], "", None
        def flush():
            nonlocal cur, mode
            if cur: toks.append(("#" if mode == "#" else "=" if mode == "=" else "") + cur)
            cur, mode = "", None
        hums = 0
        for j, s in enumerate(syl):
            if j > 0 and s["gap"] >= wg_ and s["v"] != "~":
                pass
            if s["v"] == "~":
                if j > 0 and s["gap"] >= vg_: flush(); toks.append("|")
                elif j > 0 and s["gap"] >= wg_ and hums == 0: flush()
                hums += 1; continue
            if j > 0 and s["gap"] >= vg_: flush(); toks.append("|")
            elif j > 0 and s["gap"] >= wg_: flush()
            if hums and not cur: mode = "#" if hums == 1 else "="
            hums = 0 if not (hums and not cur) else 0
            if mode == "#" and not cur and hums == 0 and s["c"] not in (None, "'"):
                pass
            if mode == "#":
                cur += str(K.DIGITS[K.CONS.index(s["c"])]) if s["c"] in K.CONS else ""
            else:
                cur += ("" if s["c"] == "'" else (s["c"] or "")) + s["v"]
        flush()
        text = " ".join(toks).replace(" | ", " | ")
        return " ".join(text.split())

def norm(src):
    s = " ".join(" | ".join(p.strip() for p in src.replace("\n", " ").split("|")).split())
    return s.replace("~", "").replace("!", "")

# ------------------------------------------------------------------ evaluation
SPEAKERS = {"large man 95 Hz": dict(f0=95, scale=0.92), "man 120 Hz": dict(f0=120, scale=1.0), "woman 210 Hz": dict(f0=210, scale=1.15),
            "child 300 Hz": dict(f0=300, scale=1.3), "man, fast 130 Hz": dict(f0=130, scale=0.97, mode="declaim")}
PROGRAMS = ["di", "demorini", "sa #7 gia ta #3 | di", "ka #e bwi da", "pia ria | lu #3 pie | ha #2 demorini"]

def rand_words(rng, n):
    out = []
    for _ in range(n):
        ns = int(rng.integers(1, 4)); w = "".join(K.CONS[rng.integers(12)] + K.VOWELS[rng.integers(7)] for _ in range(ns))
        if rng.random() < 0.3: w += K.VOWELS[rng.integers(7)]
        out.append(w)
    return out

def evaluate():
    res = {"note": "synthetic voices from the repo's formant engine (tract scale, pitch, speaking mode); not real human recordings"}
    rng = np.random.default_rng(65); per = {}
    tot = dict(prog=0, prog_ok=0, syl=0, syl_ok=0)
    conf_v, conf_c = {}, {}
    for name, spec in SPEAKERS.items():
        vo = Voice(**spec, seed=3)
        try: rec = Recogniser().tune(vo.tuning())
        except Exception as e: per[name] = dict(error=str(e)); continue
        row = {}
        for snr in (None, 25, 15):
            ok = 0
            for p in PROGRAMS:
                y = vo.say(p); y = add_noise(y, snr) if snr else y
                try: d = rec.decode(y)
                except Exception as e: d = f"<error {e}>"
                ok += d == norm(p); tot["prog"] += snr is None; tot["prog_ok"] += (d == norm(p)) and snr is None
            row[f"programs exact, {snr or 'clean'}{' dB' if snr else ''}"] = f"{ok}/{len(PROGRAMS)}"
        words = rand_words(rng, 40); a = b = 0
        for w in words:
            y = vo.say(w)
            try: d = rec.decode(y)
            except Exception: d = ""
            a += d == w
            tot["syl"] += 1; tot["syl_ok"] += d == w
            if d != w:
                for x, z in zip(w, d):
                    if x != z:
                        (conf_v if x in K.VOWELS else conf_c).setdefault(x + "->" + z, 0); (conf_v if x in K.VOWELS else conf_c)[x + "->" + z] += 1
        row["random words exact (40, clean)"] = f"{a}/40"
        per[name] = row
    res["per_speaker"] = per; res["totals_clean"] = dict(programs=f"{tot['prog_ok']}/{tot['prog']}", random_words=f"{tot['syl_ok']}/{tot['syl']}")
    res["top_confusions"] = dict(vowels=dict(sorted(conf_v.items(), key=lambda kv: -kv[1])[:6]), consonants=dict(sorted(conf_c.items(), key=lambda kv: -kv[1])[:8]))
    return res

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "eval"
    if cmd == "eval":
        r = evaluate(); json.dump(r, open(os.path.join(HERE, "voice_eval.json"), "w"), indent=1, ensure_ascii=False); print(json.dumps(r, indent=1, ensure_ascii=False))
    elif cmd == "decode":
        import wave
        def rd(p):
            with wave.open(p) as f: x = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(float) / 32768; sr = f.getframerate()
            return resample_poly(x, SR, sr) if sr != SR else x
        rec = Recogniser().tune(rd(sys.argv[2])); print(rec.decode(rd(sys.argv[3])))
