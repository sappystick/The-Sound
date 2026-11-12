# Round 52: the pre-registered manuscript test of the Gospel ending at 20:31

**Files:**
- pre-registration: `robustness/PREREG_R52.md`, commit `e7f7c5d` (10:01 UTC), made before the script existed;
- script `power/round52_2031_manuscripts.py`;
- numbers `power/round52_results.json`.

**Hypothesis (from round 51):** John 10:11, "I am the good shepherd; the good shepherd lays down his life for the sheep", the fourth of the seven "I am" sayings, stands at the centre of the Gospel as it first ended, at 20:31.

## Primary result (H1): passes
| Manuscript | Lines in 1:1–20:31 | Position of 10:11 | p | Line at the centre |
|---|---|---|---|---|
| **Sinaiticus (01)** | 4,998 | **0.5075** | **0.033** | 10:4 |
| **Vaticanus (03)** | 3,944 | **0.5046** | **0.020** | **10:7**, "Amen, amen … **I am the door of the sheep**" |

**The pre-registered rule** (p < 0.05 in both manuscripts) **is met. Status: V.**
- The test is confirmatory on a new unit: the physical lines of two 4th-century codices, two scribes, two page formats.
- It is not blind: the hypothesis came from the printed text.
- In both codices the centre of the page-count falls inside the good-shepherd discourse (10:1–18).
- Vaticanus's central line is itself an "I am" saying.

## Secondary results (reported, not part of the verdict)
| Manuscript | Coverage of 1:1–20:31 | Used? | Position | p |
|---|---|---|---|---|
| Washingtonianus (032) | 95.4% | yes | 0.524 | 0.10 |
| Alexandrinus (02) | 86.6% | no (gaps in John 6–8) | 0.449 | — |
| Bezae (05) | 80.3% | no | 0.528 | — |
| Ephraemi (04) | 40.8% | no | — | — |

- Washingtonianus, the one further codex complete enough to test, puts 10:11 past the centre (0.524), which is not significant.
- 01 and 03 contain no lines of 7:53–8:11, so excluding that passage changes nothing.

## What this means
**Established:**
- The Gospel ending at 20:31 has the middle of its seven "I am" sayings at its centre.
- This holds in words, breath groups and performed time (round 51), and now in the line counts of Sinaiticus and Vaticanus, pre-registered.
- **The "slightly off" centre of earlier rounds was the epilogue.**

**Fits with:**
- the "I am" ring around the Gospel's centre (claim C2);
- Jesus in the middle place, in John and, out of sample, in Revelation (round 50);
- the seven-with-a-middle mold: the mese among the strings, the Sun among the planets, the Son of Man among the seven lampstands (round 50).

**Limits:**
- The hypothesis was formed on the printed text before the manuscripts were counted.
- Washingtonianus does not reproduce it.
- **Next:** pre-register the same test on P66 and P75 for the chapters they preserve, on other complete codices of John, and on the Syriac and Coptic versions by words.

---

# Round 53: the papyri and the ancient translations (pre-registered)
**Files:**
- pre-registration: `robustness/PREREG_R53.md`, commit `abfcfd8`;
- script `power/round53_papyri_versions.py`;
- numbers `power/round53_results.json`.

**Common method:** John 1:1–20:31, the position of 10:11, and the same null as round 52.

| Witness | Unit | Position of 10:11 | p | Centre falls at |
|---|---|---|---|---|
| **Sahidic Coptic** | SCRIPTORIUM tokens | **0.509** | **0.038** | 10:4 |
| Sahidic Coptic (secondary) | letters | 0.505 | 0.022 | **10:7**, "I am the door" |
| **Syriac Peshitta** | words | 0.514 | 0.062 | 9:40 |
| Syriac Peshitta (secondary) | letters | 0.514 | 0.060 | 9:40 |
| **P66** (c. AD 200) | letters; 552 verses its own, 64% of the letter mass, preserved to 16:15; the rest reconstructed | **0.508** | **0.034** | 10:4 |
| **P75** (c. AD 200) | letters; 268 verses its own, 31% of the letter mass, preserved to 14:20; the rest reconstructed | **0.506** | **0.027** | 10:6 |

## Verdict by the pre-registered rules
- **H2 (both translations, p < 0.05): fails.** The Sahidic passes; the Syriac misses narrowly (0.062).
- **H3 (both papyri, p < 0.05): passes its own rule**, but **not after the pre-registered Holm correction** (adjusted p 0.068 for both hypotheses).
- **Overall status for round 53: not confirmed.**
- The round-52 result on Sinaiticus and Vaticanus stands as the confirmed finding.

## What the numbers show
- **Every witness puts 10:11 within 0.504–0.514 of John 1:1–20:31:**

  | Group | Witnesses |
  |---|---|
  | Two papyri | P66, P75 |
  | Two codices | 01, 03 |
  | Two translations | Sahidic, Peshitta |
  | The printed text | SBLGNT |

  Across them, the centre of the book falls at 9:40–10:7, in or just before the good-shepherd discourse.
