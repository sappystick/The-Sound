"""Round 39, cipher lens: runs the four parts and applies Benjamini-Hochberg across every test.

  1. atbash_scan.py      ATBASH / ALBAM discovery scan, random-cipher nulls (Hebrew Bible)
  2. acrostic_scan.py    alphabetic acrostics (Hebrew, LXX, NT), Greek name acrostics, Sibyl 8
  3. msline_scan.py      first/last letters of manuscript lines of John (P66, P75, 01, 03)
  4. els_calibration.py  equidistant letter sequences with controls (Genesis)

Usage: python3 ciphers.py <repo_root> [--reuse]
  --reuse: read the part results_*.json already in this folder instead of recomputing.
Writes results.json next to this script. Runtime about 5 minutes. Seeds fixed in each part.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def bh(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        prev = min(prev, ps[i] * m / rank)
        adj[i] = prev
    return adj


def main(root, reuse):
    texts = os.path.join(root, "sources", "texts")
    parts = {
        "atbash": os.path.join(HERE, "results_atbash.json"),
        "acrostic": os.path.join(HERE, "results_acrostic.json"),
        "msline": os.path.join(HERE, "results_msline.json"),
        "els": os.path.join(HERE, "results_els.json"),
    }
    if not reuse:
        import atbash_scan, acrostic_scan, msline_scan, els_calibration
        atbash_scan.main(os.path.join(texts, "morphhb", "wlc"), parts["atbash"])
        acrostic_scan.main(texts, parts["acrostic"])
        msline_scan.main(os.path.join(texts, "cntr", "class 1"), os.path.join(texts, "sblgnt"),
                         parts["msline"])
        els_calibration.main(os.path.join(texts, "morphhb", "wlc"), parts["els"])
    res = {}
    tests = []
    for k, p in parts.items():
        with open(p, encoding="utf-8") as f:
            res[k] = json.load(f)
        for t in res[k].pop("tests"):
            t["part"] = k
            tests.append(t)
    q_all = bh([t["p"] for t in tests])
    fams = sorted({t["family"] for t in tests})
    for t, q in zip(tests, q_all):
        t["q_round"] = float(q)
    for fam in fams:
        idx = [i for i, t in enumerate(tests) if t["family"] == fam]
        qf = bh([tests[i]["p"] for i in idx])
        for i, q in zip(idx, qf):
            tests[i]["q_family"] = float(q)
    res["multiple_testing"] = dict(
        n_tests=len(tests),
        n_by_family={f: sum(1 for t in tests if t["family"] == f) for f in fams},
        significant_round_q05=[t for t in tests if t["q_round"] <= 0.05],
        significant_round_q05_not_known=[t for t in tests if t["q_round"] <= 0.05 and not t.get("known")],
        smallest_p_not_known=sorted([t for t in tests if not t.get("known")], key=lambda t: t["p"])[:15],
    )
    res["all_tests"] = tests
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    mt = res["multiple_testing"]
    print("tests", mt["n_tests"], mt["n_by_family"])
    print("significant (round BH q<=0.05):", len(mt["significant_round_q05"]),
          "of which not known:", len(mt["significant_round_q05_not_known"]))
    for t in mt["significant_round_q05_not_known"]:
        print("  ", t["test"], t["p"], t["q_round"])


if __name__ == "__main__":
    main(sys.argv[1], "--reuse" in sys.argv)
