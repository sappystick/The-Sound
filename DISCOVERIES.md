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
- **CORRECTED in round 11: mostly mechanical.** Sound follows meaning? The noise curve falls where these themes rise (corrected over 18 themes): Father (r = −0.49), "I am" (−0.31), abide (−0.38), truth (−0.29), witness (−0.27); love is borderline (−0.23). Water, light and bread do not track quiet, and "signs" tend toward noise (+0.27, borderline). The intimate language of indwelling ("in me", "abide", "the Father in me") is John's most voiced, least noisy sound.
- **CORRECTED in round 11:** speech is quieter than narrative (0.322 against 0.331), but the gap vanishes when personal pronouns are removed.
- **N/O** Pivot verses are not quiet: the prologue centre (1:12), "It is finished" (19:30) and "I am the resurrection" (11:25) sit among John's noisiest 5–10%. That may be a contrast pattern (dense consonants at turning points). It needs a fixed list and a test before it counts.

## H. Round 11: turning points, other texts, and the open leads (code/analysis/round11.py)
- **N The noisy-turning-points idea fails.** On fixed lists, John's "Amen, amen" verses and "the hour" announcements are *quieter* than average, not noisier. The blind seams are average. The quiet is the speech formula "I say to you".
- **CORRECTION, pronouns:** John's quiet speech and the Father/abide link to quiet largely disappear when personal pronouns are removed (speech gap +0.0003; Father r −0.49 → −0.16, p = 0.10). Words like "me", "my", "in me", "you" are full of m and vowels. The quiet valley of John 14–16 is real to the ear, but it comes from the density of "I / you / in me" language, not from a separate choice of sounds. The Greek Psalms show the same pronoun effect (r −0.17 → −0.03). Matthew, Mark and Luke show no speech-quiet effect at all. John's overall quietness (round 9) still stands, since it survived removing the 150 commonest words.
- **N Reversed links are not special.** The test flags 13.8% of NT chapter pairs as reversed but also 32% as forward. Its p-values are too generous for small link counts, so John 18~Acts 26 is not notable.
- **K/V Dead Sea Scrolls:** "sons of light" occurs 20 times in the Scrolls (5 in the Community Rule) and **0** times in the Hebrew Bible; in the NT it is in John 12:36, Luke 16:8 and 1 Thessalonians 5:5. "Spirit of truth" occurs 7 times in the Scrolls and 0 in the Hebrew Bible; in the NT only in John (14:17, 15:26, 16:13) and 1 John 4:6. John and the Community Rule both emphasize light, truth, knowledge, judgement and love, but their overall emphasis profiles do not correlate significantly (rho +0.19, p = 0.29). The link lies in specific phrases, not in a whole worldview.
- **Echoes of John:** the general phrase-lean measure failed its control (Philo, who wrote before John, scored highest), so it was dropped. On a fixed list of John's signature phrases:
  - **Clement of Alexandria** (c. 200) has many: living water, bread of life, light of the world, lamb of God, only-begotten son, true vine.
  - **Ignatius** (c. 110) has two strong ones: "bread of God" and "knows whence it comes and where it goes" (John 3:8).
  - **Polycarp and Hermas** have none. Philo has none (the control passes).

## I. Round 12: Scroll idioms widened; separation → one → completion; the "I" line (code/analysis/round12.py)
- **V A cluster of Scroll-Johannine idioms.** These occur in the Dead Sea Scrolls and in John or 1–3 John, but not (or once at most) in the Hebrew Bible, the Septuagint or the rest of the NT:
  - "sons of light" (Scrolls 20; Hebrew Bible 0)
  - "spirit of truth" (Scrolls 2; John 4×)
  - "spirit of error/deceit" (Scrolls 8; 1 John 4:6)
  - "doing the truth" (Scrolls 5, Hebrew Bible 1; John 3:21, 1 John 1:6)
  - "walking in truth / in darkness" (Scrolls 3, Hebrew Bible 1; Johannine 3, other NT 0)
  - "of the truth / men of truth" (Scrolls 9, Hebrew Bible 1; Johannine only)
  The link is known in scholarship (Charlesworth and others); the counts here quantify it.
- **O Separation → one → completion.**
  - Separation words cluster in the middle: schism at 7:43, 9:16 and 10:19; scatter at 10:12, 11:52 and 16:32.
  - "One" runs from 10:16 ("one flock") and 10:30 ("I and the Father are one") to 17:21–23.
  - Completion culminates in 17:23 ("perfected into one"), 19:28 and 19:30 ("It is finished").
  - Ordered more than chance? p = 0.085, suggestive but not significant.
- **V The "I" line.**
  - John uses emphatic *egō* 3–13 times per 1,000 words, against under 3 in Matthew, Mark and Luke.
  - Jesus' last plain emphatic "I" is 18:37: "*for this I was born* … to bear witness to the truth". After that (19:6 is Pilate) the plain *egō* never returns.
  - The risen Jesus' only emphatic "I" is *kagō* ("and I / so I") in 20:21: "As the Father has sent me, *so I* send you". It is joined to the Father and followed by the breath (20:22).
  - This is a textual observation that fits the "not from myself" thread. It is too small to test statistically.

## J. Round 13: separation traced across the sources (code/analysis/round13.py)
- **V John's "schism" word has a pattern.** *Schizo / schisma* ("tear, division") occurs 5 times in John: 3 times of *people* divided over Jesus (7:43, 9:16, 10:19), then twice *negated*:
  - the seamless tunic: "let us **not tear** it" (19:24);
  - the net with the 153 fish: "the net was **not torn**" (21:11).
  So the word joins the high-priest thread and the 153 thread: people split, but what belongs to him stays whole. Reading the tunic as unity is ancient (Cyprian, *On the Unity of the Church*, c. 251); the five-occurrence pattern is our count.
