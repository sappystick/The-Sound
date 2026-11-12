# The Voynich investigation — unified plan (round 82)

This is the operating plan for the next phase. It harnesses everything established so far (rounds 66, 75–81, and the
round-82 pilot below), aligns every engine in the project onto one target, and defines a staged decipherment pipeline
with pre-registered gates so we never join the 100-year parade of false "solutions."

---

## 0. Where we stand (synthesis)

| # | Established finding | Status | Round |
|---|---|---|---|
| S1 | Letter-predictability h₂ ≈ 2.1 bits — far below any natural language; **no letter-cipher of any language reaches it** | **K/V** | 66 |
| S2 | A real "make-gold" alchemy text (Geber) and real herbals (Macer, *Circa instans*) read like language; the Voynich does **not**. Not plaintext | **N** for plaintext | 66, 76–78 |
| S3 | Words = **prefix + root + suffix slots** (learned from data: `qo- ch- ok- / -aiin -edy -ody`) + **self-citation** (copy a nearby word, drift one glyph) | **V** | 66, 80–81 |
| S4 | A held-out generator (train even pages, test odd) with only that short reach reproduces the page statistics | **V** | 80–81 |
| S5 | The "keys" are **not** keys: f49v margin letters don't index their lines; the f57v ring is a separate sign-list; zodiac labels aren't a repeated day-list | **N** | 79 |
| S6 | **The words track the pictures**: a page's illustration-topic is predictable from its text alone (pooled 90.8%, p 0.001), within hand and language | **V** | voynich.py (V1) |
| S7 | Repetition is ~8× any control and sits next to itself; words rarely reused across a page (short memory) | **V** | 66, 78–79 |

**The one-line state of knowledge:** the Voynich is a **constrained generative writing system that nonetheless carries topic-level meaning** (S6 vs S1–S5). It is neither readable plaintext nor obviously empty.

---

## 1. The reframed central question

> Given that a generator (slots + copying) produces the surface text, **is there a recoverable map from word to meaning**, and if so where does it live?

Three exit hypotheses, and the decision rule that separates them:

- **H-MEANING** — a real content system (a herbal/pharmacopoeia/astrological text in a constructed script). *Predicts:* an anchor (label→referent) learned on some pages predicts held-out pages.
- **H-EMPTY** — structured but meaningless (a hoax or auto-generated filler). *Predicts:* no anchor beats its shuffle out-of-sample; S6 is only a section-level style artifact.
- **H-HYBRID** — a meaning-bearing **core** wrapped in generative/obfuscating **machinery** (the slots and copying hide a smaller signal). *Predicts:* stripping the machinery sharpens the signal; meaning concentrates in one slot. **Best fit so far** (S6 ∧ S3).

**Decision gate for the whole program:** H-HYBRID is only worth pursuing while each stage below passes its pre-registered out-of-sample test. Two consecutive failed gates → fall back to H-EMPTY and report it.

---

## 2. The angle matrix

Every row is a viewing angle; every angle names its engine, its control, and its next action. The point of the matrix is that **no single angle decides it** — convergence across angles does.

