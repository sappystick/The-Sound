# Words of power, round 7 (round 43): the papyrus as a score

**The question:** can the earliest unspaced Greek papyri be read as notes for an instrument, as a written format with several layers that could be both read and played?

**How this round builds the picture:**
- Collect the pieces that survive.
- Test what can be tested.
- Fill the gaps openly, each fill marked as a hypothesis with a way to check it.

**Files:**
- script `power/round43_papyrus_score.py` (seed 43);
- numbers `power/round43_results.json`;
- audio `power/audio/r43_*.mp3`.

**New sources:**

| Source | Where | Edition / licence |
|---|---|---|
| P.Oxy. 1786 | `sources/texts/oxyrhynchus/` | Grenfell & Hunt, *Oxyrhynchus Papyri* XV (1922), public domain |
| Berakhot 3b | `sources/texts/sefaria/` | Sefaria |
| Odes of Solomon | `sources/texts/odes_solomon/` | Harris 1909 and 1916, public domain |
| Clement, *Protrepticus* | existing First1KGreek | |

Labels: **K** known/attested · **Calc** calculated · **N** negative · **Fill** a gap filled by hypothesis.

## 1. The surviving pieces
### Piece 1. A real two-line Christian score, from the papyri's own city and century (K)
P.Oxy. 1786 is a hymn from Oxyrhynchus, late 3rd century, "by far the most ancient piece of Church music extant" (Grenfell & Hunt).
- **Layout:** each line of text has a line of notes written above it.
- **Notes:** the notes are Greek letters, eight of them, in Alypius's diatonic Hypolydian key.
- **Five further signs:**
  - a stroke above a note for a long note;
  - a curve below for a slur;
  - a rest sign whose length is set by marks (a double rest at the metrical breaks);
  - a colon, probably affecting time;
  - dots for the beat.
- **Content:** creation is called to sing: the stars must not keep silent, the rivers, "all the powers answering Amen, Amen", praise to Father, Son and Holy Spirit.
- **Gap-filling precedent:** the editors used the notes to measure a gap in the text. The notes show that line 5 lost seven syllables, the last three an anapaest. **Music was used to fill missing text.**

So a written format with several layers did exist: pitch (letters), duration (strokes), slurs, rests, beat (dots), and words.

### Piece 2. The instrument is named, and it is the human being (K)
Clement of Alexandria, *Protrepticus* 1.5 (Greek checked in this round), writing about 200 AD in Alexandria and reading John:
- **The cosmos as music:** the Logos "tuned the whole cosmos into harmony", blending fire and air "like Dorian with Lydian". Its song is "stretched from the middle to the ends and from the ends to the middle".
- **The human as the instrument:** "disregarding the lyre and kithara, lifeless instruments", the Logos tuned "this cosmos and the small cosmos, man, soul and body, by the Holy Spirit". It "sings to God on the many-voiced instrument (πολύφωνον ὄργανον), and sings to the instrument, man".
- **The lyric line, with Clement's own gloss:** "You are my lyre, my aulos and my temple": a lyre for the harmony, an aulos for the breath (πνεῦμα), a temple for the Word (λόγος).
- **The breathing instrument:** "the Lord made man a beautiful breathing instrument (ὄργανον ἔμπνουν) after his own image".

**Calc link:** Clement's three parts are the three parts of our physical model:
- the **source** (vocal folds; strings, "lyre");
- the **breath-driven tube** (vocal tract; "aulos");
- the **resonant room** ("temple").

The speaking machine of round 42 is an outside copy of what Clement says the Logos plays.

### Piece 3. A lyre played by wind (K, with physics)
- **The texts:**
  - Berakhot 3b: "A lyre hung over David's bed; at midnight the north wind came and blew on it, and it played by itself."
  - Odes of Solomon 6:1: "As the hand moves over the harp and the strings speak, so speaks in my members the Spirit of the Lord." Harris reads "hand"; other translators read "wind".
  - The Odes add "the harp of many notes" (7), "the harp of thy Holy Spirit" (14) and "His harp is in my hands" (26).
