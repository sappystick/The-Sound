# Round 93: what can be said about what it says; coherence at every level, reading direction, page order, pointers

Pre-registered in `voynich/PREREG_93.md`, committed before the script. Script `voynich/coherence.py`, results in `coherence_results.json`. Controls through the same pipeline: Greek John, English John and Latin Macer, cut into pages of the Voynich's median size.

## What is it talking about? (the honest limit)
**No one can give its content word for word, and we cannot either.** No word has ever been tied to a meaning by evidence that survives a control. What the measurements do allow is a description of **what kind of text it is** at each level, and of **which words belong to which subject**. The most section-specific words (topic-weighted frequency):

| Section (from the pictures) | Its characteristic words |
|---|---|
| Herbal | daiin, chol, chor, cthy, chy, sho, shol |
| Balneological (bathing figures) | shedy, qokain, qokedy, qol, qokeedy, chedy, qokal |
| Stars / recipes | al, aiin, ar, qokeey, okeey, otaiin, oteey |
| Pharmaceutical (jars) | okeol, qokeol, cheol, qokeody, qokol, cheor |

These are the words that carry each section's subject: the plant-page vocabulary, the bath-page vocabulary and so on. What they *denote* is unknown.

## C. Is it coherent? Level by level
| Level | Result | Language controls | Verdict |
|---|---|---|---|
| **Whole body** | Consecutive pages share more vocabulary than random pages of the same section (0.363 against 0.288, p 0.002) | | **Coherent: the text runs on from page to page** |
| **Page** | A page's two halves are closer to each other than to halves of other pages (0.776 against 0.838, p 0.005) | Greek John 0.715 against 0.789; English 0.655 against 0.741; Latin 0.894 against 0.914 | **Coherent, in the same way and to the same degree as real texts** |
| **Line** | Words in one line share roots no more than words in neighbouring lines (5.63% against 5.62%, z 0.3) | | **Not internally bound.** A line is a layout unit (round 75, round 92 alternation), not a sentence whose words belong together |
| **Word** | Held-out glyph cost 2.12 bits, against 7.92 for the same glyphs shuffled | | **Highly structured words** (the slot grammar) |
| Word pairs (round 92) | The previous word does not help predict the next | +0.2 to +1.0 in every language | **No sentence syntax** |

**In plain terms:** each page is about something, consistently, and neighbouring pages continue it. But within a line, words do not hang together as a sentence does. The coherence lives in **which words a page uses**, not in how they are strung together.

## D. Can it be read in other directions?
| Test | Voynich | Languages |
|---|---|---|
| **D1, glyph order:** held-out bits per glyph, backward minus forward | **−0.0003** (no preference) | Greek +0.003, English +0.003, Latin +0.006 (all prefer forward) |
| **D2, word order:** gain from the neighbouring word, forward and backward | −0.415 and −0.417 (none either way) | about +0.24 to +1.07, both ways |
| **D3, vertical:** identical words directly above each other | 1.00% against 0.83% (p 0.007); one-glyph variants 1.52% against 1.28% (p 0.003) | |

- **No direction is privileged.** Every language control is slightly easier forward. The Voynich is equally predictable left-to-right and right-to-left, at the glyph level and at the word level. That fits a system built from symmetric slot rules more than a language written in time order. The effect sizes are small throughout.
- **Reading downward picks up a little structure.** A word repeats, or nearly repeats, the word directly above it about 20% more often than chance. This is consistent with the copying of rounds 78–81 reaching across a line break (copying from the line above). It is a weak copying habit, not a hidden vertical message.

## O. Page order
- **The two sides of one leaf are much more alike** than random pages (0.409 against 0.288, p 0.002).
- **Leaves on the same sheet (bifolium) look more alike** than other leaves of the quire (0.529 against 0.44–0.46, p 0.006). This passes the pre-registered test, but an exploratory check explains it away:
  - Scribes changed by bifolium (Davis 2020), so we compared only pairs written by the same hand, in the same language and section.
  - Conjugate leaves are then **no** more alike (0.536 against 0.535, p 0.47).
  - **The sheet effect is the scribe, not a hidden reading order.**

## P. Do the pictures point somewhere else?
- **P1, offset:**
  - Text-to-picture agreement peaks at the page's own picture: 0.441 at k = 0, and 0.443 at k = −1, which is not significantly different (p 0.50).
  - It falls away symmetrically at larger offsets.
  - **The text is not displaced relative to the pictures.** It does not point to the picture a few pages away, in either direction.
- **P2, misfits:**
  - The section classifier reaches only 44%, mostly confusing herbal-A with pharmaceutical-A (same language).
  - Misfit pages sit slightly more often at quire boundaries (23 against 18, p 0.039, below the pre-registered bar).
  - **Not interpretable as pointers.**

**Combined with rounds 84–87,** where labels, positions and plant shapes carried no pointer, every way of testing whether the pictures point elsewhere has now come back empty. The text goes with its **own** page's kind of picture, coarsely, and with nothing finer, nearer or farther away.

## The answer to "what is it", as far as evidence goes
- **A coherent body:** pages hold their subject, and neighbouring pages continue it.
- **Organised by subject vocabulary:** each section has its own characteristic words.
- **Not written in sentences:** no word-to-word syntax, no within-line cohesion, no reading direction.
- **Built from a word-making system:** a symmetric slot grammar, copying (including from the line above) and line-layout rules (alternation, line-initial and line-final positions).
- **Not a pointer system:** no displacement to other pages, no hidden reading order in the sheets.

This is the profile of a **topic-organised, constructed writing system that writes from subject word pools**, not of a language narrating or describing. If it carries meaning, the meaning is in **which words** a page uses: lists, names, categories, perhaps entries. It is not in sentences.

## Next
- **Test the list reading directly:** inside a page, are words arranged like entries in a list (items followed by attributes, with recurring line or paragraph formats)? Or like a table, with column-wise regularities by word position across lines?
