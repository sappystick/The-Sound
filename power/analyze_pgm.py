#!/usr/bin/env python3
"""The Greek Magical Papyri (Betz, English translation, scan supplied by the user) analysed for instructions and codes.
The translation is under copyright: only counts, structure, the ancient magical words themselves and short quotations
are kept (power/pgm_results.json). The scan's text layer loses vowel-length marks (E for both epsilon and eta, O for
omicron and omega), so letter values are computed only from standard Greek spellings of well-known names.

A  WHAT THE SPELLS ARE FOR: the table of contents (about 580 spells) classified by stated purpose.
B  SOUND AND BREATH INSTRUCTIONS: every passage that tells the user to make a sound or use the breath (hiss, pop, bellow,
   whistle, groan, breathe in, sing the vowels, shout ...), with the spell it belongs to.
C  THINGS TO MAKE: rings, metal leaves (lamellae), figurines, lamps, inks, stones; how often each is prescribed.
D  THE MAGICAL WORDS: the most frequent names; vowel strings (length, arrangement); palindromes.
E  NUMBER CODES: passages that state a number for a name; letter values (isopsephy) of key names from their Greek spelling.
Usage: python3 -I analyze_pgm.py <pgm text> <out json>
"""
import collections, json, re, sys
T = open(sys.argv[1], encoding="utf-8", errors="replace").read(); OUT = sys.argv[2]; R = {}
# ---------------------------------------------------------------- A
toc = []
seen = set()
for m in re.finditer(r"^\s*(PGM|PDM|PGM/PDM)\s+([A-Za-z0-9]+)\.\s*([\d][\d\-–, ]*)\s{2,}(\S{2,10})\s{2,}(.+)$", T[:150000], re.M):
    key = (m.group(1), m.group(2), m.group(3).strip())
    if key in seen: continue
    seen.add(key); toc.append(dict(ref=f"{m.group(1)} {m.group(2)}. {m.group(3).strip()}", title=m.group(5).strip()))
CATS = [("healing", r"headache|migraine|fever|cough|eye|ophthalm|scorpion|sting|bite|gout|bleed|womb|childbirth|swelling|inflammation|ache|disease|ill|sick|healing|cure|epilep|jaundice|tumor|wound|tooth|stomach|breast"),
        ("love and attraction", r"love|attraction|erotic|passion|affection"), ("revelation, dreams, visions", r"dream|revelation|oracle|vision|divination|direct vision|foreknowledge|prophec|lamp divination|bowl"),
        ("protection", r"phylacter|protect|amulet|guard|against .*demon|exorcis|demon"), ("binding and restraint", r"binding|restrain|curse|silenc|subject|to bind"),
        ("success and favour", r"success|favor|favour|victory|business|charm for|win"), ("immortality and ascent", r"immortal|ascent|mithras|initiat|consecrat"),
        ("power over nature or objects", r"invisib|open(ing)? doors?|fire|release from bonds|chains|stop|walk|boat|levitat|to make .* move|to make .* appear"),
        ("assistant spirit", r"assistant|paredr|daimon"), ("sleep and insomnia", r"sleep|insomnia")]
def cat(title):
    t = title.lower(); return [c for c, p in CATS if re.search(p, t)] or ["other or untitled"]
cc = collections.Counter(c for x in toc for c in cat(x["title"]))
R["A_purposes"] = dict(spells=len(toc), counts=cc.most_common(), healing=[x for x in toc if "healing" in cat(x["title"])][:60],
                       nature=[x for x in toc if "power over nature or objects" in cat(x["title"])])
# ---------------------------------------------------------------- spell locator for body text
heads = [(m.start(), m.group(1).replace("111", "III").replace("1", "I").replace("l", "I"), m.group(2)) for m in re.finditer(r"PGM\s*([IVXLCl1]+)\.\s*(\d+)", T)]
def spell_at(pos):
    k = None
    for h in heads:
        if h[0] <= pos: k = h
        else: break
    return f"PGM {k[1]}. {k[2]}" if k else "?"
