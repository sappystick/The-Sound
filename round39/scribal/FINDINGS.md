# Round 39 · Scribal lens: the copyists' own marks as data

**Script:** `scribal.py` (standard library + NumPy, seed 39). Every number below comes from `results.json`.

**Rerun** (about 50 s):
```bash
python3 round39/scribal/scribal.py "sources/texts/cntr/class 1" sources/texts/sblgnt sources/texts/sblgnt-logos/data/sblgnt/xml code/engine round39/scribal/results.json
```

Labels: **V** verified · **K** known in scholarship · **N** negative · **O** open · **Reading** an interpretation.

## Headline
**Scribes corrected what changed the sound and left same-sound spellings alone.**

| Manuscript | Corrections that sound the same | Variants that sound the same (C11) | p |
|---|---|---|---|
| P66 | 23 of 237 (9.7%) | 259 of 429 (60%) | 1.5 × 10⁻⁴⁰ |
| Sinaiticus (01) | 1 of 26 | 444 of 839 | 1.6 × 10⁻⁷ |

- **Control:** under Attic pronunciation, only 1% sound the same.
- **Reading:** this is the other half of the project's claim C11. Copyists let sound-alike spellings stand, and corrected the errors that changed what a listener would hear.
- **New:** this comparison is new here (**V**).

## Sources
**Already present:**
- CNTR transcriptions (Bunning, CC BY-SA 4.0, commit `4e743a4`) of P66, P75, P45, P46, 01, 02 and 03.
- MorphGNT SBLGNT, for lemma, number and case.
- The sound engine, `code/engine/engine.py`. Only `parse_greek` is used, with SciPy stubbed out.

**Added:** SBLGNT XML with the editors' paragraphs (`sources/texts/sblgnt-logos`, commit `d7f35ad`, CC BY 4.0); see `fetch.sh`.

**What the markup cannot show:**
- **Recorded:** sacred-name abbreviations (nomina sacra), the overline stroke, staurograms, the καί shorthand, line, column and page breaks, and corrections.
- **Not recorded:** punctuation, high points, diaereses, blank spaces and paragraph signs.

## Test 1. Sacred-name abbreviations as a theological signal
**Method:**
- Each SBLGNT occurrence is labelled divine (D) or human/other (H) by rule and from a fixed verse list. Plurals, pagan gods and a person's own spirit count as H.
- The manuscript words are aligned verse by verse; at least 96% align.
- Each cell gets an exact Fisher test.

**Controls:**
- Power on synthetic data is 0.90.
- Shuffling the labels gives false positives at 0.021.
- A hand check of 40 random labels agrees 40 of 40; one, 2 Cor 3:6, is debatable.

**Contraction rates in John** (contracted / total):

| Word | P66 | P75 | 01 | 02 | 03 |
|---|---|---|---|---|---|
| θεός | 64/66 | | | | |
| κύριος | 37/37 | | | | |
| Ἰησοῦς | 184/184 | | | | |
| πνεῦμα | 18/19 | | | | 1/24 |
| πατήρ | 94/107 | 14/71 | 5/134 | 109/109 | 0/138 |
| υἱός | 32/50 | 8/44 | | | 0/54 |
| ἄνθρωπος | 33/51 | 33/44 | 2/58 | 48/48 | |
| σταυρ- | 7/7 | | | | |
| οὐρανός | 0/13 | | | | |

**Results:**
- **K: the four core names are abbreviated everywhere** (θεός, κύριος, Ἰησοῦς, Χριστός, 97–100%; Traube, Paap, Hurtado). Vaticanus abbreviates only these four: πνεῦμα 13/341 and πατήρ 1/398 across all its books.
- **V, but grammatical:** in Paul the divine/other split for θεός and κύριος comes from plurals being written in full.
  - P46: θεός 352/352 against 2/5; κύριος 164/164 against 0/4 (q < 10⁻⁴).
  - Singular non-divine uses are abbreviated in all four witnesses: "the god of this age" (2 Cor 4:4), the belly as god (Phil 3:19), the heir as κύριος (Gal 4:1).
  - The plural explanation is new here.
- **V, mostly the same plural effect:** υἱός in Paul (P46 16/18 against 2/21). The singular-only check fails (q 0.074).
- **V, a tendency:** P66 abbreviates πατήρ for God 86/92 times, against 8/15 for human fathers (q 0.0018). It still abbreviates "our father Jacob" (4:12) and the devil as father (8:44); singular-only q 0.06.
- **N:** πνεῦμα is not split divine/human in the way Comfort proposed.
- **N:** κύριος for human masters in John is abbreviated 4 of 4 times in P66, 01 and 02.
- **O:** "Son of Man" in P75 (10/10 against 23/34, q 0.14).

## Test 2. Staurograms and line-end shorthand
- **K (Aland, Hurtado):** there are 19 staurograms, every one on a "cross/crucify" word (σταυρός, σταυρόω).
  - P66 has 12, in John 19, and also writes 4 σταυρ- forms out in full.
  - P75 has 3 (in Luke), P45 3, and 01 one (Rev 11:8).
  - P46 abbreviates σταυρ- without the sign; the great codices write it out.
- **V/K, layout check:** the ν-stroke and the καί shorthand sit at line ends 38–51% of the time, against 0.6–2% elsewhere (p < 10⁻⁷⁰). The line breaks in the transcriptions are faithful.

## Test 3. Where the corrections fall
**Set fixed before counting:** the prologue, the "I am" verses, verses with Christological titles, and the passion (chapters 18–19), 162 verses in all.

**Results:**
- **N:**
  - P66's first hand has fewer corrections at these verses (0.77×, p 0.96).
  - Sinaiticus has 1.39× (p 0.15).
  - The test could have detected a doubled rate (power 1.0 / 0.9).
- **V statistically, but mechanical:** Vaticanus's prologue has 8.1× the corrections (p 0.0012, q 0.007). There are only 3, all eye-skip omissions (1:4, 1:13, 1:14), probably caused by the prologue's repeating staircase style.
- **O:** Sinaiticus's prologue has 3.1× (q 0.09), at the known cruxes 1:15 and 1:18.
- **K (Royse):** P66's corrections move toward the SBLGNT wording 252 times and away from it 45 times.
- **V, new:** the sound comparison in the headline. Corrections and variants are different kinds of data, so treat the size of the gap as approximate; its direction is clear.

## Test 4. The scribes' own breaks
- **Failed for the papyri:** P66, P75, 03 and P46 fill every line (5, 0, 1 and 0 short lines), so the C24 check cannot be run on them with these files.
- **V, positive control:** in Sinaiticus, short lines mark SBLGNT paragraph starts at twice the chance rate (John q 0.06; Paul q 0.0004).
- **N:** the C24 cuts are not closer to Sinaiticus's breaks than chance (mean distance 4.3 verses, p 0.29). Alexandrinus (02) gives p 0.41.
- **O:** Sinaiticus breaks exactly at 13:33, the blind cut, not Brown's 13:31. One hit in three has a chance of 0.19.

## Tests and correction
95 tests (54 in Test 1, 28 in Test 3, 13 in Test 4); 16 survive Benjamini–Hochberg at q ≤ 0.05.

## Next
- Hand-code the in-line spaces and high points from images of P66 and P75 at John 1:14–19, 13:29–14:1 and 17:24–18:5.
- Run the correction-sound test on P75 Luke and P46 Paul.
