# Words of power, round 3: the magical papyri, the Testament of Solomon, and the codes in the instructions

**Sources added in this round:**
- The *Greek Magical Papyri in Translation* (ed. H. D. Betz), from the scan you supplied. It is under copyright, so only counts, the ancient magical words and short quotations are kept here.
- The *Testament of Solomon*:
  - McCown's 1922 Greek critical edition, from the scan you supplied; its Greek text was OCR'd for this round;
  - Conybeare's 1898 English translation (public domain), from J. H. Peterson's digital edition (CC BY 4.0).
- Not available: the 1928 Greek edition of the papyri (Preisendanz) is borrow-only on the Internet Archive.

**Approach, as you set it:** every claim in these texts is recorded as the text makes it, without judging whether it is possible. Codes are tested against chance, so that real patterns can be told from coincidence. Interpretations are labelled **Reading**: they are hypotheses about what an instruction may encode, not established meanings.

Scripts: `power/analyze_pgm.py`, `power/analyze_tsol.py`, `power/codes.py`. Results: `power/pgm_results.json`, `tsol_results.json`, `codes_results.json`.

---

## 1. The Greek Magical Papyri: a manual of sound, breath and objects

### What the spells are for
Of 326 spells with titles in the table of contents:

| Purpose | Spells |
|---|---|
| Revelation, dreams, visions | 52 |
| Love and attraction | 41 |
| **Healing** (headache, fever, eyes, stings, cough, childbirth) | **33** |
| Protection | 27 |
| Binding and restraint | 16 |
| Success and favour | 13 |
| Sleep | 9 |
| Power over objects or nature (invisibility, opening doors, release from bonds) | 5 |
| Ascent and immortality | 2 |

### Sound and breath are written into the instructions

| Instruction | Occurrences |
|---|---|
| sing, chant, hymn | 127 |
| pop or smack | 45 |
| facing a direction | 24 |
| silence | 23 |
| hiss | 18 |
| the vowels named | 12 |
| bellow, roar | 9 |
| draw in breath | 7 |
| an instrument | 7 |

The four most explicit passages:

1. **Breath that lifts** (the "Mithras Liturgy", PGM IV): "Draw in breath from the rays, drawing up 3 times as much as you can, and you will see yourself being lifted up and ascending to the height, so that you seem to be in midair."
2. **Hiss and pop** (same text): "Silence! Silence! … Then make a long hissing sound, next make a popping sound."
3. **The crocodile's breath** (PGM XIII, the "Eighth Book of Moses"): the popping noise is the sound of the falcon-faced crocodile which, "coming up to breathe from the deep, … goes 'Pop, pop, pop'" at the four turning points of the year.
4. **Vowels to be eaten** (PGM XIII): "the seven vowels are written on the gold lamella to be licked off, and on the silver lamella … for the phylactery."

**Reading.**
- The breath passage gives a procedure: three maximal inhalations. Over-breathing changes blood carbon dioxide and can produce light-headedness and a sense of rising. In its own words the text reports a felt lifting, "so that you *seem* to be in midair".
- The pop is tied to an animal's breath and to the solstices and equinoxes, so in the text's own logic the sound is a calendar signal and a breath-sign.
- Licking vowels off gold takes the sound into the body.

### The square of vowels (PGM XIII)
For each of seven directions the speaker faces that way and sounds all seven vowels in alphabet order, the first once, the second twice, up to seven times:

| Direction | Starts on | Sequence |
|---|---|---|
| Dawn (east) | A | A EE ĒĒĒ IIII OOOOO YYYYYY ŌŌŌŌŌŌŌ |
| South | I | I OO YYY ŌŌŌŌ AAAAA EEEEEE ĒĒĒĒĒĒĒ |
| West | Ē | Ē II OOO YYYY ŌŌŌŌŌ AAAAAA EEEEEEE |
| North | Ō | Ō AA EEE ĒĒĒĒ IIIII OOOOOO YYYYYYY |
| Earth | E | E ĒĒ III OOOO YYYYY ŌŌŌŌŌŌ AAAAAAA |
| Sky | Y | Y ŌŌ AAA EEEE ĒĒĒĒĒ IIIIII OOOOOOO |
| Cosmos | O | O YY ŌŌŌ AAAA EEEEE ĒĒĒĒĒĒ IIIIIII |

