#!/usr/bin/env python3
"""PLAIN: KANON read aloud as what it DOES, in the order it RUNS, and parsed back exactly.

The word skin (skins.py) maps each syllable to an everyday word: exact, but "sat seven geese-at" says nothing about the
action. The plain skin maps each OPERATION to a fixed English phrase:
    sa #7 gia ta #3 | di
    ->  "1. count to 7 in moon. 2. keep moon's values above 3. 3. set sun to the sum of moon. | 1. send sun out."
Every phrase is generated from the operation, its plane, its source and its number, never from anything the author
wrote, so the English cannot say something the program does not do. Each phrase pattern is unique, so the sentence
parses back to the program (written order is recovered from the execution order with the ring rule, which is a
one-to-one mapping). Numbers are decimal for people; the program keeps base twelve.
Planes are named by their bodies: i sun, a moon, e mercury, y venus, o mars, u jupiter, w saturn.
Usage: python3 plain.py   (round-trip test on random programs)"""
import os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import kanon as K
PN = {"i": "sun", "a": "moon", "e": "mercury", "y": "venus", "o": "mars", "u": "jupiter", "w": "saturn"}; NP = {v: k for k, v in PN.items()}
def b12(x): return K.to12(int(x))
def num(tok): return int("".join(str(K.DIGITS.index(c)) and str(K.DIGITS.index(c)) for c in tok), 12) if False else sum(K.DIGITS.index(c) * 12 ** k for k, c in enumerate(reversed(tok)))
# ---------------------------------------------------------------- one syllable -> phrase
def phrase(op, h, src, val, first, cad_explicit):
    H, C = PN[h], PN.get(src or "", "")
    V = None if val is None else f"{int(val)}"
    if op == "s": return f"count to {V} in {H}" if V else (f"count to the last of {C} in {H}" if cad_explicit else f"count to seven in {H}")
    if op == "k": return f"keep {V} in {H}" if V else (f"copy {C} into {H}" if cad_explicit else f"clear {H}")
    if op == "b": return f"add {C} onto the end of {H}" if cad_explicit else f"double {H} by adding it to itself"
    if op == "p": return f"multiply {H} by {V}" if V else (f"tune {H} by {C}'s ratio" if cad_explicit else f"tune {H} by sun's ratio, unchanged")
    if op == "g": return (f"set {H} to the sum of {C}" if cad_explicit else f"set {H} to its own sum") + (f" plus {V}" if V else "")
    if op == "t": return f"keep {H}'s values above {V}" if V else (f"keep {H}'s values above the last of {C}" if cad_explicit and src != h else (f"keep {H}'s values above their mean, by {C}" if cad_explicit else f"keep {H}'s values above their mean"))
    if op == "n": return f"subtract {V} from {H}" if V else (f"subtract the last of {C} from {H}" if cad_explicit and src != h else (f"negate {H}, by {C}" if cad_explicit else f"negate {H}"))
    if op == "r": return f"rotate {H} by {V}" if V else (f"reverse {H}, by {C}" if cad_explicit else f"reverse {H}")
    if op == "m": return f"take {H} modulo {V}" if V else (f"take {H} modulo the last of {C}" if cad_explicit and src != h else (f"glide {H} toward {C}" if cad_explicit else f"glide {H}"))
    if op == "d": return f"send {H} out" + (f", by {C}" if cad_explicit else "")
    if op == "h": return f"count the values of {C} into {H}" if cad_explicit else (f"rest for {V} tenths, {H}" if V else f"rest, {H}")
    if op == "l": return f"loop marker {H}" + (f" by {C}" if cad_explicit else "")
    raise ValueError(op)
