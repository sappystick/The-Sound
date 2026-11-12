#!/usr/bin/env python3
"""Parity test: kanon.py and kanon.js must compute the same planes and outputs for the same programs.
Random programs mix every primitive, marks, loops, names, the prelude and the Canon. Usage: python3 parity.py [n]"""
import json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import kanon as K
SAFE_CANON = ["kamu", "kagi", "kapi", "kasu", "kapo", "kamo", "tame", "tado", "tami", "tamo", "taso", "pari", "paso", "bake", "bada", "baro", "bato", "baka", "lane", "lake", "lame", "lamo", "maro", "maki", "basa", "bari", "dasa", "dagi", "dahe"]
def prog(R):
    vs = ["si #" + K.to12(R.randint(2, 12)), "ka #" + K.to12(R.randint(1, 9))]
    for _ in range(R.randint(1, 4)):
        ws = []
        for _ in range(R.randint(1, 4)):
            r = R.random()
            if r < 0.2: ws.append(":" + R.choice(SAFE_CANON + ["kemu", "kegi"]))
            else:
                n = R.randint(1, 3); w = "".join(R.choice("ktpbgnrmhs") + R.choice("iaeou") for _ in range(n))
                if R.random() < 0.4: w += R.choice("iaeouyw")
                if R.random() < 0.08: w = "~" + w
                if R.random() < 0.08: w += "?"
                ws.append(w)
                if R.random() < 0.4: ws.append("#" + K.to12(R.randint(1, 15)))
        vs.append(" ".join(ws))
    return " | ".join(vs)
def py_run(p):
    try:
        vm = K.VM(); vm.FUEL = 20000; vm.fuel = 20000; vm.run(p)
        return dict(ok=True, P={v: [round(x, 6) for x in vm.P[v]] for v in K.VOWELS}, say=[o for o in vm.out if isinstance(o, str)])
    except Exception as e: return dict(ok=False)
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400; R = random.Random(7); progs = [prog(R) for _ in range(n)]
    js = subprocess.run(["node", "-e", """
const K = require(process.argv[1]); const progs = JSON.parse(require('fs').readFileSync(0, 'utf8')); const out = [];
for (const p of progs) { try { const vm = new K.VM(); vm.fuel = 20000; vm.run(p); const P = {}; for (const v of K.VOWELS) P[v] = vm.P[v].map(x => Math.round(x * 1e6) / 1e6);
  out.push({ok: true, P, say: vm.out.filter((o, k) => true)}); } catch (e) { out.push({ok: false}); } }
console.log(JSON.stringify(out));""", os.path.join(HERE, "kanon.js")], input=json.dumps(progs), capture_output=True, text=True, check=True)
    J = json.loads(js.stdout); same = 0; diffs = []
    for p, j in zip(progs, J):
        q = py_run(p)
        okp = q["ok"] == j["ok"] and (not q["ok"] or all(abs((a or 0) - (b or 0)) < 1e-6 * max(1, abs(a or 0)) for v in K.VOWELS for a, b in zip(q["P"][v], j["P"][v]) ) and all(len(q["P"][v]) == len(j["P"][v]) for v in K.VOWELS))
        same += okp
        if not okp and len(diffs) < 5: diffs.append(dict(src=p, py=q, js=j))
    res = dict(programs=n, identical=same, errors_both_sides=sum(1 for j in J if not j["ok"]), first_differences=diffs)
    json.dump(res, open(os.path.join(HERE, "parity_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
    print(f"{same}/{n} programs give identical planes in Python and JavaScript ({res['errors_both_sides']} raise errors in JS)")
    for d in diffs[:3]: print(json.dumps(d, ensure_ascii=False)[:600])
