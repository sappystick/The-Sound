# KANON: where it matters, what to add, how to get it adopted (round 67)

This document has three parts:
- an honest map of where a spoken, checksummed, ring-ordered language beats the alternatives, and where it does not;
- a plan for growing it into a multi-field tool without breaking its one rule (no imports);
- the fastest route to people actually using it.

## 1. Where KANON is genuinely useful

KANON is slow as a data channel: about 3 syllables a second, roughly 10–20 bits a second. As a general programming language it will not beat Python. Its value lies where **a person must be able to hear, say, check and trust a short program or command**, and where **no screen or network can be assumed**.

| Rank | Where | Why KANON fits | What exists instead, and its gap |
|---|---|---|---|
| 1 | **Confirming what a machine is about to do** (AI agents, automation, safety-critical commands) | An agent reads its plan aloud as a short KANON verse. The human hears it, can repeat it, and the error-correcting tail guarantees that what was heard is what runs. The seal gives a visual fingerprint to compare. | Natural-language summaries are unverifiable; raw code is unreadable aloud. No mainstream "speakable, checksummed intermediate form" exists. |
| 2 | **Eyes-free and hands-free programming** (blind and low-vision developers, motor impairments, kitchens, workshops, cockpits) | 19 glyphs and 84 syllables make a closed, unambiguous vocabulary, which is far easier for speech recognition than English keywords, brackets and identifiers. Errors are flagged, not silently executed. | Voice-coding tools dictate English plus symbols, and recognition errors are frequent and silent. |
| 3 | **Device setup over sound** (Internet-of-things provisioning, offline kiosks, air-gapped machines, emergency radio) | Any speaker-to-microphone path, phone line or voice radio carries a program or configuration. It is exact at 4 dB signal-to-noise, repairs two errors per block, and needs no pairing. | Audio modems (ggwave, DTMF, FSK) send opaque bytes that a human cannot check by ear. |
| 4 | **Teaching computational thinking** (ages 8 and up, in any language, in music and history classes) | The keywords are syllables, not English, so it is culturally neutral. Programs are melodies. Ring order teaches structure, the calendar palace teaches memory, and every step is checked. | Block languages (Scratch) are visual only; text languages assume English. |
| 5 | **Digital humanities** | The Canon already holds gematria, isopsephy, planetary weekdays, star polygons and room resonances, and the project's own tests (ring structure, centres, permutation nulls) can become Canon words. | Spreadsheets and ad-hoc scripts. |
| 6 | **Live performance and sound art** (live coding at concerts) | The program and the music are the same object. The output is just-intonation melody. | Live-coding languages (TidalCycles, Sonic Pi) are typed, not sung. |
| 7 | **Memory and learning research** | A clean test bed for the method of loci, chant-based recall and one-night learning, with automatic scoring. | Bespoke lab materials. |

Weak fits, stated plainly:
- large software;
- high-throughput data;
- anything where a keyboard and screen are already present and nobody needs to listen.

## 2. Features to integrate, organised the KANON way

The rule stays: **everything lives inside the language**. New capability arrives as Canon houses (domain consonant × member vowel), as primitives of the runtime, or as prelude written in KANON. Ordered by value per effort:

### 2.1 Language core

| Feature | What it adds | How it fits |
|---|---|---|
| **Scrolls (modules)** | Named collections of definitions, loaded by name | `::scroll name` … a scroll is a book of verses; its checksum identifies its version |
| **Typed planes** | i holds numbers, a can hold text, o can hold a table | A vowel already names a plane; give each plane a declared kind and check it at the door |
| **Static ring check** | Warns when the ring order reads a plane before anything writes it, the commonest beginner error | It runs on the seal's own execution order |
| **Transpilers** | KANON → Python and JavaScript, so a spoken program can drive real software | One pass over the parsed verse; ring order becomes plain sequence |
| **Pattern verses** | Match a plane's shape (empty, one value, many) and choose a word | Uses the guard mark; no new glyph |

### 2.2 Canon expansion: multi-field houses