body = T[120000:]
def ctx(m, w=160): s = max(0, m.start() - w); return re.sub(r"\s+", " ", body[s: m.end() + w]).strip()
# ---------------------------------------------------------------- B
SOUND = {"hiss": r"\bhiss\w*", "pop / smack": r"\bpop(?:ping|s)?\b|smack\w*", "bellow / roar": r"\bbellow\w*|\broar\w*", "whistle": r"\bwhistl\w*", "groan / moan": r"\bgroan\w*|\bmoan\w*",
         "breathe in / out": r"draw in breath|draw (?:up )?breath|inhal\w*|exhal\w*|breathe (?:in|out)|holding (?:your|the) breath|blow\w* (?:on|into|three|seven)", "shout / cry aloud": r"\bshout\w*|cry (?:out|aloud)|loud voice",
         "whisper / silence": r"\bwhisper\w*|\bsilence\b|keep silent", "sing / chant / hymn": r"\bsing\b|\bchant\w*|\bhymn\w*", "the vowels": r"\bvowels?\b", "instrument": r"\blyre\b|\bsistrum\b|\bflute\b|\btrumpet\b|\bcymbal\w*|\bdrum\b|\bpipe\b",
         "facing a direction": r"facing (?:the )?(?:east|west|north|south|sun|moon)|to the (?:east|west|north|south)"}
sb = {}
for k, p in SOUND.items():
    ms = list(re.finditer(p, body, re.I)); sb[k] = dict(count=len(ms), spells=sorted({spell_at(120000 + m.start()) for m in ms})[:40], examples=[dict(spell=spell_at(120000 + m.start()), text=ctx(m)) for m in ms[:3]])
R["B_sound"] = sb
# ---------------------------------------------------------------- C
MAKE = {"ring": r"\bring\b", "metal leaf (lamella)": r"\blamella|\bleaf of (?:gold|silver|tin|lead|copper)|\bsheet of (?:gold|silver|tin|lead)|\bplate of (?:gold|silver|tin|lead)|\btin (?:leaf|lamella|tablet)|\blead (?:leaf|lamella|tablet)",
        "stone / gem": r"\bstone\b|\bgem\b|\bjasper\b|\bmagnet\w*|\bheliotrope\b|\bcarnelian\b|\bhaematite\b|\bhematite\b", "figurine": r"\bfigure\b|\bfigurine\b|\bstatue\b|\bimage of\b",
        "lamp": r"\blamp\b", "ink (myrrh, blood)": r"\bink\b|myrrh ink|blood of", "papyrus / writing": r"\bpapyrus\b|\bwrite\b", "bowl / cup / water": r"\bbowl\b|\bcup\b|\bvessel\b", "herb / plant": r"\bherb\b|\bplant\b|\broot\b|\bleaves\b",
        "animal part": r"\bcock\b|\bhawk\b|\bfalcon\b|\bdonkey\b|\bass\b|\bdog\b|\bbeetle\b|\bscarab\b|\bsnake\b|\blizard\b", "string / thread / cord": r"\bthread\b|\bcord\b|\bstring\b", "seven / number of times": r"\bseven times\b|\bthree times\b|\bnine times\b"}
R["C_make"] = {k: len(re.findall(p, body, re.I)) for k, p in MAKE.items()}
# ---------------------------------------------------------------- D
EN = set(open("/usr/share/dict/words").read().upper().split()) if __import__("os").path.exists("/usr/share/dict/words") else set()
EN |= set("PGM PDM LSJ ZPE PRE RAC CHI CHA SMA TAT EPRO AII NOTE THE AND FOR WITH FROM THIS THAT YOUR SPELL WRITE SAY GODS LORD CPR BASP ARW JEA JNES RAC GMPT".split())
caps = [w.replace("l", "I") for w in re.findall(r"\b[A-ZĒŌ][A-ZĒŌl]{2,}\b", body)]
caps = [w for w in caps if w not in EN and not re.fullmatch(r"[IVXLC]+", w) and not w.startswith("PGM")]
freq = collections.Counter(caps); R["D_names_top"] = freq.most_common(60)
V = set("AEIOY")
vows = [w for w in caps if set(w) <= V and len(w) >= 4]; vf = collections.Counter(vows)
R["D_vowel_strings"] = dict(count=len(vows), distinct=len(vf), lengths=collections.Counter(len(w) for w in vows).most_common(12), top=vf.most_common(25),
                            seven_vowel_order=sum(1 for w in vows if "AEEIOYO" in w), reversed_order=sum(1 for w in vows if "OYOIEEA" in w))
def greek(w):
    w = w.upper()
    for a, b in (("TH", "θ"), ("PH", "φ"), ("CH", "χ"), ("KH", "χ"), ("PS", "ψ")): w = w.replace(a, b)
    return w
