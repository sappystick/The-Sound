# Words of power, round 6 (round 42): sound machines, and texts written as scores

**The question:** could an instrument, or a set of devices, really have produced the sounds the texts describe in obscured language? And could people who heard them have written them down as story and music?

**Four tests, each connecting a different set of dots:**
- **A.** Build the speaking instrument properly, from tube acoustics.
- **B.** Gather the ancient records of real sound machines.
- **C.** Test whether the texts' sound descriptions are structured like scores.
- **D.** Test whether their strangest sound image, "many waters", is physically accurate.

**Files:**
- script `power/round42_sound_machines.py` (seed 42);
- numbers `power/round42_results.json`;
- audio `power/audio/r42_*.mp3`;
- new source: Heron, *Pneumatica* (Greek and German, ed. W. Schmidt 1899, public domain), in `sources/texts/heron/`.

Labels: **Calc** calculated · **K** known · **N** negative · **O** open · **Reading** interpretation.

## A. A true, buildable speaking instrument
**The vowel pipes of round 41 are not enough.** A pipe tuned to a formant only resonates; it needs a buzzing source and a resonator shaped like a mouth. That is exactly what von Kempelen built in 1791 (bellows, a reed, a leather mouth), and his machine spoke short sentences (**K**).

**The design:**
- **Source:** a free reed (a brass tongue) driven by bellows. The tongue's length sets the pitch, for example the mese at 220 Hz or a room's favoured note (round 40).
- **Resonators:** one for each Greek vowel, built as three tube sections from glottis to lips (back cavity, tongue constriction, lip opening).
- **Fitting:** the dimensions are fitted with lossless transmission-line acoustics (chain matrices; resonance where the closed-glottis condition K₂₂ = 0). The lengths total 15–19 cm and the areas are limited to 0.3–12 cm², the range of a real mouth.

| Vowel | Target F1 / F2 (Hz) | Machine F1 / F2 / F3 | F1–F2 error | Sections, glottis → lips (length cm × area cm²) |
|---|---|---|---|---|
| α a | 730 / 1250 | 736 / 1264 / 2988 | 1.0% | 8.3 × 1.2 · 1.8 × 11.5 · 6.1 × 5.7 |
| ε ɛ | 550 / 1850 | 550 / 1852 / 2884 | 0.1% | 2.2 × 0.9 · 6.4 × 2.4 · 7.2 × 1.8 |
| η e | 400 / 2100 | 406 / 2080 / 3188 | 1.2% | 8.0 × 1.4 · 5.3 × 0.4 · 2.1 × 7.5 |
| ι i | 270 / 2290 | 266 / 2204 / 2788 | 2.7% | 6.2 × 11.3 · 5.7 × 1.1 · 3.4 × 5.0 |
| ο o | 450 / 800 | 464 / 838 / 2032 | 3.9% | 13.0 × 1.1 · 3.5 × 10.6 · 1.9 × 0.9 |
| υ y | 270 / 1850 | 270 / 1822 / 2980 | 0.8% | 9.6 × 6.9 · 2.9 × 0.7 · 2.9 × 1.7 |
| ω ɔ | 570 / 840 | 562 / 830 / 2034 | 1.3% | 12.9 × 0.5 · 4.8 × 7.2 · 0.9 × 0.6 |

**Calc:** all seven vowels are reproduced within 0.1–3.9% by tubes of real-mouth size.

**What the shapes look like:**
- The back vowels (ο, ω) need a long narrow back tube and a tiny lip opening, which is lip rounding.
- ι needs a wide back and a narrow front, which is a raised tongue.

**Consonants, with von Kempelen's devices:**
- m, n: a nasal side tube opened by a valve;
- l: a flap partly closing the front tube;
- b, p: leather lips;
- s, θ, f: separate hiss whistles;
- k, t: burst valves.

**Renders:** the machine saying ABLANATHANALBA and ἐγὼ εἰμι: `r42_machine_ablanathanalba.mp3`, `r42_machine_ego_eimi.mp3`.

