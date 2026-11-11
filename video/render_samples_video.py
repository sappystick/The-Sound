#!/usr/bin/env python3
"""Word-synced sample videos for the Koine voice v2 (12 frames per second, 1280x720).

Each frame shows, at the moment of speaking:
  * the verse in Greek with the word being spoken lit in its speaker's colour (speaker estimated, round 32);
  * the current word: IPA as rendered, planned pitch targets, every rule applied (blue = evidence, amber = interpretive);
  * the melody: planned targets (dots) and the pitch measured from the final audio (line), with loudness, +-3 s;
  * a map from OpenBible.info geodata: the scene's location (last place named) and the places of the passage;
  * the whole book as a bar with this verse and arcs to its two strongest echoes (shared vocabulary, 30+ verses away).
Usage: python3 render_samples_video.py <sblgnt dir>
"""
import collections, glob, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
SBL = sys.argv[1]; SETNAME = sys.argv[2] if len(sys.argv) > 2 else "samples"; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
A2 = os.path.join(ROOT, "audio_model", "v2"); OUT = os.path.join(HERE, "samples"); os.makedirs(OUT, exist_ok=True)
RB = json.load(open(os.path.join(ROOT, "code/voice/delivery_rules.json"), encoding="utf-8")); RULE = {r["id"]: r for r in RB["rules"]}
GEO = json.load(open(os.path.join(ROOT, "data/john_geo.json"), encoding="utf-8"))
FPS, W, H = 12, 1280, 720
def font(n, kind="sans"):
    f = {"sans": "DejaVuSans.ttf", "bold": "DejaVuSans-Bold.ttf", "serif": "DejaVuSerif.ttf", "mono": "DejaVuSansMono.ttf"}[kind]
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + f, n)
BG, PANEL, INK, MUTED, RULEC = (16, 19, 26), (24, 28, 37), (234, 230, 220), (140, 146, 156), (46, 52, 64)
EVID, INTERP, GOLD = (110, 160, 235), (226, 170, 80), (214, 170, 86)
SPK = {"narrator": (150, 165, 190), "Jesus": (232, 190, 92), "Mary": (226, 120, 140), "Martha": (176, 140, 226), "they": (120, 196, 140), "John (the Baptist)": (224, 128, 96),
       "his mother": (226, 120, 140), "the steward": (176, 140, 226), "Andrew": (110, 200, 210), "Philip": (140, 170, 240), "Nathanael": (196, 160, 230), "Peter": (120, 210, 170)}
def spk_col(s): return SPK.get(s, (110, 200, 210))
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
# ---- book-level data: verse order, echoes
V = collections.OrderedDict()
for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"):
    p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(lem=nrm(p[6]), pos=p[1]))
keys = list(V); n = len(keys); idx = {f"{c}:{v}": i for i, (c, v) in enumerate(keys)}
STOP = set("ο και αυτος δε εν ειμι λεγω ου μη γαρ ουν οτι εγω συ ουτος εκεινος τις ινα προς εκ εις απο επι δια μετα περι αλλα ως καθως ημεις υμεις εαν αν οστις παρα υπο ηδη ετι ουδε τε η ποιεω εχω γινομαι ερχομαι".split())
docs = [[t["lem"] for t in V[k] if t["pos"][0] in "NVA" and t["lem"] not in STOP] for k in keys]
df = collections.Counter(l for x in docs for l in set(x)); voc = {l: i for i, l in enumerate(df)}; X = np.zeros((n, len(voc)))
for i, x in enumerate(docs):
    for l in x: X[i, voc[l]] += math.log(n / df[l])
X /= np.maximum(1e-9, np.linalg.norm(X, axis=1, keepdims=True)); SIM = X @ X.T
def echoes(i):
    s = SIM[i].copy(); s[max(0, i - 30): i + 31] = -1; return [(int(j), float(s[j])) for j in np.argsort(-s)[:2] if s[j] > 0.15]
# ---- places: scene location = last place named at or before the verse
vplaces = collections.defaultdict(list)
for nm, p in GEO["places"].items():
    for v in p["verses"]: vplaces[v].append(nm)
scene = {}; last = None
for c, v in keys:
    vs = f"{c}:{v}"; real = [p for p in vplaces.get(vs, []) if not p.startswith(("Galilee", "Judea", "Samaria", "Zion"))] or vplaces.get(vs, [])
    if real: last = real[0]
    scene[vs] = last
