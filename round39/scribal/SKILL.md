---
name: scribal-marks
description: Read the copyists' own marks in CNTR papyrus and codex transcriptions (nomina sacra, staurograms, corrections, line breaks) as data. Uses referent labels from SBLGNT, Fisher tests, circular-shift nulls and layout controls. Use when testing whether scribes encoded theology, sound or structure visually.
---

# Scribal marks

## Data
- `sources/texts/cntr/"class 1"/<MS>.txt`, in the MES.g4 markup.
- `sources/texts/sblgnt` (MorphGNT).
- `sources/texts/sblgnt-logos`, for paragraphs; fetch it with `fetch.sh`.

## Parse
| Mark | Meaning |
|---|---|
| `=` | nomen sacrum (sacred-name abbreviation) |
| U+2CE8 | staurogram |
| U+00AF | overline stroke |
| `/` `\|` `\` | line, column and page breaks |
| `~` | supplied text |
| `^` | missing text |

A correction group is `x{original} {corrected} [a{..}]`. The a/b edit repeats the corrected text and names the hand. Count one event per group.

## Procedure
1. **Nomina sacra:**
   - Decode the abbreviated forms by their first letters.
   - Align them to SBLGNT lemmas verse by verse.
   - Label each referent divine (D) or human/other (H) by rule (a plural counts as H), plus a fixed verse list.
   - Always run a singular-only check: grammatical number confounds the referent.
2. **Corrections:**
   - Count corrections per letter that survives.
   - The main null is a circular shift of the "loaded verse" mask along the verse sequence; a multinomial null is secondary.
   - Classify each substitution by the engine's sound keys (late Koine against Attic) and compare it with the C11 variants.
3. **Breaks:** a short line marks a scribal sense break. It must be under 0.6 × the local median length, complete, and end between words. The positive control is the SBLGNT paragraphing.
4. **Controls:**
   - the ν-stroke and καί shorthand at line ends (checks that the layout is faithful);
   - power on synthetic data;
   - shuffled labels;
   - Benjamini–Hochberg across all tests.

## Pitfalls
- CNTR records no punctuation, spaces or paragraph signs.
- P66, P75 and 03 fill every line, so the short-line method is blind there.
- The pericope of the adulteress is absent from SBLGNT.
- Exclude damaged (lacuna) and supplied words.
- The engine imports SciPy, so stub it.

## Run
```bash
python3 round39/scribal/scribal.py "sources/texts/cntr/class 1" sources/texts/sblgnt sources/texts/sblgnt-logos/data/sblgnt/xml code/engine out.json
```
