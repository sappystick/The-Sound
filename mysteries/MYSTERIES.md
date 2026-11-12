# Unsolved mysteries, lost treasures and undeciphered texts: what we tested and what is open (round 73)

## Tested this round

### The Beale ciphers (Virginia, published 1885): a treasure "map" in numbers
Three number ciphers. Cipher 2 (the treasure's contents) was solved by numbering the words of the Declaration of Independence. Cipher 1 (the location) and cipher 3 (the owners) have never been solved. `beale.py` reproduces everything below from `beale.json` (public-domain texts via Wikisource).

| Test | Result |
|---|---|
| **The pipeline works.** Cipher 2 decoded with the Declaration | "i have deposited in the county of bedford about four miles from bufords…" It scores **−5.40** English likelihood per character group. Wrong keys average **−7.37**; the best of 300 wrong keys reached −6.73, so a true key stands far apart. |
| Ciphers 1 and 3 decoded with the Declaration | −7.28 and −7.26: nonsense, as expected |
| **Gillogly's alphabet runs, reproduced** | Cipher 1 decoded with the Declaration contains **"defghiijklmmno"**. A shuffle of the same letters produces such a run only **0.2%** of the time. This is the classic sign that someone walked down the key list in order, i.e. a hoax or a deliberate test pattern. |
| **New test: is the key the King James Bible?** Every chapter start (1,185 for cipher 1, 1,188 for cipher 3) tried as the key | Best: cipher 1 −6.96 (Zechariah 5), cipher 3 −6.85 (Leviticus 13). Both sit **inside the wrong-key range**, with medians of −7.38. **No KJV chapter is the key.** |

**Verdict:** consistent with the scholarly view that ciphers 1 and 3 are not real messages: Gillogly 1980, and Nickell 1982 on language anachronisms. The Bible-as-key idea, often proposed, is now ruled out for every chapter start.

### The Copper Scroll (3Q15, Qumran): the real ancient treasure list
A list of 64 hiding places of gold, silver and sacred objects, engraved on copper (c. 50–100 CE). It has two unsolved features:
1. **Greek letter groups.** Seven location names are followed by two or three Greek letters. The groups are reported in the editions as ΚΕΝ, ΧΑΓ, ΗΝ, ΘΕ, ΔΙ, ΤΡ and ΣΚ.
2. **The missing second document.** The last entry says a duplicate with fuller explanations was hidden elsewhere. It has never been found.

| What we could check | Result |
|---|---|
| Placements confirmed in the text available here | ΚΕΝ follows "seventeen talents" (1:4); ΧΑΓ follows the immersion-cavern entry, which has no amount |
| Greek letter values | ΚΕΝ = 75, ΧΑΓ = 604, ΗΝ = 58, ΘΕ = 14, ΔΙ = 14, ΤΡ = 400, ΣΚ = 220. ΚΕΝ ≠ 17, so the one testable pairing does not support "the letters are the amounts". |
| Status | **Not testable yet.** The full transcription is in copyrighted editions: Milik 1962 (DJD III), Lefkovits 2000, Puech 2006. |

**What would make it testable:** the full Hebrew transcription with the position of each Greek group. Then three tests in this project's style:
- Greek groups as numbers, against each entry's quantities, distances and depths;
- the groups as abbreviations, against Greek and Hebrew names of places and people in the onomasticon (Eusebius);
- every place description mapped with distances in cubits, with candidate sites encoded as KLIMATA place codes so a field team can speak them.

## The map of real mysteries, ranked by how well this project's tools fit

| Mystery | What is unsolved | Data we can get | Fit | Next test |
|---|---|---|---|---|
| **Copper Scroll** | Greek letter groups; the lost second document; site identifications | Editions needed | ★★★ Hebrew, numbers, cubits, Greek, Temple | As above |
| **Voynich manuscript** (15th c.) | Unread script or language | **Full transcription downloaded** (Takahashi and others, voynich.nu) | ★★ Our blind segmentation and the voice-signal and structure tests | Does its structure behave like speech (breath-like units, a speaker signal) or like a constructed table? Compare with the same tests on John, Genesis and a known hoax text. |
| **Phaistos Disc** (Crete, c. 1700 BCE) | 241 stamped signs, undeciphered | Sign sequence (public) | ★ Too short for most statistics | Repetition and ring structure (a hymn shape) against chance |
| **Linear A** (Minoan) | Language unknown | Corpus available (SigLA / GORILA) | ★★ Numbers and fractions are partly read | Accounting tablets: totals and fractions with chance controls |
| **Rongorongo**, **Indus script** | Undeciphered | Corpora exist | ★ | Positional statistics |
| **Dorabella cipher** (Elgar, 1897) | 87 symbols | Public | ★ | Short: hypothesis tests only |
| **Tamam Shud code** (Somerton Man) | Letter string | Public | ★ | Initial-letter hypotheses with controls |
| **Shugborough inscription** (O U O S V A V V) | Eight letters | Public | ★ Too short | None that could be significant |
| **Antikythera mechanism** | Missing gears and fragments | Published tooth counts and inscriptions | ★★★ Our astronomy engine (planetary periods, phase stamps) | Test the proposed missing-gear trains against the cycles on the dial inscriptions |
| **Lost sources of John (the "Signs Gospel")** | Whether John used a written source | Our full Greek data | ★★★ Our strongest result, the voice-drawn outline | Does the narration/speech signal separate the hypothesised Signs-source passages? |

## Recommended next
1. **Antikythera:** best tool fit, and the data is published.
2. **The Signs Gospel source:** this project's own evidence, applied to a 100-year-old question.
3. **Voynich:** run the voice and structure tests the project validated on John, with controls.
4. **Copper Scroll:** once a transcription is available.
