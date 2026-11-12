#!/usr/bin/env python3
"""Round 85 - the MISLABELING / displacement hypothesis (user's idea) + the image-anchor test (Stage C probe 2).

MISLABELING idea: what if the label at a spot is NOT the correct label for that picture - the right label sits
elsewhere, and the permutation (which label belongs where) IS the code? Testable consequences:
  M1 section-match: a label's vocabulary should match its OWN section's running text. If labels systematically match
     a DIFFERENT section, that is displacement. Confusion matrix of label-section vs best-matching-text-section.
  M2 transposition viability: if labels are displaced pieces of the text, every label word must occur in the text.
     Measure the share of label types that never appear in any running text (round 66 found ~41% overall).
  M3 systematic vs random displacement: are the mismatches consistent (one section's labels always match another -
     a recoverable key) or scattered (noise)? Permutation test on the confusion structure.
IMAGE ANCHOR (Stage C probe 2): within the herbal section each folio is one highly-distinct plant. Do VISUALLY
  similar plant drawings get similar TEXT? Download folio thumbnails (Beinecke IIIF), crude ink-shape features,
  Mantel test of visual-distance vs text(root)-distance. Honest caveat: coarse features may miss plant identity.
Usage: python3 mysteries/voynich/mislabel.py [--no-images]
"""
import collections, io, json, math, os, re, sys, urllib.request
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
ZL = os.path.join(T, "voynich/ZL3b-n.txt"); rng = np.random.default_rng(85)
CACHE = "/tmp/claude-0/-home-user-The-Sound/5630df0b-07ac-5eb9-968f-9ce13efac22b/scratchpad/voy_img"
PREF = ["qok", "qot", "qo", "ych", "cho", "ch", "sho", "sh", "oto", "ot", "ok", "da", "ol", "or", "o", "y", "s", "d"]
SUFF = ["aiin", "oiin", "iin", "eedy", "eey", "edy", "eol", "ody", "chy", "hey", "ain", "dy", "ol", "ar", "or", "al", "hy", "y", "n"]
def root(w):
    p = next((p for p in PREF if w.startswith(p) and len(w) - len(p) >= 1), "")
    rest = w[len(p):]; s = next((s for s in SUFF if rest.endswith(s) and len(rest) - len(s) >= 1), "")
    r = rest[:len(rest) - len(s)] if s else rest
    return r if r else w

def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@=\-]", "", w).strip()

def parse():
    text = collections.defaultdict(list); label = collections.defaultdict(list); pages = {}
    cur = None; sec = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h:
            cur = h.group(1); sec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I"); pages[cur] = sec; continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*]([A-Za-z]+)\d*>\s*(.*)", ln)
        if not m or not sec: continue
        pg, loc, body = m.groups()
        ws = [clean(w) for w in re.split(r"[.\s]+", body) if clean(w) and re.search(r"[a-zA-Z]", clean(w))]
        if loc.startswith("L"): label[sec] += ws
        elif loc.startswith(("P", "T")): text[sec] += ws
    return text, label, pages

TEXT, LABEL, PAGES = parse()
SECS = [s for s in ("H", "P", "Z", "B", "A", "S", "C") if TEXT.get(s) and len(TEXT[s]) > 200]
# section root-profiles (TF over roots)
def profile(words):
    c = collections.Counter(root(w) for w in words); n = sum(c.values()) or 1
    return {k: v / n for k, v in c.items()}
TP = {s: profile(TEXT[s]) for s in SECS}
def cos(a, b):
    keys = set(a) | set(b); da = math.sqrt(sum(v * v for v in a.values())); db = math.sqrt(sum(v * v for v in b.values()))
    return sum(a.get(k, 0) * b.get(k, 0) for k in keys) / (da * db + 1e-9)

# ---- M1 / M3: which section does each section's LABELS match?
conf = {s: collections.Counter() for s in SECS}
for s in SECS:
    for w in LABEL.get(s, []):
        pr = {root(w): 1.0}
        best = max(SECS, key=lambda t: cos(pr, TP[t]))
        conf[s][best] += 1
# normalise rows
confmat = {s: {t: round(conf[s][t] / max(1, sum(conf[s].values())), 3) for t in SECS} for s in SECS}
diag = np.mean([confmat[s][s] for s in SECS if sum(conf[s].values())])
# null: shuffle each label's section membership
alllab = [(s, w) for s in SECS for w in LABEL.get(s, [])]
nulldiag = []
for _ in range(300):
    secs = [s for s, _ in alllab]; rng.shuffle(secs); cc = {s: collections.Counter() for s in SECS}
    for (_, w), s in zip(alllab, secs):
        cc[s][max(SECS, key=lambda t: cos({root(w): 1.0}, TP[t]))] += 1
    nulldiag.append(np.mean([cc[s][s] / max(1, sum(cc[s].values())) for s in SECS]))
out = {"sections": SECS, "section_text_words": {s: len(TEXT[s]) for s in SECS}, "section_label_words": {s: len(LABEL.get(s, [])) for s in SECS}}
out["M1_label_matches_own_section"] = dict(confusion_rows_label_section_to_text_section=confmat,
    mean_diagonal=round(float(diag), 3), null_mean=round(float(np.mean(nulldiag)), 3),
    p=round(float((np.sum(np.array(nulldiag) >= diag) + 1) / 301), 3),
    reading="diagonal high = labels sit in the right section (correct labeling). Strong off-diagonal = systematic displacement.")
