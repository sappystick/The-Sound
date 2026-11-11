---
name: coptic-lens
description: Read Coptic (Sahidic) texts, including Nag Hammadi Thomas, Pistis Sophia and Shenoute, against Sahidic John and the Synoptics, using Coptic SCRIPTORIUM annotations. Covers vocabulary lean (size-matched Delta against a chunk null), a word-by-word Greek-retention test against MorphGNT, and "I am" (ⲁⲛⲟⲕ ⲡⲉ) predicate rates. Use when rerunning or extending the Coptic or translation-layer lens.
---

# Coptic lens

## Steps
1. **Fetch:** `bash round39/coptic/fetch.sh`. This makes a blobless sparse clone of CopticScriptorium/corpora (the CoNLL-U folders plus `sahidica.nt_TT.zip` and `sahidic.ot_TT.zip`). Unzip the TT files to `sources/texts/coptic_scriptorium_tt`. Use the TT files: the NT CoNLL-U files are placeholders.
2. **Run:**
   ```bash
   python3 round39/coptic/coptic.py sources/texts/coptic_scriptorium sources/texts/coptic_scriptorium_tt sources/texts/sblgnt round39/coptic/results.json
   ```
3. **Tokens** are SCRIPTORIUM norm units.
4. **Greek-loan lexicon:** every lemma tagged `lang=Greek` (TT) or `OrigLang=grc` (CoNLL-U) anywhere in the corpus, excluding proper names.

## Controls
- **T1, positive:** 1–3 John must lean to John. Acts → Luke is too weak a link to survive translation.
- **T2b, positive:** proper names must be found at least 80% of the time.
- **T2b, negative:** pairing verses at random must give under 1% matches.
- **T3, positive:** recall of the Greek ἐγώ εἰμι + nominative verses.

## Pitfalls
- Sahidic Luke is nearest everything. Judge nearness only against the null.
- Chapter files can run past the end of their chapter (John 7 holds 8:12–59). Detect the drop in verse numbers.
- The lemma ⲁⲛⲟⲕ also covers clitic pronouns. Require the surface form ⲁⲛⲟⲕ.
- ⲙⲉ is two words, "truth" and "love". Split them by part of speech.
- The annotation is automatic, and the "I am" counts do not check who is speaking.
- Sahidica is for academic use only. Keep counts and short quotations.
