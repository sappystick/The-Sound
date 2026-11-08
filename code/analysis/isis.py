#!/usr/bin/env python3
"""Isis texts against John.
 A. Kyme aretalogy (structure only: the user's file is a modern-Greek machine translation of F. C. Grant's English, so
    wording and sound cannot be tested, but the line-by-line form survives): share of lines that are 'I am ...', 'I did ...',
    and what kind of predicate follows 'I am' (name / title / role / image).
 B. Isidorus' hymns (Medinet Madi, 1st c. BC; ancient Greek, SEG 8.548-551): sound measures (noise share, hiatus,
    periodicity) against John and the Homeric Hymns; John's key words in Isidorus.
Usage: python3 isis.py <kyme modern-greek txt> <isidorus greek txt> <sblgnt dir>
"""
import collections, glob, os, re, sys, unicodedata
import numpy as np
KY, ISI, SBL = sys.argv[1:4]; HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import importlib.util
t = open(KY, encoding="utf-8").read(); a = t.find("Είµαι η Ίσις"); seg = t[a: t.find("3.", a) if t.find("3.", a) > 0 else a + 6000]
lines = [re.sub(r"^\s*\d+\s+", "", l).strip() for l in seg.split("\n") if l.strip() and not l.strip().isdigit()]
lines = [l for l in lines if len(l.split()) >= 2][:60]
iam = [l for l in lines if re.match(r"(Εγώ )?Είµαι|Είμαι", l)]; acts = [l for l in lines if re.match(r"(Έ|Ε)[^\s]*α\b|Δίδαξα|Χώρισα|Διέταξα|Επινόησα|Όρισα|Έθεσα|Έδωσα|Έφερα|Αποκάλυψα|Αφιέρωσα|Κατέρριψα|Υποχρέωσα|Έκανα|Παρέδωσα|Καθόρισα|Δηµιούργησα|Ανέβασα", l)]
print(f"A. KYME ARETALOGY (structure): {len(lines)} lines; 'I am' lines {len(iam)} ({len(iam) / len(lines):.0%}); 'I did' (first-person deeds) lines {len(acts)} ({len(acts) / len(lines):.0%})")
for l in iam: print("      ", l[:90])
print("   deeds that touch our threads:")
for kw in ("Χώρισα", "φως", "δεσµώτες", "αληθινό", "γράµµατα", "Άστρο", "ποταµών"):
    for l in lines:
        if kw in l: print("      ", l[:100]); break
print("\nB. ISIDORUS' HYMNS (ancient Greek)")
spec = importlib.util.spec_from_file_location("ac", os.path.join(HERE, "acoustic.py"))
src = open(os.path.join(HERE, "acoustic.py"), encoding="utf-8").read().split("def chunks")[0]
ns = {"__file__": os.path.join(HERE, "acoustic.py")}; sys.argv = ["x", SBL, "-", "-", "-", "-"]; exec(src, ns)
isi = [w for l in open(ISI, encoding="utf-8") for w in l.split() if re.search(r"[Ͱ-Ͽἀ-῿]", w) and not re.search(r"[a-zA-Z/]", w)]
jn = [l.split()[3] for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8")]
mi = ns["measures"](isi); mj = ns["measures"](jn[:len(isi) * 20])
for k in ("noise", "hiatus", "periodicity", "stress_cv"): print(f"   {k:12s} Isidorus {mi[k]:.3f}   John {mj[k]:.3f}")
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
iw = [nrm(w) for w in isi]
for lab, pre in (("life (zoe)", "ζωη"), ("light (phos)", ("φωσ", "φεγγ")), ("son (huios)", "υι"), ("name (onoma)", "ονομ"), ("saviour (soteira)", "σωτ"), ("creator (ktistes)", "κτιστ"), ("water / river / Nile", ("υδωρ", "ποταμ", "νειλ")), ("alone (mone)", "μουν"), ("heaven (ouranos)", "ουραν")):
    hits = [i for i, w in enumerate(iw) if w.startswith(pre)]
    print(f"   {lab:20s} {len(hits)}  e.g. {' | '.join(' '.join(isi[max(0, i - 3): i + 4]) for i in hits[:2])}")
