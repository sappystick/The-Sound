#!/usr/bin/env python3
"""Build the instruction dataset (CSV + JSON) and the lineage map of practice threads."""
import collections, csv, json, os
from records import R
from words import W

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")
os.makedirs(OUT, exist_ok=True)
ORDER = ["Egypt", "Greco-Roman mysteries", "Hebrew Bible", "Second Temple Judaism (Qumran, Philo, Josephus)", "Mishnah (Second Temple practice)", "Early church", "Islam", "Living tradition"]
recs = sorted(R, key=lambda d: (d["year"], d["id"]))
assert len({d["id"] for d in recs}) == len(recs), "duplicate ids"
fields = list(recs[0].keys())
with open(os.path.join(OUT, "instructions.csv"), "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=fields); wr.writeheader(); wr.writerows(recs)
json.dump(recs, open(os.path.join(OUT, "instructions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "words.csv"), "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(W[0].keys())); wr.writeheader(); wr.writerows(W)

# ---- lineage: for each thread, which traditions attest it, earliest record in each
threads = collections.defaultdict(lambda: collections.defaultdict(list))
for d in recs:
    for t in [x.strip() for x in d["threads"].split(";") if x.strip()]:
        threads[t][d["tradition"]].append(d)
rows = []
for t, by in threads.items():
    present = [o for o in ORDER if o in by]
    chain = " -> ".join(f"{o.split(' (')[0]} ({by[o][0]['ref'] if len(by[o][0]['ref']) < 30 else by[o][0]['id']}, {by[o][0]['source'].split(',')[0].split(' (')[0]})" for o in present)
    rows.append(dict(thread=t, traditions=len(present), spans="/".join(o.split(" ")[0] for o in present),
                     records=sum(len(v) for v in by.values()), chain=chain))
rows.sort(key=lambda r: (-r["traditions"], -r["records"]))
with open(os.path.join(OUT, "lineage.csv"), "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)

# ---- field coverage summary
cov = {k: sum(bool(d[k]) for d in recs) for k in ("time", "place", "direction", "repetition", "posture", "voice", "tools", "oils", "plants", "ingestants", "materials")}
by_trad = collections.Counter(d["tradition"] for d in recs)
by_conf = collections.Counter(d["confidence"] for d in recs)
print(f"{len(recs)} records; {len(W)} words; {len(rows)} threads")
print("by tradition:", dict(by_trad)); print("by confidence:", dict(by_conf)); print("field coverage:", cov)
print("\nthreads attested in >= 3 of 5 traditions:")
for r_ in rows:
    if r_["traditions"] >= 3: print(f"  {r_['thread']:20s} {r_['spans']:45s} n={r_['records']}")
json.dump(dict(counts=dict(by_trad), confidence=dict(by_conf), coverage=cov, lineage=rows),
          open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
