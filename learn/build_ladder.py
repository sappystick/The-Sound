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
SBL, DOD, WLC = sys.argv[1:4]; STEPS = int(sys.argv[4]) if len(sys.argv) > 4 else 400; HERE = os.path.dirname(os.path.abspath(__file__))
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
            "εκεινοσ": "that one", "δυναμαι": "to be able", "θελω": "to want", "μενω": "to remain", "ζητεω": "to seek", "τηρεω": "to keep", "αγαπαω": "to love", "μαρτυρεω": "to testify", "ακολουθεω": "to follow",
            "ζαω": "to live", "αποθνησκω": "to die", "πεμπω": "to send", "αποστελλω": "to send out", "λαμβανω": "to take, receive", "ευρισκω": "to find", "ερωταω": "to ask", "αιτεω": "to ask for", "εξερχομαι": "to go out", "υπαγω": "to go away",
            "βλεπω": "to see, look", "θεωρεω": "to look at, behold", "εγειρω": "to raise", "κρινω": "to judge", "δοξαζω": "to glorify", "φιλεω": "to love (as a friend)", "πορευομαι": "to go", "ανιστημι": "to raise up, rise", "αναβαινω": "to go up", "καταβαινω": "to come down", "ζωη": "life", "μαθητησ": "disciple", "αποκρινομαι": "to answer", "ημεισ": "we", "υμεισ": "you (plural)", "περι": "about", "απο": "from", "δια": "through; because of", "ωσ": "as", "καθωσ": "just as"}
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
WHO = {("1", "S"): "I", ("2", "S"): "you", ("3", "S"): "he", ("1", "P"): "we", ("2", "P"): "you all", ("3", "P"): "they"}
PAST = {"say": "said", "come": "came", "see": "saw", "give": "gave", "go": "went", "do": "did", "make": "made", "know": "knew", "hear": "heard", "take": "took", "find": "found", "speak": "spoke", "have": "had",
        "become": "became", "send": "sent", "write": "wrote", "eat": "ate", "drink": "drank", "stand": "stood", "sit": "sat", "bring": "brought", "lead": "led", "keep": "kept", "leave": "left", "lay": "laid",
        "bear": "bore", "throw": "threw", "rise": "rose", "raise": "raised", "seek": "sought", "teach": "taught", "begin": "began", "fall": "fell", "draw": "drew", "put": "put", "let": "let", "cry": "cried", "carry": "carried",
        "lift": "lifted", "hand": "handed", "be": "was", "die": "died", "love": "loved", "believe": "believed", "live": "lived", "judge": "judged", "receive": "received", "glorify": "glorified", "testify": "testified",
        "crucify": "crucified", "baptize": "baptized", "worship": "worshipped", "stop": "stopped", "sin": "sinned", "run": "ran", "sell": "sold", "buy": "bought", "meet": "met", "feed": "fed", "wash": "washed", "open": "opened"}
PP = {"say": "said", "come": "come", "see": "seen", "give": "given", "go": "gone", "do": "done", "make": "made", "know": "known", "take": "taken", "speak": "spoken", "write": "written", "eat": "eaten", "become": "become", "be": "been"}
def inflect(base, kind):
    w = base.split(" "); v, rest = w[0], " ".join(w[1:]); j = lambda x: (x + " " + rest).strip()
    if v in ("am", "be") and kind != "base": return j({"3s": "is", "pl": "are", "1s": "am", "past": "was", "ing": "being", "pp": "been"}.get(kind, "be"))
    if kind == "3s": return j("has" if v == "have" else "does" if v == "do" else "goes" if v == "go" else v[:-1] + "ies" if v.endswith("y") and v[-2:-1] not in "aeiou" else v + ("es" if v.endswith(("s", "sh", "ch", "x")) else "s"))
    if kind == "past": return j(PAST.get(v, v + "d" if v.endswith("e") else v[:-1] + "ied" if v.endswith("y") and v[-2:-1] not in "aeiou" else v + "ed"))
    if kind == "pp": return j(PP.get(v, PAST.get(v, v + "d" if v.endswith("e") else v + "ed")))
    if kind == "ing": return j(v[:-1] + "ing" if v.endswith("e") and not v.endswith("ee") and v != "be" else v + "ing")
    return j("be" if v == "am" else v)
PRON = {("ἐγώ", "S"): {"N": "I", "G": "my", "D": "to me", "A": "me"}, ("ἐγώ", "P"): {"N": "we", "G": "our", "D": "to us", "A": "us"},
        ("σύ", "S"): {"N": "you", "G": "your", "D": "to you", "A": "you"}, ("σύ", "P"): {"N": "you all", "G": "your (all)", "D": "to you all", "A": "you all"}}
