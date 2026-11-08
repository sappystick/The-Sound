# the-sound

A research model that reads the Gospel of John, and the scriptures it points to, as spoken sound, structure and
symbol. Every claim is tested against chance before it counts.

- `EVIDENCE_TREE.md`: every discovery with its status (verified, known, negative, open) and the script behind it
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
