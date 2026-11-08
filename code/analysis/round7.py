#!/usr/bin/env python3
"""Round 7: the numbered leads, plus era ciphers, each with a positive control.

1. CHAPTER-SCALE RESONANCE: John's chapters against every chapter of the Greek Bible. For chapter pairs linked
   by 4+ rare phrases, do positions inside the two chapters correspond (order rho), against verse-order shuffles?
   Control: 2 Samuel 22 ~ Psalm 17 (Greek numbering; = Psalm 18), the same poem.
2. GENESIS LEAD: does John's chapter order follow Genesis' chapter order through their shared rare phrases?
3. WITHIN-VERSE, FORMULAS REMOVED: the same-fraction-in-verse effect with the 300 commonest stems and all
   verbs of saying removed.
4. HEBREW POETRY CYCLES: repeating verse-length cycles in poetic books against narrative books
   (from verse_symmetry_results.json).
5. CIPHERS OF THE ERA:
   a. ATBASH (alef<->tav): control Sheshach = Babel (Jer 25:26; 51:41), Leb-kamai = Kasdim (Jer 51:1).
      Scan: Hebrew words whose atbash is a proper name/word found within 5 verses.
   b. GEMATRIA: 666 (Rev 13:18) = 'Nero Caesar' in Hebrew letters (nrwn qsr); 616 (variant reading) = 'nrw qsr'.
   c. ACROSTICS: control = the alphabetic psalms (verse-initial letters run in alphabet order).
      Scan: Greek NT runs of verse-initial letters spelling sacred names (IESOUS, CHRISTOS, LOGOS, ICHTHYS),
      with the chance of such runs.
Usage: python3 round7.py <sblgnt> <lxx-swete/data> <morphhb/wlc> <verse_symmetry_results.json>
"""
import collections, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC, VSR = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(7); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ εαν αν οσ ουτοσ τουτο παντα πασ".split())
V = collections.OrderedDict()                       # (book, ch, vs) -> words
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); V.setdefault((b, r[1], r[2]), []).append(nrm(p[1]))
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for l in open(f, encoding="utf-8"): V.setdefault((b, str(int(l[2:4])), str(int(l[4:6]))), []).append(nrm(l.split()[4]))
for k in V: V[k] = [w for w in V[k] if w]
freq = collections.Counter(w[:5] for ws in V.values() for w in ws)
COMMON = {s for s, _ in freq.most_common(300)}
SAY = ("ειπ", "λεγ", "ελεγ", "λαλ", "ελαλ", "φησ", "εφη")
def phrases(ws, strict=False):
    c = [(i, w[:5]) for i, w in enumerate(ws) if w not in STOP and len(w) > 3 and not (strict and (w[:5] in COMMON or w.startswith(SAY)))]
    return [((a, b), i / max(1, len(ws) - 1)) for (i, a), (j, b) in zip(c, c[1:]) if j - i <= 3]
occ = collections.defaultdict(list); occ_s = collections.defaultdict(list)
for k, ws in V.items():
    for ph, q in phrases(ws): occ[ph].append((k, q))
    for ph, q in phrases(ws, True): occ_s[ph].append((k, q))
rare = {ph: v for ph, v in occ.items() if 2 <= len(v) <= 12}
chap_verses = collections.defaultdict(list)
for k in V: chap_verses[(k[0], k[1])].append(k[2])
vidx = {(b, c, v): i for (b, c), vs in chap_verses.items() for i, v in enumerate(vs)}

# ---------------------------------------------------------------- 1
print("1. CHAPTER-SCALE RESONANCE")
links = collections.defaultdict(list)
for ph, v in rare.items():
    for x in range(len(v)):
        for y in range(x + 1, len(v)):
            (ka, qa), (kb, qb) = v[x], v[y]
            ca, cb = (ka[0], ka[1]), (kb[0], kb[1])
            if ca != cb: links[(ca, cb) if ca < cb else (cb, ca)].append(((vidx[ka] + qa) / len(chap_verses[ca]), (vidx[kb] + qb) / len(chap_verses[cb])) if ca < cb else ((vidx[kb] + qb) / len(chap_verses[cb]), (vidx[ka] + qa) / len(chap_verses[ca])))
def rho_test(pairs, ca, cb, R=500):
    a = np.array([x for x, _ in pairs]); b = np.array([y for _, y in pairs])
    if np.std(a) == 0 or np.std(b) == 0: return 0, 1
    r = np.corrcoef(a, b)[0, 1]; na, nb = len(chap_verses[ca]), len(chap_verses[cb]); hits = 0
    for _ in range(R):   # shuffle verse order inside both chapters
        pa = rng.permutation(na); pb = rng.permutation(nb)
        aa = (pa[np.minimum((a * na).astype(int), na - 1)] + (a * na) % 1) / na; bb = (pb[np.minimum((b * nb).astype(int), nb - 1)] + (b * nb) % 1) / nb
        if np.std(aa) > 0 and np.std(bb) > 0: hits += abs(np.corrcoef(aa, bb)[0, 1]) >= abs(r)
    return float(r), (hits + 1) / (R + 1)
