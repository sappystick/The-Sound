# Audit: the novel claims, with a human-traceable trail

This file is the checkable record behind the project's strongest claims. For each claim it gives:
- the claim and its status after the robustness audit;
- the exact data, script and command, and the output file and numbers;
- the robustness and multiple-testing checks;
- the known weaknesses;
- how a person can verify it by hand.

**The audit was pre-registered.** `robustness/PREREGISTRATION.md` fixed the outlines, parameters and decision rules in commit `1a2d34d` (2026-11-08 10:56 UTC), before `robustness/robustness.py` was written or run. The full run log is `robustness/robustness_log.txt`; the numbers are in `robustness/results.json` and `robustness/highres_results.json`.

## 0. Reproducing everything
| Item | Value |
|---|---|
| Sources | `sources/fetch_sources.sh` clones every open source. Versions used in this audit: SBLGNT/MorphGNT `aaed91e`; OSHB morphhb (WLC) `3d15126`; Swete LXX `26bad3e`; CNTR transcriptions (P66, P75, 01, 03, P46) `4e743a4` |
| Software | Python 3.13.18, NumPy 2.5.3, Pillow 12.3.0, ffmpeg 6.1.1. No other dependencies. |
| Randomness | Every script fixes its random seed (`default_rng(n)`), so reruns give identical numbers. |
| Input hashes | SHA-256 (first 16 hex digits) of every input file are stored in `robustness/results.json → inputs_sha256_16`. |
| Commands | Listed in `robustness/reproduce.sh`. |

## 1. Claim register (status after audit)
| ID | Claim | Status | Strength of evidence |
|---|---|---|---|
| C24 | Blind segmentation of John's voice signal recovers the four-part outline | **HOLDS (pre-registered rule)** | Strong against Brown's outline (p 2.3 × 10⁻⁴ with 10⁶ random cut sets; survives the project-wide correction). Weaker against outlines that start the farewell at 13:1 (Moloney 0.03, Dodd 0.10) |
| C25 | This works for John, not the Synoptics, Acts or Genesis | **HOLDS (pre-registered rule)** | John lowest in 88% of 288 combinations; Synoptics significant in 0–17% of settings; Acts 0%, Genesis 0% |
| C23 | John's clause edges stay visible in unspaced papyri | **HOLDS, revised in round 29** | A letter-level trace of John's asyndeton, not an independent breath signal. Single-test p values (≥ 0.003) do not survive the project-wide correction |
| C3 | Living water at the centre of Leviticus and the Song of Songs | **DOWNGRADED to intriguing** | Fails the every-count rule: Leviticus's centre by verses is 15:7, 6 verses from the phrase, and 13 verses away in the Septuagint. Holds by words (3 verses) and letters (0) in Hebrew; the Song holds in all counts (1–2 verses). Chance corrected for 39 books: 0.007 |
| C11 | Over half of manuscript variants sound identical in Koine | **PARTIAL (pre-registered rule failed)** | 52–60% in P66, 01 and 03; 35% in P75 (only 86 variants). Under Attic pronunciation about 0%, so the effect really comes from Koine sound change |
| C1, C4–C8, C12–C17, C19, C22 | Lexical, textual and descriptive findings | **Verifiable by hand, no p value** | See section 3. These are counts and co-occurrences anyone can check in a concordance |
| C2, C18 | "I am" ring (p 0.009–0.03); "life" at book centres (p 0.001) | **Do not survive the project-wide correction** | Reported p values are above the pooled threshold. C18's p sits at its permutation floor and needs a rerun with more permutations |

## 2. The tested claims in detail
### C24 / C25: the voice-drawn outline
- **Signal.** Per verse:
  - discourse = 1st/2nd-person verbs and pronouns per word;
  - action = 3rd-person indicative narrative verbs (aorist, imperfect, historic present) per word, in verses without direct address.

  Mode = z(discourse) − z(action). Source: SBLGNT morphology. No punctuation and no outline is used.