| House | Field | First words |
|---|---|---|
| t + o … | Statistics as this project practises it | permutation test, exact Poisson-binomial, Benjamini–Hochberg, bootstrap |
| s | Sound | sine/vowel synthesis, FFT, band filters, room modes as reverb, breath-paced envelopes. This is the Resonance engine (`resonance/`) as Canon words |
| n | Text | strings in plane a, Greek and Hebrew letters, gematria and isopsephy of words (not just numbers), transliteration |
| r | Calendars | Hebrew, Julian, Gregorian, the Qumran 364-day year, planetary hours, phase stamps |
| p | Geometry | coordinates, polygons, distances, areas, SVG drawing doors (the seal machinery made general) |
| d | Doors | CSV and JSON in and out, MIDI out, the acoustic modem as a door, serial for microcontrollers |
| h | Integrity | hashes, Reed–Solomon (already in the runtime), seals as fingerprints |
| g | Data | group, join, count by key: a small table algebra over planes |

### 2.3 Channel

| Feature | Value |
|---|---|
| **Human-voice decoder** | A person speaks KANON and the machine runs it. Vowel recognition already exists (the round 42/59 formant machinery); consonants need a small classifier over 12 classes. Error correction makes this safe. |
| **Erasure decoding** | When the decoder knows a sound was unclear, it can mark it as an erasure. Reed–Solomon repairs twice as many erasures as errors. |
| **Faster modes** | Two tones at once, or a higher carrier for machine-to-machine use, while keeping the slow mode for humans |
| **Ultrasonic mode** | Above 17 kHz, silent to adults, for device-to-device use |

### 2.4 Tools

- **Packages:** `pip install kanon` and `npm install kanon`. The two interpreters already agree on 1,000 of 1,000 random programs.
- **An editor extension:** syntax colours by plane, the seal beside the code, ring order shown, hear-on-hover.
- **A voice REPL:** listens on the microphone and answers in tones and speech.
- **A microcontroller decoder** (ESP32 class): the "speak a configuration to a device" demonstration.
- **An agent tool:** a KANON function an AI assistant can call to propose actions as verses with seals and error correction, for a human to approve by ear.

## 3. The quickest route to adoption

1. **One unmistakable demonstration per audience, each under a minute:**
   - **Accessibility:** a blind user writes and runs a program by voice. A misheard syllable is repaired and flagged aloud.
   - **Devices:** a phone speaks a Wi-Fi configuration to a microcontroller across a noisy room.
   - **AI safety:** an agent reads its next action as a verse. The user repeats it back, and the action runs only if the tails match.
   - **Classrooms:** a class sings a program and the projector runs it.
2. **Zero-install first contact.** The one-night course page already runs in any browser. Add a shareable link per program, carried in the hash, so programs spread as links.
3. **Measure the "one night" claim.** A timed learner study with 10–20 people: course in the evening, delayed test the next morning on writing, speaking and decoding by ear. Publish the result either way.
4. **Packages and a reference card.** The calendar palace and planetary week fit on one printable card.
5. **Papers:**
   - "Ring-order evaluation: chiastic composition as an execution model";
   - "A speakable, error-correcting program channel, exact at 4 dB SNR";
   - the learner study.
6. **Community hooks:** a puzzle a week in verse form, a Discord or Matrix bot that runs spoken clips, and a live-coding night.

## 4. What was built this round

- **Error-correcting code.** Reed–Solomon over GF(113): one field element per spoken symbol and five parity words per block.
  - Up to 2 wrong symbols in a block are corrected; 3 or 4 are always flagged.
  - Random-damage test, 1,500 blocks at each error count:
    - 0–2 errors: 100% corrected;
    - 3–4 errors: 100% flagged;
    - 5 errors: 1 block miscorrected.
- **Digit redesign.** Digits are now a consonant chord plus a dedicated number pitch (ratio 1.6, outside the seven vowels). They had been the weak point: every error at 3 dB was a dropped or split digit.
- **Split bursts re-joined.** A consonant burst heard apart from its vowel is now re-joined to it.
- **Spoken-program fuzz test** (120 programs):

| Noise (SNR) | Exact as heard | Exact after correction | Flagged | Wrong without a flag |
|---|---|---|---|---|
| 8 dB | 120 | 120 | 0 | 0 |
| 4 dB | 120 (it was 46 with digit-pair tails, and 113 for v0.2 with checksums) | 120 | 0 | 0 |
| 3 dB | 117 | 117 | 3 | 0 |
| 2 dB | 12 | 17 | 103 | 0 |

The page's "hear it spoken" now adds the same parity words. The JavaScript encoder produces identical tails to the Python one.
