#!/usr/bin/env python3
"""Render the whole Gospel of John as a spoken reconstruction with a data-dense video track.

AUDIO: every verse of SBLGNT John is synthesised by the project engine (code/engine/engine.py): Koine pronunciation
(c. 1st century; round 9 settings), 'declaim' delivery (public reading), synagogue room acoustics (RT60 1.4 s, modal
model).  Between verses: 0.6 s.  Before the self-found section breaks (model/john_model_config.json, round 30/31):
major 3.0 s, minor 2.0 s.  The engine is a formant synthesiser: it renders the phonology, stress, pitch and room, not a
human voice.  Nothing is invented beyond the configuration recorded in video/out/render_manifest.json.

VIDEO (1280x720, one frame per verse, held for the verse's real audio duration):
  the whole book as a track (self-found sections, theme blocks, marker lanes, playhead);
  the Greek of the verse (SBLGNT), its IPA as rendered, the KJV (public domain) for orientation;
  a data panel: section, theme block, voice mode (discourse - action), noise share, syllables, breath groups,
  historic presents, body/motion words, markers (with what they are), and the two most similar distant verses
  (recurrence, round 27).
Outputs: video/out/john_ch01.mp4 ... john_ch21.mp4, video/out/john_full.mp4, video/out/john_timeline.json
Usage: python3 render_john_video.py <sblgnt dir> <kjv csv> <work dir>
"""
import collections, csv, glob, json, math, os, re, subprocess, sys, unicodedata, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
SBL, KJV, WORK = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True); WAV = os.path.join(WORK, "wav"); FR = os.path.join(WORK, "frames"); os.makedirs(WAV, exist_ok=True); os.makedirs(FR, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
CFG = json.load(open(os.path.join(ROOT, "model", "john_model_config.json"), encoding="utf-8"))
SUMM = json.load(open(os.path.join(ROOT, "model", "out", "john_summary.json"), encoding="utf-8"))
BREAKS = {tuple(int(x) for x in k.split(":")): v for k, v in SUMM["section_pauses"]["breaks"].items()}
SP = CFG["tempo"]["section_pauses"]; GAP = 0.6; ERA, MODE, SPACE = "koine", "declaim", "synagogue"
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
# ---------------- text and per-verse data
V = collections.OrderedDict()
for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"):
    p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], lem=nrm(p[6]), pos=p[1], parse=p[2]))
keys = list(V); n = len(keys); idx = {k: i for i, k in enumerate(keys)}
kjv = {(int(r["Chapter"]), int(r["Verse"])): r["Text"] for r in csv.DictReader(open(KJV, encoding="utf-8")) if r["Book"] == "John"}
vrow = {r["verse"]: r for r in csv.DictReader(open(os.path.join(ROOT, "model", "out", "john_verses.csv"), encoding="utf-8"))}
mv = {d["v"]: d for d in json.load(open(os.path.join(ROOT, "code", "analysis", "movement_path.json")))}
HPV = {"λεγω", "ερχομαι", "βλεπω", "ευρισκω", "λαμβανω", "ακολουθεω", "τρεχω", "φωνεω", "αγω", "φερω", "εισερχομαι", "εξερχομαι", "θεωρεω", "παραλαμβανω", "εγειρω", "αποστελλω", "πεμπω", "μαρτυρεω", "κραζω", "κραυγαζω"}
d_, a_ = [], []
for v in V.values():
    m = len(v); sp = any(u["pos"][0] == "V" and u["parse"][0] in "12" for u in v)
    d_.append(sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in v) / m)
    a_.append(sum(t["pos"][0] == "V" and t["parse"][0] == "3" and t["parse"][3] == "I" and t["parse"][1] in "AIP" and not sp for t in v) / m)
d_, a_ = np.array(d_), np.array(a_); MODEV = (d_ - d_.mean()) / d_.std() - (a_ - a_.mean()) / a_.std()
MODES_ = np.convolve(np.pad(MODEV, 3, mode="edge"), np.ones(7) / 7, mode="valid")
STOP = set("ο και αυτος δε εν ειμι λεγω ου μη γαρ ουν οτι εγω συ ουτος εκεινος τις ινα προς εκ εις απο επι δια μετα περι αλλα ως καθως ημεις υμεις εαν αν οστις παρα υπο ηδη ετι ουδε τε η ποιεω εχω γινομαι ερχομαι".split())
docs = [[t["lem"] for t in V[k] if t["pos"][0] in "NVA" and t["lem"] not in STOP] for k in keys]
df = collections.Counter(l for x in docs for l in set(x)); voc = {l: i for i, l in enumerate(df)}; X = np.zeros((n, len(voc)))
for i, x in enumerate(docs):
    for l in x: X[i, voc[l]] += math.log(n / df[l])