def form_gloss(t, clause):
    """A literal meaning of this exact form, for the whole-clause meaning line."""
    g = gloss(t["lem"], t["pos"]).split(",")[0].split(";")[0].strip(); pos, pa = t["pos"], t["parse"]
    if pos.startswith("V"):
        base = g[3:] if g.startswith("to ") else g
        if pa[3] == "N": return "to " + inflect(base, "base")
        if pa[3] == "P": return inflect(base, "ing")
        who = WHO.get((pa[0], pa[5]), ""); p3 = pa[0] == "3"; sg = pa[5] == "S"
        has_subj = any(u is not t and u["parse"][4] == "N" and u["pos"] != "RA" and ((p3 and u["lem"] not in ("ἐγώ", "σύ")) or (not p3 and u["lem"] in ("ἐγώ", "σύ"))) for u in clause)
        pre = "" if has_subj else who + " "
        if pa[3] == "D": return inflect(base, "base") + "!"
        if pa[3] == "S": return f"{pre}might {inflect(base, 'base')}"
        if pa[3] == "O": return f"{pre}may {inflect(base, 'base')}"
        be = base.split(" ")[0] in ("am", "be")
        if pa[1] == "P": return pre + (inflect(base, "1s") if be and who == "I" else inflect(base, "3s") if p3 and sg else inflect(base, "pl") if be else inflect(base, "base"))
        if pa[1] == "I": return pre + ("was " if sg and who != "you" else "were ") + inflect(base, "ing") if not be else pre + ("was" if sg and who != "you" else "were") + base[len(base.split(" ")[0]):]
        if pa[1] == "F": return f"{pre}will {inflect(base, 'base')}"
        if pa[1] == "A": return pre + (inflect(base, "past") if not be or sg else "were" + base[len(base.split(" ")[0]):])
        if pa[1] == "X": return pre + ("has " if p3 and sg else "have ") + inflect(base, "pp")
        if pa[1] == "Y": return f"{pre}had {inflect(base, 'pp')}"
        return pre + base
    if pos == "RA": return "the"
    if t["lem"] in ("ἐγώ", "σύ") and (t["lem"], pa[5]) in PRON: return PRON[(t["lem"], pa[5])].get(pa[4], g)
    if t["lem"] == "αὐτός" and pos == "RP":
        sgl = pa[5] == "S"; fem = pa[6] == "F"; neut = pa[6] == "N"
        return {"N": ("she" if fem else "it" if neut else "he") if sgl else "they", "G": ("her" if fem else "its" if neut else "his") if sgl else "their",
                "D": ("to her" if fem else "to it" if neut else "to him") if sgl else "to them", "A": ("her" if fem else "it" if neut else "him") if sgl else "them"}.get(pa[4], g)
    g = re.sub(r"^(a|an|the) ", "", g)
    if pos[0] in "NAR" and pa[4] == "G": return "of " + g
    if pos[0] in "NAR" and pa[4] == "D": return "to " + g
    return g
