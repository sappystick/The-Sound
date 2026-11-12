# KANON: review of v0.1 and what v0.2 adds (round 66)

The code is `lang4d/kanon.py` (Python) and `lang4d/kanon.js` (JavaScript). Run `python3 lang4d/kanon.py selftest`.

Results are in:
- `selftest_results.json`
- `parity_results.json`
- `course/course.json`

The course page is `lang4d/app/` and is also published as an artifact.

---

## 1. Review of v0.1 (round 65)

I read all of v0.1, ran its self-test, and then stress-tested it.

| # | Finding | Severity | Evidence |
|---|---|---|---|
| 1 | **Middle syllables did nothing.** The VM read only the first consonant, the first vowel and a final vowel, so `gikaa` behaved exactly like `gia`. The headline figure of "1.21 × 10⁹ context-distinct instructions" counted spellings, not behaviours. One-syllable words actually have 12 × 7 × 8 = 672 behaviours. | High: an overstated claim | `VM().run("sa #5 gikaa")` gives the same planes as `"sa #5 gia"` |
| 2 | **The audio dropped `!` and `~`.** The codec stripped them, and the self-test's normalisation hid this. So the spoken program could mean something different from the typed one. | High: speaking was not fully compiling | `decode(encode("sa #3 gia!"))` gives `sa #3 gia` |
| 3 | **No names, branches or unbounded loops.** v0.1 could not express Euclid's algorithm, a factorial or any search, so it was not Turing complete. | High for "every function in the language" | No construct for a name, a condition or a while-loop existed |
| 4 | **Loops were split by the ring.** Loop bodies were expanded before ring ordering, so copies of a body could be scattered between other words. | Medium: surprising semantics | `lu #3 pia ka #2` ran `ka` between loop iterations |
| 5 | **No limits.** Nothing stopped a runaway loop or a list that doubles each pass. | Medium | Random programs exhausted memory during testing |
| 6 | **Thin codec evidence.** The 8 dB result was one 3.7-second program with one noise seed. | Low | The v0.1 self-test |
| 7 | **The core is sound.** Fuzzing confirmed the codec design: 60 of 60 random programs decoded exactly at 8 dB SNR. The ring rule, the scale-invariant ratios and the 4 × 3 consonant keypad are good foundations. | Strength | Fuzz run in this round |

---

## 2. What v0.2 adds

### 2.1 Three orders, three meanings (fixes 1 and 4)

| Scale | Rule | Example |
|---|---|---|
| Syllables in a word | **Composition.** Each syllable acts on the word's own plane, left to right, using its own vowel as the source. | `pinata` gives `[4]`; `pitana` gives `[1, 2, 3, 4]` (same start) |
| Words in a verse | **Ring.** Outer pairs run first and the centre runs last. A loop and its body form one unit. | `sa #7 gia ta #3` gives 22; `sa #7 ta #3 gia` gives 28 |
| Verses in a book | **Sequence**, separated by a breath `\|` | |

**Measured: does a new order make a new process?** `order_study()` ran 150 random verses through every ordering of their words, and through every ordering of a chained word's syllables.
- **Execution sequence: always distinct.** The ring rule is a bijection, so every written order runs its words in a different order.
- **Final result.** Distinct in 13% of word orderings and 53% of syllable orderings on average.

That is how it should be. Operations on different planes, or two additions, commute in any usable language, so their order cannot change the result. Order changes the outcome exactly when the operations interact.

The **checksum** turns every reordering into a detectable difference: its weights depend on position, so two words swapped give a different checksum.

### 2.2 Names, guards, while-loops: Turing completeness (fixes 3)

| Construct | Meaning |
|---|---|
| `::name … ::` | Defines a word. The body may span several verses. |
| `:name` | Calls a name: user-defined, prelude or Canon. |
| `word?` | Guard: runs only if the accumulator i is positive. |
| `l` + plane, with no number | While-loop: repeats its body while that plane is positive. |
| `g #n` | Gather plus an increment. |
| `n #n` | Subtract (decrement). |

