#!/usr/bin/env python3
"""Robustness run for the novel claims, exactly as fixed in robustness/PREREGISTRATION.md (committed 1a2d34d before this
script existed).  Writes robustness/results.json and prints a verdict per claim.
Usage: python3 robustness.py <sblgnt dir> <morphhb wlc dir> <lxx-swete data dir> <cntr class-1 dir>
"""
import collections, glob, hashlib, itertools, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
SBL, WLC, LXX, CN = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
rng = np.random.default_rng(2026); R = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
# =========================================================== C24 / C25
OUT = {"Jn": {"Brown": ["1:19", "2:1", "5:1", "11:1", "13:1", "13:31", "18:1", "20:1", "21:1"], "Moloney": ["1:19", "2:1", "5:1", "11:1", "13:1", "18:1", "20:1", "21:1"],
              "Dodd": ["1:19", "2:1", "4:46", "6:1", "7:1", "9:1", "11:1", "12:1", "13:1", "18:1", "21:1"],
              "round30": ["1:19", "2:1", "5:1", "6:1", "7:1", "9:1", "10:22", "11:1", "12:12", "13:1", "13:31", "18:1", "20:1", "21:1"]},
       "Mk": {"A": ["1:14", "3:7", "6:7", "8:22", "11:1", "14:1", "16:1"], "B": ["1:14", "8:27", "11:1", "14:1", "16:1"]},
       "Mt": {"Bacon": ["3:1", "5:1", "8:1", "10:1", "11:1", "13:1", "13:53", "18:1", "19:1", "23:1", "26:1"], "Kingsbury": ["4:17", "16:21", "26:1", "28:1"]},
       "Lk": {"A": ["1:5", "3:1", "4:14", "9:51", "19:28", "22:1", "24:1"], "B": ["1:5", "3:1", "4:14", "9:51", "19:45", "22:1", "24:1"]},
       "Ac": {"standard": ["2:1", "6:1", "8:4", "9:32", "13:1", "15:36", "19:21", "21:17", "27:1"]},
       "Gen": {"toledot": ["2:4", "5:1", "6:9", "10:1", "11:10", "11:27", "25:12", "25:19", "36:1", "37:2"]}}
pv = lambda s: tuple(int(x) for x in s.split(":"))
def greek(code):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(lem=nrm(p[6]), pos=p[1], parse=p[2]))
    return V
def greek_mode(V, variant):
    d, a = [], []
    for v in V.values():
        m = len(v); sp = any(u["pos"][0] == "V" and u["parse"][0] in "12" for u in v)
        dv = sum(t["pos"][0] == "V" and t["parse"][0] in "12" for t in v)
        if variant != "verbs": dv += sum(t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in v)
        tenses = "AI" if variant == "aor_impf" else "AIP"
        av = sum(t["pos"][0] == "V" and t["parse"][0] == "3" and t["parse"][3] == "I" and t["parse"][1] in tenses and not sp for t in v)
        d.append(dv / m); a.append(av / m)
    d, a = np.array(d), np.array(a); return (d - d.mean()) / (d.std() or 1) - (a - a.mean()) / (a.std() or 1)
def hebrew_gen():
    x = open(os.path.join(WLC, "Gen.xml"), encoding="utf-8").read(); V = collections.OrderedDict()
    for m in re.finditer(r'<verse osisID="Gen\.(\d+)\.(\d+)">(.*?)</verse>', x, re.S):
        V[(int(m.group(1)), int(m.group(2)))] = re.findall(r'morph="([^"]+)"', m.group(3))
    return V
def hebrew_mode(V, variant):
    d, a = [], []
    for ms in V.values():
        segs = [s for m in ms for s in m[1:].split("/")]; n = max(1, len(ms))
        dv = sum(bool(re.match(r"V[a-zA-Z][a-z][12]", s)) for s in segs)
        if variant != "verbs": dv += sum(bool(re.match(r"(Pp|Sp)[12]", s)) for s in segs)
        av = sum(bool(re.match(r"V[a-zA-Z]w3", s)) for s in segs)
        d.append(dv / n); a.append(av / n)
    d, a = np.array(d), np.array(a); return (d - d.mean()) / d.std() - (a - a.mean()) / a.std()
