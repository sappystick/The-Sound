#!/usr/bin/env python3
"""Derive the root words of the language by a fixed, auditable rule.

SOUNDS: consonants p t k m n s l w y h, vowels a e i o u (each present in 56-97% of 3,020 inventories in PHOIBLE).
SHAPE: every root is consonant-vowel-consonant-vowel (CVCV), stressed on the first syllable. Grammar words are one
syllable (CV), so a listener (or a parser) knows a word's class from its length.
RULE: each meaning has a few source words that many people already know (from English, Spanish, Mandarin, Hindi,
Arabic, Swahili, Malay/Indonesian, Japanese, Latin, Greek...). A source word is reduced to the sound system (b>p, d>t,
g>k, f>p, v>w, r>l, z>s, ...) and its first C-V-C-V skeleton is taken. The first candidate that differs from every
root already chosen in at least two sounds is accepted; otherwise the candidate with the greatest distance; ties and
clashes are resolved by changing the final vowel. No root may begin with 'no' (reserved for numbers).
Output: lang/lexicon.json (root, meaning, source word, code number) and a distance report.
"""
import itertools, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
C = "ptkmnslwyh"; V = "aeiou"
MAP = {"b": "p", "d": "t", "g": "k", "f": "p", "v": "w", "r": "l", "z": "s", "c": "k", "q": "k", "j": "y", "x": "s"}
def skeleton(src):
    s = src.lower(); s = s.replace("sh", "s").replace("ch", "s").replace("th", "t").replace("ph", "p").replace("ng", "n").replace("kh", "h")
    s = "".join(MAP.get(ch, ch) for ch in s if ch.isalpha()); s = "".join(ch for ch in s if ch in C + V)
    out = ""
    for ch in s:
        want_c = len(out) % 2 == 0
        if want_c and ch in C: out += ch
        elif want_c and ch in V: out += ("h" if not out else "y") + ch      # no consonant available: glide
        elif not want_c and ch in V: out += ch
        elif not want_c and ch == "y": out += "i"                           # y between consonants counts as the vowel i
        # a consonant where a vowel is wanted (cluster) is skipped
        if len(out) == 4: break
    if len(out) == 3: out += out[1]
    if len(out) == 2: out += out
    return out if len(out) == 4 else None
