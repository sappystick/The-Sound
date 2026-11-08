# The Sound of the Word

Research tools and data for reading John's prologue, the early Christian hymns, the Hebrew Bible
and Egyptian ritual texts as **performed** texts: sounded, timed, placed and enacted.

The full write-up lives in the companion document
*The Sound of the Word: John's Prologue and Scripture*:
<https://claude.ai/artifact/F9vdtTrEVzyDUYc3ha2R2H>.

## Contents

| Folder | What it holds |
| --- | --- |
| `lineage/` | **The ritual instruction dataset.** Each record is one written instruction from Egyptian ritual texts, the Hebrew Bible, the Mishnah, early church manuals or living practice. The fields are time, place, direction, repetition, posture, voice, tools, oils, plants, ingestants, materials, elements and practice threads, each with a confidence flag. There is also a table of key ritual words with their broader meanings, and a lineage map of practices passed down across eras. |
| `engine/` | The Ancient Sound Engine: reconstructs and synthesizes Greek and Hebrew words by era (Classical, Koine, late Koine, Second Temple, Tiberian), delivery (speech, declamation, chant, ritual), feeling, chant tradition, instruments and room acoustics, including modal models of the Holy of Holies, the Holy Place and the King's Chamber. |
| `analysis/` | Measurement scripts and results: where the removed books fit, the prologue's sound symmetry, an elemental reading of John, the resonances of sacred rooms, and dawn star risings over Jerusalem in 30 CE. |
| `audio/` | 176 rendered examples (MP3), each with a JSON score: phonemes, accents and melody in Hz and cents. |

## The instruction dataset

```bash
cd lineage && python3 build.py   # writes data/instructions.csv|json, words.csv, lineage.csv, summary.json
```

**Confidence flags:**

- `text`: stated directly in the cited passage.
- `scholarly`: from the standard edition or scholarly description of the source.
- `verify`: a detail to check against an edition before citing.

Instructions are paraphrased by the compiler. No modern translation is reproduced.

**Adding a record:** add a call to `r(...)` in `records.py` with a unique id and a precise reference, then run `build.py`. Keep one instruction per record, and give the reference precisely enough to check it.

## Running the analyses

The analyses need two freely licensed corpora, which are not included here:

```bash
git clone --depth 1 https://github.com/nathans/lxx-swete.git   # Swete's Septuagint, CC BY-SA 4.0
git clone --depth 1 https://github.com/morphgnt/sblgnt.git      # SBL Greek New Testament (MorphGNT)
python3 analysis/removed_books.py lxx-swete/data sblgnt
python3 analysis/sound_symmetry.py sblgnt
python3 analysis/elements_john.py sblgnt lxx-swete/data
python3 analysis/room_modes.py
python3 analysis/star_risings.py
```

## Using the engine

```bash
pip install numpy scipy
python3 engine/engine.py --text "λόγος{awe}" --lang greek --era koine --mode chant --space house_church --out logos.wav
python3 engine/engine.py --text "קָדוֹשׁ קָדוֹשׁ קָדוֹשׁ" --lang hebrew --mode chant --space holy_of_holies --out qadosh.wav
```

## Ground rules

Every pattern claim is tested against chance, using shuffled texts, other centers and baselines, with the rules fixed before looking at the results. Results "found after looking" are labeled as leads. The write-up separates what holds, what is suggestive, and what was ruled out.
