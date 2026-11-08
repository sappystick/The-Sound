#!/usr/bin/env python3
"""Round 5: smaller circles, breath shape, boundaries, variants, pairings, performance map, Hebrew Psalms.
Rules fixed before running; anything added later is labelled in the output.
Usage: python3 round5.py <sblgnt dir> <morphhb/wlc dir>
"""
import collections, itertools, json, os, random, re, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL, WLC = sys.argv[1], sys.argv[2]; rng = random.Random(21); out = {}
cache = {}
def gsyl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]
def load(fn):  # (ref, text_with_punct, lemma, syllables)
    rows = []
    for line in open(os.path.join(SBL, fn), encoding="utf-8"):
        p = line.split(); rows.append(((int(p[0][2:4]), int(p[0][4:])), p[3], p[6], gsyl(p[4])))
    return rows
JN, PHP, JN1 = load("64-Jn-morphgnt.txt"), load("71-Php-morphgnt.txt"), load("83-1Jn-morphgnt.txt")
def span(rows, a, b): return [r for r in rows if a <= r[0] <= b]
def vstart(ws, ref):
    acc = 0
    for r in ws:
        if r[0] == ref: return acc
        acc += r[3]
def tot(ws): return sum(r[3] for r in ws)

# ---------------------------------------------------------------- 1. smaller circles in the prologue
print("1. SMALLER CIRCLES: what sits at each eighth of the prologue")
P = span(JN, (1, 1), (1, 18)); T = tot(P); cum = 0; marks = {}
for r in P:
    for k in range(1, 8):
        if k not in marks and cum + r[3] > T * k / 8: marks[k] = r
    cum += r[3]
for k in range(1, 8):
    r = marks[k]; i = P.index(r)
    print(f"   {k}/8  {r[0][0]}:{r[0][1]:<3d} {' '.join(x[1] for x in P[max(0, i - 3): i + 6])}")
vs = sorted({r[0] for r in P}); starts = {v: vstart(P, v) / T for v in vs}
obs = abs(starts[(1, 6)] - .25) + abs(starts[(1, 15)] - .75)
pairs = [abs(starts[a] - .25) + abs(starts[b] - .75) for a, b in itertools.combinations(vs, 2)]
p1 = sum(x <= obs for x in pairs) / len(pairs)
print(f"   Baptist passages start at {starts[(1, 6)]:.3f} (1:6) and {starts[(1, 15)]:.3f} (1:15); "
      f"share of all verse-start pairs as close to the quarter points: {p1:.3f}")
out["circles"] = dict(eighths={k: f"{marks[k][0][0]}:{marks[k][0][1]}" for k in marks}, baptist=[round(starts[(1, 6)], 3), round(starts[(1, 15)], 3)], p=p1)

# ---------------------------------------------------------------- 2. breath shape
print("\n2. BREATH SHAPE (breath groups = text between punctuation marks of the edition)")
def breaths(ws):
    groups, cur = [], 0
    for r in ws:
        cur += r[3]
        if re.search(r"[,.·;:]$", r[1]): groups.append(cur); cur = 0
    if cur: groups.append(cur)
    return groups
def mirror_r(seq, c):
    k = min(c, len(seq) - c - 1)
    a = seq[c - k:c][::-1]; b = seq[c + 1:c + 1 + k]
    if k < 3: return None
    ma, mb = sum(a) / k, sum(b) / k
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b)); den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** .5
    return num / den if den else 0
for lab, ws, pv in (("John 1:1-18", P, ((1, 12), "ἔδωκεν")), ("Philippians 2:6-11", span(PHP, (2, 6), (2, 11)), ((2, 9), "διὸ"))):
    g = breaths(ws); cum = 0; idx = 0; acc = 0; gi = 0; pc = None
    # index of the breath group that begins at the pivot word
    for r in ws:
        if r[0] == pv[0] and r[1].startswith(pv[1].rstrip("·")): pc = gi; break
        acc += r[3]
        if re.search(r"[,.·;:]$", r[1]): gi += 1
    mean = sum(g) / len(g); rr = mirror_r(g, pc)
    sh = [mirror_r(rng.sample(g[:pc] + g[pc + 1:], len(g) - 1)[:pc] + [g[pc]] + rng.sample(g[:pc] + g[pc + 1:], len(g) - 1)[pc:], pc) for _ in range(1)]
    # proper permutation: shuffle all other groups, keep pivot position
    others = g[:pc] + g[pc + 1:]; cnt = 0; R = 20000
    for _ in range(R):
        o = others[:]; rng.shuffle(o); s = o[:pc] + [g[pc]] + o[pc:]
        v = mirror_r(s, pc); cnt += (v is not None and rr is not None and v >= rr)
    print(f"   {lab}: {len(g)} breaths, mean {mean:.1f} syllables (~{mean / 4:.1f} s); pivot opens breath #{pc + 1}; "
          f"lengths {g}\n      mirror correlation around the pivot breath r = {rr:.2f}; shuffled orders as mirrored: p = {cnt / R:.3f}")
    out[f"breath_{lab}"] = dict(lengths=g, pivot_index=pc, mirror_r=rr, p=cnt / R)

