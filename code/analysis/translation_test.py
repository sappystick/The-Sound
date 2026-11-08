#!/usr/bin/env python3
"""Translation test: does the exact spoken centering of John 1:1-18 (and Philippians 2:6-11)
survive in the ancient translations?

Rule (fixed before running): the pivot is the first word of 1:12b ('he gave': Greek edoken,
Latin dedit, Sahidic af-ti, Syriac yab) and of Phil 2:9 (Greek dio, Latin propter, Sahidic etbe,
Syriac metul).  Its position is measured in each version's own spoken units:
  Greek  : syllables (engine's Koine reconstruction)        Latin  : syllables (vowel nuclei)
  Coptic : syllables (vowel nuclei; ou and ei count once)   Syriac : no vowels written -> letters and
                                                                     words only (proxy, flagged)
Also reported for every version: position by words.
If only the Greek lands on the exact midpoint while the translations drift, the balance lives in the
Greek sound rather than in the content.
Usage: python3 translation_test.py <sblgnt dir> <versions dir>
"""
import csv, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E

SBL, VER = sys.argv[1], sys.argv[2]


def greek(book_file, ch, v0, v1, pivot_v, pivot_lemma):
    words = []
    for line in open(os.path.join(SBL, book_file), encoding="utf-8"):
        p = line.split(); c, v = int(p[0][2:4]), int(p[0][4:])
        if c == ch and v0 <= v <= v1: words.append((v, p[4], p[6]))
    syl = [max(1, len(E.parse_greek(w, "koine")[0])) for _, w, _ in words]
    piv = next(i for i, (v, w, l) in enumerate(words) if v == pivot_v and l == pivot_lemma)
    return words, syl, piv


def latin_syl(w):
    w = w.lower().replace("qu", "q").replace("ae", "A").replace("oe", "A").replace("au", "A")
    w = re.sub(r"^i(?=[aeiou])", "j", w); w = re.sub(r"(?<=[aeiouA])i(?=[aeiouA])", "j", w)
    return max(1, len(re.findall(r"[aeiouyA]", w)))


def coptic_syl(w):
    w = w.replace("ⲟⲩ", "U").replace("ⲉⲓ", "I")
    n = len(re.findall("[ⲁⲉⲏⲓⲟⲩⲱUI]", w))
    return max(1, n)


def syriac_letters(w):
    return max(1, len(re.findall("[ܐ-ܯ]", w)))


def version(fname, book, ch, v0, v1, pivot_v, pivot_word_re, unit):
    rows = [r for r in csv.DictReader(open(os.path.join(VER, fname), encoding="utf-8"))
            if r["Book"] == book and int(r["Chapter"]) == ch and v0 <= int(r["Verse"]) <= v1]
    words = [(int(r["Verse"]), w) for r in rows for w in re.sub(r"[^\w\s]", " ", r["Text"]).split()]
    sizes = [unit(w) for _, w in words]
    piv = next(i for i, (v, w) in enumerate(words) if v == pivot_v and re.search(pivot_word_re, w))
    return words, sizes, piv


def pos(sizes, piv):
    before = sum(sizes[:piv]); tot = sum(sizes)
    return before / tot, before - tot / 2, tot


out = {}
TESTS = {
    "John 1:1-18": dict(g=("64-Jn-morphgnt.txt", 1, 1, 18, 12, "δίδωμι"), book="John", ch=1, v=(1, 18), pv=12,
                        lat=r"^dedit$", cop=r"^ⲁϥϯ$", syr=r"^ܝܗܒ$"),
    "Philippians 2:6-11": dict(g=("71-Php-morphgnt.txt", 2, 6, 11, 9, "διό"), book="Philippians", ch=2, v=(6, 11), pv=9,
                               lat=r"^propter$", cop=r"^ⲉⲧⲃⲉ$", syr=r"^ܡܛܠ$"),
}
for name, T in TESTS.items():
    print(f"\n{name}")
    gw, gs, gp = greek(*T["g"])
    res = {}
    for label, sizes, piv, n_words in (("Greek syllables", gs, gp, len(gw)), ("Greek words", [1] * len(gw), gp, len(gw))):
        f, off, tot = pos(sizes, piv); res[label] = dict(position=round(f, 4), offset_units=round(off, 1), total=tot)
        print(f"   {label:22s} pivot at {f:.4f}  ({off:+.1f} of {tot})")
    for label, fname, unit, rx in (("Latin syllables", "Vulgate.csv", latin_syl, T["lat"]),
                                   ("Coptic syllables", "CopSahBible2.csv", coptic_syl, T["cop"]),
                                   ("Syriac letters (proxy)", "Peshitta.csv", syriac_letters, T["syr"])):
        words, sizes, piv = version(fname, T["book"], T["ch"], *T["v"], T["pv"], rx, unit)
        for lab2, sz in ((label, sizes), (label.split()[0] + " words", [1] * len(words))):
            f, off, tot = pos(sz, piv); res[lab2] = dict(position=round(f, 4), offset_units=round(off, 1), total=tot)
            print(f"   {lab2:22s} pivot at {f:.4f}  ({off:+.1f} of {tot})")
    out[name] = res
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "translation_test_results.json"), "w"),
          ensure_ascii=False, indent=1)
