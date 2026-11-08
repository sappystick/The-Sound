#!/usr/bin/env python3
"""Koine voice: a natural neural voice speaking the project's reconstructed first-century pronunciation, with an
evidence-based prosody layer and an optional, fully traced interpretive delivery layer.

Pipeline per breath group (text between punctuation marks):
  1. PHONEMES. Each word is parsed by the project engine (code/engine, Koine era) into IPA syllables. Aspirated stops
     (th, ph, kh in 1st-century Koine) are written stop + h; everything else is passed as IPA to the neural model.
  2. VOICE. Piper (VITS, Modern Greek voice, CPU) renders the phonemes. Modern Greek is the closest living phonology to
     Koine, so the model supplies a human throat and coarticulation; the phonemes are ours, not Modern Greek spelling.
     Durations are deterministic (noise_w 0); word end times are measured by rendering each word-prefix of the group.
  3. PROSODY (Praat, PSOLA). The model's own melody is discarded. A pitch tier is built from rules (delivery_rules.json):
     reciting tone, accents, declination, cadences (evidence layer) plus speaker and mood (interpretive layer). Formants
     are shifted to an adult male vocal tract. Loudness follows stress and the rules.
  4. ROOM. The engine's room model (synagogue by default).
Every word records its speaker (estimated), timing, pitch targets, gain and the ids of every rule applied.
"""
import collections, glob, json, math, os, re, sys, unicodedata
from fractions import Fraction
import numpy as np
import parselmouth
from parselmouth.praat import call
from scipy.signal import resample_poly
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
RULES = json.load(open(os.path.join(HERE, "delivery_rules.json"), encoding="utf-8")); VC = RULES["voice"]; LEX = RULES["lexicon"]
SPEAKERS = RULES["speakers"]; SPEECHV = set(RULES["speech_verbs"])
PAUSE = {",": 0.35, "·": 0.6, ";": 0.9, ".": 0.9, "": 0.25}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
# ------------------------------------------------------------------ text, speakers, moods
def load_john(sbl):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(sbl, "*-Jn-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], w=nrm(p[4]), lem=nrm(p[6]), pos=p[1], parse=p[2]))
    return V
def assign_speakers(V):
    """Estimate who speaks each word. SBLGNT capitalises the first word of direct speech, introduced by a speech verb
    and a raised dot; the speaker is a nominative noun near that verb (else the last person named, or 'they' for a
    plural verb). Speech continues across verses until a narrative verse: one with a 3rd-person past indicative and
    no 1st/2nd-person forms."""
    cur, last_named, last_female = "narrator", None, None; named_at = -9; hist = []
    for vi, (k, toks) in enumerate(V.items()):
        for t in toks: t["raw"] = re.sub(r"[⸀⸁⸂⸃⸄⸅]", "", t["raw"])
        ranges = []
        intro = [i for i, t in enumerate(toks) if t["pos"].startswith("V") and t["lem"] in SPEECHV and t["parse"][0] not in "12"]
        for n_, i in enumerate(intro):
            start = next((j for j in range(i + 1, len(toks)) if toks[j - 1]["raw"].endswith(("·", ":")) and toks[j]["raw"][:1].isupper()), None)
            if start is None: continue
            if ranges and ranges[-1][1] == start: continue        # 'answered and said': one speech, two verbs
            who = None; lo = ranges[-1][1] if ranges else 0
            fem = any(len(toks[j]["parse"]) > 6 and toks[j]["parse"][4] == "N" and toks[j]["parse"][6] == "F" and (toks[j]["pos"] in ("RD", "RP", "RR") or toks[j]["parse"][3:4] == "P") for j in range(max(lo, i - 8), start))
            cands = []
            for j in list(range(i + 1, start)) + list(range(i, lo - 1, -1)):
                u = toks[j]
                if u["pos"][0] == "N" and len(u["parse"]) > 4 and u["parse"][4] == "N" and u["lem"] in SPEAKERS: cands.append((SPEAKERS[u["lem"]], len(u["parse"]) > 6 and u["parse"][6] == "F"))
            if fem and any(f for _, f in cands): who = next(n for n, f in cands if f)
            elif cands and not fem: who = cands[0][0]
            if who is None and fem: who = last_female or "the woman"
            plural = len(toks[i]["parse"]) > 5 and toks[i]["parse"][5] == "P"
            if who is None and plural: who = "they"
            if who is None and vi - named_at > 1 and len(hist) >= 2 and hist[-1] != hist[-2]: who = hist[-2]     # turn-taking
            if who is None: who = last_named or "a speaker"
            if not hist or hist[-1] != who: hist.append(who)
            if not hist or hist[-1] != who: hist.append(who)
            ranges.append((i, start, who))
        if ranges:
            for t in toks: t["spk"] = cur if cur != "narrator" and ranges[0][0] > 0 and not any(x["pos"].startswith("V") and x["parse"][0] == "3" and x["parse"][1] in "AI" for x in toks[:ranges[0][0]]) else "narrator"
            for n_, (i, start, who) in enumerate(ranges):
                stop = ranges[n_ + 1][0] if n_ + 1 < len(ranges) else len(toks)
                for j in range(i, start): toks[j]["spk"] = "narrator"
                for j in range(start, stop): toks[j]["spk"] = who
                cur = who
        else:
            first2 = any(t["pos"].startswith("V") and t["parse"][0] in "12" for t in toks) or any(t["lem"] in ("εγω", "συ", "ημεισ", "υμεισ") for t in toks)
            narrative = any(t["pos"].startswith("V") and t["parse"][0] == "3" and t["parse"][1] in "AI" and t["parse"][3] == "I" for t in toks)
            if cur != "narrator" and (first2 or not narrative): spk = cur
            else: spk = cur = "narrator"
            for t in toks: t["spk"] = spk
        for t in toks:
            if t["spk"] == "narrator" and t["pos"][0] == "N" and len(t["parse"]) > 4 and t["parse"][4] == "N" and t["lem"] in SPEAKERS and SPEAKERS[t["lem"]][0].isupper():
                if len(t["parse"]) > 6 and t["parse"][6] == "F": last_female = SPEAKERS[t["lem"]]
                else: last_named = SPEAKERS[t["lem"]]
                named_at = vi
    return V
def verse_moods(toks):
    lem = {t["lem"] for t in toks}; m = []
    for key, rid in (("grief", "I-GRIEF"), ("cry", "I-CRY"), ("joy", "I-JOY"), ("glory", "I-GLORY"), ("death", "I-DEATH")):
        if lem & set(LEX[key]): m.append(rid)
    if "I-DEATH" in m and not ({"αποθνησκω", "παραδιδωμι"} & lem) and not any(t["w"] == "τετελεσται" for t in toks): m.remove("I-DEATH")   # telew only as 'it is finished'
    return m
# ------------------------------------------------------------------ phonemes
def segs(ph):
    out = []
    for c in ph:
        if c in "ʰː" and out: out[-1] += c
        else: out.append(c)
    return out
def word_ipa(raw):
    grave = "\u0300" in unicodedata.normalize("NFD", raw)
    clean = re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw)
    if not clean: return []
    try: W = E.parse_greek(unicodedata.normalize("NFC", clean), "koine")
    except Exception: return []
    out = [dict(s) for w in W for s in (w if isinstance(w, list) else [w])]
    if grave:
        for s_ in out:
            if s_["accent"]: s_["accent"] = "grave"
    return out