def segment(y, k, minseg):
    n = len(y); c = np.concatenate([[0], np.cumsum(y)]); c2 = np.concatenate([[0], np.cumsum(y * y)])
    D = np.full((k + 1, n + 1), np.inf); B = np.zeros((k + 1, n + 1), int); D[0, 0] = 0
    for s in range(1, k + 1):
        for i in range(n):
            if D[s - 1, i] == np.inf: continue
            js = np.arange(i + minseg, n + 1)
            if not len(js): continue
            sm = c[js] - c[i]; v = D[s - 1, i] + (c2[js] - c2[i]) - sm * sm / (js - i); b = v < D[s, js]; D[s, js[b]] = v[b]; B[s, js[b]] = i
    cuts, j = [], n
    for s in range(k, 0, -1): j = B[s, j]; cuts.append(j)
    return sorted(cuts)[1:]
_null = {}
def pval(cuts, ref, n, k, minseg, reps=5000):
    dist = lambda cs: np.mean([min(abs(c - r) for r in ref) for c in cs]); real = dist(cuts); key = (n, k, minseg, tuple(ref))
    if key not in _null:
        nl = []
        while len(nl) < reps:
            c = np.sort(rng.choice(np.arange(minseg, n - minseg), k - 1, replace=False))
            if np.all(np.diff(c) >= minseg): nl.append(dist(c))
        _null[key] = np.array(nl)
    return float(np.mean(_null[key] <= real)), float(real), float(_null[key].mean())
TEXTS = {c: greek(c) for c in ("Jn", "Mk", "Mt", "Lk", "Ac")}; TEXTS["Gen"] = hebrew_gen()
grid = list(itertools.product((10, 15, 25), ("full", "verbs", "aor_impf"), (4, 5)))
rows = []
print("C24/C25: segmentation p-values (mean distance of cuts to outline vs random)")
for code, V in TEXTS.items():
    keys = list(V); n = len(keys); idx = {k: i for i, k in enumerate(keys)}
    for minseg, var, k in grid:
        y = hebrew_mode(V, var) if code == "Gen" else greek_mode(V, var); cuts = segment(y, k, minseg)
        for oname, br in OUT[code].items():
            ref = [idx[pv(b)] for b in br if pv(b) in idx]; p, dm, dn = pval(cuts, ref, n, k, minseg)
            rows.append(dict(book=code, outline=oname, minseg=minseg, mode=var, k=k, p=p, dist=dm, null=dn, cuts=[f"{keys[c][0]}:{keys[c][1]}" for c in cuts]))
R["segmentation"] = rows
def P(book, outline=None, minseg=15, mode="full", k=4):
    return [r for r in rows if r["book"] == book and (outline is None or r["outline"] == outline) and r["minseg"] == minseg and r["mode"] == mode and r["k"] == k]
for code in TEXTS:
    base = P(code); print(f"   {code:3s} baseline (min 15, full, k 4): " + "  ".join(f"{r['outline']} p {r['p']:.3f} (dist {r['dist']:.1f} vs {r['null']:.1f})" for r in base) + f"   cuts {base[0]['cuts']}")
jb = P("Jn"); c24a = sum(r["p"] < 0.05 for r in jb)
br = [r for r in rows if r["book"] == "Jn" and r["outline"] == "Brown" and r["k"] == 4]; c24b = np.mean([r["p"] < 0.05 for r in br])
C24 = c24a >= 3 and c24b >= 0.75
print(f"\n   C24 rule: John outlines with p<0.05 at baseline = {c24a}/4 (need 3); Brown grid share p<0.05 = {c24b:.0%} (need 75%)  ->  {'HOLDS' if C24 else 'FAILS'}")
for r in br: print(f"      Brown  min {r['minseg']:2d}  {r['mode']:8s}  p {r['p']:.3f}  cuts {' '.join(r['cuts'])}")
# C25: for each (outline index pairing) x params, John lowest p among four Gospels.  Outlines: all combinations of one outline per Gospel.
wins = tot = 0; syn_sig = collections.Counter(); syn_tot = collections.Counter()
for minseg, var in itertools.product((10, 15, 25), ("full", "verbs", "aor_impf")):
    pj = {o: P("Jn", o, minseg, var)[0]["p"] for o in OUT["Jn"]}; ps = {c: {o: P(c, o, minseg, var)[0]["p"] for o in OUT[c]} for c in ("Mk", "Mt", "Lk")}
    for c in ps:
        for o, p in ps[c].items(): syn_sig[c] += p < 0.05; syn_tot[c] += 1
    for oj, om, ot, ol in itertools.product(OUT["Jn"], OUT["Mk"], OUT["Mt"], OUT["Lk"]):
        tot += 1; wins += pj[oj] < min(ps["Mk"][om], ps["Mt"][ot], ps["Lk"][ol])