| Angle | Question | Engine / method | Control | Status → next action |
|---|---|---|---|---|
| **A. Statistical** | Is the letter/word stream language-like? | entropy h₁/h₂, Zipf, MATTR | Latin/Greek/Hebrew, random | **done (S1)** → cross-check on ZL/IT/GC/v101 transliterations |
| **B. Morphological (slots)** | What are the generative units? | learned prefix/root/suffix; MDL segmentation | shuffled glyphs | **done (S3)** → fix a canonical slot grammar as the token layer |
| **C. Sequential / positional** | Does position (line, paragraph, page) govern glyph choice? | LAAFU, line-initial/final, first/last word | within-page shuffle | **done (partial)** → model the layout rule explicitly, subtract it |
| **D. Visual / codicological** | Do labels bind to picture parts? quire/hand order? | IIIF images + label loci; hand/quire from ZL | label shuffle | **open** → build a label→picture-region dataset from Beinecke IIIF |
| **E. Topical / semantic** | Does vocabulary carry subject meaning? | TF-IDF page-topic; **root vs affix (pilot)**; word2vec over pages | shuffle $I labels | **S6 + pilot** → anchor-level (plant/star identity), not just section |
| **F. Cryptographic** | Could it be abbreviation/verbose cipher/nomenclator? | map EVA to Latin abbreviation marks; test verbose-cipher expansions | encrypt a real herbal (R78) | **partial (R78)** → the abbreviation-glyph reading (`9`=-us, `4o`=qu) |
| **G. Generative-model** | What mechanism reproduces it, held out? | copy+drift+slot generator | REAL odd pages | **done (S4)** → add a *meaning-bearing* generator and see if it fits better |
| **H. Provenance / historical** | Who, where, when, inspired by what? | documents, hands, pigments, merlons, dialect of the month-names | — | **open** → the dossier (§5) and the inspiration analysis (§6) |
| **I. Cross-manuscript** | Does any contemporary system share the method? | compare to Llull wheels, cipher MSS, shorthand, artificial languages | — | **open** → §6 tie-ins, incl. our Sefer Yetzirah 231-gates engine |
| **J. Acoustic / harmonic (our signature lens)** | Is the word-sequence periodic / musical / number-driven? | the project's harmonic + ring-composition + calendar engines | shuffled sequences | **open** → §7 |

---

## 3. The decipherment pipeline (staged, pre-registered gates)

```
 A. NORMALISE   fix one transliteration + the canonical slot token layer (prefix·root·suffix)
      │          gate: slot grammar covers >85% of word-mass on held-out pages  [R81: met]
 B. DE-MACHINE  subtract the generative layer: remove copying runs, strip affixes, keep roots
      │          gate: root stream predicts page-topic >= full-word stream, out of sample  [pilot: partial]
 C. ANCHOR      bind labels to identifiable referents (zodiac month order; plant parts;
      │          star counts; container shapes) — a small seed dictionary
      │          gate: >= 5 anchors each consistent across >= 2 independent pages
 D. PROPAGATE   from anchors, grow a word->meaning map by distribution (embedding/topic model)
      │          gate: the map assigns a coherent sense to >= 30% of root types
 E. VALIDATE    predict a HELD-OUT label or page's topic/first-word from the map, pre-registered
                 gate: out-of-sample accuracy beats shuffle at p<0.01 in two independent splits
```

Any stage that fails its gate twice sends the verdict to H-EMPTY for that section. Sections are run **separately**
(herbal-A, balneological-B, zodiac, pharmaceutical, stars/recipes) because Currier A and B behave differently.

---

## 4. Data to gather (and why)

| Data | Source | Why |
|---|---|---|
| **ZL3b reference transliteration + page metadata** ($I illustration, $L language, $H hand, $Q quire) | voynich.nu (done) | section-aware analysis; the wedge for Angle E |
| IT / GC / FG / v101 transliterations | voynich.nu | cross-validate letter-level stats (Angle A) against EVA's digraph choices |
| **High-res folio images (IIIF)** | Beinecke MS 408 (Yale) | label→picture-region binding (Angle D); plant-part and star anchors (Stage C) |
| More contemporary herbals/recipes | Macer, *Circa instans* (have); Tacuinum Sanitatis, Trithemius | genre controls; candidate plant names |
| Star/zodiac catalogues | al-Ṣūfī, Ptolemy *Almagest* star list, Alfonsine tables | anchors for the astronomical/zodiac labels |
| Alchemical corpus | Geber *Summa* (have); *Theatrum Chemicum* | the "make gold" register control |
| **Llull *Ars Magna* / combinatorial sources** | public editions | the generation-method hypothesis (§6, Angle I) |
| Provenance documents | Marci→Kircher letter (1665); Baresch→Kircher (1639); Kircher *carteggio* (digitised, Rome); Horčický signature on f1r | the author/ownership dossier (§5) |

---

## 5. Author & provenance dossier (established facts, open questions)

