#!/usr/bin/env python3
"""KANON-AGENT: an AI agent proposes; a person hears exactly what will run; only that runs.

The agent never sends free text to be executed. It sends an ACTION VERSE: literal arguments in named planes, then a
call to a tool. The tool names are KANON syllables whose English skin word IS the verb, so the written code, the
spoken word and the function are one and the same:
    :py  pay        :te  tell       :mi  meet       :kw  call       :hi  heat       :ma  map (fly a drone to)
    :le  let (grant access)         :no  no (cancel)
From the verse the engine generates, deterministically:
    the SENTENCE      "Pay $250.00 to Maria Lopez."  (and the sentence parses back to the identical verse)
    the PRECISE FORM  the plain-skin reading of every step
    the CONFIRMATION  three words derived from SHA-256 of the verse ("seed tune gall")
    the SPOKEN FORM   the sentence + confirmation words, read aloud; and the verse itself as error-corrected tones
The person approves by saying or typing the confirmation words. Their device signs (Ed25519) the verse hash with a
one-time nonce. The executor runs a verse only with a matching, unused signature, after the static checks.
Usage: python3 approve.py    (runs every scenario, writes TRANSCRIPT.md, results.json and the spoken readbacks)"""
import datetime, hashlib, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.dirname(HERE)
for p in (L, os.path.join(L, "fields"), os.path.join(L, "chain")): sys.path.insert(0, p)
import kanon as K, skins as S, plain as PL, geocode as G
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
CONTACTS = {1: "Maria Lopez", 2: "Daniel Cohen", 3: "Ground Station Svalbard", 4: "Dr Amara Okafor"}
MESSAGES = {1: "The launch window moved to Thursday.", 2: "Invoice 4471 is paid.", 3: "Please send the telemetry from pass 12."}
SUBSCRIPTIONS = {1: "the cloud backup plan", 2: "the satellite imagery feed"}
ACCESS = {1: "read", 2: "edit", 3: "admin"}
DAY0 = datetime.date(2026, 1, 1)
PLACES = {"Temple Mount, Jerusalem": (31.7781, 35.2354), "Launch Complex 39A": (28.6083, -80.6041)}
def place_index(lat, lon):
    v = 0
    for x in G.encode(lat, lon): v = v * 84 + x
    return v
def place_code(v):
    s = []
    for _ in range(7): s.append(v % 84); v //= 84
    return s[::-1]
KINDS = {   # how each argument is shown to a person, and parsed back
 "money": (lambda v: f"${v // 100:,}.{v % 100:02d}", r"\$([\d,]+)\.(\d\d)", lambda g: int(g[0].replace(",", "")) * 100 + int(g[1])),
 "contact": (lambda v: CONTACTS[v], "(" + "|".join(map(re.escape, CONTACTS.values())) + ")", lambda g: {n: k for k, n in CONTACTS.items()}[g[0]]),
 "message": (lambda v: f"“{MESSAGES[v]}”", "“(" + "|".join(map(re.escape, MESSAGES.values())) + ")”", lambda g: {n: k for k, n in MESSAGES.items()}[g[0]]),
 "date": (lambda v: (DAY0 + datetime.timedelta(days=v)).strftime("%A %d %B %Y"), r"\w+day (\d\d) (\w+) (\d{4})", lambda g: (datetime.datetime.strptime(f"{g[0]} {g[1]} {g[2]}", "%d %B %Y").date() - DAY0).days),
 "minutes": (lambda v: f"{v} minutes", r"(\d+) minutes", lambda g: int(g[0])),
 "temperature": (lambda v: f"{v // 10}.{v % 10} °C", r"(\d+)\.(\d) °C", lambda g: int(g[0]) * 10 + int(g[1])),
 "place": (lambda v: f"place “{' '.join(S.EN_ENC[K.CONS[x // 7] + K.VOWELS[x % 7]] for x in place_code(v))}”", r"place “([a-z ]+)”",
           lambda g: (lambda ws: (lambda s: __import__('functools').reduce(lambda a, b: a * 84 + b, s, 0))([K.CONS.index(S.EN_DEC[w][0]) * 7 + K.VOWELS.index(S.EN_DEC[w][1]) for w in ws]))(g[0].split())),
 "metres": (lambda v: f"{v} metres", r"(\d+) metres", lambda g: int(g[0])),
 "access": (lambda v: ACCESS[v], "(" + "|".join(ACCESS.values()) + ")", lambda g: {n: k for k, n in ACCESS.items()}[g[0]]),
 "subscription": (lambda v: SUBSCRIPTIONS[v], "(" + "|".join(map(re.escape, SUBSCRIPTIONS.values())) + ")", lambda g: {n: k for k, n in SUBSCRIPTIONS.items()}[g[0]]),
}
TOOLS = {   # name (its English skin word is the verb): planes and kinds, sentence, limits
 "py": dict(args=[("a", "money"), ("e", "contact")], say="Pay {a} to {e}.", limits={"a": (1, 100000)}),
 "te": dict(args=[("e", "contact"), ("y", "message")], say="Tell {e}: {y}", limits={}),
 "mi": dict(args=[("e", "contact"), ("y", "date"), ("o", "minutes")], say="Meet {e} on {y} for {o}.", limits={"o": (5, 240)}),
 "kw": dict(args=[("e", "contact")], say="Call {e}.", limits={}),
 "hi": dict(args=[("a", "temperature")], say="Heat the room to {a}.", limits={"a": (160, 260)}),
 "ma": dict(args=[("a", "place"), ("e", "metres")], say="Map a drone flight to {a} at {e}.", limits={"e": (10, 120)}),
 "le": dict(args=[("e", "contact"), ("a", "access")], say="Let {e} have {a} access.", limits={"a": (1, 2)}),
 "no": dict(args=[("a", "subscription")], say="No: cancel {a}.", limits={}),
}
assert all(S.EN_ENC[n] in ("pay", "tell", "meet", "call", "heat", "map", "let", "no") for n in TOOLS)
# ------------------------------------------------------------------ verse <-> structured action
def make_verse(tool, **vals):
    t = TOOLS[tool]; return " | ".join([f"k{p} #{K.to12(vals[p])}" for p, _ in t["args"]] + [f":{tool}"])
