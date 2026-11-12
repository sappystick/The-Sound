# Round 84 — Stage C (ANCHOR): do the zodiac labels bind to a measurable referent?

Executing Stage C of the pipeline (`voynich/PLAN.md`). Stage C is where every decipherment has failed: binding
labels to identifiable referents. I used the one referent measurable **without interpreting the pictures** — each
zodiac label's **clock angle**, recorded in the ZL transliteration (`<!10:30>`). 12 zodiac diagrams, **333 labels**
with angles. Script `voynich/stage_c.py`, results `voynich/stage_c_results.json`.

## The tests and what they found

| Test | Question | Result | Verdict |
|---|---|---|---|
| **C1 ring regularity** | Are a diagram's labels evenly spaced (a 30-position day-ring)? | gap CV 0.65–1.03 (even ring ≈ 0) — labels **cluster, not evenly spaced** | **not a regular day-ring** |
| **C2 angle → initial glyph** | Within a diagram, does a label's first glyph depend on its angle? | significant in **1 of 12** diagrams (≈ chance) | **N** |
| **C3 cross-diagram anchor (the gate)** | Predict a held-out diagram's label glyph from angular sector, map learned on the other diagrams | accuracy **0.775 = null 0.775 = majority-glyph baseline 0.772**, p 0.49 | **FAIL — no positional code** |
| **C4 ring-sequence repetition** | Sorted by angle, is the glyph sequence more ordered than a shuffle? | significant in **1 of 12** (≈ chance) | **N** |
| **C5 label-family coherence** | Do labels within one diagram share more structure than random labels? | within 0.342 vs null 0.327, **p 0.002** | **weak but real structure** |

## Reading (honest, and this is the valuable part)

**The decisive negative:** the zodiac labels **do not encode their angular position.** Knowing exactly where a label
sits on the ring tells you nothing about its text beyond the base rate of the commonest glyph (C3: 0.775 vs baseline
0.772). This is the most natural anchor a dial-shaped diagram could have — days, degrees, a sequence — and it is not
there. It strengthens round 79's marginal "not a repeated day-list" into a firm result on the full angular data.

**The counter-signal:** the labels are **not random filler either.** Within a single diagram they form a slightly
tighter family than labels drawn from across diagrams (C5, p 0.002) — they share prefixes, suffixes and lengths a
little more than chance. The effect is **small** (+0.015), so it may be section *style* (the whole zodiac section uses
one label-grammar) rather than meaning. But it is real, and it is what a genuine naming scheme would also produce.

**So Stage C splits.** The labels have the *structure* of a naming system (locally coherent, C5) but carry **no
recoverable binding to the one external referent we can measure** (position, C3/C1/C2/C4). We have found **zero
label→referent anchors**, against a gate of five.

## Gate C: NOT met

- Required: ≥ 5 anchors each reproducible across ≥ 2 pages. Found: **0** (the only measurable external referent,
  angle, carries no label information).
- This is **anchor-probe failure #1** (positional). Per the plan's decision rule, a second failed probe in this
  section sends the zodiac to the H-EMPTY verdict. The coherence result (C5) is the one thread that keeps H-HYBRID
  alive: the labels *could* be meaningful, but their meaning is **not positional.**

## What this means for the central question

Combine with what we knew:
- **Page level (S6):** vocabulary predicts a page's topic (90.8%) — coarse meaning exists.
- **Label level (this round):** the fine label→referent binding a decipherment needs **does not survive testing** —
  at least not through position.

The honest frontier is now sharp: **the Voynich carries coarse, topic-level meaning but resists fine anchoring.**
That is consistent with (a) a real but heavily obfuscated content system whose anchor is pictorial, not positional,
or (b) a generative system that imitates a labelled herbal/astrological book at the topic level without naming
specific things. These two are only separable by the remaining anchor: **picture identity.**

## The only remaining Stage C path: image-bound anchors

Position failed. The untested referent is **what the label points at** — the plant, the figure, the container. That
requires the Beinecke IIIF images (confirmed reachable) and visual features, then the test: *do visually similar
plants/figures get similar labels?* If yes, an anchor exists and Stage D can begin; if no (a second probe failure),
the zodiac/herbal sections go to **H-EMPTY** by the pre-registered rule.

**Pipeline status:** A pass · B partial · **C failed on position, one probe of two; image anchor is the decider.**
No overclaim: after a rigorous Stage C, the Voynich still has not yielded a single label→referent binding — exactly
the wall a century of work has hit, now mapped precisely rather than guessed at.
