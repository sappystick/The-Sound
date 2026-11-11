# Words of power, round 5 (round 41): the simulator, the decoded notes and the instrument

**What this round does:**
- Every power word is run through a range of mouths and pitches, in every room from round 40.
- It is run in each language it exists in: the original wording, and its translations.
- The words are then decoded into notes by two ancient Greek systems, and an instrument is specified to play them.

**Three layers, kept apart so that none is passed off as another:**
- **P (physics):** what a mouth and a room measurably do.
- **T (theory):** each ancient theory's own criterion, applied as the theory states it. This is not physics.
- **D (decoding):** text turned into notes by the ancient systems, and the instrument that plays them.

**Files:**
- script `power/round41_power_sim.py`;
- numbers `power/round41_results.json`;
- audio `power/audio/r41_*.mp3`.

## P. The simulator: which language is physically strongest?
**The model:**
- Each variant's phonemes go through a source-filter voice model: harmonics shaped by formants F1–F3.
- **Grid:** 4 vocal-tract lengths (13 cm child, 15 cm woman, 17.5 cm man, 19 cm large man), 8 pitches (80–300 Hz) and the 7 rooms of round 40.
- **Metrics:**
  - continuity (voiced share);
  - overtone salience: how strongly one harmonic dominates the F2 band, which is the hidden-melody strength;
  - body vibration: the share of energy below 300 Hz;
  - room coupling.
- **Physical index:** the mean z-score of the metrics, each at the variant's best mouth and room. Equal weights are a choice.

**Ranking within each meaning** (physical index; higher = physically stronger):

| Meaning | Ranking |
|---|---|
| I am | Greek Koine ἐγώ εἰμι +0.42 · English +0.36 · Latin +0.30 · Hebrew *ani hu* +0.20 · Attic +0.13 · Hebrew *ehyeh* +0.07 · Aramaic *ana hu* −0.17 · Coptic −0.28 |
| Ablanathanalba | Greek name +0.26 · proposed Aramaic *ab lana atta* −0.11 |
| Talitha koum | Greek translation +0.05 · Aramaic −0.14 |
| Ephphatha | Greek translation −0.15 · Greek transliteration −0.51 · Aramaic −0.62 |
| Abba | Aramaic +0.28 · Greek ὁ πατήρ −0.42 |
| Amen | Greek +0.22 · Hebrew +0.14 |
| Holy ×3 | Hebrew +0.09 · Greek 0.00 |
| Let there be light | Hebrew −0.03 · Greek −0.12 |

**Result (Calc).**
- **Originals against translations:** the original beats its translation in 3 of 7 pairs (sign test p = 0.77, I am a tie).
- **By language,** English and Latin come top. This is an artefact of a small sample, but it makes the point: **no language is acoustically the most powerful**.
- **Against the ancient claim (N, physics):** a sacred word does not lose physical sound strength when it is translated. Origen and Iamblichus held that it loses its power (POWER.md); whatever power they meant, it is not in the acoustics.
- **The best mouth** is always a long vocal tract at a high pitch (220 Hz). This is how the salience metric behaves, not a discovery.

**Room coupling stops discriminating.** At each variant's best mouth it reached 1.0 for everything. Above a room's **Schroeder frequency** its resonances overlap, so any pitch couples:

| Space | Schroeder frequency | Meaning |
|---|---|---|
| Galilean synagogue hall | 57 Hz | pitch never matters |
| Solomon's Holy Place | 92 Hz | pitch hardly matters |
| Solomon's Holy of Holies | 130 Hz | matters only for low voices |
| Tabernacle's Holy of Holies | 233 Hz | matters across the male range |
| King's Chamber | **274 Hz** | **the chosen note matters across the whole male singing range** |
| Queen's Chamber | 312 Hz | matters throughout |
| Rock-cut tomb | 577 Hz | the voice is always in the modal range |

