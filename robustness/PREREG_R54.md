# Pre-registration, round 54: are the seven "I am" sayings a ring around the centre of John 1:1–20:31?

**Rules:**
- This file is committed before `power/round54_ring.py` is written or run.
- **Already known:** the approximate positions of the seven sayings in the full Gospel (1:1–21:25) by syllables (round 45): 0.28, 0.37, 0.48, 0.49, 0.54, 0.69, 0.72.
- **Not yet computed:** their positions in John 1:1–20:31, and the ring statistic for any unit.
- **Status:** confirmatory, not blind.

## The seven sayings (fixed: the scholarly list of "I am" with a predicate, first occurrence of each)
1. 6:35 — the bread of life
2. 8:12 — the light of the world
3. 10:7 — the door of the sheep
4. 10:11 — the good shepherd
5. 11:25 — the resurrection and the life
6. 14:6 — the way, the truth and the life
7. 15:1 — the true vine

**Fixed choices:** repeated forms (6:41, 6:48, 6:51; 9:5; 10:9; 10:14; 15:5) are not used. The first occurrence is the convention in Brown 1966.

## Statistic
- **Position:** the fraction of John 1:1–20:31 before the middle of each saying's verse, giving x₁ … x₇ (sorted by the text's own order).
- **Ring error:**

  R = ( |(x₁+x₇)/2 − ½| + |(x₂+x₆)/2 − ½| + |(x₃+x₅)/2 − ½| + |x₄ − ½| ) / 4

  This is small when each pair balances around the book's centre and the middle saying sits on it.
- **Null:** 7 independent uniform points, sorted (400,000 simulations, seed 54).
- **p** = P(R_null ≤ R_obs).

## Primary test (H4)
- **Unit:** SBLGNT words, John 1:1–20:31.
- **Pass:** p < 0.05.

## Secondary (reported, not part of the verdict)
- the same statistic by Sinaiticus lines, Vaticanus lines, Sahidic tokens and Peshitta words;
- a **shape-only** version, centred on x₄ instead of ½ (is it a ring at all, wherever its centre is?);
- **control:** the same statistic for the seven signs (2:9, 4:50, 5:8, 6:11, 6:19, 9:7, 11:43), with no ring predicted;
- **control:** the full Gospel (to 21:25).
