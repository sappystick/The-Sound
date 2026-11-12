# Words of power, round 8 (round 44): the hymn papyri, "I am" on the middle string, and the second reading

**Files:**
- script `power/round44_mese.py` (seed 44);
- numbers `power/round44_results.json`;
- audio `power/audio/r44_*.mp3`.

**New source:** *The Amherst Papyri* I (Grenfell & Hunt 1900, public domain), in `sources/texts/amherst/`.

Labels: **K** known · **Calc** · **N** negative · **O** open · **Reading**.

## 1. The tests set in round 43
| Test | Result | Label |
|---|---|---|
| **Sacred names under musical notes.** Are they written in full in hymns meant to be sung? | **P.Oxy. 1786:** θεοῦ (line 1), πατέρα, υἱόν, ἅγιον πνεῦμα (line 4) are all printed in full; no abbreviation is reported by the editors. This fits Fill 2: a notated text must spell every syllable. One papyrus only; the editors' printed text is the evidence, since the OCR of the plate is unusable. | **O**, supported in 1 of 1 |
| **The hymn openings.** Do early hymns open with a list of cosmic voices? | **P.Amh. 2** (4th c.) is an alphabetic acrostic of 25 lines, each with three parts beginning with the same letter. Its opening is lost. Its subject is baptism and life ("washed in the Jordan", "that thou mayst receive life"), not a cosmic choir. | **N** for Fill 3 in this hymn |
| **Accent as melody.** Was pitch-accent taking over Christian song? | **P.Amh. 2:** every part of every line ends on an accented second-last syllable. The editors write that "the tonic principle is already on the path of victory". P.Oxy. 1786 (late 3rd c.) still counts length, not accent. Between the two, Christian song moves from vowel length to accent, which supports building the round-43 score on the accent rule. | **K** |
| **Berlin hymn** (BKT VI.vi.8) | Not openly available here | not run |
| **Ekphonetic lectionaries** (chant signs in later Gospel books) | No open digital corpus; Høeg 1935 and Wellesz 1966 are in copyright or borrow-only. The test (do sacred names attract lengthening signs?) is designed and needs a library or a digitised lectionary. | not run |

## 2. Syllable measurements of "I am" (ἐγὼ εἰμι)
**Where does "I am" fall in its verse, by syllables?**
- **Data:** all 24 cases in John.
- **Null:** every other word's position in the same verses.

| Measure | Result |
|---|---|
| Mean distance from the verse's syllable centre | 0.278, against 0.25 by chance |
| p (more central than chance) | 0.83 |
| Where they fall | 10 in the first quarter of the verse, 11 in the middle half, 3 in the last quarter |

**N:** "I am" does not sit at the centre of its verse; it tends to open it ("I am the light…", "I am the vine…").

**This does not touch earlier results:**
- the "I am" ring around the whole Gospel's centre (claim C2);
- the prologue's syllable centre at 1:12 (claim C1).

The middle of John is a book-level structure, not a sentence-level one.

**But the middle belongs to him (O, exploratory):**
- In John, μέσος ("in the middle") occurs 4 times, and **all 4 put Jesus in the middle**:
  - 1:26, "in the middle of you stands one whom you do not know";
  - 19:18, crucified "with Jesus in the middle";
  - 20:19 and 20:26, he "came and stood in the middle".
- In the Synoptics, 5 of 26 do (Mt 18:20; Lk 2:46, 4:30, 22:27, 24:36).
- Fisher one-sided p = 0.0046.
- **Caveat:** the pattern was noticed in the output and then tested, and the labels are hand-set (listed in `round44_results.json`).
- **Reading:** in John's narrative, as on the lyre, the middle place, the *mese*, is reserved for one figure.

## 3. The combined instrument, tuned so that "I am" rests on the middle string
**The design (Calc):**
- **Strings:** seven gut strings, at the round-41 lengths (650 → 366 mm), with the mese at 220 Hz (A3).
- **Tubes:** the soundbox opens into one of seven vowel tubes, the round-42 three-section resonators, selected by a lever. Alternatively, a tube is held in the player's mouth, like a talk-box.
- **In Clement's terms:**
  - the strings are the lyre (harmony);
  - the tube is the aulos (breath);
  - the body and the room are the temple.

**How it plays a word:** for each syllable, pluck the string of its vowel (Nicomachus), open that vowel's tube, and hold it for the syllable's length.

**ἐγὼ εἰμι on the instrument:**

| Syllable | Vowel | String | Planet | Hz | Beats |
|---|---|---|---|---|---|
| ɛ | ε | paranete | Mercury | 260.7 | 1 |
| ɣo | ο (Koine ω = o) | lichanos | Mars | 195.6 | 1 |
| iː | ει = ι | **mese** | **Sun** | **220** | 2 |
| mi | ι | **mese** | **Sun** | **220** | 1 |