- **Measured:** every direction starts on a different vowel, so all seven possible starting points are used exactly once. It is a complete 7 × 7 rotation square (in mathematical terms, a cyclic Latin square) of 196 vowel sounds. The rows are reconstructed from the scan and checked against the alphabet order; the scan's text layer loses the long-vowel marks.
- **The text's stated effect:** "If I say it complete, there will be an earthquake, the sun will stop and the moon will be afraid and the rocks and the mountains and the sea and the rivers and every liquid will be petrified; the whole cosmos will be thrown into confusion."
- **Reading.** This is the most structured sound instruction in all our material. It maps the seven vowels onto the seven directions of space (four compass points, earth, sky, the whole), each as a rising triangle of repetitions. In sound it is a programme of 196 sustained vowels with a different overtone emphasis in each (compare our E3 measurement), performed while turning through space.

### The magical words are built as mirrors
Measured in Greek letters (θ, φ, χ, ψ count as one letter):

| Word | Reads the same backwards | Occurrences |
|---|---|---|
| ABLANATHANALBA | yes | 16 |
| BAINCHŌŌŌCHŌŌŌCHNIAB | yes | 1 |
| THATHABATHATH | yes | 1 |
| ARARACHARARA | yes | 2 |
| ZŌTHAXATHŌZ | yes | 1 |
| EIOYŌŌYOIE (vowel string) | yes | 1 |

- **Vowel strings:** 298 occurrences, 187 distinct. Seven-letter strings are the third most common length (49). The alphabet order AEĒIOYŌ appears 21 times; reversed, once.
- **Reading.** A palindrome sounds the same played forwards or backwards. The ring structures measured in John's Gospel are the same idea at the scale of a book; the magical names are rings at the scale of a word.

### Number codes stated in the spells
| Stated in the text | Check |
|---|---|
| "your most great name, of which the number is **9,999**" (PGM II) | stated |
| "the name that consists of **100 letters**", inscribed on a silver leaf with a bronze stylus (PGM I) | stated |
| a pebble "numbered **3663**" clasped to the breast (PGM IV) | **BAINCHŌŌŌCH = 3663** (computed) |
| **Abrasax**, **Meithras** and **Neilos** (the Nile) | **all three = 365**, the days of the year |

- **Control:** a random magical-style word of 5–9 letters totals exactly 365 with probability about 0.0009. Three names hitting it is design, not chance.
- **Reading.** The year-number is built into the names of the year-gods and of the river whose flood made the Egyptian year. A name is spoken as sound and counted as a calendar at once.

---

## 2. The Testament of Solomon: a catalogue of remedies, with its codes stated outright