Xn = X / np.maximum(1e-9, np.linalg.norm(X, axis=1, keepdims=True)); SIM = Xn @ Xn.T
MARKNAME = {"i_am_ring": "“I am the …” ring", "i_am_images": "“I am” image", "prologue_centre": "prologue centre (1:12)", "seams": "seam",
            "schism_chain": "torn / not torn (schizō)", "vertical_axis": "ascend / descend axis", "high_priest": "high-priest thread", "living_water": "living water"}
# section names (distinctive words of each self-found section)
starts = [0] + sorted(idx[k] for k in BREAKS if k in idx) + [n]
inv = {v: k for k, v in voc.items()}; Xc = (X > 0).astype(float); SECNAME = {}
for s in range(len(starts) - 1):
    i, j = starts[s], starts[s + 1]; sub = Xc[i:j].sum(0); rest = Xc.sum(0) - sub
    z = np.log(((sub + .5) / (sub.sum() + .5 * len(voc))) / ((rest + .5) / (rest.sum() + .5 * len(voc)))) * np.sqrt(sub)
    for q in range(i, j): SECNAME[q] = (s + 1, f"{keys[i][0]}:{keys[i][1]}–{keys[j - 1][0]}:{keys[j - 1][1]}", ", ".join(inv[w] for w in np.argsort(-z)[:4]))
# ---------------- audio
manifest = dict(engine="code/engine/engine.py make()", era=ERA, mode=MODE, space=SPACE, verse_gap_s=GAP, section_pause_major_s=SP["major_seconds"],
                section_pause_minor_s=SP["minor_seconds"], breaks={f"{c}:{v}": k for (c, v), k in BREAKS.items()}, text="SBLGNT (MorphGNT)", sample_rate=E.SR)
timeline = []; t = 0.0
def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()
for k in keys:
    p = os.path.join(WAV, f"{k[0]:02d}_{k[1]:03d}.wav")
    if not os.path.exists(p):
        txt = " ".join(t_["raw"] for t_ in V[k]); meta = E.make(txt, "greek", ERA, MODE, "none", p, space=SPACE)
    meta = json.load(open(p[:-4] + ".json", encoding="utf-8")); pre = SP["major_seconds"] if BREAKS.get(k) == "major" else SP["minor_seconds"] if BREAKS.get(k) == "minor" else 0.0
    dur = wav_len(p); timeline.append(dict(v=f"{k[0]}:{k[1]}", pre=pre, start=round(t + pre, 3), dur=round(dur, 3), ipa=meta.get("ipa", ""))); t += pre + dur + GAP
    if len(timeline) % 100 == 0: print("audio", len(timeline), round(t / 60, 1), "min", flush=True)
json.dump(dict(manifest=manifest, total_s=round(t, 2), verses=timeline), open(os.path.join(OUT, "john_timeline.json"), "w"), ensure_ascii=False, indent=0)
print("audio total", round(t / 60, 1), "min", flush=True)
# ---------------- frames
W, H = 1280, 720
F = lambda s, b=False: ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVu{'Serif' if not b else 'Sans'}{'-Bold' if b == 2 else ''}.ttf", s)
SANS = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s); SANSB = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
SERIF = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", s); MONO = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", s)
BG, INK, MUTED, LINE = (18, 20, 26), (236, 232, 222), (150, 146, 138), (52, 55, 64)
GOLD, LAPIS, ROSE, LEAF, VIOLET, WATER, OCHRE = (214, 170, 86), (92, 140, 220), (222, 98, 120), (110, 186, 120), (170, 130, 220), (90, 190, 210), (200, 140, 70)
MCOL = {"i_am_ring": VIOLET, "prologue_centre": LAPIS, "schism_chain": ROSE, "vertical_axis": LEAF, "high_priest": OCHRE, "living_water": WATER, "seams": MUTED}
BLOCKS = [("water", (2, 1), (4, 42)), ("bread & life", (6, 1), (6, 71)), ("light", (8, 12), (9, 41)), ("hour & glory", (12, 20), (13, 32)), ("abide & love", (14, 1), (17, 26))]
cum = np.array([x["start"] for x in timeline]); TOT = t
def X_(i): return 40 + (W - 80) * cum[i] / TOT
base = Image.new("RGB", (W, H), BG); bd = ImageDraw.Draw(base)
bd.text((40, 14), "THE GOSPEL OF JOHN · a spoken reconstruction", font=SANSB(15), fill=GOLD)
bd.text((W - 40, 14), "Koine · declaimed · synagogue (RT60 1.4 s) · engine synthesis", font=SANS(13), fill=MUTED, anchor="ra")
y0 = 44
for nm, a, b in BLOCKS:
    if a in idx and b in idx: bd.rectangle([X_(idx[a]), y0, X_(idx[b]), y0 + 70], fill=(34, 36, 44)); bd.text((X_(idx[a]) + 3, y0 + 2), nm, font=SANS(10), fill=MUTED)
