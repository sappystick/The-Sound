# the-sound

A research model that reads the Gospel of John, and the scriptures it points to, as spoken sound, structure and
symbol. Every claim is tested against chance before it counts.

- `SYNTHESIS.md`: what has been established, graded by evidence; publishable papers; threads to close
- `EVIDENCE_TREE.md`: every discovery with its status (verified, known, negative, open) and the script behind it
- `lang4d/`: rounds 65-66, KANON - a spoken, typed, played and drawn programming language (white paper, v0.2 review, Python + JavaScript interpreters, checksummed audio codec, the Canon library, seals, the one-night course and its page in `lang4d/app/`)
- `POWER_MANUAL.md`: round 64, thought experiment: the Day of Atonement as the pyramid's operating manual; chamber acoustics, Helmholtz breathing, voice through the shafts
- `POWER_EGYPT.md`: round 63, cube / twelve / centre across the corpora; Egyptian parallels; the matrix with its purpose reversed
- `POWER_CODE.md`: round 62, decoding tests on the building instructions (elements, constants, pi, capacitor, magnetism, geometry, geography)
- `POWER_PYRAMID.md`: round 60, the Great Pyramid (Petrie 1883) against the biblical measurements, with chance baselines (negative; shared cubit system)
- `POWER_PLANETS.md`: round 59, the last construction pieces; the speaking planet organ (Nicomachus and Pliny tunings) with a vowel-recognition test
- `POWER_TABERNACLE.md`: round 56, thought experiment: the tabernacle and temple as one instrument; every part mapped and calculated; schematic and render
- `POWER_PERFORMANCE.md`: round 55, pre-registered performance timing (fails); sacred dimensions as resonator ratios; non-lexical passage detector
- `POWER_CENTRE.md`: round 52, pre-registered: 10:11 at the centre of John 1:1-20:31 in Sinaiticus and Vaticanus (passes)
- `POWER_MEASURES.md`: round 51, performed time, breath groups, story time, the 20:31 ending, mapping-free tests, the band layers
- `POWER_RERUN.md`: round 50, pre-registered reruns (R2 replicates in Revelation), Psalm 24 with Second Temple vowels, other units of measure, the seven-with-a-middle mold (Philo, Josephus, Revelation)
- `POWER_SOURCES.md`: round 47, Palestinian Aramaic of the period (Qumran, targum, Galilean Talmud) vs the Gospel Aramaic words; ancient ways of writing sound; Jericho and magrepha physics
- `POWER_LANGUAGE.md`: round 46, the four predictions by letters and accent; composition language (Greek vs Syriac, with controls)
- `POWER_AXIOM.md`: round 45, John taken as the score of a lost instrument; the whole book mapped, the axiom tested
- `POWER_MESE.md`: round 44, hymn papyri tests, "I am" on the middle string, the instrument, the technical second reading
- `POWER_SCORE.md`: round 43, the papyrus as a score (P.Oxy. 1786, Clement on the human instrument, the wind-played lyre, syllabic line division)
- `POWER_MACHINES.md`: round 42, a buildable speaking machine, ancient sound machines (Heron), texts as sound scores, "many waters"
- `POWER_SIM.md`: round 41, power-word simulator (mouths, pitches, rooms, languages), words decoded into ancient notes, a lyre and vowel pipes to play them
- `POWER_SOUNDS.md`: round 40, the original words of power as calculated sound in their spaces (renders in `power/audio/r40_*`)
- `round39/`: multi-lens team (Coptic, scribal marks, Sefer Yetzirah and calendar; partial Targum, ciphers, Syriac)
- `TIMELINE.md`: the historical Johns (the Baptist, the son of Zebedee, the beloved disciple, the Elder) as a timeline tree
- `LENSES.md`: the era lenses (sound, number, geometry, music, light, water, spirit, temple, stones, medicine, heavens, style, Egypt)
- `crossref/`: the lens cross-reference across all sources
- `sources/fetch_sources.sh`: downloads every open source text (Greek NT and OT, Hebrew Bible, papyri, Philo, Hermetica, Eusebius, Irenaeus, Josephus, Homeric Hymns, Plato, Euclid, Hippocrates, Vitruvius, Pliny, Mishnah)
- `code/engine`: the sound engine (Koine and Hebrew phonology)
- `code/analysis`: all tests and their `*_results.json`
- `code/lineage`: instruction records and the Mishnah ingest

## Method (9 steps)
1. Earliest manuscripts, read as unspaced text.
2. Spoken time from Koine syllables.
3. Centre exactness.
4. Ring error.
5. Seams.
6. Theme blocks.
7. Author's markers.
8. Pointers, kept only if p ≤ 0.01.
9. Calibration: shuffled-text nulls, known positive controls, correction for multiple tests, blind reruns.

## Run
```bash
bash sources/fetch_sources.sh      # texts land in sources/texts
python3 crossref/crossref.py sources/texts
python3 code/analysis/directions.py sources/texts/sblgnt sources/texts/lxx-swete/data sources/texts/morphhb/wlc sources/texts
```
The audio renders and the earlier history are in the `sound-of-the-word` project.