# ---- static map projection
LON0, LON1, LAT0, LAT1 = 34.75, 35.9, 31.45, 33.05
MX0, MY0, MX1, MY1 = 870, 70, 1240, 430
def proj(lon, lat):
    x = MX0 + (lon - LON0) / (LON1 - LON0) * (MX1 - MX0); y = MY1 - (lat - LAT0) / (LAT1 - LAT0) * (MY1 - MY0); return x, y
def base_frame(title, sub):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((40, 18), title, font=font(20, "bold"), fill=GOLD); d.text((40, 44), sub, font=font(13), fill=MUTED)
    d.rectangle([MX0 - 10, MY0 - 10, MX1 + 10, MY1 + 10], fill=PANEL)
    for nm, o in GEO["outlines"].items():
        for ln in o["lines"]:
            pts = [proj(x, y) for x, y in ln if LON0 - .5 < x < LON1 + .5 and LAT0 - .5 < y < LAT1 + .5]
            pts = [(min(max(x, MX0 - 10), MX1 + 10), min(max(y, MY0 - 10), MY1 + 10)) for x, y in pts]
            if len(pts) > 2:
                if o["kind"] == "area": d.polygon(pts, fill=(34, 58, 84))
                else: d.line(pts, fill=(60, 110, 150), width=2)
    for nm, p in GEO["places"].items():
        x, y = proj(*p["lonlat"])
        if MX0 <= x <= MX1 and MY0 <= y <= MY1: d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(90, 96, 108))
    d.text((MX0 - 6, MY1 + 14), "Places: OpenBible.info geodata (CC BY 4.0) · scene = last place named", font=font(10), fill=MUTED)
    by = 478; d.line([(MX0, by), (MX1, by)], fill=RULEC, width=6)
    for c in (1, 5, 10, 15, 21):
        i = next(j for j, k in enumerate(keys) if k[0] == c); x = MX0 + (MX1 - MX0) * i / (n - 1); d.text((x - 4, by + 8), str(c), font=font(10), fill=MUTED)
    d.text((MX0, by + 22), "the whole Gospel · arcs to this verse's echoes", font=font(11), fill=MUTED)
    d.text((40, 690), "Synthetic reconstruction: neural Greek voice speaking reconstructed Koine; melody from the rulebook. Speakers estimated; amber rules are interpretive.", font=font(11), fill=MUTED)
    return im
def wrap_words(d, words, f, width):
    lines, cur, w0 = [], [], 0
    for i, w in enumerate(words):
        ww = d.textlength(w + " ", font=f)
        if cur and w0 + ww > width: lines.append(cur); cur, w0 = [], 0
        cur.append(i); w0 += ww
    if cur: lines.append(cur)
    return lines