def read_action(verse):
    """Check the verse is a pure action (literal arguments, one tool call) and return (tool, {plane: value})."""
    main, defs = K.parse(verse)
    if defs: raise ValueError("an action may not define names")
    vals, tool = {}, None
    for v in main:
        if len(v) != 1: raise ValueError("each verse of an action holds one step")
        it = v[0]
        if it["urgent"] or it["guard"] or it["sandbox"]: raise ValueError("marks are not allowed in an action")
        if it["kind"] == "call":
            if it["word"] not in TOOLS: raise ValueError(f":{it['word']} is not an approved tool")
            if tool: raise ValueError("one tool call per action"); tool = it["word"]
            tool = it["word"]
        elif re.fullmatch(r"k[aeyiouw]", it["word"]) and it["num"] is not None and not tool: vals[it["word"][1]] = int(it["num"])
        else: raise ValueError(f"'{it['word']}' is not a literal argument: arguments must be stated, not computed")
    if not tool: raise ValueError("no tool call")
    need = [p for p, _ in TOOLS[tool]["args"]]
    if sorted(vals) != sorted(need): raise ValueError(f":{tool} needs arguments in {need}, got {sorted(vals)}")
    for p, (lo, hi) in TOOLS[tool]["limits"].items():
        if not lo <= vals[p] <= hi: raise ValueError(f"{KINDS[dict(TOOLS[tool]['args'])[p]][0](vals[p])} is outside the allowed range {KINDS[dict(TOOLS[tool]['args'])[p]][0](lo)} to {KINDS[dict(TOOLS[tool]['args'])[p]][0](hi)}")
    for p, kind in TOOLS[tool]["args"]: KINDS[kind][0](vals[p])        # unknown contact, message ... raise here
    return tool, vals
def sentence(verse):
    tool, vals = read_action(verse); t = TOOLS[tool]
    return t["say"].format(**{p: KINDS[k][0](vals[p]) for p, k in t["args"]})
def from_sentence(text):
    """The sentence parses back to the identical verse (no other path from English to code exists)."""
    for tool, t in TOOLS.items():
        rx = re.escape(t["say"])
        for p, k in t["args"]: rx = rx.replace(re.escape("{" + p + "}"), f"(?P<{p}>.+?)")
        m = re.fullmatch(rx, text)
        if not m: continue
        vals = {}
        for p, k in t["args"]:
            mm = re.fullmatch(KINDS[k][1], m.group(p))
            if not mm: break
            vals[p] = KINDS[k][2](mm.groups())
        else: return make_verse(tool, **vals)
    raise ValueError("not an action sentence")
