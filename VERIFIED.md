# Verified discoveries: master update (round 39)

This file pulls together every result from rounds 1–39. Each one is filed by the strength of its evidence, and each points to the code that reproduces it. The rules are the same as in `AUDIT.md`:

- A result counts as **verified** only if it passed a pre-registered rule, or survived the project-wide correction (Benjamini–Hochberg over 5,767 p-values, threshold about 0.00075), or is a plain count anyone can check by eye.
- Following the brief, physical "power" claims are recorded as claims. They are not judged real or unreal here. Only their textual, numerical and acoustic content is tested.

---

## 1. Closed in this round

| Open item | Result | Code |
|---|---|---|
| "Life" at the letter-centres of Hebrew books. The earlier p of 0.001 sat at the permutation floor. | **Exact p = 0.00082.** 5 of 39 book centres (Exodus, Leviticus, Ruth, Song of Songs, Ecclesiastes) against 0.86 expected. It survives Holm correction over the 8 motifs tested. It sits just *above* the pooled project threshold (0.00075). The other 7 motifs (water, light, heaven and earth, tree, gate, temple, name of YHWH) are all at chance, so this is not a general "centres are special" effect. | `experiments/followups.py` F1 |
| E7: the PGM XIII vowel square rendered and measured | Rendered as `experiments/audio/e7_vowel_square.mp3` (70 s on a held 110 Hz note, temple reverb). The square is a complete rotation: every direction starts on a different vowel. Each direction's overtone melody is therefore the same 7-note figure (harmonics 5, 6, 5, 7, 11, 19, 17) started at a different point. This is **structural by construction, not an extra discovery**: it confirms the square is a cyclic acoustic pattern, a canon of one overtone tune. | F2 |

---

## 1b. Round 40 (see `ROUND40.md`; sound engine in `RESONANCE.md`)

- **John 13:31–33, not 13:1.** Two independent speech signals both cut John's farewell at 13:32–33: the BSB translators' quotation marks (knowing no Greek) and Greek person morphology.
- **Two more voice-drawn outlines.**
  - Revelation: 4:1 and 22:6 hit exactly, p < 0.0001.
  - Job: the dialogue and Job's speeches, p = 0.0001.
  - Deuteronomy, Hebrews and Acts give the expected nulls.
- **Ketiv and qere.** 88% of the 1,245 written/read pairs are sound-alikes: the Hebrew parallel of C11.
- **Masoretic midpoints.** The Talmud's letter and word midpoints for the Torah are 61–93 verses from the computed ones. The verse midpoint matches the Masorah (Lev 8:8–9). The Psalms verse midpoint is within 2 verses.
- **"Life" at the centre does not replicate in Greek** (NT p 0.63, LXX p 0.27). It is a Hebrew letter-text effect only.
- **666 and 616.** Both are Nero Caesar, spelled the Hebrew way and the Latin way. 153 = *bene ha-Elohim* = T17. *Ichthyes* and *to diktyon* both = 1224 = 8 × 153.
- **Holy-of-holies cubes.** The debir puts 177 modes on 33 frequencies, against 79 for an ordinary room. Its strongest voice-range mode is 123.4 Hz.
- **Breath units.** Psalm and Proverbs half-verses are short and even (7–8 syllables). Chanted, they imply about 6–7 breaths a minute.

---

## 2. Verified discoveries

### Tier A: passed the strictest test

1. **The voice draws John's outline (C24/C25).**
   - **Finding.** Mark each verse as narration or direct speech and segment that signal blindly. The cuts fall at 1:16 / 13:33 / 18:1, which recovers the prologue, signs, farewell and passion.
   - **Strength.** Against Brown's outline, p = 2.3 × 10⁻⁴ over 10⁶ random cut sets, and it survives the pooled correction. John has the lowest p in 88% of 288 settings.
   - **Controls.** Mark, Matthew and Luke reach significance in 0–17% of settings. Acts and Genesis reach it in 0%.
   - **Meaning.** John's architecture is audible. A listener hears the sections change because who is speaking changes.
2. **The prologue's centre is 1:12** ("to them gave he power to become children of God"). This holds by letters, words and verses, in every manuscript tested (P66, P75, 01, 03, SBLGNT).
3. **Mark keeps Jesus' Aramaic; Luke drops it.**
   - Mark keeps all 4 Aramaic sayings untranslated: talitha koum, ephphatha, abba, eloi eloi lema sabachthani.
   - All four come at a healing, a prayer, or the death.
   - Luke turns all four into Greek or leaves them out. This is a count, checked against SBLGNT.

### Tier B: pre-registered and holds, with a stated limit

