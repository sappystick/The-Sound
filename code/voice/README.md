# Koine voice v2

A natural voice speaking the project's reconstructed first-century Koine. Its melody comes from a traceable rulebook.

## Pipeline
1. **Phonemes.** The project engine (`code/engine`, Koine era) turns each word into IPA syllables. Aspirated stops are written stop + h. Grave accents are read from the text and do not raise pitch.
2. **Voice.** Piper (VITS, Modern Greek voice `el_GR-joy-medium`, runs on CPU) speaks those phonemes, not Modern Greek spelling. Modern Greek is the closest living phonology to Koine.
   - Durations are deterministic.
   - Word timings are measured by rendering each word-prefix of a phrase.
3. **Prosody.** Praat (PSOLA) shifts the formants to an adult male vocal tract (ratio 0.86) and replaces the model's melody with the pitch targets from `delivery_rules.json`. Loudness follows stress and the rules.
4. **Room.** The engine's room model; synagogue by default.

## Two layers
- **Evidence** (E- rules): accent melody, the stress shift, declination, cadences at commas, stops and questions, the room.
- **Interpretive** (I- rules), switchable off:
  - estimated speaker (Jesus, other speakers, turn pauses);
  - mood from the verse's vocabulary (grief, cry, joy, glory, death), following Quintilian 11.3;
  - emphasis on "amen, amen" and on *egō eimi*.

Every word in a rendered passage's JSON lists its speaker, times, pitch targets, gain and the ids of every rule applied.

## Speaker estimation
- SBLGNT capitalises the first word of direct speech after a speech verb and a raised dot.
- The speaker is a named nominative near the verb. A feminine pronoun or participle selects the nearest named woman.
- Failing that: "they" for a plural verb; the person named in the last verse; or turn-taking in dialogue.
- Speech continues across verses until a narrative verse (3rd-person past indicative, no 1st/2nd person).

Checked by hand on 1:1, 2:3, 2:5, 4:9, 4:11, 4:15–17, 11:21–34, 13:31–15:5, 18:37, 19:28–30 and 20:15–16. Remaining errors are possible where a pronoun is the only subject (for example, 9:25).

## Validation (sample passages)
| Passage | Pitch: planned vs measured r | Median error | Voice median |
|---|---|---|---|
| 1:1–5 | 0.91 | 0.23 st | 107 Hz |
| 11:32–36 | 0.84 | 0.25 st | 95 Hz |
| 15:1–5 | 0.83 | 0.20 st | 100 Hz |
| 19:28–30 | 0.69 | 0.22 st | 95 Hz |

## Limits
- The neural voice was trained on Modern Greek. It cannot produce true aspiration (approximated with h) or pitch-accent contrasts beyond what the imposed melody gives.
- Its speaker is female; the male voice is produced by formant and pitch shifting.
- The interpretive layer is a reading, not evidence.

## Run
```
python3 render_samples.py <sblgnt dir> <voices/el_GR-joy-medium.onnx>
python3 ../../video/render_samples_video.py <sblgnt dir>
```
The voice model comes from huggingface.co/rhasspy/piper-voices (el/el_GR/joy/medium).
