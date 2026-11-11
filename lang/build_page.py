#!/usr/bin/env python3
"""Assemble lang/page/index.html: the Sala language page (sounds, script, words, grammar, machine playground, texts)."""
import json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sala as S, voice as VO
lex = json.load(open(os.path.join(HERE, "lexicon.json"), encoding="utf-8")); samples = json.load(open(os.path.join(HERE, "samples.json"), encoding="utf-8"))
mel = json.load(open(os.path.join(HERE, "melody_check.json"))); stats = json.load(open(os.path.join(HERE, "course_stats.json")))
for k in mel: shutil.copy(os.path.join(HERE, "audio", f"melody_{k}.mp3"), os.path.join(HERE, "page", "audio", f"melody_{k}.mp3"))
PHO = {"m": 97, "i": 92, "k": 90, "y": 90, "u": 88, "p": 86, "a": 86, "w": 82, "n": 78, "t": 68, "l": 68, "s": 67, "e": 61, "o": 60, "h": 56}
GRAMMAR = [["mi · yu · si", "I · you · he, she, it (add lu for we, you all, they)", "pron"], ["sa", "the action or description follows", "core"], ["ke", "what is acted on", "role"], ["pe", "to, for", "role"],
           ["na", "in, at, on (place or time)", "role"], ["wi", "with, by means of", "role"], ["ho", "from, because of", "role"], ["le", "of: the word before belongs to what follows", "core"],
           ["mo", "not", "core"], ["lu", "more than one", "core"], ["ta · ya", "before now · after now", "time"], ["so · mu", "can · must", "time"], ["ye · yo · pa", "and · or · but", "link"], ["ku … te", "if … then", "link"],
           ["ti … tu", "which … (a clause describing the word before)", "core"], ["ha", "a name follows", "core"], ["no…", "a number: no + one syllable per digit", "core"], ["ka · pu · hi · he · wa", "question · request · joy · sorrow · warning (sentence-final; each has its own melody)", "stance"]]
RULES = ["Every root is two syllables; every grammar word is one. You hear a word's class from its length.", "Words never change shape. No endings, no genders, no irregular forms.", "A sentence is: who or what, then sa, then the action or description.",
         "Each further part of the sentence is introduced by its own word: ke, pe, na, wi, ho. They can come in any order.", "A describing word follows the word it describes: kasa mahi, a big house.",
         "Any root can be a thing, an action or a quality, by its place in the sentence.", "Time is optional: ta for the past, ya for the future, nothing for now or always.", "mo before a word means not.",
         "The feeling of a sentence is said, not guessed: a final word and its melody mark question, request, joy, sorrow or warning.", "Every sentence has exactly one structure, so a person and a program read it the same way."]
GEST = dict(cons=[["p", "closed fist"], ["t", "flat hand, fingers together"], ["k", "hooked index finger"], ["m", "fingertips pinched together"], ["n", "two fingers together"], ["s", "open hand, fingers spread"],
                  ["l", "thumb and index out (L)"], ["w", "three fingers up (W)"], ["y", "thumb and little finger out (Y)"], ["h", "cupped hand (C)"]],
            vow=[["a", "at the chest"], ["e", "at the chin"], ["i", "at the forehead"], ["o", "at the shoulder"], ["u", "at the waist"]])
D = dict(C=S.C, V=S.V, roots=lex["roots"], pron=S.PRON, role={k: v[0] for k, v in S.ROLEW.items()}, tense={k: v[0] for k, v in S.TENSE.items()}, link=S.LINKW, stance={k: v[0] for k, v in S.STANCE.items()},
         grammar=GRAMMAR, rules=RULES, samples=samples, melody={k: dict(v, **{x: VO.MELODY[None if k == "plain" else k][x] for x in ("base", "rng", "rate", "gain", "final")}) for k, v in mel.items()},
         pho=PHO, gest=GEST, stats=stats, exact=sum(r["exact"] for r in lex["roots"]))
tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
open(os.path.join(HERE, "page", "index.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(D, ensure_ascii=False, separators=(",", ":"))))
print("page built", round(os.path.getsize(os.path.join(HERE, "page", "index.html")) / 1e3), "KB")
