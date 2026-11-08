# Pre-registration: robustness of the novel claims (written and committed before any robustness test was run)

Date: 2026-11-08.

Script to be written: `robustness/robustness.py`. Everything below is fixed in advance. Results go to `robustness/results.json` and `AUDIT.md` whatever they show.

## Claims under test
- **C24.** Blind segmentation of John's voice-mode signal recovers John's outline (4 parts).
- **C25.** This works for John and not for the Synoptics.
- **C3.** "Living water" (מים חיים) lies at the centre of Leviticus and of the Song of Songs.
- **C11.** More than half of John's manuscript variants sound identical when read aloud in Koine.
- **G.** Which of all reported p-values survive a project-wide false-discovery correction.

## C24 and C25: outlines (several published-style outlines per book, each break = the first verse of a new section)
| Book | Outline | Breaks |
|---|---|---|
| John | Brown | 1:19, 2:1, 5:1, 11:1, 13:1, 13:31, 18:1, 20:1, 21:1 |
| John | Moloney | 1:19, 2:1, 5:1, 11:1, 13:1, 18:1, 20:1, 21:1 |
| John | Dodd | 1:19, 2:1, 4:46, 6:1, 7:1, 9:1, 11:1, 12:1, 13:1, 18:1, 21:1 |
| John | round-30 conventional | 1:19, 2:1, 5:1, 6:1, 7:1, 9:1, 10:22, 11:1, 12:12, 13:1, 13:31, 18:1, 20:1, 21:1 |
| Mark | A (sections) | 1:14, 3:7, 6:7, 8:22, 11:1, 14:1, 16:1 |
| Mark | B (two halves) | 1:14, 8:27, 11:1, 14:1, 16:1 |
| Matthew | Bacon | 3:1, 5:1, 8:1, 10:1, 11:1, 13:1, 13:53, 18:1, 19:1, 23:1, 26:1 |
| Matthew | Kingsbury | 4:17, 16:21 (plus 26:1, 28:1) |
| Luke | A | 1:5, 3:1, 4:14, 9:51, 19:28, 22:1, 24:1 |
| Luke | B | 1:5, 3:1, 4:14, 9:51, 19:45, 22:1, 24:1 |
| Acts (control) | | 2:1, 6:1, 8:4, 9:32, 13:1, 15:36, 19:21, 21:17, 27:1 |
| Genesis (Hebrew control) | toledot | 2:4, 5:1, 6:9, 10:1, 11:10, 11:27, 25:12, 25:19, 36:1, 37:2 |

The outlines are summarised from memory of the published works and are labelled as such. Verification against the printed sources is a listed audit step.

## Parameters (full grid)
- Minimum section length: 10, 15 or 25 verses.
- Mode definition:
  - (i) full: 1st/2nd-person verbs and pronouns, minus 3rd-person indicative narrative verbs;
  - (ii) verbs only;
  - (iii) action limited to aorist and imperfect.
- Parts: k = 4 (primary) and k = 5 (secondary).
- Statistic: mean distance of the cuts to the nearest outline break, against 5,000 random cut sets with the same constraints.
- Hebrew: discourse = 1st/2nd-person verbs, pronouns and suffixes; action = 3rd-person wayyiqtol.

## Decision rules
- **C24 holds** if, with the baseline parameters (minimum length 15, mode i, k = 4), John's p < 0.05 for at least 3 of the 4 John outlines, **and** p < 0.05 in at least 75% of the 9 parameter combinations against Brown.
- **C25 holds** if John has the lowest p of the four Gospels in at least 80% of (outline × parameter) combinations at k = 4, **and** no Synoptic reaches p < 0.05 in most of its combinations.
- Acts and Genesis are reported descriptively. If either matches its outline as well as John does, the claim "unique to John" is weakened to "John among narrative books".

## C3
1. Recompute the centre of Leviticus and of the Song of Songs in WLC by verses, by words and by letters.
2. Recompute it in the Septuagint (Swete) by verses and by words, with ὕδωρ ζῶν as the phrase.

C3 holds if, in every count, the centre falls within 3 verses of an occurrence of the phrase. Also reported: the probability that a random centre would fall that close, given the book's occurrences; then combined for both books and corrected for the 39 books searched.

## C11
Rerun `ms_sound.py` with the pronunciation era set to koine-late (as originally run), koine and attic. C11 holds if the identical-sound share is above 50% under both Koine settings. The attic figure is reported as a contrast; it should be lower if the effect is truly about Koine sound changes.

## G
1. Extract every p-value written in DISCOVERIES.md.
2. Apply Benjamini–Hochberg at q = 0.05 across the whole project.
3. Report which of the claims marked S keep at least one supporting p-value that survives.