PATTERNS = []   # (regex, builder) - built from phrase() so the two can never drift apart
def _word_text(w, val):
    syl = [w[j:j + 2] for j in range(0, len(w) - len(w) % 2, 2)]; cad = w[-1] if len(w) % 2 else None; h = syl[0][1]
    unused = f", number {int(val)}" if val is not None and (syl[0][0] in "bdl" or (syl[0][0] == "h" and cad) or (syl[0][0] == "d" and len(syl) >= 2)) else ""
    if syl[0][0] == "d" and len(syl) >= 2: return "sing " + "-".join(PN[c] for c in w if c in K.VOWELS) + f" ({w})" + unused
    src_unused = f", from {PN[cad]}" if cad and val is not None and syl[0][0] in "skptnrm" else ""   # a number overrides the source: still say it
    parts = [phrase(syl[0][0], h, cad, val, True, cad is not None) + src_unused + unused]
    for s in syl[1:]: parts.append(phrase(s[0], h, s[1], None, False, True))
    return ", then ".join(parts)
def item_text(it):
    pre = ("first, " if it["urgent"] else "") + ("if sun is positive, " if it["guard"] else "") + ("try to " if it["sandbox"] else "")
    if it["kind"] == "call": core = f"call {it['word']}" + (f" with {int(it['num'])}" if it["num"] is not None else "")
    elif "body" in it:
        w = it["word"]; head = PN[w[1]]
        core = (f"repeat {int(it['num'])} times: " if it["num"] is not None else f"while {head} is positive, repeat: ") + item_text(it["body"]).rstrip(".")
        if len(w) > 2: core += f" [loop word {w}]"
    else: core = _word_text(it["word"], it["num"])
    return pre + core
def verse_text(items):
    order = K.schedule(K.bind_loops(items))
    return "; ".join(f"{k + 1}) {item_text(it)}" for k, it in enumerate(order)) + "."
def to_plain(src):
    main, defs = K.parse(src); out = []
    for n, body in defs.items(): out.append(f"define {n} as: " + " / ".join(verse_text(v) for v in body) + " end.")
    out += [verse_text(v) for v in main]
    return " | ".join(out)
# ---------------------------------------------------------------- parsing back
def _pat(s):   # turn a generated phrase into a regex with groups for plane names and numbers
    s = re.escape(s); return s
