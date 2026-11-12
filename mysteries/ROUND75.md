# Round 75: the Antikythera inscription's intervals, and the Voynich manuscript

## 1. Antikythera: the Front Cover Inscription's synodic intervals (`antikythera/intervals.py`)
**The new engine:** Keplerian orbits with real eccentricities, propagated over 300 years around 150 BC. It times every conjunction, opposition, station and greatest elongation, and gives the real range of each interval the inscription states (readings and interpretations from *Almagest* 7.1, 2016, IAM 6).

| Planet | Interval | Inscribed | Real range (median) | Verdict |
|---|---|---|---|---|
| Venus | superior conjunction → greatest evening elongation | 224 | 217–225 (221) | real |
| Venus | greatest elongation → inferior conjunction (and its mirror) | 68, 68 | 70–72 (71) | ~3 d short: **forced so that 224 + 68 = 292 = half of 584** |
| Venus | morning station → greatest morning elongation | 49 (?) | 48.8–50.8 (49.7) | **real sky supports the reading 49.** The editors' model would prefer 46, so this number was observed, not computed. |
| Mars | evening station → conjunction, conjunction → morning station | 349, 349 | 307–394 (357, 359) | inside Mars's large real range |
| Mars | retrograde | 82 | 60–81 (76) | **just above the longest real case**: a conventional figure (the editors: possibly pauses counted in) |
| **Jupiter** | evening station → conjunction → morning station | 139, 139 | 138–140 (139), 133–146 (139) | **exact** |
| **Jupiter** | retrograde including two 8-day pauses | 104 + 16 = 120 | 118–124 (121) | **exact** |

**Predictions for the lost parts:**
- **Saturn's lost intervals, using the inscription's own scheme** (equal direct halves, two 8-day pauses, retrograde motion): **2 × 120 + 2 × 8 + 122 = 378 days.** Real medians: direct half 120, retrograde 138 including pauses.
- **The unplaced "224" (fragment 51)** fits **Venus's closing interval**, greatest morning elongation → superior conjunction (real 216–226 days). That completes a symmetric Venus scheme: **224 + 68 + 68 + 224 = 584**, exactly the synodic period. Caution: fragment 51 also mentions a pause at a station, which the surviving Venus text does not use.
- **The unplaced "64" (fragment 42)** has several candidates and is not identified: Jupiter or Saturn station → opposition (real 60 and 69 days; minus an 8-day pause gives about 52 and 61), or Mars's retrograde.

**Synthesis.** The inscription mixes observed values (Jupiter's intervals, Venus's 49) with schematic ones forced to round totals (Venus 68, Mars 82, the 8-day pauses). That is consistent with a Greek writer combining Babylonian-style period relations (round 74) with observed phase intervals. Jupiter's numbers would have needed good observational records.

## 2. Voynich manuscript (`voynich/voynich.py`, transliteration IT2a-n from voynich.nu)
| Test | Voynich | Controls | Meaning |
|---|---|---|---|
| **V1. Do the words follow the pictures, within the same scribe's hand and Currier "language"?** | Illustration type predicted from words alone in all 3 groups (p 0.001–0.002); pooled accuracy **91%** against 68% for shuffled labels | **With ±10 neighbouring pages left out of training: 86% against 68%, p = 0.003**, so this is not just vocabulary drifting along the book | **The vocabulary tracks the subject matter pictured** (plants, "bathing" figures, stars), beyond scribe and "language". Consistent with Montemurro & Zanette (2013), here with a stricter control. A meaningless generator would have to be retuned for each topic. |
| **V2. Are lines units?** Excess mutual information between a word and its line position | **0.231** | KJV with one verse per line 0.249; Greek John with arbitrary line breaks 0.003 | **Voynich lines behave like verses or entries, not wrapped prose.** Line-initial words: daiin, saiin, dain, sol; line-final: daiin, dy, dam, am. |

**What this does and does not show:**
- It **does not decipher** anything.
- It narrows the possibilities: the text is organised in **line-sized units** whose **vocabulary depends on the topic**.
- That pattern fits a list, glossary, recipe or verse structure (entries per line, topic-specific terms) better than continuous prose or uniform gibberish.

**Next tests:**
- **Line-unit grammar:** are lines built from slots (first word / body / last word) like entries in a herbal or recipe list?
- **Herbal pages against real medieval herbals:** compare entry length and per-plant vocabulary distribution with a Latin herbal, *Macer floridus* or a *Circa instans* text, on the same structural measures.
