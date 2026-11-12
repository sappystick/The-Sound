#!/usr/bin/env python3
"""KANON v0.2: a programming language that is spoken, typed, played and drawn. Reference implementation.

One lattice, five readings of every program:
  TEXT     ASCII glyphs              sa #7 gia ta #3 | di
  SPEECH   syllables (sa, gi-a ...)  the audio codec: speaking IS compiling (exact round trip, checksummed)
  MUSIC    just-intonation tones     vowels are the seven planet-strings; consonants are two-tone chords on the 4x3 grid
  PROCESS  a deterministic VM        seven list-valued planes; ring-order verses; names, guards, while-loops
  FIGURE   a geometric seal          every word draws a path on the heptagon; every verse draws its ring of pairs

v0.2 (round 66) over v0.1 (round 65):
  * Three orders, three meanings. Syllable order inside a word = composition (a pipeline);
    word order inside a verse = the ring (outer pairs first, centre last); verse order = sequence.
    v0.1 ignored every syllable after the first, so its namespace figure counted words that behaved identically.
  * Names (::name ... ::  defines, :name calls), guards (word? runs only while the accumulator is positive),
    while-loops (l with no number repeats while its own plane is positive), increments (g #n), modulo (m #n).
    With these the language is Turing complete: planes act as the registers of a counter machine.
  * The Canon: a built-in library of named words organised on the 12 x 7 grid (number, statistics, geometry,
    sequences, logic, music, letters, time, seals) plus a prelude written in KANON itself. No imports, ever.
  * Every mark is now spoken (! ~ ? : =), so the audio form carries the whole program. Verse checksums
    (=xyxy, a weighted sum mod 7039) catch every single-symbol error and every swap of neighbours.
  * Seals: an SVG figure per program; equal programs draw equal seals, and a changed glyph changes the seal.
  * Loops bind to their body before ring ordering, so a loop is never split across the ring.
Usage: python3 kanon.py selftest | run FILE | speak FILE OUT.wav | decode IN.wav | seal FILE OUT.svg | chart OUT.svg
       | ring "a b c d" (write a linear sequence in ring order) | repl
"""
import json, math, os, re, sys, wave, warnings
import numpy as np
warnings.filterwarnings("ignore", category=RuntimeWarning)

FS = 22050
F0 = 154.2                     # default carrier: the ark note (round 56); every frequency is a ratio of f0
VOWELS = "aeyiouw"             # alpha epsilon eta iota omicron upsilon omega
RATIO = {"a": 4/3, "e": 32/27, "y": 256/243, "i": 1.0, "o": 8/9, "u": 64/81, "w": 0.75}
PLANET = {"a": "Moon", "e": "Mercury", "y": "Venus", "i": "Sun", "o": "Mars", "u": "Jupiter", "w": "Saturn"}
WEEKDAY = {"i": "Sunday", "a": "Monday", "o": "Tuesday", "e": "Wednesday", "u": "Thursday", "y": "Friday", "w": "Saturday"}
CONS = "ktpbdglmnrsh"          # the 4 x 3 grid: rows = seasons, columns = months (the calendar palace)
MONTH = dict(zip(CONS, ["Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul", "Tishri", "Cheshvan", "Kislev", "Tevet", "Shevat", "Adar"]))
ROWMUL = [9.0, 11.0, 13.0, 15.0]; COLMUL = [17.0, 20.0, 23.0]; MARKMUL = 6.0
MARKS = {"!": 25.0, "~": 27.0, "?": 29.0, ":": 31.0, "=": 33.0}   # each mark is a lone high tone (x f0)
DIGITS = "0123456789te"
OPNAME = {"k": "keep", "t": "test", "p": "project", "b": "bind", "d": "door", "g": "gather",
          "l": "loop", "m": "morph", "n": "negate", "r": "retro", "s": "stream", "h": "hold"}
PLANE_ROLE = {"i": "accumulator (the mese)", "a": "input / second argument", "e": "scratch", "y": "pair register",
              "o": "output stage", "u": "deep store / counter", "w": "archive (the silent string)"}
FUEL = 200000
MAXLEN = 65536                 # no plane may hold more values than this (a guard against runaway growth)

