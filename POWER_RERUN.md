# Round 50: the pre-registered reruns, Psalm 24 with Second Temple vowels, other measures, and the mold

**Pre-registration:** `robustness/PREREG_R50.md`, committed as `9912dff` before the analysis script was written.

**Files:**
- script `power/round50_reruns.py` (seed 50);
- numbers `power/round50_results.json`;
- audio `power/audio/r50_tamid_psalm24_lyre_second_temple.mp3`.

## 1. The four reruns, on new data
| Test | New data | Result | Pre-registered rule | Holm-adjusted p |
|---|---|---|---|---|
| **R1.** The middle "I am" (10:11) at the book's centre, measured by manuscript lines | Codex Sinaiticus: 5,180 lines of John · Codex Vaticanus: 4,081 lines | 01: **0.4897**, p 0.045 · 03: **0.4876**, p 0.054 | p < 0.05 in both | 0.11: **fails, narrowly** |
| **R2.** "Jesus in the middle" | **Revelation:** 8 uses of μέσος | **5 of 8** put Jesus / the Lamb / one like a son of man in the middle (1:13; 2:1; 5:6 twice; 7:17), against a Synoptic base rate of 19% | p < 0.05 | **0.026: passes** |
| **R3.** Vision chapters rise in loudness | 26 new chapters; 10 have enough events | mean τ +0.05 against 0.00 | p < 0.05 | 0.31: **fails** |
| **R4.** "I am" verses end on the mese (accent melody) | **Septuagint:** 168 "I am" verses | **43.5%** against 30.9% | p < 0.05 | **0.0016: passes, but see the mechanism below** |

### Reading the results
**R2 replicates out of sample.** In Revelation, as in John, the middle place belongs to Jesus:
- "in the middle of the lampstands, one like a son of man" (1:13);
- "he who walks in the middle of the seven lampstands" (2:1);
- "a Lamb … in the middle of the throne" (5:6, 7:17).

Counting 5:6 once instead of twice still gives 4 of 7, p ≈ 0.03. **Status: V** (pre-registered, out of sample). The labels follow the fixed rule, but the labeller knew the texts.

**R4 passes, but for a grammatical reason.**
- The Septuagint "I am" formula is "I am the LORD your God".
- Its verses often end on an unaccented little word (μου, σου, σε, or εἰμι itself) or on a circumflexed ὑμῶν / αὐτῶν. In our accent melody all of these fall on the mese.
- **The cadence comes from the formula's grammar and from our mapping choice** (unaccented syllables go on the mese), not from a tuning.
- **Status: V as a pattern; N as evidence of an instrument.**

**R1 fails narrowly, but the result is the same in every unit.**
- 10:11 stands at 0.486–0.490 of John whether it is counted by:
  - Sinaiticus lines or Vaticanus lines;
  - words, letters or spoken time (morae, the vowel-length count).
- By **verses** it is at **0.5017** (p 0.0075): almost exactly the middle verse of the Gospel.
- But the pre-registered rule needed p < 0.05 in both manuscripts, and Vaticanus gave 0.054.
- **Status: O.** A consistent position, just short of the pre-registered threshold.

**R3 does not replicate.** The rising loudness of round 42 was specific to its chapters. **Status: N.**

### Secondary (S5, uncorrected): the Aramaic lean of the "Amen, I say to you" sayings
| Book | Sayings | Greek − Syriac, sayings | Greek − Syriac, rest | Difference | p |
|---|---|---|---|---|---|
| **Matthew** | 26 | −0.49 | +0.08 | **−0.57** | **0.044** |
| Luke | 5 | −0.39 | +0.11 | −0.50 | 0.41 |

- In Matthew, as in John, the solemn sayings pattern relatively better in Aramaic than the rest of the book does.
- Luke points the same way, with too few cases to test.
- **Status: O, strengthened.** The sayings of Jesus may carry an Aramaic sound-layer under the Greek.

