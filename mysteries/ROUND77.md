# Round 77: Voynich controls with a prose herbal, a recipe book, and the pharmaceutical labels (`voynich/controls.py`)

**Controls:**
- **Platearius, *Circa instans*** (12th-c. Salernitan prose herbal), from the 1582 Lyon print (archive.org BIUSante_pharma_res012103, OCR).
  - Entries are split at each chapter's opening quality formula ("X calida / frigida est …").
  - About 270 chapters exist; the OCR splitter finds 46, so some entries merge 2–3 simples. That *lowers* the own-name score, so the control is conservative.
- **Apicius, *De re coquinaria*** books 1–5 (Latin Library): 140 recipes. Its recipes are single paragraphs, so its line measures do not apply.
- Round 76's verse herbal, Macer Floridus.

## The herbal comparison (same measures as round 76)
| Measure | Voynich herbal | *Circa instans* (first 79 words) | Macer (79 words, words / stems) | Apicius (recipes, 38 words) |
|---|---|---|---|---|
| Tokens specific to one entry | 33% | 57% | 36% / 24% | 26% |
| **Entries with their own name keyword** | **17%** | **85%** | **42% / 58%** | 28% |
| Line-position dependence (excess MI) | **0.19** | 0.06 (prose wraps) | 0.39 (verse) | n/a |
| **Same word twice in a row** | **0.83%** | 0.08% | 0.00–0.02% | 0.02% |

**Result:**
- **Both real herbals, verse and prose, name their subject.** The prose herbal does so in 85% of entries at Voynich's length; Voynich does in 17%.
- **On names, the Voynich herbal is closer to a recipe book (28%) than to any herbal.**
- **Its lines are units.** Prose wraps are near 0.05; the Voynich gives 0.19.
- **It repeats words back to back 10–80× more** than any of the three real texts.

## The pharmaceutical labels
| | Value |
|---|---|
| Labels on the pharmaceutical pages | 244 (224 distinct; 93% used only once) |
| **Labels found in their own page's text** | **7.8%** |
| Chance: a random text word from other pages | 18.6% |
| Chance: a random text word of the same length | 15.8% |
| **p (labels as rare as observed or rarer, length-matched chance)** | **< 0.005** |
| Labels found anywhere in the manuscript's text | 49% |
| Real headings named in their own entries | Macer **95%**; *Circa instans* ≥ 41% (undercounted by OCR) |

**Result:**
- **The labels are not the page's vocabulary.** They turn up in the text beside them *less* often than random words would.
- In real herbals and pharmacopoeias, a heading or label names what the entry discusses, and recurs in it.
- The labels' length matches text words (5.7 against 5.2 letters), and half of them occur somewhere in the manuscript. So they are made of the same "word stock" but are *used* as a separate set of names.

## Synthesis of rounds 75–77 on the Voynich
| Property | Voynich |
|---|---|
| Vocabulary follows the pictured topic, within scribe and "language" | yes (86–91% against 68%) |
| Lines are units, like verses or entries | yes |
| Page-specific vocabulary at a herbal's rate | yes |
| **A repeated name word per plant** | **no** (17% against 42–85%) |
| **Labels named in the adjacent text** | **no** (below chance) |
| Immediate word repetition | 10–80× real Latin |

**This profile is not a herbal written in a language,** at least not one that names its plants and labels in the way medieval Latin herbals do. It fits three explanations:
- the names live **outside** the text (in the pictures and labels as a separate system);
- the text is a **cipher or notation** whose "words" are not one-to-one with plaintext words (which would also scatter names and create repeats);
- or **generated text** whose generator varied with the section.

These are standard candidate classes. What these rounds add is measurements that any proposed decipherment must now reproduce: the 17% name rate, labels below chance, and 0.83% repetition.
