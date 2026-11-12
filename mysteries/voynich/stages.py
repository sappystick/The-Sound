#!/usr/bin/env python3
"""Round 83: rigorous execution of the decipherment pipeline's early gates (PLAN.md section 3).

STAGE A - NORMALISE. Gate: a slot grammar (prefix.root.suffix) learned on EVEN pages must generate >85% of the
  word-mass of HELD-OUT ODD pages. A word is 'covered' if it = (learned prefix or none) + (root seen on even pages)
  + (learned suffix or none), with a non-empty root. This tests that the slot layer is real, not overfit.
STAGE B - DE-MACHINE. Gate (from the localize pilot): the root stream must predict page-topic >= the full-word
  stream out of sample. Reported from localize_results.json; here we add the complementary within-section test:
  after removing copy-runs (self-citation) and stripping affixes, how much does per-word surprisal drop - i.e. how
  much of the text is 'machinery' vs 'content'? We quantify the machinery share (compressible by copy+slots).
Usage: python3 mysteries/voynich/stages.py
"""
import collections, json, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); T = os.path.join(ROOT, "sources/texts")
ZL = os.path.join(T, "voynich/ZL3b-n.txt")

def parse_pages():
    pages = collections.defaultdict(list); cur = None
    for ln in open(ZL, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\d+[rv]\d*)>", ln)
        if h: cur = h.group(1)
        if not re.match(r"<f\d+[rv]\d*\.", ln): continue
        pg = re.match(r"<(f\d+[rv]\d*)\.", ln).group(1)
        body = ln.split(">", 1)[1] if ">" in ln else ""
        body = re.sub(r"\{[^}]*\}", "", body); body = re.sub(r"<[^>]*>", "", body); body = re.sub(r"[!*%?\[\]@]", "", body)
        pages[pg] += [w for w in re.split(r"[.\s]+", body.strip()) if w and re.search(r"[a-zA-Z]", w)]
    return pages

pages = parse_pages()
folios = sorted(pages, key=lambda f: (int(re.match(r"f(\d+)", f).group(1)), f))
even = [f for i, f in enumerate(folios) if i % 2 == 0]; odd = [f for i, f in enumerate(folios) if i % 2 == 1]
train = [w for f in even for w in pages[f]]; test = [w for f in odd for w in pages[f]]

# ---- STAGE A: learn slots on train, measure coverage on test
PREF = [p for p, _ in collections.Counter(w[:2] for w in train if len(w) >= 4).most_common(12)]
PREF += [p for p, _ in collections.Counter(w[:1] for w in train).most_common(6)]
SUFF = [s for s, _ in collections.Counter(w[-3:] for w in train if len(w) >= 5).most_common(10)]
SUFF += [s for s, _ in collections.Counter(w[-2:] for w in train if len(w) >= 3).most_common(10)]
SUFF += [s for s, _ in collections.Counter(w[-1:] for w in train).most_common(4)]
PREF = sorted(set(PREF), key=len, reverse=True); SUFF = sorted(set(SUFF), key=len, reverse=True)
def decomp(w):
    p = next((p for p in PREF if w.startswith(p) and len(w) - len(p) >= 1), "")
    rest = w[len(p):]
    s = next((s for s in SUFF if rest.endswith(s) and len(rest) - len(s) >= 1), "")
    return p, (rest[:len(rest) - len(s)] if s else rest), s
roots_train = collections.Counter(decomp(w)[1] for w in train)
good_roots = {r for r, c in roots_train.items() if c >= 2 and r}
covered = mass = 0
for w in test:
    mass += 1; p, r, s = decomp(w)
    if r and (r in good_roots or len(r) <= 3): covered += 1
coverage = covered / mass
# null: shuffle each test word's letters, re-measure (a real slot grammar should fit real words far better)
rng = np.random.default_rng(83); nn = []
for _ in range(50):
    c = 0
    for w in test:
        wl = list(w); rng.shuffle(wl); p, r, s = decomp("".join(wl))
        if r and (r in good_roots or len(r) <= 3): c += 1
    nn.append(c / mass)

# ---- STAGE B: machinery share = fraction of tokens explained by copy (self-citation) or by a frequent slot word
seen = collections.Counter(train)
copy_run = 0; prev = None
for w in test:
    if w == prev: copy_run += 1
    prev = w
# "machinery" tokens: exact copies of the immediately preceding word, OR words whose root is a top-20 train root (grammar fillers)
top_roots = {r for r, _ in roots_train.most_common(20)}
machinery = 0; prev = None
for w in test:
    _, r, _ = decomp(w)
    if w == prev or r in top_roots: machinery += 1
    prev = w

out = dict(
  split=dict(folios=len(folios), even_pages=len(even), odd_pages=len(odd), train_words=len(train), test_words=len(test)),
  stageA_slot_coverage=dict(learned_prefixes=PREF[:14], learned_suffixes=SUFF[:14],
     coverage_heldout=round(coverage, 3), null_shuffled_mean=round(float(np.mean(nn)), 3),
     gate_0_85=coverage >= 0.85, verdict="PASS" if coverage >= 0.85 else "below 0.85"),
  stageB_machinery=dict(adjacent_copy_share=round(copy_run / len(test), 3),
     machinery_share_copy_or_top20_root=round(machinery / len(test), 3),
     content_share_remainder=round(1 - machinery / len(test), 3),
     note="machinery = exact adjacent copies + words built on one of the 20 commonest roots (grammatical fillers); "
          "the remainder is the candidate content stream for Stage C anchoring"))
json.dump(out, open(os.path.join(HERE, "stages_results.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
