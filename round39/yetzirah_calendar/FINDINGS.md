# Round 39 lens: Sefer Yetzirah's letter physics and the priestly 364-day calendar

- **Code:** `yetzirah_calendar.py`, with `tfread.py` (a reader for the Dead Sea Scrolls data). Every number below comes from `results.json`.
- **Run:** seed 39, about 5 s.
- **Downloads:** `fetch.sh`.
- **Labels:** **V** verified · **K** known in scholarship · **N** negative · **O** open · **Reading** an interpretation.

## Sources added
| Source | Where | Licence / note |
|---|---|---|
| *Sefer Yetzirah* 1–6, Hebrew and English | `sources/texts/sefer_yetzirah/sy*.json` | Sefaria main text: Warsaw 1884 Hebrew (public domain), Sefaria Community Translation (CC0) |
| *Sefer Yetzirah*, Gra version, Hebrew | `.../gra*.json` | Kaplan's English is copyrighted and was not used |
| 1 Enoch (Charles 1912, 1917); Jubilees (Charles 1902, 1917) | `sources/texts/enoch_jubilees_charles/` | public domain, archive.org `_djvu.txt` |
| Qumran calendar texts 4Q319–4Q330 | existing `sources/texts/dss/tf/1.9` | ETCBC/CACCHT (Abegg), CC BY-NC 4.0. 735 lines, with weekday numerals, priestly courses and festivals. Only counts are kept here. |

## Part A. *Sefer Yetzirah*

### A0. The letter classes, read from the text itself (**K**)
| Class | Warsaw 1884 | Gra version |
|---|---|---|
| 3 mothers (2.1, 3.1) | א מ ש | same |
| 7 doubles (4.1) | ב ג ד כ פ ר ת | same |
| 12 simples (5.1) | ה ו ז ח ט י ל נ ס ע צ ק | same |
| 5 places (2.3) | אחה"ע · בומ"ף · גיכ"ק · דטלנ"ת · זסשר"ץ | same groups, in the order throat, palate, tongue, teeth, lips |
| Mother → element (3.6–3.8) | א air/breath, מ water, ש fire | same |

- Both versions partition all 22 letters. ר is a double in both ("two tongues") and is placed with the teeth.
- The Warsaw edition brackets the Mantua 1562 addition, whose teeth group reads וסצר"ש.
- Sefaria has no separate Hebrew of the Saadia recension.

### A1. Power passages against narrative (**N**)
- **Passages:**
  - God's ten utterances in Genesis 1;
  - Exod 3:14, Num 6:24–26, Deut 6:4, Ps 29, Isa 6:3;
  - all of these pooled;
  - ten divine names.
- **Profiles (7):** the share of mother letters, the share of each of the five places, and an omnibus chi-square.
- **Null:** 20,000 windows of the same length from the same book, none overlapping the passage.

| Passage | Strongest deviation | p | q |
|---|---|---|---|
| Num 6:24–26 | palatals 33% vs 15% | 0.0009 | 0.027 |
| Pooled | linguals 16.2% vs 20.3% | 0.003 | 0.046 |
| Gen 1 speech | dentals 17.2% vs 13.2% | 0.012 | 0.12 |
| Exod 3:14 | mothers 35% vs 23% | 0.029 | 0.22 |
| Ps 29 | mothers 13% vs 19% (lower) | 0.039 | 0.24 |
| Divine names | gutturals 37% vs 23% | 0.024 | 0.22 |

The two significant results come from grammar, not letter power:
- **Num 6:** the six "you" suffixes (ך) and YHWH.
- **Pooled:** fewer ת and א, because speech and poetry use fewer prose particles. The object marker את occurs 1.8 times per 100 words here, against 3.6 in the books. The result stays at p = 0.04 with the divine names removed.

In Gen 1 the dentals come from ארץ, עץ and זרע. The mother letters are not raised in any passage.

**Power check:**
- Isa 28:10 (p = 0.021) and the shin stanza of Ps 119 (p = 0.016) are detected.
- The mem and bet stanzas are missed. The smallest detectable shift is about 11 points at 60 letters and 5 points at 545 letters.

