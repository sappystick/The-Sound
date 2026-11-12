# Round 89 — Move 1: the latent state, and the discovery of the content-word layer

Round 88 proved the Voynich holds long-range information our null-content model can't produce. Move 1 extracts what
carries it — and the answer compounds the model with a new, strongly content-like layer. Scripts `voynich/hmm.py`
(latent-state HMM + capstone), `voynich/burstiness_results.json`; results `voynich/hmm_results.json`.

## 1. The latent-state model (HMM)
Fit discrete HMMs (scaled Baum-Welch, from scratch) on even folios, scored on held-out odd folios.

| hidden states | held-out perplexity |
|---|---|
| 1 | 6.72 |
| 4 | 6.71 |
| **8** | **6.58** |
| 16 | 6.63 |

- The text supports about **8 latent states** (8 beats 1; more overfit) — a real but **small** word-prediction gain.
- The states are **mostly not topical**: two states dominate every section; only the balneological section gets a
  distinctive state. They capture structure (position/function), not subject.
- The state sequence is **nearly memoryless** (order-1→3 bits barely fall, 1.117→1.082) — a first-order drift, not a
  grammar of reused motifs.

## 2. The capstone — and the redirect
If an 8-state drift explained round 88, text generated from the fitted HMM would reproduce the long-range word
information. It does **not**:

| | long-range word information (d ≥ 21) |
|---|---|
| real Voynich | **0.037** |
| section-conditioned iid generator | 0.020 |
| **8-state HMM (generated)** | **0.0013 — fails** |

The HMM *fails* to reproduce the signal (a few states whose emissions are too alike cannot). **So the long-range
structure is finer than a drifting state — it lives in which specific words recur at long range.** This redirected
Move 1 to the right layer.

## 3. The discovery: a content-word layer (the strongest signal yet)
Measure each frequent word's **burstiness** — how clustered its occurrences are (Poisson/filler = 1; clustered,
topical > 1):

| | value |
|---|---|
| mean word burstiness (freq ≥ 12) | **2.15** |
| same, after shuffling the stream | **0.93** (≈ 1, the floor) |
| share of frequent words significantly clustered (>1.3) | **73%** |

**Voynich words recur in bursts ~2.3× above chance, and 73% of them are significantly clustered.** This vanishes
under shuffling, so it is real long-range structure. The top carriers each concentrate in one section:

| word | freq | burstiness | section (concentration) |
|---|---|---|---|
| `cthy` | 91 | 15.0 | herbal (0.89) |
| `chor` | 172 | 9.3 | herbal (0.72) |
| `qokain` | 273 | 9.3 | balneological (0.58) |
| `cthol` | 49 | 8.3 | herbal (0.86) |
| `qokeedy` | 293 | 7.5 | balneological (0.48) |
| `sho` | 88 | 7.0 | herbal (0.77) |
| `shedy` | 356 | 5.3 | balneological (0.52) |

This is the signature of **topical content words**: specific vocabulary that belongs to a subject and recurs when the
subject is treated. Crucially, the section-conditioned iid generator reproduces only ~half the long-range information
(0.020 of 0.037), so **the clustering is substantially finer than the coarse section blocks** — specific words recur
in local bursts, as a text does when it stays on a sub-topic across pages.

## 4. What this means — and what it does not
- **Strengthens the content side.** The Voynich behaves like a text that is *about* specific things, using specific
  vocabulary that clusters topically — not like white noise, and not fully like a simple generator. This is the best
  positive evidence in the whole investigation that there is organised content to find.
- **Honest limit.** Topical word-clustering alone does not prove *semantic* meaning: a generator with rich,
  locally-coherent per-sub-topic word pools could also produce it. But it is a real, specific, recoverable layer, and
  it is finer than anything our models reproduce.

## 5. The compounded model (growing)
The Voynich model now has four layers, each measured:
1. **Surface:** slot grammar (prefix·root·suffix) + self-citation copying (rounds 80–83).
2. **Section:** word-pool conditioned on illustration section — reproduces page topicality (round 87).
3. **Latent drift:** ~8 mostly-structural states, slow and first-order (this round) — minor.
4. **Content-word layer (new):** specific bursty words recurring in local topical clusters, finer than sections —
   carries the long-range information none of the above reproduce. **This is the decipherment target.**

## 6. Next step (with the new ability)
The content words are now identified. The forward move: **unsupervised concept discovery on the content-word layer** —
build the co-occurrence network of the bursty words (which content words appear together in the same local bursts),
cluster it into concept groups, and ask whether those groups are coherent and whether they align across pages or with
the diagrams. If the content words fall into a small set of reusable co-occurring groups, that is a "concept
vocabulary" — the shape of the hidden content, readable as structure even if not as words. Then the Currier A/B
Rosetta (Move 2) can test whether A and B encode the same concept groups differently.

**Status:** Move 1 done; it found the content-word layer — the first layer that looks like real subject-structured
content and that none of our generative models reproduce. The investigation now has a concrete target with a measured
fingerprint, and the next move (concept-cluster discovery) builds directly on it.