def to_piper(sylls):
    out = []
    for s in sylls:
        if s["accent"]: out.append("ˈ")
        for p in s["ph"]:
            for q in segs(p):
                if q.endswith("ʰ"): out += [q[0], "h"]
                elif q.endswith("ː"): out += [q[:-1], "ː"]
                else: out.append(q)
    return out
# ------------------------------------------------------------------ voice
class Voice:
    def __init__(self, model):
        from piper import PiperVoice
        from piper.config import SynthesisConfig
        self.v = PiperVoice.load(model); self.sr = self.v.config.sample_rate; self.SC = SynthesisConfig; self.map = self.v.config.phoneme_id_map
    def synth(self, ph, ls):
        ids = self.v.phonemes_to_ids([p for p in ph if p in self.map])
        a = np.asarray(self.v.phoneme_ids_to_audio(ids, self.SC(length_scale=ls, noise_scale=VC["noise_scale"], noise_w_scale=VC["noise_w"])), float)
        if a.dtype != float or np.abs(a).max() > 2: a = a / 32768.0
        return trim(a, self.sr)
def trim(a, sr):
    env = np.abs(a); thr = 0.02 * env.max() if env.max() > 0 else 0
    idx = np.flatnonzero(env > thr)
    if not len(idx): return a[:0]
    return a[max(0, idx[0] - int(0.01 * sr)): idx[-1] + int(0.03 * sr)]
