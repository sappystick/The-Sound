# Sala: a small language for the ear, the eye, the hand and the machine (version 0.1)

**Status:** a first design, built and checked by program. Nobody has learned it yet. Whether it is "learned very quickly" is an open question that only a trial with learners can answer.

Pages:
- language guide with a live parser: `lang/page/`;
- spoken course: `lang/course/` (the Akouo engine).

## Design in one table
| Channel | What it is | Basis |
|---|---|---|
| 1 Sound | 10 consonants (p t k m n s l w y h) and 5 vowels (a e i o u), giving 50 consonant-vowel syllables. Roots are two syllables, grammar words one. Stress falls on a root's first syllable. | Each sound is in 56–97% of 3,020 inventories (PHOIBLE); CV is the most widespread syllable shape |
| 2 Shape | A featural script: the stroke is the consonant (lip sounds round, tongue-tip sounds straight, back sounds angled), and the dot's position is the vowel | Hangul's principle: the sign is built from the sound |
| 3 Gesture | A handshape per consonant and a place per vowel: any word can be signed syllable by syllable | Fingerspelling; untested with signers |
| 4 Melody | Six pitch contours mark stance, each also written as a final word: statement (none), question `ka`, request `pu`, joy `hi`, sorrow `he`, warning `wa` | The project's voice model; measured medians 91–137 Hz across the six |
| + Number | Every syllable is a number (consonant × 5 + vowel), every root a number from 0 to 2,499; every sentence has one parse | Greek and Hebrew letter-numbers, turned into a working code |

## Words
148 roots (`lexicon.json`), produced by `make_lexicon.py`:
1. Each meaning has a few source words that many people know, drawn from about a dozen large languages.
2. A source word is reduced to Sala's sounds and its first C-V-C-V skeleton is taken.
3. A candidate is accepted only if it differs from every root already chosen in at least two sounds.

Results:
- 70 of the 148 roots are unchanged from their source word (wata, mama, kasa, lumi, luna, nani, sala …).
- No two roots differ by a single sound, so one misheard sound never turns a root into another root.
- No root begins with `no`, which is reserved for numbers.

## Grammar: ten rules
1. Roots are two syllables; grammar words are one.
2. Words never change shape.
3. A sentence is: who or what, then `sa`, then the action or description.
4. Other parts are introduced by their own word, in any order: `ke` (what is acted on), `pe` (to, for), `na` (in, at), `wi` (with), `ho` (from, because of).
5. A describing word follows what it describes: `kasa mahi`, a big house. `le` means "of".
6. Any root can be a thing, an action or a quality, by position.
7. Time is optional: `ta` past, `ya` future; `so` can, `mu` must.
8. `mo` before a word means not; `lu` after it means more than one.
9. Clauses join with `ye` and, `yo` or, `pa` but, `ku … te` if … then; `ti … tu` encloses a describing clause.
10. A final stance word, with its melody, says how the sentence is meant.

Formal grammar (in `sala.py`):
```
SENTENCE := LINK? CLAUSE (LINK CLAUSE)* STANCE?
CLAUSE   := NP? ('sa' TENSE* 'mo'? NP? ROLE*)?
ROLE     := ('ke'|'pe'|'na'|'wi'|'ho') NP
NP       := 'mo'? HEAD (ROOT|NUMBER)* 'lu'? ('le' NP)? ('ti' CLAUSE 'tu')?
HEAD     := ROOT | 'mi' | 'yu' | 'si' | 'ha' NAME | NUMBER
```
Every phrase ends at the next grammar word, so there is exactly one parse.

## The machine layer
| Layer | Rule | Example |
|---|---|---|
| Syllable | consonant index × 5 + vowel index | `wa` = 35 |
| Root | first × 50 + second (12 bits) | `wata` = 1755 |
| Number | `no` + one syllable per digit | 153 = `notasama` |
| Call form | stance(action(who, object, to, in, with, from, time)) | `sa puke ke poli pu` → `request(open(object=door))` |
| Bytes | 6 bits per syllable, plus word break, sentence end and name codes | about half the bytes of the text |

`sala.py` implements the tokenizer, parser, literal English, call form, and byte encoder and decoder. The page carries the same parser in JavaScript.

## Checks run
- All 99 sample sentences parse, and the bytes decode back to the same text.
- The browser parser gives the same call form, bytes and literal meaning as the Python reference on all 99.
- The six melodies are measurably distinct (`melody_check.json`).
- The starter course (`build_all.py`): 89 recorded steps teach 104 sentences (111 different words) in 5.3 minutes of audio; 68 steps add exactly one new word.

## Measured costs
- Sala takes about 1.4 to 1.7 times as many syllables as English: John 1:1–5, 14 is 128 syllables against 91; the dialogue 110 against 62.
- 148 roots are less precise than a large vocabulary: "glory" is `lumi mahi`, great light.

## Not yet done
- A learner trial.
- A test of the gesture layer with signers, and of the melodies with speakers of tone languages.
- A larger vocabulary (about 500 roots) and a longer text.
- Root choices reviewed by speakers of more languages.

## Rebuild
```
python3 lang/make_lexicon.py
python3 lang/texts.py
python3 lang/voice.py <voice.onnx>
python3 lang/build_all.py <voice.onnx>
python3 lang/build_page.py
```