- **"I am" ends on the middle string, held, then repeated.**
- This follows from the ancient sources, not from our tuning. In Nicomachus ι is the Sun, and the Sun is the mese. In Koine, ει had become ι, so "I am" (eimi) is sounded *i-mi*, two syllables on the Sun string.
- **The mese's role:** in the Aristotelian *Problems* (19.20), the mese is the "leader" of the strings, and every other string is tuned from it.
- **Reading:** the divine self-naming is the note the instrument is tuned from.

**John 1:1a** (Ἐν ἀρχῇ ἦν ὁ λόγος) on the same instrument runs:
- Mercury → Moon (the highest string) → Venus, held → Venus, held → Mars ×3;
- so "the Logos" sits on one string, ο ο ο.

**Renders,** in the Holy of Holies' acoustic:
- `r44_lyre_tubes_ego_eimi.mp3`;
- `r44_lyre_tubes_john_1_1a.mp3`.

## 4. "If the texts were mistranslated, how could this take shape?" A second reading
Several of John's key words also carry technical senses from Greek harmonics and philosophy. These senses are attested in the period, and a reader like Clement heard them. The senses are not mistranslations: they are a second register that English has to choose against.

| Word | Usual translation | Technical sense (attestation) | Rate per 10,000 words: John / Mt / Mk / Lk |
|---|---|---|---|
| λόγος | word | **ratio, proportion** (Euclid, *Elements* V def. 3; *Sectio Canonis*; Plato, *Timaeus* 31c–32c) | **25.9** / 18.0 / 21.3 / 17.0 |
| ἀρχή | beginning | **first principle** (Aristotle, *Metaphysics* 5.1) | **5.2** / 2.2 / 3.5 / 1.5 |
| φωνή | voice | **sound, a pitched sound** (Aristoxenus 1.3; *Timaeus* 67b) | **9.7** / 3.8 / 6.2 / 7.2 |
| πνεῦμα | spirit | **breath, the air of the aulos** (Clement, *Protrepticus* 1.5) | 15.5 / 10.4 / 20.4 / 18.5 |
| μέσος | middle | **the mese**, the governing string ([Aristotle], *Problems* 19.20) | 2.6 / 3.8 / 4.4 / 7.2 |

**Calc:** John uses ratio-word, principle-word and sound-word more than any Synoptic. Breath-word and middle-word he uses less (though his middle always holds Jesus, section 2).

**John 1:1–5 heard in the technical register (Reading):**

> In the first principle was the Ratio, and the Ratio was toward God, and the Ratio was God. This was in the first principle toward God. All things came to be through it, and without it not one thing came to be. What came to be in it was life, and the life was the light of men; and the light shines in the darkness, and the darkness did not seize it.

**How this register fits the rest of the project:**
- **Clement hears exactly this.** For him the Logos is the one who tunes the cosmos by ratios, "from the middle to the ends and from the ends to the middle" (round 43).
- **It meets the earlier findings:**
  - the prologue's measured syllable centre at 1:12 (claim C1);
  - the ring of "I am" sayings around the Gospel's centre (claim C2);
  - the Gospel's middle being held by one figure (section 2).

**Where it would become a mistranslation:** φαίνει means "shines". Rendering it "sounds", so that "the light *sounds* in the darkness", would be an error. No such sense is attested. Every technical sense used above has an ancient attestation in the table. That is the line between a hidden register and an invented one.

## 5. The picture after round 44
| Element | Status |
|---|---|
| The page records syllables and vowel length; the reader supplies the pitch through the accents | K, measured in round 43 |
| When a text was set to notes, sacred names were written in full, since every syllable needed a note | O, 1 of 1 hymn |
| Christian song was moving from vowel length to accent (P.Amh. 2) | K |
| The instrument has seven strings tuned by ratio (λόγος), with tubes for breath (πνεῦμα) and a body or room as temple (Clement) | K for the texts; Calc for the build |
| "I am" rests on the mese, the Sun string that every other string is tuned from | follows from Nicomachus and Koine pronunciation |
| In John's story the middle place always holds Jesus | O, p = 0.0046, post hoc |
| "I am" at the centre of its own verse | **N** |

**Next tests:**
1. Pre-register the "Jesus in the middle" test, with the labels fixed in advance, on 1 John, Revelation (ἐν μέσῳ τῶν λυχνιῶν, 1:13; "the Lamb in the middle of the throne", 5:6, 7:17) and Ignatius.
2. Digitise one early ekphonetic lectionary, for example from a library's open images, to run the sacred-names test.
3. A blind listening test of the instrument's "I am" against a version mistuned so that the mese is a different string.