# ------------------------------------------------------------------ prosody
def st(x): return 2 ** (x / 12)
def render_group(voice, words, delivery=True):
    """words: list of dicts {raw, sylls, spk, moods, rules(list)} for one breath group. -> (audio @ voice.sr, word timings, pitch points)"""
    end_punct = re.search(r"[,.;·]$", words[-1]["raw"]); end_punct = end_punct.group(0) if end_punct else ""
    spk = words[0]["spk"]; moods = words[0]["moods"] if delivery else []
    rate, base, rng_, gain = 1.0, 0.0, 1.0, 0.0; grp_rules = []
    if delivery and spk == "Jesus": rate *= 0.92; base -= 1; rng_ *= 1.1; grp_rules.append("I-JESUS")
    elif delivery and spk not in ("narrator", None): rate *= 1.03; base += 0.5; grp_rules.append("I-OTHER")
    for m in moods:
        if m == "I-GRIEF": rate *= 0.85; base -= 2; rng_ *= 0.7; gain -= 3
        if m == "I-CRY": rate *= 1.05; base += 2; gain += 4
        if m == "I-JOY": rate *= 1.03; base += 1; rng_ *= 1.2
        if m == "I-GLORY": rate *= 0.95; rng_ *= 1.1
        if m == "I-DEATH": rate *= 0.8; base -= 3; gain -= 4
        grp_rules.append(m)
    amen = delivery and any(w["raw"].lower().startswith("ἀμὴν") or nrm(w["raw"]) == "αμην" for w in words)
    if amen: rate *= 0.85; gain += 2; grp_rules.append("I-AMEN")
    ls = VC["base_length_scale"] / rate
    phs = [to_piper(w["sylls"]) for w in words]
    full = []
    for i, p in enumerate(phs): full += p + ([" "] if i < len(phs) - 1 else [])
    if end_punct in (".", "·"): full.append(".")
    elif end_punct == ";": full.append("?")
    elif end_punct == ",": full.append(",")
    a = voice.synth(full, ls); sr = voice.sr; dur = len(a) / sr
    ends = []
    for k in range(1, len(words)):
        pref = []
        for i in range(k): pref += phs[i] + [" "]
        ends.append(len(voice.synth(pref[:-1], ls)) / sr)
    ends.append(dur); ends = list(np.maximum.accumulate(np.minimum(ends, dur)))
    starts = [0.0] + ends[:-1]
    # pitch points
    pts = []; nsyl_total = sum(max(1, len(w["sylls"])) for w in words); si = 0
    for wi, w in enumerate(words):
        s0, s1 = starts[wi], ends[wi]; n = max(1, len(w["sylls"])); w["rules"] = list(dict.fromkeys(grp_rules + w.get("rules", [])))
        iam = delivery and nrm(w["raw"]) == "εγω" and wi + 1 < len(words) and nrm(words[wi + 1]["raw"]) == "ειμι"
        if iam: w["rules"].append("I-IAM")
        last_acc = max((j for j, s in enumerate(w["sylls"]) if s["accent"]), default=None) if wi == len(words) - 1 else None
        for j, s in enumerate(w["sylls"] or [dict(accent=None)]):
            t0 = s0 + (s1 - s0) * j / n; t1 = s0 + (s1 - s0) * (j + 1) / n; tm = (t0 + t1) / 2; frac = si / max(1, nsyl_total - 1); si += 1
            v = base - 2 * frac; rules = ["E-DECL"]
            acc = s.get("accent")
            if acc in ("acute", "circumflex") or (acc and acc != "grave"):
                v += 3 * rng_; rules.append("E-ACC")
            if iam: v += 1.5
            if wi == len(words) - 1 and j == n - 1:
                if end_punct in (".", "·"): v -= 4; rules.append("E-STOP")
                elif end_punct == ";": v += 4; rules.append("E-QUEST")
                elif end_punct == ",": v += 1.5; rules.append("E-COMMA")
            hz = VC["reciting_tone_hz"] * st(v)
            if acc == "circumflex" or (isinstance(acc, str) and "circ" in acc):
                pts += [(t0 + 0.25 * (t1 - t0), hz), (t0 + 0.8 * (t1 - t0), hz * st(-2.5))]
            else: pts.append((tm, hz))
            w.setdefault("pitch", []).append(round(hz, 1))
            for r in rules:
                if r not in w["rules"]: w["rules"].append(r)
        w["start"], w["end"] = s0, s1; w["gain_db"] = gain + (2 if iam or amen else 0)
    # Praat: formant shift to male tract, impose pitch tier, PSOLA resynthesis
    snd = parselmouth.Sound(a, sampling_frequency=sr)
    snd = call(snd, "Change gender", 75, 600, VC["formant_shift_ratio"], 0, 1, 1)
    man = call(snd, "To Manipulation", 0.01, 75, 600); pt = call("Create PitchTier", "p", 0, snd.duration)
    for t, hz in pts: call(pt, "Add point", min(max(t, 0.001), snd.duration - 0.001), hz)
    call([pt, man], "Replace pitch tier"); out = call(man, "Get resynthesis (overlap-add)").values[0]
    # loudness: per word gain + stress on accented syllables
    g = np.zeros(len(out))
    for w in words:
        a0, a1 = int(w["start"] * sr), int(w["end"] * sr); g[a0:a1] = w["gain_db"]
        n = max(1, len(w["sylls"]))
        for j, s in enumerate(w["sylls"]):
            if s.get("accent") and s["accent"] != "grave":
                b0 = int((w["start"] + (w["end"] - w["start"]) * j / n) * sr); b1 = int((w["start"] + (w["end"] - w["start"]) * (j + 1) / n) * sr); g[b0:b1] += 1.5
                if "E-STRESS" not in w["rules"]: w["rules"].append("E-STRESS")
    k = max(1, int(0.03 * sr)); g = np.convolve(g, np.ones(k) / k, mode="same"); out = out * (10 ** (g / 20))
    return out, end_punct, pts