xs = [X_(i) for i in range(n)]
for i in range(1, n):     # mode trace
    yA = y0 + 50 - 14 * np.clip(MODES_[i - 1], -1.5, 1.5); yB = y0 + 50 - 14 * np.clip(MODES_[i], -1.5, 1.5)
    bd.line([(xs[i - 1], yA), (xs[i], yB)], fill=GOLD if MODES_[i] > 0 else (120, 120, 130), width=1)
for k, kind in BREAKS.items():
    if k in idx: x = X_(idx[k]); bd.line([(x, y0 - 2), (x, y0 + 72)], fill=INK if kind == "major" else (90, 92, 100), width=2 if kind == "major" else 1)
lane = 0
for mk, col in MCOL.items():
    for k in keys:
        if mk in vrow.get(f"{k[0]}:{k[1]}", {}).get("markers", ""): x = X_(idx[k]); bd.line([(x, y0 + 74 + lane * 4), (x, y0 + 77 + lane * 4)], fill=col, width=2)
    lane += 1
for c in range(1, 22):
    i = idx[(c, 1)]; bd.text((X_(i), y0 + 104), str(c), font=SANS(10), fill=MUTED)
bd.text((40, y0 + 118), "track: theme blocks (shaded) · voice mode (gold = discourse, grey = action) · section breaks (white = major) · marker lanes", font=SANS(10), fill=(110, 108, 104))
bd.line([(40, 182), (W - 40, 182)], fill=LINE)
def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        tt = (cur + " " + w).strip()
        if draw.textlength(tt, font=font) <= width: cur = tt
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def fit(draw, text, maker, width, height, start, minsize, lead=1.3):
    s = start
    while s >= minsize:
        f = maker(s); L = wrap(draw, text, f, width)
        if len(L) * s * lead <= height: return f, L, s
        s -= 2
    f = maker(minsize); return f, wrap(draw, text, f, width), minsize