- **The translations sit slightly later** (0.509–0.514). Translation lengthens some passages more than others.
- **Most of each papyrus is reconstruction.** P75 is two-thirds rebuilt from the printed text, P66 a third, so these two results are only partly independent of SBLGNT.

## Honest summary across rounds 50–53
| Pre-registered test | Witnesses | Result |
|---|---|---|
| Round 50, R1 (whole Gospel to 21:25) | 01, 03 | failed narrowly (03 p 0.054) |
| **Round 52, H1 (to 20:31)** | **01, 03** | **passed** |
| Round 53, H2 (to 20:31) | Peshitta, Sahidic | failed (Peshitta p 0.062) |
| Round 53, H3 (to 20:31) | P66, P75 (reconstructed) | passed raw; failed after correction |

**The position itself is stable, near 0.505 in every witness.** The p values hover around the 0.02–0.06 line because the null is broad: any one of seven sayings could land anywhere.
- **This is a consistent, moderate signal.** It is not a decisive one.
- **What would settle it:** a test with more power, using all seven sayings' positions rather than the middle one alone. For example: do all seven sit symmetrically around the centre (the ring of claim C2)? Pre-register it on the 20:31 book.

---

# Round 54: the seven-saying ring (pre-registered)
**Files:**
- pre-registration: `robustness/PREREG_R54.md`, commit `dfdab0d`;
- script `power/round54_ring.py`;
- numbers `power/round54_results.json`.

**The test:**
- **Data:** the seven "I am" + predicate sayings (first occurrence of each).
- **Book:** John 1:1–20:31.
- **Ring error:** how far the pairs (1,7), (2,6), (3,5) and saying 4 sit from the book's centre.
- **Null:** seven random points.

## Primary result: passes
**SBLGNT words:** ring error 0.0247, **p = 0.027**.

| Saying | Verse | Position |
|---|---|---|
| bread of life | 6:35 | 0.285 |
| light of the world | 8:12 | 0.386 |
| the door | 10:7 | 0.499 |
| the good shepherd | 10:11 | 0.504 |
| resurrection and life | 11:25 | 0.563 |
| way, truth, life | 14:6 | 0.712 |
| the true vine | 15:1 | 0.745 |

**Pair midpoints:**

| Pair | Midpoint |
|---|---|
| 1 + 7 | 0.515 |
| 2 + 6 | 0.549 |
| 3 + 5 | 0.531 |
| saying 4 | 0.504 |

## Secondary results
| Witness / version | p (ring around the centre) | p (shape only, centred on saying 4) |
|---|---|---|
| Sinaiticus lines | 0.044 | 0.087 |
| Vaticanus lines | 0.028 | 0.078 |
| Sahidic tokens | 0.038 | 0.066 |
| Peshitta words | 0.063 | 0.064 |
| **Control: the seven signs** | **0.95** (no ring, as predicted) | 0.29 |
| Control: full Gospel to 21:25 | 0.0046 | 0.075 |

**Post hoc, not pre-registered:**
- **Null:** 7 random verses that contain ἐγώ ("I"), 114 of them.
- **Result:** p = 0.031. The ring is not explained by first-person speech crowding the middle of the book.

## What this proves, and what it does not
**Proves** (as far as one pre-registered test can):
- In John 1:1–20:31, the seven "I am" sayings are placed more tightly and more evenly around the book's centre than in 97% of random placements.
- They are also more tightly placed than seven random first-person verses.
- The middle saying sits on the centre, and the pairs balance around it.
- The arrangement is a property of the text. It survives every way of measuring: printed words, the lines of two codices, the Coptic translation, and, narrowly, the Syriac.
- The seven signs, as a control, show no such arrangement.

**Does not prove:**
- **That anyone designed it.** An author, an editor, or the way the discourses grew could all produce it. The test shows that the pattern exists, not why.
- **That the witnesses are independent confirmations.** The manuscripts and translations are copies of the same text. Their agreement shows the result does not depend on the unit of measurement; it is not separate evidence.
- **That it is a strict mirror.** The shape-only version (balance around saying 4, wherever it falls) is not significant (p 0.06–0.09). The pairs' midpoints drift late (0.51–0.55). The sayings are **centred and balanced**, not exact mirror images.
- **Anything about an instrument, a hidden score, or divine sound.** It is a fact about where seven sentences stand in a book. The instrument reading (seven strings around a governing mese) is one interpretation that fits it. So are the menorah (Philo, Josephus) and ancient ring composition in general.
- **That the result is free of earlier choices.** The project has looked at John's centre many times, and the 20:31 ending was suggested by the data (round 51). This test was pre-registered, but the hypothesis grew out of that history.

**The full Gospel (to 21:25) gives an even tighter ring** (p 0.005) in this pre-registered control. The ring therefore does not depend on choosing the 20:31 ending; only the exact central position of saying 4 does.
