# Pre-registration, round 52: the middle "I am" at the centre of the Gospel ending at 20:31, in the manuscripts

**Rules:**
- This file is committed **before** `power/round52_2031_manuscripts.py` is written or run.
- **Origin of the hypothesis:** round 51 (`POWER_MEASURES.md`). On the printed text (SBLGNT), 10:11 sits at the centre of John 1:1–20:31 by words, breath groups and performed time.
- **What is already known:** the position of 10:11 in the *full* Gospel by manuscript lines (round 50: 01 = 0.4897, 03 = 0.4876).
- **What has not been computed:** the manuscript line counts for the Gospel ending at 20:31.
- **Status:** confirmatory, on a new unit, but not blind.

## Primary test (H1)
- **Data:** CNTR transcriptions of Codex Sinaiticus (01) and Codex Vaticanus (03), commit `4e743a4`, John only.
- **Unit:** manuscript lines, counted by the line, column and page break marks (`/`, `|`, `\`), exactly as in round 50.
- **Book:** John 1:1 to 20:31 inclusive. Chapter 21 is excluded.
- **Position:** the lines before 10:11, plus half the lines of 10:11, divided by the total lines of 1:1–20:31.
- **Null:** the 4th of 7 uniformly random points (400,000 simulations); two-sided distance from 0.5.
- **Pass:** p < 0.05 in **both** 01 and 03.
- **One test:** the two manuscripts form a single conjunctive test, so there is no further correction.

## Secondary tests (reported, not used for the verdict)
- **Other CNTR manuscripts of John:** Alexandrinus (02), Ephraemi (04), Bezae (05), Washingtonianus (032). Each is used only if at least 95% of the verses of 1:1–20:31 are present. Each is reported with its coverage.
- **Robustness:** the same test with the 7:53–8:11 passage, if a manuscript contains it, counted and excluded.
- **Control:** the position of each manuscript's verse at the centre of 1:1–20:31, so the centre itself is reported.
