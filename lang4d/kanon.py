#!/usr/bin/env python3
"""KANON: a spoken-typed-played programming language. Reference implementation v0.1.

Layers per glyph (the 'tri-modal operator', made real):
  written ASCII glyph <-> spoken syllable <-> harmonic frequency <-> machine operation <-> drawn geometry.
Grounded in The-Sound's verified results:
  - 7 vowels = 7 planet-strings (Nicomachus ratios; rounds 41-50). iota = Sun = the mese/accumulator.
  - omega (Saturn) is the archive plane: Koine pronunciation leaves that string silent (round 45) -> write-mostly.
  - 12 consonants = the 4x3 breastpiece grid (Exod 28; round 62): the grid IS the keypad of the audio codec.
  - Verse execution order = ring composition: outer pairs first, the centre word commits last (rounds 52-54).
  - Celestial phase stamps: incommensurable planetary periods give unique multi-scale timestamps (round 39 engine).
Everything here is ordinary, honest computation: the codec is FSK-like, the VM is a small dataflow machine.
Usage: python3 lang4d/kanon.py selftest | run FILE.kn | speak FILE.kn OUT.wav | decode IN.wav | chart OUT.svg
"""
import json, math, os, sys, wave
import numpy as np

FS = 22050
F0 = 154.2                     # default carrier: the ark note (round 56); any f0 works (scale-invariant ratios)
VOWELS = "aeyiouw"             # alpha epsilon eta iota omicron upsilon omega
RATIO = {"a": 4/3, "e": 32/27, "y": 256/243, "i": 1.0, "o": 8/9, "u": 0.75*256/243, "w": 0.75}
PLANET = {"a": "Moon", "e": "Mercury", "y": "Venus", "i": "Sun", "o": "Mars", "u": "Jupiter", "w": "Saturn"}
CONS = "ktpbdglmnrsh"          # 4x3 grid, rows = manner families, cols = places
ROWMUL = [9.0, 11.0, 13.0, 15.0]    # consonant burst: row tone (x f0)
COLMUL = [17.0, 20.0, 23.0]         # consonant burst: col tone (x f0)
MARKMUL = 6.0                       # digit-shift marker tone (x f0)
DIGITS = "0123456789te"             # base-12 digits, same 4x3 grid as the consonants
OPNAME = {"k": "commit", "t": "test", "p": "project", "b": "bind", "d": "door", "g": "gather",
          "l": "loop", "m": "morph", "n": "negate", "r": "retro", "s": "stream", "h": "breath"}

