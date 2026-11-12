# Round 83: the 231-gates test, and rigorous execution of the pipeline's early gates

Executing the plan (`voynich/PLAN.md`). Three results: the **231-gates test** (Angle I) rules out one family of
generation mechanisms; **Stage A** passes its held-out gate; **Stage B** quantifies the content stream. Plus the
label-coordinate data needed for Stage C was gathered.

Scripts: `voynich/gates.py`, `voynich/stages.py`. Results: `voynich/gates_results.json`, `voynich/stages_results.json`.

## 1. The 231-gates test — which combinatorial idea generated it? (Angle I)

Sefer Yetzirah's 231 gates (our round 39) are a **free, bi-directional** letter-combination: the pair א-ב is one
gate read either way (אב = בא). So a free-combination system has **high gate occupancy** (most letter-pairs occur)
and **high reciprocity** (if `ab` occurs, `ba` occurs), with no positional layering. A **directional slot** grammar
(prefix → core → suffix) is the opposite: glyphs sit at fixed positions, transitions run forward (**high layering**),
and reciprocity is **low**. The test measures which the Voynich is.

| metric | VOY | HEB | SY | LAT | GRK | KANON | FREE (synthetic) | SLOT (synthetic) |
|---|---|---|---|---|---|---|---|---|
| alphabet n | 40 | 27 | 27 | 26 | 25 | 19 | 12 | 14 |
| gate occupancy | **0.40** | 0.88 | 0.67 | 0.97 | 0.72 | 0.61 | 1.00 | 0.36 |
| reciprocity | 0.84 | 0.92 | 0.84 | 1.00 | 0.93 | 1.00 | 1.00 | **0.30** |
| layering (forward share) | **0.71** | 0.62 | 0.65 | 0.56 | 0.68 | 0.65 | 0.50 | **0.80** |
| next-glyph entropy (bits) | **2.26** | 3.64 | 3.18 | 3.24 | 2.94 | 3.28 | 3.46 | 1.35 |

**Findings:**
- **The free letter-combination mechanism is ruled out.** A Sefer-Yetzirah-style gate system (and Hebrew itself) has occupancy 0.67–0.88 with bidirectional gates. The Voynich uses **only 40% of its possible glyph-pairs** and is **positionally layered** (0.71) — the signature of fixed slots, not free combination. So **Kabbalistic ṣerûf / Llull's combining wheels / the 231-gates idea are not the Voynich's generator** (**N**).
- **The directional-slot mechanism is confirmed and refined.** The Voynich sits nearest the synthetic SLOT model (distance 0.55 vs 0.65 to FREE; verdict *directional slot*), with the **lowest next-glyph entropy of any real text** (2.26 vs 2.9–3.6 for languages) — very few glyphs may follow each glyph, a rigid generative rule.
- **But not a pure slot DAG:** its reciprocity (0.84) is far above a strict one-way slot system (0.30). The Voynich's **core (root) slot has real internal two-way structure** — it is not a one-pass prefix→suffix pipe. This matches Stage B below: the root is where the structure (and the meaning, from the round-82 pilot) lives.

*Caveat:* occupancy depends on the glyph inventory; EVA's 40 glyphs include rare forms that lower it. Reciprocity, layering and branching entropy are robust to this, and they jointly give the verdict.

**Consequence for the plan:** the inspiration field narrows. Free-combination devices (Llull wheels, letter-mysticism) are out; **positional/slot devices stay in** — a designed slot-language (as KANON formalises), a column-based nomenclator or grille, or a heavy abbreviation system. The next inspiration test is therefore the abbreviation-expansion test (Angle F), not the gates.

## 2. Stage A — NORMALISE: the slot layer is real (held-out) ✅

Learn a slot grammar (prefixes + suffixes) on **even folios**; measure what share of **held-out odd-folio** word-mass
it generates (word = learned prefix + root-seen-in-training + learned suffix, non-empty root).

| | value |
|---|---|
| train / test words | 18.8k even / ~18.9k odd |
| learned prefixes | `qo ch ok ot da ol ai ct yt y s …` |
| learned suffixes | `edy iin eey ain ody chy hol eol ar al ol hy …` |
| **held-out coverage** | **0.865** |
| shuffled-letter null | 0.302 |
| **gate (≥ 0.85)** | **PASS** |

The slot grammar generalises to unseen pages at 86.5%, nearly 3× the shuffled-letter null. **Stage A gate met** — the
prefix·root·suffix token layer is a real property of the manuscript, not an overfit. (The learned units are the
canonical Voynich morphemes, recovered without being supplied.)

## 3. Stage B — DE-MACHINE: isolating the content stream

On held-out pages, how much of the text is generative *machinery* (copying + the commonest grammatical roots) versus
candidate *content*?

| | share |
|---|---|
| exact adjacent copies (page-level) | 0.007 |
| machinery (copies + top-20-root filler words) | 0.576 |
| **candidate content stream (remainder)** | **0.424** |

About **42% of tokens** survive as the content layer to target in Stage C. Combined with the round-82 pilot (topic
signal sits in the **root**, and the root beats the whole word in Currier-B hand 3), the de-machining target is now
specific: **the roots of the ~42% non-filler words, per section.**

## 4. Gathered this round (for Stage C)
- **Label/token coordinate dataset** (`sources/texts/voynich/spatial/`, Placა spatial corpus): per-token pixel
  position, angle and font size for the rosette fold-out and more — the data needed to test whether **label order
  tracks a figure's angular position** (experiment #4) and to bind labels to picture regions (Angle D).
- **Beinecke MS 408 IIIF** manifest confirmed reachable (image-bound anchors, Stage C).

## 5. Pipeline status after round 83
| Stage | Gate | Status |
|---|---|---|
| A Normalise | slot coverage ≥ 0.85 held-out | **PASS (0.865)** |
| B De-machine | root ≥ full for topic, out of sample | **partial pass** (Currier-B yes; herbal section needs anchors) |
| C Anchor | ≥ 5 anchors consistent across ≥ 2 pages | **next** — data now in hand (spatial + IIIF) |
| D Propagate | coherent sense for ≥ 30% of roots | pending C |
| E Validate | out-of-sample p < 0.01, two splits | pending D |

**Inspiration field after round 83:** free-combination (Kabbalah / Llull / 231-gates) **out**; directional slot
devices (designed slot-language, nomenclator/grille, abbreviation system) **in**. Two of the plan's angles have now
returned hard results; the content stream is isolated and the anchor data is gathered, so the pipeline moves to
Stage C.