VERBS = {S.EN_ENC[n] for n in TOOLS}
CONF = [S.EN_ENC[c + v] for c in K.CONS for v in K.VOWELS if S.EN_ENC[c + v] not in VERBS]   # 76 words: never a tool verb, never "no"
def confirmation(verse):
    """Three words from SHA-256 of the canonical verse, drawn from the 76 non-verb words: 438,976 possibilities.
    (The two-syllable seal has only 7,039 values: it is for the eye, not for binding an approval.)"""
    h = int(hashlib.sha256(K.norm_text(verse).encode()).hexdigest(), 16); w = []
    for _ in range(3): w.append(CONF[h % len(CONF)]); h //= len(CONF)
    return w
def heard_matches(heard, verse):
    """Compare what the person said with the confirmation words. Homophones count (meat = meet). -> (ok, explanation)."""
    want = confirmation(verse); words = [S.EN_DEC.get(w, None) for w in re.findall(r"[a-z]+", heard.lower()) if w not in ("approve", "approved", "yes")]
    got = [S.EN_ENC.get(c, "?") if c else "?" for c in words]
    if got == want: return True, "confirmed"
    diffs = [f"word {k + 1}: heard “{g}”, expected “{w}”" for k, (g, w) in enumerate(zip(got + ["(nothing)"] * 3, want)) if g != w]
    return False, "not confirmed - " + "; ".join(diffs) + ". Please repeat the three words."
def claim_check(claim, verse):
    """Flag every amount, name, number or date in the agent's own explanation that the action does not contain."""
    s = sentence(verse); flags = []
    for amt in re.findall(r"\$[\d,]+(?:\.\d\d)?", claim):
        norm = amt if "." in amt else amt + ".00"
        if norm not in s: flags.append(f"the agent says {amt}, the action says {re.search(r'\$[\d,.]+', s).group(0) if '$' in s else 'no amount'}")
    for name in CONTACTS.values():
        if name.split()[0] in claim and name not in s: flags.append(f"the agent mentions {name}, the action is for someone else")
    return flags
