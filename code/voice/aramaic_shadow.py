#!/usr/bin/env python3
"""Aramaic shadow: a few sayings from John 1 voiced in Aramaic, as an indication of what stood behind the Greek.

WHAT THIS IS. The consonantal text is the Syriac Peshitta (the Aramaic New Testament of the Syriac churches, 2nd-5th c.).
The vowels and phonetic values below were supplied BY HAND from Classical Syriac grammar (older, eastern vowel values;
spirantised b g d k p t after vowels), because no open vocalised Syriac New Testament was available. It needs checking
by a Syriacist.  Syriac is a later, eastern dialect: the Galilean and Judean Aramaic of about AD 30 differed in vowels,
some forms and vocabulary.  Treat this as an approximation of the sound of the language, not a recovery of the words.
VOICE. Piper Arabic male voice (ar_JO-kareem), chosen because its phoneme set has the Semitic consonants (pharyngeals
h. and `ayin, q, emphatics); it is driven with the IPA below, not with Arabic.  Melody: stress +3 semitones, declination,
final fall (same evidence rules as the Greek voice; no interpretive layer).
Usage: python3 aramaic_shadow.py <ar_JO-kareem-medium.onnx>
"""
import json, os, subprocess, sys
from fractions import Fraction
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import koine_voice as K
E = K.E; OUT = os.path.join(ROOT, "audio_model", "v2"); K.VC["formant_shift_ratio"] = 1.0; K.VC["base_length_scale"] = 1.25
# (ref, speaker, English, Syriac, transliteration, [phrases]); a phrase = (list of words, end punctuation); a word = "syl.ˈsyl" with ˈ on the stressed syllable
SAY = [
 ("1:23", "John (the Baptist)", "I am the voice of one crying in the wilderness: make straight the way of the Lord.", "ܐܢܐ ܩܠܐ ܕܩܪܐ ܒܡܕܒܪܐ ܕܐܫܘܘ ܐܘܪܚܗ ܕܡܪܝܐ",
  "ʾenā qālā d-qārē b-madbrā, d-ʾašwaw ʾurḥeh d-māryā", [(["ʔe.ˈnaː", "ˈqaː.laː", "də.ˈqaː.reː", "bə.mað.bə.ˈraː"], ","), (["dʔaʃ.ˈwaw", "ʔur.ˈħeh", "də.ˈmaːr.jaː"], ".")]),
 ("1:29", "John (the Baptist)", "Behold the Lamb of God, who takes away the sin of the world.", "ܗܐ ܐܡܪܗ ܕܐܠܗܐ ܗܘ ܕܫܩܠ ܚܛܝܬܗ ܕܥܠܡܐ",
  "hā ʾemreh d-ʾalāhā, haw d-šāqel ḥṭīteh d-ʿālmā", [(["ˈhaː", "ʔem.ˈreh", "da.ʔa.ˈlaː.haː"], ","), (["ˈhaw", "də.ˈʃaː.qel", "ħtˤiː.ˈθeh", "də.ˈʕaːl.maː"], ".")]),
 ("1:38", "Jesus", "What are you seeking?", "ܡܢܐ ܒܥܝܢ ܐܢܬܘܢ", "mānā bāʿēn ʾa(n)tōn", [(["ˈmaː.naː", "baː.ˈʕeːn", "ʔat.ˈtoːn"], ";")]),
 ("1:38", "two disciples", "Our master, where are you staying?", "ܪܒܢ ܐܝܟܐ ܗܘܐ ܐܢܬ", "rabban, ʾaykā hāwē ʾa(n)t", [(["rab.ˈban"], ","), (["ʔaj.ˈkaː", "ˈhaː.weː", "ˈʔat"], ";")]),
 ("1:39", "Jesus", "Come and you will see.", "ܬܘ ܘܬܚܙܘܢ", "taw w-teḥzōn", [(["ˈtaw", "wə.teħ.ˈzoːn"], ".")]),
 ("1:41", "Andrew", "We have found the Messiah.", "ܐܫܟܚܢܝܗܝ ܠܡܫܝܚܐ", "ʾeškaḥnāy la-mšīḥā", [(["ʔeʃ.kaħ.ˈnaːj", "lam.ˈʃiː.ħaː"], ".")]),
 ("1:42", "Jesus", "You are Simon son of Jona; you shall be called Kepha.", "ܐܢܬ ܗܘ ܫܡܥܘܢ ܒܪܗ ܕܝܘܢܐ ܐܢܬ ܬܬܩܪܐ ܟܐܦܐ", "ʾa(n)t-hū šemʿōn breh d-yawnā; ʾa(n)t tetqrē kēpā",
  [(["ˈʔat", "huː", "ʃem.ˈʕoːn", "bə.ˈreh", "də.ˈjaw.naː"], ","), (["ˈʔat", "teθ.qə.ˈreː", "ˈkeː.faː"], ".")]),
 ("1:43", "Jesus", "Follow me.", "ܬܐ ܒܬܪܝ", "tā bātar", [(["ˈtaː", "ˈbaː.θar"], ".")]),
]
def word(wstr, punct):
    sy = []
    for s in wstr.split("."):
        st = s.startswith("ˈ"); s = s.lstrip("ˈ"); sy.append(dict(ph=list(s), accent="acute" if st else None, long="ː" in s, nuc=[]))
    return dict(raw=wstr.replace(".", "").replace("ˈ", "") + punct, sylls=sy, spk="narrator", moods=[], rules=[])
voice = K.Voice(sys.argv[1]); ratio = Fraction(E.SR, voice.sr).limit_denominator(1000); meta = []
missing = sorted({c for *_, ph in SAY for ws, _ in ph for w in ws for c in w if c not in ".ˈ" and c not in voice.map})
print("phonemes not in the voice (dropped):", missing)
for n, (ref, spk, eng, syr, tr, phrases) in enumerate(SAY, 1):
    chunks = []
    for ws, punct in phrases:
        grp = [word(w, punct if i == len(ws) - 1 else "") for i, w in enumerate(ws)]
        a, _, _ = K.render_group(voice, grp, delivery=False); chunks += [resample_poly(a, ratio.numerator, ratio.denominator), np.zeros(int(0.45 * E.SR))]
    y = np.concatenate(chunks); y = y / (np.abs(y).max() + 1e-9) * 0.9; y = E.reverb(y, "synagogue")
    name = f"aramaic_{n}_{ref.replace(':', '-')}"; wav = os.path.join(OUT, name + ".wav"); wavfile.write(wav, E.SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", wav[:-4] + ".mp3"], check=True); os.remove(wav)
    meta.append(dict(file=name + ".mp3", ref=ref, speaker=spk, english=eng, syriac=syr, translit=tr, ipa=" | ".join(" ".join(ws) for ws, _ in phrases), dur=round(len(y) / E.SR, 1)))
    print(name, meta[-1]["dur"], "s")
json.dump(dict(_caveat="Peshitta consonants; vowels supplied by hand from Classical Syriac grammar; a later dialect than the Aramaic of AD 30; needs a Syriacist's check.", sayings=meta),
          open(os.path.join(OUT, "aramaic_index.json"), "w"), ensure_ascii=False, indent=1)
