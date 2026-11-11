# Words of power, round 4 (round 40): the original words as calculated physical sound

This round asks what each original utterance was as sound, in the space where it was spoken: its phonemes, its hidden overtone melody, the note the room favours, and how loud it became there.

- **Utterances:** 21 power utterances in their original wording, in Aramaic, Hebrew, Koine Greek, the magical names, and reconstructed Egyptian.
- **Spaces:** seven ancient spaces modelled from their recorded dimensions, plus three measured resonances from the literature.

**Approach:**
- Every view is admitted: ancient claims, magical texts and modern measurements alike.
- Each claim is recorded as its source states it, then set against what can be calculated.
- Labels: **Calc** calculated here · **K** known or reported in the literature · **N** the physics says no · **Reading** an interpretation.

**Files:**
- script `power/round40_original_sounds.py` (seed 40, about 3 minutes with audio, or `--no-audio`);
- every number: `power/round40_results.json`;
- renders: `power/audio/r40_*.mp3`, each with its analysis `.json`.

## 1. The original utterances as sound
Voiced share is the fraction of sounds made with the vocal folds vibrating. Noise share is the fraction of hiss and friction sounds. "Above John" is the share of John's narrative verses that are *more* voiced, from 300 random verses (mean 0.733 ± 0.044).

| Utterance | Original | Source | Voiced | Noise | Above John | Sound character |
|---|---|---|---|---|---|---|
| Talitha koum | ταλιθα κουμ | Mark 5:41 | 0.67 | 0.11 | 0.95 | stop-rich: emphatic tˤ and uvular q |
| Ephphatha | εφφαθα | Mark 7:34 | 0.43 | **0.43** | 1.00 | **the most breath-noise of all 21** (f-f-θ) |
| Abba | αββα | Mark 14:36 | 1.00 | 0 | 0 | fully voiced |
| Eloi … sabachthani | ελωι ελωι λεμα σαβαχθανι | Mark 15:34 | 0.78 | 0.09 | 0.13 | 12 syllables, "with a loud voice" |
| Lazarus, come out | Λάζαρε, δεῦρο ἔξω | John 11:43 | 0.87 | 0.27 | 0.003 | voiced, with a z and an ks burst |
| I am | ἐγώ εἰμι | John 18:6 | **1.00** | 0.17 | 0 | fully voiced, bright (F2 1,808 Hz) |
| It is finished | τετέλεσται | John 19:30 | 0.56 | 0.11 | 1.00 | stop-heavy (t-t-t), brightest vowels (F2 1,850) |
| Amen, amen | ἀμὴν ἀμὴν λέγω ὑμῖν | John (25 times) | **1.00** | 0.06 | 0 | nasal, continuous |
| Let there be light | יְהִי אוֹר | Gen 1:3 | 0.71 | 0.14 | 0.65 | |
| I am that I am | אֶהְיֶה אֲשֶׁר אֶהְיֶה | Exod 3:14 | 0.60 | 0.20 | 1.00 | breathy h-h-h |
| Shema | שְׁמַע יִשְׂרָאֵל … | Deut 6:4 | 0.75 | 0.19 | 0.36 | |
| Holy, holy, holy | קָדוֹשׁ ×3 | Isa 6:3 | 0.60 | 0.40 | 1.00 | dark (F2 820): six o/a vowels on one overtone |
| The great shout | תְּרוּעָה גְדוֹלָה | Josh 6:20 | 0.92 | 0.17 | 0 | |
| Seven vowels | αεηιουω | Demetrius 71; PGM XIII | 1.00 | 0 | 0 | pure vowel |
| IAŌ | ΙΑΩ | PGM (89 times) | 1.00 | 0 | 0 | |
| Ablanathanalba | ΑΒΛΑΝΑΘΑΝΑΛΒΑ | PGM (16 times) | 0.92 | 0.08 | 0 | one vowel throughout, palindrome |
| Abrasax | ΑΒΡΑΣΑΞ | PGM (34 times) | 0.63 | 0.25 | 1.00 | |
| *ḏd mdw* "words to be said" | Pyramid Texts rubric | Egyptian, reconstructed | 1.00 | 0.13 | 0 | |
| *ʿnḫ wḏꜣ snb* | royal formula | Egyptian, reconstructed | 0.81 | 0.19 | 0.05 | |
| *ḥkꜣ* heka, "magic" | Egyptian | reconstructed | 0.40 | 0.20 | 1.00 | |
| Amun | AMOUN (PGM 14) | Coptic | 0.80 | 0 | 0.06 | |

