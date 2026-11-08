#!/usr/bin/env python3
"""Render the key words and verses of John 1:1-18 (and their Hebrew/Aramaic/Ge'ez
background words) through the Ancient Sound Engine.  Output: audio/prologue/"""
import json, os
import engine as E

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "prologue")

GREEK_WORDS = [  # (slug, Greek, gloss, verse)
    ("logos", "λόγος", "Word", "1:1"),
    ("en_was", "ἦν", "was (continuous being)", "1:1"),
    ("egeneto", "ἐγένετο", "came to be", "1:3"),
    ("zoe", "ζωή", "life", "1:4"),
    ("phos", "φῶς", "light", "1:4"),
    ("skotia", "σκοτία", "darkness", "1:5"),
    ("katelaben", "κατέλαβεν", "overcame / grasped", "1:5"),
    ("eskenosen", "ἐσκήνωσεν", "tabernacled", "1:14"),
    ("doxa", "δόξα", "glory", "1:14"),
    ("monogenes", "μονογενής", "only-begotten (isopsephy 496)", "1:14, 1:18"),
    ("charitos", "χάριτος", "of grace", "1:14"),
    ("aletheias", "ἀληθείας", "of truth", "1:14"),
    ("kekragen", "κέκραγεν", "has cried out", "1:15"),
    ("exegesato", "ἐξηγήσατο", "made him known", "1:18"),
]
PHRASES = [  # (slug, text, gloss, mode, space, group, era)
    ("v1_house_church", "Ἐν ἀρχῇ ἦν ὁ λόγος καὶ ὁ λόγος ἦν πρὸς τὸν θεόν καὶ θεὸς ἦν ὁ λόγος",
     "1:1 read aloud in a house church", "declaim", "house_church", 1, "koine"),
    ("v1_synagogue_chant", "Ἐν ἀρχῇ ἦν ὁ λόγος καὶ ὁ λόγος ἦν πρὸς τὸν θεόν καὶ θεὸς ἦν ὁ λόγος",
     "1:1 intoned on a reciting tone in a mid-sized hall", "chant", "synagogue", 1, "koine"),
    ("v1_basilica_chant", "Ἐν ἀρχῇ ἦν ὁ λόγος καὶ ὁ λόγος ἦν πρὸς τὸν θεόν καὶ θεὸς ἦν ὁ λόγος",
     "1:1 chanted in a long-echo stone basilica", "chant", "basilica", 1, "koine"),
    ("v1_attic_pitch", "Ἐν ἀρχῇ ἦν ὁ λόγος καὶ ὁ λόγος ἦν πρὸς τὸν θεόν καὶ θεὸς ἦν ὁ λόγος",
     "1:1 in the older pitch-accent pronunciation", "speech", "dry", 1, "attic"),
    ("v12b_center", "ἔδωκεν αὐτοῖς ἐξουσίαν τέκνα θεοῦ γενέσθαι",
     "1:12b, the spoken center: he gave them power to become children of God", "declaim", "house_church", 1, "koine"),
    ("v14a_reader", "καὶ ὁ λόγος σὰρξ ἐγένετο καὶ ἐσκήνωσεν ἐν ἡμῖν",
     "1:14a, the reader: the Word became flesh and tabernacled among us", "declaim", "house_church", 1, "koine"),
    ("v14b_we_group", "καὶ ἐθεασάμεθα τὴν δόξαν αὐτοῦ",
     "1:14b, the group's 'we': and we beheld his glory", "declaim", "house_church", 7, "koine"),
    ("v15_cry", "οὗτος ἦν ὃν εἶπον",
     "1:15, John's cry (raised voice): this was he of whom I said", "declaim", "house_church", 1, "koine"),
]
HEBREW = [  # (slug, Hebrew, gloss, mode, ensemble)
    ("bereshit", "בְּרֵאשִׁית", "in the beginning (Gen 1:1), behind 'En archē'", "chant", "synagogue"),
    ("davar", "דָּבָר", "word", "speech", "none"),
    ("or", "אוֹר", "light", "speech", "none"),
    ("choshekh", "חֹשֶׁךְ", "darkness", "speech", "none"),
    ("mishkan", "מִשְׁכָּן", "tabernacle (s-k-n echo of eskēnōsen)", "chant", "synagogue"),
    ("shekhinah", "שְׁכִינָה", "dwelling presence (s-k-n)", "chant", "synagogue"),
    ("chesed_emet", "חֶסֶד וֶאֱמֶת", "steadfast love and truth (Ex 34:6), behind 'grace and truth'", "chant", "synagogue"),
    ("chesed_emet_temple", "חֶסֶד וֶאֱמֶת", "the same, in Temple-service style", "ritual", "temple"),
]
OTHER = [  # (slug, IPA tokens, gloss, mode, space)
    ("memra_aramaic", "m eː m ˈr aː", "Memra, the Targums' 'Word' (Aramaic)", "chant", "synagogue"),
    ("qal_geez", "q ˈaː l", "qāl, Ge'ez for Logos: both 'word' and 'voice'", "chant", "synagogue"),
]


def go():
    idx = []
    for slug, gk, gloss, v in GREEK_WORDS:
        for tag, era, mode, ens, space in (("koine_speech", "koine", "speech", "none", "dry"),
                                           ("attic_pitch", "attic", "speech", "none", "dry"),
                                           ("koine_chant_house", "koine", "chant", "none", "house_church"),
                                           ("phonaulos", "koine", "chant", "phonaulos", "house_church")):
            path = os.path.join(OUT, "words", f"{slug}_{tag}.wav")
            m = E.make(gk, "greek", era, mode, ens, path, space=space, voice=(ens != "phonaulos"))
            idx.append(dict(kind="greek word", text=gk, gloss=gloss, verse=v, variant=tag, ipa=m["ipa"],
                            file=os.path.relpath(path, OUT)))
            print(f"{gk:12s} {tag:18s} {m['ipa']}")
    for slug, txt, gloss, mode, space, group, era in PHRASES:
        path = os.path.join(OUT, "verses", f"{slug}.wav")
        m = E.make(txt, "greek", era, mode, "none", path, space=space, group=group,
                   base_f0=150.0 if slug == "v15_cry" else 118.0)
        idx.append(dict(kind="greek verse", text=txt, gloss=gloss, variant=slug, ipa=m["ipa"],
                        file=os.path.relpath(path, OUT)))
        print(f"{slug:22s} {m['ipa']}")
    for slug, hb, gloss, mode, ens in HEBREW:
        path = os.path.join(OUT, "hebrew", f"{slug}.wav")
        m = E.make(hb, "hebrew", "second-temple", mode, ens, path)
        idx.append(dict(kind="hebrew", text=hb, gloss=gloss, variant=f"{mode}/{ens}", ipa=m["ipa"],
                        file=os.path.relpath(path, OUT)))
        print(f"{slug:22s} {m['ipa']}")
    for slug, ph, gloss, mode, space in OTHER:
        path = os.path.join(OUT, "other", f"{slug}.wav")
        m = E.make(ph, "hebrew", "second-temple", mode, "none", path, space=space, phonemes=True)
        idx.append(dict(kind="aramaic/ge'ez", text=ph, gloss=gloss, variant=mode, ipa=m["ipa"],
                        file=os.path.relpath(path, OUT)))
        print(f"{slug:22s} {m['ipa']}")
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)
    print(len(idx), "files")


if __name__ == "__main__":
    go()
