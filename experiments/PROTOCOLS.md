# Experiment protocols: words of power, round 2

Each protocol states:
- the claim it draws from;
- what is measured, and the conditions;
- the equipment and procedure;
- the analysis, fixed in advance;
- what has already been run, and what still needs people or equipment.

Claims are recorded as claims. Whether any effect is real is decided by the data.

---

## E1. Breath and heart: does reciting sacred text pace the body?
**Source of the claim:** recitation as healing (Iamblichus, *Life of Pythagoras* 110–111); 1 Samuel 16:23, "there was breathing-space (*revach*) for Saul"; modern lead: Bernardi et al., *BMJ* 2001 (rosary and mantra slowed breathing to about 6 a minute).

| | |
|---|---|
| **Participants** | 30 adults with no heart condition. Within-subject: everyone does every condition. |
| **Conditions** (5 min each, order counterbalanced, 3 min rest between) | 1. seated rest; 2. silent reading of the text; 3. reading aloud at normal speaking pace (track `e1_lords_prayer_normal.mp3`); 4. reciting along with the Koine chant track (`e1_lords_prayer_chant.mp3`, looped); 5. the same with `e1_john_prologue_chant.mp3`; optional 6–7: Psalm 23 in Hebrew and the Ave Maria in Latin, if a reader of those languages records a chant track |
| **Equipment** | a chest-strap heart monitor that records beat-to-beat (RR) intervals (for example Polar H10 with a logging app); a quiet room; headphones |
| **Measures** | breathing rate (the frequency of the heart-rate oscillation); RMSSD and SDNN (heart-rate variability); share of heart-rate power at 0.08–0.12 Hz (the 6-a-minute resonance band); mean heart rate |
| **Hypotheses** | H1: breathing is slower during chant than during silent reading and normal speech. H2: the 0.1 Hz share is higher during chant. H3: heart-rate variability (RMSSD) is higher during chant than during normal speech. |
| **Analysis** | `e1_e2_analysis.py`: Wilcoxon signed-rank, each recitation against silent reading and against normal speech; 3 measures × 2 comparisons, Holm-corrected |
| **Data file** | `e1_data_template.csv`: participant, condition, t_s, rr_ms |
| **Already run here** | the recitation tracks are rendered; the analysis code is checked on simulated data (it recovers a known 6-a-minute rhythm). Phrasing alone predicts 11 breaths a minute when chanted and 21 when read at speaking pace. |
| **Safety** | stop if dizzy (slow breathing can cause light-headedness); no breath-holding |

## E2. The hum: does sounding Amen raise nitric oxide?
**Source of the claim:** sacred formulas ending in a hum (Amen, Om); 79% continuous voiced sound in sacred formulas against 67% in ordinary text (round 37, T5); modern lead: Weitzberg & Lundberg 2002 (humming raised nasal nitric oxide about fifteen-fold).

| | |
|---|---|
| **Participants** | 20 adults, no cold or nasal congestion on the day, no nitrate-rich food for 2 hours |
| **Conditions** (each 3 × 10 s, randomised) | quiet nasal exhalation; sustained "Amen" with a long m; the seven vowels α ε η ι ο υ ω on one note; "Om"; ordinary speech of the same length |
| **Equipment** | a handheld exhaled nitric-oxide meter (FeNO device) with a nasal sampling adaptor, or a chemiluminescence analyser in a lab |
| **Measures** | nasal nitric oxide (ppb) per condition |
| **Hypotheses** | H1: Amen and Om exceed quiet exhalation. H2: Amen and Om exceed the vowel chant and speech, because the closed-mouth hum is the active part. |
| **Analysis** | `e1_e2_analysis.py`: fold-change against quiet exhalation; Wilcoxon signed-rank |
| **Data file** | `e2_data_template.csv`: participant, condition, feno_ppb |
| **Already run here** | analysis code checked on simulated data. Needs the meter. |

## E3. The seven vowels: is there a melody in the overtones?
**Source of the claim:** Demetrius, *On Style* 71: Egyptian priests sounded the seven vowels in succession "instead of flute and lyre".