### The ring and its seal
- Solomon receives from the archangel Michael a ring "having a seal engraved on precious stone". McCown's Greek: *Ἡ δὲ γλυφὴ τῆς σφραγίδος τοῦ δακτυλιδίου … ἐστὶν πεντάλφα*, "the engraving of the seal of the ring is a pentalpha" (a five-pointed star).
- One manuscript writes out what the seal says: an invocation, *kyrie ho theos hēmōn … leōn … Sabaōth … Elōi*, interleaved with vowel strings such as *aee*, *aioo*, *aeniou*.
- **The recipe for making the ring** (a manuscript variant McCown prints, p. 254): "Concerning the ring: taking **virgin wax**, make the ring … to wear on the **right finger** of your hand. Wrapping it in **virgin paper**, inscribe **with the pen of the art** these **twelve names**: *leōn, sabaōth, biōnia, elōi, aōa, iaō, iasou, souieōa, aeniou, ou, ouniou, iou, irō*."
- **Measured:** the twelve names are **78% vowels**, against **55%** in ordinary Greek (John's Gospel).
- Another manuscript speaks of "eleven seals which the angel gave with the **twelve stones**".
- **Reading.** The ring is a written vowel chant worn on the body. Its twelve stones match the twelve stones of the high priest's breastplate (Exodus 28), the object that carried the Urim and Thummim.

### The 36 decans: illnesses and their exact cures (chapter 18)
33 of the 36 are preserved well enough to parse. Each names the illness it causes and what drives it out.

| Mode of remedy | Decans |
|---|---|
| A spoken formula only ("let me only hear the words, 'Michael, imprison Ruax,' and at once I retreat") | 15 |
| A written name (on paper, laurel leaves or a tin plate) | 12 |
| An object or material (laurel, salt, oil, coriander, wine, bone) | 14 |
| An action (wash, sprinkle, smear, tie, throw) | 14 |

- **Measured order:** the first ten decans, which cause pain in the head, eyes, ears, throat, shoulders, heart and bowels, are cured by **the spoken formula alone**. From the eleventh on, the cures move to **written** names, then to **materials and actions**.
- What they attack: belly, kidneys and bowels 6; eyes and ears 5; heart and nerves 4; fevers 4; household strife 4; head 3; throat and chest 3.
- **Reading.** The list runs from voice, to writing, to matter: the same three levels as the rest of this investigation. The first and simplest cures are sound alone.

### Numbers checked against the Greek
| The text says | Computed |
|---|---|
| God's name "whose number is χμδ′ (644) … among the Greeks Emmanuel" (6.8; McCown's Greek *οὗ ἡ ψῆφος χμδ᾽*) | Ἐμμανουήλ = **644** ✓ |
| The angel Afarot, "which is interpreted Raphael … Of this name the number is 640" | Ῥαφαήλ = **640** ✓ |
| The Saviour: "a man whose number, if any one shall write it on his forehead, he will defeat me" | Ἰησοῦς = 888 (the text does not state the number) |

The author computed these values correctly. Conybeare's English ("a row of numbers") hides that the Greek states the number in Greek numerals.

### Matter and force: the lifted stone and the pillar of air
- The spirit **Ephippas** is caught in a **wineskin** (*askos*). "The skin rose and stood on its feet, **inflated**", walked seven steps and bowed.
- Ephippas then offers: "I can **lift the cornerstone which men and demons rejected** and set it at the head of the corner". The stone is carried "up the steps" and laid at the entrance of the temple.
- Solomon: "**Truly now the scripture is fulfilled: 'the stone which the builders rejected, this has become the head of the corner'.**"
- Ephippas and the demon of the Red Sea then raise a **pillar** "aloft from the earth", and swear to hold it "until the world's end".
- Solomon makes a demon **saw Theban marble**; other demons dig the temple's foundations.

**Reading, with the Greek.**
- The stone episode quotes Psalm 118:22 in the Septuagint's own words (*λίθον ὃν ἀπεδοκίμασαν οἱ οἰκοδομοῦντες*). The New Testament applies that verse to Christ (Mark 12:10, Acts 4:11, 1 Peter 2:7).
- The agent that lifts the stone is a **pneuma**, which in Greek means both spirit and wind, sealed in a skin and seen "inflated". The text pictures the lifting as done by wind held in a bag, the same image as the bag of winds Aeolus gives Odysseus (*Odyssey* 10).
- The episode is a literal enactment of a prophecy about a rejected stone being set in place. In the text's own frame, that is the code it points to.