**Hard facts.**
- **Date:** vellum radiocarbon-dated **1404–1438** (Arizona AMS, 2009). The *writing* is on that vellum, so it is early-15th-c. or soon after.
- **Object:** Beinecke Rare Book Library, Yale, **MS 408**; ~234 folios, several fold-outs; **five scribal hands** (Davis 2020), two "languages" (Currier A/B).
- **Ownership chain (documented backward):** Wilfrid Voynich bought it 1912 (Villa Mondragone, Jesuit Collegio Romano) ← Athanasius Kircher / the Collegio (17th c.) ← Johannes Marcus Marci, who sent it to Kircher **1665** ← Georg Baresch, Prague alchemist, who wrote to Kircher **1639** for a decipherment ← (signature on f1r, erased, recovered under UV) **Jacobus Horčický de Tepenec** ("Jacobi à Tepenecz," d. 1622), Rudolf II's distiller/apothecary in Prague.
- **The Marci letter's claims:** Rudolf II reportedly paid **600 ducats**; authorship attributed (via a rumour from Raphael Mnishovsky) to **Roger Bacon** — **discredited** (Bacon d. 1292, two centuries too early).

**Geography / milieu clues (reading, not proof).**
- **Swallowtail (Ghibelline) merlons** on the castle in the nine-rosette fold-out → **Northern Italy**, 14th–15th c.
- **Balneological section** (women in green pools/conduits) → Central European **bath culture**.
- The **zodiac month-names** are a **later annotation** in a hand whose dialect has been read as **Occitan / Judeo-French / Old French** → points to a later annotator's region (SW France / N Italy / Savoy), not necessarily the maker.
- Pigments and quire structure are consistent with early-15th-c. European production.