- **V "Apart" (*chōris*) frames the book:** "without him nothing came to be" (1:3); "apart from me you can do nothing" (15:5); the face-cloth "rolled up apart" in the empty tomb (20:7).
- **V Gathering:** "gather up the fragments, *that nothing be lost*" (6:12–13); "to *gather into one* the scattered children of God" (11:52). Against it stand the council "gathered" against him (11:47) and the dry branches "gathered and burned" (15:6).
- **Contrasts across the sources** (separate-word share of separate + gather):
  - Separating-heavy: Paul 0.88, Hermetica 0.81, Plato's *Timaeus* 0.79, Genesis 1–11 0.69, Philo 0.67.
  - **John is balanced (0.55).** Matthew, Mark and Luke and the Septuagint lean to gathering (0.44–0.45).
  - Genesis 1 creates by separating (*diachorizo*: 1:4, 6, 7, 14, 18). Philo names the Logos "the Cutter" (*tomeus*) that divides all things.
  - The Community Rule uses *badal* (separate) 25 times and *yachad* (together; the Community's own name) 35 times the Hebrew Bible's rate. **Qumran separates in order to unite inside; John's Logos divides those who hear him, while gathering "into one" what is his.**

## K. Round 14: tearing, sound and order (code/analysis/round14.py)
- **V Torn in the other Gospels, not torn in John.**
  - In Matthew and Mark **the high priest tears his garments** (Mt 26:65; Mk 14:63), and in all three Synoptics **the temple veil is torn** (Mt 27:51; Mk 15:38; Lk 23:45). Mark also has the heavens torn (1:10).
  - In Luke's miraculous catch **the nets were tearing** (Lk 5:6).
  - John has none of these. Instead **the tunic is not torn** (19:24) and, in his own miraculous catch, **the net is not torn** (21:11).
- **V The law behind it: Leviticus 21:10**, "the high priest … **shall not tear his garments**". It is one of only 5 negated tearings among the Septuagint's 105 tearings.
  - Caiaphas breaks this law in Matthew and Mark.
  - In John, Jesus' seamless (high-priestly) tunic is kept whole.
  - This joins the high-priest thread (Josephus' seamless robe, Polycrates' *petalon*) to the schism thread: in John the true high priest's garment is never torn.
- **N Sound:** the schism verses are not reliably noisy. 7:43 is in John's noisiest 1–2%, but 10:19 is quiet; the three together give p = 0.13–0.20. "Not torn" 19:24 is quiet (16–25th percentile).
- **N Order:** with the full word families (pre-registered: "not torn" counted as wholeness), separation → gathering/one → completion is not significant (p = 0.15; p = 0.40 the other way). The arc remains a reading, not a proven design.

## L. Round 15: the earliest manuscripts, sound-alikes, and the language of delivery (code/analysis/ms_sound.py)
- **V The high-priest words survive in every early witness.** "High priest that year" (11:49), "known to the high priest" (18:15), the seamless "woven from the top" tunic (19:23; Vaticanus spells it ἄρραφος, which sounds the same), "let us not tear it" (19:24) and "not torn" with 153 (21:11) are present in P66, P75 (where extant), Sinaiticus and Vaticanus.
- **V Half of John sounds like something else.** 50% of John's words sound exactly like another Greek word form in Koine pronunciation: we/you (*hēmeis/hymeis*, 270 tokens), o/ω (2,585), ei/i/ē (2,230), ai/e (1,662).
- **V The text was handled through sound.** Where P66, Sinaiticus and Vaticanus differ from the critical text, 53–60% of the differences sound the same: a different spelling, or a different word that sounds identical. P75 is the most careful copy (35%). **Most manuscript variation in John is invisible to the ear, so the spoken text was more stable than the written one.**
- **V Sound-alikes that flip the meaning on the page but not in the ear** (111 found):
  - we/you swaps: P66 9:40 "are *we* blind?" → "*you*"; Sinaiticus 8:54 "*our* God" ↔ "*your* God", 8:42 and 16:7;
  - P75 4:13 and 6:56 "whoever *drinks*" (πίνων) → "*hungers*" (πεινῶν);
  - Sinaiticus 1:29 "who *takes away*" (αἴρων) → ἐρῶν, a sound-alike;
  - person and mood flips such as "you will see" → "to see" and "you seek" → "is sought".
- **V The language of delivery: some chains exist only in Greek.** In the Syriac Peshitta (close to Jesus' Aramaic):
  - the "schism" chain breaks into three different roots: *pelgutha* (division) for 7:43 and 10:19, *sdq* for the tunic, *ṣrṭ* for the net;
  - the double meaning of *anōthen* ("again" / "from above", 3:3) collapses to *men d-rish* ("anew");
  - "lifted up" (3:14; 12:32) becomes *rwm* (exalted), losing the cross.
  But **"wind/spirit" survives** (*ruḥa*, 3:8), and **"I am" survives** (*ena ithay*, 8:58). Conclusion: John's word-chains and misunderstanding scenes were composed for the *Greek* ear. Some images (wind/spirit, "I am") would also have worked in spoken Aramaic, but the schism chain and the *anōthen* pun did not.

## M. Round 16: translated from Aramaic, or composed in Greek? (code/analysis/semitic.py)
Model: Greek known to be translated from Hebrew (Genesis, Kingdoms, Psalms, Daniel, Ezekiel) against Greek known to be composed in Greek (Wisdom, 2 and 4 Maccabees, Josephus, Philo, Hermetica). It separates them with 97% accuracy. Score: 0 = composed, 1 = translated.
- **V John sits exactly between (0.49).** It is neither a translation nor polished Greek.
  - Unlike translations, John almost never starts a sentence with "and" (7% of sentences, against 42–79%).
  - Unlike Greek authors, John almost never uses the particles *men* and *te*.
  - Instead he has two habits of his own: **asyndeton**, sentences joined by no connective at all (56%, the highest of any text tested; Aramaic tends this way, and Burney noted it in 1922), and the narrator's *oun* ("so, then": 12.8 per 1,000 words, rising to 21.8 in the passion narrative).
  - Profile: a Semitic speaker composing directly in Greek, in his own spoken style. Not a translation (consistent with the Greek-only puns, round 15).
- **V The prologue is the most Semitic part of John (0.59).** It has no particles at all, and 79% of its sentences have no connective, closest to the Greek Psalms (72%). That fits the theory that the prologue was a hymn, possibly with a Semitic poetic background, and fits "breathes like a psalm".
- **Context:** Revelation scores as translation Greek (0.74), Mark leans Semitic (0.69), and Romans and Hebrews are composed Greek (0.36–0.39). 1 John scores 0.62.

## N. Round 17: the prologue in Aramaic, and the form of "I am" (code/analysis/aramaic_prologue.py, iam_forms.py)
- **N The Aramaic (Syriac) prologue is not more patterned than the Greek.** Against its own baseline (every other 18-verse window of the Peshitta Gospels): staircase average (51st percentile), rhyme none, consonant word-play high but not exceptional (86th). The Greek staircase is at the 80th percentile.
  - The **centre stays in 1:12** in both languages.
  - Syriac sound-echoes visible by eye: 1:5 *nuhra … manhar* (light … shines, one root) with *ḥeshukha* twice; 1:14 *shubḥeh shubḥa* ("his glory, glory") and *aggen* ("dwelt / overshadowed"), the Syriac verb of divine presence.
  - Burney's "Aramaic original hymn" is not supported by measurable structure. The prologue's patterning is a Greek-language feature, though its style is Semitic (round 16).
- **V John's "I am" has its own form.**
  - "I am **the** + noun" (the bread, the light, the door, the way) is 47% of John's "I am" uses (15 of 32), against 4% in the Septuagint and 8% in the Synoptics. Philo's 20% is mostly quotations of Exodus 3:14, "I am the One who is".
  - The Septuagint's dominant form, "I am the Lord" (36%), **never appears in John**.
  - John's other strong form is the absolute "I am" (31%; e.g. 8:58), matching Isaiah's divine *egō eimi* (Septuagint 24%).
  - The Isis-hymn form, "I am [Name], [title]", is absent from John (its only case is Pilate's "Am I a Jew?").
  - Profile: John joins Isaiah's absolute divine "I am" to everyday images (bread, light, door, vine), with no name and no title. He follows neither the Septuagint's formula nor the Egyptian aretalogy pattern.
- **Pending:** the Isis aretalogies (Kyme, Andros) themselves. Their Greek text sits on sites outside this session's network allowance (attalus.org; the PHI inscriptions database). Allowing one of those hosts would let them run through the same measures.

## O. Round 18: Sumerian literature (code/analysis/sumer.py; source: Black et al., *The Literature of Ancient Sumer*, OUP 2004, supplied by the user; text not stored)
- **V/K A motif cluster in Inana's Descent to the Underworld (c. 2000–1750 BC):**
  - the goddess's corpse is hung on a hook;
  - "after **three days and three nights**" her minister seeks help;
  - Enki makes two beings and gives them the **life-giving plant** and the **life-giving water**;
  - these are sprinkled on the corpse, "and so let Inana **arise**".
  John's parallels: "living water" (4:10, 7:38), "bread of life" (6:35, 48), "in three days I will raise it up" (2:19), the crucifixion, the seeking woman at the tomb (20). **Status: a parallel pattern, not evidence of influence.** Two thousand years separate them, and scholars dispute the "dying-and-rising god" category (J. Z. Smith against T. Mettinger).
- **V/K The shepherd-king.** Sumerian kings and gods are "shepherds" (Dumuzid the shepherd; Ur-Namma; Sulgi: "**I am the herdsman and shepherd** of the black-headed"). Shepherd and fold language is 3–10 times denser than in John. The thread runs Sumer → Ezekiel 34 → John 10, "**I am the good shepherd**".
- **V The oldest "I am" chain.** Sulgi's praise poem (c. 2050 BC) uses "I am" 18 times per 1,000 words, against John's 3.3 (English translations).
  - Its form is mostly **"I am *a* …"** (26: "a fierce-looking lion", "a king treated with respect"), "I am he who …" (16), the name ("I am Sulgi") and "I am *the* …" (11).
  - John's form is **"I am *the* …"** (15) and the absolute "I am (he)".
  - So the royal self-praise genre is ancient (Sumer → Egyptian and Isis aretalogies). John's definite, nameless "I am the bread / light / shepherd" is a different form inside the same long tradition.
- **Light and life:** John uses "light" (12.6) and "life" (23.0) per 10,000 words far more than Sumerian literature (3.3; 10.4). Temple language is denser in Sumer (15.4 against 7.3).
- **Refrains:** Sumerian narrative poems are refrain-heavy (Inana's Descent 18%, Dumuzid's Dream 20%), the sign of oral performance. The average Sumerian composition (3.8%) is close to John (5.7%).
- **The Met cuneiform volume** (*Cuneiform Texts in the Metropolitan Museum of Art I*) is scanned. Contents, from OCR: Ur III and Old Babylonian business and legal records, Gudea's temple-building cones, Old Assyrian letters, and two Amarna letters (correspondence with Egypt). OCR of all 413 pages is running.

## P. Round 18b: the Met cuneiform tablets (code/analysis/met_tablets.py; OCR of the user's scan, 413 pages, text not stored)
- **Contents:** Ur III and Old Babylonian business records (receipts of lambs, kids, cattle; silver loans), legal texts, Old Assyrian merchant letters, temple-building cones and bricks (Gudea, Ur-Nammu, Sulgi), and two Amarna letters to Pharaoh. The business records are numeric bookkeeping; they carry no literary signal.
- **Sulgi again.** A Sulgi brick from Nippur's Inanna temple reads "For Inanna … Sulgi … king of Ur … **built her E-dur-an-ki**". The temple name means "House, **bond of heaven and earth**". Sulgi is the king of the "I am" praise poem (round 18). Mesopotamian temple-towers were imagined as links between heaven and earth; scholars connect the ziggurat stairway to **Jacob's ladder** (Genesis 28:12). That ladder sits at Genesis' letter-centre (round 6) and is where John 1:51 points ("heaven opened, and the angels of God ascending and descending"). Thread: Sumerian "bond of heaven and earth" → Jacob's stairway → John 1:51. **Status: known comparison (the ziggurat link is standard); the Met brick is a concrete instance.**
- **Gudea's cone:** "he built his (Ningirsu's) **Eninnu**, the flashing thunderbird, and restored it at its place". It belongs to the temple-building tradition, which in the Literature volume includes Gudea's dream instructions for building the temple.
- **Egypt wrote and read cuneiform.** Assur-uballit of Assyria to Pharaoh (Amarna letter 16: "I have sent my messenger … he should see what you are like"), and Abi-milku of Tyre to Pharaoh (Amarna letter 153): "**I fall at your feet 7 times and 7 times**". The sevenfold bow is the Amarna court formula; compare Jacob bowing "seven times" before Esau (Genesis 33:3). This is hard evidence that Egypt, Canaan and Mesopotamia shared one scribal and diplomatic culture around 1350 BC: a documented route by which ideas moved between Egypt and Mesopotamia long before Alexandria.

## Q. Round 19: following the threads (code/analysis/round19.py)
- **V "Lamb of God" leans to Isaiah's Servant.** John 1:29–36 ranks the Servant song (Isaiah 52:13–53:12) **97th of 4,012** fifteen-verse windows of the Greek Old Testament (top 2.4%), against **725th** for the Passover lamb (Exodus 12).
  - The shared rare word is *amnos* (lamb): Isaiah 53:7, "as a **lamb** before its shearer is dumb". Exodus 12 uses *probaton*, not *amnos*.
  - John's "who **takes away** the sin" matches Isaiah 53:4 and 53:12, "he **bears** our sins".
  - This fits the old proposal that behind "lamb" lies Aramaic *ṭalyā* (lamb / servant / child).
- **V John 6 and Passover:** Exodus 16 (manna) is the 17th nearest of 1,097 chapters to John 6 (top 1.5%), and Psalm 78 (77 in Greek, "bread of heaven", quoted at 6:31) is 90th. That supports the Passover-reading background of the bread chapter (Borgen, *Bread from Heaven*).
- **V The vertical axis, "bond of heaven and earth".** John uses ascend/descend 21.4 times per 10,000 words (Synoptics 11.8, Paul 4.7) and "from above / from below" 5.8 times (Synoptics 1.6). The 29 ascend/descend verses form two strands:
  - **heaven–earth:** the Spirit descending (1:32–33); angels ascending and descending on the Son of Man (1:51, Jacob's ladder); "no one has ascended into heaven but he who descended" (3:13); the bread that "came down from heaven", 8 times in John 6; "I have not yet ascended" (20:17);
  - **pilgrim ascents to the temple:** 2:13, 5:1, 7:8–14, 11:55, 12:20.
  The ladder and ziggurat image (round 18b) runs through John as a structuring axis: heaven ↔ temple ↔ the Son of Man.
- **V Sevens (scholarly counts, confirmed).** "I am the + noun" carries 7 images: bread (6:35, 41, 48, 51), light (8:12; 9:5), door (10:7, 9), shepherd (10:11, 14), resurrection (11:25), way (14:6), vine (15:1, 5). Seven narrated signs is the standard count. *Curiosity, not evidence:* the word "sign" (*sēmeion*) occurs 17 times, and 153 = 1+2+…+17.
- **V Three days and four days.** "Destroy this temple and **in three days** I will raise it" (2:19–20; the temple is his body, 2:21). Lazarus has been dead "**four** days" (11:17, 39), past the third day. Compare Inana: "after three days and three nights" (parallel pattern, round 18).

## R. Round 20: the Isis texts (code/analysis/isis.py; user's files: Isidorus' hymns in ancient Greek, SEG 8.548–551; the Kyme aretalogy in a modern-Greek machine translation, so structure only)
- **V Isis speaks in titles and deeds; John in images and "not from myself".**
  - Kyme aretalogy: 11 of 58 lines are "I am" (19%), and 27 (47%) are first-person deeds: "I separated earth from heaven", "I showed the paths of the stars", "I brought up islands from the depths into the light", "I free the prisoners", "I ordained that the true be thought good", "I invented letters with Hermes".
  - Her "I am" predicates are names, titles and kin: "I am Isis, mistress of every land", "eldest daughter of Kronos", "wife and sister of King Osiris", "mother of King Horus", "**Queen** of rivers, winds and sea", "Queen of war / of thunder / of storms", "she who rises in the Dog Star".
  - John's Jesus has **no title, kin or sovereign deed** in his "I am": bread, light, door, shepherd, resurrection, way, vine. He says "I do nothing from myself" (13 times). His first-person deeds are relational: "I have made your name known", "I have given them your word" (John 17).
  - Isis *separates* earth from heaven (like Genesis 1); John's Son *joins* them (1:51; the vertical axis, round 19).
- **V Isidorus' hymns (Egypt, 1st c. BC) share John's religious vocabulary:** life ("finder of all life", 6 times), light ("Anchoes **your son**, who dwells in heaven's ether, is the rising sun **who showed the light**"), saviour ("immortal saviour"), creator, Nile water, "you **alone** are all the goddesses the nations name". Their sound is as quiet as John's (noise share 0.324 against 0.326), with metre (periodicity 0.054 against 0.019) and less hiatus.
  - Status: a shared Hellenistic-Egyptian vocabulary of life, light, a heavenly son and a saviour, as with the Hermetica (round 6), not borrowing. John's distinctive turn is the *form*: no name, no title, and "not from myself".

## S. The John sound model (model/)
A configurable, evidence-labelled reconstruction of John as heard (see model/README.md). Default build: 227 minutes of public reading, 31,243 syllables, 2,310 breath groups (10.2 per minute). Every verified discovery is attached as a marker on its syllables.

## T. Round 21 (code/analysis/round21.py): see REPORT.md for the consolidated picture
- **V Papyrus lines ≈ breath groups.** P75 averages 12.4 syllables per written line, very regular (CV 0.16); its prologue lines average 13.5, the size of the spoken breath groups. P66: 10.8 (CV 0.22). Sinaiticus and Vaticanus use narrow columns (6.0 and 7.6).
- **N** Songs of Ascents ↔ John's vertical axis: no link (median rank 702 of ~1,100).
- **K+** John 10:22–39 (Dedication): Psalm 82 is rank 2 (quoted at 10:34); 1 Maccabees 4 and 2 Maccabees 10 rank 97–98 (top 9%).
- **INTRIGUING** Inana's Descent motif map: descent, seven gates, corpse on a hook, three days, mourning women, life-giving water and plant, arising, and a **substitute** (Dumuzid), compare 11:50. Needs a controlled multi-myth test.
- Gudea's temple: the cosmic temple-building of Gudea ("Ningirsu, I am going to build your house for you") is thematic background to John 2:19–21, not a textual link.

## U. Round 22: the report path, steps 1–5 (code/analysis/round22.py, egypt.py; audio_model/)
1. **Manuscript lines.** P75's line breaks fall at clause ends a little more often than random word boundaries (10.9% against 8.6%, p = 0.007), but 571 breaks split a word. The breath-group-sized lines (round 21) come mainly from column width, with only a slight sense-line tendency. **Quiet farewell beyond pronouns: no** (with pronouns removed, 0.331 against 0.334, p = 0.41). Closed.
2. **Pre-registered retests.**
   - The separation → gather → complete order is not significant in John (p = 0.41) or in Matthew, Mark and Luke. **Closed: the arc is a reading, not a design.**
   - **Centre motif catalogue:** "life / living" (*ḥayyim*) appears in the centre window of 5 of 39 Hebrew books, against 0.9 by chance (p = 0.001, survives correction): Leviticus 14:50–52 and Song of Songs 4:15 (the known living-water centres), plus Ruth 2:20 ("kindness to **the living and the dead**"), Ecclesiastes 6:8, 12 ("the days of his life") and Exodus 22:3 ("found **alive**"). The other seven motifs (heaven+earth, water, light, temple, gate, tree, name of YHWH) are at chance. **V: book centres lean toward "life / the living",** an extension of the living-water finding.
3. **Myth pass (fixed motifs, keyword-coded, crude).** Of John's 6 motifs (death, mourning, three days, life-water/food, rising, substitute), Inana's Descent has all 6, Mark 5, Plutarch's Osiris 4, the Joseph story (control) 4, the Hymn to Demeter 3, and the Hymns to Apollo and Hermes 2. The "substitute" motif appears only in John, Mark and Inana. **O: Inana is the closest myth, but the Joseph control scoring 4 shows keyword coding is too blunt.** Needs scene-level coding.
4. **Egyptian sources (Project Gutenberg, public domain).**
   - *Book of the Dead* (Le Page Renouf): 492 "I am" (3.6 per 1,000 words). The **definite "I am the …" is its main form (148)**, closer to John than Sulgi's "I am a …" or Isis's titles.
   - But its predicates are divine identities: "I am the lord / master / son / bull / great god / babe / heir / guardian / pure lotus / only one". Also "I am [god's name]" (75) and the negative confession "I am not …".
   - **None of John's seven images (bread, light, door, shepherd, resurrection, way, vine) occurs as "I am the …" in the Book of the Dead or the *Egyptian Literature* anthology.**
   - **V:** John shares the Egyptian funerary *form* ("I am the …") but not its *content*. The deceased claims divine identities; John's Jesus offers everyday, life-giving things.
5. **Rendered audio** (engine; Koine; public declamation): the prologue 1:1–5, the vine 15:1–5 and "It is finished" 19:28–30, each in a synagogue, a house church and a theatre (`audio_model/*.mp3`, with the phonetic score in the matching .json).

## V. Round 23: was the text written as performance? (code/analysis/movement.py) · interactive map (map/index.html)
- **Test:** every verb of motion is a step on three axes (vertical: ascend/descend; threshold: enter/go out; approach: come/go away), and body actions are counted (stand, sit, rise, fall, bow, weep, breathe on, touch, wash, lift up the eyes).
- **N Overall movement is ordinary.** Motion per 1,000 words: John 19.7, Matthew 20.2, Mark 19.8, Luke 16.8. Body actions: 7.2 against 7.1–9.4.
- **V Only the vertical axis stands out** (2.1 against 1.1–1.3), the heaven–earth movement of rounds 18–19. The cumulative vertical path falls to −13 at 6:58 (the bread that "came down", repeated) and climbs back with the ascents.
- **V John writes in blocks:** he switches between speech and action less often than chance (0.32 against 0.44 shuffled; the Synoptics are near chance at 0.41–0.45), with long discourse blocks and long action blocks. Speech and action share a verse in 19.3% of his verses (Synoptics 15–17%).
- **N** The inside/outside staging of the trial before Pilate (18:28 in, 18:29 out, 18:33 in, 18:38 out, 19:4–5 out, 19:9 in) is visible but, with 7 moves, not more regular than chance (p = 0.46).
- **Verdict:** the text carries staging, but there is no evidence yet of a hidden spatial notation beyond narrative. Defined next tests: compare with a real Jewish-Greek performance script (Ezekiel the Tragedian's *Exagoge*) and Greek tragedy; score deixis ("this", "here", "behold", "now") against the movement track; an actor test using only the Greek; check whether actions fall on breath boundaries in the sound model.

## W. Round 24: the four performance tests and shape poetry (code/analysis/performance.py)
- **T1 Performance profile.** John against real plays (Ezekiel the Tragedian's *Exagoge*, Jewish-Greek, probably Alexandrian, via Eusebius, *Praeparatio Evangelica* 9.28–29; Sophocles' *Oedipus the King*; Euripides' *Bacchae*; Aeschylus) and narrative / exposition (Josephus, Philo, the Synoptics).
  - John is nearest the Synoptics (3.2), then Euripides (4.65) and Aeschylus (4.79). His mean distance is 4.83 to the plays and 5.18 to narrative.
  - **V John is more dialogic than the plays:** "I" 30.1 and "you" 26.3 per 1,000 words, against 9.9–18.8 and 6.4–15.5 in the tragedies and about 2 in Josephus and Philo. "Behold" is 1.5 (plays 0–0.9). The vocative "O!" of tragedy (7.2–7.6) is rare in John (0.6).
- **T2 Deixis on movement:** pointing words share verses with motion and gesture in every Gospel (John r = 0.14, Matthew 0.16, Mark 0.10, Luke 0.11; all p < 0.01). Real, but not special to John.
- **T3 Actor test:** needs performers; protocol written (code/analysis/performance_actor_protocol.md).
- **T4 Actions on breath boundaries:** no for John (ratio 1.05); Matthew 1.50, Mark 1.25, Luke 1.14.
- **S Shape poetry (Alexandria and Rhodes).** The line-length detector finds the known shape poems: Simias' Wings (+0.99), Axe (−0.53), Egg (+0.39), and the Altars of Dosiadas (+0.46) and Besantinus (+0.58), all p ≤ 0.02. John's prologue verses have no shape (+0.04, p = 0.86). P75's prologue lines lean toward longer lines in the middle (−0.48, p = 0.04), a single marginal result probably caused by column layout. **N: no shape-poem geometry in John.**
- **Verdict on "3D writing":** John is composed as voiced dialogue, more densely first- and second-person than Greek drama, with narrative carrying ordinary staging and a distinctive vertical (heaven–earth) axis. No hidden spatial, shape or movement notation was found.

## X. Round 25: tense, rhythm and participles (code/analysis/action_rhythm.py)
- **V Tense as a camera.**
  - **John uses the historic present more than any other Gospel:** 14.1 per 1,000 words, against Mark 11.6, Matthew 6.4 and Luke 2.2.
  - **He zooms in at his turning points.** In the fixed list of scenes (the well, the blind man, Lazarus' tomb, the footwashing, the arrest, the cross, the empty tomb, the lakeside), the rate is 28.7 per 1,000 against 14.1 in random verse sets (p < 0.0001). Without "says" (*legei*) it is still double (10.6 against 5.5, p = 0.003).
  - By chapter, the resurrection chapters are densest: 20 (39 per 1,000) and 21 (38), then 13 (24), 1 (23) and 4 (22). The farewell prayer (17) has none.
  - John also uses the imperfect ("the camera holding") 25% of the time, against Mark 35%, Luke 25% and Matthew 13%.
  - **Meaning:** the narrator moves the listener into the present tense at the moments of encounter, especially at the empty tomb and the lakeside. This is the ancient *enargeia* (vividness) technique.
- **N/INCONCLUSIVE Rhythm acting out motion.** Our syllable-weight measure (word-internal, classical values) **fails its control**: Odyssey 11.596 (pushing the stone uphill) does not come out heavier than 11.598 (the stone rolling down). It cannot see metre across word boundaries or settle ambiguous α/ι/υ lengths. Neither John nor Mark shows lighter rhythm in fast-action verses (both −0.025, not significant), but the method is not valid yet. **Needed:** true metrical scansion (positions across word boundaries), checked on Homer, before testing John.
- **N** Participle chains are not denser at turning points (0.050 against 0.046). Turning-point verses open *with* a connective more often (fewer asyndetic openings: 0.44 against 0.52). Narrative "and / then" carries the action.

## Y. Round 26: a validated metrical scanner, rhythm and motion, and structure across scales (code/analysis/scanner.py, rhythm_dimensions.py)
- **V The scanner works.** Quantity across word boundaries (vowels long by nature, length by position, double consonants, the mute-plus-liquid exception, epic correption, diaeresis, elision). 94.7% of Iliad 1–3 (1,949 lines) scans with zero rule violations. It reproduces Dionysius' example: Odyssey 11.598, the stone rolling down, scans DDDDD (all quick dactyls); 11.594, the stone lifted, opens with heavy spondees (SS…).
- **Rhythm acting out motion is real in Homer, but local.** Odyssey lines with verbs of rapid motion have more dactyls (+0.16 per line, p = 0.004). In the Iliad they do not (−0.02, p = 0.66), and strain lines are not heavier. A poet's device used at chosen moments, not a rule of the language.
- **N Not in the Gospels.** With the same engine applied to prose, fast-action narrative verses are no lighter than other narrative in John (−0.002), Mark, Matthew or Luke. John's prose is the lightest overall, marginally (heavy share 0.611 against 0.612–0.620).
- **N No hidden structure across scales in John's sound stream.** A test that imposes no units (detrended fluctuation analysis, which finds patterns repeating at every scale at once) gives John α = 0.503 for syllable weight and 0.518 for word length, the same as shuffled text (0.503; 0.514). Mark and Matthew show slight long-range structure in syllable weight (0.53); Josephus none.
- **Meaning:** John's sound is uniformly smooth: quiet, light, even, with no rhythmic shapes drawn into it. His structure lies elsewhere: centres, the "I am" ring, theme blocks, tense zooms and pointers to other scripture.

## Z. Structure the text finds for itself (round 27, `self_structure.py`)
Three tests that impose no units of ours, each with a null or a control.

**1. The letters choose their own units.** The unspaced letter streams of P66 (64,263 letters) and P75 (46,599 letters) were segmented two ways: by a compression model (a unigram lexicon under a minimum-description-length prior) and by byte-pair encoding.
- **S Breath edges are written into the letter stream.** The self-found boundaries fall at clause/breath ends more often than at other word ends: MDL 52% vs 43% (P66) and 56% vs 45% (P75); BPE 79% vs 60% and 82% vs 62% (all p < 0.0001). Comparing the *same word form* at a clause end and elsewhere removes word-type effects, and a lift of +3.3% to +6.7% remains (p 0.028, 0.024, < 0.0001, < 0.0001). Nothing in the stream marks the clause; the letters around it make the edge cheaper to cut.
- **S The prologue centre is 1:12 in self-found units too**, in both papyri. Counted in editors' words it is 1:11; counted in letters it is 1:12.
- **The units the model glues are spoken words, not printed ones.** Preposition + article (ἐκ τοῦ, εἰς τήν, ἐν τῷ), καὶ ὁ, ἦν δέ, and **ἐγὼ εἰμί ×13 in P66** (οὐκ εἰμί in P75). John's "I am" behaves as one unit in the letters themselves.
- **N Scribal line breaks ignore the units.** Mid-word line breaks are no more likely at self-found boundaries (MDL 19.5% vs 18.3%; BPE 8.4% vs 10.9%). Scribes broke lines by space, which agrees with "lines ≈ breath size, but not sense-lines".

**2. Recurrence plot** (`map/john_recurrence.png`). Each pair of verses is scored by IDF-weighted shared vocabulary; the top 1.5% of pairs count as recurrent.
- The detector was validated on two controls. Mark × Matthew shows lines parallel to the diagonal (0.166 against 0.010 shuffled). Mark followed by its own reversed order shows crossing lines (ratio 1.35).
- In John, echo lines and ring lines both exceed a shuffle within each chapter (0.076 vs 0.048, and 0.073 vs 0.046). They also exceed a whole-book shuffle at long range, 30 or more verses apart (0.061 vs 0.030 for both).
- **N No preference for rings.** The ring : echo ratio is 0.97, against 0.98 in the null (p 0.58). The lines are short (at most 3 verses). John has local and long-range returns, but no book-wide geometric ring.
- **Long-range links found blind** (all known to commentators, recovered without being told):
  - 3:18–20 ↔ 12:35–37, crossing: light, darkness and believing, at the opening and the close of the public ministry;
  - 5:30–32 ↔ 8:13–16: testimony;
  - 13:36–37 ↔ 21:20–22: Peter and "follow me";
  - 6:28 ↔ 14:10: "the works of God";
  - 15:19 ↔ 17:5.

**3. Lining up the layers.** Six per-verse tracks (sound, tense, voice, movement, themes and pointers) were smoothed over 7 verses and tested against circular shifts.
- **S Two modes.** Sound ↔ voice r −0.41 (p < 0.001). Voice ↔ themes +0.38 (p < 0.001). Tense ↔ movement +0.34 (p 0.003; partly shared verbs). Movement ↔ themes −0.24 (p 0.02). The text alternates between narrative action (historic presents, movement, harder sound) and discourse (1st/2nd person, theme words, quiet sound).
- **N No multi-layer synchrony.** Verses where three or more layers peak together: 64 against 62 expected (p 0.45). Leaving out sound and voice, the count is 154 against 142 (p 0.20). The pointers (centres, "I am", the schism word, the vertical axis, the high priest, living water) are independent of every other layer (|r| ≤ 0.11).
- **Meaning:** John's layers do not fire together. They take turns. The meaning-markers sit on a separate track from sound and motion, so the "extra dimension" is the alternation itself, together with the cross-references, not a stacked peak.

## AA. Controls for the breath edges; the rhythm of the mode switch (round 28, `round28.py`)
**A. The breath-edge effect belongs to John.** The same self-segmentation and the same matched test (the same word form at a clause end vs elsewhere) were run on 10 texts. The John texts are the first 40,000 letters of each manuscript; P46's Romans, 1 Corinthians and Hebrews are shorter (18,441–31,197 letters).

| Text | MDL same-word lift (p) | BPE same-word lift (p) |
|---|---|---|
| John P66 | +4.2% (0.018) | +6.4% (<0.001) |
| John P75 | +2.7% (0.13) | +8.3% (<0.001) |
| John Sinaiticus | +5.7% (0.007) | +6.3% (<0.001) |
| John Vaticanus | +6.4% (0.003) | +6.6% (<0.001) |
| **Luke, P75, same scribe** | +1.0% (0.35) | +0.6% (0.37) |
| Mark, Sinaiticus | −2.0% (0.77) | −19.1% (1.00) |
| Mark, Vaticanus | −5.6% (0.99) | −18.0% (1.00) |
| Romans, P46 | −2.6% (0.77) | +2.1% (0.20) |
| 1 Corinthians, P46 | +1.2% (0.38) | +4.8% (0.010) |
| Hebrews, P46 | −0.1% (0.48) | +2.8% (0.15) |

- **S** The effect appears in all four manuscripts of John and in neither method's run on Luke written by the same scribe in the same codex. So it comes from the composition, not the copying.
- It is absent or reversed in Mark (both codices) and in Paul, apart from one weak BPE result for 1 Corinthians. In Mark the letters actually *hide* clause ends, consistent with Mark's flowing καί-chains.
- In John alone, clause edges can be heard in the letter stream. The likely mechanism, still to be tested, is that John's clauses begin with recurring, predictable openings: asyndeton, οὖν, "λέγει αὐτῷ", "ἀμὴν ἀμήν". That is a mark of composition for speaking aloud.

**B. The action/discourse switch is not a regular beat.**
- **N** All four Gospels switch *less* often and *less* regularly than autocorrelated noise. John's regularity CV is 1.56 against 0.90 (p of more regular = 1.00); measured in spoken time it is 1.62. The switching clusters: rapid alternation in dialogues (John 4, 7, 10, 18–20), then long unbroken stretches. The longest is the farewell discourse, 13:32 → 18:4, with no switch for five chapters.
- **I** The strongest period in John is 289 verses, which divides the book into thirds (p 0.002). In spoken time that is ~76 minutes, a third of the 227-minute performance. Matthew also shows thirds (356 verses, p 0.006). Mark's strongest period is the whole book; Luke's is not significant. So the result is not unique to John. It may reflect three performance sittings, or just slow drift. Next test: whether the thirds line up with natural breaks (around 7:1 and 13:1).

## AB. The mechanism behind the breath edges; the "three movements" retested (round 29, `round29.py`)
**A. Predictable openers are not the mechanism. Missing connectives are.**
- **N** John's clause openings are not unusually predictable. Opener entropy (bits, equal samples): John 7.00, Matthew 7.13, Luke 6.75, Mark 5.36 (the most predictable). The ten commonest openers cover 35% of John's clause openings, against 37–55% in the other Gospels.
- Splitting clause ends by what follows shows where the round-28 difference comes from. BPE results (same-word lift):

  | Text | Clause ends before a stock opener | Before any other opening |
  |---|---|---|
  | John (3 manuscripts) | −7% to −9% | +13% to +14% |
  | Luke | −30% | +19% |
  | Mark | −48% | +20% |

- So a stock connective (καί, ὁ δέ) glues onto the word before it and hides the clause end. Before other openings, every Gospel's edges show.
- Mark and Luke start far more of their clauses with such connectives: 57% of Mark's clause ends in Vaticanus and 39% of Luke's in P75, against 32–34% of John's in all three manuscripts. That is what made John look unique.
- Deleting the stock openers raises the lift everywhere, Luke and Mark included (BPE +16% to +17%). The deletion test therefore cannot separate the books.
- **Revised reading of #23:** John's clause edges stay visible in unspaced writing because his clauses rarely start with a connective. This is the same feature as his record asyndeton (round 16). It is a real, measurable trait of John's composition, but it is the asyndeton showing through, not an extra hidden breath signal.

**B. No three equal movements; the method finds each Gospel's great discourse instead.**
- **N** The best three-part division of John's mode series is 1:1–13:32 | 13:33–17:26 | 18:1–21:25, which is 605, 123 and 138 verses (153, 33 and 42 minutes in the sound model). These are not equal thirds, so "three ~76-minute sittings" is rejected. The one-third period was the trace of one large block.
- **S (method)** That block is the farewell discourse, found blind. The cut falls exactly at 18:1, and the other cut at 13:33, two verses from the 13:31 where commentators begin the discourse. The 3-part fit beats power-law noise surrogates (variance explained 0.141 against 0.082; p < 0.001).
- The same test on Matthew finds the Sermon on the Mount (5:11–7:8; p < 0.001 against the surrogates). The tool recovers each Gospel's largest discourse without being told. It is a structural finder, not a sign of any special design in John.

## AC. John's sections from the text alone, 4 to 8 parts (round 30, `round30.py`)
Optimal segmentation (dynamic programming, sections of at least 15 verses) of two signals that know nothing of chapters or outlines:
- the action/discourse **mode**;
- the **vocabulary** (subject change).

Cuts were scored against a standard commentators' outline and against chapter starts, with 5,000 random cut sets as the null. Section names are each section's own most distinctive words.
- **S The four-part shape is recovered exactly.** On the mode signal the best 4 parts are:
  - 1:1–15 [light, dwelt, full, enlighten];
  - 1:16–13:32 [crowd, feast, come down, blind];
  - 13:33–17:26 [world, love, little while, fruit];
  - 18:1–21:25 [Pilate, crucify, soldiers, Peter].

  All three cuts fall within 3 verses of the outline: 1:16 against 1:19 (the prologue ends at 1:18), 13:33 against 13:31, and 18:1 exactly. The mean distance is 1.7 verses against 19.5 for random cuts (p 0.001). Prologue, signs, farewell, passion: the classic structure, found without being told. The farewell begins at 13:31, not at 13:1 where outlines put the "Book of Glory".
- **Most stable cuts** (counted over 10 segmentations): 18:1 ×7, 13:33 ×5, 6:29 ×4, 7:52 ×4, 8:56 ×4, 17:1 ×3, 17:26 ×3.
- **Finer sections follow John's discourses, not his feasts.** With 5–8 parts, agreement with the feast-based outline (5:1, 7:1, 10:22, 12:12) is no better than chance (p 0.09–0.29). The units the text marks off itself are:
  - the bread-of-life discourse, 6:29–6:60 [bread, heaven, eat/chew, eat], ending exactly where the disciples react (6:60);
  - the Abraham debate, 7:52–8:55 [Abraham, liar, set free, free]. SBLGNT omits 7:53–8:11, so this cut sits on the adulteress seam;
  - the blind man's interrogation, 9:8–9:34 [sinner, see again, open, eyes];
  - Lazarus and the shepherd, 9:35–14:x [Lazarus, Martha, feet, sheep];
  - the vine and the Paraclete, 14:4/14:5–16:33 [fruit, branch, Paraclete, sorrow];
  - the prayer, 17:1–17:25 [sanctify, world, yours, give], which matches chapter 17 exactly.
- **Meaning:** at the largest scale, John's own signals draw the four-part structure scholars use. Below that, the text divides itself by *speeches* (bread, Abraham, the blind man's trial, vine/Paraclete, prayer), not by the festival calendar. The festivals are narrative frame; the discourses are the units a listener would hear as sections.

## AD. The section-finder on all four Gospels; section pauses in the sound model (round 31, `round31.py`)
**A. Same blind segmentation, same scoring, each Gospel against its own conventional outline** (fixed before running). The table gives p for cuts lying closer to the outline than 5,000 random cut sets.

| Gospel | MODE 4 / 6 / 8 parts | WORDS 4 / 6 / 8 parts |
|---|---|---|
| John | **0.001** / 0.09 / 0.13 | 0.22 / 0.29 / 0.26 |
| Mark | 0.10 / 0.21 / 0.22 | 0.54 / 0.76 / 0.46 |
| Matthew | 0.47 / 0.90 / 0.81 | 0.15 / 0.19 / 0.05 |
| Luke | 0.60 / 0.27 / 0.43 | **0.002** / 0.11 / 0.69 |

- With 24 tests, two results survive correction: John's MODE result and Luke's WORDS result.
- **S John is the only Gospel whose outline is drawn by the voice.** The switching between narration and direct address (who is speaking, and to whom) reproduces John's structure: prologue / signs / farewell / passion, with every cut within 3 verses. In the other Gospels the same signal finds only their speech blocks: Matthew's Sermon (5:11–7:7), Luke's Sermon on the Plain (6:21–6:38) and Mark's Jerusalem controversies (10:14–15:14). John's architecture is audible: a listener hears the sections change as the voice changes.
- **Luke's outline is drawn by subject.** Vocabulary gives infancy 1:1–3:4 | ministry 3:5–19:12 | the parable of the minas 19:13–27 | Jerusalem and the passion from 19:28. The 19:28 cut is exact (p 0.002).
- **Mark and Matthew:** whole outlines are not recovered, but single landmarks are found exactly by vocabulary:
  - Mark: the parables at 4:1 (4:1–35) and Caesarea Philippi at 8:27;
  - Matthew: the parables chapter (13:53 exact at 8 parts), the genealogy (1:1–18) and the woes (23:13–28).
- **Meaning:** each Gospel's structure lives in a different channel: John's in voice, Luke's in subject, Mark's and Matthew's in their discourse blocks. Of the four, John's is the one built for the ear.

**B. Section pauses in the sound model.** `john_model_config.json` → `tempo.section_pauses`, with three modes:
- `self_found` (default): pauses at the blind cuts.
  - Major, 3 s: 1:16, 13:33, 18:1.
  - Minor, 2 s: 5:30, 6:1, 6:29, 6:60, 7:52, 8:56, 9:8, 9:35, 17:1. These are cuts that recur in 2 or more of round 30's 10 segmentations; cuts within 2 verses of a stronger one are merged, across chapter ends too.
- `legacy`: the old fixed seams.
- `none`.

The cut positions are measured; the pause lengths are assumptions. Running time is now 227.8 minutes. Each verse row carries `section_break`, and the summary lists the minute each section starts. The major breaks fall at minutes 2.9, 153.2 and 185.9.

## AE. Koine voice v2 and word-synced video (round 32, `code/voice/`, `video/render_samples_video.py`)
- **Method, not discovery.** A neural Greek voice (Piper VITS, CPU) is driven by the engine's Koine phonemes, then re-melodised in Praat from a rulebook.
  - Evidence layer: accent within a fifth (Dionysius), stress shift, declination, lectionary-style cadences, room.
  - Interpretive layer: estimated speaker, mood after Quintilian 11.3, emphasis on "amen, amen" and *egō eimi*.
  - Every word carries the ids of the rules applied.
- **Validation.** The pitch measured from the final audio follows the planned melody within a median 0.20–0.25 semitones (r 0.69–0.91) on four passages. The voice sits at 95–107 Hz median (adult male range).
- **Speaker estimation** (SBLGNT's capitalised direct speech plus subject search plus turn-taking) assigns the whole Gospel. Counted in words: narrator 6,856; Jesus about 6,250. It was checked by hand on dialogue scenes.
- **Video.** Each word lights up in its speaker's colour as it is spoken. The frame also shows the planned and measured melody, the rules applied, an OpenBible.info map of the scene, and arcs to the verse's echoes.
- **Samples:** `audio_model/v2/` (A engine / B evidence / C full) and `video/samples/`.

## AF. The spoken world and the opening pages (round 33)
- **Evidence base compiled:** `SPOKEN_WORLD.md` covers the three layers of speech (events, composition, performance); who probably spoke what language, with confidence and basis; the Koine sound system against the Judeo-Palestinian reconstruction; and the evidence for delivery. Each point is marked firm, probable or conjecture.
- **New data on every word:**
  - probable original language (`code/voice/language_layer.json`);
  - Aramaic words kept in the Greek;
  - the verse in P66, P75, Sinaiticus and Vaticanus: words that differ, and how many differences sound the same.
- **Speaker rules improved** (recitative ὅτι, quotations inside speech, the pluperfect as narrative, roles such as the steward). Every verse of 1:1–2:11 was hand-checked (`speaker_overrides.json`).
- **Opening pages rendered:** John 1:1–2:11, 10.6 minutes, Koine voice v2, with word-synced video (`video/samples/opening_*.mp4`).
- **Aramaic shadow:** eight sayings from John 1 voiced in Aramaic. The consonants are from the Peshitta; the vowels were supplied by hand and are **unverified**; Syriac is a later dialect than the Aramaic of AD 30. The voice is a male neural voice with Semitic consonants. This is an illustration only.

## AG. The Echo Ladder (round 34, `learn/`, `LEARNING_METHOD.md`)
- **S (computed):** John's clauses can be ordered so that 149 of the first 150 steps add exactly one new word. In its own order John adds 1.51 new words per clause. After 150 steps (151 words) the learner recognises 83% of all the words in John, and 864 clauses and 90 whole verses are fully readable. After 400 steps the figure is 94%.
- **Control:** the same algorithm on Hebrew Genesis gives 70% after 150 steps, with 149 of 150 one-new-word steps.
- **Engine:** a working sound-first course of 150 recorded steps: hear → see (meanings, grammar by colour) → recall, with spaced review inside the text.
- **Not measured:** learner outcomes. The method is a hypothesis until it is tried on people; the trial design is in LEARNING_METHOD.md.

## AH. Akouo version 2 (round 35, `learn/`)
- **Course extended to 400 recorded steps** (30.7 minutes): 401 words → 94% of all words in John; 1,630 clauses and 406 whole verses fully readable; 399 of 400 steps add exactly one new word.
- **Techniques added:** noticing; echo/shadowing with slow playback; word-for-word line; memory hooks from English derivatives; forms met; listening check; rebuild (dictation); memory hall; daily goal.
- **Any language:** the engine is separated from the course pack. In-app builder: paste a text → analysis by Claude, or a plain word-list fallback → ladder built in the browser → spoken by the page's voice. An offline builder is also provided (`build_course.py`).
- **Verified:** the browser ladder is identical to the Python ladder on John (60 steps); an automated run exercised every stage and review type; a Spanish course was built without analysis.
- **Not verified here:** the Claude-analysis path and the Claude voice (they need a signed-in viewer). No learner outcomes.

## AI. Sala, a designed language for people and machines (round 36, `lang/`)
- **Built:**
  - a 50-syllable sound system, chosen from PHOIBLE frequencies (each sound in 56–97% of 3,020 inventories);
  - 148 roots derived by rule from widely known words (70 unchanged; every pair at least two sounds apart);
  - 33 one-syllable grammar words and ten rules;
  - a featural script, a syllable-by-syllable hand code, and six stance melodies;
  - a number code and an unambiguous parser, giving each sentence a function-call form and a compact byte form.
- **Checked:** 99 sample sentences parse to exactly one structure and survive the byte round trip; the browser parser equals the Python reference on all 99; the six melodies are measurably distinct (medians 91–137 Hz).
- **Course:** 89 recorded steps teach 104 sentences in 5.3 minutes of audio.
- **Costs measured:** 1.4–1.7 times the syllables of English; less lexical precision.
- **Not tested:** learners, signers, speakers of tone languages. Adoption is a social matter that no design decides.
