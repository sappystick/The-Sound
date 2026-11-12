# Round 46: the four predictions by letters and by accent, and the language of composition

**Files:**
- script `power/round46_letters_accent_language.py` (seed 46);
- numbers `power/round46_results.json`.

**New source used:** the Syriac New Testament (Peshitta, ETCBC *syrnt*), already downloaded in round 39.

## A. The instrument's four predictions, under three mappings
Each mapping places John onto the seven strings differently:

| Mapping | How a syllable chooses its string |
|---|---|
| **Sound** (round 45) | the Koine *pronunciation* of its vowel; ω = ο, so one string is silent |
| **Letters** | every *written* vowel letter is a note; all seven strings sound |
| **Accent** | the ancient melodic rule: accented syllable on the paranete (c4), the run-up on the mese (a3), the fall on the lichanos (g3); a circumflex on paranete then mese |

| Prediction | Sound | Letters | Accent |
|---|---|---|---|
| **P1.** John sounds the mese (the "I am" string) more than the Synoptics | yes: 15.9% vs 13.6–13.8% | **no**: 17.8% vs 17.6–18.5% | **no**: 47.3% vs 47.9–48.2% |
| **P2.** The four movements are different modes (cadence strings) | p 0.07 | p 0.15. Cadences: movement 1 lichanos, **movements 2–4 mese** | p 0.90 |
| **P3.** The middle "I am" (10:11) sits at the book's centre | 0.487, p 0.057 | **0.489, p 0.050** | 0.487, p 0.056 |
| **P3b.** The middle sign at the centre | p 0.87 | p 0.86 | p 0.86 |
| **P4.** "I am" verses end on the mese | 6/24, p 0.20 | 9/24 vs 23%, p 0.087 | **12/24 vs 31%, p 0.039** |

**What this shows:**
- **P1 depends on pronunciation.** John's extra mese comes from Koine pronunciation (ει → ι: εἰμί, ἐκεῖνος), not from the written letters or the melody. It is a property of John's vocabulary *as spoken*.
- **P3 holds in every mapping** (p ≈ 0.05), because it depends only on where the sayings fall in the book. The fourth of the seven "I am" sayings, "I am the good shepherd; the good shepherd lays down his life", stands at the middle of the Gospel. This overlaps the "I am" ring already found (claim C2), so it is not new evidence on its own.
- **P4 is the one new hint.** Under the accent melody, half of the "I am" verses come to rest on the mese, against 31% of other verses (p = 0.039).
  - Eight tests were run (P1–P4 × 2 new mappings), and corrected for that, it does not survive (BH q ≈ 0.3).
  - It is a lead for a pre-registered rerun, not a finding.
- **P2: no modes.** By letters, the three later movements do lean to a mese cadence (24–33%) while the prologue never cadences there, but the difference is not significant.

**Overall:** the instrument reading holds at the scale of the whole book: the centre, the middle "I am", and the middle place (round 44). It does not hold at the scale of notes and cadences, whichever mapping is used.

## B. What language were the power words, and the rest of the text, composed in?
**The idea:**
- When a text is composed, its sounds are arranged in its own language. Translation keeps the meaning, but loses much of the play of sound between neighbouring words.
- So the original should carry more sound-patterning than a translation of it.

**The measure** (the same in Greek, Hebrew and Syriac letters):
- for each pair of adjacent words, count:
  - **alliteration:** the same first consonant;
  - **rhyme:** the same last two letters;
  - **shared consonants:** at least 2 consonants in common;
- compare each verse with its own words shuffled (z score, 50 shuffles per verse).

**Controls, where the original is known:**

| Text | Original | Translation | Works? |
|---|---|---|---|
| Psalms | Hebrew −0.086 ± 0.04 | Greek (Septuagint) −0.246 ± 0.04 | **yes, clearly** |
| Romans | Greek −0.191 ± 0.09 | Syriac −0.242 ± 0.09 | right direction, weak |

**The test:**

| Text | Greek | Syriac (Peshitta) | Reading |
|---|---|---|---|
| **John, whole Gospel** | **−0.217 ± 0.07** | −0.350 ± 0.06 | **Greek carries more patterning: John patterns as composed in Greek**, more clearly than Romans, which is known to be Greek |
| Mark, whole Gospel | −0.126 ± 0.07 | −0.176 ± 0.07 | Greek slightly higher; not separable |

**The power sayings of John** (49 verses: "Amen, amen", "I am", 11:43, 19:30, 20:22) as a difference in differences:
- In the power sayings, Greek is *less* patterned than the Syriac (Greek − Syriac = −0.109).
- In the rest of John, Greek is *more* patterned (+0.149).
- Difference −0.258, p = 0.20: a **lean, not significant**.

**Mark's four Aramaic-word verses** (n = 4, illustrative only):

| Verse | Greek | Syriac |
|---|---|---|
| 5:41 (*talitha koum*) | 0.48 | −0.69 |
| 7:34 (*ephphatha*) | −0.15 | −0.85 |
| 14:36 (*abba*) | 0.99 | 0.99 |
| 15:34 (*Eloi, Eloi*) | 0.10 | **1.84** |

The cry from the cross patterns strongly in Syriac.

**Conclusion:**
- **The Gospel of John was composed in Greek.** Its sound-patterning belongs to the Greek, and is lost in the Syriac, the way the Hebrew Psalms' patterning is lost in Greek. This agrees with the project's earlier result ("composed in Greek by a Semitic voice", `code/analysis/semitic.py`) by a new and independent method.
- **The power sayings lean the other way** (not significant). If the lean is real, the sayings were patterned in a Semitic language before they reached the Greek, the way Mark keeps *talitha koum* and *Eloi* untranslated (round 37). The book would then be Greek and the words of power Aramaic underneath.
- **What would settle it:** a larger set of sayings (all Gospels' words of Jesus against narration) and a pre-registered rerun.
- **Caveat:** the Peshitta is a later Syriac (Eastern Aramaic) *translation from the Greek*, not Jesus' Galilean Aramaic. A pattern that reappears in it is a pattern that Aramaic easily rebuilds, which is the most that can be measured without a first-century Aramaic text.

## C. Where this leaves the instrument hypothesis
| Scale | Instrument reading | Evidence |
|---|---|---|
| Whole book: centre, the seven sayings, the middle place | **fits** | P3 p ≈ 0.05 in every mapping; Jesus in the middle, p 0.005 (post hoc) |
| Sections: modes | does not fit | P2 not significant under any mapping |
| Verse endings: "I am" on the mese | a hint under the accent melody only | P4 p 0.039, does not survive correction |
| Notes: the vowel-by-vowel melody | does not fit | round 43 (letters are not a tune) |
| Language | the book in Greek; the power sayings possibly Aramaic underneath | B: John patterns as Greek original; sayings lean Semitic, p 0.20 |