| | |
|---|---|
| **What was run here** | Source-filter synthesis on an exactly held 110 Hz note (`audio/e3_seven_vowels_110hz_dry.mp3` and `_temple.mp3`), and measurement of the strongest upper harmonic in each vowel |
| **Result** | **α, ε, η: harmonics 11, 19, 17, exactly as predicted. ο, ω: 6 and 7, within one of the prediction.** ι and υ: the predicted high overtones (21, 15) are not the strongest in a plain voice, because the low resonance dominates. Overtone singers bring such harmonics forward by narrowing the mouth's resonance. |
| **What still needs people** | Six trained singers (two of them overtone singers) chant the vowels on 110 Hz and 146 Hz, as a plain voice and as an overtone voice. Recordings are taken at 1 m in a dry room. |
| **Measures** | the strongest harmonic in each vowel, and whether 20 listeners can sing back or point to the overtone melody when asked "do you hear a second, high melody?" (yes/no, then hum it) |
| **Hypotheses** | H1: in plain singing, open vowels already carry an audible overtone melody. H2: overtone singers make all seven audible. H3: listeners detect a second melody more often in the vowel chant than in the same note sung on one vowel. |
| **Analysis** | detection rates compared by McNemar's test; harmonic predictions checked within ±1 harmonic |
| **Code** | `e3_e4_compute.py`, `e3_stimulus.py` |

## E4. Rooms: do the described sanctuaries resonate with the chanting voice?
**Source of the claim:** the inner sanctuaries are cubes: the tabernacle's 10 cubits each way (inferred from Exodus 26) and Solomon's "twenty cubits long, twenty wide, twenty high" (1 Kings 6:20). The voice speaks "from between the cherubim" there (Numbers 7:89).

| | |
|---|---|
| **What was run here** | resonant frequencies (room modes) of the described rooms, treated as rigid boxes, with two cubit values; a control room of equal volume with ordinary proportions |
| **Result** | **A cube gathers its resonances onto few frequencies.** The 10-cubit cube (4.45 m) puts its 73 resonances between 85 and 180 Hz onto **15** frequencies, with up to **9** coinciding; an ordinary room of the same volume spreads them over **56**, with at most 3 coinciding. Solomon's 20-cubit cube rings three-fold at 96, 116, 135, 154 and 173 Hz (common cubit), in the range of a male chanting voice. With the royal cubit, its side (10.46 m) equals the length of the King's Chamber in the Great Pyramid (10.47 m, also 20 royal cubits). |
| **What still needs people** | Measure a surviving cube-shaped or near-cube stone chamber: sweep a sine tone from 60 to 250 Hz from the centre and record at three points. Then have chanters sing the room's strongest mode and a non-mode note, with 20 listeners inside rating "fullness" and "presence", not told which is which. |
| **Hypotheses** | H1: the measured resonances match the predicted modes. H2: a chant on a stacked mode is rated fuller than one off the modes, with loudness matched. |
| **Analysis** | match of measured to predicted peaks within ±3 Hz; paired listener ratings (Wilcoxon) |
| **Code** | `e3_e4_compute.py`, `e3_stimulus.py`; results in `e3_e4_results.json` |

## E5. Sound or sense: does a formula lose force in translation?
**Source of the claim:** Origen, *Against Celsus* 1.25: translated, an incantation becomes *atonon*, slack and powerless; "not the meanings … but the qualities of the sounds have power". Iamblichus, *On the Mysteries* 7.4–5.

| | |
|---|---|
| **Built and live** | the listening test "Sound or Sense", https://claude.ai/artifact/9MtD9phqr71mXVq9qgvzrz. Eight formulas × three versions: **original** sound (reconstructed Koine), the same syllables **scrambled** (same voice), and **English translation**; randomised order; ratings of force (1–7) and calm–stirred (1–7); "I understood the words" per item; languages known. Responses are stored anonymously and pooled. |
| **Participants** | 40 or more. Analyse separately those who understand Greek, Hebrew or Aramaic and those who do not. |
| **Hypotheses** | H1 (main): original > scrambled in force. H2: original > translation in force (confounded by voice; secondary). H3: the effect is larger for listeners who do not understand the words, which would mean the sound and not the meaning carries it. |
| **Analysis** | per-person means for each version; paired difference original − scrambled with 95% interval (shown live on the page); Wilcoxon signed-rank; item-level table |
| **Sharing note** | to take part, people need the page shared with them at a level that lets them use it (not view-only): view-only visitors can listen but their ratings are not saved |
