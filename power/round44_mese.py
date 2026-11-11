#!/usr/bin/env python3
"""Round 44. The 'I am' on the middle string: syllable measurements, the second (technical) reading of John's words,
and the combined instrument (seven strings + speaking tubes, mese tuned to EGO EIMI).

A. Syllable position of 'I am'. For every ego eimi in John (SBLGNT), its syllable position within its verse
   (0 = start, 1 = end). Null: the positions of all other words in the same verses (and of eimi without ego).
   Is ego eimi central (|pos - 0.5| small) more than chance?
B. 'In the middle' (mesos) in the Gospels: John's Jesus 'stands in the middle' (1:26, 19:18, 20:19, 20:26).
   Counts per 10,000 words against the Synoptics, and who is in the middle.
C. The second, technical reading. John's key words that are also technical terms of Greek harmonics
   (attested senses: logos = ratio, Euclid Elements V def. 3, Sectio Canonis; arche = first principle;
   phone = sound, pitch; pneuma = breath; mesos/mese = the central string; ho on = 'the one who is').
   Rates in John vs the Synoptics; the prologue rendered in the technical senses (labelled as a reading).
D. The combined instrument: a seven-string lyre whose soundbox opens into switchable vowel tubes (the round-42
   resonators) - Clement's lyre + aulos + temple in one body. The mese is tuned so that EGO EIMI resolves on it.
   Syllable-by-syllable it plays: string = Nicomachus vowel-string of the syllable, tube = that vowel, length =
   syllable quantity. Render: EGO EIMI, then John 1:1a.
Usage: python3 power/round44_mese.py [--no-audio]
"""
import glob, json, math, os, re, subprocess, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code", "engine")); import engine as E
from scipy.signal import lfilter
from scipy.io import wavfile
rng = np.random.default_rng(44); SR = E.SR; out = {}
def bare(t):
    t = unicodedata.normalize("NFD", t.lower()); return "".join(c for c in t if not unicodedata.combining(c)).replace("ς", "σ")
