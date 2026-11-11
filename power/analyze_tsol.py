#!/usr/bin/env python3
"""The Testament of Solomon (Conybeare's 1898 translation, public domain; digital edition by J. H. Peterson, CC BY 4.0;
Greek checked against McCown's 1922 edition, supplied by the user): every instruction, every remedy, every number.

A  THE RING: how Solomon receives it, what is engraved on it, what it does.
B  THE DEMONS AND WHAT DEFEATS EACH: for every demon interrogated, the remedy as the text gives it.
C  THE 36 DECANS (chapter 18): illness caused, remedy, and the remedy's MODE (a spoken formula; a written name; an object
   or material; an action such as washing or burning). Counts per mode.
D  NUMBER CODES: every stated number, checked against the Greek letter values of the name it belongs to.
E  MATTER AND FORCE: passages where spirits move, lift or hold up material things.
Usage: python3 -I analyze_tsol.py <conybeare text> <out json>"""
import collections, json, re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read(); OUT = sys.argv[2]; R = {}
start = t.find("1. Testament of Solomon"); start = start if start > 0 else t.find("TESTAMENT of Solomon, son of David")
body = t[start:] if start > 0 else t
# verses: Peterson's edition numbers paragraphs '73. ' ; split on ' N. ' where N increments
paras, cur, last = {}, [], 0
for m in re.finditer(r"(?<![\w\[])(\d{1,3})\. (?=[A-Z\"'])", body):
    n = int(m.group(1))
    if n == last + 1: paras[n] = m.start(); last = n
keys = sorted(paras); P = {n: re.sub(r"\s+", " ", body[paras[n]: paras[keys[i + 1]] if i + 1 < len(keys) else len(body)]).strip() for i, n in enumerate(keys)}
R["paragraphs"] = len(P)
def find(pat, flags=re.I): return [(n, x) for n, x in P.items() if re.search(pat, x, flags)]
# ---------------------------------------------------------------- A ring
R["A_ring"] = [dict(par=n, text=x[:700]) for n, x in find(r"\bring\b|\bseal\b|pentalpha|engraven")[:8]]
# ---------------------------------------------------------------- B demons
dem = []
for n in sorted(P):
    if n >= 72: continue
    x = P[n] + " " + P.get(n + 1, ""); m = re.search(r"(?:what|which) (?:angel|name)[^?]*frustrat\w*\?\W*(?:\[\d+\]\s*)?(?:And|But|So)? ?(?:he|she|it|the demon|the spirit)[^:]*:\s*(.{0,320})", x)
    if not m: continue
    ans = m.group(1); who = [w for w in re.findall(r"\b([A-Z][a-zA-ZÀ-ɏ]{2,})\b", ans) if w not in ("By", "The", "And", "But", "If", "He", "His", "Of", "In", "Who", "Lord", "God", "Almighty", "Hebrews", "Greeks", "Romans", "Saviour")]
    dem.append(dict(par=n, answer=ans.strip()[:300], names=who[:4]))
R["B_demons"] = dem
# ---------------------------------------------------------------- C decans
dec = []
for n, x in P.items():
    m = re.search(r"I (?:O Lord, )?am called ([A-Z][^\s,.;:]+)", x)
    if not m or n < 73 or n > 115: continue
    name = m.group(1).strip("'\".,")
    harm = re.search(r"called [^,.;]+[,.;]\s*(?:and\s+)?(I [^.]+)\.", x); harm = harm.group(1) if harm else ""
    spoken = bool(re.search(r"\bhear\b|\bsay\b|\bwords\b|\bname of\b", x, re.I)); written = bool(re.search(r"\bwrite\b|\bwritten\b|\binscrib", x, re.I))
    obj = re.findall(r"\b(laurel|leaves?|paper|papyrus|amulet|salt|oil|nard|water|sea-water|wine|honey|gold|silver|iron|ring|seal|stone|thread|tin|lead|plate|wax|bread|frankincense|myrrh|bones?|liver|gall|heart|rose|coriander)\b", x, re.I)
    act = re.findall(r"\b(wash|sprinkle|hang|bind|tie|burn|fumigat\w*|smear|anoint|drink|eat|wear|bury|place|carry|throw|pour)\w*", x, re.I)
    words = re.findall(r"'([^']{3,140})'", x)
    dec.append(dict(par=n, name=name, harm=harm[:160], spoken=spoken, written=written, objects=sorted({o.lower() for o in obj}), actions=sorted({a.lower() for a in act}), formula=words[:2]))
