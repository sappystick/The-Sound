#!/usr/bin/env python3
"""Build explorer/index.html (the interactive findings explorer) from the project's own data files.
Inputs: SBLGNT John, KJV (public domain), model/out/john_verses.csv, video/out/john_timeline.json (if rendered),
robustness/results.json, robustness/highres_results.json, code/analysis/movement_path.json.
Usage: python3 build.py <sblgnt dir> <kjv csv>"""
import collections, csv, glob, json, math, os, re, sys, unicodedata
import numpy as np
SBL, KJV = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
V = collections.OrderedDict()
for l in open(glob.glob(os.path.join(SBL, "*-Jn-*"))[0], encoding="utf-8"):
    p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append(dict(raw=p[3], lem=nrm(p[6]), pos=p[1], parse=p[2]))
keys = list(V); n = len(keys)
kjv = {(int(r["Chapter"]), int(r["Verse"])): r["Text"] for r in csv.DictReader(open(KJV, encoding="utf-8")) if r["Book"] == "John"}
vrow = {r["verse"]: r for r in csv.DictReader(open(os.path.join(ROOT, "model/out/john_verses.csv"), encoding="utf-8"))}
tl_path = os.path.join(ROOT, "video/out/john_timeline.json"); TL = json.load(open(tl_path, encoding="utf-8")) if os.path.exists(tl_path) else None
tlv = {x["v"]: x for x in TL["verses"]} if TL else {}
mv = {d["v"]: d["body"] for d in json.load(open(os.path.join(ROOT, "code/analysis/movement_path.json")))}
HPV = {"λεγω", "ερχομαι", "βλεπω", "ευρισκω", "λαμβανω", "ακολουθεω", "τρεχω", "φωνεω", "αγω", "φερω", "εισερχομαι", "εξερχομαι", "θεωρεω", "παραλαμβανω", "εγειρω", "αποστελλω", "πεμπω", "μαρτυρεω", "κραζω", "κραυγαζω"}
d_, a_ = [], []
for v in V.values():
    m = len(v); sp = any(u["pos"][0] == "V" and u["parse"][0] in "12" for u in v)
    d_.append(sum((t["pos"][0] == "V" and t["parse"][0] in "12") or t["lem"] in ("εγω", "συ", "ημεις", "υμεις") for t in v) / m)
    a_.append(sum(t["pos"][0] == "V" and t["parse"][0] == "3" and t["parse"][3] == "I" and t["parse"][1] in "AIP" and not sp for t in v) / m)
d_, a_ = np.array(d_), np.array(a_); MODE = (d_ - d_.mean()) / d_.std() - (a_ - a_.mean()) / a_.std()
SM = np.convolve(np.pad(MODE, 3, mode="edge"), np.ones(7) / 7, mode="valid")
STOP = set("ο και αυτος δε εν ειμι λεγω ου μη γαρ ουν οτι εγω συ ουτος εκεινος τις ινα προς εκ εις απο επι δια μετα περι αλλα ως καθως ημεις υμεις εαν αν οστις παρα υπο ηδη ετι ουδε τε η ποιεω εχω γινομαι ερχομαι".split())
docs = [[t["lem"] for t in V[k] if t["pos"][0] in "NVA" and t["lem"] not in STOP] for k in keys]
df = collections.Counter(l for x in docs for l in set(x)); voc = {l: i for i, l in enumerate(df)}; X = np.zeros((n, len(voc)))
for i, x in enumerate(docs):
    for l in x: X[i, voc[l]] += math.log(n / df[l])