**Open questions for us.**
- **One constructor or a workshop?** Five hands, but the generative *method* (slots + copying) is a single designed system. Who designed the method?
- **A physician/apothecary/alchemist context** (Horčický's own trade) fits the herbal-pharmaceutical-balneological content — but that is the earliest *owner*, not the maker.
- The maker had **a method, not just a pen.** That is the most important author-clue we can act on, and it points at §6.

---

## 6. What could have inspired the "processing" (the generation method)

The slot-grammar-plus-copying system is the fingerprint of a **deliberate generative method** available in the early 15th c. Each candidate comes with a test we can run.

| Inspiration | Why it fits | Test (our engine) |
|---|---|---|
| **Ramon Llull's *Ars combinatoria* / volvelles** (13th c., dominant through the 15th) — rotating wheels that combine a small base alphabet of concepts into terms | the Voynich *has* ring/volvelle diagrams (f57v, f85–86); combinatorial generation of words from a tiny base = the slot grammar exactly | re-examine whether a small base set + rotation reproduces the root inventory; compare the ring sign-lists to the slot alphabet |
| **Kabbalistic letter-combination (ṣerûf; Abulafia; *Sefer Yetzirah*'s 231 gates)** — alive in 15th-c. Christian-Hebraist circles | letter-combination mysticism generates "words of power" by rule — the project already built the **231-gates engine (round 39)** | **run our Sefer Yetzirah 231-gates engine on the Voynich glyph-pair inventory**: are the allowed glyph pairs a closed "gate" set, like a combination table? |
| **Medieval abbreviation / Tironian shorthand** — `9`=-us/-um, `4`+`o`=qu-, gallows = decorated capitals | several EVA glyphs *are* Latin scribal abbreviation marks; a heavily abbreviated vernacular would compress to low entropy | map EVA→abbreviation expansions; test whether expansion raises h₂ toward language |
| **Artificial / philosophical language** (Llull again; the tradition KANON revives) | a designed language has fixed slots and positional meaning — our KANON lands statistically nearest the Voynich (round 66) | treat Voynich slots as **KANON-style operators**; test a fixed slot→sense map (Stage B–D) |
| **Number / musical cycle** (our signature lens) | low-entropy slot cycles can be driven by a counting or melodic rule | the harmonic/periodicity engine on the word-sequence (Angle J) |

The strongest, most *us* move: **the Voynich generation method, Llull's wheels, Sefer Yetzirah's gates, and KANON are the same idea** — generating a lexicon by rule-governed combination of a small base. We are uniquely equipped to test that, because we built the engines for three of the four.

---

## 7. How each Sound engine maps onto the Voynich

| Our engine (round) | Voynich application |
|---|---|
| entropy + control framework (66) | Angle A — done; cross-transliteration next |
| **Sefer Yetzirah 231-gates (39)** | Angle I — is the glyph-pair graph a closed combination table (a "gate" set)? |
| **KANON slot decoder (65)** | Stages B–D — fixed slot→operation/sense map; test topic prediction |
| ring-composition / centre engine (52–54) | does a Voynich paragraph/page have a centre or ring structure? |
| **calendar / astronomy engine (39)** | the zodiac/astronomical pages — do label/star counts fit a real calendar or star catalogue? |
| harmonic / periodicity signature (38–59) | Angle J — periodicity of the word-sequence (number/musical driver) |
| Echo-Ladder learnability (34) | is the Voynich lexicon learnable as a generated system (one-new-word-per-step)? |
| codec / information theory (65) | measure the *channel capacity* of the slot system — how much meaning *could* it carry? |

---

## 8. Pilot result this round (`localize.py`): where does the meaning live?

Within each (language, hand) group, predict a page's illustration-topic from its words, three ways: **full words**,
**roots only** (strip the 12 learned prefixes + 16 suffixes), **affixes only**.

| Group | pages | full (acc/null) | root (acc/null) | affix (acc/null) |
|---|---|---|---|---|
| Language B, hand 2 | 46 | 0.52 / 0.22 (p 0.003) | 0.52 / 0.21 (p 0.003) | 0.50 / 0.23 (p 0.02) |
| Language B, hand 3 | 28 | 0.82 / 0.50 (p 0.04) | **0.86 / 0.49 (p 0.007)** | 0.79 / 0.50 (p 0.08) |
| Language A, hand 1 | 112 | 0.27 / 0.31 (n.s.) | 0.17 / 0.30 (n.s.) | 0.25 / 0.29 (n.s.) |

**Reading (honest, partial):**
- In the B-language sections the **root carries at least as much topic signal as the whole word** — in hand 3 the root *beats* the full word (0.86 vs 0.82). This supports **targeting roots** for decipherment (Stage B gate: partially met).
- But **affixes are not pure noise** (0.50–0.79) — section and suffix are correlated (the Currier A/B split is partly morphological). So the machinery is not fully content-free; de-machining must be done per section.
- **Language A / hand 1 shows no page-topic signal** — because that group is almost all herbal pages, so there is little *topic contrast* to detect. This is the key lesson for Stage C: **in the herbal section, page-topic is too coarse — we need anchor-level targets (which plant), which require the images.**

---

## 9. The pre-registered experiment queue (next rounds)

1. **Cross-transliteration robustness** (Angle A): recompute S1/S3 on ZL, IT, GC, v101 — does the signature survive EVA's choices?
2. **The 231-gates test** (Angle I, our engine): is the Voynich glyph-pair graph a closed combination table? Compare its density/closure to Sefer Yetzirah's gates and to a natural language's bigraph graph.
3. **Abbreviation-expansion test** (Angle F): apply the EVA→Latin-abbreviation reading; does expansion move h₂ toward language?
4. **Anchor hunt in the zodiac** (Stage C): the 30-labels-per-page day structure (S5 said not a repeated day-list — so test instead whether label *order* tracks the figures' angular position).
5. **Image-bound labels** (Angle D, Stage C): from Beinecke IIIF, pair each label with its picture region; test label-similarity vs picture-similarity (do similar plants get similar labels?).
6. **A meaning-bearing generator** (Angle G): extend the held-out generator with a hidden topic variable; does adding meaning improve the fit to real pages, or not (the H-EMPTY vs H-HYBRID discriminator)?
7. **Channel-capacity bound** (codec engine): how many bits of meaning *could* the slot system carry per page? Sets the ceiling on any decipherment.

---

## 10. Honesty guards

- The Voynich has defeated a century of confident solvers; **every claim is pre-registered, out-of-sample, and controlled** (the project's standing rule).
- H-HYBRID is seductive and loose; it is kept honest only by the **decision gates** (§3). Two failed gates in a section → we report H-EMPTY for that section and move on.
- "Constructed/generated" ≠ "meaningless": a rule-governed system can carry information (KANON does). The whole program is the attempt to measure whether *this* one does — and to say clearly if it does not.
