#!/usr/bin/env python3
"""Build the configurable sound model of John from model/john_model_config.json.

Output (model/out/):
  john_score.jsonl.gz  one record per syllable: verse, breath group, word, phonemes, stress, nucleus formants (F1, F2),
                       duration (s), onset time (s), pitch (Hz), relative loudness (dB), noise flag, room, markers
  john_verses.csv      one row per verse: start time, duration, syllables, breath groups, noise share, markers
  john_summary.json    totals: running time, breaths per minute, sessions, the timeline position of every marker
Usage: python3 build_john_model.py <sblgnt dir> [config] [cntr 'class 1' dir]
"""
import collections, csv, glob, gzip, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); SBL = sys.argv[1]
CFG = json.load(open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "john_model_config.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "code", "engine")); import engine as E
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
OBS = {"p", "b", "t", "d", "k", "g", "pʰ", "tʰ", "kʰ", "f", "v", "θ", "ð", "s", "z", "x", "ɣ", "ç", "ʝ", "h", "ps", "ks", "β", "φ", "dz", "ts"}
era = CFG["pronunciation"]["era"]; rate = CFG["tempo"]["syllables_per_second"]; P = CFG["tempo"]["pause_seconds"]
f0 = CFG["voice"]["f0_hz"]; rng_st = CFG["voice"]["f0_range_semitones"]; stress_db = CFG["dynamics"]["stress_boost_db"]
room = CFG["space"]["room"]; ROOM = CFG["space"]["options"][room]
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
cache = {}
def parse(raw):
    k = unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw.lower()))
    if not k: return []
    if (k, era) not in cache:
        try: cache[(k, era)] = E.parse_greek(k, era)[0]
        except Exception: cache[(k, era)] = []
    return cache[(k, era)]
# ---- markers (from DISCOVERIES.md)
IAM_RING = {(6, 35), (6, 48), (6, 51), (8, 12), (10, 7), (10, 9), (10, 11), (10, 14), (11, 25), (14, 6), (15, 1), (15, 5)}
MARK = collections.defaultdict(set)
for v in IAM_RING: MARK[v].add("i_am_ring")
for v in [(9, 5)] + list(IAM_RING): MARK[v].add("i_am_images")
for v in [(1, 12), (1, 13)]: MARK[v].add("prologue_centre")
for v in [(3, 22), (6, 1), (9, 1), (18, 1), (13, 22), (17, 26)]: MARK[v].add("seams")
for v in [(7, 43), (9, 16), (10, 19), (19, 24), (21, 11)]: MARK[v].add("schism_chain")
for v in [(1, 51), (3, 13), (6, 33), (6, 38), (6, 41), (6, 50), (6, 51), (6, 58), (6, 62), (20, 17)]: MARK[v].add("vertical_axis")
for v in [(11, 49), (11, 51), (18, 13), (18, 15), (18, 19), (19, 23), (19, 24)]: MARK[v].add("high_priest")
for v in [(4, 10), (4, 14), (7, 38), (19, 34)]: MARK[v].add("living_water")
BLOCKS = [("water", (2, 1), (4, 42)), ("bread and life", (6, 1), (6, 71)), ("light", (8, 12), (9, 41)), ("hour and glory", (12, 20), (13, 32)), ("abide and love", (14, 1), (17, 26))]
SOUND_ALIKE = {"ημεισ", "υμεισ", "ημων", "υμων", "ημιν", "υμιν", "ημασ", "υμασ"}
# ---- load text
V = collections.OrderedDict()
for l in open(glob.glob(os.path.join(SBL, "*-Jn-morphgnt.txt"))[0], encoding="utf-8"):
    p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(p[3])
if CFG["text"]["pericope_adulterae_7_53_8_11"] == "exclude":
    for k in [k for k in V if (7, 53) <= k <= (8, 11)]: del V[k]
semi = 2 ** (rng_st / 12)
t = 0.0; rows = []; vrows = []; group = 0
with gzip.open(os.path.join(OUT, "john_score.jsonl.gz"), "wt", encoding="utf-8") as fh:
    for (c, v), toks in V.items():
        vstart = t; nsyl = 0; obs = nph = 0; groups0 = group
        block = next((b for b, a, z in BLOCKS if a <= (c, v) <= z), None)
        if (c, v) in [(6, 1), (13, 1), (18, 1)]: t += P["paragraph_seam"]
        for wi, raw in enumerate(toks):
            sy = parse(raw); n = len(sy)
            for si, s in enumerate(sy):
                stressed = bool(s["accent"]); dur = (1 / rate) * (1.35 if stressed else 1.0) * (1.15 if s["long"] else 1.0)
                pitch = f0 * (semi if stressed else 1.0) * (0.94 if si == n - 1 and re.search(r"[.;·]$", raw) else 1.0)
                nuc = (s["nuc"][0].rstrip("ː") if s["nuc"] else "ə"); F = E.VOWELS.get(nuc, (0, 0, 0))
                noise = sum(p_ in OBS for p_ in s["ph"]); obs += noise; nph += len(s["ph"])
                rec = dict(v=f"{c}:{v}", g=group, w=wi, word=raw, syl=si, ph=s["ph"], stress=stressed, F1=F[0], F2=F[1], dur=round(dur, 3), t=round(t, 3),
                           f0=round(pitch, 1), db=stress_db if stressed else 0, noise=noise, room=room, block=block,
                           markers=sorted(MARK.get((c, v), set()) | ({"sound_alike"} if nrm(raw) in SOUND_ALIKE else set()) | ({"amen_amen"} if nrm(raw) == "αμην" else set())))
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); t += dur; nsyl += 1
            if re.search(r"[.;·]$", raw): t += P["full_stop"] if raw.endswith(".") else P["colon_or_raised_dot"]; group += 1
            elif raw.endswith(","): t += P["comma"]; group += 1
        vrows.append(dict(verse=f"{c}:{v}", start_s=round(vstart, 1), dur_s=round(t - vstart, 2), syllables=nsyl, breath_groups=group - groups0,
                          noise_share=round(obs / max(nph, 1), 3), block=block or "", markers=";".join(sorted(MARK.get((c, v), set())))))
with open(os.path.join(OUT, "john_verses.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(vrows[0])); w.writeheader(); w.writerows(vrows)
tot = t; first = {}
for r in vrows:
    for m in r["markers"].split(";"):
        if m and m not in first: first[m] = (r["verse"], round(r["start_s"] / tot, 3))
summary = dict(config=dict(era=era, rate=rate, f0=f0, room=room, rt60=ROOM.get("rt60_s")), running_time_min=round(tot / 60, 1), verses=len(vrows),
               syllables=sum(r["syllables"] for r in vrows), breath_groups=group, breaths_per_min=round(group / (tot / 60), 1),
               chapter_times_min={c: round(sum(r["dur_s"] for r in vrows if r["verse"].startswith(f"{c}:")) / 60, 1) for c in range(1, 22)},
               first_marker_position=first)
json.dump(summary, open(os.path.join(OUT, "john_summary.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: summary[k] for k in ("config", "running_time_min", "verses", "syllables", "breath_groups", "breaths_per_min")}, ensure_ascii=False))
print("chapter minutes:", summary["chapter_times_min"])
