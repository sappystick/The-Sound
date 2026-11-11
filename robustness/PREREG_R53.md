# Pre-registration, round 53: the middle "I am" (10:11) at the centre of John 1:1–20:31 in P66, P75, the Syriac and the Coptic

**Rules:**
- This file is committed before `power/round53_papyri_versions.py` is written or run.
- **Hypothesis:** the one confirmed in round 52 on Sinaiticus and Vaticanus.
- **Not yet computed:** the counts in P66, P75, the Peshitta and the Sahidic for 1:1–20:31.
- **Null:** the 4th of 7 uniformly random points, two-sided distance from 0.5, 400,000 simulations (seed 53).
- **Position:** the units before 10:11, plus half of 10:11, divided by the total units of 1:1–20:31.

## H2 (primary): the ancient translations, complete texts, counted in words
- **Syriac:** Peshitta John (ETCBC *syrnt* plain text). Unit = space-separated words.
- **Coptic:** Sahidic John (Coptic SCRIPTORIUM TreeTagger files, the round-39 loader). Unit = SCRIPTORIUM `norm` tokens. A verse-number drop starts the next chapter, as in round 39.
- **Pass:** p < 0.05 in both.

## H3: the papyri, by reconstruction (lower evidential weight)
- **Data:** P66 and P75 (CNTR). Both are incomplete in the later chapters.
- **Unit:** letters.
  - For each verse the papyrus preserves, use its own letter count (missing and supplied letters excluded).
  - For each verse it lacks, or preserves only in part, use the SBLGNT letter count, multiplied by that papyrus's ratio of its own letters to SBLGNT letters over its fully preserved verses.
- **A verse is "preserved"** when no letter is marked missing (`^`) or supplied (`~`).
- **Report:** coverage (the share of the 1:1–20:31 letter mass that is the papyrus's own).
- **Pass:** p < 0.05 in both.

## Correction and robustness
- **Correction:** Holm across H2 and H3 (2 tests).
- **Secondary:** Coptic by letters; Syriac by letters.
- **Control:** each witness's verse at the centre of 1:1–20:31.
