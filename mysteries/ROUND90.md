# Round 90 — concept-cluster discovery on the content-word layer

Round 89 found the content-word layer (specific bursty words carrying the long-range information no generative model
reproduces). This round asks the obvious next question with a real instrument: **do those content words organise into
coherent concept groups, and are the groups genuinely finer than the illustration sections — or just the sections and
the grammar again?** Script `voynich/concepts.py`; results `voynich/concepts_results.json`. Method: windowed PPMI
co-occurrence of the 114 bursty content words → Newman spectral communities → four controls (random partition,
section partition, morphology, and a section-conditioned **generator ensemble**).

## 1. The content words form two real communities — and they are the Currier A/B languages
Newman spectral detection on the co-occurrence graph returns **2 communities** (67 and 47 words):

| community | member flavour | dominant section | reads as |
|---|---|---|---|
| 1 | `qokain qokeedy qol shedy qokedy qoteedy keedy` | stars/recipes + balneo | **Currier B language** |
| 2 | `cthy chor cthol sho qotor cthor qotchy chaiin` | herbal (91%) | **Currier A language** |

- **Modularity Q = 0.264** vs a random partition of the same group sizes **−0.004 ± 0.011** — a real partition, not
  an artifact (>20σ).
- **MI(group; section) / H(group) = 0.76** — three-quarters of the top-level split *is* the section/language division.

So the content-word co-occurrence graph **independently re-derives the famous Currier A/B language split** — the
herbal `cth-/-or` vocabulary vs the `qok-/-edy` balneological-and-stars vocabulary — from word association alone, with
no prior labels. That the A/B division falls straight out of bursty-word co-occurrence is a genuine, if confirmatory,
structural result.

## 2. The grouping exceeds both the sections and the grammar
Two controls show the grouping is not *merely* re-labelling what we already had:

- **Beats the section partition.** Assigning each word to its own dominant section scores Q = 0.214 on the same
  graph; the discovered partition scores **0.264**. The co-occurrence groups capture association the section labels
  miss.
- **Not reducible to morphology.** Co-occurrence clustering of a slot-grammar text *will* group affix-families, so we
  measured it: correlation of co-occurrence weight with shared-affix = only **0.17**; the discovered partition is more
  coherent on the co-occurrence graph (Q 0.264) than on a morphology graph (Q 0.162); and decisively, **for word
  pairs that share no prefix or suffix, within-group co-occurrence (0.50) is 3× cross-group (0.16).** Real word
  association survives after removing morphology.

## 3. Finer sub-topics: weak, and only in the herbal section (the honest limit)
The tempting claim is "each section subdivides into sub-topics." A naïve test (Newman vs a random *partition*) says
yes everywhere — but that test is rigged: Newman finds positive modularity on almost any frequency-heterogeneous
graph. The honest null is the **section-conditioned iid generator** (rounds 87–88) run as an ensemble: does the real
within-section community structure exceed what iid draws from the same section word-pool produce?

| section | real within-section Q | generator ensemble (mean ± sd, 95th pct) | real exceeds generator? |
|---|---|---|---|
| herbal (H) | 0.113 | 0.089 ± 0.009 (95th 0.105) | **yes, +0.024** |
| balneo (B) | 0.118 | 0.109 ± 0.021 (95th 0.141) | **no (+0.008, inside the spread)** |

- **Most of the within-section community structure is reproduced by the iid generator** — it is a frequency/method
  effect, not content.
- The **herbal** section carries a small but real excess over the generator (+0.024, above the 95th percentile): a
  faint hint of genuine sub-topic organisation among the herbal content words.
- The **balneological** section shows **no** excess — its apparent sub-topics are within the generator's range.

So finer-than-section topical organisation is, at best, **weak and section-specific**, not a strong uniform layer.
This tempers round 89: the content-word layer's robust structure is the A/B split and above-morphology association;
true sub-topics are faint and only suggested in the herbal pages.

## 4. The compounded model (updated honestly)
1. **Surface:** slot grammar + self-citation copying.
2. **Section / language:** word-pool conditioned on section — and the content words' co-occurrence **re-derives the
   Currier A/B split** (this round), confirming A/B is a deep lexical-association division, not a surface artifact.
3. **Above-morphology word association:** content words carry real pairwise association beyond affix-sharing and
   beyond section labels (Q 0.264 > section 0.214; non-affix within-group 3× cross-group).
4. **Finer sub-topics:** **weak** — a small real excess over the iid generator in the herbal section only; absent in
   balneological. Round 89's "sub-topic bursts" are largely (not entirely) the A/B + section + frequency structure.

## 5. What this means, and the next move
- **Positive:** the content-word layer is organised — two language-communities, with pairwise association beyond
  grammar and section. The text behaves like it has a real lexical-semantic backbone at the A/B-and-above level.
- **Honest ceiling:** below the section/language level, organisation is faint. We have not found strong, readable
  sub-topics, and co-occurrence alone cannot turn "associated word groups" into "concepts" without an external anchor
  — which rounds 84–87 showed is absent at the object (picture) level.
- **Next (Move 2, the internal Rosetta):** the two communities are the Currier A and B languages. The sharpest
  remaining reference-free test is whether **A and B encode the same latent content in different surface forms** —
  pair A-pages and B-pages by their concept-group profiles and test for a systematic A↔B correspondence. If A and B
  are two encodings of one system, that correspondence is the lever; if they are independent, the "two languages" are
  two independent generators. That is the decisive next experiment, and this round has built the concept-group
  representation it needs.

**Status:** concept-cluster discovery done. The content words re-derive the A/B languages and carry real
above-morphology association (robust); finer sub-topics are weak and herbal-only (honest null-leaning). The model
gains a measured lexical-association layer and a clean setup for the A/B Rosetta.
