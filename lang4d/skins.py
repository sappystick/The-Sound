#!/usr/bin/env python3
"""Word skins: KANON spoken in everyday words of a natural language, with no change to the language itself.

Every KANON syllable is one cell of the 12 x 7 grid (consonant x vowel). A skin gives each cell a familiar word with
the same opening consonant and the same vowel sound, so the program "sa #7 gia ta #3 | di" can be said as
    "sat seven geese-at tap three stop deep".
The canonical form never changes: a skin is a reversible spelling, like a font. Any language can have its own skin
(as the BIP39 seed-word standard has word lists in ten languages); programs move between languages through the
canonical cells. Spelling variants that SOUND the same map to the same cell (meet/meat, no/know, sew/so), so a speech
recogniser's choice between them does not matter.

ENGLISH vowel classes (chosen so that no pair depends on a dialect merger such as cot/caught):
  a = the vowel of cat   e = bed   y = day   i = see   o = go   u = moon   w = law
Usage: python3 skins.py        (round-trip test on 2,000 random programs; prints the grid)"""
import json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import kanon as K
ENGLISH = {
 "cells": {   # consonant: words for the vowels a e y i o u w (in that order)
  "k": "cat keg cake key coat cool call", "t": "tap tell tape tea toe tune tall", "p": "pat pet pay pea pole pool paw",
  "b": "bat bed bay bee boat boot ball", "d": "dad deck day deep dough dew dawn", "g": "gap get gate geese goat goose gall",
  "l": "lab let lay leaf low loop law", "m": "map men may meet mow moon mall", "n": "nap net name need no new gnaw",
  "r": "rat red ray reed row room raw", "s": "sat set say seed so soup saw", "h": "hat hen hay heat hope hoop hawk"},
 "vowels": "at egg aim eat oak ooze awe",                       # a lone closing vowel
 "digits": "zero one two three four five six seven eight nine ten eleven",
 "marks": {"|": "stop", "!": "now", "?": "if", "~": "try", ":": "use", "::": "define", "::end": "done", "=": "check"},
 "aliases": {"kay": "cake", "tee": "tea", "pee": "pea", "be": "bee", "poll": "pole", "dew": "dew", "due": "dew", "do": "dew", "doe": "dough",
             "meat": "meet", "mo": "mow", "knew": "new", "gnu": "new", "know": "no", "nor": "gnaw", "read": "reed", "roe": "row", "rue": "room",
             "sew": "so", "sow": "so", "hey": "hay", "tow": "toe", "kale": "cake", "bae": "bay", "lei": "lay", "lo": "low", "lee": "leaf",
             "eat": "eat", "ate": "eight", "for": "four", "to": "two", "too": "two", "won": "one", "awe": "awe", "aw": "awe", "oh": "oak", "owe": "oak"},
}
def build(skin):
    enc, dec = {}, {}
    for c, words in skin["cells"].items():
        for v, w in zip(K.VOWELS, words.split()): enc[c + v] = w; dec[w] = c + v
    for v, w in zip(K.VOWELS, skin["vowels"].split()): enc["_" + v] = w; dec[w] = "_" + v
    for d, w in zip(K.DIGITS, skin["digits"].split()): enc["#" + d] = w; dec[w] = "#" + d
    for m, w in skin["marks"].items(): enc["!" + m] = w; dec[w] = "!" + m
    for a, t in skin["aliases"].items():
        if a not in dec and t in dec: dec[a] = dec[t]
    assert len(set(enc.values())) == len(enc), "two cells share a word"
    return enc, dec
EN_ENC, EN_DEC = build(ENGLISH)
def to_skin(src, enc=EN_ENC):
    """Canonical KANON -> skin words."""
    out = []
    for vi, verse in enumerate(K.norm_text(src).split("|")):
        if vi: out.append(enc["!|"])
        toks = verse.split(); k = 0
        while k < len(toks):
            tk = toks[k]
            if tk.startswith("#"): out += [enc["#" + d] for d in tk[1:]]
            elif tk == "::": out.append(enc["!::end"])
            elif tk == "=" or tk.startswith("="):
                rest = tk[1:] if len(tk) > 1 else ""; words = (rest.split("-") if rest else []) + (toks[k + 1:] if not rest else [])
                out.append(enc["!="]); out += ["-".join(_word(w, enc)) for w in words if w]; break
            else:
                m = re.fullmatch(r"(~?)(::|:)?([a-z]+)([!?]*)", tk)
                pre, col, w, post = m.groups()
                if pre: out.append(enc["!~"])
                if col: out.append(enc["!::"] if col == "::" else enc["!:"])
                out.append("-".join(_word(w, enc)))
                for ch in post: out.append(enc["!" + ch])
            k += 1
    return " ".join(out)
def _word(w, enc):
    parts = [enc[w[j:j + 2]] for j in range(0, len(w) - len(w) % 2, 2)]
    if len(w) % 2: parts.append(enc["_" + w[-1]])
    return parts
def from_skin(text, dec=EN_DEC):
    """Skin words -> canonical KANON. Unknown words raise an error naming the word."""
    verses, cur, num, pre, tail = [], [], None, "", None
    def flush_num():
        nonlocal num
        if num is not None: cur.append("#" + num); num = None
    for tok in text.lower().replace(",", " ").split():
        if tail is not None: tail.append("".join(_cell(p, dec) for p in tok.split("-"))); continue
        if tok in dec and dec[tok].startswith("#"): num = (num or "") + dec[tok][1:]; continue
        flush_num()
        if tok in dec and dec[tok].startswith("!"):
            m = dec[tok][1:]
            if m == "|": verses.append(" ".join(cur)); cur = []
            elif m in "!?": cur[-1] += m
            elif m == "~": pre += "~"
            elif m == ":": pre += ":"
            elif m == "::": pre += "::"
            elif m == "::end": cur.append("::")
            elif m == "=": tail = []
            continue
        cur.append(pre + "".join(_cell(p, dec) for p in tok.split("-"))); pre = ""
    flush_num()
    if tail is not None: cur.append("=" + "-".join(tail))
    verses.append(" ".join(cur))
    return " | ".join(v for v in verses)
def _cell(word, dec):
    if word not in dec: raise KeyError(f"'{word}' is not a word of this skin")
    c = dec[word]; return c[1:] if c.startswith("_") else c
if __name__ == "__main__":
    R = random.Random(9); bad = 0
    for _ in range(2000):
        p = K.random_program(R)
        if from_skin(to_skin(p)) != K.norm_text(p): bad += 1; print("MISMATCH", p, "|", to_skin(p))
    for p in ["sa #7 gia ta #3 | di", "demorini", "ki #70 | ka #30 | :kegi | :dasa"]:
        e = K.add_ecc(p); print(f"{p:32s} -> {to_skin(p)}\n{'':32s}    with error correction: {to_skin(e)}")
    print(f"round trip on 2,000 random programs: {2000 - bad} exact")
    print("\n      " + "  ".join(f"{v:6s}" for v in "a(cat) e(bed) y(day) i(see) o(go) u(moon) w(law)".split()))
    for c, ws in ENGLISH["cells"].items(): print(f"   {c}  " + "  ".join(f"{w:6s}" for w in ws.split()))
