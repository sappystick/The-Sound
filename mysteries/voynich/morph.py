#!/usr/bin/env python3
"""Round 86 - plant morphometry: recreate each Voynich herbal drawing as precise CALCULATED geometry, then re-run
the image anchor with strong features (not the crude ink map of round 85).

No deep vision model: classical computer vision on the ink, built from scipy.ndimage + numpy.
Per herbal folio we download the image (Beinecke IIIF), segment the drawing from the text, and compute ~40
rotation/scale-aware morphometric features:
  mass/shape : ink area, bbox aspect, solidity, components, Hu moments (7, log) - invariant shape descriptors
  skeleton   : Zhang-Suen thinning -> total length, #branch points, #endpoints, branch density (plant topology)
  profiles   : vertical ink profile in 8 bands (root->stem->leaf->flower layering); radial profile in 6 rings
  angles     : stroke-orientation histogram (8 bins) from image gradients
  complexity : box-counting fractal dimension; left-right mirror symmetry
Then: Mantel test of morphometric distance vs text(root)-distance across folios, and kNN vocabulary overlap.
Also writes a reconstruction overlay for one folio (skeleton + branch points) to show the extracted geometry.
Usage: python3 mysteries/voynich/morph.py
"""
import collections, io, json, math, os, re, urllib.request
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
ZL = os.path.join(T, "voynich/ZL3b-n.txt"); rng = np.random.default_rng(86)
CACHE = "/tmp/claude-0/-home-user-The-Sound/5630df0b-07ac-5eb9-968f-9ce13efac22b/scratchpad/voy_hi"; os.makedirs(CACHE, exist_ok=True)
PREF = ["qok", "qot", "qo", "ych", "cho", "ch", "sho", "sh", "oto", "ot", "ok", "da", "ol", "or", "o", "y", "s", "d"]
SUFF = ["aiin", "oiin", "iin", "eedy", "eey", "edy", "eol", "ody", "chy", "hey", "ain", "dy", "ol", "ar", "or", "al", "hy", "y", "n"]
def root(w):
    p = next((p for p in PREF if w.startswith(p) and len(w) - len(p) >= 1), ""); rest = w[len(p):]
    s = next((s for s in SUFF if rest.endswith(s) and len(rest) - len(s) >= 1), ""); r = rest[:len(rest) - len(s)] if s else rest
    return r or w
def clean(w):
    w = re.sub(r"\{[^}]*\}", "", w); w = re.sub(r"<[^>]*>", "", w); w = re.sub(r"\[([a-zA-Z]):[^\]]*\]", r"\1", w)
    return re.sub(r"[!*%?\[\]@=\-]", "", w).strip()

# ---------- metadata + herbal folio text
def load():
    sec = {}; svc = {}; cur = None; cursec = None; tpage = collections.defaultdict(list)
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h: cur = h.group(1); cursec = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2))).get("I"); sec[cur] = cursec; continue
        m = re.match(r"<(f\d+[rv]\d*)\.\d+,[@&+*]P\d*>\s*(.*)", ln)
        if m and cursec == "H": tpage[m.group(1)] += [root(clean(w)) for w in re.split(r"[.\s]+", m.group(2)) if clean(w)]
    man = json.load(urllib.request.urlopen(urllib.request.Request("https://collections.library.yale.edu/manifests/2002046", headers={"User-Agent": "research/1.0"}), timeout=40))
    for c in man["items"]:
        lab = c["label"]["none"][0]; svc["f" + lab] = c["items"][0]["items"][0]["body"]["id"].replace("/full/full/0/default.jpg", "")
    return sec, svc, tpage

def otsu(a):
    h, _ = np.histogram(a, 256, (0, 1)); tot = a.size; s = np.arange(256)
    w0 = np.cumsum(h); w1 = tot - w0; m0 = np.cumsum(s * h) / np.maximum(w0, 1); m1 = (np.cumsum((s * h)[::-1])[::-1]) / np.maximum(w1, 1)
    var = w0[:-1] * w1[:-1] * (m0[:-1] - m1[:-1]) ** 2
    return (np.argmax(var) / 255) if var.size else 0.5

def segment(gray):
    th = otsu(gray); ink = gray < th * 0.9
    lbl, n = ndi.label(ink)
    if n == 0: return ink, 0.0
    page = ink.size; keep = np.zeros_like(ink); H, W = ink.shape
    border = set(np.unique(np.r_[lbl[0], lbl[-1], lbl[:,0], lbl[:,-1]])) - {0}   # components touching the edge = page/binding
    sizes = ndi.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    # text rows: bands with many small components; estimate glyph size and drop components in dense small-comp bands
    for i in range(1, n + 1):
        if i in border: continue
        if sizes[i-1] < 0.0025 * page: continue        # drop tiny glyphs
        ys, xs = np.where(lbl == i)
        if (ys.max()-ys.min()+1) < 0.03*H and (xs.max()-xs.min()+1) < 0.06*W: continue  # drop small boxy text bits
        keep |= (lbl == i)
    return keep, keep.sum() / max(1, ink.sum())

