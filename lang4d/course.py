#!/usr/bin/env python3
"""The one-night course for KANON: 31 steps in the three watches of the night (evening, midnight, morning).

Built on the project's Echo Ladder method (rounds 34-35): exactly one new element per step, and every example uses
only what has already been introduced. That rule is CHECKED here, not assumed. Every example is run by both
interpreters (kanon.py and kanon.js), and every exercise has a reference answer that is run and checked too.

Memory aids are ancient and real:
  - the planetary week: the seven vowels are the seven days (i Sunday/Sun, a Monday/Moon, o Tuesday/Mars, e Wednesday/
    Mercury, u Thursday/Jupiter, y Friday/Venus, w Saturday/Saturn), the order every weekday name still keeps;
  - the calendar palace: the twelve consonants are the twelve months, in the 4 x 3 grid of the seasons (rows) - a
    method-of-loci palace with one room per operation;
  - ring composition: a verse is read from both ends toward the middle, as the scribes built their chiasms;
  - chant: every program is also a melody; the course audio is the codec itself.
Writes course/course.json and course/NN.mp3. Usage: python3 course.py"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import kanon as K
OUT = os.path.join(HERE, "course"); os.makedirs(OUT, exist_ok=True)
SAY = {"a": "ah", "e": "eh", "y": "ay", "i": "ee", "o": "oh", "u": "oo", "w": "aw"}
DIGSAY = dict(zip(K.DIGITS, ["km", "tm", "pm", "bm", "dm", "gm", "lm", "mm", "nm", "rm", "sm", "hm"]))
MARKSAY = {"|": "(breathe)", "!": "tsk", "~": "fff", "?": "vvv", ":": "shh", "=": "zzz"}
def pronounce(src):
    out = []
    for tk in re.findall(r"#[0-9te]+|\||::|[:!?~=]|[a-z]+", src):
        if tk.startswith("#"): out.append("-".join(DIGSAY[c] for c in tk[1:]))
        elif tk in MARKSAY: out.append(MARKSAY[tk])
        elif tk == "::": out.append("shh-shh")
        else:
            syl = [tk[j:j + 2] for j in range(0, len(tk) - len(tk) % 2, 2)]
            out.append("-".join(s[0] + SAY[s[1]] for s in syl) + (("-" + SAY[tk[-1]]) if len(tk) % 2 else ""))
    return " ".join(out)
W1, W2, W3 = "Evening watch: the sounds", "Midnight watch: order", "Morning watch: names and the Canon"
STEPS = [
 (W1, "The middle string", "k i # 0-9", "i is Sunday, the Sun, the middle string: the accumulator where results gather. k is the first month (Nisan) and means keep.",
  "ki #5", "Keep the number 5 in plane i. A number always follows its word after #.", "Keep 7 in i.", "ki #7", ("i", [7.0])),
 (W1, "The door", "d", "d is Av, the month of the door: what is in a plane goes out through d.",
  "ki #5 di", "Two words in a verse run in the order written. di sends i out.", "Send 9 out of the door.", "ki #9 di", ("out", ["9"])),
 (W1, "Stream and breath", "s |", "s is Shevat, the stream: count from one. | is a breath, the end of a verse.",
  "si #7 | di", "si #7 fills i with 1 to 7. The breath ends the verse; the next verse sends i out.", "Count 1 to 4 and send it out.", "si #4 | di", ("out", ["1 2 3 4"])),
 (W1, "Counting in twelves", "# t e", "Numbers are base twelve: t is ten, e is eleven, #10 is twelve. Twelve stones, twelve months, twelve digits.",
  "ki #10 | di", "#10 means one twelve and no units: 12.", "Keep 23 (one twelve and eleven).", "ki #1e", ("i", [23.0])),
 (W1, "The Moon plane, and the closing vowel", "a", "a is Monday, the Moon: the input plane. A lone vowel at the end of a word names the plane it draws from.",
  "sa #5 | kia | di", "sa #5 fills a; kia keeps into i a copy of a (the closing a is the source).", "Fill a with 1 to 3 and copy it into i.", "sa #3 | kia", ("i", [1.0, 2.0, 3.0])),
 (W1, "Gather", "g", "g is Elul, the month of gathering the harvest: g adds a plane up.",
  "sa #5 | gia | di", "gia gathers a into i: 1+2+3+4+5 = 15.", "Gather 1 to 10 into i.", "sa #t | gia", ("i", [55.0])),
 (W1, "Test", "t", "t is Iyyar, the test: keep only what is above a number.",
  "si #7 | ti #3 | di", "ti #3 keeps the values of i above 3.", "Keep the values of 1 to 9 that are above 6.", "si #9 | ti #6", ("i", [7.0, 8.0, 9.0])),
 (W1, "Negate", "n", "n is Kislev, the month of the longest nights: it subtracts, or with no number turns a value to its negative.",
  "si #5 | ni #1 | di", "ni #1 takes 1 from every value of i.", "Take 2 from each of 1 to 4.", "si #4 | ni #2", ("i", [-1.0, 0.0, 1.0, 2.0])),
 (W1, "Project", "p", "p is Sivan, the projection: multiply by a number, or by a string's ratio (pia = by 4:3, the fourth).",
  "si #3 | pi #2 | di", "pi #2 doubles every value of i.", "Triple 1 to 3.", "si #3 | pi #3", ("i", [3.0, 6.0, 9.0])),
 (W1, "Retro", "r", "r is Tevet, turning back: reverse the order.",
  "si #5 | ri | di", "ri reverses i.", "Make 4 3 2 1.", "si #4 | ri", ("i", [4.0, 3.0, 2.0, 1.0])),
 (W1, "Bind", "b", "b is Tammuz, binding: join another plane onto the end.",
  "si #3 | sa #2 | bia | di", "bia binds a onto the end of i: 1 2 3 1 2.", "Join 1 to 2 (in a) onto 1 to 3 (in i).", "si #3 | sa #2 | bia", ("i", [1.0, 2.0, 3.0, 1.0, 2.0])),
 (W1, "Morph", "m", "m is Cheshvan: morph. With a number it wraps values round like a clock (the remainder).",
  "si #9 | mi #4 | di", "mi #4 replaces each value by its remainder after dividing by 4.", "Show 1 to 7 on a clock of 3.", "si #7 | mi #3", ("i", [1.0, 2.0, 0.0, 1.0, 2.0, 0.0, 1.0])),
 (W1, "Hold", "h", "h is Adar, the last month: hold your breath and count. hia counts the values of a.",
  "sa #9 | hia | di", "hia puts the number of values in a into i.", "Count the values of 1 to 11 in a.", "sa #e | hia", ("i", [11.0])),
 (W1, "The other five days", "e y o u w", "e Wednesday (Mercury, scratch) · y Friday (Venus, pair) · o Tuesday (Mars, output) · u Thursday (Jupiter, store) · w Saturday (Saturn, archive).",
  "so #4 | sw #2 | kio | biw | di", "Seven planes now: fill o and w, copy o into i, bind w on.", "Fill u with 1 to 6 and gather it into i.", "su #6 | giu", ("i", [21.0])),
 (W2, "The ring", "(ring rule)", "A verse is read like a chiasm: first with last, second with second-last, and the centre word last of all.",
  "sa #7 gia ta #3 | di", "Ring order runs sa, then ta (the outer pair), then gia (the centre): 4+5+6+7 = 22. Written sa #7 ta #3 gia, the same words give 28.", "Make the centre gather run before the test: get 28.", "sa #7 ta #3 gia", ("i", [28.0])),
 (W2, "Spelling a sequence", "(ring spelling)", "To run A B C D in that order, write A C D B: begin and end together, then the middle.",
  "si #4 ri di pi #2", "Written si ri di pi, it runs si, pi, ri, di: 1 to 4, doubled, reversed, out: 8 6 4 2.", "Run: stream 1 to 3, then reverse, then double.", "si #3 pi #2 ri", ("i", [6.0, 4.0, 2.0])),
 (W2, "A word is a pipeline", "(syllable order)", "Inside a word, the syllables act one after another on the word's own plane. Change their order and the pipeline changes.",
  "si #7 | ka #3 | pinata | di", "pi (×1), na (subtract a's 3), ta (keep above 3): only 4 is left. pitana keeps first, then subtracts: 1 2 3 4.", "Get 1 2 3 4 from the same start.", "si #7 | ka #3 | pitana", ("i", [1.0, 2.0, 3.0, 4.0])),
 (W2, "Songs", "(d-words)", "A d-word of two or more syllables sings its own vowel line. demorini is e-o-i-i, the vowels of ego eimi, 'I am'.",
  "demorini", "No plane changes: the word is a melody, Mercury, Mars, Sun, Sun.", "Sing a word whose vowels are a-i-a.", "daka", ("events", 1)),
 (W2, "Urgent", "!", "! (tsk) puts a word ahead of the ring.",
  "si #3 di ki! #9", "Without !, ring order would run si, ki, di and say 9. With ki! first, si then di say 1 2 3.", "Make 9 come out instead.", "si #3 di ki #9", ("out", ["9"])),
 (W2, "Guard", "?", "? (vvv) makes a word ask first: it runs only if i is positive.",
  "ki #0 | ka #3 | kia? | di", "i is 0, so kia? is skipped and 0 goes out.", "Change one number so that 3 comes out.", "ki #1 | ka #3 | kia? | di", ("out", ["3"])),
 (W2, "Loops", "l", "l is Tishri, the turning of the year: repeat the next word.",
  "si #2 | li #3 pi #2 | di", "li #3 repeats pi #2 three times: 1 2 becomes 8 16.", "Double 1 to 2 five times.", "si #2 | li #5 pi #2", ("i", [32.0, 64.0])),
 (W2, "Sandbox", "~", "~ (fff) wraps a word: if it fails, it is skipped and noted, and the program carries on.",
  "ki #4 | ~si #100000 | di", "A stream of 248,832 values (#100000 is twelve to the fifth power) is over the limit; the sandbox skips it, so 4 goes out.", "Remove the sandbox and see the error, then put it back.", "ki #4 | ~si #100000 | di", ("out", ["4"])),
 (W3, "Calling a name", ":", ": (shh) calls a name. The Canon is the built-in library; :tame is the mean, :dasa says i.",
  "si #5 | :tame | :dasa", "The mean of 1 to 5 is 3.", "Say the maximum of 1 to 8.", "si #8 | :tamo | :dasa", ("out", ["8"])),
 (W3, "Defining a name, and while", "::", "::name ... :: defines a word of your own. l with no number repeats while its plane is positive.",
  "::kosu bogou nu #1 :: | ku #5 | ko #0 | lu :kosu | kio | di", "While u is positive: add u to o, take 1 from u. 5+4+3+2+1 = 15.", "Sum 7 down to 1 the same way.", "::kosu bogou nu #1 :: | ku #7 | ko #0 | lu :kosu | kio", ("i", [28.0])),
 (W3, "The prelude", "(prelude)", "Some names are written in KANON itself: :kemu multiplies by repeated addition, :kegi is Euclid's algorithm, :kehi the factorial.",
  "ki #7 | ka #6 | :kemu | :dasa", "7 × 6 = 42, using only bind, gather, negate and a while-loop.", "Find the greatest common divisor of 84 and 36.", "ki #70 | ka #30 | :kegi", ("i", [12.0])),
 (W3, "Number and letters", "(Canon: k n d)", "The Canon is laid out on the grid: k-names are number, t statistics, p geometry, b sequences, d doors, l logic, m music, r time, h seals.",
  "ki #29 | :kapi | :dasa", "The primes up to 33. :dagi says numbers as Greek numerals, :dahe as Hebrew numerals.", "Say 23 as a Greek numeral.", "ki #1e | :dagi", ("out", ["κγʹ"])),
 (W3, "Geometry and music", "(Canon: p m)", "Star polygons, room resonances and string ratios are words of the language.",
  "ki #8 | ka #3 | :paso | :dasa", "The star {8/3}: visit every third of eight points: 0 3 6 1 4 7 2 5.", "List the first seven resonances of a cube room 10 metres on a side.", "ki #t | :pamo", ("i", [17.15, 24.25, 29.7, 34.3, 38.35, 42.01, 48.51])),
 (W3, "Time", "(Canon: r)", "Days count from 1 January 2000. :rado gives the planetary weekday (0 Sunday ... 6 Saturday); :raso the seven planetary longitudes.",
  "ki #0 | :rado | :dasa", "1 January 2000 was a Saturday: 6, Saturn's day, the plane w.", "Which weekday was day 1?", "ki #1 | :rado", ("i", [0.0])),
 (W3, "Speaking a program", "=", "= (zzz) carries error correction: five short parity words that repair any two misheard sounds in the verse and flag three or four.",
  "sa #7 gia ta #3 =" , "Every verse can end with its parity words; the decoder repairs small mistakes and flags larger ones. In tests on spoken programs, none came back wrong without a flag.", "Run the ring program again.", "sa #7 gia ta #3", ("i", [22.0])),
 (W3, "Your own Euclid", "(all)", "Write the algorithm yourself: while a is positive, e = i mod a, i = a, a = e. Spell the body in ring order.",
  "::kebo kei kia kae mea :: | ki #70 | ka #30 | la :kebo | :dasa", "kei kia kae mea runs as kei, mea, kia, kae (ring order). gcd(84, 36) = 12.", "Find gcd(105, 45) with your own name.", "::kebo kei kia kae mea :: | ki #89 | ka #39 | la :kebo", ("i", [15.0])),
]
LETTER_STEP = {}
def introduced(upto):
    s = set()
    for st in STEPS[:upto + 1]:
        for g in st[2].split():
            if len(g) == 1 or g in ("0-9", "::"): s.add(g)
    return s
def check_ladder():
    """Each example uses only letters and marks introduced up to its own step."""
    problems = []
    letters_known, digits_known, marks_known = set(), set("0123456789") - set("0123456789"), set()
    for n, st in enumerate(STEPS):
        for g in st[2].split():
            if g == "0-9": digits_known |= set("0123456789")
            elif g in ("t", "e") and n == 3: digits_known |= {g}
            elif g in "|!~?:=#" or g == "::": marks_known |= set(g)
            elif len(g) == 1: letters_known.add(g)
        ex = st[4].rstrip("=").strip()
        for tk in re.findall(r"#[0-9te]+|::|[|!?~:=]|[a-z]+", ex):
            if tk.startswith("#"):
                bad = set(tk[1:]) - digits_known
                if bad: problems.append((n + 1, tk, "digits " + "".join(sorted(bad))))
            elif tk in "|!?~:=" or tk == "::":
                if set(tk) - marks_known: problems.append((n + 1, tk, "mark"))
            else:
                if re.findall(r"(?<=:)" + tk, ex) or (":" + tk) in ex or ("::" + tk) in ex: continue   # names are free
                bad = set(tk) - letters_known
                if bad: problems.append((n + 1, tk, "letters " + "".join(sorted(bad))))
    return problems
def run_js(progs):
    js = subprocess.run(["node", "-e", """
