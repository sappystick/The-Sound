#!/usr/bin/env python3
"""A Greek quantity engine and dactylic-hexameter scanner.

Quantity rules (classical): a syllable is HEAVY if its vowel is long by nature (eta, omega, a diphthong, a circumflexed
vowel, iota subscript) or if it is followed by two consonants, counting across word boundaries (zeta, xi, psi count as two;
a stop + liquid/nasal may count either way). Epsilon and omicron are short; alpha, iota, upsilon without a circumflex are
ambiguous. A long vowel or diphthong before another vowel may be shortened (epic correption).  A diaeresis splits a
diphthong.  Elided vowels are dropped.
Hexameter: five feet, each a dactyl (- u u) or spondee (- -), then (- x).  Every line is matched against the 32 patterns;
the best pattern is the one with fewest rule violations.
Usage (validation): python3 scanner.py <Iliad grc xml> <Odyssey grc xml>
"""
import re, sys, unicodedata, itertools
V = set("αεηιουω"); DIPH = {"αι", "ει", "οι", "υι", "αυ", "ευ", "ου", "ηυ", "ωυ"}
STOPS = set("πβφτδθκγχ"); LIQ = set("λρμν")
def chars(text):
    """-> list of (letter, flags) with flags: circ, isub, diaer"""
    out = []
    for ch in unicodedata.normalize("NFD", text.lower()):
        if ch in "͂": out[-1][1].add("circ") if out else None
        elif ch == "ͅ": out[-1][1].add("isub") if out else None
        elif ch == "̈": out[-1][1].add("diaer") if out else None
        elif unicodedata.category(ch) == "Mn": continue
        elif "α" <= ch <= "ω" or ch == "ς": out.append(["σ" if ch == "ς" else ch, set()])
        elif ch in " \n": out.append([" ", set()])
    return out
def syllables(text):
    """Continuous syllable stream: list of dicts {nature: 'L'|'S'|'A', cons_after: n, ml: bool, hiatus: bool, wend: bool}"""
    text = re.sub(r"[ʼ’'᾽]", "", text)
    cs = chars(text); nuclei = []; i = 0
    while i < len(cs):
        c, f = cs[i]
        if c in V:
            nxt = cs[i + 1] if i + 1 < len(cs) else None
            if nxt and c + nxt[0] in DIPH and "diaer" not in nxt[1]:
                nat = "L"; j = i + 2
            else:
                nat = "L" if (c in "ηω" or "circ" in f or "isub" in f) else "S" if c in "εο" else ("L" if "circ" in f else "A"); j = i + 1
            nuclei.append([nat, i, j]); i = j
        else: i += 1
    syl = []
    for k, (nat, a, b) in enumerate(nuclei):
        end = nuclei[k + 1][1] if k + 1 < len(nuclei) else len(cs)
        between = [c for c, _ in cs[b:end]]; cons = [c for c in between if c != " "]
        n = sum(2 if c in "ζξψ" else 1 for c in cons)
        ml = len(cons) == 2 and cons[0] in STOPS and cons[1] in LIQ
        syl.append(dict(nature=nat, cons_after=n, ml=ml, hiatus=(n == 0), wend=(" " in between)))
    return syl
def heavy_possible(s): return s["nature"] in ("L", "A") or s["cons_after"] >= 2
def light_possible(s):
    if s["cons_after"] >= 2 and not s["ml"]: return False
    if s["nature"] == "L": return s["hiatus"]           # epic correption
    return True
PATTERNS = []
for feet in itertools.product("DS", repeat=5):
    p = []
    for ft in feet: p += ["L", "S", "S"] if ft == "D" else ["L", "L"]
    PATTERNS.append(("".join(feet), p + ["L", "X"]))
def scan(line):
    syl = syllables(line); best = None
    for name, pat in PATTERNS:
        if len(pat) != len(syl): continue
        v = sum(1 for s, q in zip(syl, pat) if (q == "L" and not heavy_possible(s)) or (q == "S" and not light_possible(s)))
        if best is None or v < best[1]: best = (name, v)
    return best, len(syl)
def prose_weights(text):
    """Heavy = 1, light = 0, ambiguous = 0.5, for prose (no metre)."""
    w = []
    for s in syllables(text):
        if s["cons_after"] >= 2 and not s["ml"]: w.append(1.0)
        elif s["nature"] == "L" and not s["hiatus"]: w.append(1.0)
        elif s["nature"] == "S": w.append(0.0)
        else: w.append(0.5)
    return w
if __name__ == "__main__":
    def lines(path):
        x = open(path, encoding="utf-8").read(); res = {}
        for m in re.finditer(r'<div (?:n="(\d+)" type="textpart" subtype="[Bb]ook"|type="textpart" subtype="[Bb]ook" n="(\d+)")>(.*?)(?=<div (?:n="\d+" type="textpart" subtype="[Bb]ook"|type="textpart" subtype="[Bb]ook" n="\d+")>|\Z)', x, re.S):
            bk = int(m.group(1) or m.group(2))
            for a, b in re.findall(r'<l n="(\d+)"[^>]*>(.*?)</l>', m.group(3), re.S): res[(bk, int(a))] = re.sub(r"<[^>]+>", "", b)
        return res
    Il, Od = lines(sys.argv[1]), lines(sys.argv[2])
    ok = tot = 0
    for k, l in Il.items():
        if k[0] > 3: continue
        (b, n) = scan(l); tot += 1; ok += bool(b and b[1] == 0)
    print(f"VALIDATION: Iliad 1-3, {tot} lines: scanned with zero violations {ok / tot:.1%}")
    for n in range(593, 601):
        b, ns = scan(Od[(11, n)]); print(f"   Odyssey 11.{n}: {b[0] if b else '-':6s} viol {b[1] if b else '-'}  ({ns} syll)  {Od[(11, n)][:60]}")
