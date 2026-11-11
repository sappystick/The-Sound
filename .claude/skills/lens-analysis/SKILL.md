---
name: lens-analysis
description: The-Sound's method for reading an ancient text through one lens (sound, number, cipher, scribal marks, translation layer, calendar...) and deciding whether a pattern is real. Use whenever running a new lens, bringing in a new source, or reviewing a claimed hidden pattern in scripture, papyri, scrolls or related texts.
---

# Lens analysis: find hidden patterns without fooling yourself

Every lens in this project follows the same five steps. A pattern only counts when it survives all five.

## 1. Source first
- Use primary texts in the original language, from an open digital edition. Record the URL, licence and
  commit or download date. Texts go under `sources/texts/<name>/` (not committed); add the fetch command
  to `sources/fetch_sources.sh`.
- Prefer the earliest witness (papyrus > codex > edition). Note what the edition adds (punctuation, verse
  numbers, vowel points) because those are modern.
- Copyrighted material: keep counts and short quotations only.

## 2. State the test before running it
- Write the hypothesis, the measure and the decision rule in the script docstring before looking at results.
- Name the null model: shuffled words, shuffled verses, random positions, random words of the same length
  and letter frequencies, or a comparison text of the same genre.

## 3. Positive control
- Show the method finds a pattern that is known to be there (Psalm 119's acrostic, Jeremiah's atbash
  Sheshach = Babel, 2 Samuel 22 = Psalm 18, Matthew~Mark parallels). A method that misses the control
  cannot report a negative.

## 4. Chance and multiple testing
- Report p from the null (fixed seed, `numpy.random.default_rng(n)`), with the number of tests run.
- Correct across all tests in the round (Benjamini–Hochberg q = 0.05). Report both raw and corrected.
- Gematria / isopsephy: always report how many equal sums are expected among the terms compared.

## 5. Label every result
- **V** verified by our test (survives the null and correction) · **K** known in scholarship (cite who)
  · **N** tested and negative · **O** open · **Reading** an interpretation, not a measurement.
- A negative result is a finding. Write it down with the same care.

## Output contract for a lens
- `round39/<lens>/<lens>.py` (one runnable script, fixed seeds, paths as arguments)
- `round39/<lens>/results.json` (every number in the write-up comes from here)
- `round39/<lens>/FINDINGS.md` (plain language: sources added, tests, controls, results with labels,
  what is new, what is known, what failed, next steps)
- Python 3 standard library + NumPy only (no SciPy).
