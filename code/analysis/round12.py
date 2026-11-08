#!/usr/bin/env python3
"""Round 12: two concrete leads, each widened and tested on its own.

A. DEAD SEA SCROLL IDIOMS (fixed list).  For each Hebrew expression: count in all Scrolls, in the Community Rule
   (1QS), in the Hebrew Bible; then its Greek counterpart in John + 1-3 John, the rest of the NT, and the Septuagint.
   A 'Scroll-Johannine' idiom = present in the Scrolls and John, absent or near-absent in the Hebrew Bible/LXX.
B. SEPARATION -> ONE -> COMPLETION in John.  Fixed word families:
     separation: schisma (division), skorpizo (scatter), choris (apart from)
     one:        hen / heis used of unity (10:30; 11:52; 17:11, 21, 22, 23)
     completion: teleo / teleioo (finish, perfect)
   Where they fall on John's spoken timeline; whether the families come in that order more than chance
   (permutation of family labels over the same positions); and the 'ego' line: emphatic ego (I) by chapter, against
   the Synoptics.
Usage: python3 round12.py <sblgnt> <lxx-swete/data> <morphhb/wlc> <dss_scrolls.json>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL, LXX, WLC, DSS = sys.argv[1:5]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(12); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
def hc(s): return "".join(c for c in unicodedata.normalize("NFD", s) if "א" <= c <= "ת").translate(str.maketrans("ךםןףץ", "כמנפצ"))
NT = {}
for f in sorted(glob.glob(os.path.join(SBL, "*-morphgnt.txt"))):
    b = os.path.basename(f).split("-")[1]; NT[b] = [((int(l[2:4]), int(l[4:6])), nrm(l.split()[4]), nrm(l.split()[6])) for l in open(f, encoding="utf-8")]
JOH = ["Jn", "1Jn", "2Jn", "3Jn"]
jtext = " ".join(w for b in JOH for _, w, _ in NT[b]); ntext = " ".join(w for b in NT if b not in JOH for _, w, _ in NT[b])
ltext = " ".join(nrm(l.split(maxsplit=1)[1]) for f in glob.glob(os.path.join(LXX, "*.txt")) for l in open(f, encoding="utf-8") if len(l.split(maxsplit=1)) == 2)
dss = json.load(open(DSS)); allq = " ".join(hc(w) for s in dss.values() for w in s if w.strip()); qs = " ".join(hc(w) for w in dss["1QS"] if w.strip())
hb = " ".join(hc(p) for f in glob.glob(os.path.join(WLC, "*.xml")) for w in re.findall(r"<w [^>]*>([^<]+)</w>", open(f, encoding="utf-8").read()) for p in w.split("/"))
print("A. DEAD SEA SCROLL IDIOMS (counts)")
ID = [("sons of light", r"בני אור", r"υιοι φωτοσ|υιοι του φωτοσ"), ("sons of darkness", r"בני חושכ|בני חשכ", r"υιοι σκοτουσ|τεκνα σκοτουσ"),
      ("spirit of truth", r"רוח אמת|רוחות אמת|רוח ה אמת", r"πνευμα τησ αληθειασ"), ("spirit of deceit / error", r"רוח עול|רוח תעות|רוחות עול", r"πνευμα τησ πλανησ"),
      ("doing the truth", r"עשות אמת|לעשות אמת|ו עשות אמת", r"ποιων την αληθειαν|ποιειν την αληθειαν|ποιουμεν την αληθειαν"),
      ("walking in truth / in darkness", r"להתהלכ ב אמת|הלכ ב אמת|ב דרכי חושכ|ב חושכ יתהלכו", r"εν αληθεια περιπατ|περιπατ εν αληθεια|εν τη σκοτια περιπατ|περιπατ εν τη σκοτια|περιπατων εν τη σκοτια"),
      ("light of life", r"אור ה חיימ|ב אור חיימ", r"φωσ τησ ζωησ"), ("eternal life", r"חיי נצח|חיי עולמ", r"ζωην αιωνιον|ζωη αιωνιοσ|ζωησ αιωνιου"),
      ("love the brothers / hate", r"לאהוב כול בני אור|ו לשנוא כול בני חושכ", r"αγαπα τον αδελφον|μισων τον αδελφον|μισει τον αδελφον"), ("men of truth", r"אנשי ה אמת|אנשי אמת", r"εκ τησ αληθειασ")]
rows = []
for lab, h, g in ID:
    r = dict(scrolls=len(re.findall(h, allq)), qs=len(re.findall(h, qs)), hb=len(re.findall(h, hb)), johannine=len(re.findall(g, jtext)), other_nt=len(re.findall(g, ntext)), lxx=len(re.findall(g, ltext)))
    rows.append((lab, r)); tag = "  <- Scrolls + John, not Hebrew Bible/LXX" if r["scrolls"] and r["johannine"] and not r["hb"] and not r["lxx"] else ""
    print(f"   {lab:32s} Scrolls {r['scrolls']:3d} (1QS {r['qs']:2d})  Hebrew Bible {r['hb']:3d}  |  John+1-3Jn {r['johannine']:2d}  other NT {r['other_nt']:2d}  LXX {r['lxx']:2d}{tag}")
out["idioms"] = dict(rows)

print("\nB. SEPARATION -> ONE -> COMPLETION in John")
J = NT["Jn"]; total = len(J); pos = {}
for i, (r, w, l) in enumerate(J): pos.setdefault(r, i / total)
FAM = {"separation": lambda w, l: l in ("σχισμα", "σκορπιζω", "διασκορπιζω", "χωρισ"), "one (unity)": None, "completion": lambda w, l: l in ("τελεω", "τελειοω")}
UNITY = {(10, 16), (10, 30), (11, 52), (17, 11), (17, 21), (17, 22), (17, 23)}   # verses where hen/heis is said of unity (read from the text)
ev = []
for fam, test in FAM.items():
    vs = sorted({r for r, w, l in J if (r in UNITY and l == "εισ") or (test and test(w, l))}) if fam == "one (unity)" else sorted({r for r, w, l in J if test(w, l)})
    for v in vs: ev.append((pos[v], fam, v))
    print(f"   {fam:12s} " + ", ".join(f"{c}:{v} ({pos[(c, v)]:.2f})" for c, v in vs))
ev.sort(); order = {"separation": 0, "one (unity)": 1, "completion": 2}
lab = np.array([order[f] for _, f, _ in ev])
def inversions(x): return sum(1 for i in range(len(x)) for j in range(i + 1, len(x)) if x[i] > x[j])
real = inversions(lab); null = [inversions(rng.permutation(lab)) for _ in range(20000)]
print(f"   order test: inversions against separation -> one -> completion = {real} (random median {int(np.median(null))}); p = {np.mean(np.array(null) <= real):.4f}")
print("   centres of each family (median position): " + ", ".join(f"{f} {np.median([p for p, ff, _ in ev if ff == f]):.2f}" for f in order))
out["arc"] = dict(events=[(round(p, 3), f, f"{v[0]}:{v[1]}") for p, f, v in ev], inversions=real, p=float(np.mean(np.array(null) <= real)))
print("\n   the 'ego' line: emphatic ego (I) per 1,000 words, by fifths of each Gospel")
for b in ("Jn", "Mt", "Mk", "Lk"):
    T = NT[b]; n = len(T); fifths = [sum(1 for i, (r, w, l) in enumerate(T) if w == "εγω" and k * n / 5 <= i < (k + 1) * n / 5) / (n / 5) * 1000 for k in range(5)]
    print(f"      {b}: " + "  ".join(f"{x:5.1f}" for x in fifths))
    out.setdefault("ego", {})[b] = fifths
last_ego = max(r for r, w, l in J if w == "εγω"); print(f"   John's last emphatic 'ego': {last_ego[0]}:{last_ego[1]}; after 19:30 ('It is finished'): {sum(1 for r, w, l in J if w == 'εγω' and r > (19, 30))} times")
json.dump(out, open(os.path.join(HERE, "round12_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
