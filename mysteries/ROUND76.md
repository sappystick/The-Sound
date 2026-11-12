# Round 76: the Voynich herbal against a real Latin herbal, and the Antikythera misfits

## 1. Voynich herbal pages against Macer Floridus, *De viribus herbarum* (`voynich/herbal.py`)
**The control text:** a real 11th-century Latin herbal in verse, 77 chapters, one plant each (la.wikisource, public domain). The same measures as the Voynich herbal pages ($I = H, 128 pages), one plant per entry. Latin is also measured with crude stems, and cut to Voynich's page length (79 words).

| Measure | Voynich herbal | Macer | Macer cut to 79 words (words / stems) |
|---|---|---|---|
| Words per line | 6.8 | 6.2 | – |
| Words per entry (CV) | 79 (0.30: page-sized, even) | 175 (0.54) | 79 |
| Tokens specific to one entry | 33% | 25% | 36% / 24% |
| **Entries with their own repeated keyword (the plant's name)** | **17%** | 65% | **42% / 58%** |
| **That keyword in the entry's first line** | **11%** | 26% | **21% / 35%** |
| Line-position dependence (excess MI) | 0.19 | 0.39 (verse) | – |
| **Same word twice in a row** | **0.83%** | 0.01% | 0.00–0.02% |

**Reading:**
- Like a real herbal, Voynich herbal pages carry **page-specific vocabulary** at the same rate as Latin of equal length, and are built in **line units**.
- Unlike a real herbal, **they do not repeat a name word**: a real chapter keeps returning to its plant ("artemisia …"). They also **repeat words back to back** about 50–80 times as often ("daiin daiin").

So whatever the Voynich herbal is, it is *not* written like a plant-by-plant herbal that names its subject. Hypotheses this narrows to:
- the plant name is absent, perhaps held in the picture or a lost label;
- page-specific words are variants, not repeated terms;
- or the page-specific vocabulary is generated rather than referential.

**Next test:** a herbal in prose (*Circa instans*) and a recipe text as further controls, and the same measures on the "pharmaceutical" pages, where labels sit beside each drawing.

## 2. Antikythera: the misfits as information (`antikythera/residuals.py`)
| Question | Result |
|---|---|
| **Which numbers are inexact?** | **Always the remainder:** Venus 68 = 292 − 224; Mars 82 = 780 − 2 × 349; Jupiter 104 = 398 − 2 × 139 − 2 × 8. The author fixed the synodic period and the free intervals, then derived the last by subtraction. **This is a working method, not a hidden message**, and it is why the error collects in one number per planet. |
| **Does Mars's misfit point to a date?** | No real Mars cycle from 700 BC to AD 1 has both halves within ±4 days of 349 (0 of 328). The closest real cycles all have Mars's retrograde loop **in Leo** (the slow, aphelic configuration, retrograde about 80.7 days, the longest possible). They recur every 79 years: 658, 579, 500, 421, 342, 263, 216, 137, 58 BC. **The numbers echo that extreme configuration but do not single out an epoch.** 216 BC is near the proposed 205 BC (Carman & Evans), but the 79-year repeat makes that coincidence uninformative. |
| **Is the "8-day pause" a measurement?** | No. An 8-day stationary spell corresponds to 3.1, 0.77 and 0.41 arcminutes per day for Mars, Jupiter and Saturn. No single observing sensitivity gives 8 days for all three (at Jupiter's, Mars pauses 2 days and Saturn 15). **It is a convention**, applied uniformly. With it, Jupiter's arithmetic is exact: station-to-station 120 = 104 + 2 × 8. |
| **Then why is Mars's 82 "impossible"?** | Because it is the remainder of 780 − 2 × 349, and 349 is about 8 days below Mars's typical half-cycle (357–359). Whatever source gave 349 (a model or a schematic half), the shortfall was pushed into the retrograde. |

**What the "gaps" tell us.** The designer's process:
1. A synodic period, from the period relations (round 74).
2. One or two **free intervals per planet**, observed or modelled: Jupiter's are observed-exact, Venus's 224 and 49 close to real.
3. Conventional **8-day stations**.
4. **The remainder by subtraction.**

The misfits mark step 4. They are not concealed information, but they are diagnostic: wherever a number in the inscription is "sloppy", it was computed from the others. **A prediction for the lost Saturn and Mercury sections follows:** one inexact remainder each, and its size can be predicted from the free values once any of them are read.
