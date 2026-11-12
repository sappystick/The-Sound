# The Voynich investigation: one index (rounds 66, 75–91)

This is the single entry point for the Voynich work. Two working accounts carried it forward, one through round 81 and one through round 90. Their branches were merged at round 91, and everything now runs from `main`. Detailed records are in each round's file (`mysteries/ROUNDnn.md`) and in `DISCOVERIES.md` sections BB–BR. The operating plan is `PLAN.md`.

## The current framing
The Voynich is treated as a **self-contained, one-of-a-kind system**.
- Rounds 66–87 compared it with every outside reference available: natural languages, ciphers, Latin herbals, a recipe book, plant shapes and zodiac geometry. **None of them unlocks it.**
- From round 88 on, the work is **reference-free:** it asks the text itself what structure it holds that our best null-content model cannot produce.
- Outside material is now used only in two ways:
  - **as controls,** to show a method can detect what it claims;
  - **to look for the author's influences.**

## The chain of discovery
| Round | Step | Result | Grade |
|---|---|---|---|
| 66 | Anomaly signature against era controls | Letter predictability (h₂ 2.09) and word repetition (8×) are impossible for any natural language or simple cipher. Not a plaintext alchemical recipe | K/V, N |
| 75 | Topic and lines | Vocabulary follows the illustration type within hand and language (86–91% against 68%). Lines are units like verses | B |
| 76–77 | Against Macer, *Circa instans* and Apicius | Not written like a herbal that names its plants (17% name rate against 42–85%). Pharmaceutical labels sit **below** chance in their own page text | B |
| 78 | Cipher simulations, repeats, labels | No classic cipher of Latin reproduces the profile. Repeats are common words plus one-glyph drift. 42% of labels are orphans | B |
| 79 | "Keys" and held-out test | The f49v letters, the f57v ring and the zodiac labels are not keys. No model fitted on even pages reproduces odd pages | B / N |
| 80–81 | Generators on held-out pages | A short-range copy + drift + slot-grammar generator comes closest (2.5 ± 0.4). The learned slots are qo-, ch-, ok-, ot- / -y, -dy, -iin, -edy, -ain | B |
| 82 | Unified plan; where the meaning lives | In Currier B, the **root** carries the topic signal | B (pilot) |
| 83 | The 231-gates test | The text is a **directional slot system**, not free letter-combination. This rules out Sefer Yetzirah-style tzeruf and Llull wheels as the mechanism. The slot grammar covers 86.5% of held-out word mass | B / N |
| 84 | Zodiac labels against angle | No positional code (p 0.49) | N |
| 85–86 | Labels and plant drawings | Labels are weakly correct, not displaced. Plant shape (39 measured features) does **not** track the text (Mantel r ≈ 0, p 0.53) | N |
| 87 | Section-conditioned generator | Section conditioning is necessary and sufficient for the topicality. Drawing-as-code ruled out | B / N |
| **88** | **Reference-free long-range information** | **The text carries about 2× the long-range information of its null-content generator, and about 13× its shuffle.** There is real mid-range organisation | **B (pivotal)** |
| 89 | Hidden-state model; content words | Eight drifting states do **not** reproduce it. The organisation lives in **bursty content words** (73% of frequent words clustered; each concentrated in one section) | B |
| 90 | Concept clusters | The content words form 2 real communities that **re-derive the Currier A/B split** from co-occurrence alone. The association goes beyond morphology. Finer sub-topics are weak, in the herbal section only | B |
| **91** | **A/B internal Rosetta (pre-registered)** | **INCONCLUSIVE:** word alignment from co-occurrence fails its own positive control, and even matches herbal-A with itself only 3% of the time. Exploratory: **38%** of the A/B difference is a systematic ending shift (-or → -edy, -ol → -dy); the rest is word choice | Pre-registered: inconclusive; exploratory: B |

## The current model (each layer measured)
1. **Surface:** a directional prefix–root–suffix slot grammar, plus short-range copying and one-glyph drift.
2. **Section and language:** word pools conditioned on section. Currier A and B are two dialects or registers of one system. They share a vocabulary with shifted endings and differ in word choice.
3. **Content-word layer:** bursty words with real association beyond grammar and section. They carry the long-range information that no generator reproduces. **This is the target.**
4. **What is not there:** no object-level reference (individual plants, label positions), no outside key, no classic cipher.

## What is solid, and what is not
- **Solid:**
  - the anomaly signature;
  - topic-following vocabulary;
  - the slot grammar;
  - the long-range information beyond the generator;
  - the A/B structure;
  - every negative listed above.
- **Not established:**
  - that the content-word layer carries *meaning* rather than an elaborate construction;
  - any word-level correspondence between A and B.
- **Methodological finding (round 91):** at this corpus size, word distributions cannot align two vocabularies. Any statistics-only "translation" of the Voynich, by us or anyone else, must first pass this control.

## Next moves (in order)
1. **Phrase anchors** (from round 91): find multi-word sequences that recur in both A and B after the ending rules are applied. These would be aligned units that need no statistical matching. This is the only remaining route to an internal Rosetta.
2. **Information budget** (PLAN move 6): how many bits per page remain after the generator is removed. This sets the ceiling on any hidden content.
3. **Low-rate channels** (move 3): line-initial glyphs, gallows positions, every-nth word, corrections. These would show whether a sparse message hides inside the filler.
4. **Unique-system controls** (move 4): run the same measures on other one-off systems (Rohonc Codex; a known asemic work, used qualitatively) so the verdict is calibrated against things like it, not against languages.
5. **Numeric content** (move 5): the zodiac, rosette and star pages under the project's calendar and period engines.
6. **Influences:** which contemporary practices could have produced a directional slot system. Abbreviation systems and nomenclators remain; letter-combination mysticism is ruled out (round 83).

## Tools
| Script | What it does |
|---|---|
| `voynich/engine.py`, `voynich/generate.py` (round 66) | Anomaly signature against era controls; first generators |
| `voynich.py` | Topic prediction within hand and language; line-position information |
| `herbal.py`, `controls.py`, `textmeasures.py` | Shared measures; Macer, *Circa instans*, Apicius and label controls |
| `cipher_tests.py`, `repeats.py`, `keys.py` | Cipher simulations, repeat analysis, the key tests |
| `heldout.py` | Even/odd held-out benchmark for every generator, with replicates |
| `localize.py`, `stages.py`, `gates.py` | Where meaning lives; pipeline stages; the 231-gates test |
| `stage_c.py`, `mislabel.py`, `morph.py`, `phyllotaxis.py` | Zodiac-angle anchors, label displacement, plant morphometry, leaf geometry |
| `section_gen.py`, `longrange.py`, `hmm.py` | Section-conditioned generator, long-range information, hidden-state model |
| `concepts.py` | Content-word co-occurrence communities with four controls |
| `rosetta.py` | The A/B Rosetta test (pre-registered), refinement and rewrite rules |

## Data
Run `sources/fetch_sources.sh`. The Voynich data:
- the ZL3b-n reference transliteration (voynich.nu), which carries the page metadata: $I illustration, $L language, $H hand, $Q quire;
- the Takahashi EVA and v101 transcriptions;
- the spatial label corpus;
- pseudo-Geber.

Scripts written before round 82 take the IT2a transliteration as an argument. The Latin herbals and the Greek and English Bibles used as controls come from Wikisource, the BIU Santé scan, SBLGNT and BSB.
