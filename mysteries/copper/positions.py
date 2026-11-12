#!/usr/bin/env python3
"""Round 79: WHERE in its entry does each Greek group sit? Hebrew transcription of 3Q15 from Hebrew Wikisource
(he.wikisource.org, "מגילות מדבר יהודה/3Q15 מגילת הנחושת", CC BY-SA), which writes the scroll's numeral signs as digits
and the Greek groups in Latin capitals. Its entry numbers differ from Milik's (Milik 1, 4, 6, 7, 10, 14, 17 = here 1, 4,
6, 7, 9, 12b, 15). Null: the group inserted at a random word boundary of its own entry."""
import json, os, numpy as np
AMT = ("ככרין", "ככ", "עשתות", "כסף", "כספ", "זהב", "כלין", "כדין")   # words that open the quantity clause
E = {
 "KEN (Milik 1)": "בחרובהא שבעמק עכור תחת המעלות הבואת למזרח אמות אריח ארבעין שדת כסף וכליה משקל ככרין שבעשרה KEN",
 "XAG (Milik 4)": "בתל של כחלת כלי דמע בלגין ואפורין הכל של דמע והאוצר השבוע ומעסר שני בפי גל פתחו בשולי האמא מן הצפון אמות שש עד ניקרת הטבילה XAG",
 "HN (Milik 6)": "בבור המלח שתחת המעלות ככרין HN 42",
 "ThE (Milik 7)": "במערת בין חמדה הישן ברובד השלישי עשתות זהב ששין וחמש ThE",
 "DI (Milik 10)": "בבור שנגד השער המזרחי רחוק אמות תשעסרא בו כלין ובמזקא שבו ככרין עסר DI",
 "TP (Milik 14)": "תחת הפנא האחרת המזרחית חפר אמות שש עסרה כספ ככ TP 40",
 "SK (Milik 17)": "בבור הג[דול שבכ]חלת בעמוד בצפונו ככ [...] SK",
}
G = {"KEN", "XAG", "HN", "ThE", "DI", "TP", "SK"}; rows = {}; p_end = p_amt = 1.0
for k, s in E.items():
    w = s.split(); gi = next(i for i, x in enumerate(w) if x in G); rest = w[:gi] + w[gi + 1:]
    nb = len(rest) + 1                                   # boundaries a group could occupy (start ... end)
    a0 = max((i for i, x in enumerate(rest) if x in AMT), default=None)   # last quantity word = the closing amount clause
    in_amt = a0 is not None and gi > a0
    where = "end of entry" if gi == len(w) - 1 else ("inside the amount (after the unit, before the number)" if in_amt else "elsewhere")
    k_amt = (nb - (a0 + 1)) if a0 is not None else 1   # boundaries from after the closing unit word to the end
    rows[k] = dict(position=where, word=gi + 1, of=len(w), boundaries=nb, amount_slot_boundaries=k_amt); p_end *= 1 / nb; p_amt *= k_amt / nb
print(json.dumps(rows, ensure_ascii=False, indent=1))
allamt = all(r["position"] != "elsewhere" for r in rows.values())
res = dict(entries=rows, all_seven_in_closing_amount_clause_or_end=allamt, p_all_in_amount_slot_by_chance=float(p_amt), n_at_very_end=sum(r["position"] == "end of entry" for r in rows.values()),
           reading="Every group is attached to the entry's closing quantity: five after it (or, with no quantity, at the end), two between the unit word and the numeral. None sits in the place description.")
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "positions_results.json"), "w"), ensure_ascii=False, indent=1)
print("all in closing amount clause / end:", allamt, " chance:", f"{p_amt:.2e}", " at very end:", res["n_at_very_end"])