def frame(i):
    k = keys[i]; vs = f"{k[0]}:{k[1]}"; im = base.copy(); d = ImageDraw.Draw(im); x = X_(i)
    d.polygon([(x - 6, y0 - 8), (x + 6, y0 - 8), (x, y0)], fill=INK); d.line([(x, y0), (x, y0 + 100)], fill=INK, width=1)
    d.text((40, 196), vs, font=SANSB(34), fill=INK)
    sn = SECNAME[i]; d.text((40, 240), f"section {sn[0]} · {sn[1]}", font=SANS(13), fill=GOLD); d.text((40, 258), sn[2], font=SERIF(14), fill=MUTED)
    greek = " ".join(t_["raw"] for t_ in V[k]); f, L, s = fit(d, greek, SERIF, 780, 250, 34, 16)
    yy = 290
    for ln in L: d.text((40, yy), ln, font=f, fill=INK); yy += int(s * 1.3)
    ipa = timeline[i]["ipa"]; f2, L2, s2 = fit(d, ipa, MONO, 780, 70, 15, 10, 1.25); yy = max(yy + 8, 560)
    for ln in L2[:4]: d.text((40, yy), ln, font=f2, fill=(160, 175, 200)); yy += int(s2 * 1.25)
    eng = kjv.get(k, ""); f3, L3, s3 = fit(d, eng, SANS, 780, 60, 15, 10, 1.25); yy = max(yy + 6, 640)
    for ln in L3[:3]: d.text((40, yy), ln, font=f3, fill=MUTED); yy += int(s3 * 1.25)
    # data panel
    px = 860; d.rectangle([px - 16, 196, W - 40, 700], outline=LINE); py = 208
    r = vrow.get(vs, {}); hp = sum(t_["pos"][0] == "V" and t_["parse"][:2] == "3P" and t_["parse"][3] == "I" and t_["lem"] in HPV for t_ in V[k])
    blk = next((nm for nm, a, b in BLOCKS if a <= k <= b), "—"); md = MODEV[i]
    rows = [("time", f"{int(timeline[i]['start'] // 60)}:{timeline[i]['start'] % 60:04.1f} / {int(TOT // 60)}:{TOT % 60:02.0f}"), ("verse audio", f"{timeline[i]['dur']:.1f} s" + (f" (after {timeline[i]['pre']:.0f} s section pause)" if timeline[i]["pre"] else "")),
            ("theme block", blk), ("voice mode", f"{md:+.2f}  " + ("discourse" if md > 0 else "action")), ("noise share", f"{float(r.get('noise_share', 0)):.3f}  (book mean 0.326)"),
            ("syllables", r.get("syllables", "")), ("breath groups", r.get("breath_groups", "")), ("historic presents", str(hp)),
            ("body / motion", ", ".join(mv.get(vs, {}).get("body", [])) or "—")]
    for a, b in rows:
        d.text((px, py), a, font=SANS(12), fill=MUTED); d.text((px + 120, py), str(b)[:38], font=SANS(13), fill=INK); py += 22
    py += 6; d.text((px, py), "markers", font=SANS(12), fill=MUTED); py += 18
    ms = [m for m in r.get("markers", "").split(";") if m and m != "i_am_images"]
    if not ms: d.text((px + 8, py), "—", font=SANS(13), fill=INK); py += 20
    for m in ms[:4]: d.text((px + 8, py), "● " + MARKNAME.get(m, m), font=SANS(13), fill=MCOL.get(m, INK)); py += 20
    py += 8; d.text((px, py), "echoes (most similar verses 30+ away)", font=SANS(12), fill=MUTED); py += 18
    s_ = SIM[i].copy(); s_[max(0, i - 30): i + 31] = -1
    for j in np.argsort(-s_)[:2]:
        if s_[j] > 0.15: d.text((px + 8, py), f"{keys[j][0]}:{keys[j][1]}  (similarity {s_[j]:.2f})", font=SANS(13), fill=INK); py += 20
    # local noise strip (±20 verses)
    py = 640; d.text((px, py - 16), "noise share, ±20 verses", font=SANS(11), fill=MUTED)
    for q in range(max(0, i - 20), min(n, i + 21)):
        nv = float(vrow.get(f"{keys[q][0]}:{keys[q][1]}", {}).get("noise_share", 0.326)); hh = max(1, int((nv - 0.2) * 260))
        xq = px + (q - i + 20) * 9; d.rectangle([xq, 690 - hh, xq + 6, 690], fill=GOLD if q == i else (90, 92, 100))
    p = os.path.join(FR, f"{i:04d}.png"); im.save(p, optimize=False); return p
for i in range(n):
    p = os.path.join(FR, f"{i:04d}.png")
    if not os.path.exists(p): frame(i)
print("frames done", flush=True)
# ---------------- encode per chapter, then join
SR = E.SR; parts = []
for c in range(1, 22):
    ii = [i for i, k in enumerate(keys) if k[0] == c]; chunks = []
    for i in ii:
        sr, y = E.wavfile.read(os.path.join(WAV, f"{keys[i][0]:02d}_{keys[i][1]:03d}.wav"))
        chunks += [np.zeros(int(timeline[i]["pre"] * SR), np.int16), y.astype(np.int16), np.zeros(int(GAP * SR), np.int16)]
    aw = os.path.join(WORK, f"ch{c:02d}.wav"); E.wavfile.write(aw, SR, np.concatenate(chunks))
    lst = os.path.join(WORK, f"ch{c:02d}.txt")
    with open(lst, "w") as fh:
        for i in ii:
            fh.write(f"file '{os.path.join(FR, f'{i:04d}.png')}'\nduration {timeline[i]['pre'] + timeline[i]['dur'] + GAP:.3f}\n")
        fh.write(f"file '{os.path.join(FR, f'{ii[-1]:04d}.png')}'\n")
    mp4 = os.path.join(OUT, f"john_ch{c:02d}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", aw, "-vf", "fps=2,format=yuv420p", "-c:v", "libx264", "-tune", "stillimage",
                    "-crf", "30", "-preset", "medium", "-c:a", "aac", "-b:a", "48k", "-ac", "1", "-shortest", "-movflags", "+faststart", mp4], check=True)
    os.remove(aw); parts.append(mp4); print("encoded", mp4, round(os.path.getsize(mp4) / 1e6, 1), "MB", flush=True)
with open(os.path.join(WORK, "all.txt"), "w") as fh:
    for p in parts: fh.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(WORK, "all.txt"), "-c", "copy", "-movflags", "+faststart", os.path.join(OUT, "john_full.mp4")], check=True)
json.dump(manifest, open(os.path.join(OUT, "render_manifest.json"), "w"), ensure_ascii=False, indent=1)
print("done", round(os.path.getsize(os.path.join(OUT, "john_full.mp4")) / 1e6, 1), "MB", flush=True)
