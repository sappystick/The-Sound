#!/usr/bin/env python3
"""Two open follow-ups.
F1 'Life at book centres' (round 22, p 0.001 at the permutation floor): exact p-value. For each Hebrew book, the share
   of all 5-verse windows containing 'life' (chayyim) is the chance its centre window does; the number of books hit
   then follows a Poisson-binomial distribution, computed exactly. Same for the other seven motifs of round 22.
F2 The PGM XIII vowel square: render the seven directions (each a rising triangle, 1..7 repetitions, starting on a
   different vowel) on one held 110 Hz note, and measure which overtone each vowel brightens.
Usage: python3 followups.py <wlc dir>"""
import glob, json, os, re, subprocess, sys, unicodedata
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); WLC = sys.argv[1]; out = {}
def cons(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת").translate(str.maketrans("ךםןףץ", "כמנפצ"))
BK = {}
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    x = open(f, encoding="utf-8").read(); vs = []
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S):
        ws = [cons(p) for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2)) for p in w.split("/")]; vs.append([w for w in ws if w])
    if len(vs) > 20: BK[os.path.basename(f)[:-4]] = vs
MOT = {"life": lambda ws: "חיימ" in ws, "water": lambda ws: "מימ" in ws, "light": lambda ws: "אור" in ws, "heaven and earth": lambda ws: "שמימ" in ws and "ארצ" in ws,
       "tree": lambda ws: "עצ" in ws, "gate": lambda ws: "שער" in ws, "house of YHWH / temple": lambda ws: "היכל" in ws or any(a == "בית" and b == "יהוה" for a, b in zip(ws, ws[1:])),
       "name of YHWH": lambda ws: any(a == "שמ" and b == "יהוה" for a, b in zip(ws, ws[1:]))}
def centre(vs):
    L = [sum(len(w) for w in ws) for ws in vs]; T = sum(L); acc = 0
    for i, l in enumerate(L):
        if acc + l > T / 2: return i
        acc += l
F1 = {}
print("F1. Motifs at the letter-centres of the Hebrew books: exact p-values")
for lab, f in MOT.items():
    ps, hit, books = [], 0, []
    for name, vs in BK.items():
        win = [f([w for ws in vs[i - 2: i + 3] for w in ws]) for i in range(2, len(vs) - 2)]; ps.append(np.mean(win))
        c = centre(vs); h = f([w for ws in vs[max(0, c - 2): c + 3] for w in ws]); hit += h
        if h: books.append(name)
    dist = np.zeros(len(ps) + 1); dist[0] = 1
    for q in ps: dist = np.concatenate([dist[:1] * (1 - q), dist[1:] * (1 - q) + dist[:-1] * q])
    p = float(dist[hit:].sum()); F1[lab] = dict(hit=hit, expected=round(float(sum(ps)), 2), p=p, books=books)
    print(f"   {lab:24s} {hit} of {len(BK)} centres (expected {sum(ps):.2f})  exact p = {p:.5f}  {books}")
pv = sorted((v["p"], k) for k, v in F1.items()); m = len(pv)
for i, (p, k) in enumerate(pv): F1[k]["survives_holm"] = bool(p <= 0.05 / (m - i))
print("   Holm-corrected over 8 motifs:", {k: v["survives_holm"] for k, v in F1.items()})
out["F1"] = F1
# ---------------------------------------------------------------- F2
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
SR = E.SR; V7 = ["a", "e", "ɛ", "i", "o", "y", "ɔ"]; G7 = "αεηιουω"; FMT = dict(E.VOWELS); FMT["y"] = (270, 1700, 2150)
DIRS = [("dawn", 0), ("south", 3), ("west", 2), ("north", 6), ("earth", 1), ("sky", 5), ("cosmos", 4)]
F0, UNIT = 110.0, 0.32; tracks = [[], [], []]; plan = []
for d, s in DIRS:
    seq = [V7[(s + k) % 7] for k in range(7) for _ in range(k + 1)]; plan.append((d, "".join(G7[(s + k) % 7] * (k + 1) for k in range(7))))
    for v in seq:
        for j in range(3): tracks[j] += [FMT[v][j]] * int(UNIT * SR)
    for j in range(3): tracks[j] += [tracks[j][-1]] * int(0.6 * SR)
y = E.formant_filter(E.glottal_source(np.full(len(tracks[0]), F0), vib=0.0, jitter=0.0), *[np.array(t) for t in tracks]); y = y / np.abs(y).max()
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True); w = os.path.join(HERE, "audio", "e7_vowel_square.wav"); yr = E.reverb(y, "temple")
wavfile.write(w, SR, (yr / np.abs(yr).max() * 0.9 * 32767).astype(np.int16)); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-b:a", "128k", w[:-4] + ".mp3"], check=True); os.remove(w)
# overtone melody per direction: strongest upper harmonic of each vowel (away from F1)
def upper(v):
    a = 0; seg = None
    t = np.arange(int(0.5 * SR)) / SR; src = E.glottal_source(np.full(len(t), F0), vib=0.0, jitter=0.0); s = E.formant_filter(src, *[np.full(len(t), FMT[v][j]) for j in range(3)])
    sp = np.abs(np.fft.rfft(s[int(0.1 * SR):] * np.hanning(len(s) - int(0.1 * SR)), 1 << 17)); fr = np.fft.rfftfreq(1 << 17, 1 / SR)
    band = {h: sp[np.argmin(np.abs(fr - h * F0))] for h in range(2, 30) if 500 <= h * F0 <= 2700 and abs(h * F0 - FMT[v][0]) > 150}; return max(band, key=band.get)
H = {v: upper(v) for v in V7}
out["F2"] = dict(f0=F0, directions=[dict(direction=d, sequence=p, start=p[0], overtones=[H[V7[(s + k) % 7]] for k in range(7)]) for (d, s), (_, p) in zip(DIRS, plan)], duration_s=round(len(yr) / SR, 1),
                 complete_square=len({s for _, s in DIRS}) == 7)
print("\nF2. Vowel square rendered:", out["F2"]["duration_s"], "s; all seven starting vowels used:", out["F2"]["complete_square"])
for r in out["F2"]["directions"]: print(f"   {r['direction']:7s} starts {r['start']}: overtone melody (harmonic numbers) {r['overtones']}")
json.dump(out, open(os.path.join(HERE, "followups_results.json"), "w"), ensure_ascii=False, indent=1)
