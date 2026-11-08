#!/usr/bin/env python3
"""Test: do some kinds of instruction survive era-to-era handovers better than others?

Hypothesis (stated before running): TIME and REPETITION survive most often; DIRECTION survives
but changes target; MATERIALS are the most often dropped or changed.

Method (fixed before looking):
  * Main chain of eras: Egypt -> Hebrew Bible -> Second Temple (Qumran/Philo/Josephus + Mishnah)
    -> Early church -> Living tradition.  Side branches (Greco-Roman mysteries, Islam) excluded.
  * For every practice thread present in two consecutive chain eras (a "handover"), and every
    field type, the field's values are normalised to category tokens (below).
  * A field counts for a handover only if the earlier era has a value.  Outcome:
        kept    = later era shares at least one token
        changed = later era has values, none shared
        absent  = later era has no value for that field
  * Survival rate per field type = kept / (kept + changed + absent); and, conditional on the
    later era having a value at all, kept / (kept + changed).
  * Significance: Fisher exact test, TIME+REPETITION vs MATERIALS; and a permutation test that
    shuffles field-type labels across all handover outcomes (10,000 shuffles).
"""
import collections, itertools, json, os, random, re
from records import R

CHAIN = [["Egypt"], ["Hebrew Bible"], ["Second Temple Judaism (Qumran, Philo, Josephus)", "Mishnah (Second Temple practice)"],
         ["Early church"], ["Living tradition"]]
ERA = {t: i for i, ts in enumerate(CHAIN) for t in ts}
VOCAB = {
    "time": {"dawn": r"dawn|sunrise|daybreak|first light|morning|cockcrow|before sunrise", "evening": r"evening|twilight|sunset|lamp-lighting|tenth hour",
             "night": r"night|midnight", "noon": r"noon|midday|sixth|fifth hour", "hours": r"hour|times daily|twice|3rd|9th",
             "weekly": r"sabbath|sunday|lord's day|wednesday|friday|weekday", "full_moon": r"full moon|14th|15th",
             "new_moon": r"new moon|months", "new_year": r"new year", "festival": r"feast|festival|tabernacles|passover|easter|epiphany|khoiak|kiahk|atonement"},
    # word boundaries added after an automatic-coding run exposed matches inside words ('ten' in 'often')
    "repetition": {n: rf"(?<!\d){n}(?!\d)|\b(?:{w})\b" for n, w in (("2", "twice"), ("3", "three|thrice"), ("4", "four"), ("7", "seven"),
                                                         ("12", "twelve"), ("10", "ten"), ("9", "nine"), ("13", "thirteen"), ("15", "fifteen"))},
    "direction": {"east": r"\beast", "west": r"\bwest", "sanctuary": r"(?:toward|towards|facing|looking|into)\s+(?:the\s+)?(?:jerusalem|holy of holies|sanctuary|temple|tent)|^toward",
                  "four": r"\bfour\b", "stars": r"\bstars?\b", "mecca": r"mecca", "none": r"no required"},
    "posture": {"prostrate": r"prostrat|kiss|face down|bow", "kneel": r"kneel", "stand": r"stand", "hands": r"hands? (raised|spread|outstretched|stretched)|arms raised|raised",
                "procession": r"procession|walking|march", "dance": r"dance", "recline": r"reclin", "turn": r"turn"},
    "voice": {"hymn": r"hymn|sung|song|sing|psalm|praise|chant", "antiphon": r"antiphon|altern|response|two choirs|call and",
              "spoken": r"spoken|recit|read|declar|formula|prayer", "name": r"name", "silence": r"silen", "instrument": r"trumpet|horn|blast|tekiah"},
    "materials": {"water": r"water|immers|bath", "oil": r"oil|ointment|chrism|myron", "incense": r"incense|frankincense|myrrh|resin|kyphi|censer",
                  "linen": r"linen|flax", "blood": r"blood", "wine": r"wine", "bread": r"bread|loaves|flour|grain|barley|wheat|meal",
                  "milk_honey": r"milk|honey", "fire": r"fire|lamp|torch|coals|candle", "plants": r"hyssop|willow|palm|myrtle|cedar|citron|herb|mint",
                  "metal": r"gold|silver|bronze", "instrument": r"trumpet|horn|cymbal|harp|lyre|sistr|drum|tambourine|flute|strings",
                  "earth": r"\bearth|natron|\bclay\b|\bash(?:es)?\b|\bsand\b", "salt": r"\bsalt\b"},
    "place": {"inner": r"inner|holy of holies|sanctuary|shrine|tomb|grotto|cave", "threshold": r"door|gate|threshold|entrance",
              "water_place": r"river|pool|siloam|sea|lake", "steps": r"step|stair", "altar": r"altar", "home": r"home|house|upper room|household",
              "roof": r"roof", "court": r"court"},
}
FIELDS = {"time": ["time"], "repetition": ["repetition"], "direction": ["direction"], "posture": ["posture"], "voice": ["voice"],
          "place": ["place"], "materials": ["materials", "tools", "oils", "plants", "ingestants"]}


