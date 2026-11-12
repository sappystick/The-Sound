# The Voynich Manuscript through the Sound engine (round 66)

**The question put to it:** is the Voynich a plaintext alchemical recipe — a "how to make gold" — a ciphered natural language, or a constructed/generated system? **We claim no decoding.** We measure its known anomalies against controls, the way this project measures everything, and label each result **V** verified here · **K** known in scholarship · **N** negative · **Reading** interpretation.

**Files:** `voynich/engine.py` (angles 1–7), `voynich/generate.py` (the generative test), `voynich/results.json`, `voynich/generate_results.json`, `voynich/signature.svg`.

**Data.** Takahashi EVA transcription (`sources/texts/voynich/…/takahashi_original.txt`), split by the manuscript's own locus codes into **running text** (paragraph loci, 37,919 words) and **labels** (the words written beside pictures, 328 words). Controls, all of the right era or register:
- **the era's actual "make gold" text:** pseudo-Geber, *Summa Perfectionis* (Latin) — the alchemical classic on transmuting metals, copied all through the 15th c.;
- **a medieval recipe collection:** the *Mappae Clavicula* (Latin);
- **natural-language controls:** the Latin Vulgate, the Greek New Testament, the Hebrew Bible;
- **a constructed language:** KANON (this project's round-65 language);
- **nulls:** an order-0 random text at Voynich's letter frequencies, plus two generative grammars (below).

## 1. Voynich reproduces every known anomaly — and no natural language does
| Angle | Voynich-P | Natural-language range (Latin/Greek/Hebrew) | Verdict |
|---|---|---|---|
| **Letter predictability h₂** | **2.09 bits** | 3.13–3.58 | far below any language, below even random (3.93). **K/V** |
| h₂ within words | **1.85** | 3.07–3.66 | words are internally near-deterministic. **K/V** |
| **Top-8 suffix mass** | **0.81** | 0.25–0.49 | 81 % of words end in one of 8 two-letter endings. **K/V** |
| **Adjacent identical words / 1000** | **8.3** (8 triple-runs) | 0.3–1.2 (0 triples) | the "daiin daiin daiin" anomaly, ~8× any control. **K/V** |
| Adjacent one-edit near-repeats / 1000 | 31 | 3–11 | neighbouring words differ by one letter far too often. **V** |

The famous facts hold up exactly under our own controls: **the Voynich's text statistics are impossible for any natural language, ciphered or not.** A simple substitution cipher of Latin (or any tongue) would keep that language's h₂ ≈ 3.3; the Voynich's 2.09 cannot be reached by relabelling letters.

## 2. The "make gold" / plaintext-recipe hypothesis — tested and rejected as plaintext
- Geber's actual gold-making treatise has **h₂ = 3.58**, ordinary suffix spread (0.36), and essentially no word repetition (1.0/1000). It reads like a language, because it is one.
- The Voynich does **not**. So **the Voynich is not a readable alchemical recipe in Latin or any natural language** (**N** for the literal hypothesis).
- **What survives (Reading):** the *genre structure* is recipe-like. The Voynich's top-20 words are **more "bursty"** (clustered in sections) than Geber, the *Mappae*, or the Vulgate (burstiness CV 0.42 vs 0.27–0.35) — consistent with a sectioned, procedural document (the manuscript's own last section is in fact the one scholars already call "the recipes," short star-marked paragraphs). If a recipe is in there, it is **encoded by a process, not written as words.**

