# Evidence tree

Status: **V** verified by our tests · **K** already known in scholarship (confirmed in the primary text) · **N** tested and negative · **O** open.
Code for each result is in `code/analysis/` (the script is named in brackets).

## Root: the text as sound
- **V** John's prologue has a spoken-syllable centre that holds in P66, P75, Sinaiticus, Vaticanus and four editions [earliest_text, papyri, harden_john]
- **V** John's "I am" sayings form a ring around the Gospel's centre (p = 0.009–0.03) [john_book]
- **V** The prologue breathes like a psalm: breath groups of 12.5 syllables, regular, about 8 breaths a minute at chant pace [directions]
- **V** John is farthest from the Greek Magical Papyri of 8 text classes, and nearest the Synoptics and Psalms [directions, pgm_extract]
- **N** No number codes (sevens, isopsephy), no Archimedes-type ratios, no rings across chapters [bible_map, theme_shapes, book_rings]

## Branch: centres
- **V** "Living water" is the exact centre of Leviticus (14:47–53 by every count) and of the Song of Songs (4:15 / 5:1); p = 0.0002 [centre_catalogue, directions]
- **V** Genesis' letter-centre (28:9) falls just before Jacob's ladder (28:10), which John 1:51 points to [book_centres_hebrew]
- **N** Book centres are not special in general; writers do not quote from centres (blind test) [centre_catalogue, quote_centres]

## Branch: the river (water)
- **K/V** 153 fish → Ezekiel 47:10 (Emerton 1958). New: the 17/153 pair is in only one fishing verse of the Hebrew Bible [river_key]
- **K** Living water at Tabernacles: Zechariah 14:7–8; Mishnah Sukkah 4:9 and 5:3 (water from Siloam, lamps) → John 7–9 [river_key]
- **K** Sirach 24 (Wisdom tabernacles, "will thirst again", rivers into the garden) → John 1:14, 6:35 [river_key, john_pointers]
- Thread: Gen 2:10 → Sir 24 → Ezek 47 → Zech 14:8 → John 7:38; 19:34 → Rev 22:1

## Branch: purification (blood, water, hyssop)
- **V** Hyssop, blood and water meet only in Leviticus 14 and Numbers 19 (Greek Old Testament), and in John 19 and Hebrews 9 (New Testament). Only John has hyssop at the cross [directions]
- **V** Hebrews' centre verse is 9:7 (the high priest, "not without blood") [centre_catalogue]

## Branch: the high priest
- **K** Seamless tunic (John 19:23) = the high priest's robe "not of two pieces" (Josephus, Antiquities 3.161) [high_priest]
- **K** The robe as the cosmos; the 12 stones as the zodiac (Philo, Moses 2.124; Special Laws 1.87; Josephus, Antiquities 3.186) [high_priest]
- **V** Wisdom 18 joins the midnight Word (18:15) and the cosmic robe (18:24); found blind on the shape map [bible_map, high_priest]
- **K** Revelation 21 shares 8 of 12 stones with the breastplate; Ezekiel 28:13 (Greek) puts 9 of them in Eden [high_priest]
- **K** Polycrates: John "became a priest wearing the *petalon*" (Eusebius 3.31.3) [john_history]

## Branch: John's method
- **V** Narrator decoding ("he said this, signifying…") appears 5 times in John and 0 in Matthew, Mark and Luke; "not from myself" 13 times against 0 [john_key, river_key]
- **K** Genesis overlay: "In the beginning", the opening week, the garden, "breathed on them" (= Genesis 2:7) [john_key]
- **V** Theme blocks: water → light → bread and life → hour and glory → abide → love [theme_shapes]
- **N** John is not a miniature of the Bible's order [john_miniature, order_tests]

## Branch: history (see TIMELINE.md)
- **K** Josephus on the Baptist (Antiquities 18.116–119; Machaerus); Papias' "John the Elder" and two tombs at Ephesus (Eusebius 3.39) [john_history]
- **V** Date cross-check: John 2:20 → AD 27/28 agrees with Luke 3:1 → AD 28/29 [john_history]
- **V** Style: 1 John is nearest John; Revelation is not (cf. Dionysius of Alexandria) [john_history]
- **O** Egypt / Alexandria: the Hermetica lean toward John's vocabulary, but not significantly [alexandria_test]

## Branch: verse-level symmetry (code/analysis/verse_symmetry.py)
- **N** No chapter in the New Testament (260) or the Hebrew Bible (895, unpointed consonants) shows mirrored verse lengths, mirrored wording or a first-last frame after correction for many tests.
- **O** There are more repeating cycles in Hebrew verse lengths than chance would give (84 chapters against 45 expected), probably poetic parallelism. A follow-up test should run on poetry only.
- **V** (method) Whole-chapter shape twins: the strongest twin is 2 Samuel 22 with Psalm 18, which are the same poem, so the method works. But with about 580,000 chapter pairs, most other high twins are expected by chance.
- **V** (method limit) Shuffling the verses of a short chapter cannot confirm even a perfect frame: Psalm 8, whose first and last lines are identical, reaches only p = 0.07. Verse-level rings in short chapters need a different kind of evidence, such as identical wording.