With these constructs, the planes act as the registers of a counter machine with increment, decrement and loop-while-nonzero. That makes the language **Turing complete** (by Minsky's result). The point is demonstrated, not just asserted, by a prelude written in KANON itself using only the 12 primitive operations:

```
::kemu kua | kw #0 | lu :keso | kiw ::        multiply by repeated addition
::keso bwi nu #1 gw ::
::kegi la :keto ::                             Euclid's algorithm
::keto kei kia kae mea ::                      (spelled in ring order: runs kei, mea, kia, kae)
::kehi kyi | ko #1 | ly :keho | kio ::         factorial, built on :kemu
::keho kio :kemu ny #1 koi kay ::
```

The self-test checks 7 × 6 = 42, gcd(35, 20) = 5 and 5! = 120.

### 2.3 The Canon: no imports, ever

There are **44 built-in names**, laid out on the language's own grid. The first consonant names the domain, so a learner can guess where a function lives.

| Domain | Names |
|---|---|
| **k** number | multiply, divide, gcd, primes, square root, power, factorial, product |
| **t** statistics | mean, median, standard deviation, correlation, minimum, maximum, sort |
| **p** geometry | π, φ, polygon angle, star polygon {n/k}, resonances of a cube room, cubits to metres, Heron's formula |
| **b** sequences | Fibonacci, triangular numbers, running sum, differences, distinct values, take, count |
| **d** doors | say as numbers, as **Greek numerals** (isopsephy), as **Hebrew numerals** (gematria); sing as melody |
| **l** logic | not, equal, less, more |
| **m** music | the seven string ratios, ratio → Hz, cents, the Pythagorean comma |
| **r** time | celestial phase stamp, **planetary weekday** |
| **h** seals | checksum |

Everything is inside the runtime: Python's standard library plus NumPy (one call, the median). The browser version uses no library at all.

### 2.4 Speaking is now fully compiling (fixes 2 and 6)

- Every mark is spoken as its own high tone: `! ~ ? : =` at 25, 27, 29, 31 and 33 × f₀.
- **Checksums.** Each verse can end with `=xxxx`: two syllables encoding Σ (position × symbol code) mod 7039, a prime. This catches **every single-symbol error and every swap of neighbours**, because every weight and every code difference is non-zero modulo a prime.
- **Fuzz test.** 120 random programs, including marks, names and numbers, each checksummed:

| Noise (SNR) | Decoded exactly | Errors caught by the checksum | Errors missed |
|---|---|---|---|
| clean / 12 dB / 8 dB | 120 / 120 / 120 | – | 0 |
| 4 dB | 113 | 7 | **0** |
| 2 dB | 3 | 117 | **0** |

### 2.5 Seals: geometry with a job

Every word draws its vowel line on the **heptagon of the week**, with its consonants as marks on the **12-ring of the months**. Every verse draws a ring of its words. Arcs join the pairs that the ring rule executes together, numbered in execution order. The examples' seals are in `lang4d/seals/*.svg`.

The seals have three real uses:
1. **Reading execution order at a glance.** This is the hardest part of the ring rule to see in text.
2. **Visual comparison.** Equal programs draw equal seals.
3. **Spotting transcription slips by eye.** Usually a misheard vowel bends the seal's path, but there are exceptions: a vowel that reappears later in the same word, or a lone closing vowel, draws a line already on the figure. The checksum catches every case.

A seal cannot show which verse comes first, because verses are drawn separately. It is a fingerprint and a diagram, not a cipher.

### 2.6 Limits and safety (fixes 5)

- **Fuel.** A program may take at most 200,000 steps.
- **Plane size.** A plane may hold at most 65,536 values.
- **Numbers.** Non-finite numbers raise an error. The sandbox mark `~` turns any such error into a logged skip.

### 2.7 One night: the integrated learning engine

`course.py` builds **30 steps in the three watches of the night**, each about 4 minutes.

**Watches:**
- **Evening:** the sounds.
- **Midnight:** order.
- **Morning:** names and the Canon.

**Rules, all checked by code:**
- One new element per step, the Echo Ladder rule from rounds 34–35.
- Every example uses only what came before.
- Every exercise has an answer that is run and checked.
- Every example and answer gives the same result in Python and JavaScript (60 of 60).

**Memory aids, all real and ancient:**

| Aid | What it maps |
|---|---|
| **The planetary week** | The vowels in weekday order: i Sunday/Sun, a Monday/Moon, o Tuesday/Mars, e Wednesday/Mercury, u Thursday/Jupiter, y Friday/Venus, w Saturday/Saturn. Every weekday name still keeps this order. |
| **The calendar palace** | The 12 consonants as the 12 months (Nisan … Adar), in four seasons of three: a method-of-loci palace with one room per operation. |
| **Ring composition** | Read from both ends to the middle, the scribes' chiasm. |
| **Chant** | Each step's code is played as audio by the codec itself. |
| **Human pronunciation** | Vowels ah, eh, ay, ee, oh, oo, aw. Digits are their consonant hummed (km, tm, pm …). Marks are breaths and fricatives (tsk, fff, vvv, shh, zzz), so nothing collides with a syllable. |

**The page** (`app/`) contains:
- the course, with a "your turn" checker and progress saved locally;
- a playground with a live interpreter, trace, seal, a ring-order speller, and "hear it spoken", which synthesises the codec in the browser;
- a reference: the palace, the week, the marks and the Canon.

**Parity:** the JavaScript interpreter matches Python on **1,000 of 1,000** random programs. Reaching that took matching Python 3.12's compensated float summation.

**Not yet verified:** that a person can learn KANON in one night. The course is built to that target; it has not been timed with learners.

---

## 3. Corrected claims

| v0.1 claim | v0.2 status |
|---|---|
| ≈ 1.21 × 10⁹ context-distinct instructions | **Withdrawn as stated.** It counted spellings, not behaviours. v0.2 makes every syllable act, and the order study measures how often orderings differ: 13% for words and 53% for syllables in random code, and 100% for the execution sequence. |
| Spoken code compiles, exact to 8 dB | **Strengthened.** Exact on 120 of 120 random programs at 8 dB, every mark carried, and no silent errors down to 2 dB with checksums. |
| Every function within the language | **True for a defined scope.** That scope is the 44-name Canon, the prelude, and Turing completeness. No language contains every function, and KANON does not claim to. |
| Learnable in one night | **A design target, not a result.** It needs a timed learner study, run with the same protocol style as E1, E2 and E5. |

---

## 4. Next steps, ranked by value

1. **A timed learner study.** 10–20 people, the course in one evening, then a delayed test the next morning (write, speak, decode by ear). This is the only way to confirm the one-night claim.
2. **Human-voice front end.** Decode a person speaking KANON, using the round-42/59 formant machinery for vowels and a small consonant classifier. The checksum makes this safe: misrecognitions are flagged, not executed.
3. **Types on planes.** Make plane i a number and plane a text, so that `:dagi` and `:dahe` can round-trip text and gematria checks become first-class.
4. **A type-checked ring.** A static pass that warns when a verse's ring order leaves a word reading a plane nothing has written yet. This is the most common beginner mistake the course reveals.
5. **Error-correcting checksums.** Two more syllables would let the decoder *repair* one misheard syllable instead of only flagging it (a Reed–Solomon code over the 84 syllables).
6. **Seal font.** Generate a typeface in which each word's seal is its glyph, so written KANON can be read as figures.
7. **A Resonance bridge.** Let the sound engine (`RESONANCE.md`, on `main`) play program outputs on the room-tuned drone. The two halves of the project currently live on different branches.