def dist(a, b): return sum(x != y for x, y in zip(a, b))
# meaning : (kind, [source words])   kind is only a hint for learners; every root can serve as thing, action or quality
M = {
 "person": ("thing", ["homo", "person", "ren"]), "mother": ("thing", ["mama"]), "father": ("thing", ["papa"]), "child": ("thing", ["nino", "kodomo", "bala"]),
 "woman": ("thing", ["femina", "nana", "mujer"]), "man": ("thing", ["tato", "man", "viro"]), "friend": ("thing", ["pal", "amigo", "rafiki"]), "name": ("thing", ["nome", "nama"]),
 "body": ("thing", ["korpo", "body"]), "head": ("thing", ["kapa", "kepala"]), "hand": ("thing", ["mano", "hand"]), "foot": ("thing", ["pede", "foot"]),
 "eye": ("thing", ["mata", "oko"]), "ear": ("thing", ["kuping", "oreja"]), "mouth": ("thing", ["boka", "mulut"]), "heart": ("thing", ["hati", "kora"]),
 "water": ("thing", ["wata", "agua", "pani"]), "fire": ("thing", ["paya", "hono", "agni"]), "land": ("thing", ["tera", "land"]), "sky": ("thing", ["sela", "samaa"]),
 "sun": ("thing", ["sola", "surya"]), "moon": ("thing", ["luna"]), "star": ("thing", ["sitara", "stela"]), "day": ("thing", ["dina", "hari"]),
 "night": ("thing", ["noche", "yoru"]), "time": ("thing", ["tempo", "waktu"]), "year": ("thing", ["sana", "ano"]), "place": ("thing", ["loka", "lugar"]),
 "way": ("thing", ["via", "weya", "tao"]), "house": ("thing", ["kasa", "house"]), "door": ("thing", ["porta", "mlango"]), "food": ("thing", ["khana", "komida"]),
 "bread": ("thing", ["pane", "roti"]), "fish": ("thing", ["peska", "sakana"]), "animal": ("thing", ["animal", "hayawan"]), "tree": ("thing", ["miti", "arbol"]),
 "stone": ("thing", ["kivi", "piedra"]), "thing": ("thing", ["kosa", "thing"]), "word": ("thing", ["kata", "logo"]), "life": ("thing", ["vita", "hayat"]),
 "death": ("thing", ["mote", "maut"]), "light": ("thing", ["lumi", "luz"]), "dark": ("quality", ["yami", "oscuro"]), "god": ("thing", ["deva", "teo"]),
 "spirit": ("thing", ["ruha", "pneuma"]), "love": ("action", ["lowe", "suki"]), "joy": ("thing", ["hapi", "gozo"]), "sorrow": ("thing", ["sedih", "tristeza"]),
 "fear": ("thing", ["pavor", "takut"]), "anger": ("thing", ["ira", "hasira"]), "truth": ("thing", ["satya", "vero"]), "world": ("thing", ["dunia", "mundo"]),
 "flesh": ("thing", ["karne", "niku"]), "money": ("thing", ["pesa", "money"]), "law": ("thing", ["lege", "hukum"]), "people": ("thing", ["popo", "watu"]),
 "part": ("thing", ["parte", "sehemu"]), "kind": ("thing", ["tipo", "aina"]), "power": ("thing", ["potens", "nguvu"]), "peace": ("thing", ["salam", "paz"]),
 "good": ("quality", ["wena", "hao"]), "bad": ("quality", ["mala", "buruk"]), "big": ("quality", ["maha", "grande"]), "small": ("quality", ["piko", "kecil"]),
 "many": ("quality", ["multi", "poly"]), "few": ("quality", ["pauci", "sedikit"]), "all": ("quality", ["total", "semua"]), "other": ("quality", ["lain", "otro"]),
 "same": ("quality", ["same", "igual"]), "new": ("quality", ["nueva", "baru"]), "old": ("quality", ["lawo", "viejo"]), "long": ("quality", ["longa", "panjang"]),
 "short": ("quality", ["korta", "pendek"]), "hot": ("quality", ["kalo", "hot"]), "cold": ("quality", ["samui", "frio"]), "strong": ("quality", ["kuat", "forte"]),
 "beautiful": ("quality", ["bela", "kirei"]), "full": ("quality", ["plena", "penuh"]), "true": ("quality", ["real", "vera"]), "holy": ("quality", ["sakra", "kudus"]),
 "exist": ("action", ["yowu", "esta"]), "make": ("action", ["make", "hace"]), "have": ("action", ["tene", "have"]), "go": ("action", ["iku", "yenda", "go"]),
 "come": ("action", ["veni", "come"]), "give": ("action", ["dona", "kasi"]), "take": ("action", ["take", "toma"]), "see": ("action", ["mira", "see"]),
 "hear": ("action", ["suna", "kiku"]), "say": ("action", ["sema", "habla"]), "know": ("action", ["sabe", "jana"]), "think": ("action", ["pensa", "soch"]),
 "want": ("action", ["vole", "mau"]), "eat": ("action", ["kula", "manje"]), "drink": ("action", ["bibe", "nomu"]), "sleep": ("action", ["lala", "dormi"]),
 "work": ("action", ["labor", "kam"]), "help": ("action", ["ayuda", "saidia"]), "begin": ("action", ["komensa", "start"]), "end": ("action", ["fini", "end"]),
 "become": ("action", ["jadi", "naru"]), "send": ("action", ["tuma", "send"]), "find": ("action", ["pata", "find"]), "open": ("action", ["buka", "apri"]),
 "close": ("action", ["tutup", "cierra"]), "stay": ("action", ["mora", "kaa"]), "write": ("action", ["likha", "kaku"]), "read": ("action", ["lee", "soma"]),
 "learn": ("action", ["manabu", "learn"]), "buy": ("action", ["beli", "kau"]), "feel": ("action", ["sente", "rasa"]), "hurt": ("action", ["dolor", "sakit"]),
 "believe": ("action", ["kree", "amin"]), "show": ("action", ["mostra", "show"]), "win": ("action", ["vinse", "win"]), "born": ("action", ["nasce", "lahir"]),
 "move": ("action", ["move", "gerak"]), "wait": ("action", ["espera", "matu"]), "play": ("action", ["pele", "yoki"]), "call": ("action", ["voka", "panggil"]),
 "what": ("question", ["nani", "ke"]), "this": ("pointer", ["ini", "this"]), "that": ("pointer", ["itu", "that"]), "now": ("time", ["sasa", "ahora"]),
 "before": ("time", ["pele", "mae"]), "after": ("time", ["post", "baada"]), "above": ("place", ["supra", "atas"]), "below": ("place", ["bawah", "sub"]),
 "inside": ("place", ["naka", "dalam"]), "outside": ("place", ["luar", "soto"]), "near": ("place", ["dekat", "cerca"]), "far": ("place", ["lejos", "jauh"]),
 "like": ("link", ["kama", "como"]), "very": ("link", ["muy", "sangat"]), "only": ("link", ["hana", "tanha"]), "again": ("link", ["lagi", "otra"]),
 "also": ("link", ["juga", "tambien"]), "maybe": ("link", ["kizas", "mungkin"]), "yes": ("link", ["hai", "yes"]), "thanks": ("link", ["asante", "gracias"]),
 "number": ("thing", ["numero", "hesabu"]), "cause": ("thing", ["kausa", "sebab"]), "book": ("thing", ["kitab", "libro"]), "sign": ("thing", ["signo", "alama"]),
 "voice": ("thing", ["voce", "suara"]), "king": ("thing", ["raja", "rey"]), "wind": ("thing", ["vento", "kaze"]), "color": ("thing", ["kolor", "rangi"]),
}
FIRST = ["water", "good", "exist", "see", "say", "go", "come", "give", "know", "want", "make", "have", "person", "word", "life", "light", "god", "love", "house", "eat", "day", "what", "this", "that", "yes", "peace", "thanks"]
chosen = {}; report = []
for meaning in FIRST + [m for m in M if m not in FIRST]:
    kind, srcs = M[meaning]
    cands = [(skeleton(s), s) for s in srcs]; cands = [(k, s) for k, s in cands if k and not k.startswith("no")]
    best = None
    for k, s in cands:
        for variant in [k] + [k[:3] + v for v in V if v != k[3]] + [k[0] + v + k[2:] for v in V if v != k[1]] + [k[0] + a + k[2] + b for a in V for b in V]:
            if variant in chosen or variant.startswith("no"): continue
            d = min((dist(variant, r) for r in chosen), default=4); score = (d >= 2, variant == k, d)
            if best is None or score > best[0]: best = (score, variant, s)
            if d >= 2 and variant == k: break
        if best and best[0][0] and best[0][1]: break
    if not best[0][0]:                       # last resort: keep the first consonant, vary the rest until two sounds differ from every root
        k, src0 = cands[0]
        alt = [(sum(x == y for x, y in zip(k, w)), w) for w in (k[0] + a + c + b for a in V for c in C for b in V) if w not in chosen and not w.startswith("no") and min(dist(w, r) for r in chosen) >= 2]
        if alt: best = ((True, False, 2), max(alt)[1], src0)
    _, root, src = best; chosen[root] = dict(meaning=meaning, kind=kind, source=src, exact=skeleton(src) == root)
syl = lambda s: C.index(s[0]) * 5 + V.index(s[1])
lex = [dict(root=r, code=syl(r[:2]) * 50 + syl(r[2:]), **d) for r, d in chosen.items()]
pairs = [(a, b) for a, b in itertools.combinations(chosen, 2) if dist(a, b) == 1]
json.dump(dict(consonants=C, vowels=V, roots=lex), open(os.path.join(HERE, "lexicon.json"), "w"), ensure_ascii=False, indent=1)
print(len(lex), "roots;", sum(d["exact"] for d in chosen.values()), "taken unchanged from their source word;", len(pairs), "pairs differ by a single sound:", pairs[:12])
print(" ".join(f"{d['meaning']}={r}" for r, d in chosen.items()))
