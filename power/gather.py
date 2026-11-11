#!/usr/bin/env python3
"""Gather every instruction for building or using an object, instrument or procedure with claimed unusual effects, in the
original language beside the King James text, with literal notes on words whose sense is lost in translation.
Claims are recorded as claims; evaluation is a later step. Also runs the extended measurements (X1-X7).
Output: power/catalogue.json  (printed summary)
Usage: python3 gather.py <sblgnt> <wlc> <lxx data> <kjv csv> <cntr class-1 dir> <greek corpora dir> <power scratch dir>"""
import collections, csv, glob, json, os, re, sys, unicodedata
SBL, WLC, LXX, KJV, CN, GR, PW = sys.argv[1:8]; HERE = os.path.dirname(os.path.abspath(__file__))
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
KJ = {(r["Book"], int(r["Chapter"]), int(r["Verse"])): r["Text"] for r in csv.DictReader(open(KJV, encoding="utf-8"))}
_w = {}
def heb(book, c, v):
    if book not in _w: _w[book] = open(os.path.join(WLC, f"{book}.xml"), encoding="utf-8").read()
    m = re.search(rf'<verse osisID="{book}\.{c}\.{v}">(.*?)</verse>', _w[book], re.S)
    return " ".join(w.replace("/", "") for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(1))) if m else ""
_g = {}
def grk(code, c, v):
    if code not in _g:
        V = collections.defaultdict(list)
        for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"): p = l.split(); V[(int(p[0][2:4]), int(p[0][4:6]))].append(re.sub(r"[⸀⸁⸂⸃⸄⸅]", "", p[3]))
        _g[code] = V
    return " ".join(_g[code].get((c, v), []))
_l = {}
def lxx(fname, c, v):
    if fname not in _l:
        V = collections.defaultdict(list)
        for l in open(os.path.join(LXX, fname), encoding="utf-8"):
            p = l.split()
            if len(p) >= 2 and re.match(r"\d+\.\d+\.\d+", p[0]): _, cc, vv = p[0].split("."); V[(int(cc), int(vv))].append(p[1])
        _l[fname] = V
    return " ".join(_l[fname].get((c, v), []))
