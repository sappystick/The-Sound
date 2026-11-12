# Round 40: open investigations closed, and the methods applied across both Testaments

The code is in `round40/investigate.py`, the output in `round40/results.json` and the log in `round40/log.txt`.

Sources:
- Hebrew: WLC (morphhb).
- Greek NT: SBLGNT (MorphGNT).
- Septuagint: Swete.
- English: the Berean Standard Bible, used only for its quotation marks, as a speech signal independent of the Greek and Hebrew.

## 1. Where does John's farewell begin: 13:1 or 13:31?

The new signal knows no Greek. It is the share of each verse that the BSB translators put inside quotation marks.

| Signal | Blind cuts (4 parts) | p against Brown's outline |
|---|---|---|
| Translators' quotes (new, independent) | 3:2 · **13:33** · 17:26 | 0.014 |
| Greek 1st/2nd-person morphology | 4:8 · **13:33** · 18:1 | 0.057 |
| Quotes, 5 parts | 3:2 · 10:40 · **13:32** · 17:26 | |
| Quotes, 6 parts | 1:20 · 5:19 · 10:39 · **13:32** · 17:26 | |

**Result.** At every resolution, an independent signal places the farewell break at 13:32–33, not at 13:1. This is where Judas has gone out and Jesus begins "Little children…". It is the line Brown's outline draws at 13:31, so the voice data now favours the 13:31 division over the 13:1 one, by two independent taggers.

Taken alone, the BSB p = 0.014 would not survive the project-wide correction. The *location* replicating is the point.

## 2. Voice-drawn outlines in other books

For each book, the outline was fixed before running. Each test uses 20,000 random cut sets.

| Book | Signal | Blind cuts | Agreed outline | p |
|---|---|---|---|---|
| **Revelation** | Greek person morphology | 2:1 · **4:1** · **22:6** | 1:9 · 4:1 · 22:6 | **< 0.0001** |
| **Job** | Translators' quotes | 3:8 · 31:38 · 33:18 · 41:10 | 3:1 · 32:1 · 38:1 · 42:7 | **0.0001** |
| Deuteronomy | Quotes | 5:33 · 26:5 · 31:22 | 4:44 · 29:1 · 31:1 | 0.09 |
| Deuteronomy, Job | Hebrew person morphology | n.s. | | 0.36–0.58 |
| Hebrews | Both | n.s. | | 0.49–0.86 |
| Acts (control) | Both | n.s. | | 0.41–0.60 |

**Result.** Two more books have outlines drawn by their voices: Revelation and Job.
- **Revelation.** The cuts hit 4:1 ("After this I looked…") and 22:6 (the epilogue) exactly. The seven letters are a block of direct address, and the visions are narration.
- **Job.** The cuts fall within a few verses of the start of the dialogue and the end of Job's speeches (31:40). The LORD's speech is found 3 chapters in.

Deuteronomy is nearly all Moses speaking, so the signal has nothing to separate. That is a correct null. Hebrews (a sermon) and Acts behave as controls.

This extends C24 from one Gospel to a pattern: **books built from alternating speakers carry their outline in the voice.** Each p here is a single test; these are pre-registered candidates for the next audit.

## 3. Ketiv and qere: written against read

Across the 1,245 places where the Masoretes wrote one form and read another:
- **88% are sound-alikes.** 86.5% differ only in vowel letters (א ה ו י). 15 are the *lo/lo* pair (לא "not" against לו "to him"), identical in sound. 7 have the same letters with different vowels.
- Only 10% are a different sound. 0.6% swap letters, which is a slip of the eye rather than the ear.

**Result.** The Hebrew Bible's own marginal corrections are overwhelmingly matters of how a word *sounds* when spelled. This is the Hebrew parallel to C11 (52–60% of Greek manuscript variants are homophones in Koine).

## 4. The Masoretic midpoints against today's text

| Claim (Talmud, Kiddushin 30a) | Computed in the Leningrad text | Distance |
|---|---|---|
| Middle letter of the Torah: the vav of *gachon* (Lev 11:42) | Lev 8:29 | 93 verses |
| Middle words: *darosh darash* (Lev 10:16) | Lev 8:15 | 61 verses |
| Middle verse (Lev 13:33) | Lev 8:9 | 159 verses |
| Middle verse of Psalms (Ps 78:38) | Ps 78:36 | **2 verses** |
| Middle letter of Psalms (Ps 80:14) | Ps 77:1 | 119 verses |

**Result.** This agrees with the known modern finding: the Talmud's letter and word midpoints do not match the received text. The Masorah's own verse note puts the Torah's middle verse at Lev 8:8, and the count here gives Lev 8:9, essentially the same place. The Psalms verse midpoint is within 2 verses.

