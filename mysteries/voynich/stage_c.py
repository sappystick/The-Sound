#!/usr/bin/env python3
"""Round 84 - Stage C (ANCHOR): bind Voynich labels to an external, measurable referent - angular position.

The zodiac diagrams carry ~30 ring labels each, and the ZL transliteration records each label's CLOCK POSITION
(<!HH:MM>) - its angle around the ring. Angle is a physical referent we can read without interpreting the pictures.
Gate (PLAN.md): >= 5 anchors each consistent across >= 2 independent pages. Here an 'anchor' = a reproducible
mapping from angular position to a label feature (initial glyph / suffix / length) that holds across diagrams.

Tests:
  C1  Ring regularity: are a diagram's labels spaced evenly in angle (consistent with a 30-position day-ring)?
  C2  Angle -> feature within a diagram: does a label's initial glyph / length / suffix depend on its angle?
      (circular-to-categorical association, permutation null per diagram)
  C3  CROSS-DIAGRAM ANCHOR (the gate): bin angle into 12 sectors; is the angle->initial-glyph map SHARED across
      diagrams? Train the map on half the diagrams, predict the labels' initial glyph on the held-out diagrams
      from angle alone. Null: shuffle each held-out label's angle. >= 2-page reproducibility, p<0.01 = anchor found.
  C4  Sequence order: sort each diagram's labels by angle; is the glyph sequence more repetitive / ordered than a
      shuffle (a day-counter would repeat a motif every k positions)?
Usage: python3 mysteries/voynich/stage_c.py
"""
import collections, json, math, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
ZL = os.path.join(T, "voynich/ZL3b-n.txt")
rng = np.random.default_rng(84)

def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@]", "", w).strip()

def load_zodiac_labels():
    """return {page: [(angle_deg, label_text), ...]} for label loci that carry a clock position."""
    pages = collections.defaultdict(list); cur = None; typ = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h: cur = h.group(1); typ = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))); continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*](L[a-z]?|C[a-z]?)>\s*<!(\d{1,2}):(\d{2})>\s*(.*)", ln)
        if not m: continue
        page, loc, hh, mm, body = m.groups()
        if typ is None or typ.get("I") != "Z":        # zodiac pages only
            continue
        ang = (int(hh) % 12) * 30 + int(mm) / 60 * 30   # clock -> degrees
        lab = clean(body.split(".")[0] if "." in body else body)
        if lab and re.search(r"[a-zA-Z]", lab): pages[page].append((ang % 360, lab))
    return {p: v for p, v in pages.items() if len(v) >= 10}

Z = load_zodiac_labels()
out = {"diagrams": {p: len(v) for p, v in sorted(Z.items())}, "n_diagrams": len(Z), "total_labels": sum(len(v) for v in Z.values())}

# ---- C1 ring regularity
c1 = {}
for p, v in Z.items():
    angs = np.sort([a for a, _ in v]); gaps = np.diff(np.r_[angs, angs[0] + 360])
    c1[p] = dict(n=len(v), gap_cv=round(float(np.std(gaps) / (np.mean(gaps) + 1e-9)), 3), expected_if_30=round(360/30, 1), mean_gap=round(float(np.mean(gaps)), 1))
out["C1_ring_regularity"] = dict(per_diagram=c1, note="gap_cv near 0 = evenly spaced ring; ~30 labels at ~12 deg spacing fits a day-ring")

# ---- C2 angle -> initial glyph within a diagram (circular association via permutation)
def circ_assoc(v):
    # association between angle and initial glyph: variance of mean-angle across glyph groups vs shuffled
    labs = [w[0] for _, w in v]; angs = np.array([a for a, _ in v])
    groups = collections.defaultdict(list)
    for g, a in zip(labs, angs): groups[g].append(a)
    def stat(aa):
        gg = collections.defaultdict(list)
        for g, a in zip(labs, aa): gg[g].append(a)
        # mean resultant length per group (circular concentration), weighted
        R = 0.0
        for g, al in gg.items():
            if len(al) >= 2:
                z = np.mean(np.exp(1j * np.radians(al))); R += len(al) * abs(z)
        return R / len(labs)
    obs = stat(angs); null = np.array([stat(rng.permutation(angs)) for _ in range(500)])
    return round(obs, 3), round(float(null.mean()), 3), round(float((np.sum(null >= obs) + 1) / 501), 3)