- **Segmentation.** Exact dynamic programming, minimising within-section variance, into k sections of at least m verses.
- **Score.** Mean distance (in verses) from each cut to the nearest outline break, against random cut sets with the same constraints.
- **Result (baseline: m = 15, full mode, k = 4).** Cuts at 1:16, 13:33 and 18:1, one each at the end of the prologue, the start of the farewell discourse and the arrest.

  | Outline | p (5,000 sets) | p (1,000,000 sets) |
  |---|---|---|
  | Brown (farewell from 13:31) | <0.0002 | 0.00023 |
  | round-30 conventional | 0.001 | 0.0010 |
  | Moloney | 0.032 | 0.031 |
  | Dodd | 0.105 | 0.101 |

- **Grid (Brown, 9 parameter combinations).** p < 0.05 in 9 of 9. The cuts move by a few verses: 1:13–1:16, 13:33 every time, and 18:1 or 18:10. One setting (m = 25) replaces the prologue cut with 10:39.
- **Comparison.**
  - John has the lowest p in 88% of 288 outline × parameter combinations.
  - Share of settings with p < 0.05: Mark 17%, Matthew 0%, Luke 0%, Acts 0%, Genesis (Hebrew, wayyiqtol against 1st/2nd person) 0%.
- **Secondary (k = 5).** John is significant in 0% of settings. The fifth cut falls inside the signs section (7:52 or 8:56) rather than at an outline break. The effect is a four-part effect.
- **Known weakness: partial circularity.** The farewell discourse is by definition the stretch where Jesus speaks at length, so a speech-based signal will tend to find its start. The claim rests on two things together: the cuts land exactly at named breaks, and the same signal fails in the other books. The result is strongest for outlines that begin the farewell at 13:31.
- **Check by hand.** Read John 13:31–33 ("Now is the Son of Man glorified … Little children, yet a little while I am with you") and 18:1 ("When Jesus had spoken these words, he went forth …"). The speech-to-narration switch is audible at both points.
- **Files.**
  - `robustness/robustness.py` (section C24/C25);
  - `robustness/highres.py`;
  - `code/analysis/round30.py`, `round31.py`;
  - `robustness/results.json → segmentation` (every setting, its cuts and p).

### C23: clause edges in unspaced letters
- **Method.** The letters of each manuscript are joined with no spaces, then segmented by an MDL compression model and by byte-pair encoding. Boundary rates are compared for the same word form at a clause end and elsewhere.
- **Result.** Positive in all four John manuscripts; null in Luke by the same P75 scribe; null or negative in Mark (01, 03) and in Paul (P46).
- **Revision.** Round 29 showed that clauses opening with καί or ὁ δέ get glued onto the previous word, hiding the edge. Mark and Luke open more clauses that way. So the finding is John's asyndeton seen at letter level.
- **Weakness.** The clause ends come from SBLGNT's modern punctuation, aligned to each manuscript.
- **Files.**
  - `code/analysis/self_structure.py`, `round28.py`, `round29.py`;
  - `round28_results.json`, `round29_results.json`.

### C3: living water at the centres
| Count | Leviticus centre | Distance to phrase | Song of Songs centre | Distance |
|---|---|---|---|---|
| Hebrew verses | 15:7 | 6 | 4:14 | 1 |
| Hebrew words | 14:47 | 3 | 4:16 | 1 |
| Hebrew letters | 14:50 | 0 | 4:16 | 1 |
| Greek verses | 15:7 | 13 | 4:14 | 1 |
| Greek words | 14:45 | 5 | 5:1 | 2 |

The phrase מים חיים occurs in Genesis, Leviticus (14:5, 14:6, 14:50–52, 15:13), Numbers, the Song (4:15), Jeremiah and Zechariah. The chance that 2 or more of the 39 books have it within 3 verses of their verse-centre is 0.007. That figure is not corrected for the many other motifs looked at in the original centre catalogue.

**Verdict:** striking in Hebrew letters and words, and in the Song, but the "every count" claim is false. Downgraded to intriguing.

**Check by hand:** count the verses of Leviticus (859 in WLC). The middle verse is in chapter 15; the cleansing ritual with living water is 14:5–6 and 14:50–52.

