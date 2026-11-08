# The John sound model

`john_model_config.json` holds every configurable choice, each with its evidence:
- **text:** critical text or P66, P75, Sinaiticus, Vaticanus; nomina sacra; John 7:53–8:11
- **pronunciation:** Attic, Koine (1st–2nd c.) or late Koine; pitch or stress accent; sound-alike map
- **voice:** lector pitch, range, reciting tone, formants
- **tempo:** syllables per second, pause lengths, how breath groups are formed
- **dynamics:** loudness from the noise share, the stress boost
- **space:** synagogue, house church, courtyard, Ephesus theatre, temple court, holy of holies, the Jordan, each with its reverberation (RT60)
- **performance:** "amen" responses, reading sessions or the festival sequence
- **markers:** every verified discovery, attached to its syllables

`python3 model/build_john_model.py <sblgnt dir>` writes `model/out/`:
- `john_score.jsonl.gz`: one record per syllable (31,243): phonemes, stress, F1/F2, duration, onset time, pitch, loudness, noise, room, theme block, markers
- `john_verses.csv`: one row per verse
- `john_summary.json`: running time, breaths per minute, chapter timings, marker positions

Default build (Koine, public-reading pace of 3 syllables a second, male lector at 110 Hz, synagogue with RT60 1.4 s): **227 minutes**, 2,310 breath groups, 10.2 breaths a minute. The bread chapter (6) is the longest single reading (17.9 minutes).
Change any value in the config and rebuild. The engine (`code/engine/engine.py`) can render the score to audio when wanted.
