#!/usr/bin/env python3
"""Round 21: all open threads in one pass.
1. MANUSCRIPT LINES AS BREATH GROUPS: syllables per written line in P66, P75, Sinaiticus, Vaticanus (John), against the
   modern punctuation groups; regularity (CV); the prologue's lines.
2. SONGS OF ASCENTS: John's vertical-axis passages against Psalms 119-133 (Greek numbering; Hebrew 120-134): ranks.
3. DEDICATION: John 10:22-39 against the Dedication accounts (1 Maccabees 4:36-59; 2 Maccabees 10:1-8) and Ezekiel 34.
4. GUDEA'S TEMPLE DREAM and INANA'S DESCENT: the passages in the Sumerian literature volume beside John 2:19-21 and
   John 11 / 20 (motif table).
Usage: python3 round21.py <sblgnt> <lxx-swete/data> <cntr class 1 dir> <sumer literature txt>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, LXX, CN, LIT = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
sc = {}
def syl(w):
    if not w: return 0
    if w not in sc:
        try: sc[w] = max(1, len(E.parse_greek(w, "koine")[0]))
        except Exception: sc[w] = 1
    return sc[w]
print("1. MANUSCRIPT LINES AS BREATH GROUPS (John)")
for ms in ("P66", "P75", "01", "03"):
    lines, cur, pro = [], 0, []
    for l in open(os.path.join(CN, f"{ms}.txt"), encoding="utf-8"):
        m = re.match(r"^43(\d{3})(\d{3})\s+(.*)$", l.rstrip("\n"))
        if not m: continue
        for tok in m.group(3).split():
            br = tok.count("/") + tok.count("\\"); w = re.sub(r"[^α-ως]", "", tok.replace("ς", "σ"))
            if br and cur: lines.append(cur); (pro.append(cur) if int(m.group(1)) == 1 and int(m.group(2)) <= 18 else None); cur = 0
            cur += syl(w)
    L = np.array([x for x in lines if 3 <= x <= 40]); P = np.array([x for x in pro if 3 <= x <= 40])
    print(f"   {ms:4s} lines {len(L):5d}  syllables per line {L.mean():5.1f} (CV {L.std() / L.mean():.2f})   prologue lines {len(P)} mean {P.mean() if len(P) else float('nan'):5.1f}")
    out.setdefault("ms_lines", {})[ms] = dict(n=int(len(L)), mean=float(L.mean()), cv=float(L.std() / L.mean()))
print("   (modern punctuation groups, round 9: mean 13.5 syllables, CV 0.57)")
LV = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); LV.setdefault((b, r[1]), []).extend(w for w in (nrm(t) for t in p[1].split()) if w)
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον ην ησαν ωσ εστιν μου σου με σε".split())
def stems(ws): return {w[:5] for w in ws if w not in STOP and len(w) > 3}
CH = {k: stems(v) for k, v in LV.items() if len(v) > 40}
df = collections.Counter(s for x in CH.values() for s in x); N = len(CH)
def score(A, B): return sum(math.log(N / df[s]) for s in A & B if df.get(s, N) < .05 * N) / math.sqrt(len(B) + 1)
JN = collections.OrderedDict()
for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"): p = l.split(); JN.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(nrm(p[4]))
def jn(vs): return stems([w for v in vs for w in JN.get(v, [])])
def ranks(A, targets):
    s = sorted(((score(A, B), k) for k, B in CH.items()), reverse=True); rk = {k: i + 1 for i, (_, k) in enumerate(s)}
    return {t: rk.get(t) for t in targets}, [f"{b} {c}" for _, (b, c) in s[:5]]
print("\n2. SONGS OF ASCENTS against John's vertical-axis passages (rank among ~1,100 chapters)")
A = jn([(1, 51), (3, 13), (6, 33), (6, 38), (6, 41), (6, 50), (6, 51), (6, 58), (6, 62), (20, 17), (2, 13), (5, 1), (7, 8), (7, 10), (7, 14), (11, 55), (12, 20)])
asc = [("Psalmi", str(n)) for n in range(119, 134)]; r, top = ranks(A, asc)
print(f"   ascents ranks: {sorted(v for v in r.values() if v)};  median {int(np.median([v for v in r.values() if v]))};  top chapters: {top}")
out["ascents"] = {f"{a} {b}": v for (a, b), v in r.items()}
print("\n3. DEDICATION: John 10:22-39")
A = jn([(10, v) for v in range(22, 40)]); r, top = ranks(A, [("Machabaeorum_i", "4"), ("Machabaeorum_ii", "10"), ("Ezechiel", "34"), ("Psalmi", "81")])
print(f"   ranks: {r}; top: {top}"); out["dedication"] = {f"{a} {b}": v for (a, b), v in r.items()}
print("\n4. SUMERIAN PASSAGES")
T = open(LIT, encoding="utf-8", errors="ignore").read()
for lab, pat, w in (("Gudea / Ningirsu temple", r"Ningirsu[^.]{0,300}(dream|build)|(dream|build)[^.]{0,300}Ningirsu", 420), ("temple destroyed / rebuilt", r"(destroy|rebuil|restor)[^.]{0,80}(house|temple)", 260)):
    for m in list(re.finditer(pat, T, flags=re.I))[:3]: print(f"   {lab}: …{re.sub(r'\s+', ' ', T[max(0, m.start() - 150): m.start() + w])}…")
a = T.find("The brisk linear narrative"); seg = T[a: a + 40000]
MOTIF = [("goes down to the underworld / the dead", r"underworld|nether world", "John 11 (Lazarus in the tomb); 20 (the tomb)"),
         ("passes seven gates, stripped", r"seven gates|gate", "—"), ("killed, corpse hung on a hook", r"hook|corpse", "19 (crucified)"),
         ("three days and three nights", r"three days and three nights", "2:19 'in three days'; 11:17 'four days'"),
         ("a woman mourns / laments", r"lament|wept|weep|mourn", "11:31-35 (Mary weeps; Jesus wept); 20:11 (Mary weeps)"),
         ("life-giving water and plant", r"life-giving", "4:10 living water; 6:35 bread of life"), ("she arises", r"arise|rose", "11:44 Lazarus comes out; 20 risen"),
         ("a substitute must take her place", r"substitute|in (her|his) place", "11:50 'one man should die for the people'")]
print("   Inana's descent motif map:")
for lab, pat, jn_ in MOTIF:
    n = len(re.findall(pat, seg, flags=re.I)); print(f"      {lab:40s} {n:3d} mentions   John: {jn_}")
json.dump(out, open(os.path.join(HERE, "round21_results.json"), "w"), ensure_ascii=False, indent=1)
