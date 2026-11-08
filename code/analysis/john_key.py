#!/usr/bin/env python3
"""John as a key: the seams inside John, and the decoding devices John himself gives the reader.

A. SEAMS (from order_tests.py) examined closely
   1. John 3:31-36: is it closer in wording to 3:1-21 (Jesus and Nicodemus) or to 3:22-30 (the Baptist)?
   2. Farewell discourse: wording similarity among 13:31-14:31, 15:1-16:4a, 16:4b-33, 17:1-26
      (is 16:4b-33 a second version of 14, as some scholars propose?).
   3. Pilate trial 18:28-19:16a: seven scenes alternating outside/inside the praetorium. Where does the
      scourging and crowning (19:1-3) fall in spoken time, and do scene lengths mirror?  The 13th-century
      chapter break 19:1 cuts through it.
   4. John 16:1: where is the real seam, 16:1 or 16:4b?
B. JOHN'S OWN DECODING DEVICES, counted against Matthew, Mark and Luke
   1. Translation glosses ('which is translated', hermeneuo / methermeneuo).
   2. Narrator asides that reveal a hidden meaning ('he said this about...', 'signifying by what death').
   3. Double-meaning words used in misunderstanding scenes.
   4. Numbers in the story: 153 fish (triangular number of 17; Hebrew letter values of En-gedi and
      En-eglaim, Ezekiel 47:10); 38 years (Deut 2:14); 46 years.
   5. The Genesis overlay: 'In the beginning'; the opening week; 'he breathed on them' (emphysao: only here in
      the NT; in the Greek OT at Gen 2:7 and a few other places); the garden.
   6. Pointer words: words used in the NT only by one Gospel, then found in the Greek OT. Which OT chapters
      does each Gospel's private vocabulary point to, and is John's pointing more focused?
Usage: python3 john_key.py <sblgnt dir> <lxx-swete/data>
"""
import collections, glob, json, math, os, random, re, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL, LXX = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(153); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
cache = {}
def syl(w):
    if w not in cache:
        try: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
        except Exception: cache[w] = 1
    return cache[w]
STOP = set("και δε ο η το του τησ των τω τη τον την τοισ ταισ οι αι τα εν εισ εκ απο προσ επι δια κατα μετα περι υπο παρα οτι ινα ου ουκ μη γαρ ουν αυτοσ αυτου αυτω αυτον αυτοισ αυτων εγω συ ημεισ υμεισ μου σου μοι σοι με σε ημων υμων ειμι εστιν ην ησαν ωσ".split())
NT = {}
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    code = os.path.basename(f).split("-")[1]
    NT[code] = [dict(ref=(int(l[2:4]), int(l[4:6])), text=l.split()[3], w=nrm(l.split()[4]), lem=nrm(l.split()[6])) for l in open(f, encoding="utf-8")]
JN = NT["Jn"]
def span(a, b, book=JN): return [t for t in book if a <= t["ref"] <= b]
def stems(ts): return collections.Counter(t["lem"][:7] for t in ts if t["lem"] not in STOP and len(t["lem"]) > 3)
def cos(A, B):
    n = sum(v * B.get(k, 0) for k, v in A.items())
    return n / (math.sqrt(sum(v * v for v in A.values())) * math.sqrt(sum(v * v for v in B.values())) + 1e-9)
def S(ts): return sum(syl(t["w"]) for t in ts if t["w"])

# ================================================================ A. seams
print("A1. JOHN 3:31-36: whose words are these?")
b31 = stems(span((3, 31), (3, 36))); nic = stems(span((3, 1), (3, 21))); bap = stems(span((3, 22), (3, 30)))
c_nic, c_bap = cos(b31, nic), cos(b31, bap)
# null: any 6-verse window in John vs the two blocks, to calibrate what a typical similarity is
verses = sorted({t["ref"] for t in JN}); wins = []
for i in range(0, len(verses) - 6, 3):
    a, b = verses[i], verses[i + 5]
    if (3, 1) <= a <= (3, 36) or (3, 1) <= b <= (3, 36): continue
    W = stems(span(a, b)); wins.append(cos(W, nic))