ctrl = links.get((("Psalmi", "17"), ("Regnorum_II", "22")), [])
r, p = rho_test(ctrl, ("Psalmi", "17"), ("Regnorum_II", "22")); print(f"   control 2 Samuel 22 ~ Psalm 17(18): {len(ctrl)} phrase links, position rho {r:+.2f}, p = {p:.4f}")
res1 = []
for (ca, cb), pairs in links.items():
    if "Jn" in (ca[0], cb[0]) and ca[0] != cb[0] and len(pairs) >= 4:
        r, p = rho_test(pairs, ca, cb, 300); res1.append((p, r, len(pairs), ca, cb))
res1 = [(rho_test(links[(ca, cb) if ca < cb else (cb, ca)], ca, cb, 4000)[1] if p < 0.02 else p, r, n, ca, cb) for p, r, n, ca, cb in res1]   # refine small p-values
res1.sort(); m = len(res1); keep = res1[:max([i for i, x in enumerate(res1, 1) if x[0] <= 0.10 * i / m], default=0)]
print(f"   John chapter pairs tested: {m}; surviving correction: {len(keep)}")
for p, r, n, ca, cb in (keep or res1[:8]): print(f"      {ca[0]} {ca[1]} ~ {cb[0]} {cb[1]}  links {n}  rho {r:+.2f}  p {p:.4f}")
out["chapter_resonance"] = [(f"{a[0]} {a[1]}", f"{b[0]} {b[1]}", n, round(r, 3), p) for p, r, n, a, b in res1[:30]]

# ---------------------------------------------------------------- 2
print("\n2. GENESIS LEAD: does John's chapter order follow Genesis?")
jg = collections.Counter()
for (ca, cb), pairs in links.items():
    if {ca[0], cb[0]} == {"Jn", "Genesis"}:
        j, g = (ca, cb) if ca[0] == "Jn" else (cb, ca); jg[(int(j[1]), int(g[1]))] += len(pairs)
best = {j: max(((g, n) for (jj, g), n in jg.items() if jj == j), key=lambda x: x[1])[0] for j in range(1, 22) if any(jj == j for jj, _ in jg)}
js = sorted(best); gs = [best[j] for j in js]
rho = np.corrcoef(np.argsort(np.argsort(js)), np.argsort(np.argsort(gs)))[0, 1]
null = [np.corrcoef(np.argsort(np.argsort(js)), np.argsort(np.argsort(rng.permutation(gs))))[0, 1] for _ in range(5000)]
print(f"   John chapter -> best Genesis chapter: {dict(zip(js, gs))}")
print(f"   order correlation rho {rho:+.2f}; p = {np.mean(np.abs(null) >= abs(rho)):.3f}")
out["genesis"] = dict(map={int(k): int(v) for k, v in best.items()}, rho=float(rho))

# ---------------------------------------------------------------- 3
print("\n3. WITHIN-VERSE POSITION, FORMULAS REMOVED")
for lab, O in (("all rare phrases", occ), ("formulas removed", occ_s)):
    qa, qb = [], []
    for ph, v in O.items():
        if 2 <= len(v) <= 12:
            for x in range(len(v)):
                for y in range(x + 1, len(v)):
                    if v[x][0][0] != v[y][0][0]: qa.append(v[x][1]); qb.append(v[y][1])
    qa, qb = np.array(qa), np.array(qb); d = np.mean(abs(qa - qb)); nd = [np.mean(abs(qa - rng.permutation(qb))) for _ in range(200)]
    print(f"   {lab:18s} pairs {len(qa):6d}  mean |qA-qB| {d:.4f}  random {np.mean(nd):.4f}  p = {np.mean(np.array(nd) <= d):.3f}")
    out[f"micro_{lab}"] = [float(d), float(np.mean(nd))]

