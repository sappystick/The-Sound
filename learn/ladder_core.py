#!/usr/bin/env python3
"""The Echo Ladder core: language-agnostic. A unit is a list of dictionary forms (lemmas).
ladder(units, steps) -> list of (unit index, [new lemmas], lemmas known so far)
curve(units, order)  -> after each step: lemmas known, share of all word tokens recognised, units fully readable."""
import collections, math
def ladder(units, steps, min_len=2, max_len=9):
    freq = collections.Counter(x for u in units for x in u); known, last, used, seen, out = set(), {}, set(), set(), []
    for step in range(steps):
        best = None
        for i, L in enumerate(units):
            if i in used or tuple(L) in seen or not (min_len <= len(L) <= max_len): continue
            new = [x for x in dict.fromkeys(L) if x not in known]
            if not new: continue
            kn = [x for x in set(L) if x in known]
            score = ((0 if len(new) <= 2 else -len(new)) if not known else -len(new), sum(math.log(freq[x]) for x in new) / len(new) + 0.3 * (sum(math.log(1 + step - last[x]) for x in kn) / len(kn) if kn else 0) - 0.02 * len(L))
            if best is None or score > best[0]: best = (score, i, new)
        if best is None: break
        _, i, new = best; used.add(i); seen.add(tuple(units[i]))
        for x in set(units[i]): last[x] = step
        known |= set(new); out.append((i, new, len(known)))
    return out
def curve(units, order):
    freq = collections.Counter(x for u in units for x in u); total = sum(freq.values()); known = set(); res = []
    for n, (i, new, k) in enumerate(order, 1):
        known |= set(new); res.append(dict(step=n, lemmas=len(known), tokens=round(sum(freq[x] for x in known) / total, 4), clauses=sum(all(x in known for x in u) for u in units)))
    return res