const K = require(process.argv[1]); const progs = JSON.parse(require('fs').readFileSync(0, 'utf8'));
console.log(JSON.stringify(progs.map(p => { try { const vm = new K.VM().run(p); return {i: vm.P.i, out: vm.out, events: vm.events.length}; } catch (e) { return {error: e.message}; } })));""",
        os.path.join(HERE, "kanon.js")], input=json.dumps(progs), capture_output=True, text=True, check=True)
    return json.loads(js.stdout)
def main():
    probs = check_ladder(); steps = []; progs = []
    for n, (watch, title, new, aid, ex, expl, task, ans, check) in enumerate(STEPS, 1):
        exs = ex.rstrip("=").strip()
        vm = K.VM().run(exs); vma = K.VM().run(ans); kind, want = check
        got = vma.P["i"] if kind == "i" else ([str(o) if isinstance(o, str) else " ".join(f"{x:g}" for x in o) for o in vma.out] if kind == "out" else len(vma.events))
        if kind == "i": ok = len(got) == len(want) and all(abs(a - b) < 0.01 for a, b in zip(got, want))
        else: ok = got == want
        assert ok, (n, title, got, want)
        shown = exs + (" " + K.ecc_tail(exs) if ex.endswith("=") else "")
        steps.append(dict(n=n, watch=watch, title=title, new=new, aid=aid, example=shown, say=pronounce(shown), explain=expl, task=task, answer=ans, check=dict(kind=kind, want=want),
                          result=dict(i=vm.P["i"], out=[o if isinstance(o, str) else " ".join(f"{x:g}" for x in o) for o in vm.out], song=len(vm.events)), audio=f"{n:02d}.mp3"))
        progs += [exs, ans]
        y = K.encode(shown); w = os.path.join(OUT, f"{n:02d}.wav"); K.save_wav(w, y)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-b:a", "48k", "-ac", "1", w[:-4] + ".mp3"], check=True); os.remove(w)
    J = run_js(progs); P = [K.VM().run(p) for p in progs]
    parity = sum(1 for j, p in zip(J, P) if "error" not in j and all(abs(a - b) < 1e-9 for a, b in zip(j["i"], p.P["i"])) and len(j["i"]) == len(p.P["i"]))
    meta = dict(steps=len(STEPS), watches=[W1, W2, W3], ladder_problems=probs, js_parity=f"{parity}/{len(progs)}",
                glyphs=dict(vowels=7, consonants=12, marks=7, digits=12), pronounce=dict(vowels=SAY, digits=DIGSAY, marks=MARKSAY),
                canon={k: d for k, (d, _) in K.CANON.items()}, prelude=K.PRELUDE.strip())
    json.dump(dict(meta=meta, steps=steps), open(os.path.join(OUT, "course.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(STEPS)} steps; ladder problems: {probs or 'none'}; JavaScript parity on every example and answer: {meta['js_parity']}")
if __name__ == "__main__": main()
