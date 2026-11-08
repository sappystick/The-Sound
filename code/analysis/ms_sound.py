#!/usr/bin/env python3
"""Written for the ear: what the earliest manuscripts show.

1. HIGH-PRIEST VERSES in P66, P75, Sinaiticus (01) and Vaticanus (03): John 11:49-51 (Caiaphas 'high priest that
   year' prophesies), 18:13-16 ('known to the high priest'), 19:23-24 (the seamless tunic, 'let us not tear it'),
   21:11 ('the net was not torn').  Do the key words survive in every early witness?
2. HOMOPHONES. Using the sound engine's Koine pronunciation (stress ignored), which word forms in John sound exactly
   like a DIFFERENT word form found anywhere in the Greek Bible?  By category (we / you; o / omega mood endings...).
3. HEARD OR SEEN?  Every word where P66, P75, 01 or 03 differ from the critical text (SBLGNT) in John is classed as:
   (a) same sound, different spelling (an ear error or spelling habit); (b) same sound, a different REAL word
   (meaning changes, while the sound does not); (c) different sound (a sight error or a real variant).
   A high share of (a)+(b) means the text was handled through sound.
Usage: python3 ms_sound.py <sblgnt> <lxx-swete/data> <cntr 'class 1' dir>
"""
import collections, difflib, glob, json, os, re, sys, unicodedata
SBL, LXX, CN = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine")); import engine as E
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
cache = {}
def key(w, mode="koine-late"):
    if (w, mode) not in cache:
        try: cache[(w, mode)] = "".join(p for s in E.parse_greek(w, mode)[0] for p in s["ph"]).replace("ː", "")
        except Exception: cache[(w, mode)] = w
    return cache[(w, mode)]
NS = {"θσ": "θεοσ", "θυ": "θεου", "θν": "θεον", "θω": "θεω", "ισ": "ιησουσ", "ιυ": "ιησου", "ιν": "ιησουν", "κσ": "κυριοσ", "κυ": "κυριου", "κν": "κυριον", "κε": "κυριε",
      "χσ": "χριστοσ", "χυ": "χριστου", "χν": "χριστον", "πηρ": "πατηρ", "πρσ": "πατροσ", "πρα": "πατερα", "πρι": "πατρι", "περ": "πατερ", "πρ": "πατηρ", "υσ": "υιοσ",
      "υν": "υιον", "υυ": "υιου", "πνα": "πνευμα", "πνσ": "πνευματοσ", "ανοσ": "ανθρωποσ", "ανον": "ανθρωπον", "ανου": "ανθρωπου", "ανοι": "ανθρωποι", "ανων": "ανθρωπων", "ιηλ": "ισραηλ"}
def ms_verses(ms):
    vs = collections.OrderedDict()
    for line in open(os.path.join(CN, f"{ms}.txt"), encoding="utf-8"):
        m = re.match(r"^43(\d{3})(\d{3})\s+(.*)$", line.rstrip("\n"))
        if not m: continue
        raw = re.sub(r"x\{[^}]*\}", "", m.group(3)).replace("{", "").replace("}", "").replace("ϗ", "και").replace("¯", "ν")
        ws, complete = [], True
        for tok in raw.split():
            if "^" in tok or "%" in tok: complete = False          # letters missing or uncertain
            letters = re.sub(r"[^α-ως]", "", tok.replace("ς", "σ"))
            if letters: ws.append(NS.get(letters, letters) if "=" in tok else letters)
        vs[(int(m.group(1)), int(m.group(2)))] = (ws, complete, m.group(3))
    return vs
MS = {m: ms_verses(m) for m in ("P66", "P75", "01", "03")}
SB = collections.OrderedDict()
for l in open(os.path.join(SBL, "64-Jn-morphgnt.txt"), encoding="utf-8"):
    p = l.split(); SB.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(nrm(p[4]))

print("1. HIGH-PRIEST VERSES IN THE EARLIEST WITNESSES")
for ref, words in (((11, 49), ["αρχιερευσ", "ενιαυτου"]), ((11, 51), ["αφ", "εαυτου", "αρχιερευσ", "προεφητευσεν"]), ((18, 15), ["γνωστοσ", "αρχιερει"]),
                   ((19, 23), ["χιτων", "αραφοσ", "ανωθεν", "υφαντοσ"]), ((19, 24), ["σχισωμεν"]), ((21, 11), ["εσχισθη", "εκατον", "πεντηκοντα", "τριων"])):
    row = []
    for m, V in MS.items():
        if ref not in V: row.append(f"{m}: lacking"); continue
        ws, comp, raw = V[ref]; s = " ".join(ws)
        row.append(f"{m}: " + ", ".join(f"{w}{'✓' if w in s or w.replace('σ', '') in s else '✗'}" for w in words))
    print(f"   John {ref[0]}:{ref[1]:<3d} " + " | ".join(row))
    if ref == (21, 11):
        for m, V in MS.items():
            if ref in V: print(f"      {m} raw: {V[ref][2][:150]}")