pal = sorted({w for w in caps if len(greek(w)) >= 7 and greek(w) == greek(w)[::-1] and len(set(w)) > 2}, key=len, reverse=True)
R["D_palindromes"] = [(w, freq[w]) for w in pal][:40]
# long continuous capital runs (names written as strings with spaces), palindromic after removing spaces
runs = re.findall(r"(?:\b[A-ZĒŌ]{2,}\b[ ,]*){4,}", body); longpal = []
for r_ in runs:
    s = greek(re.sub(r"[^A-Z]", "", r_))
    for L in range(min(len(s), 70), 20, -1):
        hit = next((s[i:i + L] for i in range(0, len(s) - L + 1) if s[i:i + L] == s[i:i + L][::-1]), None)
        if hit: longpal.append(hit); break
R["D_long_palindromes"] = sorted(set(longpal), key=len, reverse=True)[:12]
# ---------------------------------------------------------------- E
nums = [dict(spell=spell_at(120000 + m.start()), text=ctx(m, 200)) for m in re.finditer(r"(?:number|numerical value|isopseph\w*|letters?)[^.]{0,80}\b(?:\d{2,4})\b|\b\d{3,4}\b[^.]{0,40}(?:number|letters)", body, re.I)]
R["E_number_passages"] = dict(count=len(nums), examples=nums[:30])
GV = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800]))
def iso(g): return sum(GV.get(c, 0) for c in g.lower().replace("ς", "σ"))
NAMES = {"Abrasax": "αβρασαξ", "Abraxas (later spelling)": "αβραξας", "Meithras": "μειθρας", "Iaō": "ιαω", "Sabaōth": "σαβαωθ", "Adōnai": "αδωναι", "Ablanathanalba": "αβλαναθαναλβα",
         "Akrammachamari": "ακραμμαχαμαρι", "Seven vowels αεηιουω": "αεηιουω", "Iēsous (Jesus)": "ιησους", "Emmanouēl": "εμμανουηλ", "Chnoubis": "χνουβις", "Neilos (the Nile)": "νειλος", "Phrē (Ra)": "φρη"}
R["E_isopsephy"] = {k: (v, iso(v)) for k, v in NAMES.items()}
# control: how often does a magical word of 5-9 letters, built from the letter frequencies of the magical words, total exactly 365?
import random
TL = {"A": "α", "B": "β", "G": "γ", "D": "δ", "E": "ε", "Z": "ζ", "I": "ι", "K": "κ", "L": "λ", "M": "μ", "N": "ν", "X": "ξ", "O": "ο", "P": "π", "R": "ρ", "S": "σ", "T": "τ", "Y": "υ"}
letters = [TL.get(ch, "") for w in caps for ch in greek(w) if ch in TL or ch in "θφχψ"] + [ch for w in caps for ch in greek(w) if ch in "θφχψ"]
letters = [c for c in letters if c] + list("ηω") * 400          # restore long vowels lost in the scan, at a modest rate
rnd = random.Random(7); hits = sum(iso("".join(rnd.choice(letters) for _ in range(rnd.randint(5, 9)))) == 365 for _ in range(200000))
R["E_control_365"] = dict(rate=hits / 200000)
json.dump(R, open(OUT, "w"), ensure_ascii=False, indent=1)
print("A.", len(toc), "spells in the contents;", ", ".join(f"{c} {n}" for c, n in cc.most_common()))
print("B. sound and breath instructions:", ", ".join(f"{k} {v['count']}" for k, v in sb.items()))
print("C. things to make:", ", ".join(f"{k} {v}" for k, v in R["C_make"].items()))
print("D. top names:", ", ".join(f"{w} {n}" for w, n in freq.most_common(25)))
print("   vowel strings:", len(vows), "occurrences,", len(vf), "distinct; lengths", R["D_vowel_strings"]["lengths"][:8], "; contain the alphabet order AEĒIOYŌ:", R["D_vowel_strings"]["seven_vowel_order"], "; reversed:", R["D_vowel_strings"]["reversed_order"])
print("   palindromic words:", R["D_palindromes"][:12]); print("   longest palindromic strings:", R["D_long_palindromes"][:5])
print("E. passages stating a number:", len(nums)); print("   letter values:", {k: v[1] for k, v in R["E_isopsephy"].items()}); print(f"   control: a random magical-style word of 5-9 letters totals 365 with probability {R['E_control_365']['rate']:.4f}")
for e in nums[:8]: print("    ", e["spell"], "|", e["text"][:240])