def zhang_suen(img):
    I = img.astype(np.uint8).copy()
    def nb(I):
        P = [np.roll(np.roll(I, dy, 0), dx, 1) for dy, dx in [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]]
        return P
    changed = True; it = 0
    while changed and it < 60:
        changed = False; it += 1
        for step in (0, 1):
            P = nb(I); P2,P3,P4,P5,P6,P7,P8,P9 = P
            C = sum(P)  # neighbor count B(P1)
            seq = [P2,P3,P4,P5,P6,P7,P8,P9,P2]
            A = sum(((seq[k] == 0) & (seq[k+1] == 1)).astype(np.uint8) for k in range(8))  # 0->1 transitions
            if step == 0: c1 = (P2*P4*P6 == 0); c2 = (P4*P6*P8 == 0)
            else: c1 = (P2*P4*P8 == 0); c2 = (P2*P6*P8 == 0)
            m = (I == 1) & (C >= 2) & (C <= 6) & (A == 1) & c1 & c2
            if m.any(): I[m] = 0; changed = True
    return I

def features(keep):
    ys, xs = np.where(keep)
    if len(xs) < 50: return None
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max(); H = y1 - y0 + 1; W = x1 - x0 + 1
    crop = keep[y0:y1+1, x0:x1+1].astype(float)
    area = crop.sum(); f = {}
    f["aspect"] = W / H; f["fill"] = area / (H * W)
    lbl, n = ndi.label(crop); f["components"] = n
    # solidity ~ area / area of filled convex-ish hull (use filled binary dilation-close as proxy)
    filled = ndi.binary_fill_holes(crop > 0); f["solidity"] = area / max(1, filled.sum())
    # Hu moments (log-abs)
    yy, xx = np.mgrid[0:crop.shape[0], 0:crop.shape[1]].astype(float); m00 = area
    xc = (xx * crop).sum() / m00; yc = (yy * crop).sum() / m00
    def mu(p, q): return (((xx - xc) ** p) * ((yy - yc) ** q) * crop).sum()
    def eta(p, q): return mu(p, q) / (m00 ** (1 + (p + q) / 2))
    n20, n02, n11, n30, n12, n21, n03 = eta(2,0),eta(0,2),eta(1,1),eta(3,0),eta(1,2),eta(2,1),eta(0,3)
    hu = [n20+n02, (n20-n02)**2+4*n11**2, (n30-3*n12)**2+(3*n21-n03)**2, (n30+n12)**2+(n21+n03)**2,
          (n30-3*n12)*(n30+n12)*((n30+n12)**2-3*(n21+n03)**2)+(3*n21-n03)*(n21+n03)*(3*(n30+n12)**2-(n21+n03)**2),
          (n20-n02)*((n30+n12)**2-(n21+n03)**2)+4*n11*(n30+n12)*(n21+n03),
          (3*n21-n03)*(n30+n12)*((n30+n12)**2-3*(n21+n03)**2)-(n30-3*n12)*(n21+n03)*(3*(n30+n12)**2-(n21+n03)**2)]
    for i, h in enumerate(hu): f[f"hu{i+1}"] = -math.copysign(math.log10(abs(h) + 1e-30), h)
    # skeleton topology
    sk = zhang_suen(crop > 0); f["skel_len"] = sk.sum() / area
    nbrs = sum(np.roll(np.roll(sk, dy, 0), dx, 1) for dy in (-1,0,1) for dx in (-1,0,1) if (dy,dx)!=(0,0))
    f["branch_pts"] = int(((sk == 1) & (nbrs >= 3)).sum()); f["end_pts"] = int(((sk == 1) & (nbrs == 1)).sum())
    f["branch_density"] = f["branch_pts"] / max(1, sk.sum())
    # vertical profile (8 bands top->bottom = flower..root layering) and radial (6 rings)
    vb = [crop[int(k*H/8):int((k+1)*H/8)].sum() / area for k in range(8)]
    for k, v in enumerate(vb): f[f"vband{k}"] = v
    rr = np.sqrt((xx - xc)**2 + (yy - yc)**2); rmax = rr.max() + 1e-9
    for k in range(6): f[f"ring{k}"] = crop[(rr >= k*rmax/6) & (rr < (k+1)*rmax/6)].sum() / area
    # stroke orientation histogram (gradients)
    gy, gx = np.gradient(ndi.gaussian_filter(crop, 1)); ang = (np.degrees(np.arctan2(gy, gx)) % 180); mag = np.sqrt(gx**2+gy**2)
    hist, _ = np.histogram(ang[mag > mag.mean()], 8, (0, 180)); hist = hist / (hist.sum()+1e-9)
    for k, v in enumerate(hist): f[f"ang{k}"] = v
    # fractal dimension (box counting)
    counts = []; sizes = [2,4,8,16,32]
    for s in sizes:
        hh = -(-crop.shape[0]//s); ww = -(-crop.shape[1]//s)
        pad = np.zeros((hh*s, ww*s)); pad[:crop.shape[0], :crop.shape[1]] = crop > 0
        counts.append((pad.reshape(hh, s, ww, s).sum(axis=(1,3)) > 0).sum())
    f["fractal_dim"] = -np.polyfit(np.log(sizes), np.log(np.maximum(counts,1)), 1)[0]
    # left-right symmetry
    half = crop[:, :W//2]; mir = crop[:, W-W//2:][:, ::-1]
    f["lr_symmetry"] = float((half*mir).sum() / (math.sqrt((half**2).sum()*(mir**2).sum())+1e-9))
    return f, sk, (y0, x0, H, W)

def main():
    sec, svc, tpage = load()
    herb = [f for f in sec if sec[f] == "H" and f in svc and tpage.get(f)]
    feats, texts, sample = {}, {}, None
    for f in herb:
        fp = os.path.join(CACHE, f + ".jpg")
        if not os.path.exists(fp):
            try: urllib.request.urlretrieve(svc[f] + "/full/500,/0/default.jpg", fp)
            except Exception: continue
        try: a = np.asarray(Image.open(fp).convert("L"), float) / 255
        except Exception: continue
        keep, frac = segment(a)
        r = features(keep)
        if r is None: continue
        feats[f], sk, box = r; texts[f] = collections.Counter(tpage[f])
        if sample is None and feats[f]["components"] <= 4: sample = (f, a, keep, sk, box)
    fl = [f for f in feats if texts.get(f)]
    out = {"herbal_folios_processed": len(fl), "n_features": len(next(iter(feats.values()))) if feats else 0,
           "feature_names": sorted(next(iter(feats.values()))) if feats else []}
    if len(fl) >= 25:
        names = sorted(feats[fl[0]]); F = np.array([[feats[f][k] for k in names] for f in fl])
        F = np.nan_to_num((F - F.mean(0)) / (F.std(0) + 1e-9))
        vd = np.linalg.norm(F[:, None] - F[None, :], axis=2)
        def tcos(a, b):
            ks = set(a) | set(b); da = math.sqrt(sum(v*v for v in a.values())); db = math.sqrt(sum(v*v for v in b.values()))
            return sum(a.get(k,0)*b.get(k,0) for k in ks)/(da*db+1e-9)
        td = np.array([[1 - tcos(texts[x], texts[y]) for y in fl] for x in fl])
        iu = np.triu_indices(len(fl), 1); obs = float(np.corrcoef(vd[iu], td[iu])[0, 1])
        null = [float(np.corrcoef(vd[iu], td[np.ix_(p:=rng.permutation(len(fl)), p)][iu])[0,1]) for _ in range(3000)]
        # kNN vocabulary overlap: for each folio, are its 5 morphometric-nearest also text-near?
        k = 5; knn_obs = [];
        for i in range(len(fl)):
            vn = np.argsort(vd[i]); vn = [j for j in vn if j != i][:k]
            knn_obs.append(np.mean([1 - td[i, j] for j in vn]))
        rand = [np.mean([1 - td[i, j] for j in rng.choice([x for x in range(len(fl)) if x != i], k, replace=False)]) for i in range(len(fl)) for _ in range(1)]
        out["anchor"] = dict(mantel_r=round(obs, 3), null_mean=round(float(np.mean(null)), 3),
            p=round(float((np.sum(np.array(null) >= obs) + 1) / 3001), 4),
            knn5_text_sim=round(float(np.mean(knn_obs)), 3), random_text_sim=round(float(np.mean(rand)), 3),
            improvement_over_round85="round85 crude features: r 0.10 p 0.078")
        # which features drive it: correlation of each feature-distance with text-distance
        drivers = {}
        for ci, nm in enumerate(names):
            fdd = np.abs(F[:, ci][:, None] - F[:, ci][None, :])[iu]
            drivers[nm] = round(float(np.corrcoef(fdd, td[iu])[0, 1]), 3)
        out["top_feature_drivers"] = dict(sorted(drivers.items(), key=lambda kv: -kv[1])[:10])
    # reconstruction overlay
    if sample:
        f, a, keep, sk, (y0, x0, H, W) = sample
        rgb = np.stack([a]*3, -1);
        sub = rgb[y0:y0+H, x0:x0+W]
        sub[keep[y0:y0+H, x0:x0+W] > 0] = sub[keep[y0:y0+H, x0:x0+W] > 0]*0.6 + np.array([0.0,0.3,0.9])*0.4  # ink in blue
        sub[sk > 0] = [1,0,0]                                                                                 # skeleton red
        Image.fromarray((np.clip(rgb,0,1)*255).astype(np.uint8)).save(os.path.join(HERE, "morph_sample.png"))
        out["reconstruction_sample"] = dict(folio=f, file="mysteries/voynich/morph_sample.png", note="blue=segmented plant ink, red=calculated skeleton")
    json.dump(out, open(os.path.join(HERE, "morph_results.json"), "w"), indent=1)
    print("folios:", out["herbal_folios_processed"], "features/plant:", out["n_features"])
    if "anchor" in out:
        print("ANCHOR (strong morphometric features):", json.dumps(out["anchor"]))
        print("top drivers:", json.dumps(out["top_feature_drivers"]))
    print("reconstruction:", out.get("reconstruction_sample", {}).get("folio"))

if __name__ == "__main__": main()