# ---------------------------------------------------------------- 4
print("\n4. HEBREW POETRY CYCLES (share of chapters with a repeating verse-length cycle, p < .05)")
vs = json.load(open(VSR))["OT"]
for lab, bks in (("poetry (Ps, Job, Prov, Song, Lam)", ("Ps", "Job", "Prov", "Song", "Lam")), ("prophets (Isa-Mal)", ("Isa", "Jer", "Ezek", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal")),
                 ("narrative (Gen-Kgs, Chr)", ("Gen", "Exod", "Num", "Josh", "Judg", "1Sam", "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr")), ("law/lists (Lev, Deut)", ("Lev", "Deut"))):
    rows = [v for k, v in vs.items() if k.split()[0] in bks]; k_ = sum(v["p_cycle"] < .05 for v in rows)
    per = collections.Counter(v["period"] for v in rows if v["p_cycle"] < .05)
    print(f"   {lab:34s} {k_:3d} of {len(rows):3d} = {k_ / len(rows):.1%} (chance 5%); periods {dict(per)}")

# ---------------------------------------------------------------- 5
print("\n5. CIPHERS OF THE ERA")
AL = "אבגדהוזחטיכלמנסעפצקרשת"; FIN = dict(zip("ךםןףץ", "כמנפצ"))
def cons(s): return "".join(FIN.get(c, c) for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת")
ATB = {a: b for a, b in zip(AL, AL[::-1])}
def atbash(w): return "".join(ATB[c] for c in w)
HV = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(WLC, "*.xml"))):
    bk = os.path.basename(f)[:-4]; x = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<verse osisID="([^"]+)">(.*?)</verse>', x, re.S):
        HV[m.group(1)] = [cons(p) for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2)) for p in [w.split("/")[-1]] if cons(p)]
print(f"   a. ATBASH control: atbash(ששך) = {atbash(cons('ששך'))} (Babel = בבל); atbash(לבקמי) = {atbash(cons('לבקמי'))} (Kasdim = כשדים)")
keys = list(HV); vocab = collections.Counter(w for ws in HV.values() for w in ws); hits = []
for i, k in enumerate(keys):
    near = set(w for kk in keys[max(0, i - 5): i + 6] for w in HV[kk])
    for w in set(HV[k]):
        if len(w) >= 3 and vocab[w] <= 3:
            a = atbash(w)
            if a != w and a in near and vocab[a] >= 2: hits.append((k, w, a))
print(f"   scan: rare words whose atbash form appears within 5 verses: {len(hits)}")
for k, w, a in hits[:15]: print(f"      {k:12s} {w} -> {a}")
# chance: same scan with a random letter substitution (a cipher nobody used)
perm = list(AL); rng.shuffle(perm); RND = dict(zip(AL, perm)); nh = 0
for i, k in enumerate(keys):
    near = set(w for kk in keys[max(0, i - 5): i + 6] for w in HV[kk])
    for w in set(HV[k]):
        if len(w) >= 3 and vocab[w] <= 3:
            a = "".join(RND[c] for c in w)
            if a != w and a in near and vocab[a] >= 2: nh += 1
print(f"   same scan with a random substitution cipher (control): {nh} hits")
out["atbash"] = dict(hits=hits, random_cipher_hits=nh)
GV = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400]))
g = lambda s: sum(GV[c] for c in s)
print(f"   b. GEMATRIA: nrwn qsr = {g('נרונקסר')} (Rev 13:18 '666'); nrw qsr = {g('נרוקסר')} (the variant '616' in some manuscripts, e.g. P115)")
print("   c. ACROSTICS control: alphabetic runs of verse-initial letters in the Hebrew Bible")
acro = []
for bk in sorted({k.split('.')[0] for k in keys}):
    chs = collections.defaultdict(list)
    for k in keys:
        if k.startswith(bk + "."): chs[k.split(".")[1]].append(HV[k][0][0] if HV[k] else "")
    for c, ini in chs.items():
        run = best_ = 0
        for x, y in zip(ini, ini[1:]):
            run = run + 1 if (x in AL and y in AL and AL.index(y) == AL.index(x) + 1) else 0; best_ = max(best_, run)
        if best_ >= 8: acro.append(f"{bk} {c} (run {best_ + 1})")
print(f"      chapters with 9+ verse initials in alphabet order: {acro}")
NAMES = {"ΙΗΣΟΥΣ": "ιησουσ", "ΧΡΙΣΤΟΣ": "χριστοσ", "ΛΟΓΟΣ": "λογοσ", "ΙΧΘΥΣ": "ιχθυσ", "ΘΕΟΣ": "θεοσ"}
ini = collections.defaultdict(str)
for k, ws in V.items():
    if k[0] in ("Mt", "Mk", "Lk", "Jn", "Ac", "Re") or len(k[0]) <= 3: ini[k[0]] += ws[0][0] if ws else ""
found = {n: [b for b, s in ini.items() if w in s] for n, w in NAMES.items()}
tot = sum(len(s) for s in ini.values()); f1 = collections.Counter("".join(ini.values()))
exp = {n: tot * np.prod([f1[c] / tot for c in w]) for n, w in NAMES.items()}
print("      Greek NT verse-initial letters spelling sacred names: " + "; ".join(f"{n}: {found[n] or 'none'} (expected by chance {exp[n]:.2f})" for n in NAMES))
out["acrostics"] = dict(hebrew=acro, greek={n: found[n] for n in NAMES}, expected={n: float(e) for n, e in exp.items()})
json.dump(out, open(os.path.join(HERE, "round7_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
