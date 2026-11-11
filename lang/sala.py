#!/usr/bin/env python3
"""Sala: reference implementation (version 0.1).

One grammar serves people and machines: every sentence has exactly one parse.
  WORD CLASSES BY LENGTH   one syllable (CV) = grammar word; two syllables (CVCV) = root; 'ha Name' = a name;
                           'no' + digit syllables = a number (0 pa 1 ta 2 ka 3 ma 4 na 5 sa 6 la 7 wa 8 ya 9 ha).
  SENTENCE   := LINK? CLAUSE (LINK CLAUSE)* STANCE?
  CLAUSE     := NP? ('sa' TENSE* 'mo'? NP? ROLE*)?          a clause without 'sa' is a fragment ("peace", "and you?")
  ROLE       := ('ke' | 'pe' | 'na' | 'wi' | 'ho') NP
  NP         := 'mo'? HEAD (ROOT | NUMBER)* 'lu'? ('le' NP)? ('ti' CLAUSE 'tu')?
  HEAD       := ROOT | 'mi' | 'yu' | 'si' | NAME | NUMBER
  TENSE      := 'ta' | 'ya' | 'so' | 'mu'
  LINK       := 'ye' | 'yo' | 'ku' | 'te' | 'pa'
  STANCE     := 'ka' | 'pu' | 'hi' | 'he' | 'wa'
Because every phrase ends at the next grammar word, no brackets or word-order rules are needed beyond these.

MACHINE CODE  consonants p t k m n s l w y h = 0-9, vowels a e i o u = 0-4; syllable = consonant*5 + vowel (0-49);
a root = first*50 + second (0-2499, 12 bits). to_bytes() packs a text at 6 bits per syllable; to_call() turns a clause
into a function-call form a program can act on.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
C, V = "ptkmnslwyh", "aeiou"
LEX = json.load(open(os.path.join(HERE, "lexicon.json"), encoding="utf-8"))["roots"]
ROOT = {x["root"]: x for x in LEX}; MEAN = {x["meaning"]: x["root"] for x in LEX}
PRON = {"mi": "I", "yu": "you", "si": "he/she/it"}
ROLEW = {"ke": ("object", "what is acted on"), "pe": ("to", "to, for"), "na": ("in", "in, at, on (place or time)"), "wi": ("with", "with, by means of"), "ho": ("from", "from, because of")}
TENSE = {"ta": ("past", "before now"), "ya": ("future", "after now"), "so": ("can", "is able or allowed"), "mu": ("must", "has to, should")}
LINKW = {"ye": "and", "yo": "or", "ku": "if", "te": "then", "pa": "but"}
STANCE = {"ka": ("question", "asks"), "pu": ("request", "asks someone to do it"), "hi": ("joy", "said gladly, warmly"), "he": ("sorrow", "said sadly"), "wa": ("urgent", "said as a warning")}
OTHER = {"sa": "the action or description follows", "mo": "not", "lu": "more than one", "le": "of (belonging to what follows)", "ti": "which … (a clause describing the word before)", "tu": "end of that clause", "ha": "a name follows", "no": "a number follows"}
PARTICLES = {**{k: v for k, v in PRON.items()}, **{k: v[1] for k, v in ROLEW.items()}, **{k: v[1] for k, v in TENSE.items()}, **LINKW, **{k: v[1] for k, v in STANCE.items()}, **OTHER}
DIGIT = {c + "a": i for i, c in enumerate(C)}
def syl_code(s): return C.index(s[0]) * 5 + V.index(s[1])
def syllables(w): return [w[i:i + 2] for i in range(0, len(w), 2)]
def is_cv(w): return len(w) % 2 == 0 and all(a in C and b in V for a, b in syllables(w))
class SalaError(Exception): pass
# ------------------------------------------------------------------ tokens
def tokenize(text):
    toks = []
    for raw in re.findall(r"[A-Za-zÀ-ɏ']+|[.?!;]", text):
        if raw in ".?!;": toks.append(("end", raw)); continue
        if toks and toks[-1] == ("part", "ha"): toks.append(("name", raw)); continue
        w = raw.lower()
        if w.startswith("no") and len(w) > 2 and is_cv(w) and all(s in DIGIT for s in syllables(w[2:])): toks.append(("num", int("".join(str(DIGIT[s]) for s in syllables(w[2:]))))); continue
        if w in PARTICLES: toks.append(("part", w)); continue
        if w in ROOT: toks.append(("root", w)); continue
        raise SalaError(f"unknown word: {raw}")
    return toks
def sentences(text):
    cur, out = [], []
    for t in tokenize(text):
        if t[0] == "end":
            if cur: out.append(cur); cur = []
        else: cur.append(t)
    if cur: out.append(cur)
    return out
# ------------------------------------------------------------------ parser
class P:
    def __init__(self, toks): self.t, self.i = toks, 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else (None, None)
    def part(self, *ws): k, v = self.peek(); return k == "part" and v in ws
    def take(self): x = self.t[self.i]; self.i += 1; return x
    def np(self):
        neg = False
        if self.part("mo"): self.take(); neg = True
        k, v = self.peek()
        if k == "root" or k == "num": self.take(); head = dict(type=k, value=v)
        elif k == "part" and v in PRON: self.take(); head = dict(type="pron", value=v)
        elif self.part("ha"):
            self.take(); k2, v2 = self.peek()
            if k2 != "name": raise SalaError("a name must follow 'ha'")
            self.take(); head = dict(type="name", value=v2)
        else: raise SalaError(f"a thing-word was expected at word {self.i + 1}")
        n = dict(head=head, mods=[], neg=neg, plural=False, of=None, rel=None)
        while self.peek()[0] in ("root", "num"): n["mods"].append(self.take()[1])
        if self.part("lu"): self.take(); n["plural"] = True
        if self.part("le"): self.take(); n["of"] = self.np()
        if self.part("ti"):
            self.take(); n["rel"] = self.clause()
            if not self.part("tu"): raise SalaError("'ti' must be closed by 'tu'")
            self.take()
        return n
    def starts_np(self): k, v = self.peek(); return k in ("root", "num") or (k == "part" and (v in PRON or v in ("ha", "mo")))
    def clause(self):
        c = dict(subject=None, pred=None, roles=[])
        if self.starts_np(): c["subject"] = self.np()
        if self.part("sa"):
            self.take(); pr = dict(tense=[], neg=False, head=None)
            while self.peek()[0] == "part" and self.peek()[1] in TENSE: pr["tense"].append(self.take()[1])
            if self.part("mo"): self.take(); pr["neg"] = True
            if self.starts_np(): pr["head"] = self.np()
            c["pred"] = pr
            while self.peek()[0] == "part" and self.peek()[1] in ROLEW: r = self.take()[1]; c["roles"].append(dict(role=r, np=self.np()))
        if c["subject"] is None and c["pred"] is None: raise SalaError(f"a clause was expected at word {self.i + 1}")
        return c
    def sentence(self):
        first = self.take()[1] if self.peek()[0] == "part" and self.peek()[1] in LINKW else None      # a sentence may open with a link: "and ...", "if ..."
        s = dict(clauses=[dict(link=first, **self.clause())], stance=None)
        while self.peek()[0] == "part" and self.peek()[1] in LINKW: l = self.take()[1]; s["clauses"].append(dict(link=l, **self.clause()))
        if self.peek()[0] == "part" and self.peek()[1] in STANCE: s["stance"] = self.take()[1]
        if self.i != len(self.t): raise SalaError(f"unexpected word {self.t[self.i][1]!r} at position {self.i + 1}")
        return s
def parse(text): return [P(s).sentence() for s in sentences(text)]
# ------------------------------------------------------------------ meaning: literal English and machine call
def mw(m): return str(m) if isinstance(m, int) else ROOT[m]["meaning"]
def np_en(n):
    h = n["head"]; core = ROOT[h["value"]]["meaning"] if h["type"] == "root" else PRON[h["value"]] if h["type"] == "pron" else str(h["value"])
    if h["type"] == "pron" and n["plural"]: core = {"I": "we", "you": "you all", "he/she/it": "they"}[core]
    out = ("not " if n["neg"] else "") + " ".join([mw(m) for m in reversed(n["mods"]) if not isinstance(m, int)] + [core] + [str(m) for m in n["mods"] if isinstance(m, int)]) + ("s" if n["plural"] and h["type"] == "root" else "")
    if n["of"]: out += " of " + np_en(n["of"])
    if n["rel"]: out += " which " + clause_en(n["rel"])
    return out
def clause_en(c):
    out = []
    if c.get("link"): out.append(LINKW[c["link"]])
    if c["subject"]: out.append(np_en(c["subject"]))
    if c["pred"]:
        p = c["pred"]; t = [TENSE[x][0] for x in p["tense"]]
        out.append("[" + " ".join(t + (["not"] if p["neg"] else [])) + "]" if t or p["neg"] else "")
        if p["head"]: out.append(np_en(p["head"]))
        for r in c["roles"]: out.append((ROLEW[r["role"]][0] + " " if r["role"] != "ke" else "") + np_en(r["np"]))
    return " ".join(x for x in out if x)
def english(s): return ", ".join(clause_en(c) for c in s["clauses"]) + {None: ".", "ka": "?", "pu": ", please.", "hi": "! (gladly)", "he": ". (sadly)", "wa": "! (warning)"}[s["stance"]]
def np_term(n):
    h = n["head"]; core = ROOT[h["value"]]["meaning"] if h["type"] == "root" else {"mi": "speaker", "yu": "listener", "si": "it"}[h["value"]] if h["type"] == "pron" else json.dumps(h["value"])
    args = [mw(m) for m in n["mods"]] + (["plural"] if n["plural"] else []) + ([f"of={np_term(n['of'])}"] if n["of"] else []) + ([f"which={call(n['rel'])}"] if n["rel"] else [])
    t = core + (f"[{', '.join(args)}]" if args else ""); return f"not({t})" if n["neg"] else t
def call(c):
    if not c["pred"]: return np_term(c["subject"])
    p = c["pred"]; name = np_term(p["head"]) if p["head"] else "be"
    args = ([f"who={np_term(c['subject'])}"] if c["subject"] else []) + [f"{ROLEW[r['role']][0]}={np_term(r['np'])}" for r in c["roles"]] + [f"{TENSE[x][0]}=true" for x in p["tense"]]
    t = f"{name}({', '.join(args)})"; return f"not({t})" if p["neg"] else t
def to_call(s):
    cs = s["clauses"]
    if cs[0]["link"] == "ku" and len(cs) > 1 and cs[1]["link"] == "te": body = f"if({call(cs[0])}, then={call(cs[1])})"; rest = cs[2:]
    else: body = call(cs[0]); rest = cs[1:]
    for c in rest: body = f"{LINKW[c['link']]}({body}, {call(c)})"
    return {None: "state", "ka": "ask", "pu": "request", "hi": "state.joy", "he": "state.sorrow", "wa": "alert"}[s["stance"]] + f"({body})"
# ------------------------------------------------------------------ numbers and bytes
def word_code(kind, v):
    if kind == "root": return syl_code(v[:2]) * 50 + syl_code(v[2:])
    if kind == "part": return syl_code(v)
    return v
def number_word(n): return "no" + "".join(C[int(d)] + "a" for d in str(n))
def to_symbols(text):
    """6-bit symbols: 0-49 syllables, 50 word break, 51 sentence end, 52 name start (then length, then bytes as two symbols each)"""
    out = []
    for raw in re.findall(r"[A-Za-zÀ-ɏ']+|[.?!;]", text):
        if raw in ".?!;": out.append(51); continue
        if out and out[-1] == 50 and len(out) >= 2 and out[-2] == syl_code("ha") and (len(out) == 2 or out[-3] in (50, 51)):
            b = raw.encode("utf-8"); out += [52, len(b)] + [x for by in b for x in (by >> 6, by & 63)] + [50]; continue
        out += [syl_code(s) for s in syllables(raw.lower())] + [50]
    return out
def to_bytes(text):
    bits = "".join(f"{s:06b}" for s in to_symbols(text)); bits += "0" * (-len(bits) % 8)
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
def from_bytes(data):
    bits = "".join(f"{b:08b}" for b in data); sym = [int(bits[i:i + 6], 2) for i in range(0, len(bits) - 5, 6)]; out, word, i = [], "", 0
    while i < len(sym):
        s = sym[i]
        if s < 50: word += C[s // 5] + V[s % 5]
        elif s == 50:
            if word: out.append(word); word = ""
        elif s == 51: out.append(".")
        elif s == 52:
            n = sym[i + 1]; by = bytes((sym[i + 2 + 2 * k] << 6) | sym[i + 3 + 2 * k] for k in range(n)); out.append(by.decode("utf-8")); i += 1 + 2 * n
        i += 1
    return re.sub(r" \.", ".", " ".join(out))
# ------------------------------------------------------------------ authoring notation: English keys -> Sala
def render(notation):
    """'word sa ta exist na begin .' -> Sala. Tokens: grammar words as they are, English meaning keys, 'ha Name', '#153'."""
    out = []; prev = None
    for tok in notation.split():
        if tok in ".?!;": out[-1] += tok if out else tok
        elif prev == "ha": out.append(tok)
        elif tok.startswith("#"): out.append(number_word(int(tok[1:])))
        elif tok in PARTICLES: out.append(tok)
        elif tok in MEAN: out.append(MEAN[tok])
        else: raise SalaError(f"no root for {tok!r}")
        prev = tok
    return " ".join(out)
def annotate(text):
    """Per word: (word, dictionary form, meaning, role, hint) for the learning course."""
    res = []
    for toks, s in zip(sentences(text), parse(text)):
        roles = []
        def walk_np(n, role, of=False):
            if n["neg"]: roles.append("link")
            roles.append("of" if of else role)
            if n["head"]["type"] == "name": roles.insert(len(roles) - 1, "link")
            roles.extend(["of" if of else role] * len(n["mods"]))
            if n["plural"]: roles.append("link")
            if n["of"]: roles.append("link"); walk_np(n["of"], role, True)
            if n["rel"]: roles.append("link"); walk_clause(n["rel"]); roles.append("link")
        def walk_clause(c):
            if c.get("link"): roles.append("link")
            if c["subject"]: walk_np(c["subject"], "subject")
            if c["pred"]:
                roles.append("link"); roles.extend(["link"] * len(c["pred"]["tense"]))
                if c["pred"]["neg"]: roles.append("link")
                if c["pred"]["head"]: walk_np(c["pred"]["head"], "verb")
                for r in c["roles"]: roles.append("link"); walk_np(r["np"], "object" if r["role"] == "ke" else "to")
        for c in s["clauses"]: walk_clause(c)
        if s["stance"]: roles.append("link")
        assert len(roles) == len(toks), (roles, toks)
        words = []
        for (k, v), r in zip(toks, roles):
            if k == "root": words.append(dict(w=v, lemma=v, gloss=ROOT[v]["meaning"], role=r, hint={"subject": "who or what", "verb": "the action or description", "object": "what is acted on", "to": "place, goal or means", "of": "belongs with the word before"}.get(r, "")))
            elif k == "part": words.append(dict(w=v, lemma=v, gloss=PRON.get(v) or (ROLEW[v][0] if v in ROLEW else TENSE[v][0] if v in TENSE else LINKW.get(v) or (STANCE[v][0] if v in STANCE else {"sa": "(does / is)", "mo": "not", "lu": "(many)", "le": "of", "ti": "which", "tu": "(end)", "ha": "(name)"}[v])), role=r if v in PRON else "link", hint=PARTICLES[v] if v not in PRON else "who or what"))
            elif k == "name": words.append(dict(w=v, lemma=v.lower(), gloss=v, role=r, hint="a name"))
            else: words.append(dict(w=number_word(v), lemma=number_word(v), gloss=str(v), role=r, hint="a number"))
        res.append(dict(tokens=words, meaning=english(s)))
    return res
if __name__ == "__main__":
    import sys
    t = " ".join(sys.argv[1:]) or render("word sa ta exist na begin . sa open ke door pu")
    print(t)
    for s in parse(t): print("  ", english(s), "|", to_call(s))
    b = to_bytes(t); print("  ", len(t), "characters ->", len(b), "bytes:", b.hex(), "->", from_bytes(b))
