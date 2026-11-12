# Round 39 · lens `coptic`: the buried library read against John

Script: `coptic.py` (seed 39, about 11 s). Results: `results.json`. Fetch: `fetch.sh`.

## Sources
- **Coptic SCRIPTORIUM**, commit `6fb5145`, CC-BY.
  - The annotation of the Bible and of Thomas is automatic.
  - Sahidica NT and Sahidic OT come from the TreeTagger files. Sahidica is © J. W. Wells, academic use only, so only counts and short quotations are kept here.
- **Sizes in tokens** (SCRIPTORIUM morpheme units):

  | Text | Tokens | Text | Tokens |
  |---|---|---|---|
  | Matthew | 33,465 | Bartholomew | 13,000 |
  | Mark | 19,986 | Acts of Pilate | 935 |
  | Luke | 34,040 | Dormition of John | 3,064 |
  | John | 26,421 | Magical papyri | 1,446 |
  | Thomas | 6,521 | Shenoute | 77,685 |
  | Pistis Sophia | 119,506 | Null pool | 1.07 M |
  | Mysteries of John | 6,303 | | |

- **Not available:**
  - the Gospel of Truth and the Apocryphon of John (no open lemmatised text);
  - the scrollmapper `versions` clone, which holds only `.git`.
- **Data repair:** the Sahidica file for John 7 runs on into 8:12–59. The Sahidic has no 7:53–8:11, so those verses go back to chapter 8.

## T1. Vocabulary lean
- **Method:** Burrows' Delta on the 250 commonest gospel lemmas, with the gospels size-matched. The null is 400 random equal-length chunks of other Sahidic text.
- **Every text, and the null chunks too, is nearest Luke and farthest from John in absolute terms.** Sahidic Luke is the vocabulary centre of Coptic writing and John is the outlier, so nearness only means something when measured against the null.
- **Lean to John against the null:**

  | Text | z | p | Label |
  |---|---|---|---|
  | Thomas | +0.35 | 0.33 | N |
  | Pistis Sophia | +2.0 | 0.032 (q 0.21) | O |
  | Mysteries of John | +1.0 | | N |
  | Bartholomew | +1.2 | | N |
  | Acts of Pilate | +1.2 | | N |
  | Dormition of John | +0.8 | | N |
  | Shenoute | +0.8 | | N |
  | Magical papyri | −0.35 | | N |

- **Controls:**
  - 1–3 John leans to John at z +5.9, so the method detects strong kinship.
  - Acts did not come out nearest Luke (it was relatively nearest Mark). Weak kinship can therefore go undetected.
- **Thomas:** no Johannine vocabulary lean. This fits the view that the Thomas–John relationship is one of themes and argument (Riley 1995; DeConick 2001; Pagels 2003), and that Thomas's sayings parallels are Synoptic (Tuckett 1988; Goodacre 2012).
- **Reading:** seven of the eight Christian texts lean slightly toward John. This may be an effect of era or genre.

## T2. The translation layer
- **Share of content words that are Greek loans:**
  - John 18.1%; Matthew 16.3%; Mark 16.2%; Luke 15.6%.
  - Null 16.0 ± 0.5%; p 0.001, q 0.0095 (**V**).
  - Thomas 15.8%; Shenoute 19.7%; Pistis Sophia 30.7%.
- **Word-by-word test** on verses aligned to MorphGNT: John keeps 670 Greek words against 673.3 expected (p 0.77, **N**). John's extra Greek comes from his own choice of words that Coptic always borrows (κόσμος 74/74, πιστεύω 91/93). The translator treated John like the Synoptics.
- **Translated in John** (Greek kept / occurrences):

  | Greek | Coptic | Kept |
  |---|---|---|
  | λόγος | ϣⲁϫⲉ | 0/34 |
  | ζωή | ⲱⲛϩ | 0/35 |
  | φῶς | ⲟⲩⲟⲉⲓⲛ | 0/21 |
  | ἀλήθεια | ⲙⲉ | 0/18 |
  | δόξα / δοξάζω | ⲉⲟⲟⲩ | 0/38 |
  | μένω | ϭⲱ | 0/37 |
  | μαρτυρέω | ⲣⲙⲛⲧⲣⲉ | 0/29 |
  | ἀγαπάω | ⲙⲉ | 3/36 |

  The "I am" predicates (bread, shepherd, door, vine, way) are translated too. Only "I am the resurrection" (ⲁⲛⲟⲕ ⲡⲉ ⲧⲁⲛⲁⲥⲧⲁⲥⲓⲥ) keeps its Greek sound.
- **Kept in John:** κόσμος 74/74, πνεῦμα 24/24, πιστεύω 91/93, παράκλητος 4/4, νόμος 13/13, σάρξ 11/12, ἀγάπη (noun) 6/7, ἀνάστασις 4/4.
- **Known and new:** Coptic's borrowing pattern is known (Crum 1939; Metzger 1977; Förster 2002). The counts for John's key words are new.
- **Reading** (link to POWER.md): John's power words did not survive as sounds in Coptic; only the technical vocabulary did.
- **The ⲙⲉ homophone:** one Sahidic sound means both "truth" and "love". John uses it 42 + 47 times, 33.7 per 10,000 tokens, against 3.0–8.2 in the Synoptics (count; Reading).

## T3. "I am" + predicate (ⲁⲛⲟⲕ ⲡⲉ + noun)
- **Rates** per 10,000 tokens, with 95% CI:
  - John 17 cases (6.43, 3.75–10.30); Matthew 3; Mark 1; Luke 1.
  - John against the Synoptics: p 1.2e-7 (**K**: Brown 1966; Ball 1996; confirmed in Coptic).
- **Thomas** 2 cases + 1 relative clause (3.07; **O**):
  - saying 77, "I am the light" and "I am the All";
  - saying 61, "I am he who exists".
- **Thomas 77** ⲁⲛⲟⲕ ⲡⲉ ⲡⲟⲩⲟⲉⲓⲛ matches Sahidic John 8:12 letter for letter. The parallel is known (DeConick, Pagels); the exact match shows shared wording, not who borrowed from whom.
- **Other texts:** Pistis Sophia 9 (0.75: "the mystery", "the knowledge"); Shenoute 2 (0.26); the later John apocrypha 0. The form did not become a general Coptic idiom (**N**).
- **Control:** the pattern finds 14 of the 17 Greek "I am" + noun verses in John.
- **The translator adds** "I am the light" at 12:46.
- **Limits:**
  - The count does not check the speaker, so Gabriel and the false messiahs are included.
  - One Pistis Sophia hit is a parse error.

## Multiple testing
19 tests; Benjamini–Hochberg at q = 0.05.

## Next
- Test the Greek P.Oxy 654/655 Thomas fragments against MorphGNT John.
- Rerun T1 with a null made only of Christian literature.
- Run the word-by-word test on the Bohairic NT as an independent translation.
- Look at ⲙⲉ in Sahidic 1 John, and render it in the sound engine.
