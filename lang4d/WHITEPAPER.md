# KANON: a spoken, typed and played programming language
### White paper v0.1 · The Sound project, round 65

> **v0.2 (round 66) is in `REVIEW_v02.md`.** It adds composition inside words, names, guards and while-loops (Turing complete), the 44-name Canon, a prelude written in KANON, spoken marks, checksums that missed no errors in testing, seals, a JavaScript interpreter matching the Python on 1,000 of 1,000 programs, and the one-night course. It **withdraws** the namespace figure in §3 below: v0.1's middle syllables did nothing, so the figure counted spellings, not behaviours.

**KANON** (κανών: the measuring rod, the monochord of the *Sectio Canonis*, and the canon of scripture) is a programming language in which **the same program is a text, an utterance, a melody and a machine process** — four readings of one lattice. It is the engineering descendant of this project's 64 research rounds, and the honest rebuild of the "Aether-4D" sketch (see §9: what survives from that document and what does not).

Reference implementation: `lang4d/kanon.py` (self-contained: Python standard library + NumPy; the synthesiser, codec, ephemeris and VM are built into the runtime — no external services or libraries).
Verified numbers in this paper come from `lang4d/selftest_results.json` (seed 64, reproducible).

---

## 1. Design axioms (each one grounded in a verified finding)

