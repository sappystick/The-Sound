# Round 74: the Copper Scroll, the Antikythera Mechanism and the lost Signs Gospel

**Sources supplied by the user.** These are used for analysis and are not redistributed here:
- J. T. Milik, "The Copper Document from Cave III of Qumran: Translation and Commentary", *ADAJ* 4–5 (1960) 137–155. A scan, OCR'd; every number was checked against the page images.
- T. Freeth et al., "A Model of the Cosmos in the ancient Greek Antikythera Mechanism", *Scientific Reports* 11 (2021) 5821.
- *Almagest* 7.1 (2016): the complete edition of the Antikythera Mechanism's inscriptions (Jones, Bitsakis and others). Used to confirm the Front Cover Inscription readings.

## 1. The Copper Scroll (`copper/entries.py`, `copper/analyze.py`)
All 64 entries are now data: place, depth, distance, amount, gold, other items, Greek group.

| Test | Result |
|---|---|
| **T1. Where the Greek groups fall** | Entries 1, 4, 6, 7, 10, 14, 17: all within the first 17 of 64 (columns I–IV). Chance **p = 3.1 × 10⁻⁵**. The groups belong to one section of the list. |
| **T2. Are they Greek numerals?** | Greek numerals are written largest value first. Only **3 of 7** groups are (ΘΕ, ΤΡ, ΣΚ), about what random letter order gives (2.83). ΚΕΝ, ΧΑΓ, ΗΝ and ΔΙ are backwards as numerals. **The groups are very probably not numbers;** abbreviations, labels or cross-references are more likely. |
| T3. Do their values match amounts? | None equals its own entry's amount (ΚΕΝ 75 against 17 talents, ΤΡ 400 against 40 …). Three equal *some* amount elsewhere (ΘΕ = ΔΙ = 14, ΤΡ = 400); chance gives this often (p = 0.078). Not supported. |
| **T4. The amounts** | 44 entries with talents, 4,333 talents in total. **The same values recur far more than a smooth distribution gives:** 22 ×4; 17, 40, 42, 60, 70 ×3; 9, 12, 900 ×2. That is 16 repeats against 5.9 expected, **p = 0.0002**. Stock numbers suggest a conventional or literary list (Milik's "folklore" view), *or* real tallies in standard lots. The smooth null is generous to "real", so this leans literary but does not settle it. |
| T5. Depths and places | "Dig three cubits" is the most frequent depth (7 of 25). The securely identified sites (Gerizim, Bet-Shan, Siloam, Absalom, Kidron, Nebo, Bet Horon, Jericho, Achor/el-Buqeia, Qumran) now have spoken, self-repairing KLIMATA place codes for field use. |

**Synthesis.** The Greek letters are a property of the first section, entries 1–17. That is where the precinct vocabulary clusters: Court, Peribolos, Esplanade, Eastern Gate, Steps, cisterns. And the letters do not behave like numerals.

**A hypothesis this makes testable:** the groups are section labels or cross-references, perhaps to the "copy with explanations" of entry 64. They would be added by a Greek-literate hand working on the first part of the inventory.

**Next test:** compare the letter forms and positions in the facsimile (DJD III, plates) with the line breaks. Labels written in the margin or at line ends would support it.

## 2. The Antikythera Mechanism (`antikythera/periods.py`): a new period-relation engine
The two relations read in the Front Cover Inscription are confirmed in the *Almagest* edition: Venus "…462, and each restitution in 5[84] days"; Saturn "…restitutions in 442". The other three are Freeth's reconstructions. The new tool searches every relation of up to 500 years, scores it against modern mean motions, checks whether its gears are buildable (prime factors under 100), finds Babylonian combinations, and runs chance controls.

| Planet | Relation | Error, deg/century | Rank among buildable relations (≤ 500 yr) | As Babylonian relations |
|---|---|---|---|---|
| Venus (read) | (289, 462) | −2.92 | 7th of 160 (e.g. (172, 275) is 15× better) | ×5 = (5, 8) + 2 × (720, 1151) |
| Saturn (read) | (427, 442) | −1.77 | 4th of 144 | 3 × (57, 59) + (256, 265) |
| Mercury (reconstructed) | (1513, 480) | −5.68 | 6th of 105 | (2673, 848) − 8 × (145, 46) |
| Mars (reconstructed) | (133, 284) | +1.40 | 5th of 171 | *is* the Babylonian ACT relation |
| Jupiter (reconstructed) | (315, 344) | +0.26 | **1st** of 143 | (391, 427) − (76, 83) |

**Findings:**
- **The designers did not pick the most accurate buildable relations.** Better ones existed for four planets. What the chosen ones share is that each is a **very simple whole-number combination of Babylonian relations**.
  - **Control:** for Venus and Mars, the chosen relation is the only accurate buildable relation (of 13) that simple.
  - For the two relations actually *read* on the Mechanism, the chance that both are this simple is **about 0.03**.
  - This is independent support for derivation from Babylonian period relations, the mechanism behind Freeth et al.'s process. It also recovers their (1445, 2310) = 5 × (289, 462) independently.
- **"Economy" (shared prime factors) is not distinctive.** Random accurate, buildable choices share primes as often (p = 0.80). Shared gears are possible with many choices, so the economy criterion cannot by itself single out the reconstructed relations.

## 3. The lost Signs Gospel (`signs/`), pre-registered before the script was written
| Run | Omnibus p | Features significant after correction |
|---|---|---|
| **Signs passages against matched John narrative (pre-registered)** | **0.0004** | δέ ↑, historic present λέγει ↑, ὁ Ἰησοῦς ↑, μετὰ τοῦτο / ταῦτα ↑ |
| Without chapter 21 | 0.0036 | δέ, ὁ Ἰησοῦς, shorter verses |
| **Power check: Mark's miracle stories against John** | **0.0002** (passes) | καί ↑↑, οὖν ↓, asyndeton ↓, Ἰουδαῖοι ↓ … |
| Exploratory genre control: Mark's miracles against the rest of Mark | 0.075 (not distinct) | only historic present |
| Exploratory, without the two genre/opening-sensitive features | 0.011 | ὁ Ἰησοῦς |

**Pre-registered decision: SOURCE DETECTED.** The miracle narratives Fortna assigns to a Signs Source are stylistically distinguishable from John's other narrative of matched genre mix, and the method has power.

**Honest reading:**
- **Part of the signal could be genre or position.** The historic present is also higher in Mark's miracles. μετὰ ταῦτα opens two source passages (6:1, 21:1).
- **The core survives:** δέ and above all **ὁ Ἰησοῦς** (Jesus named with the article). These are *not* features of miracle stories in Mark, where they run the other way or not at all.
- Removing the doubtful features leaves p = 0.011, borderline.

This is a real, specific, replicable signal worth a focused pre-registered follow-up:
- the article with ὁ Ἰησοῦς across all of John;
- the other proposed source passages (1:35–49, 21);
- other Gospels' miracle stories.

## Engine tools added
- **Period-relation finder** (`antikythera/periods.py`): exhaustive search, buildability, Babylonian decomposition with chance controls.
- **Matched-block style test with a power check and a genre control** (`signs/signs.py`): reusable for any source-criticism question.
- **The Copper Scroll as data** (`copper/entries.py`): positional, numeral-order and repetition tests, and place codes.

## Follow-up (pre-registered, `signs/PREREGISTRATION_2.md`, `signs/ho_iesous.py`): is ὁ Ἰησοῦς a source marker?
| Test | Result |
|---|---|
| T1, refined measure on the core passages (share of Ἰησοῦς with the article) | 80% against 65% in the rest of John, p = 0.077: much weaker than the round-74 rate measure |
| **T2, the wider Signs Source (1:19-49, 2:14-19, 4:4-42, 12:1-15, 18-19, 20:1-20)** | 69% against 62%, **p = 0.25: not significant** |
| T3, genre in the Synoptics | No Gospel shows a significant rise in its miracle stories (Matthew p = 0.29, Luke p = 0.31; Mark leans the other way) |

**Pre-registered decision: NOT SUPPORTED.** The round-74 "ὁ Ἰησοῦς" signal came mostly from Jesus being *named more often* in the miracle stories (a rate per 100 words), not from a source spelling his name differently. The direction is the same in the wider source passages (69% against 62%), but it is too weak to count.

**What remains of round 74:** the overall stylistic difference of the core miracle stories (p = 0.0004) stands as measured. Its most specific feature did not extend to the rest of the proposed source. Status: **a half-finding**. The core sign stories differ, but no marker has been shown to carry over to the wider source.

Descriptive by-product: Jesus appears without the article in 76 verses of John, most often in the formula ἀπεκρίθη Ἰησοῦς ("Jesus answered") and in chapters 18-20.
