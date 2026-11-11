#!/usr/bin/env python3
"""The Echo Ladder: order the real clauses of a text so that each step adds one new word to what the learner knows,
while known words keep returning at growing intervals.

Input: any corpus given as units (here: John's clauses, split at SBLGNT punctuation) of tokens with a lemma.
Algorithm (greedy, language-agnostic):
  known = {}.  Repeat: among unused units with the fewest unknown lemmas (ideally exactly 1), pick the one maximising
      log(frequency of the new lemma in the corpus)            -> useful words first
    + 0.3 * mean over its known lemmas of log(1 + steps since last met)   -> words due for review come back inside new text
    - 0.02 * length                                              -> short first
  and add its lemmas to `known`.
Outputs learn/ladder.json: the steps (tokens with gloss, grammar role, hint), and the measured curves:
  after each step: lemmas known, share of all word-tokens in the text recognised, clauses and verses fully readable.
Also prints the same ladder statistics for Hebrew Genesis (lemma = Strong number) to show the method is not Greek-specific.
Usage: python3 build_ladder.py <sblgnt dir> <dodson.csv> <morphhb wlc dir> [steps]
"""
import collections, csv, glob, json, math, os, re, sys, unicodedata
SBL, DOD, WLC = sys.argv[1:4]; STEPS = int(sys.argv[4]) if len(sys.argv) > 4 else 150; HERE = os.path.dirname(os.path.abspath(__file__))
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
# ---------------- lexicon (Dodson, public domain; beta code headwords)
BETA = dict(zip("abgdezhqiklmncoprstufxyw", "αβγδεζηθικλμνξοπρστυφχψω"))
LEX = {}
for r in csv.reader(open(DOD, encoding="utf-8"), delimiter="\t"):
    if len(r) < 4 or not r[0][:1].isdigit(): continue
    head = "".join(BETA.get(c, "") for c in r[2].split(",")[0].lower())
    if head and head not in LEX: LEX[head] = r[3].strip()
OVERRIDE = {"ο": "the", "και": "and", "αυτοσ": "he, she, it; self", "εγω": "I", "συ": "you", "ειμι": "to be", "λεγω": "to say", "οτι": "that; because", "εν": "in", "εισ": "into", "εκ": "out of, from",
            "ου": "not", "δε": "but, and", "ουτοσ": "this", "οσ": "who, which", "ινα": "so that", "μη": "not", "γαρ": "for", "ουν": "so, then", "προσ": "to, towards", "εαν": "if", "αλλα": "but", "τισ": "who? what?; someone",
            "ιησουσ": "Jesus", "θεοσ": "God", "πατηρ": "father", "εχω": "to have", "ερχομαι": "to come", "πιστευω": "to believe", "οιδα": "to know", "γινωσκω": "to know, come to know", "ποιεω": "to do, make",
            "κοσμοσ": "world", "γινομαι": "to become, happen", "διδωμι": "to give", "οραω": "to see", "λαλεω": "to speak", "ακουω": "to hear", "πασ": "all, every", "υιοσ": "son", "ανθρωποσ": "person, man",
            "εκεινοσ": "that one", "ζωη": "life", "μαθητησ": "disciple", "αποκρινομαι": "to answer", "ημεισ": "we", "υμεισ": "you (plural)", "περι": "about", "απο": "from", "δια": "through; because of", "ωσ": "as", "καθωσ": "just as"}
RAWOV = {"εἷς": "one", "ἤ": "or", "εἰ": "if", "ἄν": "would (marks possibility)", "οὗ": "where", "ὦ": "O!"}
def key(raw_lemma): return unicodedata.normalize("NFC", raw_lemma.lower())
def gloss(lem, pos=""):
    g = RAWOV.get(lem) or OVERRIDE.get(nrm(lem)) or LEX.get(nrm(lem)) or "?"
    if pos.startswith("V") and g.startswith("I "): g = "to " + g[2:]
    g = re.sub(r"\bI (?=[a-z])", "", g) if pos.startswith("V") else g
    return ", ".join(g.split(", ")[:3])