### A2. The mothers as elements (**N**)
| Test | Share | Null | Ratio | p | q |
|---|---|---|---|---|---|
| Water passages, מ | 11.6% | 8.3% | 1.41 | 0.0014 | 0.028 |
| Same, with the 23 tokens of מים removed | 8.8% | 8.2% | 1.08 | 0.29 | 0.63 |
| Fire passages, ש | 4.3% | 5.3% | 0.80 | 0.91 | 1 |
| Same, with אש removed / shin-dot only | 4.0% / 3.0% | 5.3% / 4.1% | 0.74 / 0.73 | 0.96 | 1 |

The water excess is the word "water" itself, which also serves as the positive control. Nothing is left once it is removed. Fire passages are not rich in ש even before אש is removed.

### A3. The 231 gates (**N**: the effects are vocabulary)
- **Test:** Genesis 1:1–2:3 (469 words, 1,338 letter pairs) against 5,000 non-overlapping Torah blocks of the same size.
- **Omnibus:** p = 0.31.
- **Single gates:** הי, הל and ימ survive correction within the 231 (q = 0.015). They come from the words ויהי, אלהים, השמים and המים.
- **Unused gates:** 9 gates never occur inside a Torah word (גט גק זט זס זצ חע טס סצ צש). These reflect constraints on Hebrew roots.
- **Controls:** Numbers 7, a repetitive offering list, gives 4 significant gates (omnibus p = 0.02). A random block gives none.
- **Method note:** the null must exclude windows that overlap the tested passage. Before that fix, Numbers 7 gave 0 significant gates.

## Part B. The 364-day calendar

### B0. The model, checked against the scrolls (**K**, confirmed **V**)
**The model:** months of 30, 30 and 31 days, four times over, give 364 days, exactly 52 weeks. 1/I is a Wednesday.

**The model as the texts state it:**
- 1 Enoch 72 gives 30, 30, 31 … = 364 days (72:32).
- 1 Enoch 74:13–16 gives 1,092 / 1,820 / 2,912 days = 3, 5 and 8 × 364, and 1,062 / 2,832 = 3 and 8 × 354.
- Jubilees 6:29–38 gives 13 weeks per quarter, 52 weeks and 364 days, and says the moon comes "ten days too soon".

**Festival weekdays the model implies:**
- Passover 14/I is a Tuesday and Unleavened Bread 15/I a Wednesday.
- The Omer 26/I is a Sunday, Second Passover 14/II a Thursday and Weeks 15/III a Sunday.
- Remembrance 1/VII is a Wednesday, Atonement 10/VII a Friday and Tabernacles 15/VII a Wednesday.
- No feast falls on a Sabbath.

**Checks against the scrolls:**
- All 57 festival weekdays in 4Q320 (4 iii–vi), 4Q319, 4Q325, 4Q326 and 4Q329a match the model.
- All 42 priestly courses in 4Q320's six-year table are predicted, p = 2.6 × 10⁻⁵⁷. The one fitted parameter is that Gamul serves in week 0, with weeks running Sunday to Sabbath.
- The scrolls contradict the 1917 Jubilees footnote that puts 14 Nisan on a Sabbath. It is a Tuesday, as Jaubert (1953) had it.
- Hanukkah and Purim do not appear in these scrolls.

### B1. Time markers in John (from SBLGNT; 92 verses)
- **Days:** the next day 1:29, 35, 43; 6:22; 12:12 · the third day 2:1 · two days 4:40, 43; 11:6 · four days 11:17 · six days before the Passover 12:1 · after eight days 20:26.
- **"The next day" by Gospel:** John 5, Matthew 1, Mark 1, Luke 0.
- **Hours:** the tenth 1:39 · the sixth 4:6 and 19:14 · the seventh 4:52.
- **Festivals:** Passover ×10 · Tabernacles 7:2 (its middle 7:14, last day 7:37) · Dedication 10:22 · "a feast" 5:1.
- **Week:** Sabbath 5:9; 9:14; 19:31 · Preparation 19:14, 31, 42 · first day of the week 20:1, 19.
- **Other:** night, early morning and evening; four months 4:35; years 2:20, 5:5, 8:57.