PL = "(sun|moon|mercury|venus|mars|jupiter|saturn)"; NUM = r"(\d+)"
RULES = [  # (regex, function(groups) -> (op, head, src or None, val or None, explicit))
 (rf"count to {NUM} in {PL}", lambda g: ("s", NP[g[1]], None, int(g[0]), False)), (rf"count to the last of {PL} in {PL}", lambda g: ("s", NP[g[1]], NP[g[0]], None, True)),
 (rf"count to seven in {PL}", lambda g: ("s", NP[g[0]], None, None, False)),
 (rf"keep {NUM} in {PL}", lambda g: ("k", NP[g[1]], None, int(g[0]), False)), (rf"copy {PL} into {PL}", lambda g: ("k", NP[g[1]], NP[g[0]], None, True)), (rf"clear {PL}", lambda g: ("k", NP[g[0]], None, None, False)),
 (rf"add {PL} onto the end of {PL}", lambda g: ("b", NP[g[1]], NP[g[0]], None, True)), (rf"double {PL} by adding it to itself", lambda g: ("b", NP[g[0]], None, None, False)),
 (rf"multiply {PL} by {NUM}", lambda g: ("p", NP[g[0]], None, int(g[1]), False)), (rf"tune {PL} by {PL}'s ratio", lambda g: ("p", NP[g[0]], NP[g[1]], None, True)), (rf"tune {PL} by sun's ratio, unchanged", lambda g: ("p", NP[g[0]], None, None, False)),
 (rf"set {PL} to the sum of {PL} plus {NUM}", lambda g: ("g", NP[g[0]], NP[g[1]], int(g[2]), True)), (rf"set {PL} to the sum of {PL}", lambda g: ("g", NP[g[0]], NP[g[1]], None, True)),
 (rf"set {PL} to its own sum plus {NUM}", lambda g: ("g", NP[g[0]], None, int(g[1]), False)), (rf"set {PL} to its own sum", lambda g: ("g", NP[g[0]], None, None, False)),
 (rf"keep {PL}'s values above {NUM}", lambda g: ("t", NP[g[0]], None, int(g[1]), False)), (rf"keep {PL}'s values above the last of {PL}", lambda g: ("t", NP[g[0]], NP[g[1]], None, True)),
 (rf"keep {PL}'s values above their mean, by {PL}", lambda g: ("t", NP[g[0]], NP[g[1]], None, True)), (rf"keep {PL}'s values above their mean", lambda g: ("t", NP[g[0]], None, None, False)),
 (rf"subtract {NUM} from {PL}", lambda g: ("n", NP[g[1]], None, int(g[0]), False)), (rf"subtract the last of {PL} from {PL}", lambda g: ("n", NP[g[1]], NP[g[0]], None, True)),
 (rf"negate {PL}, by {PL}", lambda g: ("n", NP[g[0]], NP[g[1]], None, True)), (rf"negate {PL}", lambda g: ("n", NP[g[0]], None, None, False)),
 (rf"rotate {PL} by {NUM}", lambda g: ("r", NP[g[0]], None, int(g[1]), False)), (rf"reverse {PL}, by {PL}", lambda g: ("r", NP[g[0]], NP[g[1]], None, True)), (rf"reverse {PL}", lambda g: ("r", NP[g[0]], None, None, False)),
 (rf"take {PL} modulo {NUM}", lambda g: ("m", NP[g[0]], None, int(g[1]), False)), (rf"take {PL} modulo the last of {PL}", lambda g: ("m", NP[g[0]], NP[g[1]], None, True)),
 (rf"glide {PL} toward {PL}", lambda g: ("m", NP[g[0]], NP[g[1]], None, True)), (rf"glide {PL}", lambda g: ("m", NP[g[0]], None, None, False)),
 (rf"send {PL} out, by {PL}", lambda g: ("d", NP[g[0]], NP[g[1]], None, True)), (rf"send {PL} out", lambda g: ("d", NP[g[0]], None, None, False)),
 (rf"count the values of {PL} into {PL}", lambda g: ("h", NP[g[1]], NP[g[0]], None, True)), (rf"rest for {NUM} tenths, {PL}", lambda g: ("h", NP[g[1]], None, int(g[0]), False)), (rf"rest, {PL}", lambda g: ("h", NP[g[0]], None, None, False)),
 (rf"loop marker {PL} by {PL}", lambda g: ("l", NP[g[0]], NP[g[1]], None, True)), (rf"loop marker {PL}", lambda g: ("l", NP[g[0]], None, None, False)),
]
RULES = [(re.compile(r + "$"), f) for r, f in RULES]
def _parse_phrase(p):
    if p == "glide sun toward sun": pass
    for rx, f in RULES:
        m = rx.match(p)
        if m and f: return f(m.groups())
    raise ValueError(f"not a KANON phrase: {p!r}")
def _parse_word(text):
    """'count to 7 in moon, then ...' -> (word, val)."""
    extra = None
    m = re.search(r", number (\d+)$", text.split(", then ")[0]) if not text.startswith("sing ") else re.search(r", number (\d+)$", text)
    if m: extra = int(m.group(1)); text = text.replace(m.group(0), "", 1)
    if text.startswith("sing "): return re.search(r"\(([a-z]+)\)$", text).group(1), extra
    parts = text.split(", then "); fsrc = re.search(rf", from {PL}$", parts[0])
    if fsrc: parts[0] = parts[0][: fsrc.start()]
    op, h, src, val, ex = _parse_phrase(parts[0])
    if fsrc: src, ex = NP[fsrc.group(1)], True
    if extra is not None: val = extra
    if ex is False and op == "m" and src is None: pass
    w = op + h; chain = ""
    for p in parts[1:]:
        o2, h2, s2, v2, _ = _parse_phrase(p); chain += o2 + s2
    return w + chain + (src if ex else ""), val
