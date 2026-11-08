# Discoveries: consolidated list (round 7)

## A. Verified (survive their controls and correction)
1. The prologue's spoken centre holds in every manuscript tested (P66, P75, Sinaiticus, Vaticanus, 4 editions).
2. John's "I am" ring (p = 0.009–0.03, robust across manuscripts).
3. "Living water" at the exact centre of Leviticus (14:47–53 by every count) and of the Song of Songs (4:15 / 5:1); p = 0.0002.
4. Hyssop, blood and water meet only in Leviticus 14 and Numbers 19 (Greek Old Testament) and in John 19 and Hebrews 9 (New Testament). Only John has hyssop at the cross.
5. 17/153 falls in only one fishing verse of the Hebrew Bible (Ezekiel 47:10).
6. Wisdom 18 (the midnight Word and the cosmic robe) and the light family were found blind on the shape map.
7. Genesis' letter-centre (28:9) falls just before Jacob's ladder.
8. The narrator's decoding devices and "not from myself" occur in John only (5 and 13 times, against 0 in the other Gospels).
9. John is farthest from the Greek Magical Papyri of 8 text classes; the prologue breathes like a psalm.
10. 1 John is nearest John in style; Revelation is not.
11. Date cross-check: John 2:20 gives AD 27/28, agreeing with Luke 3:1 (AD 28/29).
12. Chapter-scale resonance recovers John's shared tradition blind: John 1~Mark 1, John 6~Matthew 14, John 19~Matthew 27 and Mark 15, John 12~Mark 11. Same order inside each pair, surviving correction.

## B. Already known, confirmed in the primary texts
153 → Ezekiel 47 (Emerton) · seamless tunic → the high priest (Josephus, Antiquities 3.161) · the robe as the cosmos and the stones as the zodiac (Philo, Josephus) · Wisdom 18 → the Logos · John 20:22 → Genesis 2:7 · Revelation's stones → the breastplate · Zechariah 14 and the Mishnah behind John 7–9 · Sirach 24 behind John · Polycrates' *petalon* · Papias' two Johns · 666 = "Nero Caesar" in Hebrew letters (616 = the variant spelling, matching the variant reading).

## C. Potential (open; needs more data or a targeted test)
- **Inverted links:** John 18 (Jesus before Pilate) ~ Acts 26 (Paul before Agrippa) in reverse order ("all the Jews", "Jesus the Nazarene", "do you say this of yourself"); John 4 ("this mountain", worship) ~ Matthew 17 ("say to this mountain") in reverse. Only 4 links each.
- **Egypt / Hermetica** lean toward John's vocabulary (not significant). Genesis is John's strongest book-level position link (p = 0.010 uncorrected), but John's chapter order does not follow Genesis (rho −0.21).

## D. Negative (tested, not found)
- Book rings and John as a miniature of the Bible's order.
- Centre-quoting, number codes, sevens, Archimedes-type ratios.
- Verse-level mirrors, frames and cycles after correction. Repeating cycles are in narrative, not poetry (narrative 11.2%, poetry 4.7%).
- Atbash beyond its known cases: the scan recovers Sheshach → Babel (Jeremiah 51:41) but finds only noise otherwise (13 hits, against 7 for a random cipher).
- Name acrostics in the Greek New Testament: none (the control finds Lamentations 1 and Psalm 34).

## E. Round 8: the within-verse effect, resolved (code/analysis/micro_verse.py)
- **Explained as language, not design.** Each phrase has a habitual slot: some open sentences, others close them. Cross-book pairs are *no closer* than two random uses of the same phrase (0.303 against 0.286). The same effect appears in Josephus (ratio 0.92) and in the Hebrew Bible (0.88).
- **The one real signal is quotation.** When two verses share more rare words, the phrase sits in almost the same place (ratio 0.89 → 0.41 → 0.28 → 0.08 as shared words rise from 0 to 4+). Copying keeps word order.
- **New Testament writers reshape the Old Testament when they quote it.** NT~OT pairs keep the position least (0.93), against NT~NT (0.78, the Synoptic parallels) and refrains in the same chapter (0.63).
- **A blind quotation detector** built from this finds only known links for John: Isaiah 53:1 (John 12:38); "baptize with water ... Holy Spirit" (Matthew 3:11, Luke 3:16, Acts 11:16); the cock crowing (Matthew 26:74, Mark 14:68); "take up your mat" (Mark 2:9). John shares remarkably little verbatim wording with any other book, which fits the view that John is independent of the Synoptics.

## F. Round 9: the ear's measures (code/analysis/acoustic.py)
New measuring method: John's reconstructed Koine sound, scored on the criteria the ancient critics used (Dionysius of Halicarnassus, *On Composition*). The criteria: hiatus, stress evenness, syllable-weight rhythm (nPVI), cadence, alliteration, and the **noise share** (stops and fricatives, the acoustically noisy sounds, against voiced sonorants and vowels).
- **V John is acoustically "quieter" than every prose class:** noise share 0.326, against the Synoptics 0.344 (p = 8e-13), Psalms 0.344 (p = 3e-10), Josephus 0.347 and Philo 0.346. It matches Homeric verse (0.325). It survives removing the 150 commonest words (content words only: 0.319 against 0.328, p = 0.0002), so it lies in John's chosen vocabulary. John uses fewer s, k and dh sounds and more m, i, u and e. The quietest stretch is the farewell discourse (0.309).
- **V John does not polish away hiatus:** 27 vowel clashes per 100 word junctures, the highest of all classes (Josephus 5, Hebrews 12, Philo 12). That is an open, vowel-rich, unrhetorical sound: written to be voiced, not to impress the schools.
- **N** Stress evenness, weight rhythm and alliteration put John with the Psalms and ordinary prose. Homeric verse is the most periodic (the control passes). The "cadence" difference at sentence ends appears in every corpus (word endings), so it is not design.
- **V** The prologue's centre falls in verse 12 in the Syriac Peshitta, Coptic Sahidic and Latin Vulgate as in Greek (letters). Translation keeps the proportions, so the centre is a property of the content's balance, not of Greek sound alone.
- **N** The "I am" sayings are not quieter than random verse sets (p = 0.28).

## G. Round 10: John's sound map (code/analysis/john_noise_map.py; chart john_noise_map.svg)
- **V The deepest quiet in John is the vine-and-abiding discourse.** The noise share drops from about 0.33 to 0.275 across John 14:30–16:33. The quietest points are 15:1 ("I am the true vine") and 16:19, then 5:37 (the Father's witness). By fifths of the book, John dips only in the fourth fifth (0.314); Matthew, Mark and Luke stay flat.
- **V Sound follows meaning.** The noise curve falls where these themes rise (corrected over 18 themes): Father (r = −0.49), "I am" (−0.31), abide (−0.38), truth (−0.29), witness (−0.27); love is borderline (−0.23). Water, light and bread do not track quiet, and "signs" tend toward noise (+0.27, borderline). The intimate language of indwelling ("in me", "abide", "the Father in me") is John's most voiced, least noisy sound.
- **V Speech is quieter than narrative** (verses with first- or second-person verbs: 0.322 against 0.331, p = 0.0015).
- **N/O** Pivot verses are not quiet: the prologue centre (1:12), "It is finished" (19:30) and "I am the resurrection" (11:25) sit among John's noisiest 5–10%. That may be a contrast pattern (dense consonants at turning points). It needs a fixed list and a test before it counts.
