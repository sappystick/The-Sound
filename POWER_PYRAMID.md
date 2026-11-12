# Round 60: does the Great Pyramid map onto the biblical measurements?

**Files:**
- script `power/round60_pyramid_vs_bible.py` (seed 60);
- numbers `power/round60_results.json`.

**Source added:** W. M. F. Petrie, *The Pyramids and Temples of Gizeh* (1883, public domain), in `sources/texts/petrie/`. Values are in inches, checked against the OCR.

**History:** the idea is old. Piazzi Smyth (1864) and later C. T. Russell claimed the pyramid encodes biblical measures, for example that the coffer equals the ark in volume. Because there are many dimensions and a free choice of units, matches are easy to find, so every test here has a chance baseline.

## Results
| Test | What was compared | Result | Chance | p | Verdict |
|---|---|---|---|---|---|
| **T1, lengths** | 23 pyramid dimensions against 27 biblical objects, under 5 different cubits, within 1% | 10 matched | 6.1 | 0.062 | **N** (not beyond chance) |
| **T2, shapes** (no units needed) | 20 proportions within the pyramid's rooms against those within the biblical objects | 1 matched (the King's Chamber 2:1) | 2.2 | 0.90 | **N** |
| **T3a, King's Chamber** | 412.4 × 206.3 × 230.1 in = **20.00 × 10.00 × 11.16 royal cubits** | its plan is exactly 20 × 10, the numbers of the tabernacle's Holy Place (20 × 10) and of Solomon's porch | — | — | **K** (Petrie); the heights differ |
| **T3b, coffer = ark** (Smyth) | coffer inside 1.18 m³; the ark outside 0.50–0.81 m³ under any attested cubit | equal only with Smyth's invented "sacred cubit" (1.44 m³) | — | — | **N** |