- **Calc:** wind across a string sheds vortices at about 0.2 × wind speed ÷ string diameter. These lock onto one of the string's harmonics, which is how an aeolian harp works.
  - On the planetary heptachord of round 41 (gut strings, 0.8 mm), a night wind of 1.5–8 m/s sounds harmonics 1–12.
  - At 3 m/s it sounds harmonics 3–5 of every string.
- **The link:** the wind plays the overtones of the strings. These belong to the same overtone series that the vowels brighten in the voice (rounds 38–41).
- **Reading:** "the Spirit (wind) plays the lyre" and "the vowel colours the voice" are, physically, the same act of bringing out the hidden harmonics.
- **Render:** `r43_aeolian_lyre_midnight.mp3`, the seven planetary strings played by a gusting midnight wind.

### Piece 4. The papyri are written in spoken syllables (K, verified)
When a scribe split a word at the end of a line, did the split fall where the spoken syllable breaks?

| Manuscript | Words split at a line end | At a syllable boundary | By chance |
|---|---|---|---|
| P66 | 998 | **95.6%** | 34.5% |
| P75 | 612 | **98.0%** | 35.0% |
| Sinaiticus (01) | 2,073 | **98.8%** | 35.3% |
| Vaticanus (03) | 1,595 | **97.9%** | 34.4% |

- **The result:** in every manuscript, the probability that this happened by chance is effectively zero.
- **What it means:** the unspaced line is built out of spoken syllables. The page is sound written down in syllable units, the same units that P.Oxy. 1786 gives one note each. The rule is known from ancient grammarians and papyrology (Turner); it is measured here on John.
- **An oddity:** P66 breaks the rule most often (4.4%). It is also the papyrus with the most corrections (round 39).

### Piece 5. The letters themselves are not a hidden melody (N)
In Greek vocal notation the notes are letters. So, reading each syllable's vowel letter as its note (Alypius, approximate table):

| Text | Stepwise share | Same syllables shuffled | z |
|---|---|---|---|
| John | 0.354 | 0.372 | −5.0 |
| Mark | 0.362 | 0.386 | −6.5 |
| Revelation | 0.336 | 0.364 | −8.8 |
| Psalms (LXX, sung) | 0.320 | 0.347 | −6.5 |
| Odes (LXX canticles, sung) | 0.319 | 0.353 | −6.8 |
| Genesis (LXX) | 0.403 | 0.404 | −0.2 |

- **Result:** the real letter-melodies are *less* smooth than chance. Greek tends to vary its vowels from syllable to syllable, which produces leaps.
- Sung texts (Psalms, canticles) behave like prose.
- **N:** the vowel letters do not carry a concealed tune. Ancient composers wrote the notes *above* the text (Piece 1) because the text alone does not hold them.

## 2. Filling the gaps: how the pieces fit
**Fill 1: the papyrus is a score with some layers written and some carried by the reader.**

| Layer | Where it lives | Status |
|---|---|---|
| syllables | written: the scribe's line divisions follow them (Piece 4) | measured |
| pitch | the accent system, the ancient melodic rule: pitch rises to the acute syllable, and a circumflex takes two notes. Usually unwritten in early papyri; supplied by the trained reader, or written above as in 1786 | K (Devine & Stephens 1994; West 1992) |
| duration | vowel length (η and ω long, ε and ο short), written into the spelling; 1786 adds the stroke | K |
| rests | the line and sense breaks; 1786 writes them as rest signs | K / Calc |
| sacred-name layer | P66 marks θεός etc. with a stroke above the letters | **Fill:** in 1786, the same city and century, the stroke above means *long*. A reader trained in both would hold the sacred names. *Test:* in notated Byzantine lectionaries (ekphonetic signs, from about the 8th century), do sacred names attract lengthening signs more than other words? |
| the instrument | Clement: the human being, as lyre, aulos and temple (Piece 2) | K |
| the room | the temple; the room's favoured note (rounds 40–41) | Calc |

