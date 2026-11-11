#!/usr/bin/env python3
"""Letter-number codes in the instrument and power texts, with the chance rate for each kind of match.

Hebrew gematria (alef=1 ... tav=400, final letters as ordinary) and Greek isopsephy (alpha=1 ... omega=800).
For every equality reported, the control is: among all distinct consonantal word forms of the Hebrew Bible (WLC), how
many share that value. A value shared by many words makes an equality cheap; a value shared by few makes it rarer.
Usage: python3 codes.py <wlc dir>
"""
import collections, glob, json, os, re, sys, unicodedata
WLC = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
HV = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400])); HV.update({"ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90})
def gem(w): return sum(HV.get(c, 0) for c in w)
GV = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", [1, 2, 3, 4, 5, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800]))
def iso(w): w = "".join(c for c in unicodedata.normalize("NFD", w.lower()) if not unicodedata.combining(c)).replace("ς", "σ"); return sum(GV.get(c, 0) for c in w)
# distinct consonantal forms in the Hebrew Bible
forms = set()
for f in glob.glob(os.path.join(WLC, "*.xml")):
    if "VerseMap" in f: continue
    for w in re.findall(r"<w [^>]*>([^<]+)</w>", open(f, encoding="utf-8").read()):
        c = re.sub(r"[^א-ת]", "", w.replace("/", ""))
        if c: forms.add(c)
vals = collections.Counter(gem(w) for w in forms); N = len(forms)
def share(v): return vals[v]
HEB = [("serpent (nachash), Numbers 21:9", "נחש"), ("messiah (mashiach)", "משיח"), ("bronze (nechoshet)", "נחשת"), ("voice, sound, thunder (qol)", "קול"), ("breath, spirit, wind (ruach)", "רוח"),
       ("relief, breathing-space (revach), 1 Sam 16:23", "רוח"), ("lyre (kinnor)", "כנור"), ("ram's horn (shofar)", "שופר"), ("silver trumpet (chatsotsrah)", "חצצרה"), ("alarm blast / shout (teru'ah)", "תרועה"),
       ("ark (aron)", "ארון"), ("mercy seat (kapporet)", "כפרת"), ("cherubim (keruvim)", "כרבים"), ("Urim", "אורים"), ("Thummim", "תמים"), ("bells (pa'amonim)", "פעמנים"),
       ("Jericho", "יריחו"), ("wall (chomah)", "חומה"), ("word / thing (davar)", "דבר"), ("amen", "אמן"), ("YHWH", "יהוה"), ("Adonai", "אדני"), ("Elohim", "אלהים"), ("Sabaoth (tseva'ot)", "צבאות"),
       ("light (or)", "אור"), ("one (echad)", "אחד"), ("love (ahavah)", "אהבה"), ("life (chayyim)", "חיים"), ("water (mayim)", "מים"), ("living water (mayim chayyim)", "מיםחיים")]
rows = [dict(term=t, word=w, value=gem(w), forms_sharing=share(gem(w))) for t, w in HEB]
by = collections.defaultdict(list)
for r in rows: by[r["value"]].append(r["term"])
eq = {v: ts for v, ts in by.items() if len(ts) > 1}
sums = []
for a in rows:
    for b in rows:
        if a["term"] < b["term"]:
            for c in rows:
                if c["value"] == a["value"] + b["value"] and c["term"] not in (a["term"], b["term"]): sums.append((a["term"], b["term"], c["term"], c["value"]))
GRK = [("Abrasax", "αβρασαξ"), ("Meithras", "μειθρας"), ("Neilos (the Nile)", "νειλος"), ("Emmanouēl", "εμμανουηλ"), ("Raphaēl", "ραφαηλ"), ("Iēsous", "ιησους"), ("Christos", "χριστος"), ("amēn", "αμην"),
       ("egō eimi (I am)", "εγωειμι"), ("phōnē (voice)", "φωνη"), ("logos (word)", "λογος"), ("ichthys (fish)", "ιχθυς"), ("the seven vowels", "αεηιουω"), ("Iaō", "ιαω"), ("Sabaōth", "σαβαωθ"), ("Bainchōōōch", "βαινχωωωχ")]
grk = [dict(term=t, word=w, value=iso(w)) for t, w in GRK]
out = dict(hebrew_forms=N, hebrew=rows, hebrew_equalities={str(k): v for k, v in eq.items()}, hebrew_sums=sums, greek=grk, mean_forms_per_value=round(N / len(vals), 1))
json.dump(out, open(os.path.join(HERE, "codes_results.json"), "w"), ensure_ascii=False, indent=1)
print(f"{N} distinct consonantal word forms in the Hebrew Bible, over {len(vals)} values: on average {N / len(vals):.0f} forms share any one value")
for r in rows: print(f"   {r['term']:46s} {r['word']:8s} = {r['value']:4d}   ({r['forms_sharing']} forms in the Bible share this value)")
print("equal values among the instrument terms:", eq)
print("A + B = C among them:", [s for s in sums][:12])
print("Greek:", {g['term']: g['value'] for g in grk})