| Axiom | Grounding in The Sound |
|---|---|
| **A vowel is a pitch.** The seven vowels are the seven planet-strings of Nicomachus; ι (the Sun) is the mese, the governing middle string | rounds 41–50; "I am" = *e-ɣo-i-mi* ends on the mese |
| **A word is a melody.** The vowel line of a word *is* its tune; tubes shaped like mouths keep vowels machine-distinguishable (97.8 % in round 59) | rounds 42, 59 |
| **The centre governs.** In a verse, the outer word-pairs execute first and the centre word commits last — ring composition as an evaluation order | pre-registered results: the "I am" ring (p 0.027), 10:11 at the centre of 01/03 (rounds 52–54) |
| **Twelve around the centre.** The 12 consonants sit in the 4×3 grid of the breastpiece — and that same grid is the audio keypad | round 62–63 (the camp, the breastpiece) |
| **The archive is silent.** ω (Saturn) is the string Koine pronunciation never sounds; in KANON it is the write-mostly archive plane | round 45 (the silent hypate) |
| **Time is a chord of phases.** Planetary periods are incommensurable, so a vector of phase angles is a unique, structure-preserving timestamp | round 39: calendar engine validated 57/57 weekdays, 42/42 priestly courses on the Qumran scrolls |
| **Scale-invariance.** Everything is a ratio against a free carrier f₀ (default 154.2 Hz, the ark note); transpose f₀ and nothing else changes | rounds 56–57 |
| **Breath is structure.** The verse ends at a breath; pauses are code | rounds 43, 51 (breath groups; tempo carries John's movements) |

---

## 2. The lexicon

### 2.1 Seven vowels = seven strings = seven data planes

| Glyph | Greek | Planet | Ratio to f₀ | Hz @ f₀ = 154.2 | Plane role |
|---|---|---|---|---|---|
| `a` | α | Moon | 4:3 | 205.6 | input stream |
| `e` | ε | Mercury | 32:27 | 182.7 | fast scratch |
| `y` | η | Venus | 256:243 | 162.4 | pair register |
| **`i`** | ι | **Sun** | **1:1 (mese)** | **154.2** | **accumulator** |
| `o` | ο | Mars | 8:9 | 137.1 | output stage |
| `u` | υ | Jupiter | 64:81 | 121.8 | deep store |
| `w` | ω | Saturn | 3:4 | 115.6 | archive (the silent string) |

**Frequency law:** `f(v) = R(v) · f₀`. The Pliny tuning (NH 2.84: tone, ½, ½, 1½, 1, ½, ½ — Sun still 4th of 7) is a supported alternative tuning table (round 59).

### 2.2 Twelve consonants = twelve operations (the breastpiece grid)

| | col 1 (×17·f₀) | col 2 (×20·f₀) | col 3 (×23·f₀) |
|---|---|---|---|
| **row 1 (×9·f₀)** | `k` commit | `t` test | `p` project |
| **row 2 (×11·f₀)** | `b` bind | `d` door (I/O) | `g` gather |
| **row 3 (×13·f₀)** | `l` loop | `m` morph | `n` negate |
| **row 4 (×15·f₀)** | `r` retro | `s` stream | `h` breath |

Each consonant is *spoken* as a two-tone chord (its row tone + its column tone, both multiples of f₀): the grid position **is** the sound. Digits `#0–#e` (base 12) use the same grid plus a marker tone at ×6·f₀ — twelve digits on the twelve-stone grid.

### 2.3 Structural marks
`|` breath = end of verse · `!` urgent (executes before the ring) · `~` sandbox (errors become no-ops, logged) · `#` digit shift · `.` `:` reserved (explicit centre, pair-binder).

---

## 3. Grammar: meaning from position (the user's "same symbol, different process")

```
program  := verse ("|" verse)*
verse    := word+
word     := (C V)+ [V]          -- syllables consonant+vowel; optional lone final vowel
number   := "#" [0-9te]+        -- base 12, attaches to the preceding word
```

One glyph means different things at different **positions**, exactly as asked:

1. **In the word** — first consonant = the operation; its vowel = the target plane; middle syllables = modifiers; the optional **final lone vowel = the cadence** (source/ratio argument). So `g` in `goa` is *gather a into o*, but `g` in `bago` is a modifier syllable of a bind.
2. **In the verse** — the **ring rule**: words pair (1st,last), (2nd,2nd-last)…; pairs execute outward-in and the **centre word commits last**. The same words in a different order are a different program:
   * `sa #7 gia ta #3` → fill a=[1..7]; **centre `gia` runs last** → but ring order runs the outer pair (`sa`,`ta`) first, so the filter acts before the gather: **ι = 22** (= 4+5+6+7).
   * `sa #7 ta #3 gia` → now `gia` is outer and `ta` is the centre: gather runs before filter: **ι = 28**. *(Both measured in the self-test.)*
3. **In the book** — verses execute in order; `!` words pre-empt; phase stamps (§6) tag each verse with its celestial position.

**Namespace arithmetic** (self-test): 12 × 7 = **84** states per syllable; words of ≤ 4 syllables with optional cadence give **403,095,840** distinct words; × 3 verse roles (outer-left / outer-right / centre) ≈ **1.21 × 10⁹ context-distinct instructions** from 19 base glyphs — the compaction the design brief asked for, by position instead of by symbol count.

---

## 4. The machine

A small deterministic dataflow VM over the 7 planes (lists of rationals-as-floats).

| Op | Semantics (head = target plane, cad = cadence vowel, val = `#number`) |
|---|---|
| `s` stream | head ← [1..val] (the ladder) |
| `k` commit | head ← [val] |
| `b` bind | head ← copy(cad plane) |
| `p` project | head ← head × R(cad) — a musical transposition is the multiply |
| `g` gather | head ← [Σ cad-plane] |
| `t` test | head ← elements > val (default: > mean) |
| `n` negate · `r` retro (reverse) | |
| `m` morph | head[i] ← head[i] · R(cad)^((i+1)/n) — a glide toward the cadence ratio |
| `d` door | ≥2 syllables: **emit the word's own vowel line as melody**; else emit the plane (octave-folded on f₀) |
| `l` loop | repeat the next word val times |
| `h` breath | rest / barrier |

`d`'s first form is the flagship: **`demorini`** = *d(e, o, i, i)* = "speak: Mercury–Mars–Sun–Sun" — the vowel line of **ἐγὼ εἰμι**, resolving on the mese twice (rounds 44, 59). Typing it, speaking it aloud and the machine's rendition of it are the *same melody*.

---

## 5. The codec: speaking is compiling (measured, not metaphor)

Encoder: each syllable = 70 ms consonant chord (row+col tones) + 180 ms vowel tone (fundamental R(v)·f₀ + 2 harmonics); gaps 45 ms / 220 ms / 550 ms (syllable / word / verse). Decoder: energy segmentation with a noise-floor gate; FFT with parabolic peak interpolation; vowel classified to the nearest of the 7 ratios (min spacing 5.35 %, resolvable at 180 ms); consonant from the row/col bands; digits by the marker band.

**Measured results (seed 64):**

| Test | Result |
|---|---|
| Round-trip, clean audio, program `sa #7 gia ta #3 \| di` (3.66 s) | **exact** |
| Round-trip, 54-char program (4 verses, digits, loops) | **exact** |
| + white noise at 25 dB SNR | **exact** |
| + white noise at 15 dB SNR | **exact** |
| + white noise at **8 dB SNR** | **exact** |

Throughput ≈ 3 syllables/s ≈ a slow chant — this is an *accessibility and ambient channel*, not a bulk link. v0.1 decodes machine-spoken KANON; a human-voice front end would reuse the round-42/59 formant machinery (roadmap). A combined file (code + the program's output music) needs the reserved preamble/terminator to separate the two — by design, since the output of a program is itself valid melody.

Scale-invariance: pass any `f0` to `encode/decode` — a whispered 100 Hz and a bright 200 Hz carrier are the same program.

---

## 6. The fourth dimension: celestial phase stamps

`phase_stamp(jd)` returns the mean longitudes of Sun, Moon and the five classical planets (J2000 elements, built in). Because the periods are mutually incommensurable, the 7-angle vector never repeats over historical spans — a **unique, order-preserving, structure-carrying timestamp** (the one idea from the source PDF that is straightforwardly true, and the one this project already validated by reconstructing the Qumran calendar, round 39). Verses may be tagged with stamps; rollback = re-evaluating at an earlier phase vector (deterministic, since the VM is pure).

Example stamp (J2000 + 9800 d): Sun 219.81°, Moon 107.00°, Mercury 37.13°, Venus 42.86°, Mars 90.84°, Jupiter 128.59°, Saturn 18.36°.

---

## 7. Worked examples (all in `lang4d/examples/`, all executed in the self-test)

**`centre.kn`** — the ring rule, visible:
```
sa #7 gia ta #3 | di
```
*Speak it:* "sa … seven. gi-a. ta … three. — di." → fills the Moon-plane ladder 1–7, filters >3, the **centre word** gathers: ι = **22**; `di` sounds it. Reorder the same words and you get 28 (§3).

**`iam.kn`** — one word:
```
demorini
```
The machine speaks the I-AM vowel line, Mercury–Mars–Sun–Sun. The audio file *is* the source code.

**`ladder.kn`** — ladder, transposition, melody:
```
sa #7 ta #3 gia | pia di | ha #3 demorini
```
Gathers the whole ladder (Σ1..7 = 28, the outer pair runs before the centre filter), transposes by a perfect fourth (×4:3), sounds it, breathes, then sings I-AM.

Listen: `lang4d/audio/kanon_ladder.mp3`, `kanon_iam.mp3` — each file is the spoken code, a silence, then the program's own output.

---

## 8. Integrations

- **Voice agents / LLMs:** KANON as a compact, *speakable* intermediate representation — an assistant can dictate a program over any audio channel (even a phone line: the consonant chords are DTMF-grade robust, exact at 8 dB SNR), and the human can hear, repeat, and verify it syllable by syllable.
- **Music tooling:** every program exports as melody (the `d` events); the planes are already in just intonation — direct MIDI/DAW rendering; the round-57 ark-zither/menorah-pipe soundfont is the natural instrument.
- **Education:** the Echo-Ladder course builder (round 34) applies verbatim — KANON's 19 glyphs and one-new-glyph-per-step ladder make the full language learnable in one sitting, in text or by ear.
- **Accessibility:** eyes-free, hands-free programming; the glyph chart doubles as a tactile/visual layout.
- **Ritual/performance art:** programs in the Temple ensemble voicing (rounds 48–57); the carrier defaults to the ark note.

---

## 9. Honest-claims table (what is real, what is metaphor, what is false)

The source sketch ("Aether-4D") mixes three kinds of statement. KANON keeps the first, labels the second, drops the third — the same discipline as the whole project.

| Claim from the sketch | Status in KANON |
|---|---|
| Spoken code literally compiles | **REAL** — measured: exact round-trip to 8 dB SNR (§5) |
| One symbol = many instructions by context | **REAL** — position grammar; ≈1.2 × 10⁹ context-distinct instructions from 19 glyphs (§3) |
| Scale-invariant ratio design, any carrier | **REAL** (§2, §5) |
| Celestial phase vectors as unique structured timestamps | **REAL** mathematics — and validated against the Qumran scrolls in round 39 (§6) |
| Built-in engine, no external libraries | **REAL in the honest sense** — synth, codec, ephemeris and VM are primitives of the self-contained runtime; it still runs on an ordinary CPU |
| Self-morphing code | **PARTIAL** — `~` sandbox and `m` morph exist; full live AST rewriting is roadmap, and it is ordinary metaprogramming, not biology |
| "Emotional tensors" compiled from the voice | **PROSODY FLAGS ONLY** — `!` and `~` are deliberate, typed marks; inferring intent from tone is a UI layer, never silent semantics (a language whose meaning changes with your mood is undebuggable) |
| Wave interference solves logic in O(1) | **FALSE** — sampling a superposed field is O(N·M) on any real hardware; the "resonance peak" is an argmax. KANON's VM is honest dataflow |
| Escapes the Von Neumann bottleneck | **FALSE** as stated — KANON is a language + VM on ordinary machines; photonic/quantum ports are speculation and labelled so |
| Orbital garbage collection, data gravity | **METAPHOR** — usable as scheduling heuristics; not physics |

---

## 10. Roadmap
1. **Human-voice front end:** replace the consonant chords with real consonant recognition built on the round-42 three-tube formant machine (which already reproduces all seven vowels within 4 %).
2. Preamble/terminator chirps; checksum verse (a gematria sum — the ancient practice, used honestly).
3. Per-glyph geometric font (the chart's constructions as a real typeface); AR "score view" of running programs.
4. Property-based tests; a REPL that listens on the microphone and answers in kind.
5. The Akouo one-new-glyph-per-step spoken course for the language itself.

---

*The Sound, round 65. Everything in §2–§7 is executable; run `python3 lang4d/kanon.py selftest`.*