share = wins / tot; maj = {c: syn_sig[c] / syn_tot[c] for c in syn_sig}; C25 = share >= 0.8 and all(v <= 0.5 for v in maj.values())
print(f"\n   C25 rule: John lowest p in {share:.0%} of {tot} outline x parameter combinations (need 80%); Synoptic share p<0.05: " + ", ".join(f"{c} {v:.0%}" for c, v in maj.items()) + f"  ->  {'HOLDS' if C25 else 'FAILS'}")
ctrl = {c: np.mean([r["p"] < 0.05 for r in rows if r["book"] == c and r["k"] == 4]) for c in ("Ac", "Gen")}
print(f"   controls (share of k=4 settings with p<0.05): Acts {ctrl['Ac']:.0%}, Genesis {ctrl['Gen']:.0%};  John (all outlines) {np.mean([r['p'] < 0.05 for r in rows if r['book'] == 'Jn' and r['k'] == 4]):.0%}")
k5 = np.mean([r["p"] < 0.05 for r in rows if r["book"] == "Jn" and r["k"] == 5]); print(f"   secondary k=5: John share p<0.05 {k5:.0%}")
R["C24"] = dict(holds=bool(C24), baseline_outlines_sig=int(c24a), brown_grid_share=float(c24b)); R["C25"] = dict(holds=bool(C25), john_lowest_share=share, synoptic_sig_share=maj, controls=ctrl, john_k5=float(k5))
# =========================================================== C3
print("\nC3: living water at book centres")
HEB = re.compile(r"[א-ת]")
def wlc_book(f):
    x = open(f, encoding="utf-8").read(); vs = []
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)">(.*?)</verse>', x, re.S):
        ws = re.findall(r'<w lemma="([^"]*)"[^>]*>([^<]*)</w>', m.group(3)); vs.append(((int(m.group(1)), int(m.group(2))), ws))
    return vs
def lem(l): return re.sub(r"[^0-9]", "", l.split("/")[-1])
def wlc_hits(vs):
    hits = set()
    for i, (k, ws) in enumerate(vs):
        L = [lem(a) for a, _ in ws]
        if any(L[j] == "4325" and L[j + 1] == "2416" for j in range(len(L) - 1)): hits.add(i)
    return hits
def centres(units):
    """units: list of (verse index, count) -> verse index containing the midpoint"""
    tot = sum(c for _, c in units); half = tot / 2; acc = 0
    for vi, c in units:
        acc += c
        if acc >= half: return vi
def cover(nv, hits, dd): return len({i for h in hits for i in range(h - dd, h + dd + 1) if 0 <= i < nv}) / nv
books = sorted(glob.glob(os.path.join(WLC, "*.xml"))); allbooks = {}
for f in books:
    vs = wlc_book(f); h = wlc_hits(vs)
    if vs: allbooks[os.path.basename(f)[:-4]] = (vs, h)
c3 = {}; ok = True
for b in ("Lev", "Song"):
    vs, h = allbooks[b]; nv = len(vs)
    cv = {"verses": centres([(i, 1) for i in range(nv)]), "words": centres([(i, len(ws)) for i, (k, ws) in enumerate(vs)]),
          "letters": centres([(i, sum(len(HEB.findall(t)) for _, t in ws)) for i, (k, ws) in enumerate(vs)])}
    res = {}
    for u, ci in cv.items():
        dd = min(abs(ci - x) for x in h); res[u] = dict(centre=f"{vs[ci][0][0]}:{vs[ci][0][1]}", dist=dd, chance=cover(nv, h, dd)); ok &= dd <= 3
    c3[b] = dict(hits=[f"{vs[i][0][0]}:{vs[i][0][1]}" for i in sorted(h)], centres=res)
    print(f"   {b} (WLC): phrase at {c3[b]['hits']};  " + ";  ".join(f"{u}: centre {r['centre']}, {r['dist']} verses from phrase (chance {r['chance']:.3f})" for u, r in res.items()))
# Septuagint
def lxx(fname):
    V = collections.OrderedDict()
    for l in open(os.path.join(LXX, fname), encoding="utf-8"):
        p = l.split()
        if len(p) < 2: continue
        k = tuple(int(x) for x in p[0].split(".")[1:3]); w = nrm(p[1])
        if w: V.setdefault(k, []).append(w)
    return V