4. **Clause edges survive in unspaced papyri (C23).**
   - **Finding.** In P66, the letters run on with no spaces, yet the edges between John's clauses still show statistically.
   - **Control.** Luke, copied by the same P75 scribe, shows nothing.
   - **Limit.** This is a trace of John's asyndeton (clauses with no joining word), not a separate breath signal. Single-test p ≥ 0.003.
5. **Many variants sound alike (C11, partial).**
   - 52–60% of the variants in P66, 01 and 03 sound the same in Koine pronunciation, against about 0% in Attic.
   - So copying by ear, or by inner dictation, is a large share of how the text changed.
   - The pre-registered >50% rule failed for P75, at 35% (n = 86).
6. **"Life" at book centres.** Exact p = 0.00082 (see §1): Holm-significant, but just short of the pooled threshold.
7. **"Living water" at the centre of Leviticus and the Song (C3, downgraded).**
   - It holds by Hebrew letters and words. The Song holds in every count.
   - It fails by verses in Leviticus and in the Septuagint.

### Tier C: plain verified facts (counts and computations)

| Domain | Fact |
|---|---|
| Spoken delivery | "Voice" (φωνή) occurs **0.97 per 1,000 words** in John, against 0.38–0.72 in the other Gospels. The modelled breath pacing runs 3.5–12.7 breaths per minute across sections. The model's self-found major pauses fall at 1:16, 13:33 and 18:1. |
| Sacred formulas | 79% of the sounds in formula words are voiced, against 67% in the surrounding narrative. |
| Counts | "And God said" occurs 10× in Genesis 1. *Qol YHWH* ("the voice of the LORD") occurs 7× in Psalm 29. |
| Textual | The angel stirring the pool at Bethesda (John 5:4) is **absent** from P66, P75, 01 and 03. |
| Sound | *Talitha* (Mark 5:41) and *Tabitha* (Acts 9:40) differ by one sound, in two parallel raisings. |
| Sanctuary acoustics | A cube (Holy of Holies, 20 × 20 × 20 cubits) packs its room modes into **15 distinct frequencies**. An ordinary room of equal volume has 56. Cube rooms resonate on few, strong notes. |
| Vowels | On a held note, α, ε and η fall exactly on harmonics. The PGM XIII square is a complete 7 × 7 rotation over seven directions. |
| Isopsephy | **365 = Abrasax = Meithras = Neilos.** The chance that three names share one value is about 0.0009. Bainchōōōch = 3663. |
| Testament of Solomon | **Emmanuel = 644**: the text's own "χμδʹ" checks against the letter values. Raphael = 640 also checks. |
| Testament of Solomon, continued | The names in the ring recipe are 78% vowels, against 55% in ordinary Greek. The 36 decans' cures run from spoken, to written, to material. The cornerstone episode quotes Ps 118:22 and has a wind-spirit carried in an *askos* (wineskin). There are cross-links to Tobit (the fish liver and heart) and to Exodus 28 (the engraved stones). |
| PGM | ABLANATHANALBA appears 16 times, a true palindrome in Greek letters. |
| Gematria (with controls) | Serpent = Messiah = 358. Ark = Urim = 257. Love = one = 13. That is 3 equal pairs against 0.6 expected, but the term list was chosen by us. Sums (A + B = C) are at chance. |

### Not supported, or not surviving correction (kept for honesty)

- The "I am" ring structure: does not survive the pooled correction.
- Any physical effect of a word, vowel or name: **untested**, because no live participants have taken part yet. Protocols E1, E2 and E5 are built and the app is live, but no data has been collected.
- Akouo and Sala (the learning method and the universal language): built, but not tested on learners.

---

## 3. Trickle effects: areas these findings touch

