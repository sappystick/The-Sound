#!/usr/bin/env python3
"""Round 14: the three next steps on separation.

1. TEARING across the Gospels and the Septuagint: every tearing verb (schizo, (dia)rhegnymi, perirhegnymi) with
   what is torn, and every NEGATED tearing ('not tear').  The contrast: in Matthew and Mark the high priest tears
   his garments and the temple veil is torn; in John the tunic is not torn and the net is not torn.
2. SOUND of the schism verses (7:43, 9:16, 10:19) and the not-torn verses (19:24, 21:11): noise share of a
   5-verse window, percentile in John, with and without personal pronouns.
3. ORDER RETEST with the full families (fixed here, before running):
     separation = chorizo/schizo/skorpizo... used positively;   gathering/one = synago (not 'synagogue'), unity
     verses (10:16, 10:30, 11:52, 17:11, 17:21-23) and the NEGATED tearings (19:24, 21:11) = wholeness;
     completion = teleo / teleioo.
   Also run with the negated tearings counted as separation, to show the effect of that choice.
Usage: python3 round14.py <sblgnt> <lxx-swete/data>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, LXX = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(14); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
TEAR = ("σχιζ", "σχισ", "εσχισ", "σχισθ", "εσχισθ", "ρηγν", "ρηξ", "ερρηξ", "ερρηγ", "διαρρηγ", "διαρρηξ", "διερρηξ", "διερρηγ", "διερρησσ", "περιρρηξ", "ρηγνυ", "διαρρησσ", "σχισμ")
NEG = {"ου", "ουκ", "μη", "ουχ", "μηδε", "ουδε"}
NT = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]
    for l in open(f, encoding="utf-8"):
        p = l.split(); NT.setdefault((b, int(p[0][2:4]), int(p[0][4:6])), []).append((p[3], nrm(p[4])))
print("1. TEARING IN THE GOSPELS (verb, negated?, verse text)")
for k, toks in NT.items():
    if k[0] not in ("Mt", "Mk", "Lk", "Jn"): continue
    ws = [w for _, w in toks]
    for i, w in enumerate(ws):
        if w.startswith(TEAR):
            neg = any(x in NEG for x in ws[max(0, i - 3): i])
            print(f"   {k[0]:2s} {k[1]}:{k[2]:<3d} {'NOT torn' if neg else 'torn    '}  {' '.join(t for t, _ in toks)[:110]}")
LX = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    b = os.path.basename(f)[3:-4]
    if b.endswith("translatio_Graeca"): continue
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); LX.setdefault((b, r[1], r[2]), []).append(p[1].strip())
neg_lxx = []; n_tear = 0
for k, toks in LX.items():
    ws = [nrm(t) for t in toks]
    for i, w in enumerate(ws):
        if w.startswith(TEAR):
            n_tear += 1
            if any(x in NEG for x in ws[max(0, i - 3): i]): neg_lxx.append(f"{k[0]} {k[1]}:{k[2]}  {' '.join(toks)[:100]}")
print(f"\n   Septuagint: {n_tear} tearings, {len(neg_lxx)} negated:")
for x in neg_lxx: print("     ", x)
out["lxx_negated"] = neg_lxx

print("\n2. SOUND OF THE SCHISM AND NOT-TORN VERSES (percentile of the 5-verse window in John; low = quiet)")
OBS = {"p", "b", "t", "d", "k", "g", "pʰ", "tʰ", "kʰ", "f", "v", "θ", "ð", "s", "z", "x", "ɣ", "ç", "ʝ", "h", "ps", "ks", "β", "φ", "dz", "ts"}
PRON = set("εγω μου μοι με εμου εμοι εμε συ σου σοι σε ημεισ ημων ημιν ημασ υμεισ υμων υμιν υμασ".split())
cache = {}
def phon(raw):
    k = unicodedata.normalize("NFC", re.sub(r"[^\ẁ-ͯἀ-῿]", "", raw.lower()))
    if k not in cache:
        try: cache[k] = [p for s in E.parse_greek(k, "koine")[0] for p in s["ph"]]
        except Exception: cache[k] = []
    return cache[k]
jk = [k for k in NT if k[0] == "Jn"]
for drop in (False, True):
    o = np.array([sum(sum(x in OBS for x in phon(t)) for t, w in NT[k] if not (drop and w in PRON)) for k in jk], float)
    n = np.array([sum(len(phon(t)) for t, w in NT[k] if not (drop and w in PRON)) for k in jk], float)
    w5 = np.convolve(o, np.ones(5), "same") / np.maximum(np.convolve(n, np.ones(5), "same"), 1); pct = np.array([np.mean(w5 <= x) for x in w5])
    sel = {"schism 7:43": ("Jn", 7, 43), "schism 9:16": ("Jn", 9, 16), "schism 10:19": ("Jn", 10, 19), "not torn 19:24": ("Jn", 19, 24), "not torn 21:11": ("Jn", 21, 11)}
    print(f"   {'(pronouns removed) ' if drop else ''}" + "; ".join(f"{lab} {pct[jk.index(k)]:.2f}" for lab, k in sel.items()))
    sch = [jk.index(sel[x]) for x in sel if x.startswith("schism")]; real = pct[sch].mean()
    null = np.array([pct[rng.choice(len(jk), 3, replace=False)].mean() for _ in range(5000)])
    print(f"      the three schism verses together: mean percentile {real:.2f}; as noisy by chance p = {np.mean(null >= real):.3f}")

print("\n3. ORDER RETEST WITH THE FULL FAMILIES")
J = [(k[1], k[2], w) for k in jk for t, w in NT[k]]; total = len(J); pos = {}
for i, (c, v, w) in enumerate(J): pos.setdefault((c, v), i / total)
SEP = ("χωρισ", "σχισ", "εσχισ", "σκορπι", "εσκορπ", "διασκορπ", "διεσκορπ", "σχιζ")
GAT = ("συναγαγ", "συναγει", "συνηγαγ", "συναγουσ", "συνηχθ")
UNITY = {(10, 16), (10, 30), (11, 52), (17, 11), (17, 21), (17, 22), (17, 23)}; NEGT = {(19, 24), (21, 11)}
def events(neg_as):
    ev = []
    for (c, v), p in pos.items():
        ws = [w for cc, vv, w in J if (cc, vv) == (c, v)]
        if any(w.startswith(SEP) for w in ws): ev.append((p, neg_as if (c, v) in NEGT else 0))
        if any(w.startswith(GAT) for w in ws) or (c, v) in UNITY: ev.append((p, 1))
        if any(w.startswith(("τελεω", "τετελ", "τελειω", "τελεσ", "ετελει", "τελειωσ", "τετελειω", "τελεσω")) for w in ws): ev.append((p, 2))
    return sorted(ev)
def inv(x): return sum(1 for i in range(len(x)) for j in range(i + 1, len(x)) if x[i] > x[j])
for neg_as, lab in ((1, "not-torn counted as wholeness (pre-registered)"), (0, "not-torn counted as separation")):
    ev = events(neg_as); lab_ = np.array([f for _, f in ev]); real = inv(lab_); null = [inv(rng.permutation(lab_)) for _ in range(20000)]
    print(f"   {lab:48s} events {len(ev)}  inversions {real} (random median {int(np.median(null))})  p = {np.mean(np.array(null) <= real):.4f}")
    out[f"order_{neg_as}"] = dict(n=len(ev), inversions=real, p=float(np.mean(np.array(null) <= real)))
json.dump(out, open(os.path.join(HERE, "round14_results.json"), "w"), ensure_ascii=False, indent=1)