R["C_decans"] = dec
modes = collections.Counter()
for d in dec:
    modes["spoken formula"] += d["spoken"] and not d["written"]; modes["written name"] += d["written"]; modes["object or material"] += bool(d["objects"]); modes["action (wash, burn, hang ...)"] += bool(d["actions"])
R["C_modes"] = dict(modes)
HARM = {"head and brain": r"head|brow|migraine|brain|mind|madness", "eyes and ears": r"\beyes?\b|\bears?\b|deaf|sight", "throat, chest, lungs": r"throat|tonsil|parotid|cough|breath|chest|lung", "heart and nerves": r"heart|nerve|shoulder|paraly|tremble",
        "belly, kidneys, bowels": r"bowel|colic|reins|kidney|bladder|belly|stomach|liver|spleen", "fever and chills": r"fever|shiver|chill", "skin and joints": r"skin|joint|gout|knee|foot|feet|limb",
        "household and quarrels": r"home|house|strife|quarrel|partisan|wife|husband|friend", "childbirth and women": r"childbirth|women|womb|breast"}
R["C_harm"] = {k: sum(1 for d in dec if re.search(p, d["harm"] + " " + P[d["par"]][:300], re.I)) for k, p in HARM.items()}
# ---------------------------------------------------------------- D numbers
GV = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800]))
def iso(g): return sum(GV.get(c, 0) for c in g.lower().replace("ς", "σ"))
CHECK = {"Emmanouēl (Ἐμμανουήλ)": "εμμανουηλ", "Raphaēl (Ῥαφαήλ)": "ραφαηλ", "Iēsous (Ἰησοῦς)": "ιησους", "Sōtēr, 'Saviour' (σωτήρ)": "σωτηρ", "Christos (Χριστός)": "χριστος", "Michaēl (Μιχαήλ)": "μιχαηλ"}
nums = [dict(par=n, text=re.sub(r"\s+", " ", x[max(0, m.start() - 220): m.end() + 120])) for n, x in P.items() for m in re.finditer(r"\bnumber\w*|\bsum\b|\bletters\b", x)]
R["D_numbers"] = dict(passages=nums, checks={k: iso(v) for k, v in CHECK.items()})
# ---------------------------------------------------------------- E matter and force
R["E_matter"] = [dict(par=n, text=x[:600]) for n, x in find(r"lift\w*|in the air|pillar|corner-?stone|carry stones|saw\w* (?:up )?(?:the )?(?:Theban )?marble|raise\w* (?:it|the stone)|support\w* it")]
json.dump(R, open(OUT, "w"), ensure_ascii=False, indent=1)
print(R["paragraphs"], "paragraphs;", len(dem), "demon-remedy pairs before the decans;", len(dec), "decans parsed")
print("remedy modes among decans:", R["C_modes"]); print("what the decans attack:", R["C_harm"])
print("stated numbers checked:", R["D_numbers"]["checks"]); print(len(nums), "passages mention a number or letters")
print("matter and force passages:", [e["par"] for e in R["E_matter"]])
for d in dec[:6] + dec[-4:]: print("  ", d["par"], d["name"], "|", d["harm"][:70], "| spoken" if d["spoken"] else "", "| written" if d["written"] else "", d["objects"], d["actions"], d["formula"][:1])