# ---------------------------------------------------------------- 3. boundaries
print("\n3. BOUNDARIES: offset of a known pivot from the centre under each proposed edge (% of unit)")
TESTS = [("Good shepherd, pivot 10:11", JN, (10, 11), [((10, 1), (10, 18)), ((10, 1), (10, 21)), ((9, 39), (10, 21)), ((9, 41), (10, 21)), ((10, 1), (10, 42))]),
         ("Lazarus, pivot 11:25", JN, (11, 25), [((11, 1), (11, 44)), ((11, 1), (11, 46)), ((11, 1), (11, 53)), ((11, 17), (11, 44))]),
         ("Pilate, pivot 19:1", JN, (19, 1), [((18, 28), (19, 16)), ((18, 28), (19, 22)), ((18, 33), (19, 16))]),
         ("Samaritan woman, pivot 4:21", JN, (4, 21), [((4, 1), (4, 42)), ((4, 4), (4, 42)), ((4, 1), (4, 26)), ((4, 7), (4, 42))]),
         ("Tabernacles, pivot 8:12", JN, (8, 12), [((7, 1), (8, 59)), ((7, 1), (10, 21)), ((7, 37), (8, 59))]),
         ("Philippians hymn, pivot 2:9", PHP, (2, 9), [((2, 6), (2, 11)), ((2, 5), (2, 11)), ((2, 1), (2, 11))])]
out["boundaries"] = {}
for lab, bk, pv, opts in TESTS:
    res = []
    for a, b in opts:
        ws = span(bk, a, b); f = vstart(ws, pv) / tot(ws); res.append((f"{a[0]}:{a[1]}-{b[0]}:{b[1]}", round((f - .5) * 100, 2)))
    best = min(res, key=lambda x: abs(x[1]))
    print(f"   {lab:30s} " + "  ".join(f"{s} {o:+.1f}%" for s, o in res) + f"   -> closest: {best[0]}")
    out["boundaries"][lab] = res

# ---------------------------------------------------------------- 4. disputed readings in the prologue
print("\n4. DISPUTED READINGS: centre offset (syllables) when one variant replaces the SBLGNT reading")
base = vstart(P, (1, 12)) + sum(r[3] for r in P if r[0] == (1, 12) and False)
# pivot = 'edoken' inside 1:12
acc = 0
for r in P:
    if r[0] == (1, 12) and r[1].startswith("ἔδωκεν"): break
    acc += r[3]
before, total = acc, T
VAR = [("1:3 'oude hen' -> 'ouden' (P66, Sinaiticus)", "before", gsyl("οὐδέν") - gsyl("οὐδὲ") - gsyl("ἕν")),
       ("1:4 'en' (was) -> 'estin' (is) (Sinaiticus, Bezae)", "before", gsyl("ἐστίν") - gsyl("ἦν")),
       ("1:13 'hoi ... egennethesan' -> singular 'hos ... egennethe' (Latin witnesses)", "after", gsyl("ἐγεννήθη") - gsyl("ἐγεννήθησαν")),
       ("1:16 'hoti' -> 'kai' (Byzantine)", "after", gsyl("καί") - gsyl("ὅτι")),
       ("1:18 'monogenes theos' -> 'ho monogenes theos' (P75)", "after", gsyl("ὁ")),
       ("1:18 'monogenes theos' -> 'ho monogenes huios' (Byzantine)", "after", gsyl("ὁ") + gsyl("υἱός") - gsyl("θεός"))]
off0 = before - total / 2
print(f"   SBLGNT: {off0:+.1f} of {total}")
out["variants"] = []
for lab, side, d in VAR:
    nb, nt = before + (d if side == "before" else 0), total + d; off = nb - nt / 2
    print(f"   {lab:72s} {d:+d} syl {side:6s} -> offset {off:+.1f}")
    out["variants"].append((lab, d, side, off))