def tokens(rec, ftype):
    text = " ".join(rec[f] for f in FIELDS[ftype]).lower()
    return {tok for tok, pat in VOCAB[ftype].items() if re.search(pat, text)}


bythread = collections.defaultdict(lambda: collections.defaultdict(list))
for d in R:
    if d["tradition"] in ERA:
        for t in [x.strip() for x in d["threads"].split(";") if x.strip()]:
            bythread[t][ERA[d["tradition"]]].append(d)

outcomes = []  # (thread, era_a, era_b, ftype, outcome, a_tokens, b_tokens)
for t, eras in bythread.items():
    present = sorted(eras)
    for a, b in zip(present, present[1:]):
        for ft in FIELDS:
            ta = set().union(*(tokens(x, ft) for x in eras[a])); tb = set().union(*(tokens(x, ft) for x in eras[b]))
            if not ta: continue
            o = "kept" if ta & tb else ("changed" if tb else "absent")
            outcomes.append((t, a, b, ft, o, sorted(ta), sorted(tb)))

summary = {}
print(f"{len(outcomes)} field-handovers across {len({(o[0], o[1], o[2]) for o in outcomes})} thread-handovers\n")
print(f"{'field':11s} {'n':>4s} {'kept':>5s} {'changed':>8s} {'absent':>7s} {'survival':>9s} {'kept|present':>13s}")
for ft in FIELDS:
    c = collections.Counter(o[4] for o in outcomes if o[3] == ft); n = sum(c.values())
    if not n: continue
    s1 = c["kept"] / n; s2 = c["kept"] / max(1, c["kept"] + c["changed"])
    summary[ft] = dict(n=n, kept=c["kept"], changed=c["changed"], absent=c["absent"], survival=round(s1, 3), kept_given_present=round(s2, 3))
    print(f"{ft:11s} {n:4d} {c['kept']:5d} {c['changed']:8d} {c['absent']:7d} {s1:9.2f} {s2:13.2f}")

# Fisher exact: (time+repetition) vs materials, kept vs not kept
from scipy.stats import fisher_exact
def kn(fts): c = collections.Counter(o[4] == "kept" for o in outcomes if o[3] in fts); return c[True], c[False]
k1, n1 = kn({"time", "repetition"}); k2, n2 = kn({"materials"})
OR, p = fisher_exact([[k1, n1], [k2, n2]], alternative="greater")
print(f"\nTIME+REPETITION kept {k1}/{k1 + n1}  vs  MATERIALS kept {k2}/{k2 + n2}: odds ratio {OR:.2f}, one-sided Fisher p = {p:.3f}")
# permutation: shuffle field labels
rng = random.Random(7); labels = [o[3] for o in outcomes]; kept = [o[4] == "kept" for o in outcomes]
def diff(lab):
    a = [k for k, l in zip(kept, lab) if l in ("time", "repetition")]; b = [k for k, l in zip(kept, lab) if l == "materials"]
    return (sum(a) / len(a)) - (sum(b) / len(b))
real = diff(labels); cnt = 0
for _ in range(10000):
    rng.shuffle(labels); cnt += diff(labels) >= real
print(f"permutation test (10,000 label shuffles): difference {real:+.2f}, p = {cnt / 10000:.3f}")

# direction: what changed?
print("\ndirection handovers:")
for o in outcomes:
    if o[3] == "direction": print(f"  {o[0]:14s} era {o[1]}->{o[2]}: {o[5]} -> {o[6]}  [{o[4]}]")
json.dump(dict(summary=summary, fisher=dict(time_rep=[k1, k1 + n1], materials=[k2, k2 + n2], odds_ratio=OR, p=p),
               permutation_p=cnt / 10000, outcomes=outcomes),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "handover_test.json"), "w"), indent=1, ensure_ascii=False)

# ---- robustness (added after the first run, labelled as such) ----------------------------
# 1) reverse one-sided test; 2) per-token survival (share of the earlier era's categories that
#    reappear later), which removes the advantage of fields with many categories.
OR2, p2 = fisher_exact([[k2, n2], [k1, n1]], alternative="greater")
print(f"\n[robustness] MATERIALS kept more than TIME+REPETITION: one-sided Fisher p = {p2:.4f}")
print(f"[robustness] per-token survival (share of earlier categories that reappear, given a later value):")
pt = {}
for ft in FIELDS:
    vals = [len(set(o[5]) & set(o[6])) / len(o[5]) for o in outcomes if o[3] == ft and o[6]]
    if vals: pt[ft] = round(sum(vals) / len(vals), 2); print(f"   {ft:11s} {pt[ft]:.2f}  (n={len(vals)})")
# per-category survival within materials
cat = collections.Counter(); catk = collections.Counter()
for o in outcomes:
    if o[3] == "materials" and o[6]:
        for tok in o[5]: cat[tok] += 1; catk[tok] += tok in o[6]
print("[robustness] materials by category (kept / handovers where it was present earlier):")
for tok, n in cat.most_common(): print(f"   {tok:11s} {catk[tok]}/{n}")
