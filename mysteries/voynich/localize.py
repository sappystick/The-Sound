#!/usr/bin/env python3
"""Round 82 seed: where does the Voynich's MEANING live? (`localize.py`)

Established: (a) a page's illustration-topic is predictable from its words (V1, 90.8%); (b) words = prefix+root+suffix
slots + copying (R80-81). New question: is the topic signal carried by the ROOT, or by the generative machinery
(prefix/suffix)? If the root carries it and affixes do not, meaning is localized to one slot - a decipherment wedge.

Data: ZL3b-n.txt (Zandbergen-Landini reference, with $I illustration / $L language / $H hand page metadata).
Method: within each (language,hand) group, leave-one-page-out nearest-centroid on TF-IDF, predicting $I. Run on
  FULL words, ROOT only (strip learned 12 prefixes + 16 suffixes), AFFIX only (prefix+suffix, root removed).
Null: shuffle the $I labels inside the group. Accuracy above null for ROOT but not AFFIX => meaning is in the root.
Usage: python3 mysteries/voynich/localize.py
"""
import collections, json, math, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ZL = os.path.join(ROOT, "sources/texts/voynich/ZL3b-n.txt")
rng = np.random.default_rng(82)
PREF = ["qo", "ch", "Sh", "sh", "ok", "ot", "da", "ol", "qok", "qot", "o", "y"]
SUFF = ["aiin", "iin", "edy", "eey", "dy", "ain", "ody", "chy", "hol", "eol", "ar", "or", "al", "y", "n", "ol"]

def parse():
    pages = {}; meta = {}; cur = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>\s*<!([^>]*)>", ln)
        if h:
            cur = h.group(1); tags = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9])", h.group(2)))
            meta[cur] = tags; pages.setdefault(cur, []); continue
        t = re.match(r"<(f\d+[rv]\d*)\.", ln)
        if not t: continue
        body = ln.split(">", 1)[1] if ">" in ln else ""
        body = re.sub(r"\{[^}]*\}", "", body)              # drive comments
        body = re.sub(r"<[^>]*>", "", body)                # inline markers <%> <-> <$>
        body = re.sub(r"[!*%?\[\]@]", "", body)            # uncertainty / rare markers
        words = [w for w in re.split(r"[.\s]+", body.strip()) if w and re.search(r"[a-zA-Z]", w)]
        pages[t.group(1)] += words
    return pages, meta

def strip_slots(w):
    p = next((p for p in sorted(PREF, key=len, reverse=True) if w.startswith(p) and len(w) - len(p) >= 2), "")
    rest = w[len(p):]
    s = next((s for s in sorted(SUFF, key=len, reverse=True) if rest.endswith(s) and len(rest) - len(s) >= 1), "")
    root = rest[:len(rest) - len(s)] if s else rest
    return p, root, s

def transform(words, mode):
    out = []
    for w in words:
        p, r, s = strip_slots(w)
        if mode == "full": out.append(w)
        elif mode == "root": out.append(r if r else w)
        elif mode == "affix": out.append((p + "_" + s) if (p or s) else "_")
    return out

def tfidf(pagewords):
    df = collections.Counter()
    for ws in pagewords: df.update(set(ws))
    nP = len(pagewords); vocab = {w: i for i, w in enumerate(df)}
    idf = {w: math.log(nP / df[w]) for w in df}
    M = np.zeros((nP, len(vocab)))
    for i, ws in enumerate(pagewords):
        c = collections.Counter(ws); n = sum(c.values()) or 1
        for w, k in c.items(): M[i, vocab[w]] = (k / n) * idf[w]
    nrm = np.linalg.norm(M, axis=1, keepdims=True); return M / np.where(nrm == 0, 1, nrm)

def loo_accuracy(M, labs):
    labs = np.array(labs); correct = 0
    for i in range(len(labs)):
        cents = {}
        for lab in set(labs):
            idx = [j for j in range(len(labs)) if j != i and labs[j] == lab]
            if idx: cents[lab] = M[idx].mean(0)
        pred = max(cents, key=lambda l: float(M[i] @ cents[l]))
        correct += pred == labs[i]
    return correct / len(labs)

def main():
    pages, meta = parse()
    groups = collections.defaultdict(list)
    for f, ws in pages.items():
        m = meta.get(f, {})
        if len(ws) >= 25 and "I" in m and "L" in m and "H" in m:
            groups[(m["L"], m["H"])].append((f, ws, m["I"]))
    res = {"modes": {}}
    pooled = {mode: dict(obs=0, n=0, null=np.zeros(300)) for mode in ("full", "root", "affix")}
    detail = []
    for (L, H), items in sorted(groups.items()):
        labs = [it[2] for it in items]
        if len(items) < 6 or len(set(labs)) < 2: continue
        row = dict(language=L, hand=H, pages=len(items), types=dict(collections.Counter(labs)))
        for mode in ("full", "root", "affix"):
            M = tfidf([transform(it[1], mode) for it in items])
            obs = loo_accuracy(M, labs)
            null = np.array([loo_accuracy(M, list(rng.permutation(labs))) for _ in range(300)])
            row[mode] = dict(accuracy=round(obs, 3), null_mean=round(float(null.mean()), 3), p=round(float((np.sum(null >= obs) + 1) / 301), 3))
            pooled[mode]["obs"] += obs * len(items); pooled[mode]["n"] += len(items); pooled[mode]["null"] += null * len(items)
        detail.append(row)
    res["groups"] = detail
    res["pooled"] = {mode: dict(accuracy=round(pooled[mode]["obs"] / pooled[mode]["n"], 3),
                                null_mean=round(float((pooled[mode]["null"] / pooled[mode]["n"]).mean()), 3),
                                p=round(float((np.sum(pooled[mode]["null"] / pooled[mode]["n"] >= pooled[mode]["obs"] / pooled[mode]["n"]) + 1) / 301), 3))
                     for mode in ("full", "root", "affix")}
    res["interpretation"] = ("If ROOT accuracy >> null and AFFIX accuracy approx null, the topic signal lives in the root slot "
                             "and the prefix/suffix machinery is content-free - so a decipherment should target roots, not whole words.")
    json.dump(res, open(os.path.join(HERE, "localize_results.json"), "w"), indent=1)
    print(f"{'group':<14}{'pages':>6}   full(acc/null)    root(acc/null)    affix(acc/null)")
    for r in detail:
        print(f"L{r['language']} H{r['hand']}{'':<6}{r['pages']:>6}   {r['full']['accuracy']:.2f}/{r['full']['null_mean']:.2f} p{r['full']['p']:<4} {r['root']['accuracy']:.2f}/{r['root']['null_mean']:.2f} p{r['root']['p']:<4} {r['affix']['accuracy']:.2f}/{r['affix']['null_mean']:.2f} p{r['affix']['p']}")
    print("\nPOOLED:", json.dumps(res["pooled"]))

if __name__ == "__main__": main()