# ---------------------------------------------------------------- 5. pairings between centres
print("\n5. PAIRINGS: rare words shared by the centres of different units")
UN = [("Prologue", JN, (1, 1), (1, 18)), ("First witnesses", JN, (1, 19), (1, 51)), ("Cana", JN, (2, 1), (2, 11)),
      ("Nicodemus", JN, (3, 1), (3, 21)), ("Samaritan woman", JN, (4, 1), (4, 42)), ("Bethesda", JN, (5, 1), (5, 47)),
      ("Bread of life", JN, (6, 22), (6, 71)), ("Tabernacles", JN, (7, 1), (8, 59)), ("Blind man", JN, (9, 1), (9, 41)),
      ("Shepherd", JN, (10, 1), (10, 21)), ("Lazarus", JN, (11, 1), (11, 44)), ("Footwashing", JN, (13, 1), (13, 30)),
      ("Farewell", JN, (13, 31), (17, 26)), ("Pilate", JN, (18, 28), (19, 16)), ("Resurrection", JN, (20, 1), (20, 31)),
      ("1 John", JN1, (1, 1), (5, 21))]
freq = collections.Counter(r[2] for r in JN + JN1)
def window(ws, ref):
    vs_ = sorted({r[0] for r in ws}); i = vs_.index(ref); keep = set(vs_[max(0, i - 1): i + 2])
    return {r[2] for r in ws if r[0] in keep and freq[r[2]] <= 6}
def centre(ws):
    T_ = tot(ws); acc = 0
    for r in ws:
        if acc + r[3] > T_ / 2: return r[0]
        acc += r[3]
units = [(lab, span(bk, a, b)) for lab, bk, a, b in UN]
cw = [(lab, window(ws, centre(ws))) for lab, ws in units]
shared = [(a[0], b[0], sorted(a[1] & b[1])) for a, b in itertools.combinations(cw, 2) if a[1] & b[1]]
real = sum(len(s[2]) for s in shared)
for s in shared: print(f"   {s[0]} + {s[1]}: {s[2]}")
cnt = 0; R = 2000
for _ in range(R):
    ws_ = [window(ws, rng.choice(sorted({r[0] for r in ws}))) for _, ws in units]
    cnt += sum(len(a & b) for a, b in itertools.combinations(ws_, 2)) >= real
print(f"   total rare words shared between centres: {real}; random positions with as many: p = {cnt / R:.3f}")
out["pairings"] = dict(shared=shared, total=real, p=cnt / R)

# ---------------------------------------------------------------- 6. performance map
print("\n6. PERFORMANCE MAP of John at 4 syllables per second")
G = tot(JN); out["performance"] = []
def mmss(s): return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}"
for lab, bk, a, b in UN:
    if bk is not JN: continue
    ws = span(bk, a, b); st = vstart(JN, ws[0][0]) / 4; c = centre(ws); ct = vstart(JN, c) / 4; du = tot(ws) / 4
    print(f"   {lab:16s} starts {mmss(st)}  lasts {du / 60:5.1f} min  centre {c[0]}:{c[1]} at {mmss(ct)}")
    out["performance"].append((lab, mmss(st), round(du / 60, 1), f"{c[0]}:{c[1]}", mmss(ct)))
print(f"   whole Gospel: {G} syllables = {G / 4 / 3600:.2f} hours; spoken midpoint at {mmss(G / 8)}")

# ---------------------------------------------------------------- 7. Hebrew Psalms
print("\n7. HEBREW PSALMS: position of the traditionally central line, in Hebrew syllables")
xml = open(os.path.join(WLC, "Ps.xml"), encoding="utf-8").read()
def psalm(n):
    vv = []
    for m in re.finditer(rf'<verse osisID="Ps\.{n}\.(\d+)">(.*?)</verse>', xml, re.S):
        for w in re.findall(r"<w [^>]*>([^<]+)</w>", m.group(2)):
            w = w.replace("/", "")
            try: s = sum(len(x) for x in E.parse_hebrew(w, "second-temple"))
            except Exception: s = 1
            vv.append((int(m.group(1)), w, max(1, s)))
    return vv
for n, pv, word, note in ((23, 4, "כִּֽי", "'for you are with me' (23:4)"), (92, 9, "וְאַתָּ֥ה", "'but you, LORD, are on high forever' (92:9 Hebrew = 92:8 English)")):
    ws = psalm(n)
    for skip_title in (False, True):
        w2 = [x for x in ws if not (skip_title and x[0] == 1)] if n == 92 else ws
        if skip_title and n != 92: continue
        acc = 0; Tt = sum(x[2] for x in w2)
        for x in w2:
            if x[0] == pv and unicodedata.normalize("NFD", x[1]).startswith(unicodedata.normalize("NFD", word)[:3]): break
            acc += x[2]
        lab = f"Psalm {n}" + (" without title verse" if skip_title else "")
        print(f"   {lab:28s} {note}: starts at {acc / Tt:.3f} ({acc - Tt / 2:+.1f} of {Tt} syllables)")
        out[f"psalm_{n}_{skip_title}"] = dict(position=round(acc / Tt, 4), offset=acc - Tt / 2, total=Tt)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "round5_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