**Reading:** in large halls the room accepts any note. In the King's Chamber and in small stone tombs the room selects: some notes ring and others die. These are the spaces where "finding the note" is physically real.

## T. The ancient theories' own criteria (not physics)
- **Nicomachus's planetary vowels.** Only the seven-vowel hymn uses all seven planets. Ablanathanalba, Abrasax and Aramaic *ana hu* use only the Moon (α). The Greek "I am" uses Mars, Mercury and the Sun.
- **Sefer Yetzirah's mother letters.** Hebrew *amen* (אמן) is 2/3 mothers, aleph and mem, "air and water", the highest share of any word. Hebrew *ani hu* has 1/3. (**Reading**; the letter-class test of round 39 found no general effect.)
- **Pythagorean consonance.** The steps of the overtone melodies are rarely simple ratios: 0–0.5 per word, mostly 0 (**N**).
- **Letter-number values:**
  - ἐγὼ εἰμι = 873;
  - Abrasax = 365;
  - ΙΑΩ = 811;
  - the seven vowels = 1,294;
  - Hebrew אמן = 91 (7 × 13);
  - Hebrew *ani hu* = 73;
  - Holy ×3 = 1,230.

## D. Decoding the words into notes
**Two ancient systems:**
- **D1, Nicomachus** (*Harmonic Manual*; *Excerpta* 6). The seven vowels are the seven planets and the seven strings of the lyre: ω Saturn = hypate (lowest) … α Moon = nete (highest). Pythagorean heptachord, with mese = 220 Hz. The ancient absolute pitch is unknown, so everything can be transposed.
- **D2, Alypius's vocal notation, Lydian key.** This is an **approximate reconstruction**. The alphabet descends in triplets, each a note and its two raised forms (quarter tones), with ι = mese. The exact pitches should be checked against Pöhlmann & West (2001).

| Word | Nicomachus (planets) | Alypius, Lydian |
|---|---|---|
| **Seven vowels** αεηιουω | **D4 C4 B♭3 A3 G3 F3 E3**: the whole lyre, Moon to Saturn, in alphabet order | C♯4 C4 B♭3 A3 F3 D3+ C3 |
| **Ablanathanalba** | **D4 ×6**: one note, the Moon string, throughout | **C♯4 C4+ G3+ C♯4 F♯3 C♯4 A3+ C♯4 F♯3 C♯4 G3+ C4+ C♯4**: a palindromic melody returning six times to α (C♯4) |
| **I am** ἐγὼ εἰμι | **C4 E3 C4 A3 A3**: Mercury, Saturn, Mercury, then **the Sun twice: it ends on the mese** | C4− C4 C3 C4− **A3** G3 **A3**: it ends on ι = mese |
| ΙΑΩ | A3 D4 E3: Sun, Moon, Saturn (the centre, the top and the bottom of the lyre) | A3 C♯4 C3 |
| Abrasax | D4 ×3 | C♯4 C4+ F3− C♯4 E3 C♯4 F3+ |

**What the decoding shows:**
- **In Nicomachus's system the seven-vowel hymn is the scale itself.** Sung in alphabet order, the vowels play every string of the lyre from the Moon down to Saturn. The hymn is a descent through the heavens in one sweep (Calc; **Reading**: a planetary scale sung as vowels).
- **Ablanathanalba is a reciting tone with neighbour notes.**
  - In Alypius's notation it repeatedly leaves and returns to one central note, and reads the same in pitch forwards and backwards. That pitch palindrome follows from any letter palindrome.
  - In Nicomachus's system it is a single held note on the Moon string.
  - Either way, it is chant structure, not a melody that wanders.
- **"I am" comes to rest on the mese.** The mese is the lyre's central string, its "leader" in the Aristotelian *Problems* (19.20), and in Nicomachus it is the Sun.
  - In Nicomachus's system this follows from the source: ι is the Sun, which is the mese.
  - In Alypius's notation ι = mese was the anchor chosen for the reconstruction, so there it is a consequence of that choice, not a discovery.
  - **Reading:** the word of divine self-naming resolves on the centre and governing string.