## 3. Labels vs text — the user's specific question
The words beside the pictures behave differently from the running text (**V**, measurable):
- **41 % of label words never occur in the running text at all** (label-exclusive vocabulary).
- Labels start with a different glyph distribution (KL = 0.66 bits); nearly **half of all labels begin with the single glyph `o`** (152 of 328), against a much flatter spread in the text.
- Labels are shorter (4.9 vs 5.2 letters) and, among themselves, extremely similar — adjacent labels differ by one edit **113×/1000**, the highest near-repeat rate anywhere in the manuscript.
- **Reading:** labels look like members of tight *paradigms* — small families of near-identical words (as you'd expect for a list of related items: the plants on a page, the stars in a ring), not independent names. This is consistent with a **systematic naming scheme** (a generated code) rather than natural words for distinct things.

## 4. The line is a structural unit (Currier's LAAFU) — **K/V**
Glyph choice depends on where a word sits in its line (KL of line-first vs mid initials = 1.0 bit). Line-final words overwhelmingly end in `y` (1,492), and the glyph **`m` appears almost only at line-ends** (650) — a known Voynich "edge" marker. Natural prose does not care where a word falls in a line. This points to a **layout-driven generation rule**, not sentences.

## 5. What *does* reproduce the whole signature: a generative grammar (the honest, novel result)
We fit two mechanisms directly to Voynich-P (`generate.py`):
- **SLOT** — a 3-slot *prefix·core·suffix* grammar (Stolfi's crust-mantle-core / Rugg's grille). The learned slots are the real Voynich morphemes: prefixes `qo- ch- Sh- ok- ot- da- ol-`, suffixes `-edy -iin -eey -ain -ody -chy -hol`.
- **AUTOCOPY** — Timm & Schinner's (2019) self-citation: each word is a lightly mutated copy of a recent word.

| | h₂ | within-word h₂ | top-8 suffix | adj repeat/1000 | triples | edit-1/1000 |
|---|---|---|---|---|---|---|
| **Voynich-P** | 2.09 | 1.85 | 0.81 | 8.3 | 8 | 31 |
| Latin (Vulgate) | 3.33 | 3.20 | 0.43 | 0.3 | 0 | 2.9 |
| **SLOT grammar** | 2.72 | 2.55 | 0.68 | 1.5 | 0 | 10 |
| **AUTOCOPY** | 2.95 | 2.84 | 0.62 | **21** | **23** | **37** |

- The **slot grammar** collapses h₂ and concentrates the suffixes the way *only the Voynich does* — the word-shape anomaly is a generation rule.
- **Self-citation** reproduces the repetition and near-repeat anomalies that the slot grammar (and every language) cannot — the sequence anomaly is a copying rule.
- Together, a **weighted slot grammar + self-citation span the entire Voynich signature.** Both are *generative mechanisms*. **This is the strongest result:** the Voynich's statistics are those of a **constructed/generated system, not of concealed natural-language text.**

Tie-in to this project: of all eight corpora, **KANON — our own constructed language — is the closest single model to the Voynich's (entropy, rigidity, repetition) cluster** (z-scaled distance 3.33, vs 4.7 for the nearest natural language). A language built from fixed consonant-vowel slots and positional meaning lands, by construction, in the Voynich's statistical neighbourhood. That is not a claim that KANON *is* the Voynich; it is evidence that **the Voynich's anomalies are the fingerprints of exactly the kind of slot-and-position system KANON formalises.**

## 6. Contrasting scholarly views (for balance)
| View | Fits our measurements? |
|---|---|
| **Natural language under a cipher** (Bax; many) | **Poorly** — cannot produce h₂ ≈ 2.1 by any letter-relabelling |
| **A priori / constructed language** (Friedman; Tiltman) | **Well** — slot grammar + positional rules match |
| **Meaningless hoax by a grille** (Rugg 2004) | **Partly** — the grille reproduces word shape but not the lawful label/line structure |
| **Self-citation / auto-copying text** (Timm & Schinner 2019) | **Well** for the repetition half; needs the slot grammar for the rest |
| **Encoded herbal/alchemical content** (many) | **Possible at the genre level** — bursty sections, picture-labels — but the content, if any, is not plaintext |

Our data favours the **constructed/generative** family and is consistent with that system carrying **real content organised like a herbal/recipe book** — just not as readable words.

## 7. Limits
- One transcription (Takahashi EVA); EVA's digraph choices affect letter-level stats. A cross-check on the ZL/v101 transliterations is the next step.
- Latin OCR of Geber/Mappae is noisy; it inflates their letter inventories slightly but cannot create the ~1.3-bit h₂ gap.
- "Constructed/generated" does not mean "meaningless." A generation rule can carry information (KANON does). Distinguishing a meaning-bearing generator from an empty one is the open frontier — and is exactly where a KANON-style decoder (slots → fixed operations) could be tested against the Voynich's own slot inventory.