for b, fn in (("Lev", "03.Leviticus.txt"), ("Song", "31.Canticum.txt")):
    V = lxx(fn); ks = list(V); nv = len(ks)
    h = {i for i, k in enumerate(ks) if any(V[k][j].startswith("υδ") and V[k][j + 1].startswith(("ζων", "ζωντ")) for j in range(len(V[k]) - 1))}
    cv = {"verses": centres([(i, 1) for i in range(nv)]), "words": centres([(i, len(V[k])) for i, k in enumerate(ks)])}
    res = {}
    for u, ci in cv.items():
        dd = min(abs(ci - x) for x in h) if h else 999; res[u] = dict(centre=f"{ks[ci][0]}:{ks[ci][1]}", dist=dd, chance=cover(nv, h, dd) if h else None); ok &= dd <= 3
    c3[b + "_LXX"] = dict(hits=[f"{ks[i][0]}:{ks[i][1]}" for i in sorted(h)], centres=res)
    print(f"   {b} (LXX): phrase at {c3[b + '_LXX']['hits']};  " + ";  ".join(f"{u}: centre {r['centre']}, {r['dist']} verses" for u, r in res.items()))
# corrected probability: each book's chance of its centre (by verses) falling within 3 verses of an occurrence; P(>=2 books) across all 39
pb = [cover(len(vs), h, 3) for vs, h in allbooks.values() if h]; names = [b for b, (vs, h) in allbooks.items() if h]
dist_ = np.zeros(len(pb) + 1); dist_[0] = 1
for q in pb: dist_ = np.concatenate([dist_[:1] * (1 - q), dist_[1:] * (1 - q) + dist_[:-1] * q])
p2 = float(dist_[2:].sum()); real_hits = [b for b, (vs, h) in allbooks.items() if h and min(abs(len(vs) // 2 - x) for x in h) <= 3]
print(f"   books with the phrase: {names}; chance per book {[round(x, 3) for x in pb]}; centres actually within 3 verses: {real_hits}")
print(f"   P(2 or more of the 39 books have it within 3 verses of their verse-centre, by chance) = {p2:.5f}   ->  C3 {'HOLDS' if ok else 'FAILS'} on the every-count rule")
R["C3"] = dict(holds=bool(ok), detail=c3, p_two_books=p2, books=names, per_book_chance=pb, note="not corrected for the number of motifs inspected in the original centre catalogue")
# =========================================================== C11
print("\nC11: identical-sound share of manuscript variants, by pronunciation era")
c11 = {}
for era in ("koine-late", "koine", "attic"):
    env = dict(os.environ, MS_ERA=era)
    subprocess.run([sys.executable, os.path.join(ROOT, "code/analysis/ms_sound.py"), SBL, LXX, CN], env=env, capture_output=True, check=True)
    v = json.load(open(os.path.join(ROOT, "code/analysis/ms_sound_results.json"), encoding="utf-8"))["variants"]; c11[era] = {}
    for ms, cnt in v.items():
        tot_ = sum(cnt.values()); same = tot_ - cnt.get("different sound", 0); c11[era][ms] = same / tot_
    print(f"   {era:10s} " + "  ".join(f"{ms} {s:.0%}" for ms, s in c11[era].items()))
subprocess.run([sys.executable, os.path.join(ROOT, "code/analysis/ms_sound.py"), SBL, LXX, CN], capture_output=True, check=True)   # restore default output
C11 = all(s > 0.5 for era in ("koine-late", "koine") for s in c11[era].values())
print(f"   C11 rule (>50% under both Koine settings in every manuscript) -> {'HOLDS' if C11 else 'FAILS'};  attic mean {np.mean(list(c11['attic'].values())):.0%} vs koine-late mean {np.mean(list(c11['koine-late'].values())):.0%}")
R["C11"] = dict(holds=bool(C11), shares=c11)
# =========================================================== G
print("\nG: project-wide false-discovery correction over every p-value in DISCOVERIES.md")
txt = open(os.path.join(ROOT, "DISCOVERIES.md"), encoding="utf-8").read()
pat = re.compile(r"p\s*(?:=|<|≤|of)?\s*(<\s*)?(0?\.\d+|1\.0+)")
allp = []
for line in txt.splitlines():
    for m in pat.finditer(line):
        try: allp.append((float(m.group(2)), line))
        except ValueError: pass
ps = np.array([p for p, _ in allp]); m_ = len(ps); order = np.argsort(ps); thr = 0
for rank, i in enumerate(order, 1):
    if ps[i] <= 0.05 * rank / m_: thr = ps[i]
surv = [(p, l) for p, l in allp if p <= thr]
S_lines = [l for l in txt.splitlines() if re.search(r"\*\*S\b", l)]
S_ok = [l for l in S_lines if any(p <= thr for p, ll in allp if ll == l)]; S_nop = [l for l in S_lines if not any(ll == l for _, ll in allp)]
print(f"   {m_} p-values extracted; BH threshold at q 0.05 = {thr:.4f}; {len(surv)} survive")
print(f"   lines labelled S: {len(S_lines)}; with a surviving p {len(S_ok)}; with no p (lexical / descriptive claims) {len(S_nop)}; with p but none surviving {len(S_lines) - len(S_ok) - len(S_nop)}")
for l in S_lines:
    if l not in S_ok and l not in S_nop: print("      not surviving:", l.strip()[:150])
R["G"] = dict(n=m_, threshold=float(thr), survive=len(surv), S=len(S_lines), S_ok=len(S_ok), S_nop=len(S_nop), S_fail=[l.strip()[:200] for l in S_lines if l not in S_ok and l not in S_nop])
# G2: every p-value stored in any results file of the project (keys named p, p_*, *_p, pval), BH across all of them
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            kk = str(k).lower()
            if isinstance(v, (int, float)) and not isinstance(v, bool) and (kk == "p" or kk.startswith("p_") or kk.endswith("_p") or kk.startswith("pval")) and 0 <= v <= 1: yield path + "/" + str(k), float(v)
            else: yield from walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from walk(v, path + f"[{i}]")
pool = []
for f in sorted(glob.glob(os.path.join(ROOT, "code/analysis/*_results.json"))):
    try: pool += [(os.path.basename(f) + q, v) for q, v in walk(json.load(open(f, encoding="utf-8")))]
    except Exception: pass
pool += [(f"DISCOVERIES.md:{l[:60]}", p) for p, l in allp]
pp = np.array([v for _, v in pool]); M = len(pp); thr2 = 0
for rank, v in enumerate(np.sort(pp), 1):
    if v <= 0.05 * rank / M: thr2 = v
print(f"   G2: {M} p-values pooled from {len(glob.glob(os.path.join(ROOT, 'code/analysis/*_results.json')))} results files + DISCOVERIES; BH threshold q 0.05 = {thr2:.5f} (Bonferroni would be {0.05 / M:.6f})")
rep = open(os.path.join(ROOT, "REPORT.md"), encoding="utf-8").read(); solid = []
for line in rep.split("## 2.")[0].splitlines():
    m = re.match(r"\| (\d+) \| (.*?) \| (.*?) \|$", line)
    if not m: continue
    ps_ = [float(x) for x in re.findall(r"p[ =<≤]*([0-9]*\.[0-9]+)", m.group(2))]
    verdict = "no p (lexical/descriptive)" if not ps_ else ("survives" if min(ps_) <= thr2 else "does not survive")
    solid.append(dict(n=int(m.group(1)), claim=m.group(2)[:140], min_p=min(ps_) if ps_ else None, verdict=verdict))
for sx in sorted(solid, key=lambda z: z["n"]): print(f"      #{sx['n']:2d} {sx['verdict']:28s} {('p ' + str(sx['min_p'])) if sx['min_p'] is not None else '':10s} {sx['claim'][:90]}")
R["G2"] = dict(n=M, bh_threshold=float(thr2), bonferroni=0.05 / M, solid=solid)
# =========================================================== hashes
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
R["inputs_sha256_16"] = {os.path.basename(p): sha(p) for p in [glob.glob(os.path.join(SBL, f"*-{c}-*"))[0] for c in ("Jn", "Mk", "Mt", "Lk", "Ac")] + [os.path.join(WLC, "Gen.xml"), os.path.join(WLC, "Lev.xml"), os.path.join(WLC, "Song.xml"), os.path.join(LXX, "03.Leviticus.txt"), os.path.join(LXX, "31.Canticum.txt")]}
R["prereg_commit"] = "1a2d34d31d128b727a244dfefddc1e22e35397b3"
json.dump(R, open(os.path.join(HERE, "results.json"), "w"), ensure_ascii=False, indent=1, default=float)