**Calc.** As a group the power utterances are more voiced than John's narrative: 0.78 against 0.73, p = 0.001 (20,000-fold permutation). This replicates round 37's finding T5 on a wider set that now includes the Hebrew, Aramaic and Egyptian words.

**Caveats:**
- The Aramaic and Egyptian forms are hand-set phonemes; the Greek and Hebrew come from the engine's parsers.
- Egyptian vowels are not written in hieroglyphs. They are reconstructed from Coptic (Loprieno 1995), and the conventional "a" vowels are a convention, not evidence.

**The exceptions are telling:**
- **Ephphatha** ("be opened") is the noisiest word of all, 43% breath friction. Mark says Jesus "sighed" (ἐστέναξεν) as he spoke it.
- **Holy, holy, holy** carries most of its sound in noise and dark vowels.
- **Reading:** the word for opening is made of moving air. The threefold holy is a dark, steady drone.

## 2. Hidden overtone melodies
When a vowel is chanted on one note, its second formant brightens a particular harmonic of that note (measured on audio in round 38's E3). The table gives that harmonic for each vowel, at each room's favoured note.

| Utterance | King's Chamber (132 Hz) | Holy of Holies (155 Hz) | Rock tomb (171 Hz) |
|---|---|---|---|
| Seven vowels | 9-14-16-17-6-14-6 | 8-12-14-15-5-12-5 | 7-11-12-13-5-11-5 |
| Holy, holy, holy | 6 ×6 | **5 ×6** | 5 ×6 |
| Ablanathanalba | **9 ×6** | 8 ×6 | 7 ×6 |
| Lazarus, come out | 9-9-14-14-6-14-6 | 8-8-12-12-5-12-5 | 7-7-11-11-5-11-5 |
| I am | 14-6-17-17 | 12-5-15-15 | 11-5-13-13 |
| Talitha koum | 9-17-9-7 | 8-15-8-6 | 7-13-7-5 |

**Calc:**
- The seven vowels make a full overtone melody.
- Ablanathanalba and the threefold "holy" hold **one overtone throughout**.
- Ablanathanalba is a palindrome in its letters and also constant in its sound: forwards, backwards and spectrally, it is the same.

**Reading:** two strategies of sacred sound. One moves through all the colours (the seven vowels); the other holds a single colour (the palindromic names, the threefold holy).

## 3. The spaces: favoured notes, resonance and loudness
Each room is modelled as a rigid box.
- **Modes:** its resonant frequencies, computed up to 320 Hz.
- **Mode width:** B = 2.2 / RT.
- **Favoured note:** the pitch in 85–180 Hz where most modes stack.
- **Sound level:** the level at 2 m from the source, direct plus reverberant field (Sabine).

| Space | Basis | Favoured note | Modes a sung note excites | Chant / loud voice / shout (dB) |
|---|---|---|---|---|
| Holy of Holies, Solomon | 1 Kgs 6:20, 20-cubit cube | 155 Hz (D♯3), 18 modes stacked | 1.1% | 71 / 81 / 88 |
| Holy Place, Solomon | 1 Kgs 6:2 | 155.5 Hz (D♯3) | 0.8% | 70 / 80 / 87 |
| Tabernacle's Holy of Holies | 10-cubit cube (Exod 26) | 158 Hz | 3.1% | 75 / 85 / 92 |
| King's Chamber, Great Pyramid | 10.47 × 5.24 × 5.84 m, granite | **132 Hz (C3)** | 1.1% | 77 / 87 / 94 |
| Queen's Chamber | 5.75 × 5.23 m, gabled | 163 Hz (E3) | 0.4% | 78 / 88 / 95 |
| Rock-cut tomb (typical Judean kokhim chamber) | 3 × 3 × 2 m (Hachlili 2005); Lazarus's own tomb is unmeasured | 171 Hz (F3) | 3.2% | **83 / 93 / 100** |
| Galilean synagogue hall | about 20 × 15 × 7 m | 173.5 Hz (F3) | 0.5% | 68 / 78 / 85 |

**Reported in the literature (K):**
- Newgrange resonates at 110 Hz, and six megalithic chambers at 95–120 Hz, clustered at 110–112 Hz (Jahn, Devereux & Ibison 1996, *J. Acoust. Soc. Am.* 99:649).
- The Ħal Saflieni Hypogeum's Oracle Room is reported at about 110–114 Hz (Debertolis et al. 2015).
- 110 Hz tones shift frontal EEG asymmetry in listeners (Cook, Pajot & Leuchter 2008, *Time and Mind* 1:95).

**Calc: the pop and the hiss wake the whole room.**
- A sung note excites only 0.4–3% of a room's low resonances.
- A pop (an impulse) or a hiss (broadband noise) excites all of them.
- The magical papyri prescribe 45 pops and 18 hisses (round 38).
- **Reading:** physically, these are the sounds that set a whole stone chamber ringing. They are the ancient equivalent of the acoustician's clap test.

**Calc: small stone rooms amplify.**
- A loud voice reaches 93 dB in a tomb-sized stone chamber, against 78 dB in a synagogue hall.
- A shout reaches 100 dB.
- Both pass the level at which loud low tones stimulate the balance organ, the saccule, about 90 dB (K: Todd & Cody 2000; Todd et al. 2008). The voice is then felt as well as heard.
- In a small stone chamber the sound becomes a bodily sensation.

## 4. The events, calculated
| Event (text) | Calculated sound | Thresholds crossed | Label |
|---|---|---|---|
| Temple dedication: 120 trumpets with singers "as one" (2 Chr 5:12–14); "the priests could not stand to minister" | They stood "at the east end of the altar", in the open court: about 108 dB at 10 m and 98 dB at 30 m. Had the sound filled the house, 125–127 dB | balance organ (90); discomfort (110) inside; near pain (130) inside | Calc; **Reading:** at these levels people do lose balance and composure. The text gives the cause as the cloud of glory. |
| Jericho: 7 shofars and the great shout (Josh 6:20) | At 30 m: 7 shofars about 86 dB; 40,000 shouting (Josh 4:13) 105.5 dB; 600,000 (Exod 12:37) 117 dB | not masonry damage (about 165 dB, a 250-fold larger pressure) | **N** for sound as the mechanism |
| "I am", and the soldiers fell (John 18:6) | A fully voiced phrase; outdoors, about 75–85 dB at a few metres | none physical | **N** for force; **Reading:** the text presents it as the effect of the divine name (cf. Exod 3:14) |
| Lazarus, "with a loud voice" (John 11:43) | 90–97 dB at 1 m outdoors; inside a small stone chamber, a voice reaches 93–100 dB | balance organ, for those in the chamber | Calc |
| Ephphatha, with a sigh (Mark 7:34) | 43% breath friction; spoken close, with touch to ears and tongue (Mark 7:33) | felt as touch and air, not only as sound | **Reading:** a word a deaf man could feel |

## 5. What this adds
- **The voiced-sound effect now holds across five languages:** Greek, Hebrew, Aramaic, the magical names and Egyptian (p = 0.001). The exceptions are the words of opening and of holiness, which are made of breath and noise.
- **Each sacred space has a computable favoured note.**
  - King's Chamber: C3, 132 Hz.
  - Solomon's Holy of Holies: D♯3, 155 Hz.
  - Megalithic chambers (measured, K): about 110 Hz.
  - The renders sing each formula on its room's note.
- **The two magical sound-gestures have a clear physical role.** The pop and the hiss excite every resonance of a room, where a sung note excites 1–3%.
- **The temple dedication's sound would have been physically overwhelming.** About 108 dB at 10 m in the open court, and 125 dB or more if it filled the house. Jericho's walls, by contrast, could not fall to sound: the pressure falls short by a factor of about 250.

## 6. Limits
- The rooms are idealised boxes. The reverberation times are estimates from the materials.
- The Holy of Holies depends on the cubit: 155 Hz uses 0.445 m; with 0.525 m it is about 131 Hz.
- The source powers are typical values (speech 10 µW to a shout of 5 mW; shofar 0.3 W).
- Aramaic and Egyptian vowels are reconstructions.
- The synthesis is a formant model, not a recorded voice.

## Renders (`power/audio/`)
| File | Utterance | Space | Note |
|---|---|---|---|
| `r40_talitha_koum.mp3` | Talitha koum | rock tomb | 171 Hz |
| `r40_lazarus.mp3` | Lazarus, come out | rock tomb | 171 Hz |
| `r40_ephphatha.mp3` | Ephphatha | synagogue hall | 173.5 Hz |
| `r40_ego_eimi.mp3` | I am | synagogue hall | 173.5 Hz |
| `r40_qadosh.mp3` | Holy, holy, holy | Holy of Holies | 155 Hz |
| `r40_yehi_or.mp3` | Let there be light | Holy of Holies | 155 Hz |
| `r40_seven_vowels.mp3` | Seven vowels | King's Chamber | 132 Hz |
| `r40_djed_medu.mp3` | *ḏd mdw* | King's Chamber | 132 Hz |
| `r40_ablanathanalba.mp3` | Ablanathanalba | King's Chamber | 132 Hz |
| `r40_ankh_wedja_seneb.mp3` | *ʿnḫ wḏꜣ snb* | Queen's Chamber | 163 Hz |
