---
name: yetzirah-calendar-lens
description: Rerun The-Sound's Sefer Yetzirah letter-class tests on the Hebrew Bible (mothers, five places of articulation, 231 gates), and the priestly 364-day calendar engine (Enoch, Jubilees, Qumran 4Q319–4Q330) with the lunar new-moon model for dating John's chronology. Use for any letter-class or calendar claim about scripture.
---

# Yetzirah and calendar lens

## Procedure
1. **Fetch:** run `bash round39/yetzirah_calendar/fetch.sh`. It downloads the Sefaria Sefer Yetzirah JSON (main and Gra versions) and Charles's Enoch and Jubilees from archive.org. The run also needs the existing `morphhb/wlc`, `sblgnt`, `cntr` and `dss/tf/1.9` texts.
2. **Run** (about 5 s, seed 39):
   ```bash
   python3 -I round39/yetzirah_calendar/yetzirah_calendar.py sources/texts round39/yetzirah_calendar
   ```
3. **A0, letter classes:** extract them from the Sefer Yetzirah text itself, never from memory. The main text marks its letter groups with gershayim; the Gra version uses single geresh marks.
4. **A1 and A2, letter profiles:**
   - Compare letter-share profiles against windows of the same length from the same book. Align windows to word starts and exclude any window that overlaps the passage.
   - Normalise final letter forms. ש counts both shin and sin; the shin-dot variant comes from the WLC pointing.
   - In element tests, always rerun with the element words removed (lemma H4325 mayim, H784 esh).
5. **A3, the 231 gates:**
   - Count unordered adjacent pairs of distinct letters inside words.
   - The null is non-overlapping Torah blocks of the same word count.
   - Correct within the 231 gates; the omnibus chi-square goes into the round's correction family.
6. **B0, calendar model:**
   - The model is months of 30, 30 and 31 days, four times over, with 1/I on a Wednesday.
   - The positive control is the scrolls themselves. Parse the CACCHT numeral signs (variants of א = 1, י֜ = 10, ך֜ = 20) and the course names in 4Q320 4 iii–vi and the other calendar texts. Expect 57 of 57 weekdays and 42 of 42 courses to match.
   - Map lines to words with `oslots` (`tfread.dss_lines`) and drop empty glyph tokens.
7. **B1 and B2, John's chronology:**
   - Take John's time markers from SBLGNT by lemma.
   - Compute the lunar Nisan from the Meeus new-moon series plus ΔT, with first-visibility thresholds of 18, 24 and 30 hours and an equinox rule.
   - Score each marker in John as consistent, contradicted or undetermined under each calendar.

## Controls
- **Letter profiles:** the shin stanza of Ps 119 and Isa 28:10. The mem and bet stanzas are below the test's power.
- **Lexical:** the raw water/מ excess.
- **Gates:** Numbers 7.
- **Astronomy:** Meeus's example 49.a and the full moon of 3 April AD 33.
- **Calendar:** the Qumran weekdays and priestly courses.

## Pitfalls
- **Power:** short passages have low power. Report the smallest detectable shift.
- **Genre:** speech and poetry lack את and אשר, which shifts the share of ת and א.
- **Overlap:** null windows that overlap the passage hide the effect.
- **Charles's footnote:** the 1917 Jubilees footnote putting 14 Nisan on a Sabbath is wrong; the scrolls give a Tuesday.
- **Hanukkah:** it is not a feast of the 364-day calendar.
- **Lunar dates:** they are ±1 day. B2 is a model comparison, not a p value.
- **Licence:** the Dead Sea Scrolls data are CC BY-NC. Commit counts only, never transcriptions.
