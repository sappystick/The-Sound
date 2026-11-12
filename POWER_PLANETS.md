# Round 59: the last construction pieces, and the speaking planet organ

**Files:**
- script `power/round59_speaking_planets.py` (seed 59);
- numbers `power/round59_results.json`;
- audio `power/audio/r59_*.mp3`.

**New source checked this round:** Pliny, *Natural History* 2.84 (Latin, in the repo): the Pythagorean intervals between the planets.

## 1. The remaining pieces, added
| Piece | Text | Calc / role |
|---|---|---|
| Tabernacle bars | 5 per side; the middle one runs end to end (Exod 26:26–29) | the frame's tie-rods; the middle bar rings at 131–187 Hz (round 58) |
| Entrance screen (5 pillars), veil (4 pillars) | gold hooks; bronze and silver sockets (26:32–37) | the outer and inner baffles |
| **Court, 60 pillars** | 20 + 20 + 10 + (3 + 3 + 4) (27:9–19) | pillars 5 cubits apart; the court is a picket of 60 posts |
| **Laver of bronze mirrors** | from the mirrors of the women who served at the entrance (38:8) | thin polished bronze: a cymbal or bell metal |
| **Anointing oil** | myrrh 500, cinnamon 250, calamus 250, cassia 500 shekels (30:23–24) | **2 : 1 : 1 : 2, octave ratios** (Reading) |
| **Incense** | four spices, "an equal part of each" (30:34) | **1 : 1 : 1 : 1, unison** (Reading) |
| Ephod's shoulder stones | two onyx stones, six names on each (28:9–10) | 6 + 6: the 12 notes as two hexachords |
| Breastpiece | a span square, doubled; 4 rows of 3 (28:15–21) | the 12-note display |
| Gold plate, "Holy to the LORD" | on the turban (28:36) | the name written on the player (compare the War Scroll's inscribed trumpets) |
| **Solomon's ten stands and lavers** | 4 × 4 × 3 cubits on 1.5-cubit wheels; lavers of 4 cubits, 40 baths (1 Kgs 7:27–39) | ten bronze bowls: a set of ten (compare the *magrepha*'s ten holes) |
| **Solomon's doors** | inner sanctuary: lintel and posts "**a fifth**"; nave: posts "**a fourth**" (6:31–33) | the Hebrew ordinals; the musical fifth and fourth share the names by coincidence (Reading) |
| Windows | recessed frames (6:4) | the sound holes |
| **Ezekiel's six gates** | each 50 × 25, three chambers each side, each one rod (6 long cubits) square (40:6–37) | **36 cells, each 55 Hz (A1)**: the same A as the lowest side chamber |
| 30 pavement chambers; kitchens 40 × 30 | (40:17; 46:21–24) | 40 : 30 = 4 : 3, a fourth |
| The east gate shut | "this gate shall be shut … for the LORD has entered by it" (44:1–2) | the stopped pipe (sounds an octave below an open one) |
| **Joshua's seven shofars** | 7 priests, 7 days, 13 circuits, the long blast and the shout (Josh 6) | the horn section (round 40: sound cannot topple walls) |
| **Gideon's trumpets and jars** | 300 trumpets; jars smashed (Judg 7:16–20) | breaking pottery = impulses that wake every resonance (round 40) |
| Miriam's drum | the *tof* (Exod 15:20) | the frame drum |
| **David's 4,000** | "with the instruments I made for praise" (1 Chr 23:5) | the full ensemble |
| **Herod's temple** | a 100-cubit cube house; **15 semicircular steps where the Levites sang** (Middot 2:5; 4:6); **a golden vine over the entrance** (Josephus, *War* 5.210) | the 15 steps = the 15 Songs of Ascents. The golden vine = "**I am the true vine**" (John 15:1), the 7th saying of the ring (round 54) |

## 2. The speaking planet organ
**The idea:** each planet is a string with its own vowel. Played in the order of a word's vowels, the strings give the word's planetary melody and say its vowels.

**Two ancient tunings, both with the Sun 4th of 7.** Both are anchored here at Sun = 154.2 Hz, the ark's note.

| Planet | Vowel | Nicomachus (the lyre) | Pliny 2.84 (Pythagoras: tone, ½, ½, 1½, 1, ½, ½) |
|---|---|---|---|
| Moon | α | 205.6 Hz (top string) | 115.5 Hz (nearest the Earth, lowest) |
| Mercury | ε | 182.8 | 122.4 |
| Venus | η | 162.4 | 129.7 |
| **Sun** | **ι** | **154.2 (mese)** | **154.2** |
| Mars | ο | 137.1 | 173.1 |
| Jupiter | υ | 121.8 | 183.4 |
| Saturn | ω | 115.6 (lowest) | 194.3 |

**The two tunings run in opposite directions:**
- Pliny's pitches rise with distance from the Earth.
- Nicomachus's lyre puts Saturn lowest.
- Both keep the Sun in the middle.
- Pliny's whole span is "seven tones".

**How it plays:**
- Each syllable sounds its vowel's planet string with a **sustained (bowed or reed) source**, through that vowel's three-section tube (round 42).
- The formants glide for 50 ms between syllables.
- The consonants come from the speaking machine's devices: bursts, hiss and nasal tubes.
- Each note is held for its syllable's length.

**Does it speak?** A recogniser matched the spectral colour of every sounded vowel against the seven tube shapes:

| Text | Vowels | Recognised (with tubes) | Control (same strings, no tubes) |
|---|---|---|---|
| ἐγὼ εἰμι | 4 | 100% | 0% |
| John 1:1 | 23 | 100% | 0% |
| the seven vowels | 7 | 100% | 0% |
| *talitha koum* | 4 | 75% | 0% |
| "Lazarus, come out" | 7 | 100% | 0% |
| **All** | 90 | **97.8%** | **0%** (chance 14%) |

**Recogniser control:** steady vowels are identified 18 of 21 times.

**What this shows:**
- **Calc:** the instrument preserves the vowels. Through the tubes, every vowel stays distinct and identifiable. Without them, none is.
- The planet melody of a word is fixed by its vowels:
  - **ἐγὼ εἰμι = Mercury, Mars, Sun, Sun**, resting on the Sun string in both tunings.
  - **John 1:1** begins Mercury, Moon, Venus, Venus, Mars ×3.

**What it does not show:**
- **That listeners would understand it.** The recogniser knows the tube shapes, so this is a machine test of distinctness, not of human intelligibility. That needs a blind listening test, in the E5 style of round 37.
- **That the ancients built such a thing.** Talking-statue tubes (Lucian, Hippolytus), vowel hymns (PGM, Demetrius) and planet scales (Nicomachus, Pliny) are attested separately, never combined in one machine.

**Renders** (`power/audio/`):
- `r59_ego_eimi_nicomachus.mp3`, `r59_ego_eimi_pliny.mp3`;
- `r59_john_1_1_pliny.mp3`;
- `r59_seven_vowels_pliny.mp3`;
- `r59_talitha_koum_pliny.mp3`;
- `r59_lazarus_pliny.mp3`.
