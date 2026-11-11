# The spoken world behind John: what was said, in what language, and how it sounded

This file gathers the evidence the voice reconstruction rests on, and marks each point as **firm**, **probable** or **conjecture**. The citations are given from memory of the standard works and should be checked against the printed sources before publication.

## 1. Three layers of speech
| Layer | What it is | Language | Status |
|---|---|---|---|
| A. The events (about AD 28–30) | What Jesus, John the Baptist and the others actually said | Aramaic for almost all of it; Hebrew for scripture; Greek possible with Pilate | Not recoverable word for word |
| B. The Gospel as composed (about AD 90–100) | The text John wrote | Greek | **Firm**: its word-chains work only in Greek (finding 12), and every early manuscript is Greek |
| C. The Gospel as performed | A reader voicing the text aloud to a gathered group | Greek, in the pronunciation of the time | **Firm** that it was read aloud; the reader's delivery is reconstructed |

**The voice we render is layer C**: what a first-century audience heard. Layer A can only be approximated. The Aramaic sayings (section 5) are an illustration of the sound of that language, not a recovery of the words.

## 2. Who spoke what (layer A)
| Speaker | Most probable language | Confidence | Basis |
|---|---|---|---|
| Jesus | Galilean Aramaic | very probable | Aramaic sayings kept in the Gospels (*talitha koum*, *ephphatha*, *abba*, *eloi eloi lema sabachthani*); John keeps *rabbi*, *Messias*, *Kephas*, *rabbouni* |
| John the Baptist | Judean Aramaic | probable | A Judean preacher to Judean crowds (Josephus, *Antiquities* 18.116–119); his self-description quotes Isaiah 40:3 |
| The disciples | Galilean Aramaic; some bilingual | probable | Peter's Galilean accent was recognisable (Matthew 26:73); Andrew and Philip have Greek names and the Greeks approach Philip (John 12:21) |
| Priests, Levites, Pharisees | Aramaic, or Hebrew for legal debate | probable | Hebrew was still a living language (Qumran documents, the Bar Kokhba letters, the Mishnah) |
| Pilate | Greek with provincials; Latin officially | probable | His Latin inscription at Caesarea; the three-language title on the cross (John 19:20) |
| The narrator | Greek | firm | Section 1 |

The general picture, that Aramaic was the everyday language with Hebrew and Greek alongside, is the standard view (Fitzmyer, "The Languages of Palestine in the First Century AD"). The machine-readable version of this table, with a basis for every speaker, is `code/voice/language_layer.json`.

## 3. How the Greek sounded (layer C)
The engine's Koine values, set against the reconstruction for Judeo-Palestinian Koine (Kantor, *The Pronunciation of New Testament Greek*, 2023; Gignac's grammar of the papyri; Horrocks, *Greek: A History of the Language*; Allen, *Vox Graeca*):

| Letter(s) | Classical | 1st-century Palestine | Our engine | Evidence |
|---|---|---|---|---|
| αι | ai | e | ɛ | Spelling swaps αι/ε in papyri and inscriptions |
| ει | ei | i | i | ει/ι swaps (the commonest "error" in the papyri) |
| οι, υ | oi, ü | ü | y | οι/υ swaps; not yet merged with ι |
| η | long open e | close e | e | η/ε swaps, not yet η/ι in most regions |
| ω, ο | long/short o | o (length lost) | o | ω/ο swaps |
| αυ, ευ | au, eu | av/af, ev/ef | av, ɛv | Spellings with β; Latin transcriptions |
| β | b | soft v | v | β for Latin v |
| γ | g | soft gh | ɣ | Omission and γ/ι swaps between vowels |
| δ | d | d or soft dh | ð | Uncertain for this date |
| φ, θ, χ | aspirated p, t, k | still aspirated stops | pʰ, tʰ, kʰ | Latin and Semitic transcriptions; fricatives come later |
| Accent | pitch | turning into stress | pitch rise + stress | Loss of vowel length; accent-based verse appears later |

This is the same sound system that explains finding 11: about half of the manuscript variants in John sound identical in it, and almost none do in classical pronunciation.

## 4. How it was delivered
| Point | Status | Basis |
|---|---|---|
| Read aloud to a group by a reader | firm | Public reading is assumed in the texts themselves (Revelation 1:3; Colossians 4:16; 1 Timothy 4:13); Justin, *First Apology* 67, describes "the memoirs of the apostles" being read |
| The reader was a man | probable | The office of reader (*anagnōstēs*) in the early churches |
| Melody followed the word accents within about a fifth | probable | Dionysius of Halicarnassus, *On Composition* 11; the Seikilos epitaph |
| Phrase-end cadences | probable | Byzantine lectionary (ekphonetic) notation from about the 8th century: the oldest direct record of how the Gospels were intoned, but 700 years later |
| The voice was suited to the speaker and the emotion | conjecture for any given verse | Quintilian, *Institutio Oratoria* 11.3, on delivery; applied as a separate, switchable layer |
| The room | probable | House gatherings and synagogue halls (Dura-Europos; Galilean synagogues); the engine's room models |

## 5. The Aramaic sayings (illustration only)
Eight short sayings from John 1 are voiced in Aramaic in `audio_model/v2/aramaic_*.mp3`, listed in `aramaic_index.json`.
- **Text:** the consonants of the Syriac Peshitta.
- **Vowels:** supplied by hand from Classical Syriac grammar, because no open vocalised Syriac New Testament was available. **This needs a Syriacist's check.**
- **Dialect:** Syriac is a later, eastern Aramaic. The Galilean and Judean Aramaic of AD 30 differed in vowels, forms and some vocabulary.
- **Voice:** a male Arabic neural voice, used only because it has the Semitic consonants; it is driven by the phonetic transcription, not by Arabic.

## 6. Data now attached to every spoken word
`audio_model/v2/opening_*_C_full.json`:

| Data point | Source |
|---|---|
| Word, verse | SBLGNT |
| Pronunciation (IPA), syllables, accent type | Project engine, Koine era |
| Start and end time | Measured from the synthesis |
| Planned pitch per syllable; measured pitch of the audio | Rulebook; Praat |
| Loudness | Rulebook; stress |
| Rules applied | `delivery_rules.json`, evidence or interpretive |
| Speaker | Estimated; hand-checked for 1:1–2:11 (`speaker_overrides.json`) |
| Probable original language and confidence | `language_layer.json` |
| Aramaic word kept in the Greek | `language_layer.json` |
| The verse in P66, P75, Sinaiticus and Vaticanus: words that differ, and how many differences sound the same | CNTR transcriptions |
| Place of the scene | OpenBible.info geodata |
| Echoes elsewhere in the Gospel | Shared vocabulary (round 27) |

## 7. What would make it more accurate (not available in this environment)
1. **A trained human reader** following the pronunciation script and pause marks. This is the real standard; everything synthetic should be checked against it.
2. **A voice model trained on reconstructed Koine or on a male Greek reader.** The open Greek neural voices are Modern Greek and female; ours is shifted to a male range.
3. **A vocalised Aramaic text** (the SEDRA database or a Syriacist's transcription), and a reconstruction in Galilean Aramaic by a specialist.
4. **Measured acoustics** of surviving first-century halls, to replace the modelled rooms.
5. **Generated scenery or a lip-synced reader.** These need GPU video models and would be illustration, not evidence.