HB = {"Gen": "Genesis", "Exod": "Exodus", "Num": "Numbers", "Josh": "Joshua", "1Sam": "I Samuel", "2Kgs": "II Kings", "1Kgs": "I Kings", "1Chr": "I Chronicles", "2Chr": "II Chronicles", "Ps": "Psalms"}
NT = {"Jn": "John", "Mk": "Mark", "Ac": "Acts"}
# (id, title, category, source, refs, what is built or done, sound, claimed effect, literal notes)
C = [
 ("trumpets", "Two silver trumpets", "instrument", "Num", [(10, 2), (10, 9), (10, 10)], "two trumpets of hammered silver; distinct signals: one blast, two, an alarm", "trumpet blasts", "the people are 'remembered before the LORD' and saved from enemies", "Hebrew *teru'ah* = an alarm blast and also the shout of a crowd: the same word for instrument and voice."),
 ("jericho", "The fall of Jericho", "procedure", "Josh", [(6, 4), (6, 5), (6, 16), (6, 20)], "seven priests, seven ram's-horn trumpets, the ark; once round the city for six days, seven times on the seventh; a long blast, then a great shout", "ram's horns and the shout of the people", "the wall falls", "6:20 *watippol ha-chomah tachteyha*: 'the wall fell **beneath itself**': it collapsed downward in place, not outward."),
 ("sinai", "The voice of the shofar at Sinai", "event", "Exod", [(19, 16), (19, 19)], "", "a shofar growing louder and louder", "Moses speaks and God answers 'by a voice'", "*be-qol*: *qol* is 'voice', 'sound' and 'thunder'; the passage does not separate them."),
 ("bells", "The bells on the high priest's robe", "garment", "Exod", [(28, 33), (28, 34), (28, 35)], "a blue robe whose hem alternates golden bells and pomegranates", "bells sounding as he walks", "'his sound shall be heard when he goes into the holy place … **that he die not**'", "*we-nishma' qolo*: 'and its sound shall be heard': sound as a condition of survival in the sanctuary."),
 ("ark", "The ark and the mercy seat", "object", "Exod", [(25, 10), (25, 17), (25, 18), (25, 22)], "a chest of acacia wood overlaid with gold, 2.5 × 1.5 × 1.5 cubits; a gold cover with two hammered cherubim facing each other", "a voice heard from between the cherubim (Numbers 7:89)", "'there I will meet with you and speak with you from above the mercy seat, from between the two cherubim'", "Numbers 7:89 'he heard **the voice speaking** to him from between the two cherubim' (*middabber*, reflexive: 'speaking to itself')."),
 ("breastplate", "The breastplate with Urim and Thummim", "object", "Exod", [(28, 15), (28, 16), (28, 17), (28, 30)], "a square of gold, blue, purple and scarlet, a span each way; twelve stones in four rows; the Urim and Thummim placed inside", "", "judgement and answers from God", "*Urim* and *Thummim* are usually rendered 'lights and perfections'; their working is never described."),
 ("oil", "The holy anointing oil and incense", "recipe", "Exod", [(30, 23), (30, 24), (30, 25), (30, 34), (30, 35)], "myrrh 500, cinnamon 250, calamus 250, cassia 500 shekels, a hin of olive oil; incense of stacte, onycha, galbanum, frankincense, equal parts, salted", "", "makes things holy; copying it is forbidden on pain of being cut off (30:33, 38)", ""),
 ("serpent", "The bronze serpent", "object", "Num", [(21, 8), (21, 9)], "a serpent of bronze set on a pole", "", "anyone bitten who looks at it lives", "*nachash nechoshet*, 'serpent of bronze': the two words sound almost alike. John 3:14 applies it to Jesus."),
 ("lyre", "David's lyre", "instrument", "1Sam", [(16, 16), (16, 23)], "a skilled player of the lyre (*kinnor*) plays with his hand", "lyre", "the evil spirit departs from Saul", "16:23 *we-ravach le-Sha'ul*: 'and there was **breathing-space** for Saul'. *ravach* shares its root with *ruach*, wind, breath, spirit: the cure is literally that breath came back."),
 ("musician", "Elisha's musician", "procedure", "2Kgs", [(3, 15)], "a player of a stringed instrument plays", "string music", "'the hand of the LORD came upon him' and he prophesies", "*ke-naggen ha-menaggen*: 'as the player played': the state comes during the playing."),
 ("prophets", "Prophesying with instruments", "procedure", "1Chr", [(25, 1), (25, 3)], "the sons of Asaph, Heman and Jeduthun", "lyres, harps, cymbals", "they 'prophesy' with the instruments", "The verb *nibba'* ('prophesy') is used of the music itself."),
 ("temple", "The dedication of Solomon's temple", "event", "2Chr", [(5, 12), (5, 13), (5, 14)], "120 priests with trumpets and the Levite singers with cymbals, harps and lyres", "trumpets and singers 'as one, to make **one sound** heard'", "the house is filled with a cloud; the priests cannot stand to minister", "*le-hashmia' qol echad*: 'to make one voice heard': unison is the stated condition."),
 ("psalm29", "The seven voices of Psalm 29", "text", "Ps", [(29, 3), (29, 4), (29, 5), (29, 7), (29, 8), (29, 9)], "", "'the voice of the LORD', seven times", "breaks cedars, divides flames of fire, shakes the wilderness, makes deer give birth, strips the forests", "*qol YHWH* seven times in eleven verses (measured, X2)."),
 ("water", "Healing the waters", "recipe", "2Kgs", [(2, 20), (2, 21)], "a new bowl with salt in it, thrown into the spring", "a spoken formula: 'Thus says the LORD, I have healed these waters'", "the water is healed", "Compare Exodus 15:25: a piece of wood thrown into bitter water makes it sweet."),
 ("bones", "Elisha's bones", "object", "2Kgs", [(13, 21)], "", "", "a dead man who touches them revives", ""),
 ("words", "Creation by ten sayings", "text", "Gen", [(1, 3), (1, 6), (1, 9)], "", "'And God said'", "each saying brings something into being", "Measured (X1): 'and God said' occurs ten times in Genesis 1; the Mishnah (Avot 5:1) says the world was made 'with ten utterances'."),
 ("tobit", "Tobit's fish: heart, liver and gall", "recipe", "LXX:21.Tobias.txt", [(6, 8), (6, 9), (8, 2), (8, 3), (11, 11), (11, 13)], "the heart and liver of the fish burnt on incense embers; the gall applied to the eyes", "", "the smoke drives a demon away; the gall heals blindness", "Septuagint Greek; the Hebrew and Aramaic originals survive only in fragments at Qumran."),
 ("ephphatha", "Opening deaf ears", "procedure", "Mk", [(7, 33), (7, 34), (7, 35)], "fingers into the ears, spitting, touching the tongue, looking up to heaven, a groan", "*Ephphatha*: 'be opened', kept in Aramaic", "hearing and speech restored", "*estenaxen*, 'he groaned', just before the word: a sound before the sound."),
 ("eyes", "Spittle in two stages", "procedure", "Mk", [(8, 23), (8, 24), (8, 25)], "spitting on the eyes, laying on hands, then hands again", "", "sight restored in two stages", ""),
 ("siloam", "Clay and the pool of Siloam", "procedure", "Jn", [(9, 6), (9, 7)], "spittle and earth made into clay, spread on the eyes; wash in the pool of Siloam", "", "a man born blind sees", "John translates *Siloam* as 'Sent'."),
 ("bethesda", "The stirred pool of Bethesda", "place", "Jn", [(5, 2), (5, 3), (5, 7)], "a pool with five porticoes", "", "the first to enter the water when it is 'stirred' is healed (5:7; and the longer text of 5:3b-4)", "Measured (X5): verses 3b-4, the angel stirring the water, are absent from the earliest manuscripts."),
 ("tabitha", "Tabitha, arise", "procedure", "Ac", [(9, 40)], "everyone sent out; kneeling; prayer; then a command", "*Tabitha, anastēthi*", "a dead woman opens her eyes", "Measured (X4): *Tabitha qumi* and Jesus' *talitha qumi* (Mark 5:41) differ by one sound, and the scenes match step by step."),
]
cat = []
for cid, title, kind, src, refs, built, sound, effect, note in C:
    passages = []
    for c, v in refs:
        if src.startswith("LXX:"): orig = lxx(src[4:], c, v); eng = KJ.get(("Tobit", c, v), ""); lang = "Greek (Septuagint)"
        elif src in NT: orig = grk(src, c, v); eng = KJ.get((NT[src], c, v), ""); lang = "Greek"
        else: orig = heb(src, c, v); eng = KJ.get((HB[src], c, v), ""); lang = "Hebrew"
        passages.append(dict(ref=f"{src.split(':')[-1].split('.')[-2] if src.startswith('LXX:') else (HB.get(src) or NT.get(src))} {c}:{v}", lang=lang, original=orig, kjv=eng))
    cat.append(dict(id=cid, title=title, kind=kind, built=built, sound=sound, claim=effect, literal=note, passages=passages))
