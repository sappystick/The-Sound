# KANON: the standout use, and every dimension it can carry (round 71)

## 1. The one that stands out

Of everything reviewed, **one use is both obvious and genuinely new**:

> **A human-verifiable instruction format: short programs that a person can hear, say, see and approve, that a machine runs exactly, and that repair themselves in transit.**
> The first product: **approving the actions of AI agents** (and, from the same design, autonomous satellites and payments).

Why this beats the other candidates:
- **Need.** Every AI lab and every autonomy programme now has to answer "how does a person approve exactly what the machine will do?". No standard answer exists.
- **No incumbent.** Free text cannot be verified and code cannot be read aloud. Hex hashes are unreadable to people.
- **Fit.** It uses every property KANON already proved:
  - static bounds before execution (F1–F6);
  - readback in everyday words (the skins);
  - repair of misheard words (Reed–Solomon);
  - a visual fingerprint (seals);
  - survival over phone and radio channels (GSM 40 of 40).
- **Low barrier.** It needs no certification, no chain and no new hardware. It can ship as a tool any agent framework calls.

Everything else (the blockchain, works-as-objects, lab and flight profiles, place codes) uses the same core, so this is a beachhead, not a narrowing.

## 2. Dimensions: new ideas, each with a concrete design and a real use

Rating: **★★★** strong real use · **★★** useful · **★** artistic or experimental.

### Space and geography: **place codes** (built: `fields/geocode.py`) ★★★
- **The design.**
  - Each syllable splits the current cell into 12 × 7. The consonant takes longitude in twelve and the vowel latitude in seven, in Ptolemy's seven *klimata*.
  - The roles swap on every second syllable, so cells stay square.
- **Precision:** 3 syllables ≈ 34 km; 5 ≈ 400 m; **7 ≈ 4.8 m**; 8 ≈ 0.5 m.
- **Measured.** On 5,000 random places the worst error is 2.8 m. With 2 misheard syllables, **5,000 of 5,000 were repaired**.
- **Examples:**
  - the Temple Mount is "**mow net pool row mow say law**";
  - the Western Wall, 200 m away, shares the first 5 syllables;
  - Ephesus and Patmos share "lohw…".
- **Why it beats what exists.** what3words is proprietary, gives no hint of where a place is, and cannot repair errors. Plus codes are open but cannot be spoken comfortably or repaired. KLIMATA codes are open, hierarchical (a prefix is a region), speakable and self-repairing.
- **Uses:** emergency calls, rural addresses, drone and rover waypoints, field science, and KANON programs that take places as arguments.

### Touch: **one braille cell per syllable** ★★★
8-dot braille has 256 cells and KANON needs 84 syllables plus digits and marks, so every symbol fits in one cell. The consonant's grid row and column are the left dots, and the vowel is the right dots.
- **Uses:** blind programmers read and write KANON natively. Tactile labels and keys carry the same error-correction words.
- The same mapping drives **haptic patterns** (consonant = rhythm, vowel = vibration pitch) for wearables.

### Light and colour: **a screen-to-camera channel** ★★
Seven vowels ↔ seven hues. Newton chose *seven* spectral colours by analogy with the musical scale, the same move KANON makes. Consonants are shown as shape or position, never colour alone.
- **Use:** a phone camera reads a program off a screen or a printed card, with Reed–Solomon in the same alphabet.
- **The rule:** colour is a redundant layer. Every glyph must read in greyscale, for colour-blind users and for print.

### Glyphs: **a featural script** ★★
Hangul is the model: its letter shapes encode how the sound is made. The KANON equivalent:
- each **consonant** is a stroke drawn from its grid row (season) and column (month);
- each **vowel** is a dot at its heptagon position (weekday);
- a syllable is one compact block.

Seals are already the word-level version. A real typeface makes KANON writable by hand and readable by OCR, again with the same error correction.

### Sound: harmonics and resonance ★★
- **Errors you can hear.** Units and planes have sounds (speed is *pani*). A type or unit mismatch could be sonified as a dissonant interval in the just-intonation scale, so code review happens by ear. Whether listeners actually catch errors this way is a measurable experiment.
- **Room tuning.** Choose the carrier from a room's resonant modes, as the Resonance engine does, so a spoken program resonates in its space. This one is artistic.

### Many orders at once: **polyphony as concurrency** ★★
Today there are three orders: syllable pipeline, verse ring, book sequence. The next two:
- **Voices = threads.** Each plane can be a voice. A *chord* of verses means "run these concurrently", with a fixed, rhythm-defined interleaving, so concurrency is deterministic and **race conditions become audible clashes**.
- **2-D works.** Like the PGM XIII vowel square: a grid of verses where rows run in ring order and columns in sequence, so one score defines a 2-D process (pipelines, cellular automata, and image or video generation from a single square).

### Time and astronomy: **sky-keyed scheduling** ★★
The phase stamp (the 7 planetary mean longitudes) already gives unique timestamps. Next:
- verses keyed to astronomical events ("run at the next new moon", "every planetary week", "at this orbital phase") for agriculture, religious calendars and satellite operations;
- sunrise and sunset computed from a place code, for prayer times and field operations.

Astronomy here is a clock, never a claim of influence.

### Numbers ★★
- **84 = 12 × 7** is the grid: months × days.
- Mixed radix lets a number be read as a calendar date: syllable *n* = month *n*//7, day *n*%7.
- Base twelve stays for programs. **Decimal is shown for money and measurements**, as the chain prototype taught.

### Space-bound execution ★
Verses that run only inside a place code's cell: geofenced actions for drones, the field and art installations. These combine place codes with guards.

### Physical tokens ★
Extrude a seal into a 3D-printed or engraved token: a physical, verifiable key or certificate. The token's shape decodes back to the program, and the parity words cover a chipped edge.

## 3. Suggested order
1. **KANON-AGENT approval** (the standout).
2. **KLIMATA place codes:** small, open, immediately useful, and now prototyped.
3. **The braille and haptic channel:** highest accessibility value for little effort.
4. **The glyph typeface** and **colour-camera channel:** these give the written and visual layers.
5. **Polyphony, 2-D works and sky-keyed scheduling**, for the language core and art.
