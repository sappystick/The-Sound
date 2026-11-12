# Resonance: a sound engine built on the project's data points

Resonance turns the project's findings into listening sessions you can configure. It plays on studio headphones, bone-conduction headphones or speakers. Every session comes with an **evidence card** stating what each layer rests on. Every rendered file can be **measured back** to confirm it contains what its configuration says.

| Part | File |
|---|---|
| Data points, with sources and evidence levels | `resonance/datapoints.py` → `datapoints.json` |
| Engine (Python, renders WAV) | `resonance/resonance.py` |
| Tests a list of configurations by measuring the audio | `resonance/verify.py` → `verify_report.json` |
| Ten presets across traditions and targets | `resonance/presets.py` → `presets.json` |
| 90-second verified samples (true-stereo MP3) | `resonance/samples/01–10.mp3`, each with its evidence card |
| Real-time web version (Web Audio) | `resonance/app/` (artifact) |

## What goes in: the data points

| Kind | Values | Evidence |
|---|---|---|
| Vowels of ancient languages | Sumerian a e i u · Akkadian a e i u · Middle Egyptian a i u · Coptic a e ɛ i o ɔ u · Tiberian Hebrew i e ɛ a ɔ o u · Galilean Aramaic a e i o u · Koine a e i y o u · Attic (8) · the seven vowels of the magical papyri | Reconstructed (the PGM seven-vowel order is measured, E3/E7) |
| Tunings and ratios | Pythagorean · Babylonian heptatonic (7 rotations; tablets CBS 10996 and UET VII 74) · Archytas' enharmonic and chromatic · Timaeus world-soul partials 1-2-3-4-8-9-27 · harmonic series · just intonation | Reconstructed or symbolic |
| Room resonances | Tabernacle cube, Solomon's debir (**123.4 Hz**, 15 coinciding modes), hekal, King's Chamber, Ħal Saflieni (reported 111 Hz) | Measured from stated dimensions; the Hypogeum value is preliminary |
| Breath paces | 6 a minute (resonance breathing) · John's reconstructed delivery, 3.5–12.7 · Psalm half-verse units | Established or measured |
| Beat bands | Delta, theta, alpha, beta; 40 Hz (auditory steady-state response) | Mixed; the 40 Hz cortical response is established |
| Symbolic structure | 7 (vowels, directions, Ps 29), 10 (Gen 1), 4 (John's parts), 365 | Symbolic |

## How a session is built

1. **Root.** Set in Hz, or taken from a room. The default is the debir's strongest mode in the voice range, 123.4 Hz.
2. **Drone.** A chord from the chosen tuning on that root. It swells on the in-breath and falls on the out-breath.
3. **Voice.** On each out-breath, one vowel from the chosen language is sung at the root and closes on a hum. Humming raises nasal nitric oxide about fifteen-fold, an established finding. The PGM XIII orders follow the vowel square's seven directions.
4. **Breath.** The pace glides from a start rate to an end rate, with an inhale:exhale ratio. A faint air sound marks each in-breath.
5. **Beat.** Choose binaural, monaural, isochronic or none. The beat can glide (for example 10 → 7 → 6 Hz). The carrier is a degree of the drone's scale moved into the device's band, so the beat tone is part of the chord.
6. **Room.** Reverberation is synthesised from the room's computed modes.
7. **Safety.** Average level is −20 dBFS and peaks stay below −1 dBFS. The session fades in and out, and the beat never exceeds 45 Hz.

### Device rules (enforced, with a warning)

| Device | Rule | Why |
|---|---|---|
| Studio headphones | Binaural allowed; carrier 200–900 Hz; a beat above 30 Hz triggers a warning | Binaural beats arise in the brainstem from separate ears. They fade above about 1,000–1,500 Hz carriers and stop sounding like beats above about 30 Hz |
| Bone-conduction headphones | Binaural switched to **monaural**; nothing below 250 Hz; carrier 300–650 Hz | Bone conduction reaches both inner ears almost equally (interaural attenuation about 0–10 dB). Consumer transducers carry little bass |
| Speakers | Binaural switched to **isochronic** | The two channels mix in the air |

## Targets: `design(target, device, language, minutes, room, tuning)`

| Target | Breath | Beat | What the evidence supports |
|---|---|---|---|
| resonance_breathing | 6/min, 4:6 | faint 10 Hz isochronic | **Breath: established** (heart-rate variability) · beat: mixed |
| deep_relaxation | 6 → 5/min | binaural 10 → 7 → 6 Hz | Breath: established · beat: mixed |
| sleep_onset | 6 → 4.5/min, 4:7 | binaural 7 → 4 → 2 Hz | Breath: established · beat: mixed |
| meditation_theta | 6/min | binaural 8 → 6 Hz | Breath: established · beat: mixed |
| focus_gamma40 | none | monaural 40 Hz | **40 Hz cortical response: established** · benefit to focus or memory: preliminary |
| alert_beta | 10/min | isochronic 14 → 18 Hz | Mixed |
| chant_only | 6/min | none | Breath: established |

## Verification: "test a list"

```bash
python3 resonance/verify.py resonance/presets.json 75
```

Each configuration is rendered, and the audio is then measured:
- **Binaural beat.** Subtracting left from right cancels every shared layer and leaves only the two beat tones. Their spacing is read in 8-second windows.
- **Monaural and isochronic beat.** The envelope rate in a band around the carrier, and a check that both ears are identical.
- **Breath.** The pace of the slow loudness swell of the whole mix.
- **Voice.** The pitch against the root, and the share of voice energy that falls on out-breaths.
- **Bone conduction.** A crosstalk simulation, run when the mode is binaural: 68% of the binaural difference remains at 10 dB crosstalk, 44% at 5 dB, 0% at 0 dB.
- **Safety.** Level, peak, fade-in, carrier band, and energy below 200 Hz on bone conduction.

**Result: 10 of 10 presets pass every check.** For example, a binaural glide set to 9.47 → 6.27 Hz measured 9.19 → 6.50 Hz. A sleep glide set to 6.36 → 2.43 Hz measured 6.04 → 2.80 Hz. A 6-per-minute breath measured 5.84–6.06 across presets. The Hypogeum voice was set to 111 Hz and measured 111.1 Hz.

On its first run the verifier caught a real bug: the temple-hall root had fallen to 9.6 Hz. It was fixed before release.

## What is claimed, and what is not

- **Established:** the 40 Hz steady-state response of the auditory cortex; the heart-rate effects of slow breathing near 6 a minute, which the rosary and mantra study of Bernardi et al. (2001) links directly to liturgical recitation; humming and nitric oxide; and the device acoustics above.
- **Mixed:** whether binaural or other beats entrain slower brain rhythms, or change mood, anxiety or attention. Meta-analyses find small and inconsistent effects.
- **Reconstructed or symbolic:** the ancient vowel values, tunings and the meanings of numbers. They shape the sound; they are not claims about the body.
- **Untested here:** any effect on a specific brain area or organ beyond the above. The engine does not measure the listener. The protocols for testing it on people are in `experiments/PROTOCOLS.md`: E1 (heart-rate variability with breath and vowel tracks), E2 (resonance perception) and E5 (blind listening).
  - **Next step:** wire the engine's configurations into those protocols. The same session can then be played against a matched control (identical except for one layer) while heart-rate variability is recorded.

Not a medical device. Listen at moderate volume (about 60–70 dB), take breaks, and do not use it while driving.
