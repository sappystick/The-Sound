# Everyday words, any language, and one program that is the whole work (round 69)

## 1. KANON in everyday words: `skins.py`

A **skin** gives every KANON syllable (one cell of the 12 × 7 grid) a familiar word with the same first consonant and the same vowel sound. The language does not change; a skin is a reversible spelling, like a font.

|   | a (cat) | e (bed) | y (day) | i (see) | o (go) | u (moon) | w (law) |
|---|---|---|---|---|---|---|---|
| k | cat | keg | cake | key | coat | cool | call |
| t | tap | tell | tape | tea | toe | tune | tall |
| p | pat | pet | pay | pea | pole | pool | paw |
| b | bat | bed | bay | bee | boat | boot | ball |
| d | dad | deck | day | deep | dough | dew | dawn |
| g | gap | get | gate | geese | goat | goose | gall |
| l | lab | let | lay | leaf | low | loop | law |
| m | map | men | may | meet | mow | moon | mall |
| n | nap | net | name | need | no | new | gnaw |
| r | rat | red | ray | reed | row | room | raw |
| s | sat | set | say | seed | so | soup | saw |
| h | hat | hen | hay | heat | hope | hoop | hawk |

Other elements of the skin:
- **Lone closing vowels:** at, egg, aim, eat, oak, ooze, awe.
- **Digits:** zero … eleven (numbers stay base twelve).
- **Marks:** stop (the breath), now (!), if (?), try (~), use (:), define / done (:: … ::), check (=).

**Example:** `sa #7 gia ta #3 | di` is said as **"sat seven geese-at tap three stop deep"**. *I am*, `demorini`, is **"deck-mow-reed-need"**.

**Why these vowels and not mop / top / pot.** In much of North America, *cot* and *caught* sound the same, so "mop" (ah) and "law" (aw) would collide. The skin therefore uses the vowel of *cat* for `a` and keeps *law* for `w`, so no pair depends on accent. "mop, top, cop, pot, pop" would fit a skin for a dialect that keeps the two vowels apart. Skins are swappable, so regional skins are allowed.

**Measured:** 2,000 random programs converted to words and back, all exact. Spellings that sound alike map to the same cell (meet/meat, no/know, so/sew, read/reed), so a speech recogniser's choice between them never matters.

**Why this is the bigger adoption win.** Ordinary speech recognisers (phone dictation, Whisper and so on) already know *cat, tea, moon*. A person can therefore speak KANON to any device **today**, without the custom human-voice decoder the roadmap listed. The text the recogniser returns converts straight back to the program. One caveat: skin words are longer than bare syllables, so speech is slower. The tone codec stays the machine channel.

**Any language.** The canonical form is the 84 cells, so each language can have its own skin, with words of the same opening consonant and vowel in that language. A program dictated in an English skin can be read back in a Spanish skin with nothing lost. The BIP39 seed-word standard is the precedent: one scheme, word lists in ten languages. Spanish has five vowels, so its skin would use diphthongs (ai, au) for the other two cells.

## 2. One program, every channel: `work/`

`work/work.kn` is 5 lines of KANON. `work/build_work.py` turns it into:

| Channel | What it is | How it comes from the program |
|---|---|---|
| **Song** (`work_song.mp3`, 77 s) | The program spoken in just-intonation tones over a drone, then the program's own output melodies | `encode()` of the program with error-correction words, then `render_events()` of what it computes |
| **Lyrics** | "deck-mow-reed-need stop sat seven geese-at tap three …" | The English skin of the same program: the singer sings the code |
| **Music video** (`work.mp4`) | Each frame shows the word being sounded drawn as its seal (growing as it is sung), the verse's ring of words, the error-correction words and the lyric | Drawn frame by frame from the program and its timeline |
| **Contract** | Shares 50 / 30 / 20 (sum checked = 100). Revenue 5,000 pays 2,500 / 1,500 / 1,000. | `::tako` and `::paga` are verses *inside the song*, run by the same machine |
| **Statistics** | Words, syllables, verses, duration, melodies, plays | Computed from the program; play counts are fed in |
| **Identity** | `id` = SHA-256 of the canonical source; seal `=goma` | One hash for everything |

**Verified:**
- **The song decodes back to the exact source**, drone included (`song_decodes_to_source: true`). The song *is* the program, not a description of it.
- **Rebuilding reproduces every hash.** `build_work.py --verify` re-renders from source and gets MATCH for the id, the seal, the song's audio samples, the video's frames and the contract. Anyone holding the source can regenerate the whole work and check any copy.

So where a work today scatters across separate places (audio file, video file, lyric sheet, label contract, royalty statement, streaming stats, registration), here **one source holds all of them**. Every rendering can be checked against it.

## 3. Crypto: what it is good for, honestly

| Use | How | Status |
|---|---|---|
| **Seed phrases that repair themselves** | Today's recovery phrases (BIP39) can only say "this is wrong". With skin words plus Reed–Solomon parity words, up to 2 misremembered or misheard words are repaired. | Code ready (`add_ecc` plus skins). Caveat: the parity words are derived from the secret and leak about 6.8 bits each, so the secret must be made longer to compensate. Needs a security review before real money. |
| **Speak-to-confirm transactions** | "send … to *pole-moon-…*": the address and amount as a sealed, error-corrected verse that the wallet reads aloud and the user repeats back | Design |
| **Owning a work** | Register the work's `id` (the source hash) on a chain, for example as token metadata. Owning the token points to the one source from which song, video, contract and statistics all derive, and anyone can verify a copy. | Design: nothing deployed |
| **The contract executing on chain** | A blockchain cannot run the KANON VM directly. Either transpile the contract verses (`::tako`, `::paga`) to the chain's contract language, or keep KANON as the human-readable, sealed specification while a conventional smart contract checks the hash. | Design |
| **Statistics on chain** | Play counts come from outside the chain, via an oracle (a trusted data feed). KANON makes the *rule* verifiable, not the *data source*. | Limit stated |

**Not claimed:**
- Ownership of a hash on a chain does not by itself create legal rights. Copyright and contracts still need legal form.
- Content addressing proves *which* work a copy is, not *who* made it.

## 4. Where this could go next
- **A song people can perform.** A singer sings the English-skin lyrics; a phone recognises the words and checks the seal, so a live performance can be verified against the source. Speech recognition of skin words makes this possible today.
- **Richer music.** Keep the codec layer decodable while arranging around it: drone, rhythm section, harmonised output melodies. The drone already proved compatible.
- **Visual identity.** The work's seal (`work_seal.svg`) as its cover art, and the video's per-word seals as a typeface.
- **Translations.** The same work sung in other language skins, the same hash under every one.
