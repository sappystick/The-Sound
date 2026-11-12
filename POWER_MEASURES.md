# Round 51: other ways of measuring, and the band

**Files:**
- script `power/round51_other_measures.py` (seed 51);
- numbers `power/round51_results.json`;
- audio `power/audio/r51_band_john_10_11.mp3`.

## 1. Where is the middle "I am" (10:11) by performed time, breath and story?
**How the units are counted:**
- **Performed time:** the engine's declaimed timing of every verse, plus pauses at the punctuation (full stop or question 0.8 s, raised dot 0.6 s, comma 0.3 s). The whole Gospel takes **3 h 25 min**.
- **Breath groups:** stretches between punctuation marks, with any group over 25 syllables split. John has 2,443 of them.

| Unit | Gospel as transmitted (1:1–21:25) | **Gospel ending at 20:31** |
|---|---|---|
| Performed seconds | 0.487 (p 0.059) | **0.505 (p 0.022)** |
| Breath groups | 0.473 (p 0.12) | **0.495 (p 0.023)** |
| Words | 0.486 (p 0.061) | **0.504 (p 0.017)** |

**What explains the "slightly off" position:**
- In every unit tested since round 45, 10:11 has sat 1–1.5% before the centre.
- That offset is the size of **chapter 21**.
- Chapter 21 is widely judged an epilogue added after the Gospel's first ending at 20:30–31 ("Many other signs … these are written that you may believe"; **K**: Brown 1970; most commentators).

**Measured on the Gospel that ends at 20:31:**
- the fourth of seven "I am" sayings stands on the centre: 0.495–0.505;
- in performed time, breath and words alike;
- p ≈ 0.02 in each.

**Status: O, exploratory.**
- I chose this ending after seeing the offset.
- It must be pre-registered and rerun on the manuscripts (01 and 03 lines, ending at 20:31) before it counts.
- The pre-registered R1 of round 50 remains a narrow failure.

**Story time** (a model built on John's festival frame: Passover AD 28, Passover 29, Tabernacles and Dedication 29, Passover 30):
- 10:11 falls on about **day 608 of 776**, position 0.81. It is **not** the centre of the story.
- The book slows down the end of the story: **42% of the Gospel is spent on the last week** (12:1 onward).
- The centre is a centre of the **telling**, not of the events.

**The mold, once more:** 7:14, "when the feast was already **at its middle** (μεσούσης), Jesus went up into the temple and taught". Here the verb is μεσόω, which was not part of the tests.

## 2. Is the instrument failing only because of how we assign vowels to strings?
**No, for two tests this can be proved:**
- **The mode test (P2).** It is a table of final vowels by movement. Reassigning vowels to strings only relabels the columns, so χ² cannot change: it is **27.544 under three random assignments**. No tuning can create modes that are not there.
- **"I am" cadences.** Without any mapping, do "I am" verses end on a different *vowel* distribution from other verses? χ² 6.1, p 0.40: **no**. So no assignment of vowels to strings can make them end on the mese more than other verses.

**Calc:** these two failures are properties of the text, not of the measuring.

## 3. The band: other instruments, other layers
Each instrument carries one layer of the text. Do the four movements (cuts 1:16, 13:33, 18:1) differ in any layer more than random cuts do?

| Instrument | Layer | p | Label |
|---|---|---|---|
| Drum | the accent pattern of each verse's last word | 0.99 | N |
| Lyre | the final vowel of each verse | 0.17 | N |
| Aulos | breath groups per verse | 0.12 | N |
| **Time** | **performed seconds per verse** | **0.006** | **V** |

**The tempo layer changes by movement:**

| Movement | Seconds per verse | Breath groups per verse |
|---|---|---|
| Prologue | 10.9 | 2.5 |
| Signs | 13.8 | 2.7 |
| Farewell | 14.1 | 2.9 |
| Passion | **16.4** | **3.5** |

**Reading:**
- The "mode" the instrument model was looking for exists, but in **time**, not in pitch.
- The Gospel's breaths lengthen as it moves toward the passion: each verse longer, with more breaths. The prologue is the tightest.
- A band would show the movements by *tempo and breath*, not by changing strings.
- **Caveat:** verse length also tracks genre (narrative verses are longer), so this is a property of the telling, not proof of a score.

## 4. The band plays John 10:11
`r51_band_john_10_11.mp3` plays "I am the good shepherd. The good shepherd lays down his life for the sheep":
- the lyre and vowel tubes play the vowels;
- an aulos drone holds the mese (220 Hz), with its overtones;
- a drum strikes every accented syllable;
- a trumpet *tekiah* closes it;
- all in a Temple acoustic.

## 5. What changes in the picture
1. **The "slightly off" centre is explained.**
   - The off-centre position of the middle "I am" matches the epilogue's length.
   - On the Gospel ending at 20:31 it sits on the centre in time, breath and words.
   - Exploratory; it needs a pre-registered manuscript rerun.
2. **Pitch-level failures are real, not measurement errors.** No vowel-to-string tuning can rescue them.
3. **The structure is carried by time and breath.** That is the band's real score: tempo slows, and breaths lengthen, toward the passion.