# ---- Greek sources outside the Bible
def section(path, pat, before=350, after=650):
    x = open(path, encoding="utf-8").read(); x = re.sub(r"<teiHeader.*?</teiHeader>", "", x, flags=re.S)
    x = re.sub(r'<div[^>]*n="([^"]+)"[^>]*>', r" [§\1] ", x); x = re.sub(r"<milestone[^>]*n=\"([^\"]+)\"[^>]*/>", r" [§\1] ", x); x = re.sub(r"<[^>]+>", " ", x); x = re.sub(r"\s+", " ", x)
    n = "".join(c for c in unicodedata.normalize("NFD", x.lower()) if not unicodedata.combining(c)); m = re.search(pat, n)
    if not m: return None
    i = m.start(); secs = re.findall(r"\[§([^\]]+)\]", x[:i]); return dict(where=".".join(secs[-2:]), text=re.sub(r" \[§[^\]]+\] ", " ", x[max(0, i - before): i + after]).strip())
JOS = glob.glob(os.path.join(GR, "perseus/data/tlg0526/tlg001/*grc*.xml"))[0]
EXTRA = [
 ("amphion", "Amphion's walls of Thebes", "instrument", os.path.join(PW, "pausanias.xml"), r"χορδας επι τεσσαρσι", "Pausanias, Description of Greece 9.5.7-8", "the lyre (given by Hermes, in some accounts)", "stones follow his song and build the walls"),
 ("hammers", "Pythagoras' hammers and the string", "instrument", os.path.join(PW, "iamb_vitapyth.xml"), r"χαλκε|σφυρ", "Iamblichus, Life of Pythagoras 115-120", "hammers of different weights; then strings stretched by weights on a peg (a monochord)", "the discovery that consonance follows whole-number ratios 12:9:8:6"),
 ("trumpet_jos", "The silver trumpet described", "instrument", JOS, r"στενη δ. εστι συριγξ", "Josephus, Antiquities 3.291", "a silver tube about a cubit long, slightly thicker than a flute, ending in a bell", "the signals of Numbers 10"),
 ("ring", "Solomon's ring and incantations", "object", JOS, r"δακτυλιον", "Josephus, Antiquities 8.47-48", "a ring with a root under its seal; Solomon's incantations recited", "a demon drawn out through the nostrils; a cup of water overturned as proof"),
 ("vowels", "The seven-vowel hymn", "procedure", os.path.join(PW, "demetrius.xml"), r"επτα φωνηεντ", "Demetrius, On Style 71", "the seven vowels sounded in succession", "heard 'instead of flute and lyre'"),
 ("music_heal", "Healing through music", "procedure", os.path.join(PW, "iamb_vitapyth.xml"), r"δια τησ μουσικησ ιατρει", "Iamblichus, Life of Pythagoras 110-111", "a lyre-player in the centre, a singing circle, in spring", "relief of despondency, anger and desire"),
]
for cid, title, kind, path, pat, where, built, claim in EXTRA:
    s = section(path, pat)
    cat.append(dict(id=cid, title=title, kind=kind, built=built, sound="", claim=claim, literal="", passages=[dict(ref=where + (f" (found at section {s['where']})" if s else ""), lang="Greek", original=s["text"] if s else "(passage not located automatically)", kjv="")]))