# ---- M2 transposition viability: label types that never occur in ANY running text
textset = set(w for s in SECS for w in TEXT[s])
out["M2_transposition_viability"] = {s: dict(
    label_types=len(set(LABEL.get(s, []))),
    share_in_running_text=round(len([w for w in set(LABEL.get(s, [])) if w in textset]) / max(1, len(set(LABEL.get(s, [])))), 3))
    for s in SECS}
out["M2_note"] = ("If labels were displaced pieces of the running text (a transposition code), ~100% of label types "
    "would occur in the text. Types exclusive to labels cannot come from transposing the text.")

# ---- IMAGE ANCHOR (Stage C probe 2)
img = {"status": "skipped"}
if "--no-images" not in sys.argv:
    try:
        os.makedirs(CACHE, exist_ok=True)
        from PIL import Image
        man = json.load(urllib.request.urlopen(urllib.request.Request("https://collections.library.yale.edu/manifests/2002046", headers={"User-Agent": "research/1.0"}), timeout=40))
        svc = {}
        for c in man["items"]:
            lab = c["label"]["none"][0]; b = c["items"][0]["items"][0]["body"]["id"]
            svc["f" + lab] = b.replace("/full/full/0/default.jpg", "")
        herb = [f for f in PAGES if PAGES[f] == "H" and f in svc]
        herb = herb[:70]
        feats = {}; texts = {}
        # text per herbal folio
        tpage = collections.defaultdict(list)
        cur = None; sec = None
        for ln in open(ZL, encoding="utf-8", errors="replace"):
            h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
            if h: cur = h.group(1); sec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I"); continue
            m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*]P\d*>\s*(.*)", ln)
            if m and sec == "H": tpage[m.group(1)] += [root(clean(w)) for w in re.split(r"[.\s]+", m.group(2)) if clean(w)]
        for f in herb:
            fp = os.path.join(CACHE, f + ".jpg")
            if not os.path.exists(fp):
                try: urllib.request.urlretrieve(svc[f] + "/full/180,/0/default.jpg", fp)
                except Exception: continue
            try:
                a = np.asarray(Image.open(fp).convert("L").resize((120, 160)), float) / 255
            except Exception: continue
            ink = a < 0.55
            grid = ink.reshape(8, 20, 10, 12).mean(axis=(1, 3)).ravel()   # 8x10 ink-density map
            feats[f] = np.concatenate([grid, [ink.mean(), (ink.any(1).sum() / 160), (ink.any(0).sum() / 120)]])
            texts[f] = collections.Counter(tpage.get(f, []))
        fl = [f for f in herb if f in feats and texts.get(f)]
        if len(fl) >= 20:
            F = np.array([feats[f] for f in fl]); F = (F - F.mean(0)) / (F.std(0) + 1e-9)
            vd = np.linalg.norm(F[:, None] - F[None, :], axis=2)
            def tcos(a, b):
                ks = set(a) | set(b); da = math.sqrt(sum(v * v for v in a.values())); db = math.sqrt(sum(v * v for v in b.values()))
                return sum(a.get(k, 0) * b.get(k, 0) for k in ks) / (da * db + 1e-9)
            td = np.array([[1 - tcos(texts[x], texts[y]) for y in fl] for x in fl])
            iu = np.triu_indices(len(fl), 1); obs = float(np.corrcoef(vd[iu], td[iu])[0, 1])
            null = []
            for _ in range(2000):
                p = rng.permutation(len(fl)); null.append(np.corrcoef(vd[iu], td[np.ix_(p, p)][iu])[0, 1])
            img = dict(status="ok", herbal_folios=len(fl), mantel_r_visual_vs_text=round(obs, 3),
                       null_mean=round(float(np.mean(null)), 3), p=round(float((np.sum(np.array(null) >= obs) + 1) / 2001), 3),
                       caveat="crude ink-shape features; a null may mean weak features, not absence of an anchor",
                       reading="r>0 and p<0.05 = visually similar plants get similar text (an image anchor exists)")
        else: img = dict(status="too few folios", n=len(fl))
    except Exception as e:
        img = dict(status="error", error=str(e)[:200])
out["IMAGE_ANCHOR_stageC_probe2"] = img
json.dump(out, open(os.path.join(HERE, "mislabel_results.json"), "w"), indent=1)
print("sections:", SECS)
print("\nM1 label->text-section confusion (rows=label section):")
print("        " + "".join(f"{t:>7}" for t in SECS))
for s in SECS: print(f"  {s:<5}" + "".join(f"{confmat[s][t]:>7}" for t in SECS))
print(f"  diagonal {out['M1_label_matches_own_section']['mean_diagonal']} vs null {out['M1_label_matches_own_section']['null_mean']} p {out['M1_label_matches_own_section']['p']}")
print("\nM2 share of label types occurring in running text:", {s: out['M2_transposition_viability'][s]['share_in_running_text'] for s in SECS})
print("\nIMAGE ANCHOR:", json.dumps(img))