# ---------------- grammar role and hint from MorphGNT codes
PERS = {("1", "S"): "I", ("2", "S"): "you", ("3", "S"): "he/she/it", ("1", "P"): "we", ("2", "P"): "you all", ("3", "P"): "they"}
TENSE = {"P": "now", "I": "was …ing", "F": "will", "A": "did", "X": "has done", "Y": "had done"}
CASE = {"N": ("subject", "who does it"), "G": ("of", "of / from"), "D": ("to", "to / for / in"), "A": ("object", "what is acted on"), "V": ("address", "calling someone")}
def role(pos, parse):
    if pos.startswith("V"):
        m = parse[3]
        if m == "N": return "verb", "to … (infinitive)"
        if m == "P": return "verb", "…ing (participle" + (", " + CASE[parse[4]][0] if parse[4] in CASE else "") + ")"
        who = PERS.get((parse[0], parse[5]), ""); extra = {"D": "command", "S": "might / should", "O": "may (wish)"}.get(m, TENSE.get(parse[1], ""))
        return "verb", f"{who} · {extra}".strip(" ·")
    if parse[4] in CASE: return CASE[parse[4]][0], CASE[parse[4]][1] + (", plural" if parse[5] == "P" else "")
    return "link", {"C": "joining word", "P": "placing word (preposition)", "D": "how / when / where", "X": "small word", "I": "exclamation"}.get(pos[0], "")
# ---------------- units: clauses
def john_units():
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=re.sub(r"[⸀⸁⸂⸃⸄⸅()]", "", p[3]), lem=key(p[6]), pos=p[1], parse=p[2]))
    units = []
    for (c, v), toks in V.items():
        cur = []
        for t in toks:
            cur.append(t)
            if re.search(r"[,.;·]$", t["raw"]) and len(cur) >= 2: units.append(dict(ref=f"{c}:{v}", toks=cur)); cur = []
        if cur:
            if units and units[-1]["ref"] == f"{c}:{v}" and len(cur) < 2: units[-1]["toks"] += cur
            else: units.append(dict(ref=f"{c}:{v}", toks=cur))
    return units, V
def ladder(units, lemmas_of, steps, freq):
    known, last, used, out = set(), {}, set(), []; seen_text = set()
    for step in range(steps):
        best = None
        for i, u in enumerate(units):
            if i in used: continue
            L = lemmas_of(u); key = tuple(L)
            if key in seen_text or not (2 <= len(L) <= 9): continue
            new = [x for x in dict.fromkeys(L) if x not in known]
            if not new: continue
            kn = [x for x in set(L) if x in known]
            if not known and len(new) > 2: continue
            score = (0 if not known else -len(new), sum(math.log(freq[x]) for x in new) / len(new) + 0.3 * (sum(math.log(1 + step - last[x]) for x in kn) / len(kn) if kn else 0) - 0.02 * len(L))
            if best is None or score > best[0]: best = (score, i, new)
        if best is None: break
        _, i, new = best; used.add(i); seen_text.add(tuple(lemmas_of(units[i])))
        for x in set(lemmas_of(units[i])): last[x] = step
        known |= set(new); out.append((i, new, len(known)))
    return out
units, V = john_units(); lem_of = lambda u: [t["lem"] for t in u["toks"]]
freq = collections.Counter(t["lem"] for u in units for t in u["toks"]); total = sum(freq.values())
L = ladder(units, lem_of, max(STEPS, 400), freq)
def coverage(known):
    tok = sum(freq[x] for x in known) / total; cl = sum(all(x in known for x in lem_of(u)) for u in units); ve = sum(all(t["lem"] in known for t in toks) for toks in V.values()); return tok, cl, ve