**John's timeline:**
- **Opening week:** day 1 at 1:19 → day 2 at 1:29 → day 3 at 1:35 → day 4 at 1:43 → "the third day" at 2:1.
- **Year 1:** Passover 2:13 → 4:35 → 4:52.
- **Year 2:** the feast and Sabbath of 5:1, 9 → Passover near (6:4) → Tabernacles 7:2–37 → Sabbath 9:14 → Dedication 10:22.
- **Year 3:**
  - before the feast: Passover near (11:55) → six days before (12:1) → five days before (12:12);
  - the last night: supper 13:1, night 13:30 → morning 18:28;
  - the day of death: Preparation, the sixth hour (19:14) → the great Sabbath (19:31);
  - after: 20:1 → 20:26.

### B2. Which calendar fits John (model comparison)
The assumptions are written out in `results.json`.

**Astronomy checks:**
- The new-moon formula reproduces Meeus's 1977 worked example to within 1 minute.
- The AD 33 full moon falls on 3 April, the date of the eclipse.

**Which years fit:**
- 14 Nisan falls on a Friday only in AD 27, 30 and 33. This holds for first-visibility thresholds of 18–30 hours.
- With John 2:20 and his three Passovers, the fit is 7 April AD 30 (**K**: Fotheringham 1934; Humphreys & Waddington 1983; Brown; Meier).

| John's marker | Lunar | 364-day | Jaubert's hybrid |
|---|---|---|---|
| 18:28 the Passover meal is still ahead | fits | contradicts | fits |
| 19:14 the Preparation of the Passover | fits | contradicts | fits |
| 19:31 the great Sabbath is the 15th | fits | contradicts | fits |
| 13:1 before the feast | fits | fits | fits |
| 13:30–19:14 one continuous night and day | fits | fits | contradicts |
| 10:22 Dedication | fits | contradicts | fits |
| **Fit / contradictions** | **6 / 0** | **2 / 4** | **5 / 1** |

- **Result:** John's chronology fits the official lunar calendar with no contradictions.
- **Known:** Jaubert (1957) also kept John on the lunar calendar and put the 364-day calendar behind the Synoptic supper (**K**, scored explicitly here).
- **Caveat:** this is a model comparison, not a p value.

### B3. John 1:19–2:11 as a week
- Three "next days" plus "on the third day" give day 6 by inclusive counting, or day 7 by exclusive counting.
- The usual 7-day reading (Boismard 1956; Brown 1966) needs an extra day at 1:39–41.
- **Manuscript check:**
  - P66, P75, Alexandrinus and Vaticanus read πρῶτον in 1:41; Sinaiticus and Washingtonianus read πρῶτος.
  - None reads πρωΐ ("in the morning"), the conjecture that would supply the seventh day.
  - **K**; the manuscript check is new here.
- The Sinai "third day" echo: Olsson 1974.
- **Reading, O:** if the "third day" of Cana were a Tuesday, it would fall on the 364-day calendar's Passover weekday.

## Multiple testing
63 tests were corrected together (Benjamini–Hochberg). 4 have q < 0.05:
- the priestly courses (a positive control);
- the Num 6 palatals and the pooled linguals (grammar and genre);
- the raw water/מ excess (the word "water" itself).

## New vs known
**New here:**
- the first quantitative test of *Sefer Yetzirah*'s letter categories on the Hebrew Bible (negative);
- a calendar engine that reproduces every weekday and priestly course in the scrolls;
- John's chronology scored explicitly under three calendars;
- the opening week counts 6 days, not 7, in all six early manuscripts checked.

**Known:** Charles; Jaubert 1953 and 1957; Talmon, VanderKam and Ben-Dov on the courses; Fotheringham; Humphreys & Waddington; Brown; Boismard; Meier.

## Failed or limited
- A1 has low power: the mem and bet acrostic stanzas are missed.
- The Charles OCR is noisy, so the 1917 editions were used for the checks.
- 4Q321's moon observations were not modelled.
- The lunar dates carry ±1 day.

## Next
1. Rerun A1 with a null matched for genre.
2. Model 4Q321's moon observations against the computed moons.
3. Test 5:1/5:9 (a feast on a Sabbath) under each calendar.
