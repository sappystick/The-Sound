# Round 56: the tabernacle and temple read as one instrument (thought experiment)

**The assumption, taken as true for this round:** the building instructions of Exodus 25–30 and 1 Kings 6–7 are a single design for a single instrument.

**Labels:** every part is given three ways:
- **Text:** what the instruction says (dimensions and materials).
- **Mapping:** the role it plays in the instrument. This is the speculative step.
- **Calc:** its acoustics, calculated from the stated dimensions (cubit 0.445 m).

**Files:**
- script `power/round56_tabernacle_instrument.py`;
- numbers `power/round56_results.json`;
- schematic **`power/round56_design.svg`**;
- audio **`power/audio/r56_tabernacle_instrument.mp3`** (62 s).

**New sources checked this round:**
- Josephus, *Antiquities* 3.291: the silver trumpets are "a little less than a cubit, a narrow tube slightly thicker than an aulos, ending in a bell".
- Bavli Zevachim 88b: **72 golden bells with 72 clappers** on the high priest's hem.

## The parts
| Part | Text | Mapping | Calc |
|---|---|---|---|
| **Court** | 100 × 50 cubits, linen hangings 5 high (Exod 27) | outer baffle and listening space | **3.85 Hz**, the base of the whole frame. Every length that divides 100 cubits is one of its harmonics |
| **Holy Place** | 20 × 10 × 10 (Exod 26, from the boards) | tuning chamber | 19.3 / 38.5 / 38.5 Hz = harmonics **5, 10, 10** |
| **Silver sockets** | 100, from 100 talents of silver | the feet: isolate the resonator from the ground | — |
| **Coverings** | 4 layers: linen, goat hair, rams' skins, *tachash* skins | the skin: damping, which sets how long the chamber rings | — |
| **Veil** | woven linen with cherubim, 10 × 10 | the diaphragm coupling the two chambers | — |
| **Holy of Holies** | a 10-cubit cube (Solomon's: 20) | the inner resonator | **38.5 Hz on all three axes** (Solomon's: 19.3); modes stack |
| **Ark** | acacia box 2.5 × 1.5 × 1.5, gold inside and out | the soundbox at the centre | **154.2 Hz** (and 257 Hz). Its length is ¼ of the tabernacle's Holy of Holies and ⅛ of Solomon's, so **it sounds exactly 2 and 3 octaves above the room it stands in** |
| **Mercy seat and two cherubim** | wings spread over the ark, faces toward each other. "**From between the two cherubim I will speak with you**" (Exod 25:22; Num 7:89) | the mouth: two wings forming a horn over the soundbox | mouth 1.1 m; efficient above **≈ 98 Hz**, the whole voice range |
| **Menorah** | beaten gold; one shaft, six branches, seven lamps | **the seven voices.** The centre shaft is the mese (Philo: the middle lamp is the Sun) | heptachord tuned with **mese = 154.2 Hz, the ark's note**: 115.6, 121.8, 137.0, **154.2**, 162.4, 182.7, 205.5 Hz |
| **Table of showbread** | 2 × 1 × 1.5; 12 loaves | the tuning standard. Its sides give the **octave, fifth and fourth**; its 12 loaves give 12 notes (Josephus's 12-note *nabla*) | the 12 notes of a Pythagorean cycle on 154.2 Hz |
| **Altar of incense** | 1 × 1 × 2 | the breath: the air supply | 385 / 193 Hz |
| **Altar of burnt offering** | 5 × 5 × 3, hollow, bronze, grating halfway down | the drum | 77 / 129 Hz. **N** as a "singing" heated tube: a mid-height grating does not drive the fundamental |
| **Bronze sea** | 10 cubits across, a handbreadth thick (1 Kgs 7:23–26) | the gong | ≈ 24 Hz lowest mode (order of magnitude only) |
| **Jachin and Boaz** | bronze, 18 high, 12 round, hollow, four fingers thick (1 Kgs 7:15; Jer 52:21) | the bass, flanking the entrance | struck: **≈ 118 Hz**; standing on a base: 18.6 Hz; ring mode ≈ 660 Hz; as air columns: 21 Hz |
| **Silver trumpets** | two; under a cubit, with a bell (Num 10; Josephus) | the signal voices | fundamental 204 Hz; playable partials ≈ 408–1,225 Hz |
| **Robe of the ephod** | golden bells and pomegranates; "**its sound shall be heard when he goes in**" (Exod 28:35); 72 bells (Zevachim 88b) | the shaker, sounded by the player's own steps | small bells, 2–5 kHz |
| **Breastpiece** | 12 stones in 4 rows; Urim and Thummim | the display: 12 outputs, one per note | — |

## What the design makes
**Assembled, the parts make a walk-in resonator, played by a person who enters it.**
1. **The frame.** The court, the Holy Place, the Holy of Holies and the ark are all harmonics of one base, 3.85 Hz (the court's length): harmonics 5, 10 and 40.
   - The building is a single harmonic series, nested room inside room.
   - Lengths of 1.5, 3, 28 and 30 cubits fall outside it; the frame is not perfect.
2. **The note.** The ark's length gives 154.2 Hz, exactly 2 octaves above the tabernacle's inner room and 3 above Solomon's. Tuned to it, the menorah's centre shaft becomes the mese, and the table supplies the octave, fifth and fourth to tune the rest.
3. **The voice.** The text names the output point itself: "from between the two cherubim". The cherubim's wings form a horn over a soundbox tuned to the room. A voice sung on the ark's note at that point would set every chamber's harmonic series ringing, and would seem to come from the mercy seat.
4. **The player.** The high priest enters with:
   - bells on his hem, "that its sound be heard";
   - the 12-stone breastpiece;
   - incense as breath.

   **The trumpets** signal from outside. **The bronze pillars and sea** are the bass and the gong at the threshold.

**In one sentence:** the design makes a **tuned, nested resonance chamber whose single note is the ark's**. In it a human voice becomes the voice "from between the cherubim", carried on the harmonic series of the whole building.

**What you hear** in `r56_tabernacle_instrument.mp3`, all in a 10-cubit-cube acoustic, over the building's harmonic series:

| Time | Sound |
|---|---|
| 0 s | two silver trumpets |
| 7.5 s | the 72 bells as the priest walks |
| 15 s | Jachin and Boaz struck |
| 21 s | the bronze sea |
| 25 s | the menorah's seven voices, Moon to Saturn |
| 34 s | the voice from between the cherubim: the vowel line of *ehyeh asher ehyeh*, on the ark's note, through the vowel tubes |

## Status
**What is calculated** (and true of the stated dimensions):
- the harmonic relations: the ark 2 and 3 octaves above its room;
- the rooms as harmonic series;
- the table's consonances;
- the pillars' and trumpets' pitches.

**What is mapping:** every role in the "Mapping" column. The texts present these as furniture for worship and as the place of God's presence, not as a sound device.

**Fits the texts:**
- sound is named at the two points that matter: the voice "from between the cherubim" and the bells "heard when he goes in";
- trumpets, cymbals, lyres and singers fill the later Temple (rounds 47–48).

**Does not prove:**
- That any of this was built or played as an instrument.
- That the harmonic relations are anything more than the result of using simple numbers: 2.5 divides 10 and 20 as any simple fraction would (round 55: simple ratios were a general building habit).

---

# Round 57: Ezekiel's temple and Noah's ark added, and the instrument made real
**Files:**
- script `power/round57_full_instrument.py`;
- numbers `power/round57_results.json`;
- audio **`power/audio/r57_ark_instrument.mp3`** (78 s).

**Texts checked this round:**
- Ezek 40:5 (the cubit "and a handbreadth"); 41:5–7; 43:2; 43:13–17; 47:3–5;
- Gen 6:14–16;
- Bavli Menachot 28b (the menorah 18 handbreadths high).

## 1. Noah's ark (Gen 6:14–16; common cubit)
| Calc | Value | Reading |
|---|---|---|
| Axes, 300 × 50 × 30 | 1.29 / 7.7 / 12.9 Hz = **harmonics 1, 6, 10** | one harmonic series, like the tabernacle |
| Three decks of 10 cubits | **38.5 Hz**, the same note as the tabernacle's Holy of Holies | the ark's decks and the inner sanctuary share their height |
| Sealed hull ("pitch inside and out") with one opening | a **Helmholtz resonator**, the bottle-mouth kind of resonance | a one-cubit square opening breathes at **0.14 Hz: one cycle every 7 s, the period of an ocean swell**; a one-cubit strip along the length breathes at 2.1 Hz |

**The frame:** 27 of 30 stated lengths divide 300 cubits, so most of the tabernacle, Solomon's temple and Noah's ark sit on one harmonic series of 1.29 Hz. **Weak evidence:** 300 = 2² × 3 × 5² absorbs most small numbers.

## 2. Ezekiel's temple (Ezek 40–47; long cubit 0.52 m)
- **Above hearing:** of the architecture, only a few parts sound in the hearing range, among them the altar hearth (12 cubits, 27.5 Hz) and the 6-cubit wall (55 Hz).
- **The halls are below hearing:** outer square 0.66 Hz; temple 3.3 Hz; nave 8.3 Hz; inner room 16.5 Hz.
- **The side chambers form a chord (Calc, with an inference).** They are 4 cubits wide at ground level and grow wider at each of three levels (41:5–7). Commentators infer 5 and 6.
  - Widths 4 : 5 : 6 resonate at **82.5, 66.0, 55.0 Hz = E2, C2, A1**: an **A-minor triad**, in tune to within 1, 15 and 1 cents.
  - The minor triad follows from the 4 : 5 : 6 widths.
  - The exact pitch of A depends on the 0.52 m cubit and is a coincidence.
- **The altar's steps:** 2, 4, 4 cubits, giving an octave and a unison.
- **The river:** its depth rises in four steps of 1,000 cubits (ankle, knee, waist, swimming), a four-stage crescendo.
- **The voice:** "with a roar like the roar of mighty waters" (43:2). Round 42 found that 10–30 voices together sound like rushing water.

## 3. Could it actually make an instrument? Yes: the furniture is already instrument-sized
**The buildings mostly resonate below hearing:** 0.7–40 Hz, apart from Ezekiel's side chambers (55–83 Hz). As instruments they are halls, which reinforce the notes sung or played inside them. **The furniture sits in the voice range.** Here it is, specified as a real, buildable ensemble:

| Part | Built as | Calculated specification |
|---|---|---|
| **Ark**, 1.11 × 0.67 × 0.67 m, acacia lined with gold | a **box zither**: seven gut strings over the lid (the mercy seat), on a 1.0 m speaking length | the box rings at **154, 257, 257, 300, 308, 363, 395, 401 Hz …** (46 modes below 1 kHz) |
| The seven strings | the heptachord, mese = the ark's own note | **A♯2 115.6 · B2 121.8 · C♯3 137.0 · D♯3 154.2 · E3 162.4 · F♯3 182.7 · G♯3 205.5 Hz**. Gut strings of 0.8–1.4 mm at 87–110 N each: ordinary lyre tensions |
| **Menorah**, 18 handbreadths (1.3–1.6 m) | **seven stopped pipes** on a wind chest | pipe lengths **0.73, 0.70, 0.62, 0.55, 0.52, 0.46, 0.41 m** (30 mm bore). They fit the lamp's height, centre pipe = mese |
| **Incense altar**, 0.45 × 0.45 × 0.89 m | bellows box / wind chest for the pipes | a portative organ; the water organ (*hydraulis*) existed from the 3rd c. BC |
| **Table**, 0.89 m | a monochord for tuning | open 154 Hz; stops at ½, ⅔, ¾ give 308, 231, 206 Hz (octave, fifth, fourth) |
| **Cherubim** | a horn over the lid | mouth 1.1 m, efficient above ≈ 98 Hz |
| Robe's 72 bells | a shaker worn by the player | 2–5 kHz |
| Two silver trumpets | signals | partials 408–1,021 Hz |

**What it would look like:** a gilded chest the size of a large cello case, strung across its lid, with two winged figures arching over it as a sound-horn. Beside it, a 1.5 m golden stand of seven pipes on a small bellows chest, and a long table with a single string for tuning. The player wears a bell-hemmed robe. The whole sits in a stone or curtained cube that reinforces the ark's note.

**What it would sound like:**
- a dark, resonant **box zither around D♯3 and a fourth either side**, with the box's own resonances (the octave above and the fifth above that) blooming under every pluck;
- a soft, hollow **seven-pipe drone** (stopped pipes give odd harmonics: a flute-like, clarinet-like colour);
- a shimmer of **bells**, and the bright trumpet calls.

**The rendered performance** (`r57_ark_instrument.mp3`), in the Holy of Holies' acoustic:

| Time | What plays |
|---|---|
| 0.5 s | **the table**: open string, octave, fifth, fourth (tuning by the canon) |
| 7 s | **the ark zither**: the seven strings, Moon to Saturn |
| 14 s | **the menorah pipes** hold the mese and the fourths. The strings play **"I am"** twice: Mercury – Mars – Sun – Sun |
| 25 s | **Ezekiel's chambers**: the A-minor drone, an octave up so it can be heard, rising in four river steps |
| 46 s | **"a roar like mighty waters"**: 60 voices through the vowel tubes, swelling with the breathing of Noah's ark |
| 50 s | **the 72 bells** |
| 66 s | **two silver trumpets** |

## Status
- **Calculated, and true of the texts' numbers:**
  - the ark's tone and its octave relation to its room;
  - Noah's ark as a single harmonic series, its decks sharing the inner sanctuary's height, and its 7-s Helmholtz breathing;
  - Ezekiel's chambers as a minor triad (the 5 and 6 inferred);
  - every string, pipe and box value above, which are physically realistic.
- **Mapping:** the roles. No text describes these objects as instruments.
- **What this shows:** read as a design, the instructions are physically buildable as a working ensemble, with realistic tensions and lengths, in the voice range. It does **not** show that they were meant or used that way.

---

# Round 58: the whole prologue on the ark instrument, and what was still missing
**Files:**
- script `power/round58_prologue_and_additions.py`;
- numbers `power/round58_results.json`;
- audio **`power/audio/r58_prologue_ark_instrument.mp3`** (3 min 54 s).

## 1. John 1:1–18 played on the ark instrument
**How it is played:**
- **Strings:** each of the prologue's **499 syllables** plucks the ark-zither string of its vowel, held for its length (short 0.3 s, long 0.6 s), and rings through the ark box's own resonances.
- **Pipes:** the menorah pipes hold the mese (154.2 Hz) throughout.
- **Breath:** pauses fall at the punctuation.
- **The centre:** at **1:12**, the prologue's measured syllable centre (claim C1), the pipes open to the fourth and fifth above.

**Strings played:**

| String | Times played |
|---|---|
| lichanos (Mars) | 181 |
| paranete (Mercury) | 117 |
| nete (Moon) | 88 |
| **mese (Sun, "I am")** | **55** |
| trite (Venus) | 47 |
| parhypate (Jupiter) | 11 |
| hypate (Saturn) | silent, because Koine ω = ο |

**Calc:** in performed time, **1:12 begins at 117.1 s of 233.5 s, 50.2% of the piece**. The prologue's syllable centre is also the centre of the performance.

**Verse start times (s):** 1:1 1.0 · 1:2 12.4 · 1:3 17.9 · 1:4 29.4 · 1:5 38.4 · 1:6 49.9 · 1:7 60.0 · 1:8 74.2 · 1:9 83.8 · 1:10 94.4 · 1:11 107.2 · **1:12 117.1** · 1:13 133.9 · 1:14 147.6 · 1:15 168.2 · 1:16 188.1 · 1:17 199.2 · 1:18 212.9

## 2. Construction texts added this round (checked on Sefaria)
| Text | What it gives | Calc / mapping |
|---|---|---|
| **1 Kgs 6:6**, Solomon's side chambers, **5, 6, 7 cubits wide (explicit)** | three stacked storeys | 77.1, 64.2, 55.1 Hz (D♯2, C2, A1). **The lowest (5 cubits) is exactly one octave below the ark's note.** Frequencies 42 : 35 : 30 make a minor third over a septimal minor third: a dark, narrow chord |
| **Exod 26:28**, "the centre bar halfway up the planks shall run from end to end" | one wooden bar through the whole tabernacle, 30 cubits (13.4 m) | its lowest ringing note is **131–187 Hz** (hardwood, 3,500–5,000 m/s along the grain): **the range of the ark zither** |
| **1 Kgs 7:49**, ten lampstands, five right and five left | 70 lamps | ten seven-pipe ranks: 70 pipes |
| **Zech 4:2**, "a lampstand all of gold … seven lamps … **seven pipes**" | the text itself says "pipes" (Hebrew *mutsaqot*, conduits) | the menorah's pipes, named |
| **1 Chr 15:20–21**, harps "on *alamoth*", lyres "on the *sheminith*" | usually read as registers: high, and "the eighth" (an octave); meaning uncertain (K) | the zither doubled an octave lower: 57.8–102.8 Hz |
| **1 Chr 25:7**, 288 trained singers | 24 courses × 12 | 12 per course, as Josephus's 12-note *nabla* |
| **1 Kgs 10:12**, harps and lyres of almug wood | the only explicit instruction to build instruments for the House | — |
| **Mishnah Middot 4:6**, Herod's house 100 × 100 × 100 cubits | **the temple Jesus taught in was a cube** | 3.85 Hz on every axis; Holy of Holies 20 × 20; 15 steps where the Levites sang (Middot 2:5) |
| **Rev 21:16–17**, the city "its length, width and height equal", 12,000 stadia; wall 144 cubits | **the final sanctuary is a cube** | the same shape as the tabernacle's and Solomon's inner rooms and Herod's house |

## 3. What is still missing
1. **Tabernacle structure:**
   - the boards' tenons and the five bars per side (Exod 26:15–29);
   - the entrance screen on 5 pillars;
   - the court's 60 pillars with silver hooks and bands (27:9–19).
2. **Tabernacle materials:**
   - the laver made from bronze mirrors (38:8);
   - the anointing oil and incense recipes (30:22–38).
3. **The priestly garments in full:** the ephod, the onyx shoulder stones with the 12 names, the sash, tunic and turban, and the gold plate "Holy to the LORD" (Exod 28).
4. **Solomon:**
   - the ten lavers on wheeled stands, 4 cubits, 40 baths each (1 Kgs 7:27–39);
   - the olive-wood doors with five- and four-sided frames (6:31–35);
   - the windows (6:4).
5. **Ezekiel 40–48 in full:**
   - six gates with their chambers and porches;
   - 30 chambers on the pavement;
   - the kitchens;
   - the east gate kept shut (44:1–2).
6. **Other sound objects with instructions:**
   - Joshua's seven shofars (Josh 6);
   - Gideon's 300 trumpets and smashed jars (Judg 7:16–20);
   - Miriam's drum (Exod 15:20);
   - David's 4,000 instruments (1 Chr 23:5).
7. **Herod's temple in full:** Mishnah Middot 1–5, and Josephus, *War* 5.184–237 (the Nicanor gate, the 15 steps, the golden vine over the entrance).
