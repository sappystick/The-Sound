#!/usr/bin/env python3
"""The earliest manuscripts themselves: P66, P75 (c. 200), Sinaiticus (01), Vaticanus (03), P46.
Transcriptions: Center for New Testament Restoration (Alan Bunning), CC BY-SA 4.0, MES markup:
   \\ page break   / line break   = sacred name (nomen sacrum)   ^ missing letter   x{..} uncorrected
Tests (rules fixed before running):
 1. Prologue centre in each manuscript's own wording: position of 'edoken' (1:12b) by spoken syllables
    (sacred names expanded, as they were read aloud), by letters as written, and by the scribe's lines.
 2. Philippians 2:6-11 centre ('dio', 2:9) in P46.
 3. The seven 'I am' sayings: ring around the midpoint of the whole Gospel in 01 and 03.
 4. Real sacred-name abbreviations: density by chapter, and where they fall in the prologue.
Usage: python3 papyri.py "<cntr>/class 1" [sblgnt dir]
"""
import collections, json, os, random, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E

CN = sys.argv[1]
NS = {"θσ": "θεοσ", "θυ": "θεου", "θν": "θεον", "θω": "θεω", "ισ": "ιησουσ", "ιυ": "ιησου", "ιν": "ιησουν", "ιη": "ιησου",
      "κσ": "κυριοσ", "κυ": "κυριου", "κν": "κυριον", "κε": "κυριε", "κω": "κυριω", "χσ": "χριστοσ", "χυ": "χριστου", "χν": "χριστον", "χω": "χριστω",
      "πηρ": "πατηρ", "πρσ": "πατροσ", "πρα": "πατερα", "πρι": "πατρι", "περ": "πατερ", "πρ": "πατηρ", "υσ": "υιοσ", "υν": "υιον", "υω": "υιω",
      "υυ": "υιου", "πνα": "πνευμα", "πνσ": "πνευματοσ", "πνι": "πνευματι", "πνοσ": "πνευματοσ", "πνει": "πνευματι", "ανοσ": "ανθρωποσ",
      "ανου": "ανθρωπου", "ανον": "ανθρωπον", "ανοι": "ανθρωποι", "ανων": "ανθρωπων", "ανοισ": "ανθρωποισ", "ανουσ": "ανθρωπουσ",
      "ανω": "ανθρωπω", "ιηλ": "ισραηλ", "δαδ": "δαυιδ", "ουνου": "ουρανου", "σωρ": "σωτηρ", "προσ": "πατροσ", "πρεσ": "πατερεσ"}


def load(ms, book):
    vs = collections.OrderedDict()
    for line in open(os.path.join(CN, f"{ms}.txt"), encoding="utf-8"):
        m = re.match(r"^(\d{2})(\d{3})(\d{3})\s+(.*)$", line.rstrip("\n"))
        if m and int(m.group(1)) == book: vs[(int(m.group(2)), int(m.group(3)))] = m.group(4)
    return vs


def clean_words(raw):
    """-> list of (spoken_word, written_letters, is_nomen_sacrum, line_breaks_before)"""
    raw = re.sub(r"x\{[^}]*\}", "", raw)                       # drop the uncorrected original reading
    raw = raw.replace("{", "").replace("}", "").replace("ϗ", "και").replace("¯", "ν")
    out = []
    for tok in raw.split():
        lb = tok.count("/") + tok.count("\\")
        ns = "=" in tok
        letters = re.sub(r"[^α-ως⳨]", "", tok.replace("ς", "σ"))
        if not letters:
            if out: out[-1] = (*out[-1][:3], out[-1][3]); continue
            continue
        spoken = letters
        if ns:
            key = letters.replace("⳨", "")
            spoken = "σταυρ" + key[1:] if "⳨" in letters else NS.get(key, letters)
        out.append((spoken, len(letters), ns, lb))
    return out


cache = {}
def syl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]


def seq(vs, first, last):
    rows = []
    for (c, v), raw in vs.items():
        if first <= (c, v) <= last:
            for w in clean_words(raw): rows.append(((c, v), *w))
    return rows


