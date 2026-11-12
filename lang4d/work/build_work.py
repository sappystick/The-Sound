#!/usr/bin/env python3
"""ONE PROGRAM, EVERY CHANNEL. A KANON 'work' is a single source file that is at once
   the SONG        - its sound is the program itself (the codec's just-intonation tones, error-corrected), then its output
   the LYRICS      - the English word skin of the same program, so the singer literally sings the code
   the VIDEO       - every frame drawn from the program: the word being sounded, its seal, the verse's ring, the lyric
   the CONTRACT    - royalty shares and payout rules are verses of the program, run by the same machine
   the STATISTICS  - computed from the program and from play counts fed into it
   the IDENTITY    - one hash of the canonical source; every rendering carries hashes that anyone can recompute
Whoever holds the source can regenerate everything; whoever holds a rendering can check it against the source.
Usage: python3 build_work.py work.kn [plays] [revenue]       python3 build_work.py --verify work.kn"""
import hashlib, json, math, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.dirname(HERE); sys.path.insert(0, L)
import kanon as K, skins as S
W, H, FPS = 1280, 720, 25
FONT = "/usr/share/fonts/truetype/dejavu/"
def font(n, size): return ImageFont.truetype(FONT + n, size)
def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(src): return K.norm_text(" ".join(l.strip() for l in src.splitlines() if l.strip()))
# ---------------------------------------------------------------- timeline of the spoken program (mirrors K.encode)
def timeline(src):
    GS, GW, GV = 0.045, 0.22, 0.55; t = 0.08; ev = []
    for vi, vtext in enumerate(src.split("|")):
        for tk in vtext.split():
            start = t
            if tk.startswith("="):
                t += 0.07 + GS
                for k, w in enumerate(tk[1:].split("-")):
                    if k: t += GW - GS
                    t += (len(w) // 2) * (0.07 + 0.18 + GS) + (len(w) % 2) * (0.18 + GS)
            elif tk.startswith("#"): t += len(tk[1:]) * (0.07 + 0.18 + GS)
            else:
                import re
                pre, col, w, _, post = re.fullmatch(r"(~?)(::?|=)?([a-z]*)(#[0-9te]+)?([!?]*)", tk).groups()
                t += (len(pre) + len(col or "") + len(post)) * (0.07 + GS) + (len(w) // 2) * (0.07 + 0.18 + GS) + (len(w) % 2) * (0.18 + GS)
            ev.append(dict(verse=vi, token=tk, start=round(start, 4), end=round(t, 4))); t += GW - GS
        t += GV - GW
    return ev, t
# ---------------------------------------------------------------- the song
def song(prog_ecc, events):
    code = K.encode(prog_ecc); n = len(code); tt = np.arange(n) / K.FS
    drone = sum(a * np.sin(2 * np.pi * K.F0 * r * tt) for r, a in ((0.5, 0.5), (0.75, 0.25), (1.0, 0.15)))   # root, fifth below, unison
    drone *= 0.06 * np.minimum(1, tt / 2) * np.minimum(1, (tt[-1] - tt) / 2)
    out = K.render_events(events) * 0.8
    y = np.concatenate([code * 0.9 + drone, np.zeros(K.FS // 2), out]); return y / (np.abs(y).max() + 1e-9) * 0.9, n
# ---------------------------------------------------------------- the video
HEPT = K.HEPT
def pt(cx, cy, r, k, n): a = -math.pi / 2 + 2 * math.pi * k / n; return cx + r * math.cos(a), cy + r * math.sin(a)
def draw_seal(d, w, cx, cy, r, lamp, ink, prog=1.0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 84, 100), width=2); R2 = r * 1.22
    d.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=(55, 58, 72), width=1)
    vs = [c for c in w if c in K.VOWELS]; pts = [pt(cx, cy, r, HEPT[v], 7) for v in vs]; m = max(1, math.ceil(len(pts) * prog))
    for c_i, c in enumerate(w):
        if c in K.CONS:
            x1, y1 = pt(cx, cy, R2, K.CONS.index(c), 12)
            if c_i + 1 < len(w) and w[c_i + 1] in K.VOWELS: x2, y2 = pt(cx, cy, r, HEPT[w[c_i + 1]], 7); d.line([x1, y1, x2, y2], fill=(110, 115, 135), width=2)
            d.rectangle([x1 - 5, y1 - 5, x1 + 5, y1 + 5], fill=ink)
    if m > 1: d.line(pts[:m], fill=lamp, width=6, joint="curve")
    for k, (x, y) in enumerate(pts[:m]): d.ellipse([x - (10 if k == 0 else 6), y - (10 if k == 0 else 6), x + (10 if k == 0 else 6), y + (10 if k == 0 else 6)], fill=lamp if k == 0 else ink)
def frames(prog, prog_ecc, tl, total, out_t, manifest_head, stats, contract):
    BG, INK, LAMP, NIGHT, MUT = (16, 19, 31), (230, 228, 220), (227, 162, 79), (143, 176, 232), (150, 152, 170)
    fT, fB, fM, fS = font("DejaVuSerif-Bold.ttf", 38), font("DejaVuSans.ttf", 26), font("DejaVuSansMono.ttf", 22), font("DejaVuSans.ttf", 18)
    verses = [v.strip() for v in prog_ecc.split("|")]; nframes = int(math.floor((total + out_t) * FPS)); h = hashlib.sha256()
    lyr = [S.to_skin(K.strip_checksums(v)) for v in verses]
    for f in range(nframes):
        t = f / FPS; img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
        cur = next((e for e in tl if e["start"] <= t < e["end"] + 0.175), None); vi = cur["verse"] if cur else (len(verses) - 1 if t > total else 0)
        d.text((48, 36), "KANON · one program, every channel", font=fT, fill=INK)
        d.text((48, 86), f"work {manifest_head['id'][:16]}…   seal ={manifest_head['seal']}   verse {vi + 1} of {len(verses)}", font=fS, fill=MUT)
        if t <= total:
            tok = cur["token"] if cur else ""
            w = "".join(ch for ch in tok if ch.isalpha()) if not tok.startswith(("#", "=")) else ""
            prog_in = 1.0 if not cur else min(1.0, max(0.05, (t - cur["start"]) / max(0.05, cur["end"] - cur["start"])))
            if w: draw_seal(d, w, 300, 400, 150, LAMP, INK, prog_in)
            elif tok.startswith("="):
                pw = tok[1:].split("-")
                for k, x in enumerate(pw): draw_seal(d, x, 90 + k * 95, 400, 34, NIGHT, INK)
                d.text((300, 300), "error-correction words: repair 2, flag 3-4", font=fS, fill=MUT, anchor="mm")
            d.text((300, 600), tok, font=fM, fill=LAMP, anchor="mm")
            # the verse as a ring of its words, numbered by execution order
            items = verses[vi].split("=")[0].split(); n = len(items); cx, cy, R = 900, 330, 130
            if n:
                for k in range(n // 2):
                    (x1, y1), (x2, y2) = pt(cx, cy, R, k, n), pt(cx, cy, R, n - 1 - k, n); d.line([x1, y1, cx, cy, x2, y2], fill=(61, 90, 140), width=2)
                for k, wd in enumerate(items):
                    x, y = pt(cx, cy, R, k, n); hot = cur is not None and wd == cur["token"]
                    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=LAMP if hot else NIGHT); d.text((x, y + 26), wd[:14], font=fS, fill=INK if hot else MUT, anchor="mm")
            d.text((640, 640), lyr[vi][:78], font=fB, fill=INK, anchor="mm")
            d.text((640, 680), "lyrics = the program in English words", font=fS, fill=MUT, anchor="mm")
        else:
            d.text((640, 250), "the program's own output", font=fB, fill=LAMP, anchor="mm")
            y0 = 320
            for k, line in enumerate([f"contract: shares {contract['shares']} (sum {contract['sum']})", f"payout for revenue {contract['revenue']}: {contract['payout']}",
                                       f"statistics: {stats['words']} words, {stats['syllables']} syllables, {stats['duration_s']} s, {stats['plays']} plays", "re-render the source to check every hash"]):
                d.text((640, y0 + 44 * k), line, font=fB if k < 3 else fS, fill=INK if k < 3 else MUT, anchor="mm")
        raw = img.tobytes(); h.update(raw); yield raw
    yield h.hexdigest()
# ---------------------------------------------------------------- contract and statistics, run by the same machine
def run_contract(prog, revenue):
    vm = K.VM().run(prog); shares = vm.P["o"]; total = vm.P["i"]
    pay = K.VM(); pay.defs.update(vm.defs); pay.run(f"ka #{K.to12(revenue)} | :paga")
    return dict(shares=[int(x) for x in shares], sum=int(total[-1]) if total else None, revenue=revenue, payout=[round(x, 2) for x in pay.P["i"]],
                valid=bool(total) and total[-1] == 100, rule_source="::tako (shares) and ::paga (payout) inside the work itself")
def build(path, plays=1000, revenue=5000, render=True):
    src = canonical(open(path).read()); prog_ecc = K.add_ecc(src); vm = K.VM().run(src)
    tl, total = timeline(prog_ecc); syl = sum(len("".join(c for c in v if c.isalpha())) // 2 for v in src.split())
    stats = dict(words=len([t for t in src.split() if t != "|"]), syllables=syl, verses=src.count("|") + 1, duration_s=round(total, 2), plays=plays,
                 melodies=sum(1 for e in vm.events if e[0] == "melody"), lyric_words=len(S.to_skin(src).split()))
    contract = run_contract(src, revenue)
    head = dict(id=sha(src.encode()), seal=K.checksum_word(src))
    man = dict(**head, canonical_source=src, lyrics=S.to_skin(src), spoken_with_error_correction=prog_ecc, statistics=stats, contract=contract)
    if render:
        y, ncode = song(prog_ecc, vm.events); pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
        man["song_pcm_sha256"] = sha(pcm.tobytes()); man["song_seconds"] = round(len(y) / K.FS, 2)
        man["song_decodes_to_source"] = K.correct(K.decode(y[:ncode]))[0] == src
        tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "song.wav"); K.save_wav(wav, y)
        out_t = len(y) / K.FS - total
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", "-c:a", "aac", "-b:a", "128k", "-shortest", os.path.join(HERE, "work.mp4")], stdin=subprocess.PIPE, stderr=open(os.path.join(tmp, "ff.log"), "w"))
        for fr in frames(src, prog_ecc, tl, total, out_t, head, stats, contract):
            if isinstance(fr, str): man["video_frames_sha256"] = fr
            else:
                try: ff.stdin.write(fr)
                except BrokenPipeError: raise RuntimeError(open(os.path.join(tmp, "ff.log")).read()[-800:])
        ff.stdin.close(); ff.wait()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "128k", os.path.join(HERE, "work_song.mp3")], check=True)
        K.program_seal(src, os.path.join(HERE, "work_seal.svg"), title="the work's seal")
    return man
if __name__ == "__main__":
    if sys.argv[1] == "--verify":
        man = json.load(open(os.path.join(HERE, "manifest.json"))); again = build(sys.argv[2], man["statistics"]["plays"], man["contract"]["revenue"])
        for k in ("id", "seal", "song_pcm_sha256", "video_frames_sha256", "contract"):
            print(f"{'MATCH' if again[k] == man[k] else 'DIFFERS':8s} {k}")
    else:
        man = build(sys.argv[1], *(int(x) for x in sys.argv[2:4]))
        json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), ensure_ascii=False, indent=1)
        print(json.dumps({k: man[k] for k in ("id", "seal", "lyrics", "statistics", "contract", "song_seconds", "song_decodes_to_source")}, ensure_ascii=False, indent=1))
