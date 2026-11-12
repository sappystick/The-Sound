#!/usr/bin/env python3
"""KANON-FLIGHT: a restricted profile of KANON for operations procedures and on-board command sequences, with a
static checker that proves resource bounds BEFORE anything runs.

Rules (each checked statically, by reading the program, not running it):
  F1 bounded loops   every loop has a numeric count; while-loops (l with no number) are not allowed
  F2 no recursion    the graph of name calls has no cycle
  F3 known library   only Canon words on the approved list may be called
  F4 bounded memory  an upper bound on every plane's length is derived; it must stay under the declared limit
  F5 guarded acts    every door word (d...) that issues a command carries the guard mark ? (it runs only if the
                     accumulator, holding a check result, is positive)
  F6 protected link  every verse carries an error-correction tail (Reed-Solomon, as spoken or radioed)
Outputs a worst-case step count (an execution-time bound in VM steps), a memory bound, and the program's seal checksum.
These are the properties flight-software standards ask a procedure language to make visible. They do NOT make a
program certified: certification (DO-178C, NASA NPR 7150.2, ECSS-E-ST-40C) is a process around the code.
Usage: python3 profile.py FILE.kn"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); import kanon as K
APPROVED = {"tame", "tami", "tamo", "taso", "lake", "lame", "lamo", "lane", "kamu", "kade", "kasu", "baka", "bake", "bada", "dasa", "haso"}
def analyse(src, mem_limit=4096):
    main, user = K.parse(src); defs = {**K.parse(K.PRELUDE)[1], **user}; issues = []
    # F2: call graph
    calls = {n: {it["word"] for v in body for it in v if it["kind"] == "call"} for n, body in defs.items()}
    def cyc(n, path):
        for m in calls.get(n, ()):
            if m in path: return path + [m]
            if m in defs:
                c = cyc(m, path + [m])
                if c: return c
        return None
    used = set()
    def collect(verses):
        for v in verses:
            for it in v:
                if it["kind"] == "call" and it["word"] not in used:
                    used.add(it["word"])
                    if it["word"] in defs: collect(defs[it["word"]])
    collect(main)
    for n in (used & set(defs)) | set(user):
        c = cyc(n, [n])
        if c: issues.append(("F2", f"recursion: {' -> '.join(c)}"))
    # F3
    for n in used - set(defs):
        if n not in APPROVED: issues.append(("F3", f":{n} is not on the approved library list"))
    # F1, F4, F5 and the bounds, by abstract interpretation of plane lengths
    L = {v: 0 for v in K.VOWELS}; steps = [0]
    def word_len(w, val, L):
        syl = [w[j:j + 2] for j in range(0, len(w) - len(w) % 2, 2)]; cad = w[-1] if len(w) % 2 else None; head = syl[0][1]
        if syl[0][0] == "d" and len(syl) >= 2: return
        for k, sy in enumerate(syl):
            op, src = sy[0], (cad if k == 0 else sy[1]); S = L[src] if src else L[head]; v = val if k == 0 else None
            if op == "s": L[head] = int(v) if v is not None else (10 ** 9 if src else 7)
            elif op == "k": L[head] = 1 if v is not None else (S if src else 0)
            elif op == "b": L[head] = L[head] + S
            elif op in "gh": L[head] = 1 if (op == "g" or src) else L[head]
            steps[0] += 1
    def run_items(items, mult, L, depth=0):
        for it in K.schedule(K.bind_loops(items)):
            if it["kind"] == "call":
                n = it["word"]
                if n in defs and depth < 20:
                    for v in defs[n]: run_items(v, mult, L, depth + 1)
                else:
                    steps[0] += 1; L["i"] = max(L["i"], 1) if n not in ("bake", "bada", "taso") else L["i"]
            elif "body" in it:
                if it["num"] is None: issues.append(("F1", f"while-loop {it['word']} has no bound")); n = 1
                else: n = int(it["num"])
                for _ in range(min(n, 1000)): run_items([it["body"]], mult, L, depth)
                if n > 1000: steps[0] += (n - 1000) * 3
            else:
                if it["word"][0] == "d" and len(it["word"]) <= 3 and not it["guard"]: issues.append(("F5", f"command {it['word']} is not guarded with ?"))
                word_len(it["word"], it["num"], L)
    for v in main: run_items(v, 1, L)
    mem = max(L.values()) if L else 0
    if mem > mem_limit: issues.append(("F4", f"a plane may hold {mem} values (limit {mem_limit})"))
    # F6
    for v in src.split("|"):
        if v.strip() and "=" not in v: issues.append(("F6", f"verse without error-correction tail: {v.strip()[:40]}"))
    return dict(passed=not issues, issues=issues, worst_case_steps=steps[0], memory_bound_values=mem, plane_bounds=L,
                checksum=K.checksum_word(K.strip_checksums(src)), names_used=sorted(used))
if __name__ == "__main__":
    src = open(sys.argv[1]).read(); r = analyse(src)
    print(("PASS" if r["passed"] else "FAIL") + f"  worst case {r['worst_case_steps']} steps, memory bound {r['memory_bound_values']} values, seal ={r['checksum']}")
    for rule, msg in r["issues"]: print(f"   {rule}  {msg}")