known = set(); steps = []; curve = []
canon_new = [len({x for x in lem_of(u)} - set().union(*[set(lem_of(w)) for w in units[:i]])) if i else len(set(lem_of(u))) for i, u in enumerate(units[:400])]
for n, (i, new, k) in enumerate(L):
    known |= set(new); tok, cl, ve = coverage(known); curve.append(dict(step=n + 1, lemmas=len(known), tokens=round(tok, 4), clauses=cl, verses=ve))
    if n < STEPS:
        u = units[i]
        steps.append(dict(n=n + 1, ref=u["ref"], new=new, toks=[dict(w=t["raw"], lem=t["lem"], g=gloss(t["lem"], t["pos"]), role=role(t["pos"], t["parse"])[0], hint=role(t["pos"], t["parse"])[1], new=t["lem"] in new) for t in u["toks"]]))
print(f"JOHN: {len(units)} clauses, {total} words, {len(freq)} different words (lemmas)")
for n in (10, 25, 50, 100, 150, 250, 400):
    if n <= len(curve): c = curve[n - 1]; print(f"   after {n:3d} steps: {c['lemmas']:3d} words known -> recognises {c['tokens']:.0%} of all the words in John; {c['clauses']} clauses and {c['verses']} whole verses fully readable")
one = sum(len(new) == 1 for _, new, _ in L[:STEPS]); print(f"   steps adding exactly one new word: {one}/{STEPS};  reading John in its own order, the first {STEPS} clauses add {sum(canon_new[:STEPS]) / STEPS:.2f} new words each (ladder: {L[STEPS - 1][2] / STEPS:.2f})")
# natural review: how often each learned word returns later in the ladder
ret = collections.Counter(); first = {}
for n, (i, new, k) in enumerate(L[:STEPS]):
    for x in set(lem_of(units[i])):
        if x in first and first[x] != n: ret[x] += 1
        first.setdefault(x, n)
early = [x for x, s in first.items() if s < STEPS * 0.6]; print(f"   words learned in the first 60% of steps come back a median {sorted(ret[x] for x in early)[len(early) // 2]} more times inside later steps (review inside new text)")
# top-N frequency coverage (Zipf)
cum = 0; marks = {}
for r_, (x, c) in enumerate(freq.most_common(), 1):
    cum += c
    if r_ in (10, 50, 100, 200, 500): marks[r_] = cum / total
print("   the commonest words alone:", ", ".join(f"top {k} = {v:.0%}" for k, v in marks.items()))
json.dump(dict(steps=steps, curve=curve, total_words=total, total_lemmas=len(freq), clauses=len(units), verses=len(V), zipf=marks, canon_new=sum(canon_new[:STEPS]) / STEPS,
               distractors=sorted({gloss(x) for x, _ in freq.most_common(300) if gloss(x) != "?"})), open(os.path.join(HERE, "ladder.json"), "w"), ensure_ascii=False)
# ---------------- the same algorithm on Hebrew Genesis (no Greek-specific code)
x = open(os.path.join(WLC, "Gen.xml"), encoding="utf-8").read(); hu = []
for m in re.finditer(r'<verse osisID="Gen\.(\d+)\.(\d+)">(.*?)</verse>', x, re.S):
    ws = [re.sub(r"[^0-9]", "", l.split("/")[-1]) for l in re.findall(r'<w lemma="([^"]*)"', m.group(3))]; ws = [w for w in ws if w]
    for a in range(0, len(ws), 6): hu.append(ws[a:a + 6])
hf = collections.Counter(w for u in hu for w in u); ht = sum(hf.values()); HL = ladder(hu, lambda u: u, 150, hf); hk = set()
for i, new, k in HL: hk |= set(new)
print(f"HEBREW GENESIS (control, same algorithm): {len(hf)} lemmas; after 150 steps {len(hk)} words known -> {sum(hf[w] for w in hk) / ht:.0%} of all words recognised; one-new-word steps {sum(len(n) == 1 for _, n, _ in HL)}/150")