def _parse_item(t):
    it = dict(urgent=False, guard=False, sandbox=False)
    for flag, key in (("first, ", "urgent"), ("if sun is positive, ", "guard"), ("try to ", "sandbox")):
        if t.startswith(flag): it[key] = True; t = t[len(flag):]
    m = re.match(r"repeat (\d+) times: (.*?)(?: \[loop word ([a-z]+)\])?$", t) or re.match(r"while (\w+) is positive, repeat: (.*?)(?: \[loop word ([a-z]+)\])?$", t)
    if m:
        body = _parse_item(m.group(2)); lw = m.group(3) or ("l" + (NP[m.group(1)] if not m.group(1).isdigit() else "i"))
        if m.group(1).isdigit() and not m.group(3): lw = "li"
        return [dict(it, kind="word", word=lw, num=float(m.group(1)) if m.group(1).isdigit() else None)] + body
    m = re.match(r"call ([a-z]+)(?: with (\d+))?$", t)
    if m: return [dict(it, kind="call", word=m.group(1), num=float(m.group(2)) if m.group(2) else None)]
    w, val = _parse_word(t); return [dict(it, kind="word", word=w, num=None if val is None else float(val))]
def _render(items):
    out = []
    for it in items:
        tok = ("~" if it["sandbox"] else "") + (":" if it["kind"] == "call" else "") + it["word"] + ("!" if it["urgent"] else "") + ("?" if it["guard"] else "")
        out.append(tok + ("" if it["num"] is None else f" #{b12(it['num'])}"))
    return " ".join(out)
def _verse_from(text):
    text = text[:-1] if text.endswith(".") else text
    steps = [s.strip() for s in re.split(r"(?:^|; )\d+\) ", text) if s.strip()]; units = [_parse_item(s) for s in steps]
    urgent = [u for u in units if u[0]["urgent"]]; rest = [u for u in units if not u[0]["urgent"]]
    written = urgent + K.ring(rest) if rest else urgent
    return _render([x for u in written for x in u])
def from_plain(text):
    out = []
    for part in [p.strip() for p in text.split(" | ")]:
        m = re.match(r"define ([a-z]+) as: (.*) end\.$", part)
        if m: out.append(f"::{m.group(1)} " + " | ".join(_verse_from(v) for v in m.group(2).split(" / ")) + " ::")
        else: out.append(_verse_from(part))
    return " | ".join(out)
def well_formed(src):
    """The agent and flight profiles require every loop word to have a body (a loop with nothing to repeat is an error)."""
    main, defs = K.parse(src)
    for v in main + [x for b in defs.values() for x in b]:
        if v and v[-1]["kind"] == "word" and v[-1]["word"][0] == "l": return False
    return True
def canonical_semantics(src):
    vm = K.VM(); vm.run(src); return ([vm.P[v] for v in K.VOWELS], [str(o) for o in vm.out], len(vm.events))
if __name__ == "__main__":
    for p in ["sa #7 gia ta #3 | di", "sa #7 ta #3 gia | di", "si #7 | ka #3 | pinata | di", "si #3 di ki! #9", "ki #0 | ka #3 | kia? | di",
              "si #2 | li #3 pi #2 | di", "::kosu bogou nu #1 :: | ku #5 | ko #0 | lu :kosu | kio | di"]:
        e = to_plain(p); b = from_plain(e); print(f"{p}\n   {e}\n   back: {b}   same behaviour: {canonical_semantics(b) == canonical_semantics(p)}")
    R = random.Random(11); exact = same = errs = 0; N = 2000; shown = 0
    for _ in range(N):
        p = K.random_program(R).replace("~", "")
        try: base = canonical_semantics(p)
        except Exception: continue
        if not well_formed(p): continue
        errs += 1; e = to_plain(p)
        try: b = from_plain(e)
        except Exception as ex:
            if shown < 6: print("PARSE", ex, "|", p); shown += 1
            continue
        exact += K.norm_text(b) == K.norm_text(p)
        try: ok = canonical_semantics(b) == base
        except Exception as ex: ok = False
        same += ok
        if not ok and shown < 6: print("DIFF", p, "->", b); shown += 1
    print(f"well-formed random programs that run: {errs}; read back exactly as written: {exact}; read back with identical behaviour: {same}")
    print("   (not exact as written = an urgent word written mid-verse; the English puts it first, where it runs)")