pct = sum(x < c_nic for x in wins) / len(wins)
shared = sorted(set(b31) & set(nic), key=lambda k: -b31[k])[:12]
print(f"   similarity to 3:1-21 = {c_nic:.3f}; to 3:22-30 = {c_bap:.3f}; 3:31-36 is closer to 3:1-21 than {pct:.0%} of other 6-verse passages of John")
print("   shared words with 3:1-21:", " ".join(shared))
out["john3"] = dict(to_nicodemus=round(c_nic, 3), to_baptist=round(c_bap, 3), percentile_vs_other_passages=round(pct, 3), shared=shared)

print("\nA2. FAREWELL DISCOURSE: wording similarity between its parts")
PARTS = {"13:31-14:31": ((13, 31), (14, 31)), "15:1-16:4a": ((15, 1), (16, 4)), "16:4b-33": ((16, 5), (16, 33)), "17": ((17, 1), (17, 26))}
st = {k: stems(span(*v)) for k, v in PARTS.items()}; mat = {}
for a in PARTS:
    mat[a] = {b: round(cos(st[a], st[b]), 3) for b in PARTS if b != a}
    print(f"   {a:12s} " + "  ".join(f"{b}: {v:.3f}" for b, v in mat[a].items()))
out["farewell"] = mat

print("\nA3. THE PILATE TRIAL (18:28-19:16a): seven scenes, outside / inside")
SC = [("1 outside: the accusers", (18, 28), (18, 32)), ("2 inside: 'Are you the king?'", (18, 33), (18, 38)),
      ("3 outside: 'I find no case', Barabbas", (18, 39), (18, 40)), ("4 inside: scourging, crown of thorns", (19, 1), (19, 3)),
      ("5 outside: 'Behold the man'", (19, 4), (19, 8)), ("6 inside: 'Where are you from?'", (19, 9), (19, 11)),
      ("7 outside: 'Behold your king', handed over", (19, 12), (19, 16))]
# scene 3 conventionally starts at 18:38b; scene 2 ends 18:38a.  Split verse 18:38 at 'καὶ τοῦτο εἰπὼν'.
trial = span((18, 28), (19, 16)); cut = next(i for i, t in enumerate(trial) if t["ref"] == (18, 38) and t["w"] == "τουτο")
lens = []
for k, (lab, a, b) in enumerate(SC):
    ts = [t for i, t in enumerate(trial) if a <= t["ref"] <= b]
    if k == 1: ts = [t for i, t in enumerate(trial) if a <= t["ref"] <= b and i < cut]
    if k == 2: ts = [t for i, t in enumerate(trial) if (18, 38) <= t["ref"] <= b and i >= cut]
    lens.append((lab, S(ts)))
T = sum(l for _, l in lens); acc = 0; pos = []
for lab, l in lens: pos.append((lab, l, round(acc / T, 3), round((acc + l) / T, 3))); acc += l
for lab, l, a, b in pos: print(f"   {lab:42s} {l:4d} syllables  spans {a:.3f}-{b:.3f}")
mirror = [(lens[i][1], lens[6 - i][1]) for i in range(3)]
print(f"   midpoint 0.500 falls in scene {next(k + 1 for k, (_, _, a, b) in enumerate(pos) if a <= .5 < b)}; mirrored scene lengths (1-7, 2-6, 3-5): {mirror}")
out["trial"] = dict(scenes=pos, mirror_pairs=mirror)

print("\nA4. JOHN 16:1 vs 16:4b: where does the wording turn?")
def seam_at(ref, n=120):
    idx = next(i for i, t in enumerate(JN) if t["ref"] >= ref)
    return round(1 - cos(stems(JN[max(0, idx - n):idx]), stems(JN[idx:idx + n])), 3)
for r in [(15, 18), (15, 26), (16, 1), (16, 4), (16, 5), (16, 16), (16, 25)]:
    print(f"   seam strength at {r[0]}:{r[1]:<3d} {seam_at(r)}")
out["seam_16"] = {f"{r[0]}:{r[1]}": seam_at(r) for r in [(15, 18), (15, 26), (16, 1), (16, 4), (16, 5), (16, 16), (16, 25)]}

