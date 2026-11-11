# Pre-registration, round 50: reruns of the four suggestive results, out of sample

**Rules:**
- This file is written and committed **before** `power/round50_reruns.py` exists or is run.
- Every test below is fixed here: its data, its definitions, its null, and the rule for passing.
- Results that fail are reported as failures.

**Correction:** the four primary tests (R1–R4) are corrected together by Holm's method at α = 0.05. The secondary tests are reported without correction and labelled as secondary.

## R1. The middle "I am" (John 10:11) at the book's centre, measured without syllables
- **Units:**
  - **R1a, primary:** manuscript lines of Codex Sinaiticus (01), from CNTR line breaks.
  - **R1b, primary:** manuscript lines of Codex Vaticanus (03), same method.
  - **Secondary:** words, letters and verses (SBLGNT).
- **Position:** the fraction of John's units (from 1:1 to the end of 21:25) that precede the middle of 10:11.
- **Null:** the 4th of 7 uniformly random points, the same as in rounds 45–46.
- **Pass:** p < 0.05 (two-sided distance from 0.5) in **both** 01 and 03.

## R2. "Jesus in the middle": out of sample, in Revelation
- **Data:** every occurrence of the lemma μέσος in Revelation (SBLGNT).
- **Labelling rule, fixed now:** an occurrence is a "yes" if the entity said to be *in the middle* is Jesus, the Lamb, or "one like a son of man". Anything else is "no". Each label is listed in the results with its verse.
- **Test:** one-sided binomial against the Synoptic base rate of 5/26 = 0.192 (round 44).
- **Pass:** p < 0.05.

## R3. Vision chapters rise in loudness: new chapters only
- **Data:** the round-42 lexicon, loudness ranks and Kendall τ method, unchanged.
- **Chapters, fixed now** (none used in round 42):
  - Ezekiel 9, 37, 40;
  - Daniel 8, 12 (Theodotion);
  - Zechariah 1, 2, 4, 6;
  - Joel 2; Habakkuk 3; Isaiah 24, 29, 66;
  - Revelation 5, 6, 7, 9, 12, 13, 15, 17, 18, 20, 21, 22;
  - Acts 9, 10.
- **Included chapters:** only those with at least 4 events and more than one loudness rank.
- **Test:** mean signed τ against the same events shuffled within each chapter (5,000 shuffles).
- **Pass:** one-sided p < 0.05 with mean τ > 0.

## R4. "I am" verses end on the mese under the accent melody: out of sample, in the Greek Old Testament
- **Data:** every Septuagint verse (Swete) containing ἐγώ immediately followed by εἰμι.
- **Accent rule:** as in round 46, applied to the Swete text's accents.
- **Cadence:** the last syllable of the verse.
- **Test:** one-sided binomial against the mese-cadence rate of all other Septuagint verses.
- **Pass:** p < 0.05.

## S5. Secondary: Aramaic lean of the power sayings, out of sample
- **Data:** Matthew and Luke verses containing ἀμὴν λέγω (the "power" set), against the other verses of each book.
- **Method:** the round-46 Greek − Syriac difference in differences, unchanged.
- **Prediction:** a negative difference.
- **Reported:** uncorrected.

## Also in this round (not tests)
**Psalm 24 re-rendered with Second Temple vowels:**
- Tiberian *qamets* is read as long ā rather than ɔ.
- Shewa is read as a short ɛ.

**Other units of measure, and other texts that fit the mold** (descriptive):
- the Chaldean planetary order with the Sun 4th of 7;
- the menorah as the planets (Philo; Josephus);
- Genesis 1, day 4.
