# Round 86 — plant morphometry: recreating the drawings as calculated geometry, and the decisive image anchor

The user's idea: don't just *look* at the plant drawings — **recreate each one as precise calculated geometry**
(spatial, angular, shadow/ink, skeletal), which yields far more data points than visual inspection, then test whether
that geometry predicts the text. Done, with no deep-learning model — classical computer vision built from
`scipy.ndimage` + NumPy. Script `voynich/morph.py`, results `voynich/morph_results.json`, reconstruction
`voynich/morph_sample.png`.

## 1. The method — each plant becomes ~40 numbers
For every herbal folio (Beinecke IIIF image): segment the drawing from the page (remove the binding/border components
and the text by size), then compute a **39-feature morphometric fingerprint**:

| group | features |
|---|---|
| mass & shape | ink area, bbox aspect, fill, solidity, component count, **7 Hu moments** (rotation/scale-invariant shape) |
| **skeleton / topology** | Zhang–Suen thinning → total length, **branch points**, **endpoints**, branch density (the plant's branching structure) |
| layering | vertical ink profile in 8 bands (flower→stem→root), radial profile in 6 rings |
| stroke angles | 8-bin orientation histogram from image gradients |
| complexity | **box-counting fractal dimension**, left–right mirror symmetry |

The reconstruction overlay (`morph_sample.png`, folio f3v) shows it working: the plant ink segmented out (blue), the
**calculated skeleton** traced through it (red), page border and text excluded. This is the "recreate as data"
deliverable — each drawing turned into measured geometry, ~40 dimensions instead of an eyeball impression.

## 2. The result — zero
Mantel test: morphometric distance between plants vs text (root-vocabulary) distance, across the herbal folios, with
a 3000-permutation null.

| features | folios | Mantel r | p |
|---|---|---|---|
| round 85 (crude 8×10 ink map) | 70 | +0.10 | 0.078 (marginal) |
| round 86 (39 morphometric, 1st segmentation) | 118 | −0.05 | 0.90 |
| **round 86 (39 morphometric, clean segmentation)** | **74** | **−0.003** | **0.53** |

- The 5 morphometric-nearest plants to each folio are **no more text-similar than random** (0.487 vs 0.483).
- No single feature predicts the text (top driver correlation ≈ 0.06 — noise).
- **The better the shape features, the weaker the correlation** — crude features gave a marginal hint; comprehensive
  geometry gives exactly zero. So round 85's r = 0.10 was a **segmentation/feature artifact, not a real anchor.**

**The Voynich herbal text does not describe, name, or track the specific plant drawn next to it** — at least not
through any aspect of the drawing's geometry (shape, topology, layering, angle, complexity, symmetry).

## 3. Stage C: both probes have now failed (the pre-registered rule triggers)
| Stage-C probe | referent | result |
|---|---|---|
| probe 1 (round 84) | angular position | null (p 0.49) |
| **probe 2 (round 86)** | **plant geometry** | **null (p 0.53), robust** |

Two independent anchor probes, both null. By the plan's pre-registered decision rule (**two failed probes → H-EMPTY
for that section at the object level**), the conclusion for the herbal section is now earned, not guessed:

> **The herbal text carries no recoverable object-level reference.** Its words are not bound to the individual plants.

## 4. The synthesis this whole investigation has reached
Put the two robust facts side by side:
- **Section level (S6):** page vocabulary predicts the illustration *type* at 90.8% — the text is "about" herbs on
  herb pages, stars on star pages. Real, coarse meaning.
- **Object level (rounds 84 + 86):** the text does **not** encode which plant, via position or geometry. No fine
  reference.

**The Voynich is topical but not referential.** It shifts its vocabulary by subject section, yet within a section it
does not name the specific thing depicted. That is the sharpest, best-supported characterization the engine has
produced, and it fits one surviving model: a **section-conditioned generative system** — the generator (slots +
self-citation, rounds 80–83) is primed with a different word-pool per section, producing subject-appropriate text
without encoding specific referents. It is neither a readable herbal nor white noise; it is **meaningful about
categories and empty about individuals.**

## 5. Honest limits
- A **deep botanical-ID model** might read diagnostic features that classical morphometry misses. But the evidence
  cuts against a hidden anchor: moving from crude to comprehensive geometry drove the correlation to zero, not up.
- Medieval herbal drawings are often schematic or chimeric, so even a perfect reader might find no botanical identity
  to match — but that itself would mean the drawings carry no object reference for the text to track.
- Segmentation is heuristic; the reconstruction overlay shows it works on clean folios, and the result held across
  two segmentation methods and 74–118 folios.

**Pipeline status:** A pass · B partial · **C failed (both anchor probes null) → herbal section is topical-not-
referential by the pre-registered rule.** The honest end-state for the text: *the Voynich means at the level of
sections, not of things.* Where a decipherment needs object reference, the manuscript — rigorously, repeatedly —
does not provide it.
