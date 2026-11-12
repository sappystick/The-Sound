# Round 91: Move 2, Currier A and B as an internal Rosetta

Pre-registered in `voynich/ROSETTA_PREREG.md`, committed before the script. Script `voynich/rosetta.py`, results in `voynich/rosetta_results.json`. The material is herbal pages only, so the illustration genre is held fixed:
- herbal-A: 94 pages, 7,248 tokens;
- herbal-B: 32 pages, 3,244 tokens.

**The question.** Are A and B two encodings of the same kind of content, an internal bilingual that needs no outside key? Or are they the same writing system applied to different content?

## 1. Lexical distance (R1, descriptive)
- The Jensen–Shannon divergence between herbal-A and herbal-B is **0.567**. Two halves of herbal-A, token-matched, give **0.340 ± 0.004**.
- 56% of herbal-B's tokens are word types that also occur in herbal-A.
- On the same plant-page genre, A and B differ far more than sampling explains.

## 2. Structural correspondence (R2, primary): **INCONCLUSIVE, the method has no power**
| Pair | S (co-occurrence kept by the mapping) | null mean (95%) | p |
|---|---|---|---|
| **Positive control:** Greek John against English John | 0.015 | 0.001 (0.040) | 0.28 |
| Negative control: Greek John against English Genesis | 0.014 | 0.000 (0.039) | 0.27 |
| Same-system ceiling: herbal-A odd against even pages | 0.006 | 0.003 (0.042) | 0.44 |
| Herbal-A against herbal-B | 0.029 | 0.001 (0.041) | 0.12 |

The positive control fails: the method cannot detect that Greek John and English John share content. **By the pre-registered rule the verdict is INCONCLUSIVE.** The herbal result cannot be read either way.

**Exploratory refinement** (graph matching learned on even pages, scored on odd pages) also fails every control. Its sharpest diagnostic: matching herbal-A **against itself** recovers the true word identity for only **3%** of the 60 commonest words. Its proposed pairs for John are random (και = "he", ιησους = "me").

**What this establishes (useful in itself):** with a few thousand tokens per side, co-occurrence statistics are too noisy to align vocabularies word for word, even between two halves of the *same* text. **Any claimed A ↔ B "dictionary" built from word distributions alone at this scale is unsupported.** The same applies to any Voynich "translation" obtained by matching its word statistics to a candidate language.

## 3. Rewrite rules (exploratory 2): A and B are partly the same words, re-spelled
Rules were learned greedily on even pages and judged on odd pages.
- **The rules found:** -or → -edy, -ol → -dy, -chy → -ar, -ody → -ol, -ain → -or, -eedy → -ain, -dy → (dropped), and t- and l- dropped.
- **Effect on held-out pages:** the divergence falls from **0.612 to 0.525**, which closes **38%** of the gap to the same-language ceiling (0.385).
- **Random rules of the same number make it worse** (mean 0.776, best of 200 random sets 0.650).

**Reading:**
- About **two-fifths of the A/B difference is a systematic affix shift.** The leading shifts are A's -or / -ol endings corresponding to B's -edy / -dy, as in chor → chedy and chol → chdy. Currier (1976) described this contrast qualitatively; this round measures it out of sample.
- The **other three-fifths is not re-spelling.** B uses different words and word frequencies, even on plant pages.

## 4. Where this leaves the A/B Rosetta
- **Not shown:** that A and B encode the same content. The decisive word-level test is **underpowered at this corpus size**, demonstrated by controls in which the answer is known.
- **Shown:**
  - A and B share a vocabulary whose endings are systematically shifted (38% of the difference);
  - beyond that, they differ in word choice;
  - so they are best described as **two dialects or registers of one writing system, used with different word preferences.** That rules out both a fully independent system and a simple letter-for-letter re-encoding.
- **What would make the Rosetta testable:** a unit larger than the word that can be matched across A and B without statistics. Two candidates:
  - **repeated multi-word phrases** that occur in both languages after the affix rules are applied;
  - the **few herbal plants drawn twice**, once in an A section and once in a B section, if any can be identified from the images.
- Either would give aligned pairs directly, instead of inferring alignment from noisy co-occurrence. This is the next move: the **"phrase anchors" test**.

## Status
- Move 2 pre-registered decision: **INCONCLUSIVE** (method power).
- Exploratory: **A and B are partly the same vocabulary with systematic ending shifts** (38% of the gap, held out). The rest is a difference in word choice.
- Methodological result: distribution-based word alignment fails even against the text itself at this scale.
