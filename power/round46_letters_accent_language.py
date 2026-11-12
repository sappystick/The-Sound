#!/usr/bin/env python3
"""Round 46. (A) The four predictions of round 45, replayed with the LETTER mapping and the ACCENT melody.
(B) Which language were the power words, and the rest of the text, composed in?

A. Mappings onto the seven-string instrument (Nicomachus, round 41):
   letters - every written vowel letter is a note (alpha nete ... omega hypate); all seven strings sound.
   accent  - the ancient accent rule (round 43): accented syllable = paranete (c4), syllables before the accent = mese
             (a3), after it = lichanos (g3); a circumflex = paranete then mese.
   P1 mese share (John vs Synoptics); P2 do the four movements (cuts 1:16, 13:33, 18:1) differ in cadence string
   (chi-square vs 5,000 random cut sets); P3 middle 'I am' and middle sign at the book centre (units of the mapping);
   P4 'I am' verses cadence on the mese (binomial vs other verses).
B. Composition language. A sound-patterning score that works in any alphabet: for adjacent words, alliteration (same
   first consonant), rhyme (same last two letters) and shared consonant skeleton (>= 2 shared consonants), summed per
   verse and compared with the same verse's words shuffled (z per verse; 50 shuffles). The original composition
   should carry more patterning than a translation of it.
   Controls (original known): Hebrew Psalms (WLC) vs Greek Psalms (LXX, a translation); Greek Romans vs Syriac Romans.
   Test: Greek John vs Syriac John (Peshitta, ETCBC syrnt), overall and for the power sayings (verses with
   'amen amen' or 'ego eimi', plus 11:43, 19:30, 20:22) - a difference in differences.
Usage: python3 power/round46_letters_accent_language.py
"""
import glob, json, math, os, re, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
rng = np.random.default_rng(46); out = {}
def bare(t):
    t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if not unicodedata.combining(c)).replace("ς", "σ")