# ================================================================ B. John's decoding devices
print("\nB1-2. JOHN'S OWN DECODING: translation glosses and narrator asides, per 10,000 words")
def find_seq(book, pat):
    ws = [t["w"] for t in book]; hits = []
    for i in range(len(ws)):
        if re.fullmatch(pat[0], ws[i]) and all(i + j < len(ws) and re.fullmatch(p, ws[i + j]) for j, p in enumerate(pat[1:], 1)): hits.append(book[i]["ref"])
    return hits
DEV = {"translation gloss (hermeneuo)": [[r"(μεθ)?ερμηνευ\w*"]],
       "'he said this about / signifying'": [[r"τουτο", r"δε", r"(ειπεν|ελεγεν)"], [r"σημαινων"]],
       "'he spoke about ...' (elegen peri / eirekei peri)": [[r"(ελεγεν|ειρηκει|ειπεν)", r"περι"]],
       "'his disciples did not understand / remembered'": [[r"εμνησθησαν"], [r"ουκ", r"εγνωσαν"], [r"ουκ", r"εγνωσαν"]]}
r_dev = {}
for lab, pats in DEV.items():
    row = {}
    for code in ("Mt", "Mk", "Lk", "Jn"):
        h = sorted({x for p in pats for x in find_seq(NT[code], p)}); row[code] = dict(n=len(h), per10k=round(1e4 * len(h) / len(NT[code]), 1), refs=[f"{a}:{b}" for a, b in h])
    r_dev[lab] = row
    print(f"   {lab:48s} " + "  ".join(f"{c} {row[c]['n']:2d} ({row[c]['per10k']:4.1f})" for c in row))
    print(f"      John: {', '.join(row['Jn']['refs'])}")
out["devices"] = r_dev

print("\nB3. DOUBLE-MEANING WORDS in John's misunderstanding scenes")
DM = {"ανωθεν": "again / from above (3:3, 3:7, 3:31, 19:11, 19:23)", "πνευμα": "wind / spirit (3:8)", "υψοω": "lifted up on the cross / exalted (3:14, 8:28, 12:32-34)",
      "ναοσ": "temple / his body (2:19-21)", "κοιμα": "sleep / death (11:11-13)", "ζαω": "living water / running water (4:10-11, 7:38)"}
r_dm = {}
for lem, gloss in DM.items():
    m = (lambda x: x.startswith(lem)) if lem == "κοιμα" else (lambda x: x == lem)
    refs = sorted({t["ref"] for t in JN if m(t["lem"])}); syn = sum(1 for c in ("Mt", "Mk", "Lk") for t in NT[c] if m(t["lem"]))
    r_dm[lem] = dict(gloss=gloss, john=len(refs), synoptics=syn); print(f"   {lem:8s} {gloss:58s} John {len(refs):2d} verses, Synoptics together {syn} uses")
out["double_meanings"] = r_dm

print("\nB4. NUMBERS IN THE STORY")
HEBV = dict(zip("אבגדהוזחטיכלמנסעפצקרשתךםןףץ", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 20, 40, 50, 80, 90]))
def gem(s): return sum(HEBV.get(c, 0) for c in s)
nums = dict(triangular_17=sum(range(1, 18)), gedi=gem("גדי"), eglaim=gem("עגלים"), en_gedi=gem("עין גדי"), en_eglaim=gem("עין עגלים"))
print(f"   153 = 1+2+...+17 = {nums['triangular_17']}.  Ezekiel 47:10 (river from the temple; fishermen 'from En-gedi to En-eglaim'):"
      f" Gedi = {nums['gedi']}, Eglaim = {nums['eglaim']}  (J. A. Emerton's 1958 proposal; 17 and 153)")
ez = [l.split(maxsplit=1)[1].strip() for l in open(glob.glob(os.path.join(LXX, "53.Ezechiel.txt"))[0], encoding="utf-8") if l.startswith("53.47.10 ")]
print("   Greek Ezekiel 47:10:", " ".join(ez))
print("   38 years ill (5:5) = Israel's 38 years in the wilderness (Deut 2:14); 46 years building the temple (2:20)")
out["numbers"] = nums