**What the matches really are.**
- The genuine matches (20, 10, 10, 4 and 2 cubits) all use the **Egyptian royal cubit (0.5236 m)**, with round numbers.
- **Both traditions built in cubits with round numbers.** Any two such buildings share 20 × 10 and 2:1.
- The other "matches" each need a different unit (an 18-inch cubit here, Smyth's there). That is the classic pyramidology error.

**A real link, through the unit.**
- Ezekiel's measuring cubit is "a cubit and a handbreadth" (Ezek 40:5): 6 + 1 = **7 handbreadths**.
- That is the construction of the **Egyptian royal cubit** (7 palms, against the common 6).
- So Ezekiel's temple and the Great Pyramid share the same **long cubit** (K: a known observation in metrology). They share a unit, not a design.

**The acoustics do not match either:**
- the King's Chamber favours 132 Hz (round 40), the ark 154 Hz;
- the coffer's resonances are not the ark's.

## Verdict
- **The Great Pyramid does not map onto the biblical measurements beyond chance**, by length or by shape.
- What they share is real but ordinary:
  - the cubit system (Ezekiel's long cubit = the Egyptian royal cubit);
  - round cubit numbers;
  - a 2:1 room (King's Chamber 20 × 10; Holy Place 20 × 10).
- The famous coffer-and-ark equation fails with any attested cubit.

## Addendum: the King's Chamber and Solomon's porch have the same floor
**The texts:**
- Solomon's porch (*ulam*) was "20 cubits long, along the width of the House, and 10 cubits deep" (1 Kgs 6:3).
- Chronicles says Solomon's House was laid out in cubits "**by the former measure**" (2 Chr 3:3). This is commonly read as the older, longer cubit: the 7-handbreadth royal cubit that Ezekiel also uses ("a cubit and a handbreadth", Ezek 40:5).

| Room | Plan | In metres |
|---|---|---|
| **King's Chamber** (Petrie) | 20 × 10 royal cubits | **10.47 × 5.24** (height 5.84) |
| **Solomon's porch**, former (royal) cubit 0.5236 m | 20 × 10 cubits | **10.47 × 5.24** |
| Solomon's porch, long cubit 0.52 m | 20 × 10 | 10.40 × 5.20 |
| Solomon's porch, common cubit 0.445 m | 20 × 10 | 8.90 × 4.45 |
| Solomon's Holy Place (*hekhal*) | 40 × 20 | twice the King's Chamber in each direction |
| Solomon's Holy of Holies (*debir*) | 20 × 20 × 20 | a cube; not the same |

**Calc:** if Solomon's "former measure" is the royal cubit, **the King's Chamber and Solomon's porch have the same floor to the centimetre.** Solomon's Holy Place is the same plan doubled.
- They therefore share the same horizontal resonances: 16.4 Hz along the length and 32.7 Hz across.

**What differs:**
- **Height:** the King's Chamber is 11.16 royal cubits high. Chronicles gives the porch 120 cubits, a figure usually judged a textual error. Kings gives no height.
- **Function:** a sealed granite burial chamber deep inside the pyramid, against an open entrance porch in front of the temple.
- **Position:** the innermost room of the pyramid, against the outermost part of the temple.

**How strong is it?**
- The match is exact, and it is real **if** "the former measure" is the royal cubit. That reading is plausible but not certain.
- Both buildings were laid out in the same royal cubit with round numbers. A 20 × 10 room is among the commonest plans such a system produces, so a shared plan does not by itself show that one was copied from the other.
- It does show that **Solomon's builders and the pyramid's builders worked in the same unit, and at least once chose the same room**.
- **Next test:** collect the plans of other Egyptian royal-cubit chambers (other pyramids and temples). If 20 × 10 is common, the match is ordinary. If it is rare, it becomes meaningful.

---

# Round 61: the area-by-area map, pyramid ↔ Bible
**Files:**
- script `power/round61_pyramid_map.py` (seed 61);
- numbers `power/round61_results.json`.

**Method:**
- **Best counterpart:** each area in and around the Great Pyramid is matched to its best biblical counterpart.
- **Shape error:** the difference in proportions.
- **Size error:** the size difference under the best of four attested cubits.
- **Local p:** the share of copies of the same area (shape kept, size randomly scaled ×0.5–2) that find an equally good counterpart. In other words: is this size coincidence better than chance, given the area's shape?
- **Correction:** 12 areas were tested, so the Bonferroni threshold is 0.004.

## Measured pairs, best first
| Pyramid area | Best biblical counterpart | Cubit needed | Shape error | Size error | Local p | Verdict |
|---|---|---|---|---|---|---|
| **King's Chamber** 10.47 × 5.24 × 5.84 m | **20 × 10 cubits**: the tabernacle's Holy Place (20 × 10 × 10); Solomon's porch (20 × 10) | **royal 0.5236** (the builders' own unit) | 5.7% (the height differs) | **0.0%** | **0.001** | **survives correction** (0.001 × 12 = 0.012) |
| Queens' pyramids, about 46 m square | Ezekiel's temple house, 100 × 100 | 18-inch 0.457 | 0 (both square) | 0.6% | 0.033 | does not survive correction; needs a foreign cubit |
| Base, 230.36 m square (440 royal cubits) | **500 × 500**: Ezekiel's outer wall; **Herod's Temple Mount** (Middot 2:1) | 18-inch 0.457 | 0 (both square) | 0.8% | 0.04 | does not survive correction; the builders' own measure is 440, not 500 |
| Khufu's cedar ship, 43.4 × 5.9 m | (size only) the tabernacle court | common | very different | 2.5% | 0.19 | **N** |
| Coffer (outside) | (size only) the altar of burnt offering | 18-inch | 74% | 0.4% | 0.39 | **N** |
| Antechamber | Solomon's side chambers 5:6:7 | royal | 34% | 3.5% | 0.60 | **N** |
| Queen's Chamber | the tabernacle's Holy of Holies, 10-cube | royal | 16% | 9.9% | 0.75 | **N**: its plan is about 11 × 10 royal cubits |
| Grand Gallery, Queen's niche, subterranean chamber, coffer (inside) | — | — | large | large | ≥ 0.5 | **N** |

## Functional links: the same role, not the same measurements
| Pyramid | Bible | What they share |
|---|---|---|
| King's Chamber, holding the coffer | Holy of Holies, holding the ark | the innermost chamber with a lidded box (the sizes differ: round 60) |
| Antechamber, with 3 portcullis slabs | the veil, and the screens before it | barriers between the outer and the innermost room |
| **Grand Gallery, 7 corbel courses** | the menorah (7); the 15 steps of ascent | a sevenfold ascending structure |
| Queen's Chamber (the middle room) | the Holy Place | the middle room on the way in |
| Subterranean chamber | the rock below the sanctuary | the room cut into the bedrock beneath |
| Base square, oriented to the cardinal points | the court; Ezekiel's 500 square; Herod's Temple Mount | the square precinct facing the four directions |
| **Khufu's cedar ship** | **Noah's ark** | a great wooden vessel tied to the sacred site (proportions 7.4:1 against 6:1) |
| Three queens' pyramids | the three storeys of side chambers; the three courts | a set of three |
| 5 relieving chambers above the King's Chamber | the side-chamber storeys | stacked compartments over the main room |

## Verdict
1. **One direct measured match survives:** the King's Chamber floor is 20 × 10 royal cubits, exactly the plan of the tabernacle's Holy Place and of Solomon's porch "by the former measure" (round 60). It is in the builders' own unit, and it beats chance after correction.
2. **Two near-matches:** the base square against the 500 × 500 of Ezekiel and Herod's Temple Mount, and the queens' pyramids against Ezekiel's 100 × 100 house. Both need an 18-inch cubit that the pyramid's builders did not use (the base is 440 royal cubits), and neither survives correction.
3. **Everything else is a functional parallel, not a measured one.** An inner chamber with a box, barriers before it, an ascent, a square oriented precinct, a sacred ship. These are common to sacred architecture, and many may be ordinary features of temple-building in general.
4. **The pattern overall:** the two traditions share a unit (the royal cubit, which is Ezekiel's), round numbers, and the grammar of sacred space. They do not share a hidden plan.