def verses(code):
    V = {}
    for l in open(glob.glob(os.path.join(ROOT, f"sources/texts/sblgnt/*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(p[3])
    return V
G = {c: verses(c) for c in ("Jn", "Mt", "Mk", "Lk")}
ORDER = list("ωυοιηεα"); NAME = dict(zip(ORDER, ["hypate", "parhypate", "lichanos", "mese", "trite", "paranete", "nete"]))
MESE = ORDER.index("ι"); PARANETE = ORDER.index("ε"); LICHANOS = ORDER.index("ο")
VOW = set("αεηιουω")

def seq_letters(words):
    return [ORDER.index(c) for w in words for c in re.sub(r"[^α-ω]", "", bare(w)) if c in VOW]
ACC = {}
def seq_accent(words):
    s = []
    for w in words:
        if w not in ACC:
            r = []
            for pw in E.parse_greek(w, "koine"):
                sy = [x for x in pw if x.get("nuc")]; acc = next((i for i, x in enumerate(sy) if x["accent"] in ("acute", "grave", "circ")), None)
                for i, x in enumerate(sy):
                    if acc is None or i < acc: r.append(MESE)
                    elif i == acc: r += [PARANETE, MESE] if x["accent"] == "circ" else [PARANETE]
                    else: r.append(LICHANOS)
            ACC[w] = r
        s += ACC[w]
    return s
MAPS = {"letters": seq_letters, "accent": seq_accent}
SIGNS = [(2, 9), (4, 50), (5, 8), (6, 11), (6, 19), (9, 7), (11, 43)]
IAM7 = [(6, 35), (8, 12), (10, 7), (10, 11), (11, 25), (14, 6), (15, 1)]
iam_refs = {ref for ref, ws in G["Jn"].items() for i in range(len(ws) - 1) if bare(ws[i]).strip(".,;·") == "εγω" and bare(ws[i + 1]).startswith("ειμι")}
res_A = {}
for mname, fn in MAPS.items():
    S = {c: {ref: fn(ws) for ref, ws in V.items()} for c, V in G.items()}
    p1 = {c: round(sum(x == MESE for s in v.values() for x in s) / sum(len(s) for s in v.values()), 4) for c, v in S.items()}
    allc = {c: np.bincount([x for s in v.values() for x in s], minlength=7) for c, v in S.items()}
    J = [(ref, s) for ref, s in S["Jn"].items() if s]; refs = [r for r, _ in J]; cad = np.array([s[-1] for _, s in J])
    def chi(cuts):
        b = [0] + list(cuts) + [len(J)]; tab = np.array([np.bincount(cad[b[i]:b[i + 1]], minlength=7) for i in range(4)], float)
        e = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum(); m = e > 0
        return float((((tab - e) ** 2)[m] / e[m]).sum()), tab
    o, tab = chi([refs.index((1, 16)), refs.index((13, 33)), refs.index((18, 1))])
    nl = np.array([chi(np.sort(rng.choice(np.arange(15, len(J) - 15), 3, replace=False)))[0] for _ in range(5000)])
    cum = np.cumsum([0] + [len(s) for _, s in J]); T = cum[-1]
    fr = lambda r: float((cum[refs.index(r)] + cum[refs.index(r) + 1]) / 2 / T)
    sims = np.sort(rng.random((200000, 7)), axis=1)[:, 3]
    mi, ms = fr(IAM7[3]), fr(SIGNS[3])
    isI = np.array([r in iam_refs for r in refs]); a = int((cad[isI] == MESE).sum()); n1 = int(isI.sum()); base = float((cad[~isI] == MESE).mean())
    p4 = sum(math.comb(n1, k) * base ** k * (1 - base) ** (n1 - k) for k in range(a, n1 + 1))
    res_A[mname] = dict(
        P1_mese_share=p1, P1_most_sounded_John=NAME[ORDER[int(allc["Jn"].argmax())]],
        P1_john_string_shares={NAME[ORDER[i]]: round(float(allc["Jn"][i] / allc["Jn"].sum()), 3) for i in range(7)},
        P2_chi2=round(o, 2), P2_p=round(float((nl >= o).mean()), 4),
        P2_cadence_of_movements=[NAME[ORDER[int(np.argmax(t))]] for t in tab],
        P2_mese_cadence_share_by_movement=[round(float(t[MESE] / t.sum()), 3) for t in tab],
        P3_middle_i_am=round(mi, 3), P3_p=round(float((np.abs(sims - .5) <= abs(mi - .5)).mean()), 3),
        P3_middle_sign=round(ms, 3), P3_sign_p=round(float((np.abs(sims - .5) <= abs(ms - .5)).mean()), 3),
        P4=dict(i_am_verses=n1, on_mese=a, base=round(base, 3), p=round(p4, 4)))
out["A_predictions"] = res_A

# ---------------------------------------------------------------- B. composition language
SYR_V = set("ܐܘܝ")  # matres lectionis treated as vowels/weak
def cons(w, script):
    if script == "greek": return re.sub(r"[αεηιουω]", "", w)
    if script == "hebrew": return re.sub(r"[אהוי]", "", w)
    return "".join(c for c in w if c not in SYR_V)
def pattern(words, script):
    s = 0
    for a, b in zip(words, words[1:]):
        ca, cb = cons(a, script), cons(b, script)
        if ca and cb and ca[0] == cb[0]: s += 1
        if len(a) > 2 and len(b) > 2 and a[-2:] == b[-2:]: s += 1
        if len(set(ca) & set(cb)) >= 2: s += 1
    return s
def zscores(vs, script, reps=50):
    z = {}
    for k, ws in vs.items():
        if len(ws) < 5: continue
        o = pattern(ws, script); nl = [pattern(list(rng.permutation(ws)), script) for _ in range(reps)]
        sd = np.std(nl); z[k] = (o - np.mean(nl)) / sd if sd > 0 else 0.0
    return z
def greek_vs(code): return {k: [re.sub(r"[^α-ω]", "", bare(w)) for w in v] for k, v in verses(code).items()}
def syriac_vs(book):
    V, ch = {}, 0
    for l in open(os.path.join(ROOT, f"sources/texts/syrnt/plain/0.1/{book}.txt"), encoding="utf-8"):
        l = l.strip(); m = re.match(r"^\S+ (\d+)$", l)
        if m and not re.match(r"^\d", l): ch = int(m.group(1)); continue
        m = re.match(r"^(\d+) (.*)$", l)
        if m and ch: V[(ch, int(m.group(1)))] = [re.sub(r"[^ܐ-ܯ]", "", w) for w in m.group(2).split() if re.sub(r"[^ܐ-ܯ]", "", w)]
    return V
def hebrew_vs(book):
    t = open(os.path.join(ROOT, f"sources/texts/morphhb/wlc/{book}.xml"), encoding="utf-8").read(); V = {}
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)">(.*?)</verse>', t, re.S):
        ws = [re.sub(r"[^א-ת]", "", re.sub(r"<[^>]+>", "", w)) for w in re.findall(r"<w[^>]*>(.*?)</w>", m.group(3))]
        V[(int(m.group(1)), int(m.group(2)))] = [w for w in ws if w]
    return V
def lxx_vs(name):
    V = {}
    for l in open(os.path.join(ROOT, f"sources/texts/lxx-swete/data/{name}.txt"), encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: r = p[0].split("."); V.setdefault((int(r[1]), int(r[2])), []).append(re.sub(r"[^α-ω]", "", bare(p[1])))
    return V
def mean_ci(z):
    a = np.array(list(z.values())); return round(float(a.mean()), 3), round(float(1.96 * a.std(ddof=1) / math.sqrt(len(a))), 3), len(a)
res_B = {}
zHPs, zGPs = zscores(hebrew_vs("Ps"), "hebrew"), zscores(lxx_vs("27.Psalmi"), "greek")
zGRo, zSRo = zscores(greek_vs("Ro"), "greek"), zscores(syriac_vs("Romans"), "syriac")
zGJn, zSJn = zscores(greek_vs("Jn"), "greek"), zscores(syriac_vs("John"), "syriac")
zGMk, zSMk = zscores(greek_vs("Mk"), "greek"), zscores(syriac_vs("Mark"), "syriac")
res_B["control_psalms"] = dict(hebrew_original=mean_ci(zHPs), greek_translation=mean_ci(zGPs))
res_B["control_romans"] = dict(greek_original=mean_ci(zGRo), syriac_translation=mean_ci(zSRo))
res_B["john"] = dict(greek=mean_ci(zGJn), syriac=mean_ci(zSJn))
res_B["mark"] = dict(greek=mean_ci(zGMk), syriac=mean_ci(zSMk))
JV = G["Jn"]
power = {r for r, ws in JV.items() for i in range(len(ws) - 1) if (bare(ws[i]).strip(".,;·") == "αμην" and bare(ws[i + 1]).strip(".,;·") == "αμην") or (bare(ws[i]).strip(".,;·") == "εγω" and bare(ws[i + 1]).startswith("ειμι"))} | {(11, 43), (19, 30), (20, 22)}
def did(zg, zs, keys):
    common = [k for k in zg if k in zs]; P = [k for k in common if k in keys]; O = [k for k in common if k not in keys]
    d = lambda K: np.array([zg[k] - zs[k] for k in K])
    dp, do = d(P), d(O); obs = dp.mean() - do.mean(); pool = np.concatenate([dp, do]); cnt = 0
    for _ in range(20000):
        rng.shuffle(pool); cnt += abs(pool[:len(dp)].mean() - pool[len(dp):].mean()) >= abs(obs)
    return dict(power_verses=len(P), greek_minus_syriac_power=round(float(dp.mean()), 3), greek_minus_syriac_other=round(float(do.mean()), 3),
                difference=round(float(obs), 3), p_two_sided=round((cnt + 1) / 20001, 4))
res_B["john_power_sayings_DiD"] = did(zGJn, zSJn, power)
mark_aram = {(5, 41), (7, 34), (14, 36), (15, 34)}
res_B["mark_aramaic_word_verses"] = {f"{a}:{b}": dict(greek=round(zGMk.get((a, b), float("nan")), 2), syriac=round(zSMk.get((a, b), float("nan")), 2)) for a, b in sorted(mark_aram)}
res_B["note"] = ("z = sound-patterning of adjacent words against the verse's own words shuffled. Higher in the original than in a translation "
                 "if the controls hold. The Peshitta is a later Syriac (Eastern Aramaic) translation, not Jesus' Galilean Aramaic.")
out["B_language"] = res_B
json.dump(out, open(os.path.join(HERE, "round46_results.json"), "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:6000])