c2 = {p: dict(zip(("obs", "null", "p"), circ_assoc(v))) for p, v in Z.items()}
out["C2_angle_to_initial_glyph"] = dict(per_diagram=c2, significant=[p for p, r in c2.items() if r["p"] < 0.05])

# ---- C3 cross-diagram anchor (THE GATE): is angle->initial-glyph shared across diagrams?
def sector(a, k=12): return int(a // (360 / k))
items = [(p, sector(a), w[0]) for p, v in Z.items() for a, w in v]
dpages = sorted(Z)
half = len(dpages) // 2
splits = []
for rep in range(200):
    perm = list(rng.permutation(dpages)); tr, te = set(perm[:half]), set(perm[half:])
    # learn angle-sector -> most common initial glyph on train
    m = collections.defaultdict(collections.Counter)
    for p, s, g in items:
        if p in tr: m[s][g] += 1
    pred = {s: (c.most_common(1)[0][0] if c else None) for s, c in m.items()}
    te_items = [(s, g) for p, s, g in items if p in te]
    acc = np.mean([pred.get(s) == g for s, g in te_items]) if te_items else 0
    # null: shuffle held-out angles
    sec_te = [s for s, _ in te_items]; gl_te = [g for _, g in te_items]
    nacc = np.mean([pred.get(s) == g for s, g in zip(rng.permutation(sec_te), gl_te)]) if te_items else 0
    splits.append((acc, nacc))
splits = np.array(splits)
base = max(collections.Counter(g for _, _, g in items).values()) / len(items)   # majority-class baseline
out["C3_cross_diagram_anchor"] = dict(
    mean_heldout_accuracy=round(float(splits[:, 0].mean()), 3), mean_null_accuracy=round(float(splits[:, 1].mean()), 3),
    majority_class_baseline=round(float(base), 3),
    p=round(float((np.sum(splits[:, 1] >= splits[:, 0].mean()) + 1) / 201), 3),
    gate_anchor_reproducible=bool(splits[:, 0].mean() > max(splits[:, 1].mean(), base) + 0.03 and (np.sum(splits[:, 1] >= splits[:, 0].mean()) + 1) / 201 < 0.01),
    note="predict a held-out diagram's label initial glyph from angular sector alone, map learned on other diagrams")

# ---- C4 sequence order: glyph-sequence repetition around the ring vs shuffle
def seq_rep(v):
    seq = [w[0] for a, w in sorted(v)]
    adj = sum(1 for a, b in zip(seq, seq[1:]) if a == b)
    null = []
    for _ in range(500):
        s = list(seq); rng.shuffle(s); null.append(sum(1 for a, b in zip(s, s[1:]) if a == b))
    return adj, round(float(np.mean(null)), 2), round(float((np.sum(np.array(null) >= adj) + 1) / 501), 3)
c4 = {p: dict(zip(("adj_equal", "null", "p"), seq_rep(v))) for p, v in Z.items()}
out["C4_sequence_order"] = dict(per_diagram=c4, significant=[p for p, r in c4.items() if r["p"] < 0.05])

out["GATE_C"] = dict(
    anchors_found=out["C3_cross_diagram_anchor"]["gate_anchor_reproducible"],
    c2_significant_diagrams=len(out["C2_angle_to_initial_glyph"]["significant"]),
    verdict=("ANCHOR REPRODUCIBLE across diagrams" if out["C3_cross_diagram_anchor"]["gate_anchor_reproducible"]
             else "no reproducible angle->text anchor; labels do not encode a shared positional code"))
json.dump(out, open(os.path.join(HERE, "stage_c_results.json"), "w"), indent=1)
print("zodiac diagrams:", out["n_diagrams"], "total labels:", out["total_labels"])
print("C1 ring gap CV (even ring ~0):", {p: r["gap_cv"] for p, r in c1.items()})
print("C2 angle->initial glyph significant in", len(out["C2_angle_to_initial_glyph"]["significant"]), "of", len(Z), "diagrams")
print("C3 cross-diagram anchor:", json.dumps(out["C3_cross_diagram_anchor"]))
print("C4 ring-sequence repetition significant in", len(out["C4_sequence_order"]["significant"]), "of", len(Z))
print("\nGATE C:", out["GATE_C"]["verdict"])
