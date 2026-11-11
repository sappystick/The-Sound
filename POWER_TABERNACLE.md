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