def render_passage(voice, V, refs, delivery=True, space="synagogue", verse_gap=0.6):
    """refs: list of (chapter, verse). -> audio @ engine SR, timeline (words), meta."""
    sr = voice.sr; ratio = Fraction(E.SR, sr).limit_denominator(1000); chunks, words_out, t = [], [], 0.0; prev_spk = None
    for ref in refs:
        toks = V[ref]; moods = verse_moods(toks); groups, cur = [], []
        for tk in toks:
            cur.append(dict(raw=tk["raw"], sylls=word_ipa(tk["raw"]), spk=tk["spk"], moods=moods, ref=f"{ref[0]}:{ref[1]}", rules=[]))
            if re.search(r"[,.;·]$", tk["raw"]) or (len(cur) and cur[-1]["spk"] != tk["spk"]): groups.append(cur); cur = []
        if cur: groups.append(cur)
        # split groups at speaker changes
        gg = []
        for g_ in groups:
            part = [g_[0]]
            for w in g_[1:]:
                if w["spk"] != part[-1]["spk"]: gg.append(part); part = [w]
                else: part.append(w)
            gg.append(part)
        for gi, grp in enumerate(gg):
            if delivery and prev_spk is not None and grp[0]["spk"] != prev_spk:
                chunks.append(np.zeros(int(0.25 * E.SR))); t += 0.25; grp[0]["rules"].append("I-TURN")
            prev_spk = grp[0]["spk"]
            a, punct, pts = render_group(voice, grp, delivery)
            a = resample_poly(a, ratio.numerator, ratio.denominator)
            for w in grp:
                words_out.append(dict(ref=w["ref"], word=w["raw"], ipa=" ".join("".join(s["ph"]) for s in w["sylls"]), speaker=w["spk"], start=round(t + w["start"], 3), end=round(t + w["end"], 3),
                                      pitch_hz=w.get("pitch", []), gain_db=w["gain_db"], rules=w["rules"]))
            chunks.append(a); t += len(a) / E.SR
            pz = PAUSE.get(punct, 0.25) if gi < len(gg) - 1 else max(PAUSE.get(punct, 0.25), verse_gap)
            chunks.append(np.zeros(int(pz * E.SR))); t += pz
    y = np.concatenate(chunks); y = y / (np.abs(y).max() + 1e-9) * 0.9
    if space and space != "dry": y = E.reverb(y, space)
    return y, words_out
def measure_f0(y, sr, step=0.02):
    s = parselmouth.Sound(y, sampling_frequency=sr); p = s.to_pitch(time_step=step, pitch_floor=60, pitch_ceiling=300)
    return [(round(t, 3), round(float(f), 1)) for t, f in zip(p.xs(), p.selected_array["frequency"])]