def render(name, label):
    js = json.load(open(os.path.join(A2, f"{name}_C_full.json"), encoding="utf-8")); words = js["words"]
    sr, y = wavfile.read(os.path.join(A2, f"{name}_C_full.wav")); y = y.astype(float) / 32768; dur = len(y) / sr
    hop = int(sr / 50); rms = np.array([np.sqrt(np.mean(y[i:i + hop] ** 2)) for i in range(0, len(y), hop)]); rms_db = 20 * np.log10(rms + 1e-5); rms_t = np.arange(len(rms)) / 50
    f0 = np.array(js["f0"]); plan = []
    for w in words:
        k = len(w["pitch_hz"])
        for j, hz in enumerate(w["pitch_hz"]): plan.append((w["start"] + (w["end"] - w["start"]) * (j + .5) / max(1, k), hz, w["speaker"]))
    plan = np.array([(a, b) for a, b, _ in plan]) if plan else np.zeros((0, 2))
    base = base_frame(label, f"John {js['refs'][0]}–{js['refs'][-1]} · Koine voice v2 (reconstructed 1st-century pronunciation) · evidence + delivery layers · synagogue room")
    by_verse = collections.OrderedDict()
    for i, w in enumerate(words): by_verse.setdefault(w["ref"], []).append(i)
    fdir = os.path.join(OUT, "_frames_" + name); os.makedirs(fdir, exist_ok=True)
    nf = int(math.ceil(dur * FPS))
    for fi in range(nf):
        t = fi / FPS; im = base.copy(); d = ImageDraw.Draw(im)
        cur = next((i for i, w in enumerate(words) if w["start"] <= t < w["end"]), None)
        if cur is None: cur = max([i for i, w in enumerate(words) if w["start"] <= t] or [0])
        w = words[cur]; ref = w["ref"]; vi = by_verse[ref]
        # speaker chip and verse
        col = spk_col(w["speaker"]); d.rounded_rectangle([40, 76, 40 + 22 + d.textlength(w["speaker"], font=font(15, "bold")) + 16, 104], 12, fill=col)
        d.text((60, 81), w["speaker"], font=font(15, "bold"), fill=BG); d.text((40 + 60 + d.textlength(w["speaker"], font=font(15, "bold")), 80), f"John {ref}", font=font(18), fill=INK)
        if w.get("lang"):
            lx = 40 + 60 + d.textlength(w["speaker"], font=font(15, "bold")) + d.textlength(f"John {ref}", font=font(18)) + 24
            d.text((lx, 84), ("composed in Greek" if w["speaker"] == "narrator" else f"first spoken in {w['lang']} ({w['lang_conf']}) · heard here in the Gospel's Greek"), font=font(12), fill=MUTED)
        toks = [words[i]["word"] for i in vi]
        for size in (28, 24, 21, 18, 16):
            f = font(size, "serif"); L = wrap_words(d, toks, f, 780); lh = int(size * 1.55)
            if len(L) * lh <= 172: break
        yy = 120
        for line in L:
            x = 40
            for li in line:
                gi = vi[li]; ww = d.textlength(toks[li], font=f)
                if gi == cur: d.rounded_rectangle([x - 4, yy - 2, x + ww + 4, yy + int(size * 1.35)], 6, fill=spk_col(words[gi]["speaker"])); d.text((x, yy), toks[li], font=f, fill=BG)
                else: d.text((x, yy), toks[li], font=f, fill=INK if words[gi]["end"] <= t else (118, 124, 136))
                x += ww + d.textlength(" ", font=f)
            yy += lh
        # current word panel: left = the word; right = rules and the earliest manuscripts
        py = 300; d.rectangle([40, py, 820, py + 205], fill=PANEL)
        d.text((56, py + 10), w["word"], font=font(30, "serif"), fill=INK); d.text((56, py + 52), "/" + w["ipa"] + "/", font=font(16, "mono"), fill=(160, 178, 210))
        d.text((56, py + 80), "pitch  " + "  ".join(f"{h:.0f} Hz" for h in w["pitch_hz"][:4]), font=font(12), fill=MUTED)
        d.text((56, py + 98), f"gain {w['gain_db']:+.0f} dB · {w['end'] - w['start']:.2f} s", font=font(12), fill=MUTED)
        if w.get("aram"):
            d.text((56, py + 124), "Aramaic kept in the Greek", font=font(11, "bold"), fill=GOLD)
            for q, ln in enumerate(wrap_words(d, w["aram"].split(), font(12), 340)[:3]): d.text((56, py + 140 + 16 * q), " ".join(w["aram"].split()[i] for i in ln), font=font(12), fill=INK)
        ry = py + 12
        for r in w["rules"][:6]:
            rr = RULE.get(r, {}); c = EVID if rr.get("layer") == "evidence" else INTERP
            d.text((400, ry), r, font=font(11, "bold"), fill=c); d.text((472, ry), rr.get("effect", "")[:56], font=font(11), fill=INK); ry += 16
        if js.get("mss", {}).get(ref):
            d.text((400, py + 116), "this verse in the earliest manuscripts (against SBLGNT)", font=font(11, "bold"), fill=MUTED)
            for q, ln in enumerate(js["mss"][ref]): d.text((400, py + 133 + 16 * q), ln, font=font(11), fill=INK if "same wording" in ln else (226, 170, 80) if "differ" in ln else MUTED)
        # melody panel
        gy0, gy1, gx0, gx1 = 520, 678, 40, 820; d.rectangle([gx0, gy0, gx1, gy1], fill=PANEL)
        lo, hi = 70.0, 150.0; Y = lambda hz: gy1 - 8 - (math.log(hz / lo) / math.log(hi / lo)) * (gy1 - gy0 - 16); Xt = lambda tt: gx0 + (tt - (t - 3)) / 6 * (gx1 - gx0)
        m = (rms_t > t - 3) & (rms_t < t + 3)
        for tt, db in zip(rms_t[m], rms_db[m]):
            hh = max(0, (db + 50) * 1.4); d.line([(Xt(tt), gy1), (Xt(tt), gy1 - hh)], fill=(40, 46, 58))
        m = (f0[:, 0] > t - 3) & (f0[:, 0] < t + 3) & (f0[:, 1] > 0); pts = [(Xt(a), Y(min(max(b, lo), hi))) for a, b in f0[m]]
        for a, b in zip(pts, pts[1:]):
            if abs(a[0] - b[0]) < 6 and abs(a[1] - b[1]) < 14: d.line([a, b], fill=INK, width=2)
        for a, b in plan[(plan[:, 0] > t - 3) & (plan[:, 0] < t + 3)] if len(plan) else []:
            x0, y0 = Xt(a), Y(min(max(b, lo), hi)); d.ellipse([x0 - 3, y0 - 3, x0 + 3, y0 + 3], outline=GOLD, width=2)
        d.line([(Xt(t), gy0), (Xt(t), gy1)], fill=(200, 90, 90), width=1)
        for hz in (80, 100, 125): d.text((gx0 + 4, Y(hz) - 7), f"{hz}", font=font(9), fill=MUTED)
        d.text((gx0 + 30, gy0 + 4), "melody: planned (gold) vs measured (white) · loudness (shade) · ±3 s", font=font(11), fill=MUTED)
        # map highlight
        sp = scene.get(ref)
        for p in {q for r_ in by_verse for q in vplaces.get(r_, [])}:
            x, y_ = proj(*GEO["places"][p]["lonlat"]); d.ellipse([x - 4, y_ - 4, x + 4, y_ + 4], outline=INK)
        if sp:
            x, y_ = proj(*GEO["places"][sp]["lonlat"]); d.ellipse([x - 7, y_ - 7, x + 7, y_ + 7], fill=GOLD); d.text((x + 10, y_ - 8), sp.rstrip(" 12"), font=font(14, "bold"), fill=INK)
        else: d.text((MX0 + 6, MY0 + 4), "no place named yet", font=font(12), fill=MUTED)
        # book bar with echo arcs
        i = idx[ref]; bx = lambda j: MX0 + (MX1 - MX0) * j / (n - 1); byy = 478
        for j, s in echoes(i):
            a, b = sorted((bx(i), bx(j))); r_ = min((b - a) / 2, 60); d.arc([a, byy - r_, b, byy + r_], 0, 180, fill=EVID, width=2); d.text((bx(j) - 12, byy + 40 + 12 * echoes(i).index((j, s))), keys[j][0].__str__() + ":" + str(keys[j][1]), font=font(10), fill=EVID)
        d.ellipse([bx(i) - 5, byy - 5, bx(i) + 5, byy + 5], fill=GOLD)
        # legend
        ly = 566
        for s in sorted({w_["speaker"] for w_ in words}, key=lambda s: s != "narrator"):
            d.rounded_rectangle([MX0, ly, MX0 + 10, ly + 10], 3, fill=spk_col(s)); d.text((MX0 + 18, ly - 2), s, font=font(11), fill=INK); ly += 15
        d.text((MX0 + 190, 566), "■ evidence rule", font=font(11), fill=EVID); d.text((MX0 + 190, 582), "■ interpretive rule", font=font(11), fill=INTERP)
        im.save(os.path.join(fdir, f"{fi:05d}.png"))
    mp4 = os.path.join(OUT, f"{name}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(fdir, "%05d.png"), "-i", os.path.join(A2, f"{name}_C_full.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-preset", "medium", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    for f_ in glob.glob(os.path.join(fdir, "*.png")): os.remove(f_)
    os.rmdir(fdir); print(name, round(os.path.getsize(mp4) / 1e6, 1), "MB", flush=True); return mp4
if SETNAME == "opening":
    LABELS = {x["name"]: x["label"] for x in json.load(open(os.path.join(A2, "opening_index.json"), encoding="utf-8"))}; REEL = "opening_pages.mp4"
else:
    LABELS = {"prologue_1-1-5": "In the beginning was the Word", "lazarus_11-32-36": "Jesus wept", "vine_15-1-5": "I am the vine", "finished_19-28-30": "It is finished"}; REEL = "sample_reel.mp4"
parts = [render(k, v) for k, v in LABELS.items()]
with open(os.path.join(OUT, "_list.txt"), "w") as fh:
    for p in parts: fh.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "_list.txt"), "-c", "copy", "-movflags", "+faststart", os.path.join(OUT, REEL)], check=True)
os.remove(os.path.join(OUT, "_list.txt")); print("reel", round(os.path.getsize(os.path.join(OUT, REEL)) / 1e6, 1), "MB")