This bears on the "life" centre result: the counting traditions themselves drifted, so the centre tests should be run by verse as well as by letter. Five of our "life" hits are by letter.

## 5. "Life" at the centre: Greek replication

| Corpus | Books whose centre contains *zōē* | Expected | Exact p |
|---|---|---|---|
| Hebrew Bible, *chayyim* (round 39) | 5 of 39 | 0.86 | 0.0008 |
| Greek NT | 2 of 25 | 2.07 | 0.63 |
| Septuagint | 3 of 55 | 1.82 | 0.27 |

**Result.** It does **not** replicate in Greek, including in the Greek translation of the same Hebrew books. The effect, if real, belongs to the Hebrew letter-text, which is consistent with a compositional or scribal feature rather than a theme of the books. It stays in Tier B.

## 6. Semitic sounds left untranslated in the NT

- **Untranslated Semitic words per 1,000 words.**
  - John has the most: 4.2.
  - Mark: 2.6.
  - Matthew: 2.4.
  - Luke keeps far fewer.
- **Opening *amēn* ("amen, I say to you").** Used as a solemn opener, it is unique to Jesus' speech:
  - John 50, always doubled;
  - Matthew 27;
  - Mark 12;
  - Luke 5.
- **The four Aramaic sayings.** Mark alone keeps them all: talitha koum, ephphatha, abba, and eloi … sabachthani.
- **Hallelujah.** It is found only in Revelation 19, four times, all in the heavenly liturgy.

**Result.** The untranslated sound is concentrated in Jesus' own voice and in worship. This adds to round 37.

## 7. Stated numbers, checked

| Claim | Computation | Rarity among 39,611 Hebrew forms |
|---|---|---|
| Eliezer = 318 (the 318 men, Gen 14:14) | אליעזר = 318 ✓ | 66 forms share the value |
| Nero Caesar = 666 (Rev 13:18) | נרון קסר = 666 ✓ | 38 |
| …and the variant **616** (P115, Codex C) | נרו קסר (the Latin spelling) = 616 ✓ | 59 |
| 153 fish (John 21:11) | *bene ha-Elohim* = 153 ✓. 153 = 1 + 2 + … + 17 (a triangular number) ✓ | 54 |
| *ichthyes* ("fishes") and *to diktyon* ("the net") | both = 1224 = 8 × 153 ✓ | |
| *ichthys* (singular) | 1219, which does not match | |

**Result.** The 666/616 pair is the strongest. Two manuscript readings both match one name, spelled the Hebrew way and the Latin way. That is a textual variant explained by a sound and spelling difference. The 153 links are arithmetically real, but they are found after the fact.

## 8. Breath units in the Hebrew Bible

The atnach accent divides each verse into halves. Measured in syllables per half-verse:
- **Proverbs:** 7, the most even of the books measured (CV 0.28).
- **Psalms and Job:** 8.
- **Lamentations:** 13. Its evenness (CV 0.35) is the second best, as expected of an acrostic dirge.
- **Narrative:** 13–14 (CV 0.46–0.50).

**Result.** The poetry has short, even breath units. At a slow chant of about 2 syllables a second, a Psalm half-verse lasts about 4–5 s. Two of them make one breath cycle of about 8–10 s: **6–7 breaths a minute, the resonance-breathing rate.** This is an inference, not a measurement of singers.

## 9. Room modes of the described buildings

| Room | Lowest mode | Modes up to 120 Hz | Distinct frequencies |
|---|---|---|---|
| Tabernacle, most holy place (10-cubit cube) | 38.5 Hz | 28 | **8** |
| Solomon's debir (20-cubit cube) | 19.3 Hz | 177 | **33** |
| Ordinary room of the same volume | 15.3 Hz | 175 | 79 |
| Solomon's hekal (40 × 20 × 30) | 9.6 Hz | 492 | 95 |
| Ezekiel's nave (40 × 20 × 20, height assumed) | 9.6 Hz | 337 | 60 |
| New Jerusalem (12,000-stadia cube) | one cycle every 3.6 hours | | |

**Result.** Each holy-of-holies cube concentrates its resonance: the debir puts 177 modes on 33 frequencies, against 79 for an ordinary room. Its strongest band in the voice range is **123.4 Hz (15 coinciding modes)**, which is the root the sound engine uses for "debir".

## Open now

These items are still open:
- Listeners for E1, E2 and E5.
- A second annotator for John's speech.
- A verse-count rerun of the "life" centres.
- Revelation and Job in the next pre-registered audit.
- The magical corpora not reachable here: Preisendanz's Greek, Sepher ha-Razim, the Sword of Moses.
