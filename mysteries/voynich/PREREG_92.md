# Pre-registration, round 92: phrase anchors, information budget, low-rate channels, a unique-system control

Committed **before** `anchors.py`, `budget.py` and `channels.py` exist. Data: ZL3b-n paragraph text.

## P. Phrase anchors (the A/B Rosetta by aligned units)
**Normalisation formulas,** each applied to both sides before counting:
- **F0** identity.
- **F1** the affix rewrite rules of round 91, re-learned on **even** pages.
- **F2** root only: strip the learned prefix and suffix sets.
- **F3** suffix class: every suffix collapses to one class symbol, keeping prefix and root.
- **F4** skeleton: drop the glyphs e, o, a, i and y.
- **F5** F1 followed by F4.
- **F6** F2 followed by F4.

**Counting.** Shared phrase types (bigrams and trigrams) between two corpora, counted on **odd** pages only, so F1 is never scored on the pages it was learned from.

**Statistic.** Excess = observed shared types ÷ the mean under a null. The null shuffles the word order within each corpus 200 times, keeping each corpus's word frequencies.

**Three comparisons per formula:**
- **AB:** herbal-A against herbal-B.
- **Ceiling:** herbal-A odd pages against herbal-A even pages, token-matched to herbal-B. Same dialect, same topic.
- **Floor:** herbal-B against stars-B. Same dialect, different topic.

**Decision, per formula** (Holm-corrected over 7 formulas × 2 n-gram sizes):
- If AB's excess is significant (p < 0.01) **and** at least the floor's excess, then AB **shares phrases beyond topic-free system habit**. The shared phrases above the null become **anchors**, listed with their pages.
- If AB's excess does not exceed the floor's under any formula: **NO PHRASE ANCHORS.** A and B share only what any two texts of the system share.

Reported descriptively: which formula brings AB closest to the ceiling.

## I. Information budget
- **Models:** word cross-entropy on odd pages for models trained on even pages:
  - (a) the section unigram;
  - (b) an interpolated bigram, with weights tuned on a slice of the even pages;
  - (c) the same models with each word replaced by its root (content only).
- **Budget:** bits per page = tokens × entropy, using model (b).
- **Controls, run through the identical pipeline:** Latin (Macer), Greek John and English John, each as same-size page splits.
- **Descriptive:** the outcome sets a ceiling on how much any hidden message could hold. It makes no decision about meaning.

## C. Low-rate channels
Five candidate hidden sequences:
- the first glyph of each line;
- the last glyph of each line;
- the first word of each paragraph;
- the gallows glyph (k, t, p, f) of each line in order;
- every 7th word.

**Test for each sequence:**
- **Order:** its conditional entropy (bigram) against 1,000 within-page shuffles of the same sequence, one-sided, Holm over 5.
- **Acrostic repeats:** repeated 4-grams of the line-initial glyphs across pages, against shuffles.

**Decision:**
- p < 0.01 after correction: the channel **CARRIES ORDER** and is reported for follow-up.
- Otherwise: **NO HIDDEN CHANNEL** found there.

## U. Unique-system control (if a transcription can be obtained)
- **Material:** the Rohonc Codex, if a public machine-readable transcription is available. If none is, this is reported as not done.
- **Measures:** the round-66 anomaly measures and the long-range information measure of round 88.
- **Descriptive:** whether the Voynich resembles another one-off system more than it resembles languages.