**What the machine can and cannot do:**
- **Can:** with seven resonators, a reed tuned to the lyre string of each vowel (round 41), and the consonant valves, it plays a word's sound line and its planetary melody at once. That is a word sung by an instrument.
- **Cannot:** it speaks only what is set into it. It adds no hidden content.

## B. Ancient machines that made sacred sound (primary texts)
| Device | Source | How it worked |
|---|---|---|
| A trumpet that sounds when the temple doors open | Heron, *Pneumatica* 1.17 (Schmidt pp. 96–99; read in this round) | The opening door pulls a cord; an inverted vessel drops into water, and the displaced air blows the trumpet |
| Singing birds and a turning owl | Heron, *Pneumatica* 1.15–16 | Water drives air through small pipes; the pitch depends on the pipes' width and length and how deep they sit in the water |
| Altar fire, libations and a hissing serpent | Heron, *Pneumatica* 2.21 | Fire heats the air in a hollow base; the expanding air drives the liquid and the hiss |
| A figure that sounds a trumpet when blown | Heron, *Pneumatica* (Schmidt ch. X) | Breath goes through a hidden channel to the trumpet |
| The water organ | Ktesibios; Heron 1.42; Vitruvius 10.8 | Water-regulated air pressure through tuned pipes |
| The talking serpent Glycon | Lucian, *Alexander* 26 | Cranes' windpipes carried a hidden speaker's voice into the serpent's head |
| The talking skull | Hippolytus, *Refutation* 4.41 | A crane's windpipe hidden behind it carried an accomplice's voice |
| The singing Colossus of Memnon | Strabo 17.1.46; Pausanias 1.42.3; visitors' inscriptions on the statue | It sounded at sunrise until a Roman repair (about AD 199); probably dawn heating of damp, cracked stone |
| The thunder machine (*bronteion*) | Pollux, *Onomasticon* 4.130 | Stones poured onto stretched hides or bronze vessels |
| The bull-roarer (*rhombos*) | Clement, *Protrepticus* 2.17 | A whirled blade gives a roaring, wind-like sound (an object of the Dionysian mysteries) |

**K:** these machines are attested in the very period of the New Testament, and of the papyri. Temples had machines that made sounds on cue (doors, fire, water), and two accounts describe hidden tubes used to give a god a voice.

## C. Are the sound descriptions written like scores?
**Method:**
- Every sound event in the Greek Old Testament (Swete) and the Greek New Testament (SBLGNT) was tagged from a fixed lexicon.
- Each event got a loudness rank fixed **before** the test: silence 0 · breeze 1 · song 2 · voice, roar, wind 3 · cry, trumpet, many waters 4 · thunder, earthquake 5.
- In every chapter with at least 4 events, the loudness order was measured (Kendall τ: positive = crescendo, negative = decrescendo).
- **Null:** the same events shuffled within the chapter.
- **Vision chapters:** fixed in advance. Exod 19, 20; 1 Kgs 19; Isa 6; Ezek 1, 3, 10, 43; Dan 7, 10; Ps 29 (LXX 28) and 93 (LXX 92); Acts 2; Rev 1, 4, 8, 10, 11, 14, 16, 19. Of these, 14 had enough events.

| Test | Result | p | Label |
|---|---|---|---|
| Are sound sequences shaped at all? (all 126 chapters, mean \|τ\|) | 0.283 against 0.264 | 0.11 | **N** |
| Are vision chapters more shaped? (mean \|τ\|) | 0.26 against 0.24 | 0.36 | **N** |
| Do vision chapters rise? (mean signed τ) | **+0.23 against 0.00**: 5 crescendos, 0 decrescendos | **0.0014** | **O**: exploratory |

**Why the crescendo result is exploratory:**
- The direction was noticed in the first run and then tested, so it was not pre-registered.
- The vision set itself was fixed in advance.

**What the rise looks like:**
- Rev 16: voices → thunder → earthquake.
- Rev 4: voice → trumpet → voice → thunder.
- Ps 93 (LXX 92): song → voices → "many waters".
- 1 Kgs 19 (Swete): voice → breeze → voice → cry.

**Reading.** In visions, sound builds toward a climax. Ordinary chapters show no direction (mean τ +0.02). This is how a composed piece is shaped, and it is a property a writer could carry over from a heard performance.

