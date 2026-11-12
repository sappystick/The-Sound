# Round 79: Voynich keys and held-out models; new sources for the Copper Scroll, Antikythera and the Signs Gospel

## 1. Voynich: are the "keys" keys? (`voynich/keys.py` → `keys_results.json`)
| Test | Result |
|---|---|
| **K1. f49v line letters:** does each margin letter relate to the line beside it? | Letter = the line's first glyph 5% (shuffle 6.5%, p 0.77); letter occurs in the line 60% (shuffle 68%, p 0.90). **No relation.** The letters ("foryekspoyepoyedysky") are not an index of their lines. |
| **K2. f57v ring sequence:** is its order taken from the text? | Neighbour pairs are no more text-like than shuffles (p 0.63); no relation to glyph frequency. It uses glyphs that are almost absent from the text: **'v' never occurs, 'x' only 25 times.** It is a sign list with its own order, not a key drawn from the text. |
| **K3. Zodiac labels:** a shared day-name sequence? | Pages hold **30 labels each** (the split Aries and Taurus pages hold 15 + 15), consistent with days of a month. But labels in the same position across months are only marginally alike (p 0.063), and neighbours are not (p 0.32). **Not a repeated list of day names.** |

## 2. Voynich held-out test (`voynich/heldout.py` → `heldout_results.json`)
Each model was fitted on the even pages, then generated text with the exact section, line and word layout of the 103 odd pages. That text was scored against the real odd pages. The self-citation model's two probabilities were tuned on the even pages only.

| | name rate | repetition | rep. ratio | near-repeats | line MI | page-specific | section signal | **distance** |
|---|---|---|---|---|---|---|---|---|
| **Real odd pages** | 0.19 | 0.0081 | 2.44 | 1.77 | 0.225 | 0.28 | 0.36 | 0 |
| Section word frequencies | 0.29 | 0.0049 | 1.49 | 1.31 | 0.004 | 0.21 | 0.32 | 5.3 |
| Self-citation (Timm & Schinner style) | 0.60 | 0.0113 | 3.80 | 4.26 | 0.201 | 0.20 | 0.39 | 9.8 |
| **Self-citation, tuned on the even pages** | 0.59 | 0.0100 | 3.36 | 2.14 | 0.194 | 0.20 | 0.32 | **4.8** |
| Verbose cipher of real Latin herbals | 0.08 | 0.0044 | 0.45 | 1.05 | 0.001 | 0.004 | 0.06 | 7.8 |

**Findings:**
- **No model reproduces the manuscript.** The tuned self-citation model comes closest (4.8).
  - It reproduces the line units (MI 0.19 against 0.225) and the repetition rate.
  - It fails on one measure: it reuses page words three times too often (name rate 0.59 against 0.19).
- **The verbose cipher fails on every measure.** A chunk cipher of continuous Latin produces no line units, no repetition and no page-specific vocabulary. This makes a cipher of ordinary herbal prose very unlikely.
- **New constraint for any explanation: the repetition is very short-range.** The real text repeats a word *next to itself* 2.4× more than chance, yet does not reuse words across a page (17%). Copying from the last ten words, as the published generator does, cannot produce both. Any generator, cipher or language must copy only from the immediately preceding word or two.

## 3. Copper Scroll: where the Greek groups sit (`copper/positions.py`)
Source: the Hebrew transcription on Hebrew Wikisource (CC BY-SA). It gives the scroll's numeral signs as digits and the Greek groups in place. The DJD III plates are still copyrighted. Wikimedia's photographs, including the Louvre facsimile and the Amman strips, could not be downloaded because Wikimedia's rate limit refused the requests.

| Group | Position in its entry |
|---|---|
| ΚΕΝ, ΘΕ, ΔΙ | at the very end, **after the amount** |
| ΧΑΓ | at the very end (the entry has no amount) |
| ΣΚ | after "talents [lost]", at the end |
| **ΗΝ** | **between the unit and the number**: "talents ΗΝ 42" |
| **ΤΡ** | **between the unit and the number**: "silver, talents ΤΡ 40" |

- **All seven groups are attached to the entry's closing quantity; none sits in the place description.** For random positions within each entry the chance is 2 × 10⁻⁶. That figure overstates the case, because a scribe adding a tag naturally writes it at the end.
- **ΗΝ and ΤΡ are the informative cases.** They take the slot between the unit word and the numeral.
- Together with round 74 (the groups are not numerals and do not equal the amounts), this points to **marks that qualify or check the amount** in the first section of the list, such as a standard, a lot or an auditor's mark, rather than to place names or hidden numbers.
- Grade: C, a pattern that is suggestive but not yet tested against an alternative.
- **Next step:** the line breaks in the plates (Puech 2006 or the EDF facsimile), to see whether ΗΝ and ΤΡ were squeezed in later.

## 4. Antikythera: newer readings
- **What was searched:** 2017–2025 literature on the Front Cover Inscription.
- **What it found:** nothing that supersedes the *Almagest* 7.1 (2016) edition already used. The 2021 *Scientific Reports* model relies on that edition, and the 2025 *Heritage* paper discusses accuracy, not new readings.
- **The NYU archive copy could not be fetched:** archive.nyu.edu is outside this session's allowed network.
- **Status:** the round-75 predictions (Saturn 2×120 + 2×8 + 122 = 378; "224" is Venus's closing interval; "64" unidentified) stay open until new imaging or readings appear.

## 5. Signs Gospel, pre-registered test 3 (`signs/PREREGISTRATION_3.md`, `signs/ruckstuhl.py`)
The question: are the evangelist's own characteristics, from Ruckstuhl's and Schweizer's lists, thinner in the sign stories? The test counts 11 of these characteristics.

| | per 100 words | null (John, matched) | p (lower) |
|---|---|---|---|
| **Core sign stories** | 3.43 | 4.19 | **0.051** |
| Without chapter 21 | 3.47 | 4.16 | 0.09 |
| Power check: Mark's miracles | 0.64 | 4.13 | 0.0002 (passes) |

**Pre-registered decision: EVANGELIST'S STYLE PRESENT, by the narrowest margin** (p = 0.051 against a 0.05 threshold).

- **What the numbers say:** the sign stories carry 82% of the evangelist's characteristic density. Mark carries 15%. The stories sit much closer to John than to another author.
- **Where the shortfall comes from:** characteristics of speech (ἐμός, ἀμὴν ἀμήν, καθώς, ἀπεκρίθη καὶ εἶπεν), which narrative scenes rarely need. The narrative ones are at the normal rate: οὖν, ἵνα, partitive ἐκ, τότε οὖν.
- **The Signs Gospel question is settled at this level:**
  - The core miracle stories are distinguishable (round 74).
  - No source marker carries over (round 74b).
  - The stories are written largely in the evangelist's own style (this round).
  - If a source exists, it has been thoroughly rewritten, which is close to the modern majority view.