## 2. Psalm 24 with Second Temple vowels
**The change:** *qamets* is read as long ā, as Origen's *Secunda* and the Septuagint's transcriptions write it with α, instead of the medieval Tiberian ɔ.

**The effect:**
- The low **Saturn string falls silent** (25% → 0%).
- The **Moon string, the top string, rises to 36%**, and becomes the most-sounded string of the psalm.
- The Second Temple psalm is played high and bright, centred on α. The medieval reading sat low on ω.

**Listen:** `r50_tamid_psalm24_lyre_second_temple.mp3`, against the round-49 Tiberian version.

## 3. Measuring without syllables: what it looks like
| Unit | What it measures | 10:11's position |
|---|---|---|
| Manuscript lines, Sinaiticus | the physical page: the scribe's space | 0.490 |
| Manuscript lines, Vaticanus | the same, another scribe and format | 0.488 |
| Letters | the written text | 0.488 |
| Words | the units of sense | 0.486 |
| Morae | spoken time | 0.487 |
| **Verses** | **the units of reading** | **0.502** |

The middle "I am" stays at the centre whatever is counted. It is not an artefact of syllables.

**Other ways of measuring still to try:**
- **performed seconds**, with pauses at the sense breaks;
- **breath groups**;
- **narrative time:** the days of the story;
- **place:** the itinerary, with Jerusalem as a centre;
- **speakers:** how much of the book each voice holds;
- **the audience's actions:** where a listener responds, for example "Amen".

## 4. What else fits the mold: seven, with a governing middle
The same shape recurs across the sources: **seven, with the centre as the leader**.

| Seven | Its middle | Source (read in this round, unless marked) |
|---|---|---|
| The lyre's seven strings | the **mese**, the leader string | Nicomachus; [Aristotle], *Problems* 19.20 |
| The seven planets, Chaldean order (Saturn, Jupiter, Mars, **Sun**, Venus, Mercury, Moon) | the **Sun**, 4th of 7 | Ptolemy, *Almagest* 9.1 (from the literature) |
| The menorah's seven lamps | the **central shaft and lamp** | Exod 25:31–37 |
| The menorah as the planets | the lamps "imitate the planets" | **Josephus**, *Antiquities* 3.144–146; *War* 5.217 |
| The menorah as the **choir (χορεία) of the seven planets** | "**the middle of the seven, the sun**", attended and guarded on each side | **Philo**, *Who is the Heir* 221–225 |
| Seven lampstands in Revelation | "**in the middle of the seven lampstands, one like a son of man**" (1:13; 2:1) | Revelation, and R2 above |
| John's seven "I am" sayings | **the good shepherd, 10:11**, at the book's centre | rounds 45–50 |
| The Babylonian lyre (nine strings) | string 5, ***qablītum*, "the middle"** | Kilmer; West (from the literature) |
| Genesis 1: seven days | day 4, sun and moon, is **not** at the centre by words (0.41, p 0.37) | **N** |

**Reading:** Philo and Josephus, both Jewish writers of John's century, read the Temple's lampstand as the seven planets with the Sun in the middle, and Philo calls the planets a *choir*. Revelation, from John's circle, places the Son of Man in the middle of the seven lampstands.
- On Nicomachus's lyre the Sun is the mese.
- In John the fourth of seven "I am" sayings stands at the book's centre.
- Wherever John's tradition counts to seven, the middle place is Jesus.

This is one image, the light in the middle of the seven, expressed as lamps, planets, strings and sayings.

## Scorecard after the reruns
| Claim | Status |
|---|---|
| The middle place belongs to Jesus (John, then Revelation out of sample) | **V** |
| The middle "I am" at the book's centre | **O**: same position in every unit; just short of the pre-registered threshold in Vaticanus |
| "I am" verses end on the mese | V as a pattern, but grammatical (the formula's pronoun endings) |
| Vision chapters rise in loudness | **N** (did not replicate) |
| The solemn sayings carry an Aramaic layer | **O**, strengthened (Matthew, p 0.044, secondary) |