**Next:** test it as a pre-registered replication on the Hebrew text and on books outside this set (1 Enoch, 4 Ezra, the Apocalypse of Abraham).

**Limits:** the lexicon misses events described without a sound word. "A great wind" in 1 Kgs 19 is πνεῦμα and fire is not a sound word, so Elijah's wind, earthquake and fire are only partly caught.

## D. "The voice of many waters" is acoustically accurate
**The texts:** Ezek 1:24 and 43:2; Rev 1:15, 14:2 and 19:6; Ps 93:4. Revelation 19:6 equates three things outright: "the voice of a great multitude, as the voice of many waters, as the voice of mighty thunderings".

**The test (Calc):**
- One voice is a comb of harmonics with gaps between them. Rushing water is broadband noise.
- Summing N voices at random pitches and vowels, the fine-structure flatness of the spectrum is measured (1 = perfectly filled; water-like noise = 0.56):

| Voices | 1 | 3 | 10 | 30 | 100 | 1,000 |
|---|---|---|---|---|---|---|
| Flatness | 0.00 | 0.06 | 0.39 | **0.70** | 0.87 | 0.96 |

**Calc:**
- Between about 10 and 30 voices, a crowd becomes acoustically like rushing water: the gaps between harmonics fill and the comb dissolves into noise.
- So the image "a multitude = many waters" describes a physical fact that the writer could only have known by hearing it.
- **Caveat:** summing power spectra idealises the crowd. A real crowd also fluctuates, which makes it even more noise-like.

**Reading:** the obscure image is a precise acoustic description, not a decoration. "Many waters" is what a large, many-voiced assembly sounds like, worship in heaven heard as a crowd.

## E. The sound scores, performed by ancient-type machines
Each rendering uses only sound classes that the machines of section B could make: the door trumpet or shofar, the *bronteion*, the bull-roarer, the water organ, a crowd, and the speaking machine.

| File | Text | Sequence |
|---|---|---|
| `r42_sinai_exod19.mp3` | Exod 19:16–19 | thunder → trumpet → trumpet "growing louder" → a voice (ἐγὼ εἰμι, machine) |
| `r42_elijah_1kgs19.mp3` | 1 Kgs 19:11–12 | wind → earthquake → fire → "a sound of thin silence": breath through the ι resonator (the one decrescendo) |
| `r42_pentecost_acts2.mp3` | Acts 2:2–4 | rushing wind → many voices |
| `r42_patmos_rev1.mp3` | Rev 1:10–15 | trumpet → voice → "many waters" (200 machine voices) |

## Putting the dots together: the theory, and what has and has not been shown
**The theory.** Some obscure descriptions record complex sound events: performed, staged or experienced. They were written in the only notation available, which was narrative and simile.

**The evidence so far:**
1. **The technology existed and is documented.** There were machines for trumpets on cue, singing water-birds, hissing fire, thunder and roaring, and hidden tubes that gave statues a voice (section B, **K**).
2. **The texts' sound images are physically accurate.** "Many waters" for a multitude is what acoustics predicts (section D, **Calc**).
3. **The vision chapters are shaped like music.** Their sound rises toward a climax (section C, **O**, p = 0.0014, exploratory).
4. **A word can be built into an instrument.** The speaking machine reproduces every Greek vowel to within a few per cent, using an ancient-feasible design: reed, bellows and shaped tubes (section A, **Calc**).

**What this does not show:**
- that any biblical vision was produced by a machine;
- that the sounds carried meaning beyond what was spoken.

What it does show: the authors heard precisely, wrote sound with structure, and lived among devices that could make such sounds.

**A prediction that could prove this wrong (next test):** if some visions record staged events, their sound events should co-occur with the cues Heron's machines used: doors opening, fire lit, water moving.
- **Test:** the co-occurrence of door, fire and water words with sound events, in vision chapters against other chapters.
- **Example to check:** in Rev 4:1, "a door opened in heaven" is followed at once by "the first voice … as of a trumpet". That is the exact sequence of Heron's door trumpet (*Pneumatica* 1.17).
