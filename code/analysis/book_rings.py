#!/usr/bin/env python3
"""Book-scale rings elsewhere (angle 2): do a book's key repeated units balance around its spoken
midpoint, as John's seven 'I am' sayings do?  Same method and null as john_book.py.
  Mark: the three Passion predictions (8:31, 9:31, 10:33)
  Matthew: the five great discourses, start verses (5:1, 10:5, 13:1, 18:1, 24:3)
  Revelation: the opening of each septet (seals 6:1, trumpets 8:7, bowls 16:2) - clustered, reported only
"""
import json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import engine as E
SBL = sys.argv[1]; cache = {}
def nsyl(w):
    if w not in cache: cache[w] = max(1, len(E.parse_greek(w, "koine")[0]))
    return cache[w]
def book(fn):
    vs, t = {}, 0
    for line in open(os.path.join(SBL, fn), encoding="utf-8"):
        p = line.split(); k = (int(p[0][2:4]), int(p[0][4:])); vs.setdefault(k, t); t += nsyl(p[4])
    return vs, t
def sym_err(ps):
    k = len(ps); return sum(abs((ps[i] - .5) + (ps[k - 1 - i] - .5)) for i in range(k // 2)) + (abs(ps[k // 2] - .5) if k % 2 else 0)
rng = random.Random(5); out = {}
for name, fn, items in (("Mark: Passion predictions", "62-Mk-morphgnt.txt", [(8, 31), (9, 31), (10, 33)]),
                        ("Matthew: five discourses", "61-Mt-morphgnt.txt", [(5, 1), (10, 5), (13, 1), (18, 1), (24, 3)]),
                        ("Revelation: septets", "87-Re-morphgnt.txt", [(6, 1), (8, 7), (16, 2)])):
    vs, N = book(fn); ps = [vs[k] / N for k in items]; mid = min(vs, key=lambda k: abs(vs[k] - N / 2))
    e = sym_err(ps); p = sum(sym_err(sorted(rng.random() for _ in ps)) <= e for _ in range(100000)) / 100000
    out[name] = dict(midpoint=f"{mid[0]}:{mid[1]}", positions=[(f"{c}:{v}", round(x, 3)) for (c, v), x in zip(items, ps)], ring_error=round(e, 3), p=p)
    print(f"{name}: midpoint {mid[0]}:{mid[1]}; positions " + ", ".join(f"{c}:{v}={x:.3f}" for (c, v), x in zip(items, ps)) + f"; ring p = {p:.3f}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "book_rings_results.json"), "w"), indent=1)