### Cross-links between the texts
| Link | Where |
|---|---|
| Fish liver and gall burned against the demon Asmodeus | Testament of Solomon 5 = Tobit 6 and 8 (both name Asmodeus) |
| Twelve stones with the ring's seals | Testament of Solomon (manuscript variant) ~ the breastplate's twelve stones, Exodus 28 |
| Solomon's ring and incantations used to heal | Testament of Solomon ~ Josephus, *Antiquities* 8.45–49 (Eleazar) |
| Vowel strings on a ring or leaf worn on the body | Testament ring recipe ~ PGM XIII gold and silver lamellae |
| The cornerstone lifted into place | Testament of Solomon 22–23 ~ Psalm 118:22 ~ Mark 12:10, 1 Peter 2:7 |

---

## 3. Letter-number codes in the biblical instrument texts

Values: Hebrew alef = 1 … tav = 400; Greek alpha = 1 … omega = 800.

| Code | Values | Note |
|---|---|---|
| **Serpent = Messiah** | *nachash* נחש = *mashiach* משיח = **358** | John 3:14 makes the same link in words: "as Moses lifted up the serpent … so must the Son of Man be lifted up" |
| **Ark = Urim** | *aron* ארון = *urim* אורים = **257** | the two oracle objects of the sanctuary |
| **Love = One** | *ahavah* = *echad* = **13**; together they equal YHWH (**26**) | a long-noted equivalence |
| **Amen = YHWH + Adonai** | 91 = 26 + 65 | a long-noted equivalence; Greek *amēn* = **99**, the number early Christian papyri write for "amen" |
| **Voice + ark = silver trumpet** | *qol* 136 + *aron* 257 = *chatsotsrah* 393 | |
| **Bells + life = serpent / Messiah** | *pa'amonim* 290 + *chayyim* 68 = 358 | |

**Chance control:**
- The Hebrew Bible has 39,953 distinct written word forms spread over 1,191 values, so on average **34 words share any given value**.
- Among 30 terms drawn at random from the Bible, equal pairs average **0.6**. Here there are **3** (excluding *ruach*/*revach*, which are spelled identically), which chance gives about 1–2% of the time.
- **But I chose these terms, and included pairs the tradition had already noticed,** so the true rate is less impressive than that number suggests.
- Sums of the form A + B = C occur 12 times here, against 8 expected: **at chance**.

**Verdict on codes:**
- The number codes the texts **state themselves** are real and deliberate: 644 Emmanuel, 640 Raphael, 365 Abrasax/Meithras/Neilos, 3663 Bainchōōōch, 9,999, the 100-letter name.
- Codes **found by searching** among biblical terms are mostly at chance level, except a few traditional equalities, which may well have been noticed and valued in antiquity.

---

## 4. What these instructions have in common

| Element | Where it appears |
|---|---|
| **Vowels** sustained, repeated, arranged in squares and triangles, written on metal and worn or eaten | PGM XIII square; seven-vowel hymn (Demetrius); ring names (78% vowels); lamellae |
| **Breath** drawn in, hissed, popped; spirit = wind | Mithras Liturgy; crocodile's pop; Ephippas in the wineskin; 1 Samuel 16:23 *revach*; YHWH as breath-letters |
| **Number** built into names | 365, 644, 640, 3663, 9,999 |
| **Mirror form** | palindromic names; ring structures in John |
| **Voice first, then writing, then matter** | the decans' cures; *Sefer Yetzirah* "carved with voice, hewn with breath"; Genesis's ten sayings |
| **Objects that carry the sound** | the ring and its seal, gold and silver leaves, the breastplate's twelve stones, the bells "that he die not" |

## 5. Next steps
1. **E6, breath (with safety screening):** the Mithras Liturgy's "three maximal breaths". Measure breathing, the sensation of lifting, and heart rate; a fit, supervised volunteer group only.
2. **E7, the vowel square:** render the 7 × 7 square, measure its overtone content direction by direction, and test listeners.
3. Add the Preisendanz Greek text of the papyri if a copy can be obtained, to check the vowel squares and numbers letter by letter.
4. Bring in the *Sepher ha-Razim*, the *Sword of Moses* and the Coptic magical papyri, which continue these traditions.