def load(code):
    V = {}
    for l in open(glob.glob(os.path.join(ROOT, f"sources/texts/sblgnt/*-{code}-morphgnt.txt"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault(p[0], []).append(dict(raw=p[3], w=re.sub(r"[^α-ω]", "", bare(p[3])), lem=bare(p[6]), pos=p[1], parse=p[2]))
    return V
G = {c: load(c) for c in ("Mt", "Mk", "Lk", "Jn")}
def nsyl(w): return max(1, len(E.parse_greek(w, "koine")[0])) if w else 0
SYL = {}
def syl(w):
    if w not in SYL: SYL[w] = nsyl(w)
    return SYL[w]

# ---------------------------------------------------------------- A
pos_ego, pos_other, pos_eimi_alone = [], [], []
for ref, ws in G["Jn"].items():
    s = [syl(x["raw"]) for x in ws]; tot = sum(s); cum = np.cumsum([0] + s)
    for i, x in enumerate(ws):
        mid = (cum[i] + s[i] / 2) / tot
        if x["w"] == "εγω" and i + 1 < len(ws) and ws[i + 1]["w"] == "ειμι": pos_ego.append((ref, float(mid)))
        elif x["w"] == "ειμι" and not (i > 0 and ws[i - 1]["w"] == "εγω"): pos_eimi_alone.append(float(mid))
        else: pos_other.append(float(mid))
pe = np.array([p for _, p in pos_ego]); po = np.array(pos_other)
obs = float(np.mean(np.abs(pe - 0.5))); null = np.array([np.mean(np.abs(rng.choice(po, len(pe)) - 0.5)) for _ in range(20000)])
out["A_ego_eimi_position"] = dict(n=len(pe), mean_distance_from_centre=round(obs, 3), null_mean=round(float(null.mean()), 3),
    p_central=round(float((null <= obs).mean()), 4), p_peripheral=round(float((null >= obs).mean()), 4),
    in_first_quarter=int((pe < 0.25).sum()), in_middle_half=int(((pe >= 0.25) & (pe <= 0.75)).sum()), in_last_quarter=int((pe > 0.75).sum()),
    positions=[(r, round(p, 2)) for r, p in pos_ego])

# ---------------------------------------------------------------- B
res_B = {}
for c, V in G.items():
    n = sum(len(v) for v in V.values()); hits = [(r, " ".join(x["raw"] for x in v)) for r, v in V.items() for x in v if x["lem"] == "μεσοσ"]
    res_B[c] = dict(mesos=len(hits), per_10k=round(1e4 * len(hits) / n, 2), refs=[f"{int(r[2:4])}:{int(r[4:6])}" for r, _ in hits])
JESUS_MIDDLE = {  # hand labels: is Jesus (or 'the one coming', 1:26) the one in the middle? (post hoc, labelled)
 "Mt": {"18:20"}, "Mk": set(), "Lk": {"2:46", "4:30", "22:27", "24:36"}, "Jn": {"1:26", "19:18", "20:19", "20:26"}}
syn_yes = sum(len(JESUS_MIDDLE[c]) for c in ("Mt", "Mk", "Lk")); syn_n = sum(res_B[c]["mesos"] for c in ("Mt", "Mk", "Lk"))
jn_yes, jn_n = len(JESUS_MIDDLE["Jn"]), res_B["Jn"]["mesos"]
tot, yes = syn_n + jn_n, syn_yes + jn_yes
p_f = sum(math.comb(yes, k) * math.comb(tot - yes, jn_n - k) for k in range(jn_yes, min(yes, jn_n) + 1)) / math.comb(tot, jn_n)
res_B["jesus_in_the_middle"] = dict(John=f"{jn_yes}/{jn_n}", Synoptics=f"{syn_yes}/{syn_n}", fisher_p_one_sided=round(p_f, 4), labels=JESUS_MIDDLE,
                                    note="post hoc: the pattern was noticed in the output, then tested")
out["B_in_the_middle"] = res_B

# ---------------------------------------------------------------- C
TECH = {  # lemma: (everyday sense, technical sense in harmonics/philosophy, attestation)
 "λογοσ": ("word, account", "ratio, proportion", "Euclid, Elements V def. 3; Sectio Canonis; Plato, Timaeus 31c-32c"),
 "αρχη": ("beginning", "first principle, source", "Aristotle, Metaphysics 5.1"),
 "φωνη": ("voice", "sound, pitched sound", "Aristoxenus, Elements of Harmonics 1.3; Plato, Timaeus 67b"),
 "πνευμα": ("spirit", "breath, wind (the aulos' air)", "Clement, Protrepticus 1.5; Aristotle, On the Soul 2.8"),
 "μεσοσ": ("middle", "the mese, the central and governing string", "[Aristotle], Problems 19.20; Nicomachus, Manual 3"),
 "φωσ": ("light", "light", "-"),
 "ζωη": ("life", "life", "-"),
 "δοξα": ("glory", "opinion, appearance (no harmonic sense)", "-"),
 "αληθεια": ("truth", "truth", "-"),
 "μαρτυρια": ("testimony", "testimony", "-"),
}
res_C = {}
for lem in TECH:
    res_C[lem] = {c: round(1e4 * sum(x["lem"] == lem for v in V.values() for x in v) / sum(len(v) for v in V.values()), 1) for c, V in G.items()}
out["C_technical_words_per_10k"] = dict(rates=res_C, senses=TECH,
    second_reading_John_1_1_5="In the first principle was the Ratio, and the Ratio was toward God, and God was the Ratio. "
        "This was in the first principle toward God. All things came to be through it, and apart from it not one thing came to be. "
        "What came to be in it was life, and the life was the light of men; and the light sounds in the darkness, and the darkness did not seize it.",
    note="READING. Each technical sense is attested in Greek usage of the period (column 'attestation'); this is a second register heard by an educated Alexandrian reader, as Clement hears it, not a correction of the standard translation. 'Sounds' for phainei is NOT attested (phainei = shines); it is shown in brackets in the write-up as an example of what a mistranslation would look like.")

# ---------------------------------------------------------------- D
R41 = json.load(open(os.path.join(HERE, "round41_results.json")))["instrument"]["heptachord_lyre"]
R42 = json.load(open(os.path.join(HERE, "round42_results.json")))["A_speaking_machine"]["vowels"]
STR = {s["vowel"]: s for s in R41}  # Greek vowel letter -> string
IPA2GK = {"a": "α", "ɛ": "ε", "e": "η", "i": "ι", "o": "ο", "y": "υ", "ɔ": "ω", "u": "ο"}
def resonate(x, freqs, bws=(80, 100, 140)):
    y = np.zeros_like(x)
    for f, b in zip(freqs, bws): bb, aa = E.resonator_coeffs(f, b); y += lfilter(bb, aa, x)
    return y
def pluck(f0, n):
    t = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 30):
        if k * f0 > 8000: break
        y += np.sin(2 * np.pi * k * f0 * t) * abs(math.sin(k * math.pi * 0.2)) / k * np.exp(-t * (1.2 + 0.5 * k))
    return y
def play(text, beat=0.42):
    words = E.parse_greek(text, "koine"); seq = []; y = []
    for w in words:
        for s in w:
            v = s["nuc"][0].rstrip("ː"); g = IPA2GK.get(v, "α"); st = STR[g]
            L = beat * (2 if s.get("long") or s["nuc"][0].endswith("ː") else 1); n = int(L * SR)
            tone = pluck(st["Hz"], n); spoken = resonate(tone, R42[v]["machine"] if v in R42 else R42["a"]["machine"])
            y.append(0.45 * tone / (np.abs(tone).max() + 1e-9) + 0.55 * spoken / (np.abs(spoken).max() + 1e-9))
            seq.append(dict(syllable="".join(s["ph"]), vowel=g, string=st["string"], planet=st["planet"], Hz=st["Hz"], beats=L / beat))
        y.append(np.zeros(int(0.12 * SR)))
    return np.concatenate(y), seq
y1, s1 = play("ἐγώ εἰμι"); y2, s2 = play("Ἐν ἀρχῇ ἦν ὁ λόγος")
out["D_instrument"] = dict(
    design="seven gut strings (round 41 lengths, mese 220 Hz = A3) over a soundbox whose mouth opens into one of seven vowel tubes "
           "(round 42 three-section resonators) chosen by a lever, or a tube held in the player's mouth (a talk-box). Strings = Clement's lyre; tube = aulos; soundbox and room = temple.",
    ego_eimi=s1, john_1_1a=s2,
    resolves_on_mese=s1[-1]["string"] == "mese",
    note="With Koine pronunciation ει = i, so EGO EIMI is e-ɣo-i-mi: Mercury - Mars - Sun - Sun, ending on the mese twice. "
         "The mese is the Sun string in Nicomachus by the source, not by our tuning choice.")
rend = []
if "--no-audio" not in sys.argv:
    for name, y in (("ego_eimi", y1), ("john_1_1a", y2)):
        y = E.reverb(y / (np.abs(y).max() + 1e-9), "holy_of_holies")
        wav = os.path.join(HERE, "audio", f"r44_lyre_tubes_{name}.wav"); wavfile.write(wav, SR, (E.norm(y) * 32767).astype(np.int16))
        mp3 = wav[:-4] + ".mp3"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True); os.remove(wav); rend.append(os.path.relpath(mp3, ROOT))
out["renders"] = rend
out["E_hymn_papyri_and_ekphonetic"] = dict(
    p_oxy_1786=dict(sacred_names="written in full in the editors' transcription: θεοῦ (l. 1), πατέρα, υἱόν, ἅγιον πνεῦμα (l. 4); no overlined contraction reported",
                    opening="lost; preserved part calls on creation (stars, rivers, all the powers) to sing", notation="vocal notes above every line"),
    p_amh_2=dict(date="4th c. (Grenfell & Hunt 1900)", form="alphabetic acrostic, 25 lines, three cola per line marked by double dots",
                 metre="accentual: every colon ends on an accented penultimate (the 'tonic principle already on the path of victory')",
                 subject="baptism and life ('washed in the Jordan', 'that thou mayst receive life'); opening mutilated", notation="none"),
    berlin_bkt_vi_6_8="not openly available here",
    ekphonetic="no open digital corpus found (Hoeg 1935, Engberg, Wellesz 1966 are in copyright / borrow-only); test designed, not run")
json.dump(out, open(os.path.join(HERE, "round44_results.json"), "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print({k: v for k, v in out["A_ego_eimi_position"].items() if k != "positions"}); print(out["A_ego_eimi_position"]["positions"])
print(res_B); print(res_C); print(s1); print(s2); print(rend)