HOOKS = {"λέγω": "lexicon, dialogue", "ἐγώ": "ego", "θεός": "theology", "κόσμος": "cosmos, cosmic", "ἄνθρωπος": "anthropology", "φῶς": "photo, photon", "ζωή": "zoo, zoology", "ὕδωρ": "hydrant, hydro-", "ἀκούω": "acoustic",
         "γράφω": "graph, autograph", "πατήρ": "paternal, patriarch", "λόγος": "logic, -logy", "ἀλήθεια": "Alethea (the name: 'truth')", "ἀγαπάω": "agape", "ἀγάπη": "agape", "πιστεύω": "(pistis: faith) epistemology", "οὐρανός": "Uranus",
         "ἄρτος": "(artos) — bread; cf. 'artophorion'", "μαθητής": "mathematics (things learned)", "γινώσκω": "know, gnostic, diagnosis", "οἶδα": "idea, video (seeing = knowing)", "ὁράω": "panorama", "βλέπω": "—", "ἔργον": "energy, ergonomic",
         "δόξα": "doxology, orthodox", "ὄνομα": "synonym, anonymous", "μόνος": "mono-, monk", "πᾶς": "pan-, panorama", "πολύς": "poly-", "μέγας": "mega-", "μικρός": "micro-", "καλός": "calligraphy", "κακός": "cacophony",
         "ἅγιος": "hagiography", "πνεῦμα": "pneumatic, pneumonia", "σάρξ": "sarcophagus, sarcasm", "αἷμα": "haemoglobin", "ὀφθαλμός": "ophthalmology", "χείρ": "chiropractor", "πούς": "podium, octopus", "καρδία": "cardiac",
         "φωνή": "phone, phonetic", "γυνή": "gynaecology", "ἀνήρ": "android, Andrew", "υἱός": "—", "ἀδελφός": "Philadelphia (brother-love)", "φίλος": "philosophy, -phile", "φιλέω": "philosophy, -phile", "μισέω": "misanthrope",
         "ἀρχή": "archaic, archetype", "τέλος": "teleology", "ἡμέρα": "ephemeral (lasting a day)", "νύξ": "nocturnal (Latin cousin)", "ὥρα": "hour, horoscope", "τόπος": "topic, topography", "ὁδός": "odometer, exodus, method",
         "θύρα": "door (the same old word)", "ποιμήν": "—", "βασιλεύς": "basilica, Basil", "νόμος": "astronomy, economy", "ἱερόν": "hierarchy, hieroglyph", "δίδωμι": "dose, antidote", "λαμβάνω": "syllable (taken together)",
         "ἔρχομαι": "—", "πέμπω": "pomp (a sending, procession)", "ἀποστέλλω": "apostle", "μαρτυρέω": "martyr (witness)", "μαρτυρία": "martyr (witness)", "κρίνω": "critic, crisis", "κρίσις": "crisis", "σῴζω": "soteriology",
         "ζάω": "zoo", "ἀποθνῄσκω": "thanatology (thanatos: death)", "ἐγείρω": "Gregory ('watchful, awake')", "μένω": "remain, permanent (Latin cousin)", "τηρέω": "—", "αἰτέω": "—", "ζητέω": "—", "εὑρίσκω": "eureka!",
         "δύναμαι": "dynamic, dynamite", "θέλω": "—", "δεῖ": "—", "βαπτίζω": "baptize", "ἄγγελος": "angel (messenger)", "προφήτης": "prophet", "χριστός": "Christ (anointed)", "κύριος": "Kyrie", "ἐκκλησία": "ecclesiastical",
         "σημεῖον": "semaphore, semantic", "ψυχή": "psyche, psychology", "χαρά": "—", "εἰρήνη": "Irene, irenic", "χάρις": "charisma, eucharist", "ἀμήν": "amen", "ῥαββί": "rabbi", "εἷς": "(hen) henotheism", "δύο": "duo, dual",
         "τρεῖς": "three, triad", "πρῶτος": "prototype, protein", "ἔσχατος": "eschatology", "νέος": "neo-, new", "παλαιός": "palaeo-", "σοφία": "philosophy", "τέκνον": "—", "παιδίον": "paediatric", "οἶκος": "economy, ecology",
         "οἰκία": "economy, ecology", "πόλις": "metropolis, politics", "γῆ": "geology, geography", "θάλασσα": "thalassic", "ὄρος": "orography", "ποταμός": "hippopotamus (river-horse), Mesopotamia", "ἰχθύς": "ichthyology", "πρόβατον": "—",
         "ἄμπελος": "—", "καρπός": "carpology; harvest (cousin)", "σῶμα": "somatic, psychosomatic", "ἐν": "in (same word)", "ἐκ": "ex-, exit", "ἀπό": "apo-, apostle", "περί": "perimeter, periscope", "ὑπέρ": "hyper-", "ὑπό": "hypo-",
         "διά": "diameter, dialogue", "μετά": "meta-", "πρός": "prosthetic", "ἀντί": "anti-", "σύν": "syn-, sympathy", "κατά": "catalogue, catastrophe", "παρά": "parallel, paragraph", "ἐπί": "epicentre, epidemic"}
units, V = john_units(); lem_of = lambda u: [t["lem"] for t in u["toks"]]
freq = collections.Counter(t["lem"] for u in units for t in u["toks"]); total = sum(freq.values())
L = ladder(units, lem_of, max(STEPS, 600), freq)
def coverage(known):
    tok = sum(freq[x] for x in known) / total; cl = sum(all(x in known for x in lem_of(u)) for u in units); ve = sum(all(t["lem"] in known for t in toks) for toks in V.values()); return tok, cl, ve
known = set(); steps = []; curve = []
canon_new = []; _seen = set()
for u in units[:STEPS]: canon_new.append(len(set(lem_of(u)) - _seen)); _seen |= set(lem_of(u))
for n, (i, new, k) in enumerate(L):
    known |= set(new); tok, cl, ve = coverage(known); curve.append(dict(step=n + 1, lemmas=len(known), tokens=round(tok, 4), clauses=cl, verses=ve))
    if n < STEPS:
        u = units[i]
        steps.append(dict(n=n + 1, ref=u["ref"], new=new, mean=" ".join((lambda g, prev: g[3:] if g.startswith("to ") and prev is not None and prev["pos"].startswith("P") else g)(form_gloss(t, u["toks"]), u["toks"][j - 1] if j else None) for j, t in enumerate(u["toks"])), toks=[dict(w=t["raw"], lem=t["lem"], g=gloss(t["lem"], t["pos"]), role=role(t["pos"], t["parse"])[0], hint=role(t["pos"], t["parse"])[1], new=t["lem"] in new) for t in u["toks"]]))
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
for st_ in steps:
    for t in st_["toks"]:
        if t["new"] and HOOKS.get(t["lem"], "—") != "—": st_.setdefault("hooks", {})[t["lem"]] = HOOKS[t["lem"]]
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
