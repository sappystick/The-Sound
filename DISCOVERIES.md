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