| Discovery | Areas affected | What can be updated |
|---|---|---|
| Voice-drawn outline (A1) | Johannine structure studies; commentary outlines; performance criticism; lectionary division | Section breaks can be justified from the text's own speech signal rather than from theme. 13:33 (not 13:1) is the data-preferred start of the farewell, which is a testable claim against Moloney and Dodd. |
| Prologue centre 1:12 (A2) | Chiasm studies of John 1:1–18; theology of "becoming children" | The centre is stable across manuscripts, so arguments built on it are not edition artefacts. |
| Aramaic retention (A3) | Synoptic problem (Markan priority, Luke's audience); healing and prayer practice; the "words of power" thesis | Untranslated sound clusters exactly where effect is claimed. This is a textual fact any theory of Mark must explain. |
| Clause edges in papyri (B4) | Papyrology; scribal habits; ancient reading aloud (*scriptio continua*) | Readers of unspaced text could still recover John's clause rhythm. That supports reading aloud as the designed mode. |
| Homophone variants (B5) | Textual criticism (the cause of variants); critical apparatus weighting; the Koine phonology timeline | Variants that sound alike should be classed as transmission by ear and weighted lower as evidence of meaning change. |
| Centre motifs (B6, B7) | Hebrew Bible compositional studies; Masoretic counting traditions (the scribes' marking of middle letters and verses) | "Life" at centres is now precise enough to compare against the Masoretic notes on book midpoints. |
| Sanctuary acoustics, vowels, isopsephy | Temple archaeology; liturgical acoustics; history of magic (PGM, Testament of Solomon); early Christian–magical overlap (Emmanuel 644) | Stated numbers in ritual texts can be verified rather than guessed. Built spaces described in texts can be modelled acoustically. |
| Spoken model, Akouo, Sala | Language pedagogy; reconstructed pronunciation; audio Bible production | A data-driven delivery (pauses, breath, speaker) can be produced for any text the same way. |

---

## 4. Open investigations with strong leads

1. **E1, E2, E5 with real participants.** Vowel and breath effects on heart-rate variability (HRV), perceived resonance, and the formula listening test. The protocols and app (`experiments/PROTOCOLS.md`, the E5 artifact) are ready. *Lead:* the breath pacing of 3.5–12.7 per minute overlaps the 6-per-minute resonance band known from HRV research.
2. **Life at centres against the Masoretic midpoint notes.** Do the scribes' marked midpoints coincide with the 5 hit books?
3. **The 13:33 versus 13:1 boundary.** Replicate with independent speech tagging (a second annotator, or another edition's quotation marks).
4. **Homophone variants in the Hebrew Bible.** Ketiv and qere pairs ("written" versus "read" forms) are the natural parallel: how many are sound-alikes?
5. **Magical-text corpus extension.**
   - Preisendanz's Greek edition (the PDF was restricted here).
   - Sepher ha-Razim.
   - The Sword of Moses.
   - Coptic magical papyri.
   - For each, run the same stated-number check, vowel ratio check and remedy-mode count.
6. **Acoustics of other described spaces.** Solomon's temple (1 Kings 6), Ezekiel's temple (Ezekiel 40–48) and the New Jerusalem cube (Revelation 21:16) can be modelled with the same room-mode code.

---

## 5. How to apply the methods to undiscovered ground

| Method (built here) | Old Testament | New Testament | Beyond |
|---|---|---|---|
| **Voice-mode segmentation** (`code/analysis/round30.py`) | Deuteronomy (Moses' speeches), Job (dialogue against narrative), Jeremiah, Ezekiel: does the speaker signal draw their outlines? | Hebrews, Revelation (who speaks: the angel, the Lamb, the elders), Acts speeches | Plato's dialogues, Homer, the Qur'an (speaker shifts) |
| **Letter-stream segmentation of unspaced text** (round 29) | Dead Sea Scrolls (1QIsaᵃ) | All CNTR class-1 papyri: P46 (Paul), P45, P72 | Any *scriptio continua* inscription |
| **Untranslated-sound retention** | Hebrew words kept in the Septuagint (hallelujah, amen, sabaoth): where do they cluster? | Maranatha (1 Cor 16:22), abba (Rom 8:15, Gal 4:6), hosanna | Kept words in the Vulgate, Peshitta and Coptic versions |
| **Centre-motif test, exact** (`followups.py`) | Run per section (Torah portions, psalm books) | Run per NT book in Greek letters | Gilgamesh tablets, Avesta |
| **Homophone-variant test** (C11) | Ketiv and qere; Dead Sea Scroll against MT spellings | All variant units in other papyri | Homeric variants |
| **Stated-number verification** (`power/codes.py`) | Every number tied to a name (e.g. 318 = Eliezer, Gen 14:14) | 666 / 616 (Rev 13:18) with the chance control; 153 fish (John 21:11) | All PGM, Testament of Solomon and Sepher ha-Razim number claims |
| **Room acoustics** (`experiments/e3_e4_compute.py`) | The Tabernacle, Solomon's temple, Ezekiel's temple | The New Jerusalem cube | Hypogeum of Ħal Saflieni, King's Chamber |
| **Breath pacing** | Psalms (by colon length), Lamentations (acrostics) | Hymns: Phil 2, Col 1, John 1 | Liturgies, chants, mantras |
| **Echo Ladder courses** (`learn/`) | Hebrew Genesis 1–11 | Mark in Greek | Any text and language (the engine is language-agnostic) |

---

## Reproduce

```
python3 experiments/followups.py <morphhb/wlc dir>     # round 39
bash robustness/reproduce.sh                           # audit
```

The other scripts are as listed in `AUDIT.md`, `POWER.md` and `POWER_CODES.md`.
