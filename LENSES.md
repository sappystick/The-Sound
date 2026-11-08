# Lenses: ways of viewing the text, with their era sources and the test behind each

Each lens = an ancient way of thinking, the sources it is read from, and the measurement we run on the text.
Cross-reference rates for every lens across all sources: `crossref/crossref.csv` (run `crossref/crossref.py`).

| Lens | Era sources (in `sources/`) | Test on the text |
|---|---|---|
| Sound and breath | Koine phonology; Psalms; chant traditions | syllables, vowel colour, breath groups (engine; directions.py) |
| Centre and ring (chiasm, inclusio) | Hebrew poetry; Greek ring composition | centre exactness r, ring error E, shuffles (john_book, centre_catalogue) |
| Number (isopsephy, gematria) | Hebrew and Greek letter values; Philo on numbers; Irenaeus on number speculation | verse scans with chance rates (river_key, john_pointers) |
| Geometry and measure | Euclid; Plato, Timaeus; Archimedes (265/153 ≈ √3) | ratio tests against random cuts (directions step 4, theme_shapes) |
| Harmony and music | Plato, Timaeus; Homeric Hymns; psalm titles | breath regularity; staircase; hymn comparison |
| Word / ratio (Logos) | Philo; Hermetica (Poimandres); Heraclitus; Euclid's "logos" = ratio | vocabulary lean (alexandria_test); proportion test |
| Light | Genesis 1; Wisdom 7, 18; Hermetica "light and life" | light family on the shape map; theme blocks |
| Water | Genesis 2; Ezekiel 47; Zechariah 14; Mishnah Sukkah | living-water centres; river thread |
| Spirit / breath | Genesis 2:7; Ezekiel 37; Hippocrates and Aristotle on pneuma | breath letters; emphysao thread |
| Temple and priest (architecture) | Exodus 25–28; Josephus, Antiquities 3; Vitruvius (Latin) | high-priest thread; room acoustics (room_modes) |
| Stones and materials | Exodus 28; Ezekiel 28; Revelation 21; Pliny, Natural History 37 (Latin) | stone-list overlap (high_priest) |
| Medicine and purity | Leviticus 14; Numbers 19; Hippocrates | blood, water and hyssop (directions step 5) |
| Heavens and time | festival calendar; Philo's zodiac; star risings | star_risings; Passover dates (john_history) |
| Art, poetry and writing style | Homeric Hymns; Psalms; Greek prose (Josephus, Philo) | style classes (directions step 2); authorship Delta |
| Egypt and Alexandria | Philo; Wisdom; Corpus Hermeticum; Greek Magical Papyri | vocabulary lean; spell-likeness |

## Cross-reference highlights (rate per 10,000 words; crossref.csv)
- **Light:** John 16.8, the highest with Irenaeus (16.0), against the Synoptics' 8.8 and the Hermetica's 14.9.
- **Life:** John 31.1, second only to the Hermetica (63.0); Synoptics 6.3.
- **Water:** John 22.0, against Plato's Timaeus 34.1 and the Hermetica 19.9.
- **Breath / spirit and number:** low in John, high in the Hermetica, Philo and Irenaeus. John's "spirit" is narrative, not speculative.
