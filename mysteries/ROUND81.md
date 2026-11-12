# Round 81: a word-grammar generator, on held-out Voynich pages (`voynich/heldout.py` → `heldout_results.json`)

Round 80's short-range generator (B3t) came closest to the real pages, but it made too few one-off word forms. This round's generator (B4) keeps B3t's copying and one-glyph drift. The change is in the fresh words: a share g of them is **built from slots**, prefix + root + suffix, all learned from the even pages.
- **Prefixes:** the 12 commonest word starts, learned as o, c, q, qo, ch, s, d, sh, da, ok, ot, a.
- **Suffixes:** the 16 commonest word endings, learned as y, dy, n, in, l, r, iin, edy, ey, ol, hy, ar, or, eey, al, ain.
- **Root:** whatever is left.

These are the slots long described for Voynich words. Here they come out of the data without being supplied.

Prefix and root are drawn by section; the suffix is drawn according to the root's last glyph. The grammar share and a softening of the line-position draws were tuned on the even pages: g = 0.2, with no softening chosen. Both generators were then each run **8 times** on the odd pages with different seeds, because a single run varies: B3t scored 2.70 in round 80 and 2.02 in this round's first run.

| Mean of 8 runs | name rate | rep. ratio | near-repeats | line MI | page-specific | section signal | **distance** |
|---|---|---|---|---|---|---|---|
| **Real odd pages** | 0.19 | 2.44 | 1.86 | 0.225 | 0.281 | 0.37 | 0 |
| B3t short-range (round 80) | 0.35 | 2.90 | 2.07 | 0.272 | 0.212 | 0.36 | **2.53 ± 0.35** |
| **B4 word grammar** | 0.33 | 3.14 | 2.21 | 0.202 | **0.281** | 0.30 | **2.59 ± 0.41** |

## Findings
- **The word grammar fixes the measure it was built for.** One-off word forms per page now match exactly: 0.281 against 0.281, where round 80 gave 0.212. The line-position signal also moves closer, from 0.272 to 0.202 against the real 0.225.
- **The overall fit does not improve: it is a tie** (2.59 ± 0.41 against 2.53 ± 0.35). The gains are paid for elsewhere:
  - The built words are shared by every section, so **the vocabulary follows the sections less**: section signal 0.30 against 0.37.
  - Repetition rises slightly.
- **Repeated rare words per page are still too many** (0.33 against 0.19) in both models. This is now the clearest thing no generator reproduces. Real pages coin new forms but almost never use the same rare form twice. Something deliberately avoids reuse, or the page's own words vary more than one-glyph drift allows.
- **What it shows, stated carefully:**
  - A text built from a learnable word grammar, with occasional copying and line-position habits, matches the measured Voynich structure on unseen pages about as well as anything tested. The measures fitted were line units, repetition, drift, page vocabulary and section topics.
  - This keeps a **constructed or generated text** sufficient as an explanation.
  - It does not exclude a natural language with fixed affixes. The slot grammar found here would also describe an agglutinative language.

## Next
- **Section-specific roots with shared affixes:** test whether this recovers the section signal while keeping the one-off forms.
- **A "no reuse" rule for rare forms within a page:** test whether this closes the name-rate gap.
