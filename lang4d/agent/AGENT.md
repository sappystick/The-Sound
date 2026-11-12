# KANON-AGENT: approve exactly what runs (round 72)

## The question: can the English line up with the actual command?

Yes. It can do so on the core model, without inventing a looser English layer. Three alignments, all checked by code:

| Layer | What it says | How it stays exact |
|---|---|---|
| **Verb = syllable** | Tool names are KANON syllables whose English skin word *is* the verb: `:py` **pay**, `:te` **tell**, `:mi` **meet**, `:kw` **call**, `:hi` **heat**, `:ma` **map**, `:le` **let**, `:no` **no** | The skin table is the same one used everywhere; nothing new was invented |
| **Sentence = action** | "Pay $250.00 to Maria Lopez." | Generated from fixed templates filled with the verse's own values, never from the agent's words. It **parses back to the identical verse**: 2,000 of 2,000 random actions. |
| **Precise form = every step** | "1) keep 25000 in moon. \| 1) keep 1 in mercury. \| 1) call py." | `plain.py`: an English reading of *any* KANON program, in execution order. It parses back with identical behaviour for every well-formed program tested (1,110 of 1,110), and exact text apart from leading zeros and urgent words, which are moved to where they run. |

**Errors are reported in the same language as the command.** A misheard confirmation word produces "word 3: heard 'raw', expected 'gate'. Please repeat the three words." A lie in the agent's explanation produces "the agent says $25, the action says $250.00". A limit violation produces "$5,000.00 is outside the allowed range $0.01 to $1,000.00".

## The flow
1. The agent proposes an **action verse**: literal arguments in named planes, then one tool call. Example: `ka #12574 | ke #1 | :py`.
2. **Static checks** run before a person sees anything:
   - only literal arguments (no computed amounts);
   - one approved tool;
   - every argument within the tool's limits;
   - known contacts, messages and places.
3. **The person** sees and hears:
   - the sentence;
   - a flag for anything in the agent's own explanation that the action does not contain;
   - the seal;
   - **three confirmation words** from SHA-256 of the verse.

   The confirmation words come from the 76 non-verb skin words, giving 438,976 combinations; they can never be "pay" or "no". The two-syllable seal (7,039 values) is only for the eye.
4. **The person says or types the words.** Homophones count ("lei" for "lay"). On a match, their device signs the verse hash with a one-time nonce: Ed25519 in Python, ECDSA P-256 in the browser.
5. **The executor** re-checks everything, verifies the signature against *this* verse, then checks that the nonce is unused, then runs.

## Results (`approve.py` → `TRANSCRIPT.md`, `results.json`)

| Scenario | Result |
|---|---|
| Honest payment, approved by voice words | executed |
| Explanation says $25, action says $250 | flagged: "the agent says $25, the action says $250.00" |
| Payee swapped after approval | refused: the approval does not match this action |
| Amount raised after approval (page) | refused: the approval does not match this action |
| Approval replayed | refused: already used |
| $5,000 against a $1,000 limit | rejected before the person sees it |
| Amount computed inside the action | rejected: arguments must be stated, not computed |
| Drone at 300 m against a 120 m limit | rejected before the person sees it |
| Confirmation said with homophones | accepted |
| One confirmation word wrong | refused, naming the word |
| The action sent over a GSM phone call (phone channel plus Reed–Solomon) | received with an identical hash |
| English sentence parses back to the verse | 2,000 of 2,000 |
| Browser and Python produce the same sentence, words, seal and rejections | 11 of 11 cases |

**Spoken readbacks** (Piper voice) are in `readback_pay.mp3` and `readback_drone.mp3`. The page speaks with the browser's own voice.

## Limits
- Contacts, messages and places are fixed registries in this demo. A real deployment needs signed registries, so a renamed contact cannot change what "Maria Lopez" means.
- The claim check catches amounts and names. It is a warning, not a proof. The guarantee is the sentence, which comes from the verse.
- Voice is not authentication. The signature comes from the person's device key; the spoken words only confirm attention to *this* action.
- Speech recognition is not built into the page, because the artifact frame blocks the microphone. Any recogniser can feed the text field, and homophones are handled.