**Speculative (D3; there is no ancient rule mapping numbers to Hz).** Taken as hertz and folded into one octave:
- 873 for ἐγὼ εἰμι → 218 Hz, 14 cents from the mese (A3);
- Abrasax 365 → F♯3;
- ΙΑΩ 811 → G♯3;
- Ablanathanalba 179 → F3.

With five words, a chance landing within 15 cents of one chosen note is about 12%, so the "I am" result is a likely coincidence.

## The instrument
**1. A heptachord lyre tuned to the planetary vowels** (Pythagorean; lowest string 650 mm, same material and tension throughout):

| String | Vowel | Planet | Note | Length (mm) |
|---|---|---|---|---|
| hypate | ω | Saturn | E3, 165 Hz | 650.0 |
| parhypate | υ | Jupiter | F3, 173.8 Hz | 617.0 |
| lichanos | ο | Mars | G3, 195.6 Hz | 548.4 |
| mese | ι | Sun | A3, 220 Hz | 487.5 |
| trite | η | Venus | B♭3, 231.8 Hz | 462.7 |
| paranete | ε | Mercury | C4, 260.7 Hz | 411.3 |
| nete | α | Moon | D4, 293.3 Hz | 365.6 |

**2. Vowel pipes.**
- Each vowel gets a pair of stopped pipes tuned to its first two formants (length = c / 4f).
- Sounded together over a drone, a pair gives the colour of that vowel.
- Historical precedent: Kratzenstein (1779) built resonators that sounded the vowels.

| Vowel | F1 pipe (mm) | F2 pipe (mm) |
|---|---|---|
| a | 117 | 69 |
| ɛ | 156 | 46 |
| e | 214 | 41 |
| i | 318 | 37 |
| o | 191 | 107 |
| y | 318 | 46 |
| ɔ | 150 | 102 |

A set of 14 small pipes, blown in the order of a word's vowels over a drone, would "speak" its vowel line without a voice. For Ablanathanalba that means the a-pair six times.

**3. Renders**, on the lyre over a drone at the King's Chamber note (132 Hz):

| File | Content |
|---|---|
| `r41_seven_nicomachus.mp3` | the planetary descent |
| `r41_ablanathanalba_alypius_lydian.mp3` | the palindrome melody |
| `r41_ablanathanalba_nicomachus.mp3` | the Moon reciting tone |
| `r41_ego_eimi_alypius_lydian.mp3` | "I am", Alypius |
| `r41_ego_eimi_nicomachus.mp3` | "I am", Nicomachus |

## Beyond physics: how the spiritual claims can still be tested
The simulator settles the acoustic question: no wording is physically stronger because it is the original. Claims about power beyond acoustics cannot be measured by a sound model, but they can be tested on people:
- **E5 (live, `experiments/e5_app/`):** listeners judge original, translated and scrambled versions blind.
- **Physiological arm:**
  - heart-rate variability during 6-breaths-a-minute recitation (round 37, T4);
  - EEG during 110 Hz tones (Cook et al. 2008);
  - balance (sway) at 90+ dB in a small stone room (round 40).
  - In each case the original, a translation and a scrambled version are compared, with listeners and experimenters blind to which is which.
- **Ancient-theory arm:** score each word by the theories' own criteria (layer T), then check whether those scores predict any measured response.

A claimed power that survives blind comparison is a finding. One that disappears under blinding was carried by expectation and context. That is still a real effect on people, but a different one.

## Limits
- The voice model is idealised: formant targets, with no coarticulation.
- Aramaic, Coptic and Egyptian forms are hand-set phonemes.
- The physical index's weights are a choice.
- The Alypius table is approximate.
- Absolute ancient pitch is unknown, so all notes can be transposed.