print("\nB5. THE GENESIS OVERLAY")
lxx_lines = []
for f in sorted(glob.glob(os.path.join(LXX, "*.txt"))):
    for l in open(f, encoding="utf-8"):
        p = l.split(maxsplit=1)
        if len(p) == 2: lxx_lines.append((os.path.basename(f)[3:-4] + " " + ".".join(p[0].split(".")[1:]), p[1].strip()))
emph_lxx = [r for r, w in lxx_lines if re.match(r"(εμφυσ|ενεφυσ|ενφυσ)", nrm(w)) and not nrm(w).startswith(("εμφυσιο", "ενεφυσιω"))]  # emphysioo (to instruct) is a different verb
emph_nt = [(c, t["ref"]) for c, b in NT.items() for t in b if t["lem"].startswith("εμφυσ")]
print("   'breathed into' (emphysao) in the NT:", emph_nt, " in the Greek OT:", emph_lxx)
days = [t["ref"] for t in span((1, 19), (2, 1)) if t["w"] in ("επαυριον",)] + [t["ref"] for t in span((2, 1), (2, 1)) if t["w"] == "τριτη"]
print("   opening week markers ('the next day' x3, 'on the third day'):", days, "-> day 1 (1:19), 2 (1:29), 3 (1:35), 4 (1:43), then 'the third day' (2:1) = day 6 or 7 by ancient inclusive counting")
kepos = {c: sorted({t["ref"] for t in NT[c] if t["lem"] == "κηποσ"}) for c in ("Mt", "Mk", "Lk", "Jn")}
print("   'garden' (kepos) in the passion and resurrection:", kepos)
gen13 = collections.Counter()
for r, w in lxx_lines:
    if r.startswith("Genesis ") and int(r.split()[1].split(".")[0]) <= 3:
        k = nrm(w)
        if k not in STOP and len(k) > 3: gen13[k[:5]] += 1
def gen_density(code): ws = [t["w"][:5] for t in NT[code] if t["w"] not in STOP and len(t["w"]) > 3]; return sum(1 for w in ws if w in gen13) / len(ws)
gd = {c: round(gen_density(c), 4) for c in ("Mt", "Mk", "Lk", "Jn")}
print("   share of each Gospel's content words that also occur in Genesis 1-3 (Greek):", gd)
out["genesis"] = dict(emphysao_nt=emph_nt, emphysao_lxx=emph_lxx, days=days, kepos=kepos, gen13_density=gd)

print("\nB6. POINTER WORDS: a Gospel's private vocabulary (used by no other NT book), traced into the Greek OT")
lemma_books = collections.defaultdict(set)
for c, b in NT.items():
    for t in b: lemma_books[t["lem"]].add(c)
lxx_stem = collections.defaultdict(list)
for r, w in lxx_lines:
    k = nrm(w)
    if len(k) > 4: lxx_stem[k[:6]].append(r.rsplit(".", 1)[0])
def pointers(code):
    priv = {t["lem"] for t in NT[code] if lemma_books[t["lem"]] == {code} and len(t["lem"]) > 4}
    tally = collections.Counter(); found = 0
    for lem in priv:
        locs = lxx_stem.get(lem[:6], [])
        if 0 < len(locs) <= 40:
            found += 1
            for ch, n in collections.Counter(locs).items(): tally[ch] += 1 / len(set(locs))
    return priv, found, tally
r6 = {}
for code in ("Mt", "Mk", "Lk", "Jn"):
    priv, found, tally = pointers(code); top = tally.most_common(8); tot = sum(tally.values())
    conc = sum(v for _, v in tally.most_common(10)) / tot if tot else 0
    r6[code] = dict(private_words=len(priv), traced=found, top=[(k, round(v, 2)) for k, v in top], top10_share=round(conc, 3))
    print(f"   {code}: {len(priv)} private words, {found} traceable to rare Greek-OT words; top-10 chapters hold {conc:.0%} of the pointing")
    print("      strongest:", ", ".join(f"{k} ({v:.1f})" for k, v in top))
out["pointers"] = r6
json.dump(out, open(os.path.join(HERE, "john_key_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