def where(rows, ref, pred):
    i = next(k for k, r in enumerate(rows) if r[0] == ref and pred(r[1]))
    S = [syl(r[1]) for r in rows]; L = [r[2] for r in rows]
    lines_before = sum(r[4] for r in rows[:i + 1]); lines_tot = sum(r[4] for r in rows)
    return dict(syllables=round(sum(S[:i]) / sum(S), 4), syl_offset=round(sum(S[:i]) - sum(S) / 2, 1), syl_total=sum(S),
                letters=round(sum(L[:i]) / sum(L), 4), letters_total=sum(L),
                lines=round(lines_before / lines_tot, 4) if lines_tot else None, lines_total=lines_tot)


out = {}
print("1. Prologue centre (pivot 'edoken', 1:12b) in the manuscripts' own wording")
for ms in ("P66", "P75", "01", "03"):
    vs = load(ms, 43); rows = seq(vs, (1, 1), (1, 18))
    try: r = where(rows, (1, 12), lambda w: w.startswith("εδωκ"))
    except StopIteration: print(f"   {ms}: pivot not legible"); continue
    out[f"prologue_{ms}"] = r
    print(f"   {ms:4s} syllables {r['syllables']:.4f} ({r['syl_offset']:+.1f} of {r['syl_total']})   letters as written {r['letters']:.4f}"
          f"   scribe's lines {r['lines']} of {r['lines_total']}")

print("\n2. Philippians 2:6-11 in P46 (pivot 'dio', 2:9)")
for ms in ("P46", "01", "03"):
    vs = load(ms, 50); rows = seq(vs, (2, 6), (2, 11))
    try: r = where(rows, (2, 9), lambda w: w.startswith("διο")); out[f"philippians_{ms}"] = r
    except StopIteration: print(f"   {ms}: not found"); continue
    print(f"   {ms:4s} syllables {r['syllables']:.4f} ({r['syl_offset']:+.1f} of {r['syl_total']})   letters {r['letters']:.4f}")

print("\n3. 'I am' ring in the complete Gospels (01, 03)")
SAY = [(6, 35), (8, 12), (10, 7), (10, 11), (11, 25), (14, 6), (15, 1)]
def sym_err(ps): return sum(abs((ps[i] - .5) + (ps[6 - i] - .5)) for i in range(3))
rng = random.Random(11)
for ms in ("01", "03"):
    vs = load(ms, 43); rows = seq(vs, (1, 1), (21, 25))
    S = [syl(r[1]) for r in rows]; L = [r[2] for r in rows]; cumS, cumL = [0], [0]
    for s_, l_ in zip(S, L): cumS.append(cumS[-1] + s_); cumL.append(cumL[-1] + l_)
    first = {}
    for k, r in enumerate(rows): first.setdefault(r[0], k)
    for unit, cum in (("syllables", cumS), ("letters", cumL)):
        ps = sorted(cum[first[k]] / cum[-1] for k in SAY); e = sym_err(ps)
        p = sum(sym_err(sorted(rng.random() for _ in range(7))) <= e for _ in range(50000)) / 50000
        out[f"ring_{ms}_{unit}"] = dict(middle=round(ps[3], 3), error=round(e, 3), p=p)
        print(f"   {ms} by {unit:9s}: middle saying at {ps[3]:.3f}, ring error {e:.3f}, p = {p:.3f}")

print("\n4. Sacred-name abbreviations as written")
for ms in ("P66", "01", "03"):
    vs = load(ms, 43); rows = seq(vs, (1, 1), (21, 25))
    ch_w = collections.Counter(r[0][0] for r in rows); ch_n = collections.Counter(r[0][0] for r in rows if r[3])
    tot = sum(ch_n.values()) / len(rows)
    prol = [(f"{r[0][0]}:{r[0][1]}", r[1]) for r in rows if r[0][0] == 1 and r[0][1] <= 18 and r[3]]
    out[f"nomina_{ms}"] = dict(share=round(tot, 4), by_chapter={c: round(ch_n[c] / ch_w[c], 3) for c in sorted(ch_w)}, prologue=prol)
    print(f"   {ms}: {sum(ch_n.values())} of {len(rows)} words ({tot:.1%}); prologue: {prol}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "papyri_results.json"), "w"), ensure_ascii=False, indent=1)
