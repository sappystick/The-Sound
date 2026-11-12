# Round 92: phrase anchors (seven formulas), information budget, low-rate channels

Pre-registered in `voynich/PREREG_92.md`, committed before any script existed. Scripts: `anchors.py`, `budget.py`, `channels.py`, plus a shared loader `zl.py`. Each has a matching `*_results.json`.

## P. Phrase anchors: the internal Rosetta by aligned units
- **Corpora:** herbal-A odd pages (3,775 tokens) against herbal-B odd pages (1,646).
- **Controls:**
  - **ceiling:** herbal-A odd pages against token-matched herbal-A even pages (same dialect, same topic);
  - **floor:** herbal-B against token-matched stars-B (same dialect, different topic).
- **Rewrite rules,** re-learned on even pages only: -or → -edy, -ol → -dy, -chy → -ar, -ody → -ol, -ain → -or, -dy → (dropped), -ar → -y.

| Formula | AB 2-gram z | ceiling | floor | AB 3-gram z | ceiling | floor |
|---|---|---|---|---|---|---|
| F0 identity | 2.1 | 5.8 | 3.3 | −0.2 | 5.3 | 4.4 |
| F1 rewrite rules | 1.9 | 5.9 | 3.2 | −0.3 | 5.6 | 4.2 |
| F2 root only | −3.5 | −1.7 | 0.4 | 2.9 | 4.2 | 1.1 |
| F3 suffix class | 3.1 | 1.4 | 3.2 | 1.7 | 6.3 | 4.5 |
| F4 skeleton (no e o a i y) | 1.4 | 2.4 | 0.6 | 0.1 | 5.6 | 4.4 |
| F5 rewrite + skeleton | −0.3 | 0.5 | 0.7 | 1.5 | 5.1 | 4.0 |
| F6 root + skeleton | −3.0 | −1.6 | −2.8 | 0.5 | 2.3 | 0.2 |

**Pre-registered decision: NO PHRASE ANCHORS.** No A/B comparison survives Holm correction while also exceeding the floor.

**Why this result can be trusted (the method has power):**
- Two parts of the *same dialect* share phrases far above chance, whether the topic is the same (ceiling, z up to 6.3) or different (floor, z up to 4.5).
- With the surface form kept (F0, F1), herbal-A and herbal-B share **zero** three-word phrases. Ceiling and floor each share several, at 5–10× their nulls.
- No formula brings A against B up to the floor. Neither the ending rewrite, nor stripping to roots, nor reducing to consonant skeletons does it.

**Reading:** the system's fixed phrases belong to the **dialect, not the subject.** B carries its phrases from plant pages to star pages. A and B, even on the same plant pages, do not share them in any normalised form we tried. Round 91 found that A and B share **words**, with shifted endings; round 92 finds they do not share **phrases**. The two dialects build word sequences by different habits, so **no internal Rosetta exists at the phrase level.** Together with round 91, the A/B route to a key is closed at the scale of data that exists.

## I. Information budget
Every text runs through the same pipeline: train on even pages, score odd pages, and spell new words with a character model.

| Text | bits/word (unigram) | (bigram) | gain from previous word | bits per 100 words |
|---|---|---|---|---|
| **Voynich** | 12.24 | 12.69 | **−0.45** | ≈ 1,220 |
| Voynich, roots only | 7.78 | 8.08 | −0.30 | ≈ 780 |
| Voynich A / B | 13.01 / 11.65 | 13.51 / 12.12 | −0.50 / −0.47 | |
| Latin herbal (Macer) | 13.91 | 13.69 | **+0.22** | ≈ 1,370 |
| Greek John | 11.20 | 10.26 | **+0.94** | ≈ 1,030 |
| English John | 9.39 | 8.38 | **+1.02** | ≈ 840 |

- **The budget is not small.** A Voynich page carries about 12 bits of surprise per word, in the range of real languages.
- **The surprise sits in which words are used** (section and content words), not in their order.
- **The root channel alone holds at most about 780 bits per 100 words.** That is the ceiling for any message carried by roots.
- **New, and the clearest result here: the previous word does not help predict the next one.**
  - In every language control, knowing the previous word lowers the cost of the next by 0.2–1.0 bits.
  - In the Voynich it *raises* it, because pair statistics don't generalise from even to odd pages.
  - Adjacent word order carries **no transferable information**, in both dialects.
- A natural language with this much vocabulary and **no** word-to-word syntax would be extraordinary. A system that writes from section word-pools with position rules, as the generators of rounds 80–81 do, produces exactly this. This finding favours the constructed-system reading more strongly than any single earlier test.

## C. Low-rate channels
| Hidden sequence | conditional entropy against within-page shuffles | after Holm |
|---|---|---|
| **First glyph of each line** | 2.999 against 3.146, p 0.001 | **CARRIES ORDER** |
| **Gallows glyph of each line** | 1.494 against 1.562, p 0.001 | **CARRIES ORDER** |
| Last glyph of each line | p 0.53 | none |
| First word of each paragraph | p 0.66 | none |
| Every 7th word | p 0.35 | none |
| Repeated line-initial 4-grams on 3 or more pages | 287 against 201, p 0.003 | repeated patterns |

**Exploratory confound check.** Paragraphs open with gallows glyphs (p, t, k, f), and a within-page shuffle destroys that. Keeping each paragraph's opening line fixed and shuffling only the rest, **the order survives** (p 0.001 for both sequences). So it is not just "openings are special".

**What drives it: alternation.** Consecutive lines **avoid** starting with the same glyph: 7.6% do, against 14.4% expected.
- The largest deficits are the repeats q→q, o→o and d→d.
- The largest excesses are switches: o→q, d→q, q→s, q→c.

Line-initial glyphs alternate between classes, roughly a q-line, then an o/d/s line, then a q-line.

**Reading:**
- A **line-level layout rule** that has not appeared in our earlier tests. Whether it is known in the literature still has to be checked; LAAFU line effects are well known, but this alternation between successive lines is a specific form.
- It is **order, not a message.** An alternation lowers entropy and conveys almost nothing. The "every 7th word" and "paragraph-first word" channels show nothing.
- If a sparse message is hidden, these candidate channels don't hold it.
- The alternation is a **new constraint for any generator.** The round-80/81 generators draw each line's first word independently, so they cannot produce it.

## U. Unique-system control
**Not done.** No public machine-readable Rohonc Codex transcription could be obtained. A blog-hosted transcription exists, but its host is outside this session's allowed network. As pre-registered, this is reported as not done.

## Status of the self-contained-system programme
1. **The A/B route is closed** at the available data scale. A and B share words with shifted endings (round 91) but no phrases (round 92).
2. **The text carries language-sized word surprise but no adjacent-word syntax.** This is the clearest signature yet of a constructed system that writes from pools.
3. **Low-rate channels:** no hidden message in the obvious places. A new line-alternation rule was found.
4. **What remains as content:** the bursty content-word layer and its long-range organisation (rounds 88–90). That is real, and it is the only place left for meaning to live.

## Next
- **Add line-initial alternation to the generator** and re-score it on held-out pages.
- **Ask what the content-word sequence encodes:** test whether the order of content words across a section follows the illustrations' order, or a cycle, or a list such as a calendar or the zodiac.
