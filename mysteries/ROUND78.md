# Round 78: the cipher hypothesis tested; the repeated words; labels that point nowhere (`voynich/cipher_tests.py`, `voynich/repeats.py`)

## 1. Can a cipher turn a real herbal into the Voynich herbal?
Each method encrypts Macer Floridus (a real Latin herbal), and the result is measured exactly as the Voynich herbal pages were.

| Process | Name rate | Repetition | Repetition ÷ expected from word frequencies | Line structure (MI) | Words per line |
|---|---|---|---|---|---|
| Plain Latin | 0.42 | 0.00% | **0.05** (grammar avoids "the the") | 0.34 | 6.1 |
| Letter substitution | 0.42 | 0.00% | 0.05 | 0.34 | 6.1 |
| Homophonic word code (3 or 6 variants) | 0.39–0.40 | 0.00% | 0.00–0.07 | 0.22–0.27 | 6.1 |
| Nulls inserted | 0.40 | 0.00% | 0.01 | 0.29 | 6.8 |
| **Verbose syllable cipher** | **0.04** | 0.34% | 0.40 | 0.14 | **19.0** |
| Topic-resampling generator | 0.90 | 1.04% | 2.79 | **0.01** | 6.1 |
| **Voynich herbal** | **0.11** | **0.84%** | **2.0–2.6** | **0.18** | **6.7** |

**Result:**
- No single classic cipher reproduces the Voynich.
- **Word-level ciphers keep the names. A verbose cipher removes them but explodes line length and erases line structure. A generator gets the repetition but keeps the names and loses the lines.**
- The Voynich's defining combination is three things at once: no plant names, words repeating **2–2.6× more** than their frequencies predict, and verse-like lines of about 7 words.
- To be viable, a cipher hypothesis must explain all three. A **verbose cipher operating inside short line units**, or a **slot-based generator with line positions**, are the two classes left. Both were proposed before (verbose ciphers; Rugg's table-and-grille, 2004); these numbers are now the test any version must pass.

## 2. The repeated words, one by one
| Question | Result |
|---|---|
| How many, and which? | 283 back-to-back repeats (0.84% of 33,641 words), **2.6× what word frequencies predict**. The commonest: daiin ×20, chol ×19, qokeedy ×19, qokeey ×12, qokedy ×11, chedy ×10. **Half are top-20 words.** |
| By section | Herbal 2.0×, stars/recipes 2.1×, cosmological 1.6×, pharmaceutical 1.55×, biological 1.3×, **astronomical 0.66× (the only section below chance)** |
| Do they cross line breaks? | Almost never: 275 inside a line, 8 across a break. They belong to the line unit. |
| **Hidden spacing?** | **No.** The gaps between repeats are as irregular as random positions (p = 0.18). |
| **Numbers in their lengths?** | **No periodicity** (p = 0.23). Neighbouring repeats have similar lengths (p = 0.002), explained by each section's favourite words (qokeedy-type words cluster in the biological section). |
| Near-repeats (one letter apart, e.g. *daiin dain*) | 456 against 247 if shuffled (**1.85×**): the text drifts by small changes from word to word |

**Reading.** The repeats are not a hidden counter or pointer. They are common words recurring, plus near-copies with one letter changed. That is the signature of a process that **builds each word by modifying the previous one** (a known Voynich property, here quantified with controls). It fits the slot-generator or verbose-cipher classes above, and not a natural language.

## 3. Labels that point elsewhere or nowhere
| | Result |
|---|---|
| Labels in the whole manuscript | 1,017; **952 are not in their own page's text** |
| Do labels cross-reference other sections (e.g. jar → herbal page)? | **No strong pattern.** Where labels do appear elsewhere, it is in proportion to how much text each section has (ratios 0.8–1.4). |
| **Labels found nowhere in the text** | **423 (42%)**: zodiac 144, pharmaceutical 124, astronomical 69, biological 37 |
| What marks a label | Half start with **o** (52%, against 21% of text words); **ot-/ok-** 28–37% against 11%. Orphan labels are longer (6.45 against 5.18 letters). **Labels are a separate naming vocabulary.** |

**The ones that point to something else.** Singled out:
- **f57v, the ring of single glyphs.** A **17-glyph sequence written four times** (o l d r v x k k f ? t r ? ? y c ?), with **90% agreement at period 17** (shuffled 99th percentile: 29%). Single glyphs vary between copies (k→m, f→p), like counters. **Four quadrants of 17 suggests a rotating dial (volvelle) or a table key.**
- **f49v, a letter at the start of each text line** (f o r y e ? k s p o ? y e ? ? p o ? y e ? d y s k y). It is not periodic (0.17 against 0.15 chance). It behaves like **a line index or enumeration**: a key pointing to lines.
- **f66r, a column of words ending in single glyphs** (… raral, y, o, s, sh, y, d): another list or key.

## Next investigations for the Voynich
1. **Test the two surviving classes** with a fixed-rule test. Build the simplest verbose cipher within line units, and the simplest slot generator, each fitted on half the manuscript. Score both on the held-out half against all the round 75–78 numbers.
2. **The keys.**
   - Do the f49v line letters predict anything about their lines (first glyph, length, word classes)?
   - Do the f57v ring's 17 glyphs occur in a fixed order anywhere else?
   - If the ring is a dial, does its order match how frequent those glyphs are in the text, as a cipher alphabet's order might?
3. **Zodiac labels** (144 orphans). Each of the 12 zodiac pages has about 30 labelled figures (days of the month?). Test whether label order runs systematically around each circle, e.g. shared prefixes in order, as day-names or numbers would.