cat.append(dict(id="sistrum", title="The sistrum of Isis", kind="instrument", built="a curved metal frame with loose rods that rattle; a cat's face on top", sound="shaking", claim="'things must be shaken and never cease from motion' (Plutarch): the rattle wards off Typhon (destruction)", literal="", passages=[dict(ref="Plutarch, On Isis and Osiris 63", lang="English summary", original="", kjv="")]))
# ---- extended measurements
X = {}
gen = open(os.path.join(WLC, "Gen.xml"), encoding="utf-8").read(); g1 = re.findall(r'<verse osisID="Gen\.1\.(\d+)">(.*?)</verse>', gen, re.S)
said = [int(v) for v, body in g1 if re.search(r'lemma="[^"]*559[^"]*"[^>]*>[^<]*</w>\s*(?:<w [^>]*>[^<]*</w>\s*)?<w lemma="430"', body)]
X["X1_ten_sayings"] = dict(count=len(said), verses=said)
ps = open(os.path.join(WLC, "Ps.xml"), encoding="utf-8").read(); p29 = re.findall(r'<verse osisID="Ps\.29\.(\d+)">(.*?)</verse>', ps, re.S)
qol = [(int(v), len(re.findall(r'lemma="[^"]*6963[^"]*"[^>]*>[^<]*</w>\s*(?:<seg[^>]*>[^<]*</seg>\s*)?<w lemma="3068', body))) for v, body in p29]
X["X2_psalm29_voice_of_YHWH"] = dict(count=sum(n for _, n in qol), verses=[v for v, n in qol for _ in range(n)])
X["X3_divine_name"] = dict(letters="yod he waw he", note="All four are the letters that also serve as vowel signs (matres lectionis); none is a stop. Pronounced as consonants they are a glide, a breath, a glide, a breath: y-h-w-h. The name contains no closure of the mouth at all.")
mk, ac = grk("Mk", 5, 41), grk("Ac", 9, 40)
X["X4_talitha_tabitha"] = dict(mark=mk, acts=ac, aramaic_mark="talitha qumi ('little girl, arise')", aramaic_acts="Tabitha qumi (Peter's words, if spoken in Aramaic)", differs_by="one consonant: l/b",
                              parallel_steps=["the mourners are put out (Mk 5:40 / Ac 9:40)", "he or she takes the hand / gives the hand (Mk 5:41 / Ac 9:41)", "a two-word command", "she rises / sits up", "the onlookers are amazed / many believe"])
def ms(fn):
    V = {}
    for l in open(os.path.join(CN, fn), encoding="utf-8"):
        if l.startswith("43005"): V[(int(l[2:5]), int(l[5:8]))] = l[9:].strip()
    return V
bet = {}
for name, fn in (("P66", "P66.txt"), ("P75", "P75.txt"), ("Sinaiticus", "01.txt"), ("Vaticanus", "03.txt")):
    V = ms(fn); v3 = V.get((5, 3), ""); bet[name] = dict(has_5_4=V.get((5, 4), "-").strip() not in ("-", ""), mentions_moving_water=bool(re.search(r"κινησ", v3)), v3=v3[:160])
X["X5_bethesda"] = bet
X["X6_jericho_sevens"] = dict(priests=7, trumpets=7, days=7, circuits_day7=7, note="Joshua 6:4: seven priests, seven ram's horns, the seventh day, seven times round")
X["X7_cubes"] = dict(note="The inner sanctuary of the tabernacle (10 cubits each way, inferred from its curtains) and of Solomon's temple ('twenty cubits long, twenty wide, twenty high', 1 Kings 6:20) are cubes. Acoustics in experiments/rooms.")
json.dump(dict(catalogue=cat, measured=X), open(os.path.join(HERE, "catalogue.json"), "w"), ensure_ascii=False, indent=1)
print(len(cat), "entries:", ", ".join(c["title"] for c in cat))
for k, v in X.items(): print(k, json.dumps(v, ensure_ascii=False)[:400])
for c in cat:
    if c["passages"] and not c["passages"][0]["original"] and c["id"] != "sistrum": print("MISSING original for", c["id"], c["passages"][0]["ref"])