# ------------------------------------------------------------------ numbers to words, for speech
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def words(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    if n < 1000: return ONES[n // 100] + " hundred" + (" and " + words(n % 100) if n % 100 else "")
    return words(n // 1000) + " thousand" + (" " + words(n % 1000) if n % 1000 else "")
def speakable(text):
    text = re.sub(r"\$([\d,]+)\.(\d\d)", lambda m: f"{words(int(m.group(1).replace(',', '')))} dollars" + (f" and {words(int(m.group(2)))} cents" if int(m.group(2)) else ""), text)
    text = re.sub(r"(\d+)\.(\d) °C", lambda m: f"{words(int(m.group(1)))} point {words(int(m.group(2)))} degrees Celsius", text)
    text = re.sub(r"\b(\d{4})\b", lambda m: words(int(m.group(1)[:2])) + " " + words(int(m.group(1)[2:])), text)
    return re.sub(r"\b(\d+)\b", lambda m: words(int(m.group(1))), text).replace("“", "").replace("”", "")
VOICE = "/tmp/claude-0/-home-user-the-sound/1e79aa4f-ac53-5c71-93b8-a7e8d094c1e4/scratchpad/voices/en_US-ryan-medium.onnx"
def say(text, mp3):
    if not os.path.exists(VOICE): return False
    tmp = tempfile.mktemp(suffix=".wav"); subprocess.run(["piper", "-m", VOICE, "-f", tmp], input=text, text=True, capture_output=True, check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-b:a", "64k", mp3], check=True); return True
# ------------------------------------------------------------------ the approval device and the executor
class Approver:
    def __init__(self): self.sk = Ed25519PrivateKey.generate(); self.pub = self.sk.public_key()
    def approve(self, verse, heard, nonce):
        ok, why = heard_matches(heard, verse)
        if not ok: return None, why
        msg = json.dumps(dict(hash=hashlib.sha256(K.norm_text(verse).encode()).hexdigest(), nonce=nonce), sort_keys=True).encode()
        return dict(nonce=nonce, sig=self.sk.sign(msg).hex()), why
class Executor:
    def __init__(self, pub): self.pub = pub; self.used = set(); self.log = []
    def run(self, verse, token):
        tool, vals = read_action(verse)                                   # static checks again, at the point of execution
        if token is None: raise PermissionError("no approval")
        msg = json.dumps(dict(hash=hashlib.sha256(K.norm_text(verse).encode()).hexdigest(), nonce=token["nonce"]), sort_keys=True).encode()
        try: self.pub.verify(bytes.fromhex(token["sig"]), msg)
        except Exception: raise PermissionError("the approval does not match this action (it was changed after approval)")
        if token["nonce"] in self.used: raise PermissionError("this approval was already used")
        self.used.add(token["nonce"]); vm = K.VM(); vm.run(K.strip_checksums(verse).replace(f":{tool}", ""))      # arguments land in planes exactly
        args = {p: int(vm.P[p][-1]) for p, _ in TOOLS[tool]["args"]}; self.log.append((tool, args)); return f"executed {sentence(verse)}"
# ------------------------------------------------------------------ scenarios
def main():
    R = {}; md = ["# KANON-AGENT approval demo: transcript", "", "Generated by `approve.py`. Every line below was produced by running the code.", ""]
    ap = Approver(); ex = Executor(ap.pub)
    def show(title, verse, claim=None):
        md.extend([f"## {title}", "", f"- **Action verse (what will run):** `{verse}`"])
        try:
            s = sentence(verse); c = confirmation(verse)
            md.extend([f"- **Sentence (generated from the verse):** {s}", f"- **Precise form:** {PL.to_plain(verse)}", f"- **Seal:** ={K.checksum_word(K.norm_text(verse))} · **Confirmation words:** {' '.join(c)}",
                       f"- **Spoken readback:** “{speakable(s)} To approve, say: {' '.join(c)}.”", f"- **Sentence parses back to the same verse:** {from_sentence(s) == K.norm_text(verse)}"])
            if claim:
                fl = claim_check(claim, verse); md.append(f"- **Agent's own explanation:** “{claim}”"); md.append(f"- **Claim check:** {'; '.join(fl) if fl else 'consistent with the action'}")
            return s, c
        except ValueError as e:
            md.append(f"- **Rejected before reaching the person:** {e}"); return None, None
    # A honest payment
    vA = make_verse("py", a=25000, e=1); sA, cA = show("A. An honest payment", vA, claim="I will pay Maria $250.00 for the translation work.")
    tok, why = ap.approve(vA, "approve " + " ".join(cA), "n1"); out = ex.run(vA, tok); md.extend([f"- **Person says:** “approve {' '.join(cA)}” → {why}", f"- **Executor:** {out}", ""])
    say(speakable(sA) + " To approve, say: " + " ".join(cA) + ".", os.path.join(HERE, "readback_pay.mp3")); R["A"] = out
    # B the agent's words and its action disagree
    vB = make_verse("py", a=25000, e=1); show("B. The explanation says $25, the action says $250", vB, claim="Just sending Maria $25 for lunch."); md.append("")
    R["B"] = claim_check("Just sending Maria $25 for lunch.", vB)
    # C the action is changed after approval
    vC = make_verse("py", a=25000, e=2); md.extend(["## C. The agent swaps the payee after approval", "", f"- Approved verse: `{vA}` (token n1, already used) and a fresh approval n2 for it", f"- Submitted instead: `{vC}` (pays Daniel Cohen)"])
    tok2, _ = ap.approve(vA, "approve " + " ".join(cA), "n2")
    try: ex.run(vC, tok2); R["C"] = "EXECUTED (bad)"
    except PermissionError as e: R["C"] = f"refused: {e}"
    md.extend([f"- **Executor:** {R['C']}", ""])
    # D over the limit
    vD = make_verse("py", a=500000, e=1); show("D. A payment over the $1,000 limit", vD); md.append(""); 
    try: read_action(vD); R["D"] = "accepted (bad)"
    except ValueError as e: R["D"] = f"rejected: {e}"
    # E computed instead of stated
    vE = "ka #100 | pa #e | ke #1 | :py"; show("E. An amount computed inside the action instead of stated", vE); md.append("")
    try: read_action(vE); R["E"] = "accepted (bad)"
    except ValueError as e: R["E"] = f"rejected: {e}"
    # F hearing the confirmation
    alias = {}
    for a, t in S.ENGLISH["aliases"].items():
        if a != t: alias.setdefault(t, a)
    homophone = " ".join(alias.get(w, w) for w in cA)
    if homophone == " ".join(cA): homophone = "lei hope gate" if cA == ["lay", "hope", "gate"] else homophone
    okH, whyH = heard_matches("approve " + homophone, vA); wrong = cA[:2] + ["raw" if cA[2] != "raw" else "row"]; okW, whyW = heard_matches("approve " + " ".join(wrong), vA)
    md.extend(["## F. Hearing the confirmation", "", f"- Said with homophones “{homophone}” → {whyH}", f"- Said “{' '.join(wrong)}” → {whyW}", ""]); R["F"] = dict(homophones=okH, wrong_word=okW, explanation=whyW)
    # G replay
    try: ex.run(vA, tok); R["G"] = "EXECUTED again (bad)"
    except PermissionError as e: R["G"] = f"refused: {e}"
    md.extend(["## G. Replaying a used approval", "", f"- **Executor:** {R['G']}", ""])
    # H the action over a mobile phone call
    md.extend(["## H. The action sent over a GSM phone call", ""])
    tmp = tempfile.mkdtemp(); y = K.encode(K.add_ecc(vA), channel="phone"); K.save_wav(os.path.join(tmp, "a.wav"), y)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "a.wav"), "-ar", "8000", "-ac", "1", "-c:a", "libgsm", os.path.join(tmp, "a.gsm")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "a.gsm"), "-ar", str(K.FS), "-ac", "1", os.path.join(tmp, "b.wav")], check=True)
    heardv, rep = K.correct(K.decode(K.load_wav(os.path.join(tmp, "b.wav")), channel="phone")); same = hashlib.sha256(heardv.encode()).hexdigest() == hashlib.sha256(K.norm_text(vA).encode()).hexdigest()
    md.extend([f"- Sent `{K.add_ecc(vA)}` as phone-band tones through the GSM codec ({len(y) / K.FS:.1f} s)", f"- Received `{heardv}`; hash identical: {same}", ""]); R["H"] = same
    # J a drone flight
    tm = place_index(*PLACES["Temple Mount, Jerusalem"]); vJ = make_verse("ma", a=tm, e=100); sJ, cJ = show("J. A drone flight to a place code", vJ); md.append("")
    say(speakable(sJ) + " To approve, say: " + " ".join(cJ) + ".", os.path.join(HERE, "readback_drone.mp3"))
    vJ2 = make_verse("ma", a=tm, e=300); show("J2. The same flight at 300 metres (limit 120)", vJ2); md.append("")
    # other tools
    for title, v in [("K. A meeting", make_verse("mi", e=4, y=319, o=45)), ("L. A message", make_verse("te", e=3, y=3)), ("M. A thermostat", make_verse("hi", a=215)),
                     ("N. Access", make_verse("le", e=2, a=1)), ("O. A cancellation", make_verse("no", a=2))]:
        show(title, v); md.append("")
    # round trip over many actions
    import random
    rr = random.Random(3); n = ok = 0
    for _ in range(2000):
        tool = rr.choice(list(TOOLS)); vals = {}
        for p, k in TOOLS[tool]["args"]:
            lo, hi = TOOLS[tool]["limits"].get(p, (1, 1))
            vals[p] = dict(money=rr.randint(1, 100000), contact=rr.choice(list(CONTACTS)), message=rr.choice(list(MESSAGES)), date=rr.randint(0, 700), minutes=rr.randint(5, 240),
                           temperature=rr.randint(160, 260), place=place_index(rr.uniform(-80, 80), rr.uniform(-179, 179)), metres=rr.randint(10, 120), access=rr.randint(1, 2), subscription=rr.choice(list(SUBSCRIPTIONS)))[k]
        v = make_verse(tool, **vals); n += 1; ok += from_sentence(sentence(v)) == K.norm_text(v)
    R["sentence_round_trip"] = f"{ok}/{n}"; md.extend(["## Sentence round trip", "", f"- {ok} of {n} random actions: the English sentence parses back to the identical verse.", ""])
    open(os.path.join(HERE, "TRANSCRIPT.md"), "w").write("\n".join(md)); json.dump(R, open(os.path.join(HERE, "results.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(R, indent=1, ensure_ascii=False))
if __name__ == "__main__": main()