print("\n2. HOMOPHONES IN JOHN (Koine pronunciation, stress ignored)")
vocab = set()
for f in glob.glob(os.path.join(LXX, "*.txt")):
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: vocab.update(nrm(t) for t in p[1].split())
for f in glob.glob(os.path.join(SBL, "*-morphgnt.txt")):
    for l in open(f, encoding="utf-8"): vocab.add(nrm(l.split()[4]))
vocab.discard("")
bykey = collections.defaultdict(set)
for w in vocab: bykey[key(w)].add(w)
jtok = [w for ws in SB.values() for w in ws]; homo = collections.Counter(); pairs = collections.Counter()
for w in jtok:
    others = bykey[key(w)] - {w}
    if others: homo[w] += 1; pairs[(w, min(others))] += 1
print(f"   {sum(homo.values())} of {len(jtok)} words in John ({sum(homo.values()) / len(jtok):.0%}) sound exactly like another word form")
cat = {"we / you (hēmeis / hymeis family)": lambda a, b: {a[:2], b[:2]} == {"ημ", "υμ"},
       "o / omega (indicative / subjunctive)": lambda a, b: a.replace("ω", "ο") == b.replace("ω", "ο"),
       "ei / i / ē (itacism)": lambda a, b: re.sub("ει|η", "ι", a) == re.sub("ει|η", "ι", b),
       "ai / e": lambda a, b: a.replace("αι", "ε") == b.replace("αι", "ε")}
for lab, f in cat.items():
    n = sum(c for (a, b), c in pairs.items() if f(a, b)); ex = [f"{a}/{b}" for (a, b), c in pairs.most_common(400) if f(a, b)][:6]
    print(f"   {lab:40s} {n:4d} tokens   e.g. {', '.join(ex)}")

print("\n3. HEARD OR SEEN? differences from SBLGNT in each witness (complete, legible verses only)")
res = {}
for m, V in MS.items():
    c = collections.Counter(); ex = collections.defaultdict(list)
    for ref, (ws, comp, raw) in V.items():
        if not comp or ref not in SB: continue
        sm = difflib.SequenceMatcher(a=SB[ref], b=ws, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "replace" or (i2 - i1) != (j2 - j1): continue
            for a, b in zip(SB[ref][i1:i2], ws[j1:j2]):
                if key(a) == key(b): k = "same sound, other REAL word" if b in vocab and b != a else "same sound, spelling only"
                else: k = "different sound"
                c[k] += 1
                if k == "same sound, other REAL word" and len(ex[k]) < 8: ex[k].append(f"{ref[0]}:{ref[1]} {a}->{b}")
    tot = sum(c.values()); res[m] = dict(c)
    print(f"   {m:4s} differing words {tot:5d}:  spelling-only {c['same sound, spelling only'] / max(tot, 1):.0%}   other real word, same sound {c['same sound, other REAL word'] / max(tot, 1):.0%}   different sound {c['different sound'] / max(tot, 1):.0%}")
    print(f"        same sound but a different word: {'; '.join(ex['same sound, other REAL word'])}")
out["variants"] = res
json.dump(out, open(os.path.join(HERE, "ms_sound_results.json"), "w"), ensure_ascii=False, indent=1)

print("\n4. MEANING-CHANGING SOUND-ALIKES IN THE MANUSCRIPTS (we/you swaps; person, mood or tense flipped by one vowel)")
flip = []
for m, V in MS.items():
    for ref, (ws, comp, raw) in V.items():
        if not comp or ref not in SB: continue
        sm = difflib.SequenceMatcher(a=SB[ref], b=ws, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "replace" and (i2 - i1) == (j2 - j1):
                for a, b in zip(SB[ref][i1:i2], ws[j1:j2]):
                    if key(a) == key(b) and a != b and ({a[:2], b[:2]} == {"ημ", "υμ"} or re.sub(r"(ε|αι)$", "", a) == re.sub(r"(ε|αι)$", "", b) and a[-2:] != b[-2:] and (a.endswith(("θε", "ετε", "σθαι", "σθε", "εται", "ετε")) or b.endswith(("θε", "ετε", "σθαι", "σθε", "εται"))) or (a.replace("ω", "ο") == b.replace("ω", "ο") and a.endswith(("ομεν", "ωμεν", "ητε", "ετε", "η", "ει")))):
                        flip.append((m, f"{ref[0]}:{ref[1]}", a, b))
wy = [f for f in flip if {f[2][:2], f[3][:2]} == {"ημ", "υμ"}]
print(f"   {len(flip)} meaning-flipping sound-alikes; we/you swaps: {len(wy)}")
for f in wy[:12]: print(f"      {f[0]:4s} John {f[1]:7s} {f[2]} -> {f[3]}")
out["flips"] = flip
json.dump(out, open(os.path.join(HERE, "ms_sound_results.json"), "w"), ensure_ascii=False, indent=1)