# ================================================================ lexing and parsing
TOKEN = re.compile(r"\s*(\|)|\s*(=[a-z]+)|\s*(::?)([a-z]*)([!?]*)|\s*(~?)([a-z]+)([!?]*)|\s*(#[0-9te]+)")
def is_word(w):
    if len(w) < 2: return False
    body = w[: len(w) // 2 * 2]
    return all((c in CONS) if j % 2 == 0 else (c in VOWELS) for j, c in enumerate(body)) and (len(w) % 2 == 0 or w[-1] in VOWELS)

def lex(src):
    """-> flat token list: ('word', w, flags), ('num', v), ('call', name, flags), ('def', name), ('end',), ('bar',), ('sum', s)."""
    out, pos, src = [], 0, src.replace("\n", " ")
    while pos < len(src):
        if src[pos:].strip() == "": break
        m = TOKEN.match(src, pos)
        if not m or m.end() == pos: raise SyntaxError(f"cannot read {src[pos:pos+12]!r}")
        pos = m.end()
        if m.group(1): out.append(("bar",))
        elif m.group(2): out.append(("sum", m.group(2)[1:]))
        elif m.group(3):
            colons, name, fl = m.group(3), m.group(4), m.group(5)
            if colons == "::": out.append(("def", name) if name else ("end",))
            else:
                if not is_word(name): raise SyntaxError(f"bad name {name!r}")
                out.append(("call", name, dict(urgent="!" in fl, guard="?" in fl, sandbox=False)))
        elif m.group(7):
            w = m.group(7)
            if not is_word(w): raise SyntaxError(f"bad word {w!r}: syllables are consonant+vowel, with an optional final vowel")
            out.append(("word", w, dict(urgent="!" in m.group(8), guard="?" in m.group(8), sandbox=m.group(6) == "~")))
        else:
            v = 0
            for ch in m.group(9)[1:]: v = v * 12 + DIGITS.index(ch)
            out.append(("num", float(v)))
    return out

def parse(src):
    """-> (main: list of verses, defs: {name: list of verses}). A verse is a list of items."""
    main, defs, cur_def, verse, sums = [], {}, None, [], []
    def close():
        nonlocal verse
        if verse: (defs[cur_def] if cur_def else main).append(verse)
        verse = []
    for t in lex(src):
        if t[0] == "bar": close()
        elif t[0] == "def": close(); cur_def = t[1]; defs[cur_def] = []
        elif t[0] == "end": close(); cur_def = None
        elif t[0] == "num":
            if verse: verse[-1]["num"] = t[1]
            else: verse.append(dict(kind="word", word="ki", num=t[1], urgent=False, guard=False, sandbox=False))
        elif t[0] == "sum": sums.append(t[1])
        else: verse.append(dict(kind=t[0], word=t[1], num=None, **t[2]))
    close()
    return main, defs

# ================================================================ scheduling: the ring
def bind_loops(items):
    """A loop word and its body become one unit before ring ordering."""
    out, i = [], 0
    while i < len(items):
        it = items[i]
        if it["kind"] == "word" and it["word"][0] == "l" and i + 1 < len(items):
            out.append(dict(it, body=items[i + 1])); i += 2
        else: out.append(it); i += 1
    return out

def schedule(items):
    """Urgent words first, then outer pairs inward; the centre commits last (rounds 52-54)."""
    out, rest = [], []
    for it in items: (out if it["urgent"] else rest).append(it)
    n = len(rest)
    for k in range(n // 2): out += [rest[k], rest[n - 1 - k]]
    if n % 2: out.append(rest[n // 2])
    return out

def ring(seq):
    """Spell a linear sequence so that ring order executes it as written: a b c d e -> a c e d b."""
    n = len(seq); pos = [None] * n; order = []
    for k in range(n // 2): order += [k, n - 1 - k]
    if n % 2: order.append(n // 2)
    for j, slot in enumerate(order): pos[slot] = seq[j]
    return pos

# ================================================================ the machine
def fold(x):
    x = abs(float(x)) or 1.0
    while x >= 2.5: x /= 2
    while x < 0.625: x *= 2
    return x

def truthy(p): return bool(p) and p[-1] > 0
def toint(x): return int(round(x, 9))     # counts are taken after rounding away float noise, identically in kanon.js

class VM:
    def __init__(self, f0=F0, trace=False):
        self.P = {v: [] for v in VOWELS}; self.events = []; self.log = []; self.out = []
        self.defs = {}; self.fuel = FUEL; self.trace = trace; self.f0 = f0; self.steps = []
        load_prelude(self)
    def run(self, src):
        main, defs = parse(src); self.defs.update(defs)
        for verse in main: self.verse(verse)
        return self
    def verse(self, items):
        for it in schedule(bind_loops(items)): self.item(it)
    def tick(self):
        self.fuel -= 1
        if self.fuel < 0: raise RuntimeError("out of fuel (a loop that never ends?)")
    def item(self, it):
        self.tick()
        if it["guard"] and not truthy(self.P["i"]): self.steps.append(("skip", it["word"])); return
        try:
            if it["kind"] == "call": self.call(it["word"], it["num"])
            elif "body" in it: self.loop(it)
            else: self.word(it["word"], it["num"])
        except Exception as e:
            if it["sandbox"]: self.log.append(f"~{it['word']}: skipped ({e})")
            else: raise
    def loop(self, it):
        w, val, body = it["word"], it["num"], it["body"]; plane = w[1]
        if val is not None:
            for _ in range(toint(val)): self.item(body)
        else:
            while truthy(self.P[plane]): self.item(body)
    def call(self, name, val):
        self.steps.append(("call", name))
        if name in self.defs:
            for v in self.defs[name]: self.verse(v)
        elif name in CANON: CANON[name][1](self, val)
        else: raise NameError(f"unknown name :{name}")
    # ---- one word: a chain of syllables applied to the head plane
    def word(self, w, val):
        syl = [w[j:j + 2] for j in range(0, len(w) - len(w) % 2, 2)]; cad = w[-1] if len(w) % 2 else None
        op, head = syl[0][0], syl[0][1]
        if op == "d" and len(syl) >= 2:          # d-words are songs: the word's own vowel line is the melody
            self.events.append(("melody", [RATIO[c] for c in w if c in VOWELS])); self.steps.append((w, "song")); return
        self.op(op, head, cad, val, explicit=cad is not None)
        for s in syl[1:]: self.tick(); self.op(s[0], head, s[1], None, explicit=True)
        self.steps.append((w, val)); self.log.append(f"{w}{'' if val is None else ' #' + str(int(val))} -> {head}={[round(x, 4) for x in self.P[head]][:8]}")
    def op(self, op, head, src, val, explicit):
        P = self.P; H = P[head]; S = P[src] if src else H
        if op == "s":
            n = toint(val) if val is not None else (toint(S[-1]) if explicit and S else 7)
            if n > MAXLEN: raise OverflowError(f"stream of {n} values exceeds {MAXLEN}")
            P[head] = [float(k) for k in range(1, n + 1)]
        elif op == "k": P[head] = [float(val)] if val is not None else (list(S) if explicit else [])
        elif op == "b": P[head] = H + list(S)
        elif op == "p": P[head] = [x * (val if val is not None else RATIO[src or "i"]) for x in H]
        elif op == "g": P[head] = [float(sum(S)) + (val or 0.0)]
        elif op == "t":
            thr = val if val is not None else (S[-1] if explicit and src != head and S else (sum(H) / len(H) if H else 0.0))
            P[head] = [x for x in H if x > thr]
        elif op == "n":
            if val is not None: P[head] = [x - val for x in H]
            elif explicit and src != head: d = S[-1] if S else 0.0; P[head] = [x - d for x in H]
            else: P[head] = [-x for x in H]
        elif op == "r":
            if val is not None and H: k = toint(val) % len(H); P[head] = H[k:] + H[:k]
            else: P[head] = H[::-1]
        elif op == "m":
            if val is not None: P[head] = [math.fmod(x, val) if val else x for x in H]
            elif explicit and src != head and S and S[-1]: P[head] = [math.fmod(x, S[-1]) for x in H]
            else:
                tgt, n = RATIO[src or "i"], max(1, len(H)); P[head] = [x * tgt ** ((j + 1) / n) for j, x in enumerate(H)]
        elif op == "d":
            self.events.append(("melody", [fold(x) for x in H])); self.out.append([round(x, 6) for x in H])
        elif op == "h":
            if explicit: P[head] = [float(len(S))]
            else: self.events.append(("rest", (val or 2) * 0.1))
        elif op == "l": pass
        if len(P[head]) > MAXLEN: raise OverflowError(f"plane {head} would hold {len(P[head])} values (limit {MAXLEN})")
        if not all(math.isfinite(x) for x in P[head]): raise ArithmeticError("not a finite number")

# ================================================================ the Canon: built-in names on the 12 x 7 grid
def _i(vm): return vm.P["i"]
def _a(vm): return vm.P["a"]
def _set(vm, xs):
    xs = list(xs)
    if len(xs) > MAXLEN: raise OverflowError(f"result of {len(xs)} values exceeds {MAXLEN}")
    xs = [float(x) for x in xs]
    if not all(math.isfinite(x) for x in xs): raise ArithmeticError("not a finite number (division by zero or an empty input)")
    vm.P["i"] = xs
def _primes(n):
    n = int(n)
    if n > 10 ** 6: raise OverflowError("primes are listed up to 1,000,000")
    s = [True] * (n + 1); s[:2] = [False, False][: n + 1]
    for p in range(2, int(n ** 0.5) + 1):
        if s[p]: s[p * p::p] = [False] * len(s[p * p::p])
    return [k for k, v in enumerate(s) if v]
GREEKNUM = [(900, "ϡ"), (800, "ω"), (700, "ψ"), (600, "χ"), (500, "φ"), (400, "υ"), (300, "τ"), (200, "σ"), (100, "ρ"), (90, "ϙ"), (80, "π"), (70, "ο"), (60, "ξ"), (50, "ν"), (40, "μ"), (30, "λ"), (20, "κ"), (10, "ι"), (9, "θ"), (8, "η"), (7, "ζ"), (6, "ϛ"), (5, "ε"), (4, "δ"), (3, "γ"), (2, "β"), (1, "α")]
HEBNUM = [(400, "ת"), (300, "ש"), (200, "ר"), (100, "ק"), (90, "צ"), (80, "פ"), (70, "ע"), (60, "ס"), (50, "נ"), (40, "מ"), (30, "ל"), (20, "כ"), (10, "י"), (9, "ט"), (8, "ח"), (7, "ז"), (6, "ו"), (5, "ה"), (4, "ד"), (3, "ג"), (2, "ב"), (1, "א")]
def _numeral(n, table):
    n, s = int(n), ""
    if table is HEBNUM:
        while n >= 400: s += "ת"; n -= 400
        if n % 100 in (15, 16): s += _numeral(n - n % 100, table) if n >= 100 else ""; return s + ("טו" if n % 100 == 15 else "טז")
    for v, ch in table:
        while n >= v: s += ch; n -= v
    return s + ("ʹ" if table is GREEKNUM else "")
def _say(vm, text): vm.out.append(text); vm.log.append(f"says {text}")
def _seal_sum(vm, val): _set(vm, [checksum_value(" ".join(f"#{to12(x)}" for x in _i(vm)))])
def to12(x):
    x = int(abs(x)); s = ""
    while True:
        s = DIGITS[x % 12] + s; x //= 12
        if not x: return s
def _modes(side):
    c = 343.0; fs = sorted({round(c / 2 * math.sqrt(a * a + b * b + d * d) / side, 2) for a in range(4) for b in range(4) for d in range(4) if a + b + d})
    return fs[:7]
def _phase(vm, val):
    jd = 2451545.0 + (_i(vm)[-1] if _i(vm) else 0.0); _set(vm, list(phase_stamp(jd).values()))
CANON = {
 # k: number                                                       (column = family, vowel = member)
 "kamu": ("multiply: i <- i x a (pairwise, or by a's last value)", lambda vm, v: _set(vm, [x * y for x, y in zip(_i(vm), _a(vm))] if len(_a(vm)) == len(_i(vm)) else [x * (_a(vm)[-1] if _a(vm) else 1) for x in _i(vm)])),
 "kade": ("divide: i <- i / a", lambda vm, v: _set(vm, [x / (_a(vm)[-1] or float("nan")) for x in _i(vm)])),
 "kagi": ("greatest common divisor of the values of i", lambda vm, v: _set(vm, [float(math.gcd(*[int(x) for x in _i(vm)]))] if _i(vm) else [])),
 "kapi": ("primes up to i's last value", lambda vm, v: _set(vm, _primes(_i(vm)[-1] if _i(vm) else v or 0))),
 "kasu": ("square root of each value", lambda vm, v: _set(vm, [math.sqrt(x) for x in _i(vm)])),
 "kapo": ("power: i <- i ^ a's last value", lambda vm, v: _set(vm, [x ** (_a(vm)[-1] if _a(vm) else 2) for x in _i(vm)])),
 "kaha": ("factorial of i's last value", lambda vm, v: _set(vm, [float(math.factorial(int(_i(vm)[-1])))])),
 "kamo": ("product of all values of i", lambda vm, v: _set(vm, [float(math.prod(_i(vm)))])),
 # t: statistics
 "tame": ("mean", lambda vm, v: _set(vm, [sum(_i(vm)) / len(_i(vm))])),
 "tado": ("median", lambda vm, v: _set(vm, [float(np.median(_i(vm)))])),
 "tasi": ("standard deviation", lambda vm, v: _set(vm, [float(np.std(_i(vm)))])),
 "taku": ("correlation of i with a", lambda vm, v: _set(vm, [float(np.corrcoef(_i(vm), _a(vm))[0, 1])])),
 "tami": ("minimum", lambda vm, v: _set(vm, [min(_i(vm))])),
 "tamo": ("maximum", lambda vm, v: _set(vm, [max(_i(vm))])),
 "taso": ("sort ascending", lambda vm, v: _set(vm, sorted(_i(vm)))),
 # p: geometry and proportion
 "papi": ("pi", lambda vm, v: _set(vm, [math.pi])),
 "pagu": ("the golden ratio", lambda vm, v: _set(vm, [(1 + 5 ** 0.5) / 2])),
 "pari": ("interior angle of a regular polygon with i sides (degrees)", lambda vm, v: _set(vm, [180.0 * (x - 2) / x for x in _i(vm)])),
 "paso": ("star polygon {n/k}: the visiting order of its points (i = n, a = k)", lambda vm, v: _set(vm, [(j * int(_a(vm)[-1] if _a(vm) else 2)) % int(_i(vm)[-1]) for j in range(min(int(_i(vm)[-1]), MAXLEN + 1))])),
 "pamo": ("first seven resonant frequencies of a cube room of side i metres (Hz)", lambda vm, v: _set(vm, _modes(_i(vm)[-1]))),
 "pake": ("cubits to metres (royal cubit 0.5236 m)", lambda vm, v: _set(vm, [x * 0.5236 for x in _i(vm)])),
 "pahe": ("Heron: area of a triangle with sides i[0], i[1], i[2]", lambda vm, v: _set(vm, [(lambda a, b, c: math.sqrt(max(0, (a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c))) / 4)(*_i(vm)[:3])])),
 # b: sequences
 "bari": ("Fibonacci numbers up to i's last value", lambda vm, v: _set(vm, (lambda n: [x for x in (lambda f: f(f, [1, 1], n))(lambda f, s, n: s if s[-1] > n else f(f, s + [s[-1] + s[-2]], n)) if x <= n])(_i(vm)[-1]))),
 "basa": ("triangular numbers T1..Tn, n = i's last value", lambda vm, v: _set(vm, [k * (k + 1) / 2 for k in range(1, min(int(_i(vm)[-1]), MAXLEN + 1) + 1)])),
 "bake": ("running sum", lambda vm, v: _set(vm, list(np.cumsum(_i(vm))))),
 "bada": ("differences between neighbours", lambda vm, v: _set(vm, list(np.diff(_i(vm))))),
 "baro": ("distinct values, in order of first appearance", lambda vm, v: _set(vm, list(dict.fromkeys(_i(vm))))),
 "bato": ("take the first n values (n = #number, default 3)", lambda vm, v: _set(vm, _i(vm)[: int(v or 3)])),
 "baka": ("count of values", lambda vm, v: _set(vm, [len(_i(vm))])),
 # d: doors
 "dasa": ("say i as plain numbers", lambda vm, v: _say(vm, " ".join(f"{x:g}" for x in _i(vm)))),
 "dagi": ("say i as Greek numerals (isopsephy)", lambda vm, v: _say(vm, " ".join(_numeral(x, GREEKNUM) for x in _i(vm)))),
 "dahe": ("say i as Hebrew numerals (gematria)", lambda vm, v: _say(vm, " ".join(_numeral(x, HEBNUM) for x in _i(vm)))),
 "dami": ("sing i as a melody (folded to the octave)", lambda vm, v: vm.events.append(("melody", [fold(x) for x in _i(vm)]))),
 # l: logic (1 = true, 0 = false)
 "lane": ("not", lambda vm, v: _set(vm, [0.0 if x else 1.0 for x in _i(vm)])),
 "lake": ("equal: i == a", lambda vm, v: _set(vm, [1.0 if _i(vm) == _a(vm) else 0.0])),
 "lame": ("less: i's last < a's last", lambda vm, v: _set(vm, [1.0 if _i(vm)[-1] < _a(vm)[-1] else 0.0])),
 "lamo": ("more: i's last > a's last", lambda vm, v: _set(vm, [1.0 if _i(vm)[-1] > _a(vm)[-1] else 0.0])),
 # m: music
 "maro": ("the seven string ratios (a e y i o u w)", lambda vm, v: _set(vm, [RATIO[c] for c in VOWELS])),
 "mahe": ("ratios -> Hz on the carrier", lambda vm, v: _set(vm, [x * vm.f0 for x in _i(vm)])),
 "maki": ("interval in cents from i[0] to each value", lambda vm, v: _set(vm, [1200 * math.log2(x / _i(vm)[0]) for x in _i(vm)])),
 "mapu": ("the Pythagorean comma (cents)", lambda vm, v: _set(vm, [1200 * math.log2(3 ** 12 / 2 ** 19)])),
 # r: time
 "raso": ("celestial phase stamp: seven mean longitudes for J2000 + i days", _phase),
 "rado": ("planetary weekday of J2000 + i days (0 = Sunday ... 6 = Saturday)", lambda vm, v: _set(vm, [float((int(2451545.0 + (_i(vm)[-1] if _i(vm) else 0) + 1.5)) % 7)])),
 # h: seals and checks
 "haso": ("checksum of i's values (mod 7039)", _seal_sum),
}
PRELUDE = """
::kemu kua | kw #0 | lu :keso | kiw ::
::keso bwi nu #1 gw ::
::kegi la :keto ::
::keto kei kia kae mea ::
::kehi kyi | ko #1 | ly :keho | kio ::
::keho kio :kemu ny #1 koi kay ::
"""
# Written in KANON itself, from the 12 primitive operations only:
#   :kemu  multiply i by a by repeated addition (a while-loop on the counter plane u)       uses u, w
#   :kegi  Euclid's algorithm: gcd of i and a (while a > 0: e = i mod a; i = a; a = e)        uses e
#          its body is spelled in ring order: kei kia kae mea executes as kei, mea, kia, kae
#   :kehi  factorial of i (while y > 0: o = o * y; y = y - 1), built on :kemu              uses y, o
def load_prelude(vm):
    _, defs = parse(PRELUDE); vm.defs.update(defs)

# ================================================================ checksums (speech-safe)
def symbols(src):
    """Token codes for checksumming: syllables 0-83, lone vowels 84-90, digits 91-102, marks 103-108."""
    codes = []
    for t in re.findall(r"#[0-9te]+|[!?~:]|[a-z]+", src.replace("::", ": :")):
        if t.startswith("#"): codes += [91 + DIGITS.index(c) for c in t[1:]]
        elif t in "!?~:": codes.append(103 + "!?~:".index(t))
        else:
            for j in range(0, len(t) - len(t) % 2, 2): codes.append(CONS.index(t[j]) * 7 + VOWELS.index(t[j + 1]))
            if len(t) % 2: codes.append(84 + VOWELS.index(t[-1]))
        codes.append(109)   # word boundary
    return codes
MOD = 7039   # a prime just under 84 x 84: the checksum is spoken as two syllables
def checksum_value(src): return sum((j + 1) * c for j, c in enumerate(symbols(src))) % MOD
def checksum_word(src):
    v = checksum_value(src); a, b = divmod(v, 84); return CONS[a // 7] + VOWELS[a % 7] + CONS[b // 7] + VOWELS[b % 7]
def add_checksums(src): return " | ".join(f"{v.strip()} ={checksum_word(v.strip())}" for v in src.split("|") if v.strip())
def verify(text):
    """-> list of (verse, ok) for a decoded program carrying =checksums."""
    res = []
    for v in text.split("|"):
        m = re.search(r"=([a-z]{4})\s*$", v.strip())
        body = re.sub(r"=([a-z]{4})\s*$", "", v.strip()).strip()
        try: ok = bool(m) and checksum_word(body) == m.group(1)
        except (ValueError, IndexError): ok = False      # a garbled word cannot be checksummed: flag it
        res.append((body, ok))
    return res
def strip_checksums(text): return " | ".join(re.sub(r"\s*=[a-z]{4}\s*$", "", v.strip()) for v in text.split("|"))

# ================================================================ audio codec
def _tone(freqs, dur, amp=0.8):
    t = np.arange(int(dur * FS)) / FS; y = sum(np.sin(2 * np.pi * f * t) for f in freqs)
    return amp * y / max(1, len(freqs)) * np.minimum(1, t / 0.008) * np.minimum(1, (dur - t) / 0.015)
def _vowel(v, dur=0.18, f0=F0):
    f = RATIO[v] * f0; t = np.arange(int(dur * FS)) / FS
    y = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t)
    return 0.8 * y / 1.65 * np.minimum(1, t / 0.012) * np.minimum(1, (dur - t) / 0.025)
def encode(src, f0=F0):
    GS, GW, GV = 0.045, 0.22, 0.55; out = [np.zeros(int(0.08 * FS))]; sil = lambda s: np.zeros(int(s * FS))
    mark = lambda ch: [_tone([MARKS[ch] * f0], 0.07), sil(GS)]
    def syl(w):
        o = []
        for j in range(0, len(w) - len(w) % 2, 2):
            i = CONS.index(w[j]); o += [_tone([ROWMUL[i // 3] * f0, COLMUL[i % 3] * f0], 0.07), _vowel(w[j + 1], 0.18, f0), sil(GS)]
        if len(w) % 2: o += [_vowel(w[-1], 0.18, f0), sil(GS)]
        return o
    for vtext in src.replace("\n", " ").split("|"):
        for tk in vtext.split():
            m = re.fullmatch(r"(~?)(::?|=)?([a-z]*)(#[0-9te]+)?([!?]*)", tk)
            if tk.startswith("#"):
                for ch in tk[1:]:
                    i = DIGITS.index(ch); out += [_tone([ROWMUL[i // 3] * f0, COLMUL[i % 3] * f0, MARKMUL * f0], 0.07), _vowel("i", 0.12, f0), sil(GS)]
            else:
                pre, colons, w, _, post = m.groups()
                if pre: out += mark("~")
                for ch in (colons or ""): out += mark(ch)
                out += syl(w)
                for ch in post: out += mark(ch)
            out.append(sil(GW - GS))
        out.append(sil(GV - GW))
    y = np.concatenate(out); return y / (np.abs(y).max() + 1e-9) * 0.9
def _peak(mag, freqs, lo, hi):
    band = (freqs >= lo) & (freqs <= hi)
    if not band.any(): return 0.0, 0.0
    i = np.argmax(mag * band)
    if 0 < i < len(mag) - 1:
        a, b, c = mag[i - 1], mag[i], mag[i + 1]; d = 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
        return freqs[i] + d * (freqs[1] - freqs[0]), mag[i]
    return freqs[i], mag[i]
def decode(y, f0=F0):
    env = np.convolve(np.abs(y), np.ones(220) / 220, mode="same"); thr = 1.8 * np.percentile(env, 25) + 0.015 * env.max(); on = env > thr
    edges = np.flatnonzero(np.diff(on.astype(int)))
    starts = list(edges[::2] if on[0] == 0 else np.r_[0, edges[1::2]]); ends = list(edges[1::2] if on[0] == 0 else edges[0::2])
    segs = []
    for a, b in [(a, b) for a, b in zip(starts, ends) if b - a > int(0.035 * FS)]:
        if segs and a - segs[-1][1] < int(0.03 * FS): segs[-1] = (segs[-1][0], b)
        else: segs.append((a, b))
    toks, prev, num = [], None, False
    for a, b in segs:
        if prev is not None:
            gap = (a - prev) / FS
            if gap > 0.4: toks.append(" | "); num = False
            elif gap > 0.12: toks.append(" "); num = False
        prev = b; seg = y[a:b]; nb = min(len(seg), int(0.06 * FS))
        spec = np.abs(np.fft.rfft(seg[:nb] * np.hanning(nb), 1 << 14)); fr = np.fft.rfftfreq(1 << 14, 1 / FS)
        best = lambda mults: (lambda es: (int(np.argmax(es)), max(es)))([_peak(spec, fr, m * f0 * 0.97, m * f0 * 1.03)[1] for m in mults])
        r, er = best(ROWMUL); c, ec = best(COLMUL); mk = _peak(spec, fr, MARKMUL * f0 * 0.93, MARKMUL * f0 * 1.07)[1]
        mi, em = best(list(MARKS.values()))
        if em > 2.0 * max(er, ec, mk) and (b - a) < int(0.12 * FS):
            ch = list(MARKS)[mi]; toks.append(ch); num = False; continue
        has_burst = max(er, ec) > 0.12 * spec.max(); vpart = seg[nb:] if has_burst else seg; vowel = None
        if len(vpart) > (int(0.05 * FS) if has_burst else int(0.09 * FS)):
            vs = np.abs(np.fft.rfft(vpart * np.hanning(len(vpart)), 1 << 15)); vf = np.fft.rfftfreq(1 << 15, 1 / FS)
            fpk, _ = _peak(vs, vf, f0 * 0.70, f0 * 1.40); vowel = min(VOWELS, key=lambda v: abs(math.log(fpk / (RATIO[v] * f0))))
        if has_burst and mk > 0.5 * max(er, ec):
            if not num: toks.append("#"); num = True
            toks.append(DIGITS[r * 3 + c])
        else:
            num = False
            if has_burst: toks.append(CONS[r * 3 + c] + (vowel or "i"))
            elif vowel and toks and toks[-1] and toks[-1][-1] in CONS: toks.append(vowel)
            elif vowel and toks and toks[-1] and toks[-1][-1] in VOWELS + "| #!?~:=" and len(vpart) > int(0.12 * FS): toks.append(vowel)
    s = " ".join("".join(toks).split())
    s = re.sub(r"(\S)#", r"\1 #", s)       # a number always stands apart from its word
    return s
def norm_text(src):
    s = " ".join(" | ".join(p.strip() for p in src.replace("\n", " ").split("|")).split())
    return re.sub(r"(\S)#", r"\1 #", s)

# ================================================================ time: celestial phase stamps (round-39 style)
EPH = {"Sun": (280.466, 0.98564736), "Moon": (218.316, 13.176396), "Mercury": (252.251, 4.09233445),
       "Venus": (181.980, 1.60213034), "Mars": (355.433, 0.52402068), "Jupiter": (34.351, 0.08308529), "Saturn": (50.077, 0.03349791)}
def phase_stamp(jd): d = jd - 2451545.0; return {p: round((L0 + n * d) % 360.0, 4) for p, (L0, n) in EPH.items()}

# ================================================================ figures: seals
HEPT = {v: k for k, v in enumerate("iaoeuyw")}       # points of the heptagon in weekday order, Sun at the top
def _pt(cx, cy, r, k, n): a = -math.pi / 2 + 2 * math.pi * k / n; return cx + r * math.cos(a), cy + r * math.sin(a)
def word_seal(w, cx, cy, r, ink="#2a2a2a", accent="#b07a2a"):
    """A word's seal: its vowel line drawn as a path on the heptagon (the weekday circle); each consonant is a mark
    on the outer 12-ring (the calendar months), joined to the vowel it sounds with."""
    s = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{ink}" stroke-opacity=".18"/>',
         f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 1.22:.1f}" fill="none" stroke="{ink}" stroke-opacity=".10"/>']
    vs = [c for c in w if c in VOWELS]; pts = [_pt(cx, cy, r, HEPT[v], 7) for v in vs]
    if len(pts) > 1: s.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{accent}" stroke-width="2.2" stroke-linejoin="round"/>')
    for j, c in enumerate(w):
        if c in CONS:
            x1, y1 = _pt(cx, cy, r * 1.22, CONS.index(c), 12)
            if j + 1 < len(w): x2, y2 = _pt(cx, cy, r, HEPT[w[j + 1]], 7); s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ink}" stroke-opacity=".45" stroke-width="1"/>')
            s.append(f'<rect x="{x1 - 2.5:.1f}" y="{y1 - 2.5:.1f}" width="5" height="5" fill="{ink}"/>')
    for k, (x, y) in enumerate(pts): s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3.6 if k == 0 else 2.6}" fill="{accent if k == 0 else ink}"/>')
    return "\n".join(s)
def program_seal(src, path=None, title=None):
    """The program's figure: one ring per verse. Words sit on the ring in written order; arcs join the pairs that the
    ring rule executes together, numbered by execution order; each word carries its own small seal."""
    main, defs = parse(src); verses = main or list(defs.values())[0]
    W = 300 * max(1, min(3, len(verses))); rows = (len(verses) + 2) // 3; H = 300 * rows + 70
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif">', f'<rect width="{W}" height="{H}" fill="#f6f4ef"/>',
         f'<text x="16" y="28" font-size="16" fill="#222">{(title or src)[:90].replace("<", "&lt;")}</text>',
         f'<text x="16" y="48" font-size="11" fill="#777">checksum {" ".join("=" + checksum_word(" ".join(i["word"] for i in v)) for v in verses)}</text>']
    for vi, v in enumerate(verses):
        cx, cy = 150 + 300 * (vi % 3), 70 + 150 + 300 * (vi // 3); R = 110; n = len(v)
        order = schedule(bind_loops(v)); rank = {id(it): k for k, it in enumerate(order)}
        pos = {id(it): _pt(cx, cy, R, k, max(n, 1)) for k, it in enumerate(v)}
        for k in range(n // 2):
            (x1, y1), (x2, y2) = pos[id(v[k])], pos[id(v[n - 1 - k])]
            s.append(f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="#3d6f8a" stroke-opacity=".55" stroke-width="1.6"/>')
        for k, it in enumerate(v):
            x, y = pos[id(it)]; s.append(word_seal(it["word"], x, y, 20))
            label = (":" if it["kind"] == "call" else "") + it["word"] + ("" if it["num"] is None else f" #{to12(it['num'])}")
            s.append(f'<text x="{x:.1f}" y="{y + 40:.1f}" font-size="11" text-anchor="middle" fill="#222">{label}</text>')
            if id(it) in rank: s.append(f'<text x="{x + 24:.1f}" y="{y - 20:.1f}" font-size="10" fill="#3d6f8a">{rank[id(it)] + 1}</text>')
        if n % 2: s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="#3d6f8a"/>')
    s.append("</svg>"); svg = "\n".join(s)
    if path: open(path, "w").write(svg)
    return svg

# ================================================================ audio rendering of outputs
def render_events(events, f0=F0):
    out = []
    for kind, pay in events:
        if kind == "rest": out.append(np.zeros(int(pay * FS)))
        else:
            for r in pay:
                fr = fold(r) * f0; t = np.arange(int(0.35 * FS)) / FS
                out += [sum(np.sin(2 * np.pi * fr * k * t) * abs(math.sin(k * math.pi * 0.2)) / k * np.exp(-t * (1.0 + 0.4 * k)) for k in range(1, 12)), np.zeros(int(0.06 * FS))]
    if not out: return np.zeros(FS // 4)
    y = np.concatenate(out); return y / (np.abs(y).max() + 1e-9) * 0.85
def save_wav(path, y):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(FS); f.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
def load_wav(path):
    with wave.open(path) as f: return np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(float) / 32767

# ================================================================ order analysis: does every reordering make a new process?
def signature(src):
    vm = VM(); vm.run(src); return json.dumps([vm.P[v] for v in VOWELS] + [vm.events, vm.out], sort_keys=True, default=str)
def order_study(n_verses=300, seed=66):
    """For random verses, run every ordering of its words, and every ordering of the syllables of a chained word,
    and count how many distinct processes (final state + output) result."""
    import itertools, random
    R = random.Random(seed); ops_safe = "kbpgtnrmh"; res = dict(words=[], syllables=[])
    for _ in range(n_verses):
        ws = ["sa #" + to12(R.randint(3, 9))]
        for _ in range(3): ws.append(R.choice(ops_safe) + R.choice("ia") + R.choice(VOWELS) + (" #" + to12(R.randint(1, 5)) if R.random() < 0.5 else ""))
        perms = set(itertools.permutations(ws)); sigs = {signature(" ".join(p)) for p in perms}; res["words"].append(len(sigs) / len(perms))
        w = R.choice(ops_safe) + "i" + "".join(R.choice(ops_safe) + R.choice("ia") for _ in range(2))
        sp = [w[j:j + 2] for j in range(0, 6, 2)]; base = "sa #7 ka #3 ki #5 "
        ps = set(itertools.permutations(sp[1:])); sg = {signature(base + sp[0] + "".join(p)) for p in ps}; res["syllables"].append(len(sg) / len(ps))
    return {k: dict(mean_distinct_fraction=round(float(np.mean(v)), 3), all_distinct_share=round(float(np.mean([x == 1 for x in v])), 3)) for k, v in res.items()}

# ================================================================ self-test
def selftest(quick=False):
    out = {}
    assert all(is_word(k) for k in CANON), [k for k in CANON if not is_word(k)]
    vm = VM().run("sa #7 gia ta #3 | di"); assert vm.P["i"] == [22.0], vm.P["i"]
    vm2 = VM().run("sa #7 ta #3 gia | di"); assert vm2.P["i"] == [28.0], vm2.P["i"]
    out["v0.1_compat"] = dict(ring_22=vm.P["i"], reordered_28=vm2.P["i"], iam_song=VM().run("demorini").events)
    # chains: syllable order is composition order
    c1 = VM().run("si #7 | ka #3 | pinata"); c2 = VM().run("si #7 | ka #3 | pitana")
    out["syllable_order"] = dict(pinata=c1.P["i"], pitana=c2.P["i"], note="the same three syllables: subtract a then keep values above a, or keep then subtract - two pipelines, two results")
    assert c1.P["i"] == [4.0] and c2.P["i"] == [1.0, 2.0, 3.0, 4.0], (c1.P["i"], c2.P["i"])
    # names, loops, guards: programs written in KANON itself
    m = VM().run("ki #7 | ka #6 | :kemu"); assert m.P["i"] == [42.0], m.P["i"]
    g = VM().run("ki #2e | ka #18 | :kegi"); assert g.P["i"] == [5.0], g.P["i"]     # gcd(35, 20) = 5 (numbers in base 12)
    f = VM().run("ki #5 | :kehi"); assert f.P["i"] == [120.0], f.P["i"]
    out["prelude"] = dict(multiply_7x6=m.P["i"], gcd_35_20=g.P["i"], factorial_5=f.P["i"])
    cnt = VM().run("::kosu bogou nu #1 :: | ku #5 | ko #0 | lu :kosu")    # while u > 0: o = o + u; u = u - 1
    assert cnt.P["o"] == [15.0], cnt.P["o"]; out["while_loop"] = dict(o=cnt.P["o"], note="lu repeats :kosu while plane u is positive: 5+4+3+2+1")
    gd = VM().run("ki #0 | ka #3 | kia? | :dasa"); gd2 = VM().run("ki #1 | ka #3 | kia? | :dasa")
    out["guard"] = dict(skipped=gd.out, ran=gd2.out); assert gd.out == ["0"] and gd2.out == ["3"]
    # the Canon
    cn = VM().run("ki #29 | :kapi | :dasa | ki #1e | :dagi | ki #e0 | :dahe | ki #8 | ka #3 | :paso | :dasa | ki #8 | :pamo | :dasa")
    out["canon_examples"] = cn.out; out["canon_size"] = len(CANON)
    # codec, now with every mark and checksums
    progs = ["sa #7 gia ta #3 | di", "ki #7 | ka #6 | :kemu | :dasa", "~kia? sa! #5 | ::kesa gia di :: | :kesa", "demorini | sa #7 gia ta #3 | lu #3 pia | ka #e bwi da"]
    rt = []
    for p in progs:
        sp = add_checksums(p); d = decode(encode(sp)); rt.append(dict(src=p, exact=d == norm_text(sp), checks=all(ok for _, ok in verify(d))))
    out["codec_roundtrip"] = rt; assert all(r["exact"] and r["checks"] for r in rt), rt
    if not quick:
        out["codec_fuzz"] = fuzz(120); out["order_study"] = order_study(150)
    out["namespace"] = dict(syllables=84, behaviours_per_one_syllable_word="12 ops x 7 heads x 8 cadences = 672 (+ number)",
        note="v0.2: every syllable acts, so distinct words of k syllables can behave distinctly; the order study measures how often they do")
    out["phase_stamp_J2000+9800d"] = phase_stamp(2451545.0 + 9800)
    return out

def random_program(R):
    def word():
        w = "".join(R.choice(CONS) + R.choice(VOWELS) for _ in range(R.randint(1, 3)))
        return w + (R.choice(VOWELS) if R.random() < 0.3 else "")
    vs = []
    for _ in range(R.randint(1, 3)):
        ws = []
        for _ in range(R.randint(1, 4)):
            w = word(); r = R.random()
            if r < 0.1: w = "~" + w
            elif r < 0.2: w = ":" + w
            if R.random() < 0.15: w += R.choice("!?")
            ws.append(w)
            if R.random() < 0.3: ws.append("#" + "".join(R.choice(DIGITS) for _ in range(R.randint(1, 2))))
        vs.append(" ".join(ws))
    return " | ".join(vs)

def fuzz(n=120, seed=66):
    import random
    R = random.Random(seed); nr = np.random.default_rng(seed); progs = [add_checksums(random_program(R)) for _ in range(n)]; res = {}
    for snr in (None, 12.0, 8.0, 4.0, 2.0):
        exact = flagged = silent_errors = 0
        for p in progs:
            y = encode(p)
            if snr is not None: y = y + nr.standard_normal(len(y)) * y.std() / 10 ** (snr / 20)
            d = decode(y); ok = d == norm_text(p); exact += ok
            if not ok:
                if all(o for _, o in verify(d)) and d.count("|") == p.count("|"): silent_errors += 1
                else: flagged += 1
        res["clean" if snr is None else f"{snr:g} dB"] = dict(exact=f"{exact}/{n}", errors_caught_by_checksum=flagged, errors_missed=silent_errors)
    return res

# ================================================================ glyph chart
def glyph_chart(path):
    W, H = 1000, 760
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif">', f'<rect width="{W}" height="{H}" fill="#f6f4ef"/>',
         '<text x="24" y="40" font-size="26" fill="#222">KANON v0.2: the calendar palace</text>',
         '<text x="24" y="62" font-size="13" fill="#666">seven vowels = the seven days and planet-strings; twelve consonants = the twelve months and operations; a syllable = one of 84 days</text>']
    for j, v in enumerate("iaoeuyw"):
        y0 = 110 + j * 42; hot = v == "i"
        s.append(f'<text x="30" y="{y0}" font-size="22" fill="{"#b07a2a" if hot else "#222"}">{v}</text>')
        s.append(f'<text x="62" y="{y0}" font-size="14" fill="#333">{WEEKDAY[v]} · {PLANET[v]} · ratio {RATIO[v]:.4f} · {RATIO[v] * F0:.1f} Hz · plane: {PLANE_ROLE[v]}</text>')
    gx, gy, cw, ch = 30, 440, 160, 62
    for k, c in enumerate(CONS):
        r, col = k // 3, k % 3; x, y = gx + col * cw, gy + r * ch
        s.append(f'<rect x="{x}" y="{y}" width="{cw - 8}" height="{ch - 8}" rx="6" fill="#fff" stroke="#bbb"/>')
        s.append(f'<text x="{x + 10}" y="{y + 24}" font-size="18" fill="#222">{c}</text><text x="{x + 34}" y="{y + 23}" font-size="13" fill="#333">{OPNAME[c]}</text>')
        s.append(f'<text x="{x + 10}" y="{y + 44}" font-size="11" fill="#888">{MONTH[c]}</text>')
    for r, season in enumerate(["spring", "summer", "autumn", "winter"]): s.append(f'<text x="{gx + 3 * cw + 4}" y="{gy + r * ch + 30}" font-size="12" fill="#888">{season}</text>')
    s.append(f'<text x="600" y="460" font-size="15" fill="#222">marks (spoken as high tones)</text>')
    for k, (mk, d) in enumerate([("|", "breath: end of verse"), ("!", "urgent: runs before the ring"), ("~", "sandbox: errors become no-ops"), ("?", "guard: runs only if i > 0"),
                                 (":", ":name calls · ::name defines · :: ends"), ("#", "number, base 12"), ("=", "checksum of the verse")]):
        s.append(f'<text x="600" y="{488 + k * 24}" font-size="13" fill="#333"><tspan font-size="16">{mk}</tspan>   {d}</text>')
    s.append(f'<text x="600" y="680" font-size="13" fill="#333">inside a word: syllables compose left to right</text>')
    s.append(f'<text x="600" y="700" font-size="13" fill="#333">inside a verse: outer pairs first, the centre last</text>')
    s.append(f'<text x="24" y="{H - 16}" font-size="11" fill="#999">The Sound · KANON v0.2 · run python3 lang4d/kanon.py selftest</text></svg>')
    open(path, "w").write("\n".join(s))

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"; here = os.path.dirname(os.path.abspath(__file__))
    if cmd == "selftest":
        out = selftest(quick="--quick" in sys.argv); json.dump(out, open(os.path.join(here, "selftest_results.json"), "w"), indent=1, ensure_ascii=False, default=str)
        print(json.dumps(out, indent=1, ensure_ascii=False, default=str)); glyph_chart(os.path.join(here, "glyph_chart.svg"))
    elif cmd == "run":
        vm = VM().run(open(sys.argv[2]).read()); print("\n".join(vm.log)); print("output:", vm.out); print("events:", vm.events)
    elif cmd == "speak":
        src = open(sys.argv[2]).read().strip(); vm = VM().run(src)
        y = np.concatenate([encode(add_checksums(src)), np.zeros(FS), render_events(vm.events)]); save_wav(sys.argv[3], y)
        print("wrote", sys.argv[3], f"{len(y) / FS:.1f} s (spoken code with checksums, silence, then the program's own output)")
    elif cmd == "decode":
        d = decode(load_wav(sys.argv[2])); print(d)
        for v, ok in verify(d): print(("ok   " if ok else "CHECK") + " " + v)
    elif cmd == "seal": program_seal(open(sys.argv[2]).read(), sys.argv[3]); print("wrote", sys.argv[3])
    elif cmd == "chart": glyph_chart(sys.argv[2]); print("wrote", sys.argv[2])
    elif cmd == "ring": print(" ".join(ring(sys.argv[2].split())))
    elif cmd == "canon":
        for k, (d, _) in CANON.items(): print(f":{k:6s} {d}")
    elif cmd == "repl":
        vm = VM(); print("KANON v0.2 - type a verse; ':: ' lines define; Ctrl-D to leave")
        for line in sys.stdin:
            try: vm.run(line); print(" i =", vm.P["i"], " out:", vm.out[-1:] if vm.out else "")
            except Exception as e: print(" error:", e)

if __name__ == "__main__": main()