# ---------------------------------------------------------------- parsing
def parse(src):
    """-> list of verses; verse = list of items dict(word, num, urgent, sandbox)."""
    verses = []
    for vtext in src.replace("\n", " ").split("|"):
        items, toks = [], vtext.split()
        for tk in toks:
            urgent = tk.endswith("!"); tk = tk.rstrip("!")
            sandbox = tk.startswith("~"); tk = tk.lstrip("~")
            if not tk: continue
            if tk.startswith("#"):
                v = 0
                for ch in tk[1:]: v = v*12 + DIGITS.index(ch)
                if items: items[-1]["num"] = float(v)
                else: items.append(dict(word="ki", num=float(v), urgent=False, sandbox=False))
                continue
            ok = len(tk) >= 2 and all((c in CONS if j % 2 == 0 else c in VOWELS) for j, c in enumerate(tk[:len(tk)//2*2]))
            if len(tk) % 2 == 1 and tk[-1] not in VOWELS: ok = False
            if not ok: raise SyntaxError(f"bad word {tk!r}: syllables are consonant+vowel, optional final vowel")
            items.append(dict(word=tk, num=None, urgent=urgent, sandbox=sandbox))
        if items: verses.append(items)
    return verses

def schedule(items):
    """Ring order (rounds 52-54): urgent words first, then outer pairs inward, the centre commits last."""
    out, rest = [], []
    for it in items: (out if it["urgent"] else rest).append(it)
    n = len(rest)
    for k in range(n // 2): out += [rest[k], rest[n-1-k]]
    if n % 2: out.append(rest[n//2])
    return out

def expand_loops(items):
    out, i = [], 0
    while i < len(items):
        it = items[i]
        if it["word"][0] == "l" and i + 1 < len(items):
            out += [items[i+1]] * int(it["num"] or 2); i += 2
        else: out.append(it); i += 1
    return out

# ---------------------------------------------------------------- the machine
def fold(x):
    x = abs(float(x)) or 1.0
    while x >= 2.5: x /= 2
    while x < 0.625: x *= 2
    return x

class VM:
    def __init__(self):
        self.plane = {v: [] for v in VOWELS}
        self.events = []            # (kind, payload) audio/events stream
        self.log = []
    def run(self, src):
        for items in parse(src):
            for it in schedule(expand_loops(items)):
                try: self.word(it)
                except Exception as e:
                    if it["sandbox"]: self.log.append(f"~{it['word']}: skipped ({e})")
                    else: raise
        return self
    def word(self, it):
        w, val = it["word"], it["num"]
        op, head = w[0], w[1]
        cad = w[-1] if len(w) % 2 == 1 else None
        P = self.plane
        if op == "s": P[head] = [float(k) for k in range(1, int(val or 7) + 1)]
        elif op == "k": P[head] = [float(val if val is not None else 1.0)]
        elif op == "b": P[head] = list(P[cad or "i"])
        elif op == "p": P[head] = [x * RATIO[cad or "i"] for x in P[head]]
        elif op == "g": P[head] = [float(sum(P[cad] if cad else P[head]))]
        elif op == "t":
            thr = val if val is not None else (sum(P[head]) / len(P[head]) if P[head] else 0.0)
            P[head] = [x for x in P[head] if x > thr]
        elif op == "n": P[head] = [-x for x in P[head]]
        elif op == "r": P[head] = P[head][::-1]
        elif op == "m":
            tgt, n = RATIO[cad or "i"], max(1, len(P[head]))
            P[head] = [x * tgt ** ((j + 1) / n) for j, x in enumerate(P[head])]
        elif op == "d":
            if len(w) >= 4:   # the word's own vowel line is the melody (e.g. 'demorini' = e o i i, the I AM line)
                self.events.append(("melody", [RATIO[c] for c in w if c in VOWELS]))
            else:
                self.events.append(("melody", [fold(x) for x in P[head]]))
        elif op == "h": self.events.append(("rest", (val or 2) * 0.1))
        elif op == "l": pass
        self.log.append(f"{w}{'' if val is None else ' #'+format(int(val),'d')} -> {OPNAME[op]} {head}={[round(x,3) for x in P[head]][:8]}")

# ---------------------------------------------------------------- audio codec (speakable code)
def _tone(freqs, dur, amp=0.8):
    t = np.arange(int(dur * FS)) / FS
    y = sum(np.sin(2 * np.pi * f * t) for f in freqs)
    e = np.minimum(1, t / 0.008) * np.minimum(1, (dur - t) / 0.015)
    return amp * y / max(1, len(freqs)) * e

def _vowel(v, dur=0.18, f0=F0):
    f = RATIO[v] * f0
    t = np.arange(int(dur * FS)) / FS
    y = np.sin(2*np.pi*f*t) + 0.45*np.sin(2*np.pi*2*f*t) + 0.2*np.sin(2*np.pi*3*f*t)
    e = np.minimum(1, t / 0.012) * np.minimum(1, (dur - t) / 0.025)
    return 0.8 * y / 1.65 * e

def encode(src, f0=F0):
    GAP_S, GAP_W, GAP_V = 0.045, 0.22, 0.55
    out = [np.zeros(int(0.08 * FS))]
    for vtext in src.replace("\n", " ").split("|"):
        for tk in vtext.split():
            tk = tk.rstrip("!").lstrip("~")
            if not tk: continue
            if tk.startswith("#"):
                for ch in tk[1:]:
                    i = DIGITS.index(ch); r, c = i // 3, i % 3
                    out += [_tone([ROWMUL[r]*f0, COLMUL[c]*f0, MARKMUL*f0], 0.07), _vowel("i", 0.12, f0), np.zeros(int(GAP_S*FS))]
            else:
                for j in range(0, len(tk) - len(tk) % 2, 2):
                    i = CONS.index(tk[j]); r, c = i // 3, i % 3
                    out += [_tone([ROWMUL[r]*f0, COLMUL[c]*f0], 0.07), _vowel(tk[j+1], 0.18, f0), np.zeros(int(GAP_S*FS))]
                if len(tk) % 2: out += [_vowel(tk[-1], 0.18, f0), np.zeros(int(GAP_S*FS))]
            out.append(np.zeros(int((GAP_W - GAP_S) * FS)))
        out.append(np.zeros(int((GAP_V - GAP_W) * FS)))
    y = np.concatenate(out)
    return y / (np.abs(y).max() + 1e-9) * 0.9

def _peak(mag, freqs, lo, hi):
    band = (freqs >= lo) & (freqs <= hi)
    if not band.any(): return 0.0, 0.0
    i = np.argmax(mag * band)
    if 0 < i < len(mag) - 1:
        a, b, c = mag[i-1], mag[i], mag[i+1]
        d = 0.5 * (a - c) / (a - 2*b + c + 1e-12)
        return freqs[i] + d * (freqs[1] - freqs[0]), mag[i]
    return freqs[i], mag[i]

def decode(y, f0=F0):
    env = np.convolve(np.abs(y), np.ones(220) / 220, mode="same")
    thr = 1.8 * np.percentile(env, 25) + 0.015 * env.max()   # noise-floor-aware gate
    on = env > thr
    edges = np.flatnonzero(np.diff(on.astype(int))); segs = []
    starts = list(edges[::2] if on[0] == 0 else np.r_[0, edges[1::2]])
    ends = list(edges[1::2] if on[0] == 0 else edges[0::2])
    raw = [(a, b) for a, b in zip(starts, ends) if b - a > int(0.035 * FS)]
    for a, b in raw:                                   # merge fragments split by noise dips
        if segs and a - segs[-1][1] < int(0.03 * FS): segs[-1] = (segs[-1][0], b)
        else: segs.append((a, b))
    toks, prev_end, num_mode = [], None, False
    for a, b in segs:
        gap = (a - prev_end) / FS if prev_end is not None else 0.0
        if prev_end is not None:
            if gap > 0.4: toks.append(" | "); num_mode = False
            elif gap > 0.12: toks.append(" "); num_mode = False
        prev_end = b
        seg = y[a:b]
        nb = min(len(seg), int(0.06 * FS))
        burst = seg[:nb] * np.hanning(nb)
        spec = np.abs(np.fft.rfft(burst, 1 << 14)); fr = np.fft.rfftfreq(1 << 14, 1 / FS)
        def best(mults):
            es = [_peak(spec, fr, m*f0*0.95, m*f0*1.05)[1] for m in mults]
            return int(np.argmax(es)), max(es)
        r, er = best(ROWMUL); c, ec = best(COLMUL)
        mk = _peak(spec, fr, MARKMUL*f0*0.93, MARKMUL*f0*1.07)[1]
        has_burst = max(er, ec) > 0.12 * spec.max()
        vpart = seg[nb:] if has_burst else seg
        vowel = None
        if len(vpart) > (int(0.05 * FS) if has_burst else int(0.09 * FS)):
            vs = np.abs(np.fft.rfft(vpart * np.hanning(len(vpart)), 1 << 15)); vf = np.fft.rfftfreq(1 << 15, 1/FS)
            fpk, _ = _peak(vs, vf, f0 * 0.70, f0 * 1.40)
            vowel = min(VOWELS, key=lambda v: abs(math.log(fpk / (RATIO[v] * f0))))
        if has_burst and mk > 0.5 * max(er, ec):
            if not num_mode: toks.append("#"); num_mode = True
            toks.append(DIGITS[r * 3 + c])
        else:
            if num_mode: num_mode = False
            if has_burst: toks.append(CONS[r * 3 + c] + (vowel or "i"))
            elif vowel and toks and toks[-1] and toks[-1][-1] in VOWELS + "| #" and len(vpart) > int(0.12 * FS): toks.append(vowel)
            elif vowel and toks and toks[-1] and toks[-1][-1] in CONS: toks.append(vowel)
    return " ".join("".join(toks).split())

def norm_text(src):
    return " ".join(" | ".join(p.strip() for p in src.replace("\n", " ").split("|")).split()).replace("~", "").replace("!", "")

# ---------------------------------------------------------------- celestial phase stamp (round-39 style)
EPH = {"Sun": (280.466, 0.98564736), "Moon": (218.316, 13.176396), "Mercury": (252.251, 4.09233445),
       "Venus": (181.980, 1.60213034), "Mars": (355.433, 0.52402068), "Jupiter": (34.351, 0.08308529),
       "Saturn": (50.077, 0.03349791)}
def phase_stamp(jd):
    d = jd - 2451545.0
    return {p: round((L0 + n * d) % 360.0, 4) for p, (L0, n) in EPH.items()}

# ---------------------------------------------------------------- rendering
def render_events(events, f0=F0):
    out = []
    for kind, pay in events:
        if kind == "rest": out.append(np.zeros(int(pay * FS)))
        else:
            for r in pay:
                fr = fold(r) * f0
                t = np.arange(int(0.35 * FS)) / FS
                y = sum(np.sin(2*np.pi*fr*k*t) * abs(math.sin(k*math.pi*0.2)) / k * np.exp(-t*(1.0+0.4*k)) for k in range(1, 12))
                out += [y, np.zeros(int(0.06 * FS))]
    if not out: return np.zeros(FS // 4)
    y = np.concatenate(out); return y / (np.abs(y).max() + 1e-9) * 0.85

def save_wav(path, y):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(FS)
        f.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())

def glyph_chart(path):
    W, H = 980, 730
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif">',
         f'<rect width="{W}" height="{H}" fill="#f7f4ec"/>',
         '<text x="24" y="40" font-size="26" font-weight="bold" fill="#222">KANON glyphs: one lattice, four readings</text>',
         '<text x="24" y="62" font-size="13" fill="#666">speak it, type it, play it, run it - vowels are the seven planet-strings, consonants the 4x3 breastpiece grid</text>']
    s.append('<text x="24" y="100" font-size="16" font-weight="bold" fill="#333">7 vowels = strings (data planes)</text>')
    x0, y0 = 40, 120
    for j, v in enumerate("aeyiou w".replace(" ", "")):
        r = RATIO[v]; ypos = y0 + j * 46; ln = 420 / r * 0.75
        hot = v == "i"
        s.append(f'<line x1="{x0}" y1="{ypos}" x2="{x0+ln:.0f}" y2="{ypos}" stroke="{"#b8860b" if hot else "#555"}" stroke-width="{4 if hot else 2.5}"/>')
        s.append(f'<circle cx="{x0+ln:.0f}" cy="{ypos}" r="5" fill="{"#b8860b" if hot else "#777"}"/>')
        frac = {"a":"4:3","e":"32:27","y":"256:243","i":"1:1 (mese)","o":"8:9","u":"64:81","w":"3:4"}[v]
        s.append(f'<text x="{x0+440}" y="{ypos+5}" font-size="14" fill="#222"><tspan font-weight="bold">{v}</tspan>  {PLANET[v]}  {frac}  {RATIO[v]*F0:.1f} Hz  - {PLANE_ROLE[v]}</text>')
    s.append('<text x="24" y="470" font-size="16" font-weight="bold" fill="#333">12 consonants = operations (the 4x3 grid is also the audio keypad)</text>')
    gx, gy, cw, ch = 40, 490, 150, 44
    for i, cch in enumerate(CONS):
        r, c = i // 3, i % 3; x, yy = gx + c * cw, gy + r * ch
        s.append(f'<rect x="{x}" y="{yy}" width="{cw-8}" height="{ch-8}" rx="7" fill="#fff" stroke="#999"/>')
        s.append(f'<text x="{x+10}" y="{yy+24}" font-size="15" fill="#222"><tspan font-weight="bold">{cch}</tspan> {OPNAME[cch]}</text>')
    for r in range(4): s.append(f'<text x="{gx+3*cw+4}" y="{gy+r*ch+24}" font-size="12" fill="#888">row tone x{ROWMUL[r]:.0f}</text>')
    for c in range(3): s.append(f'<text x="{gx+c*cw+10}" y="{gy+4*ch+12}" font-size="12" fill="#888">col x{COLMUL[c]:.0f}</text>')
    s.append(f'<text x="560" y="500" font-size="15" font-weight="bold" fill="#333">a word is a melody</text>')
    s.append('<text x="560" y="522" font-size="13" fill="#444">demorini = d(e,o,i,i): "speak: Mercury-Mars-Sun-Sun"</text>')
    s.append('<text x="560" y="540" font-size="13" fill="#444">- the vowel line of EGO EIMI (rounds 44-59)</text>')
    s.append('<text x="560" y="575" font-size="13" fill="#444">verse order: outer pairs first, the centre word commits last</text>')
    s.append('<text x="560" y="593" font-size="13" fill="#444">(ring composition: the mese governs - rounds 52-54)</text>')
    s.append(f'<text x="560" y="628" font-size="13" fill="#444">digits #0-#e: same grid + marker tone x{MARKMUL:.0f} (base 12)</text>')
    s.append('<text x="560" y="646" font-size="13" fill="#444">carrier f0 free; default 154.2 Hz, the ark note (round 56)</text>')
    s.append(f'<text x="24" y="{H-16}" font-size="11" fill="#999">The Sound - KANON v0.1. All claims computable; see WHITEPAPER.md honest-claims table.</text></svg>')
    open(path, "w").write("\n".join(s))

PLANE_ROLE = {"i": "accumulator (the mese)", "a": "input stream", "e": "fast scratch", "y": "pair register",
              "o": "output stage", "u": "deep store", "w": "archive (the silent string)"}

# ---------------------------------------------------------------- self-test
def selftest():
    out = {}
    p1 = "sa #7 gia ta #3 | di"
    vm = VM().run(p1)
    out["program1"] = dict(src=p1, iota=vm.plane["i"], alpha=vm.plane["a"],
        note="ring order: s and t (outer pair) run first, centre g commits: sum(4..7)=22; linear order would give 28")
    assert vm.plane["i"] == [22.0], vm.plane
    vm2 = VM().run("sa #7 ta #3 gia | di")   # same words, different positions -> different meaning
    out["program1_reordered"] = dict(iota=vm2.plane["i"], note="now g is outer, t is centre: gather runs before filter")
    p3 = "ka #4 demorini | sa #5 pia ria | ha #3 da"
    vm3 = VM().run(p3); out["program3_events"] = [[k, [round(x,3) for x in v] if isinstance(v, list) else v] for k, v in vm3.events]
    clean = encode(p1); dec = decode(clean)
    out["codec_clean"] = dict(encoded_seconds=round(len(clean)/FS, 2), decoded=dec, exact=dec == norm_text(p1))
    assert dec == norm_text(p1), (dec, norm_text(p1))
    rng = np.random.default_rng(64)
    results = {}
    for snr in (25.0, 15.0, 8.0):
        sig = clean.std(); noisy = clean + rng.standard_normal(len(clean)) * sig / (10 ** (snr/20))
        d = decode(noisy); ok = d == norm_text(p1)
        a = norm_text(p1).replace(" ", ""); b = d.replace(" ", "")
        acc = sum(x == yy for x, yy in zip(a, b)) / max(len(a), len(b))
        results[f"{snr:.0f} dB SNR"] = dict(exact=ok, char_accuracy=round(acc, 3))
    out["codec_noise"] = results
    big = encode("demorini | sa #7 gia ta #3 | lu #3 pia | ka #e bwi da")
    out["codec_long"] = dict(decoded=decode(big), exact=decode(big) == norm_text("demorini | sa #7 gia ta #3 | lu #3 pia | ka #e bwi da"))
    per_syl = 12 * 7
    words = sum(per_syl ** s * (1 + 7) for s in range(1, 5))
    out["namespace"] = dict(per_syllable=per_syl, words_up_to_4_syllables=words,
        with_3_verse_roles=words * 3, note="each word also means differently as head/pair/centre of its verse (ring grammar)")
    out["phase_stamp_J2000+9800d"] = phase_stamp(2451545.0 + 9800)
    out["constants"] = dict(f0_default=F0, ratios={v: round(RATIO[v], 5) for v in VOWELS})
    return out

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    here = os.path.dirname(os.path.abspath(__file__))
    if cmd == "selftest":
        out = selftest()
        json.dump(out, open(os.path.join(here, "selftest_results.json"), "w"), indent=1)
        print(json.dumps(out, indent=1))
        glyph_chart(os.path.join(here, "glyph_chart.svg"))
    elif cmd == "run":
        vm = VM().run(open(sys.argv[2]).read())
        print("\n".join(vm.log)); print("events:", vm.events)
    elif cmd == "speak":
        src = open(sys.argv[2]).read()
        vm = VM().run(src)
        y = np.concatenate([encode(src), np.zeros(FS), render_events(vm.events)])
        save_wav(sys.argv[3], y); print("wrote", sys.argv[3], f"{len(y)/FS:.1f}s  (spoken code, silence, then the program's own output)")
    elif cmd == "decode":
        with wave.open(sys.argv[2]) as f:
            y = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(float) / 32767
        print(decode(y))
    elif cmd == "chart": glyph_chart(sys.argv[2]); print("wrote", sys.argv[2])

if __name__ == "__main__": main()