Xn = X / np.maximum(1e-9, np.linalg.norm(X, axis=1, keepdims=True)); SIM = Xn @ Xn.T
summ = json.load(open(os.path.join(ROOT, "model/out/john_summary.json"), encoding="utf-8")); BR = summ["section_pauses"]["breaks"]
verses = []; t_model = 0
for i, k in enumerate(keys):
    vs = f"{k[0]}:{k[1]}"; r = vrow.get(vs, {}); s = SIM[i].copy(); s[max(0, i - 30): i + 31] = -1; ech = [f"{keys[j][0]}:{keys[j][1]}" for j in np.argsort(-s)[:2] if s[j] > 0.15]
    T = tlv.get(vs); start = T["start"] if T else float(r.get("start_s", 0)); dur = T["dur"] if T else float(r.get("dur_s", 0))
    verses.append(dict(v=vs, c=k[0], t=round(start, 2), d=round(dur, 2), g=" ".join(x["raw"] for x in V[k]), e=kjv.get(k, ""), ipa=(T or {}).get("ipa", ""),
                       nz=float(r.get("noise_share", 0.326)), m=round(float(MODE[i]), 2), sm=round(float(SM[i]), 2), sy=int(r.get("syllables", 0)), bg=int(r.get("breath_groups", 0)),
                       hp=int(sum(x["pos"][0] == "V" and x["parse"][:2] == "3P" and x["parse"][3] == "I" and x["lem"] in HPV for x in V[k])),
                       bd=mv.get(vs, []), mk=[q for q in r.get("markers", "").split(";") if q and q != "i_am_images"], br=BR.get(vs, ""), ec=ech))
chap_start = {}
for x in verses: chap_start.setdefault(x["c"], x["t"])
RS = json.load(open(os.path.join(ROOT, "robustness/results.json"), encoding="utf-8")); HR = json.load(open(os.path.join(ROOT, "robustness/highres_results.json"), encoding="utf-8"))
seg = [dict(b=r["book"], o=r["outline"], ms=r["minseg"], md=r["mode"], k=r["k"], p=r["p"], cu=r["cuts"]) for r in RS["segmentation"] if r["k"] == 4]
DATA = dict(verses=verses, chapStart=chap_start, total=(TL["total_s"] if TL else verses[-1]["t"] + verses[-1]["d"]), hasVideo=bool(TL), seg=seg, hr=HR,
            c3=RS["C3"]["detail"], c3p=RS["C3"]["p_two_books"], c11=RS["C11"]["shares"], g=RS["G"], g2=dict(n=RS["G2"]["n"], thr=RS["G2"]["bh_threshold"]),
            c25=RS["C25"], prereg=RS["prereg_commit"], hashes=RS["inputs_sha256_16"])
# voice lab: samples, validation (planned vs measured pitch), rulebook
A2 = os.path.join(ROOT, "audio_model", "v2"); lab = []
if os.path.exists(os.path.join(A2, "index.json")):
    for name, info in json.load(open(os.path.join(A2, "index.json"), encoding="utf-8")).items():
        js = json.load(open(os.path.join(A2, f"{name}_C_full.json"), encoding="utf-8")); f0 = np.array(js["f0"]); P, M = [], []
        for w in js["words"]:
            k_ = len(w["pitch_hz"])
            for j, hz in enumerate(w["pitch_hz"]):
                tm = w["start"] + (w["end"] - w["start"]) * (j + .5) / max(1, k_); m = (np.abs(f0[:, 0] - tm) < 0.04) & (f0[:, 1] > 0)
                if m.any(): P.append(hz); M.append(float(np.median(f0[m, 1])))
        P, M = np.array(P), np.array(M)
        lab.append(dict(name=name, refs=js["refs"], dur=info["duration"], speakers=info["speakers"], rules=info["rules"], r=round(float(np.corrcoef(np.log(P), np.log(M))[0, 1]), 2),
                        err=round(float(np.median(np.abs(12 * np.log2(M / P)))), 2), median=round(float(np.median(f0[f0[:, 1] > 0, 1])), 1),
                        words=[dict(w=x["word"], s=x["speaker"], r=x["rules"]) for x in js["words"]]))
def _j(n):
    q = os.path.join(A2, n); return json.load(open(q, encoding="utf-8")) if os.path.exists(q) else None
DATA["opening"] = _j("opening_index.json") or []; DATA["aramaic"] = _j("aramaic_index.json") or {"sayings": []}
_ll = json.load(open(os.path.join(ROOT, "code/voice/language_layer.json"), encoding="utf-8"))
DATA["langs"] = [dict(who=k, **{x: v[x] for x in ("lang", "confidence", "basis")}) for k, v in _ll["speakers"].items()]
DATA["lab"] = lab; DATA["rulebook"] = json.load(open(os.path.join(ROOT, "code/voice/delivery_rules.json"), encoding="utf-8"))["rules"]
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))))
print("explorer built:", round(os.path.getsize(os.path.join(HERE, "index.html")) / 1e6, 2), "MB; video timings:", bool(TL))
