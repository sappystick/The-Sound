# Pre-registration, round 55: is John timed as a performance?

**Rules:**
- This file is committed before `power/round55_performance.py` is written or run.
- **Book:** John 1:1–20:31.
- **Performed time:** the round-51 method. Each verse gets the engine's declaimed timing, plus pauses at the punctuation (full stop or question 0.8 s, raised dot 0.6 s, comma 0.3 s).
- **Correction:** Holm across T1 and T2 at α = 0.05.

## T1. Do the movement boundaries fall at the ratios of a divided string?
- **Cuts:** the blind four-part cuts from AUDIT C24: 1:16, 13:33, 18:1.
- **Position of a cut:** the fraction of performed time that precedes its verse.
- **The ratios:** the Pythagorean canon's divisions of a string, measured from either end. A string stopped at these points sounds the octave, fifth, fourth or tone:

  F = {1/9, 1/4, 1/3, 1/2, 2/3, 3/4, 8/9}
- **Statistic:** D = the mean over the 3 cuts of the distance to the nearest member of F.
- **Null:** 3 sorted uniform random points (400,000 simulations, seed 55).
- **p:** P(D_null ≤ D_obs).
- **Pass:** Holm-adjusted p < 0.05.

## T2. Do the "Amen, amen" cues stand at the joints?
- **Cues:** every verse of 1:1–20:31 containing ἀμὴν ἀμήν.
- **Joint:** a verse in which a paragraph of the SBLGNT edition begins. These paragraphs are editorial and modern; that is a limitation.
- **Statistic:** the share of cue verses that are joints.
- **Test:** one-sided binomial against the share of all verses of 1:1–20:31 that are joints.
- **Pass:** Holm-adjusted p < 0.05.

## Exploratory (not tests; reported and labelled)
- **E1. Sacred dimensions as instrument ratios.** The dimensions given in the text for sacred structures and objects (tabernacle, ark, table, altars, Solomon's temple and its rooms) against secular ones (Og's bed, Solomon's palace halls, Goliath's measures).
  - **Measure:** the share of their pairwise ratios that are consonant (2:1, 3:2, 4:3, 5:4, 5:3, 6:5, 1:1).
  - **Null:** random dimension pairs drawn from the same pool of numbers.
- **E2. Passages that are not ordinary language.** A detector for "played" or non-lexical passages: verses whose word sequence is unusually repetitive (low compression ratio, low type/token ratio).
  - **Data:** the Hebrew Bible and the Greek New Testament.
  - **Positive control:** Isaiah 28:10 and 28:13, *ṣaw lāṣāw ṣaw lāṣāw qaw lāqāw qaw lāqāw*.
  - **Report:** the top-ranked verses.
