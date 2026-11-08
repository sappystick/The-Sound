#!/usr/bin/env python3
"""Was movement written into tense and rhythm?  Three dimensions, each with a control.

A. TENSE AS CAMERA. Historic presents (present indicative, 3rd person, of narrative verbs: say, come, see, find, take,
   follow, run, call, bring, go in, go out) per 1,000 words in John, Mark, Matthew, Luke; where they cluster in John; whether
   John's turning-point scenes (fixed list) are denser in historic presents than his other narrative.  Also the imperfect
   ('the camera holding') against the aorist ('snapshot').
B. RHYTHM ACTS OUT MOTION (Dionysius, On Composition 20). Syllable weight (heavy = long vowel or closed syllable; classical
   values) per line or verse.  Control 1: Odyssey 11.593-600, Sisyphus: the uphill lines heavy, the rolling-down line
   (598) light.  Control 2: across the Iliad, are lines with verbs of rapid motion (rush, run, fly, flow, roll, fall, leap)
   lighter than other lines?  Then John: are verses with fast-action verbs lighter than his other narrative verses?
C. PARTICIPLE CHAINS AND ASYNDETON at John's turning points against his other narrative.
Usage: python3 action_rhythm.py <sblgnt> <greek dir>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, GR = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(20); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
cache = {}
def weights(raw):
    k = unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw.lower()))
    if not k: return []
    if k not in cache:
        try: cache[k] = [2 if (s["long"] or s["ph"][-1] not in s["nuc"]) else 1 for s in E.parse_greek(k, "attic")[0]]
        except Exception: cache[k] = []
    return cache[k]
def light_share(tokens):
    w = [x for t in tokens for x in weights(t)]; return (w.count(1) / len(w)) if w else np.nan
G = {}
for code in ("Jn", "Mk", "Mt", "Lk"):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], pos=p[1], parse=p[2], lem=nrm(p[6]), w=nrm(p[4])))
    G[code] = V
HPV = {"λεγω", "ερχομαι", "βλεπω", "ευρισκω", "λαμβανω", "ακολουθεω", "τρεχω", "φωνεω", "αγω", "φερω", "εισερχομαι", "εξερχομαι", "θεωρεω", "παραλαμβανω", "εγειρω", "αποστελλω", "πεμπω", "μαρτυρεω", "κραζω", "κραυγαζω"}
def is_hp(t): return t["pos"].startswith("V") and t["parse"][0] == "3" and t["parse"][1] == "P" and t["parse"][3] == "I" and t["lem"] in HPV
TURN = [((11, 38), (11, 44)), ((13, 1), (13, 11)), ((18, 1), (18, 12)), ((19, 16), (19, 30)), ((20, 1), (20, 18)), ((21, 1), (21, 14)), ((9, 1), (9, 12)), ((4, 5), (4, 15))]
def in_turn(r): return any(a <= r <= b for a, b in TURN)
print("A. TENSE AS CAMERA")
for code, V in G.items():
    toks = [t for v in V.values() for t in v]; n = len(toks); hp = sum(is_hp(t) for t in toks)
    ind = [t for t in toks if t["pos"].startswith("V") and t["parse"][3:4] == "I"]
    impf = sum(t["parse"][1] == "I" for t in ind); aor = sum(t["parse"][1] == "A" for t in ind)
    print(f"   {code}: historic presents {hp:4d} ({1000 * hp / n:4.1f} per 1,000 words)   imperfect : aorist = {impf}:{aor} ({impf / max(1, impf + aor):.0%} imperfect)")
    out.setdefault("A", {})[code] = dict(hp_per_k=1000 * hp / n, impf_share=impf / max(1, impf + aor))
J = G["Jn"]; ch = collections.Counter(); chn = collections.Counter()
for r, v in J.items(): ch[r[0]] += sum(is_hp(t) for t in v); chn[r[0]] += len(v)
print("   John, historic presents per 1,000 words by chapter:", "  ".join(f"{c}:{1000 * ch[c] / chn[c]:.0f}" for c in range(1, 22)))
keys = list(J); hpv = np.array([sum(is_hp(t) for t in J[k]) for k in keys], float); nw = np.array([len(J[k]) for k in keys], float)
narr = np.array([not any(t["parse"][0] in "12" for t in J[k] if t["pos"].startswith("V")) or hpv[i] > 0 for i, k in enumerate(keys)])
tm = np.array([in_turn(k) for k in keys])
real = hpv[tm].sum() / nw[tm].sum()
null = []
for _ in range(3000):
    sh = np.zeros(len(keys), bool); start = rng.integers(0, len(keys) - tm.sum()); sh[rng.permutation(len(keys))[:tm.sum()]] = True; null.append(hpv[sh].sum() / nw[sh].sum())
print(f"   turning-point scenes: {1000 * real:.1f} historic presents per 1,000 words; random verse sets {1000 * np.mean(null):.1f}; p = {np.mean(np.array(null) >= real):.4f}")
out["A"]["john_turning"] = dict(rate=1000 * real, random=1000 * float(np.mean(null)))
hp2 = np.array([sum(is_hp(t) and t["lem"] != "λεγω" for t in J[k]) for k in keys], float); real2 = hp2[tm].sum() / nw[tm].sum()
null2 = [hp2[s].sum() / nw[s].sum() for s in (np.isin(np.arange(len(keys)), rng.permutation(len(keys))[:tm.sum()]) for _ in range(3000))]
print(f"   without 'says' (legei): turning points {1000 * real2:.1f} vs random {1000 * np.mean(null2):.1f}; p = {np.mean(np.array(null2) >= real2):.4f}")
print("\nB. RHYTHM ACTS OUT MOTION (share of light syllables; higher = quicker)")
def homer(work):
    x = open(glob.glob(os.path.join(GR, f"perseus/data/tlg0012/{work}/*grc*.xml"))[0], encoding="utf-8").read(); books = {}
    for m in re.finditer(r'<div n="(\d+)" type="textpart" subtype="book">(.*?)(?=<div n="\d+" type="textpart" subtype="book">|\Z)', x, re.S):
        books[int(m.group(1))] = {int(a): re.sub(r"<[^>]+>", "", b) for a, b in re.findall(r'<l n="(\d+)"[^>]*>(.*?)</l>', m.group(2), re.S)}
    return books
Od = homer("tlg002")
for n in range(593, 601):
    line = Od[11].get(n, ""); print(f"   Odyssey 11.{n}: light {light_share(line.split()):.2f}   {line[:70]}")
Il = homer("tlg001")
FAST = ("αιξ", "αισσ", "ηιξ", "θε", "θεε", "εθε", "ορμ", "ωρμ", "πετ", "επτ", "ρε", "ερρε", "κυλινδ", "εκυλ", "πιπτ", "πεσ", "επεσ", "αλτ", "αλλο", "θορ", "εθορ", "δραμ", "τρεχ", "σευ", "εσσυ")
fast, rest = [], []
for b, L in Il.items():
    for n, line in L.items():
        ws = [nrm(t) for t in line.split()]
        (fast if any(w.startswith(FAST) and len(w) > 3 for w in ws) else rest).append(light_share(line.split()))
fast, rest = np.array([x for x in fast if x == x]), np.array([x for x in rest if x == x]); d = fast.mean() - rest.mean()
allv = np.concatenate([fast, rest]); null = [np.mean(p[:len(fast)]) - np.mean(p[len(fast):]) for p in (rng.permutation(allv) for _ in range(2000))]
print(f"   Iliad: lines with rapid-motion verbs light {fast.mean():.3f} (n {len(fast)}) vs other lines {rest.mean():.3f};  difference {d:+.3f};  p = {np.mean(np.array(null) >= d):.4f}")
out["B_iliad"] = dict(fast=float(fast.mean()), rest=float(rest.mean()), p=float(np.mean(np.array(null) >= d)))
JFAST = {"τρεχω", "πιπτω", "αλλομαι", "βαλλω", "σπευδω", "εξερχομαι", "εγειρω", "ανιστημι", "φευγω", "πηδαω", "σπαω", "παιω", "ραπιζω", "μαστιγοω", "ελκω"}
for code in ("Jn", "Mk"):
    V = G[code]; f_, r_ = [], []
    for k, v in V.items():
        if any(t["pos"].startswith("V") and t["parse"][0] in "12" for t in v): continue        # narrative verses only
        (f_ if any(t["lem"] in JFAST for t in v) else r_).append(light_share([t["raw"] for t in v]))
    f_, r_ = np.array([x for x in f_ if x == x]), np.array([x for x in r_ if x == x]); d = f_.mean() - r_.mean(); allv = np.concatenate([f_, r_])
    null = [np.mean(p[:len(f_)]) - np.mean(p[len(f_):]) for p in (rng.permutation(allv) for _ in range(2000))]
    print(f"   {code}: fast-action narrative verses light {f_.mean():.3f} (n {len(f_)}) vs other narrative {r_.mean():.3f}; difference {d:+.3f}; p = {np.mean(np.array(null) >= d):.3f}")
    out.setdefault("B_gospels", {})[code] = dict(diff=float(d), p=float(np.mean(np.array(null) >= d)))
print("\nC. PARTICIPLE CHAINS AND ASYNDETON at John's turning points")
def chains(v):
    c = run = 0
    for t in v:
        if t["pos"].startswith("V") and t["parse"][3:4] == "P": run += 1
        elif t["pos"].startswith("V"): c += run >= 2; run = 0
    return c
ch_ = np.array([chains(J[k]) for k in keys], float)
real = ch_[tm].mean(); null = [ch_[rng.permutation(len(keys))[:tm.sum()]].mean() for _ in range(3000)]
print(f"   participle chains (2+ participles then a main verb) per verse: turning points {real:.3f} vs random {np.mean(null):.3f}; p = {np.mean(np.array(null) >= real):.3f}")
asy = np.array([1.0 if J[k] and J[k][0]["w"] not in ("και", "δε", "ουν", "γαρ", "αλλα", "οτε", "ωσ") and (len(J[k]) < 2 or J[k][1]["w"] not in ("δε", "ουν", "γαρ")) else 0.0 for k in keys])
real = asy[tm].mean(); null = [asy[rng.permutation(len(keys))[:tm.sum()]].mean() for _ in range(3000)]
print(f"   verses opening without a connective: turning points {real:.2f} vs random {np.mean(null):.2f}; p (higher) = {np.mean(np.array(null) >= real):.3f}")
json.dump(out, open(os.path.join(HERE, "action_rhythm_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