**Fill 2: why the sacred names are abbreviated.** A notated hymn must write every syllable, because each syllable carries a note. P.Oxy. 1786 writes "Father, Son and Holy Spirit" out in full, letter by letter (as read by its editors). An abbreviated sacred name hides its syllables. So a text full of nomina sacra cannot be sung from the page without a reader who restores the sound.
- **Reading:** the abbreviation is a cue to *speak the name out*, not a hidden code. It assumes a voice.
- *Test:* check the other early Christian musical papyri. If sacred names are always written in full under notes, but abbreviated in reading texts, the cue reading gains support.

**Fill 3: the cosmic choir.** The hymn's surviving lines call on the stars, the rivers and "all the powers" (δυνάμεις, used of heavenly bodies, as the editors note) to sing.
- **The parallels:**
  - in Nicomachus (round 41), the seven planets *are* the seven vowels and the seven strings;
  - in Clement, the Logos tunes the cosmos and the human together;
  - in John 1:1–5, the Logos makes all things, "and the life was the light".
- **Fill:** the hymn's lost opening probably listed the cosmic voices one by one: heaven, the stars, the sea, the rivers. Its "powers answering Amen" is the planetary choir of Nicomachus sung in Christian form.
- *Test:* compare with the other early hymn papyri (P.Amh. 2; Berlin, *Klassikertexte* VI.vi.8). Do they also open with a list of cosmic voices?

## 3. The score of P66, John 1:1–5, in the layout of P.Oxy. 1786
**The rules:**
- **Pitch:** by the accent rule (accented syllable highest, the rise before it, the fall after it), with a cadence at the end.
- **Length:** by vowel quantity, marked with ¯ as in 1786.
- **Rests:** ‖ where P66's lines end.
- **Sacred names:** θν and θσ held double (Fill 1).
- **Note signs:** Alypius letters, approximate table: Γ = c4, Ι = a3, Μ = g3, Σ = e3.

The opening, notes above syllables:
```
Ι   Ι   ΓΙ¯  ΓΙ¯ Ι  Γ  Μ   Ι¯  Ι  Γ  Μ   ΓΙ¯ Ι    Ι    Ι¯  Γ¯ ‖
ɛn  ar  kʰe  en  o  lo ɣos kɛ  o  lo ɣos en  pros ton  tʰɛ on ‖
Ι¯  Ι¯  Γ¯   ΓΙ¯ Ι  Γ  Μ   ...
kɛ  tʰɛ os   en  o  lo ɣos ...
```
The full score is in `round43_results.json → D_score_P66_John_1_1_5`. Lining the P66 words up with the modern text is approximate after 1:3, because P66 writes ουδεν as one word.

**Renders, played by the round-42 speaking machine (reed and vowel tubes) in a synagogue-sized room:**

| File | Version |
|---|---|
| `r43_p66_john1_accent.mp3` | the accent-rule score |
| `r43_p66_john1_letters_as_notes.mp3` | the vowel letters read as notes (Piece 5's hypothesis, for comparison) |
| `r43_aeolian_lyre_midnight.mp3` | the self-playing lyre |

## 4. The picture so far
- **What the page records:**
  - **written:** syllables and vowel length;
  - **left to the reader:** pitch, held in the accents and the reader's training, and the full sound of the sacred names, which the page abbreviates;
  - **in the space:** the room.
- **Where notes appear:** in the papyri's own world, notes were added above the text when a hymn was to be sung (1786).
- **The instrument:** Christians of the period named it outright. It was the human being: strings for harmony, breath through a tube, a body as temple, tuned by the Spirit and played by the Logos (Clement). Their image of the Spirit playing a lyre is the physics of a wind-sounded string, and a wind-sounded string brings out the same overtones the vowels do.

**What is not supported:** the letters hide no melody (Piece 5). The "notes" of the text are its syllables, quantities and accents, not its alphabet.

**Next tests:**
1. Sacred names and lengthening signs in early ekphonetic lectionaries.
2. Whether sacred names are written in full under notes in the other Christian musical papyri.
3. The opening structure of the other hymn papyri.
4. A listening test: the accent-rule score against the letters-as-notes version (an E5-style blind comparison).