### C11: variants that sound the same
| Pronunciation | P66 | P75 | Sinaiticus | Vaticanus |
|---|---|---|---|---|
| Koine (late), original setting | 60% | 35% | 53% | 53% |
| Koine | 59% | 35% | 52% | 53% |
| Attic | 0% | 0% | 0% | 1% |

The Attic column is the control. With classical pronunciation, almost every variant changes the sound. So the identical-sound variants are explained by Koine sound changes (itacism, the merger of ο and ω, loss of vowel length): scribes wrote as they heard. The pre-registered rule required more than 50% in every manuscript; P75 fails it with few variants. Script: `code/analysis/ms_sound.py` (era switch `MS_ERA`, default unchanged).

## 3. Lexical and descriptive findings (checkable in any concordance)
| Claim | How to check |
|---|---|
| Prologue centre in 1:12 (P66, P75, 01, 03, Syriac, Coptic, Latin) | Count syllables of 1:1–18 in each witness; the midpoint falls in verse 12 (`earliest_text.py`, `aramaic_prologue.py`) |
| σχίζω/σχίσμα: the crowd divided 3 times (7:43, 9:16, 10:19); "let us not tear it" (19:24); "the net was not torn" (21:11); LXX Leviticus 21:10, the high priest shall not tear his garments | Concordance |
| 153 fish; Ezekiel 47:10, fishermen from En-gedi to En-eglaim. The only fishing verse in the Hebrew Bible whose gematria yields 17/153 (Emerton) | Ezekiel 47:10; gematria of גדי (Gedi, 17) and עגלים (Eglaim, 153) |
| Hyssop, blood and water together only in Leviticus 14, Numbers 19, John 19 and Hebrews 9 | Concordance |
| "I am the + image" in 47% of John's "I am" sayings, against 4% in the Septuagint | `iam_forms.py` |
| John's noise share 0.326, against 0.344–0.347 for the Synoptics | `acoustic.py`; depends on the engine's Koine phoneme model |

## 4. Multiple testing across the whole project
- **Narrow pool.** 40 p-values written in DISCOVERIES.md. Benjamini–Hochberg at q = 0.05 gives a threshold of 0.028; 23 survive.
- **Wide pool.** 5,767 p-values stored in 56 results files, including descriptive sub-tests. The BH threshold is 0.00075 (Bonferroni would be 0.000009).
  - Survives: C24 against Brown (0.00023, high-resolution).
  - Does not survive: claims whose permutation p sits at its floor of 0.001, and claims at p ≥ 0.001.
- **Honest summary.** One structural claim (C24/C25) passes the strictest correction. Several others are suggestive and pre-registered for replication. The lexical findings stand or fall by inspection, not statistics.

## 5. What this audit cannot settle
- **The outlines** in the pre-registration were summarised from memory of the published works (Brown 1966/70, Moloney 1998, Dodd 1953, Bacon 1930, Kingsbury 1975). They must be checked against the printed books.
- **The pronunciation model** (engine) is a reconstruction. Sound-based measures inherit its assumptions.
- **Punctuation-based measures** (C23) depend on a modern edition.
- **No outside expert** has yet reviewed the work.

## 6. Spoken reconstruction (video)
`video/render_john_video.py` renders every verse with the engine, using the same settings as the sound model: Koine, declaimed, synagogue room, the self-found section pauses. The render manifest is `video/out/render_manifest.json` and the verse timings are `video/out/john_timeline.json`. Each video frame shows the data for its verse. The synthesis is a formant model of the phonology, not a recording of a voice.

## 7. Voice v2 (round 32)
See `code/voice/README.md`.
- The rulebook (`code/voice/delivery_rules.json`) separates evidence rules from interpretive rules; the interpretive layer can be switched off (sample version B).
- Pitch validation: planned against measured, median error 0.20–0.25 semitones.
- Place data: OpenBible.info (CC BY 4.0), `data/john_geo.json`.
- Voice model: Piper `el_GR-joy-medium`, a Modern Greek voice.
