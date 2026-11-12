# Round 80: a short-range generator, on held-out Voynich pages (`voynich/heldout.py` → `heldout_results.json`)

Round 79 showed that the Voynich repeats a word next to itself, but rarely reuses words across a page. This round builds a generator with only that short reach.

**The generator (B3).** From the second word of a line onward, each word is one of three things:
- an exact copy of the previous word;
- the previous word with one glyph changed (the glyph swaps are learned from neighbouring words in the training pages, so a new word can appear);
- a fresh draw from the section's words for that line position (first, middle or last).

It never copies from further back and never across a line break. It was fitted on the even pages, and its two probabilities were tuned on the even pages only. It was then scored on the 103 odd pages, with the same layout and measures as round 79.

| | name rate | repetition | rep. ratio | near-repeats | line MI | page-specific | section signal | **distance** |
|---|---|---|---|---|---|---|---|---|
| **Real odd pages** | 0.19 | 0.0081 | 2.44 | 1.87 | 0.225 | 0.28 | 0.37 | 0 |
| Section word frequencies | 0.23 | 0.0049 | 1.57 | 1.23 | 0.002 | 0.21 | 0.39 | 5.4 |
| Self-citation, tuned (round 79's best) | 0.62 | 0.0091 | 3.26 | 2.19 | 0.203 | 0.21 | 0.36 | 4.8 |
| Verbose cipher of Latin herbals | 0.07 | 0.0047 | 0.49 | 1.22 | −0.001 | 0.004 | 0.07 | 7.7 |
| Short-range, rates taken straight from the training pages | 0.41 | 0.0127 | 4.13 | 2.80 | 0.280 | 0.22 | 0.32 | 5.5 |
| **Short-range, tuned on the training pages** | 0.37 | 0.0095 | 2.98 | 2.06 | 0.284 | 0.22 | 0.42 | **2.7** |

Fitted rates: copy 0.97% and one-glyph change 1.47% per word, taken straight from the training pages. Tuned: 0.49% and 0.73%.

## Findings
- **The short-range generator is the best explanation so far.** At a distance of 2.7, it is closer than any earlier model; the next best is 4.8. It gets the repetition, near-repeats, line units and section signal about right, on pages it never saw.
- **It needs very little copying.** About 1 word in 200 is a copy and 1 in 140 is a one-glyph change. That is far below the copy rate of the Timm & Schinner-style generator (5–7%). Most of the structure comes from line-position vocabularies plus occasional drift.
- **What it still misses** (these are the next targets):
  1. **Name rate.** It is 0.37 against the real 0.19: its pages still repeat some rare words too often. The real pages repeat fewer page-specific words.
  2. **Line-position signal.** It is too strong (0.28 against 0.225). The real first and last words are less fixed than drawing them from separate lists makes them.
  3. **Page-specific vocabulary.** It is too low (0.22 against 0.28). Real pages contain more one-off word forms.

  Points 1 and 3 together suggest that the real text invents new word forms on each page, perhaps by a productive word grammar, rather than reusing them.
- **What this does and does not show.** A simple mechanical process reproduces most of the measured structure. That makes a **generated or constructed text** a sufficient explanation for those measures. It does **not** rule out a natural language with the same habits: Uralic and Turkic languages, for example, have rich suffixing and repeated particles. It **does** further weaken a plain cipher of ordinary Latin prose.

## Next
- Replace the fresh draws with a word grammar that builds words from prefix, root and suffix slots, so new forms appear on each page.
- Soften the line-position draws.
- Score both changes on the same held-out pages.
