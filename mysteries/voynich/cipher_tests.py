#!/usr/bin/env python3
"""Can a cipher turn a real Latin herbal into something with the Voynich herbal's numbers?
Plaintext: Macer Floridus (77 chapters, verse lines). Each cipher is applied, then the SAME measures are taken.
  T0 plaintext                         T1 letter substitution (one fixed letter -> letter mapping)
  T2 homophonic word code, 3 variants   T3 homophonic word code, 6 variants (each word type gets k codewords, chosen at random)
  T4 verbose syllable cipher (each 2-letter chunk -> one codeword: words become chunk-words)
  T5 nulls: a filler codeword inserted at random (12% of positions)
  T6 generator: each chapter is resampled word by word from its own word frequencies (topic kept, order and grammar gone)
Target (Voynich herbal): name rate 17%, immediate repetition 0.83% (and its ratio to the rate expected from word
frequencies alone), line-position MI 0.19, page-specific tokens 33%, about 6.8 words per line.
Usage: python3 cipher_tests.py <IT2a-n.txt> <macer html>"""
import collections, html, json, math, os, re, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from textmeasures import measures, words
VP, MP = sys.argv[1:3]; HERE = os.path.dirname(os.path.abspath(__file__)); R_ = random.Random(79)
t = open(MP, encoding="utf-8").read(); body = html.unescape(re.sub(r"<[^>]+>", "\n", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)))
L = [l.strip() for l in body.split("\n") if l.strip()]; st = next(k for k, l in enumerate(L) if l.startswith("I.") and "Artemisia" in l and k > 200); M = []
for l in L[st:]:
    if re.match(r"^[IVXLC]+\.\s+\S", l): M.append([]); continue
    if l.startswith("Toggle"): break
    if M and not re.fullmatch(r"\d+|\[|\]|recensere", l):
        ws = re.findall(r"[a-zà-ÿ]+", l.lower().replace("j", "i").replace("v", "u"))
        if ws: M[-1].append(ws)
M = [e for e in M if e]
V, herb = [], False
for l in open(VP, encoding="utf-8", errors="replace"):
    m = re.match(r"<(f\w+)>\s+<!(.*)>", l)
    if m: herb = "$I=H" in m.group(2); V.append([]) if herb else None; continue
    m = re.match(r"<(f\w+)\.(\d+),(.)(\w)(\w*)>\s+(.*)", l)
    if not m or not herb or m.group(4) != "P": continue
    tx = re.sub(r"<[^>]*>", "", m.group(6)); tx = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", tx); tx = re.sub(r"\{[^}]*\}", "", tx)
    ws = [w for w in re.split(r"[.,]", tx.replace("!", "").replace("%", "")) if re.fullmatch(r"[a-z]+", w)]
    if ws: V[-1].append(ws)
V = [e for e in V if sum(len(x) for x in e) >= 20]
def trunc(E, n=79):
    out = []
    for e in E:
        ls, k = [], 0
        for ln in e:
            if k >= n: break
            ls.append(ln[: n - k]); k += len(ln)
        out.append(ls)
    return out
def rep_ratio(E):
    ws = [w for e in E for ln in e for w in ln]; c = collections.Counter(ws); n = len(ws)
    obs = sum(1 for e in E for x in [words(e)] for a, b in zip(x, x[1:]) if a == b) / max(1, sum(len(words(e)) - 1 for e in E))
    exp = sum((v / n) ** 2 for v in c.values()); return round(obs / exp, 2)
def cw(): return "".join(R_.choice("qokchedyaiinlrst") for _ in range(R_.randint(3, 6)))
def apply(E, f): return [[f(ln) for ln in e] for e in E]
letters = "abcdefghiklmnopqrstuxyz"; perm = dict(zip(letters, R_.sample(letters, len(letters))))
T = {"T0 plaintext": M, "T1 letter substitution": apply(M, lambda ln: ["".join(perm.get(c, c) for c in w) for w in ln])}
for k in (3, 6):
    book = collections.defaultdict(lambda: [cw() for _ in range(k)])
    T[f"T{2 if k == 3 else 3} homophonic word code x{k}"] = apply(M, lambda ln, b=book: [R_.choice(b[w]) for w in ln])
chunk = collections.defaultdict(cw)
T["T4 verbose syllable cipher"] = apply(M, lambda ln: [chunk[w[i:i + 2]] for w in ln for i in range(0, len(w), 2)])
null = cw(); T["T5 nulls (12%)"] = apply(M, lambda ln: [x for w in ln for x in ([null, w] if R_.random() < 0.12 else [w])])
T["T6 generator (resample each chapter)"] = [[R_.choices(words(e), k=len(ln)) for ln in e] for e in M]
rows = {}
for name, E in list(T.items()) + [("VOYNICH herbal (target)", V)]:
    m = measures(trunc(E)); rows[name] = dict(name_rate=m["M3_entries_with_own_keyword"], repetition=m["M5_immediate_repetition_rate"], repetition_vs_frequency_expectation=rep_ratio(E),
                                                line_MI=m["M4_line_position_excess_MI"], page_specific=m["M2_share_of_tokens_entry_specific"], words_per_line=m["M1_words_per_line"])
tgt = rows["VOYNICH herbal (target)"]
for name, r in rows.items():
    r["distance_to_voynich"] = round(math.sqrt(((r["name_rate"] - tgt["name_rate"]) / 0.2) ** 2 + ((r["repetition"] - tgt["repetition"]) / 0.004) ** 2 + ((r["line_MI"] - tgt["line_MI"]) / 0.1) ** 2 + ((r["words_per_line"] - tgt["words_per_line"]) / 3) ** 2), 2)
json.dump(rows, open(os.path.join(HERE, "cipher_results.json"), "w"), indent=1)
print(f"{'':42s}{'names':>7s}{'repeat':>8s}{'rep/exp':>8s}{'lineMI':>8s}{'specif':>8s}{'w/line':>8s}{'dist':>7s}")
for n, r in rows.items(): print(f"{n:42s}{r['name_rate']:7.2f}{r['repetition']:8.4f}{r['repetition_vs_frequency_expectation']:8.2f}{r['line_MI']:8.3f}{r['page_specific']:8.3f}{r['words_per_line']:8.2f}{r['distance_to_voynich']:7.2f}")
