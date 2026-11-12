# Pre-registration: Currier A and B as an internal Rosetta (Move 2, round 91)

Written and committed **before** `rosetta.py` exists.

## Question
Are Currier languages A and B **two encodings of the same kind of content**, where a word in A corresponds to a word in B (an internal bilingual that needs no outside key)? Or are they the **same writing system applied to different content**, with no correspondence to exploit?

## Material: topic held fixed
Only **herbal pages** are used: herbal-A (95 pages) against herbal-B (32 pages). Both carry the same illustration genre, so a difference in subject matter cannot explain away a missing correspondence. Paragraph text only, from the ZL3b transliteration.

## R1. Lexical distance (descriptive)
- **Measure:** the Jensen–Shannon divergence between the herbal-A and herbal-B word distributions.
- **Ceiling:** two random page halves of herbal-A, the smaller one token-matched to herbal-B (50 draws).
- **Reported only;** it is already known that A and B differ.

## R2. Structural correspondence: the primary test
If B is a re-encoding of A's content, words that play the same role should behave alike in ways that do not depend on spelling. They should also keep the same partners.

1. **Words.** For each side, the 60 most frequent words.
2. **Spelling-free profile of each word** (z-scored within its side):
   - log frequency;
   - burstiness (cv² of gaps between occurrences);
   - page dispersion (share of pages the word appears on);
   - share of line-initial occurrences;
   - share of line-final occurrences.
3. **Mapping.** A one-to-one A → B mapping by the Hungarian method on profile distance. The mapping uses **no co-occurrence information.**
4. **Score S.** The Spearman correlation between PPMI(a, a′) in A and PPMI(m(a), m(a′)) in B, over all word pairs. PPMI is computed from co-occurrence within a 10-token window.
5. **Null.** 2,000 random one-to-one mappings that keep frequency rank within ±5. This keeps frequency from getting any credit. The p-value is one-sided.

## Controls (fixed now)
- **Positive control: same content, different encoding.** Greek John (SBLGNT word forms) against English John (BSB). Verses are treated as lines and chapters as pages.
- **Negative control: different content, different encoding.** Greek John against English Genesis 1–21, of similar size.
- **Same-system ceiling.** Herbal-A, odd pages against even pages.

## Decision
- **The method is valid only if** the positive control gives p < 0.01 and its S exceeds the negative control's S. Otherwise the verdict is **INCONCLUSIVE: the method cannot detect a re-encoding even when one exists.** In that case the exploratory variant below is reported as exploratory only.
- **If the method is valid:**
  - herbal-A against herbal-B with p < 0.01 and S ≥ the negative control's S: **SHARED STRUCTURE: Rosetta candidate**, and the matched pairs are listed for inspection;
  - p ≥ 0.05: **NO SHARED STRUCTURE**: A and B are not word-for-word re-encodings of the same content;
  - between the two: **WEAK**.

## Exploratory (labelled as such in the results)
- **Refined mapping.** The feature mapping is refined by graph matching on even pages, then scored on odd pages. Its null applies the same refinement to random starting mappings.
- **Rewrite-rule check.** Which suffix and prefix swaps (for example -ol → -edy) best turn A's frequent words into B's, and do they generalise to held-out words?
