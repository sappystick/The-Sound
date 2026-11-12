# Pre-registration, round 93: coherence at every level, reading direction, page order, pointers

Committed **before** `coherence.py` exists. Data: ZL3b-n paragraph text, with metadata. Every test is scored against its own shuffle null. Where a comparison text is useful, the same measure is run on Greek John and English John (pages of the Voynich's median size) and on the Latin herbal Macer.

## C. Coherence at each level
| Level | Measure | Null | "Coherent" if |
|---|---|---|---|
| **Body** | Vocabulary similarity (cosine of word counts) of consecutive pages | random page pairs from the same section | consecutive > random, p < 0.01 |
| **Page** | Divergence between the two halves of a page | halves taken from two different pages of the same section, size-matched | own halves closer, p < 0.01 |
| **Line** | Share of word pairs in one line that share a root | the same for pairs drawn from neighbouring lines | within-line > across-line, p < 0.01 |
| **Word** | Held-out glyph cross-entropy of words (character 4-gram) | the same words with glyphs shuffled inside each word | real far below shuffled (descriptive) |

## D. Reading direction
- **D1 glyphs:**
  - **Measure:** a character 4-gram model trained on even pages and scored on odd pages, run once forward and once with every line reversed.
  - **Statistic:** asymmetry = backward bits − forward bits per glyph, compared with the language controls.
  - **Descriptive:** it says which direction the system "expects".
- **D2 words:**
  - **Measure:** a held-out bigram word model, forward against backward (round-92 pipeline).
  - **Descriptive.**
- **D3 vertical reading:**
  - **Measure:** words in the same position in consecutive lines (directly above each other). Rate of identical words and of one-glyph near-identical words.
  - **Null:** the rate with the lower line shifted by a random offset.
  - **Decision:** vertical structure if p < 0.01.

## O. Page order
- **O1:** similarity of the two sides of one leaf (recto and verso), against random pages of the same section.
- **O2:**
  - **The question:** were the pages written as bifolia (sheets folded in two)?
  - **Measure:** within each quire, leaves are paired as conjugates by position (first with last, and so on). Their similarity is compared with that of physically adjacent leaves.
  - **Decision:** conjugates > adjacent at p < 0.01 means the **text follows the sheets, not the present page order.**
  - The pairing is approximate wherever quires are irregular.

## P. Pointers: do the pictures point somewhere else?
- **P1, offset test:**
  - **Measure:** each page's illustration type is predicted from its own text (nearest centroid, leave-one-out). Agreement with the illustration type of the page **k places away** is measured for k = −6 … +6 in manuscript order.
  - **Decision:** if the peak is at k ≠ 0 and beats k = 0 at p < 0.01 (paired bootstrap), the **text is displaced relative to the pictures**, pointing elsewhere.
- **P2, misfits:**
  - **Measure:** pages whose text classifies as a different section than their picture.
  - **Question:** do they sit at quire boundaries more than chance? That would point to misbinding rather than content (one-sided, permutation).
