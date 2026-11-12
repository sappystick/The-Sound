# Round 85 — the image-anchor test, and the mislabeling / displacement hypothesis

Two tests: the image anchor (Stage C probe 2) and the user's **mislabeling/displacement** idea — *what if the label at
a spot is not the right one for that picture, and the permutation (which label belongs where) is the code?* Both are
run rigorously, with controls. Script `voynich/mislabel.py`, results `voynich/mislabel_results.json`.

## 1. The mislabeling / displacement hypothesis

The idea has two testable forms; I tested both.

### M1 — are labels in the wrong section? (displacement)
For every label, find which section's running-text vocabulary (root profile) it best matches. If labels are correctly
placed, they match **their own** section; if displaced, they match **another** section systematically.

Confusion (rows = the label's actual section; columns = the text-section its words best match):

| label in ↓ / matches → | H | P | B | A | S | C |
|---|---|---|---|---|---|---|
| **H** herbal | 0.63 | 0.03 | 0.13 | 0.13 | 0.07 | 0 |
| **P** pharma | 0.57 | 0.09 | 0.06 | 0.13 | 0.09 | 0.06 |
| **B** balneo | 0.53 | 0.06 | 0.07 | 0.07 | 0.17 | 0.10 |
| **A** astro | 0.56 | 0.09 | 0.02 | 0.18 | 0.08 | 0.07 |

- **Diagonal (own-section match) 0.22 vs shuffle-null 0.15, p 0.003** — labels match their *own* section slightly more than a random reassignment. So labels are **weakly in the right place**, not systematically displaced to one other section.
- The big "everything matches H" column is a base-rate pull (herbal has the most text), which the permutation null already controls for — the p 0.003 diagonal excess survives it.
- **Verdict: no systematic displacement code.** There is no consistent "section X's labels really belong to section Y" permutation. The labels are where they belong, just noisily.

### M2 — are labels displaced pieces of the running text? (transposition)
A transposition code recycles the text's own words in a new order, so **every** label word would occur somewhere in
the running text.

| Section | share of label types that occur in the running text |
|---|---|
| Herbal | 0.42 |
| Pharma | 0.37 |
| Balneological | 0.66 |
| Astronomical | 0.49 |
| Stars/recipes | 0.00 |
| Cosmological | 0.54 |

- **34–63% of label words never appear in the running text at all.** A transposition of the text cannot produce words the text does not contain.
- **Verdict: labels are not transposed/displaced text.** This rules out the specific "the code is a reshuffle of the text's words" form of the idea.

### What survives of the idea
The one form I **cannot** test with these tools is a **picture↔label permutation keyed to correctly-identified
pictures** — "this label is the true name of *that* plant over there." That requires reliably identifying what each
picture depicts, which needs a vision model. It is a legitimate open possibility; it is just not decidable from text
statistics alone. Honestly: the testable forms of the displacement/mislabeling code are **not supported**, but the
vision-dependent form remains open.

## 2. The image anchor (Stage C probe 2)

Within the herbal section each folio is one highly-distinct plant. If the text names/describes the plant, **visually
similar plants should get similar text.** I downloaded 70 herbal folio thumbnails (Beinecke IIIF), computed a crude
ink-shape feature (an 8×10 ink-density map + extent), and ran a Mantel test of visual distance vs text (root) distance.

| | value |
|---|---|
| herbal folios | 70 |
| Mantel r (visual vs text) | **+0.098** |
| null mean | 0.00 |
| **p** | **0.078** |

- A **weak positive** association — visually similar plants do tend to have slightly more similar text — but it **does not reach significance** (p 0.078).
- **Honest caveat:** the features are crude (ink density on 600-year-old drawings). A null here may mean *weak features*, not *no anchor*. This probe is **feature-limited**, not decisive.

## 3. Gate C status and the honest frontier

| Stage-C probe | Referent | Result |
|---|---|---|
| probe 1 (round 84) | angular position | **null** (p 0.49) |
| probe 2 (this round) | picture appearance | **marginal, not significant** (r 0.10, p 0.08), feature-limited |
| displacement (M1) | own vs other section | labels weakly correct; **no displacement code** |
| transposition (M2) | label words in text | **labels aren't recycled text** |

**Gate C is not met:** no anchor reaches the pre-registered p < 0.01 bar. But I will **not** declare the section
H-EMPTY, because probe 2 is a non-significant *hint* limited by crude vision features, not a clean failure. The honest
state:

> The Voynich carries **coarse, topic-level meaning** (page vocabulary tracks the section, 90.8%), and the herbal text
> shows a **weak, unconfirmed** tendency to track plant appearance. But **no fine label→referent anchor survives at the
> rigour we require**, and the two "code via mislabeling" forms are ruled out. The one instrument that could break the
> tie is a **real vision model** on the plant drawings — the deciding tool we do not have here.

This is the wall, mapped precisely: not "undeciphered because no one tried the right trick," but "the measurable
anchors — position, text-recycling, displacement — are empty, and the picture-identity anchor is exactly as hard as
identifying 500-year-old drawn plants, which is the real bottleneck."

**Pipeline:** A pass · B partial · **C unmet (position null, image marginal, displacement/transposition ruled out);
decider = a vision model on the drawings.**
