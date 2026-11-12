#!/usr/bin/env python3
"""Build the approval page: template.html + kanon.js + the tool, contact and skin tables -> index.html.
Also writes parity_cases.json: verses with the sentence and confirmation words Python produces, which the page's
JavaScript must reproduce exactly (checked by test_parity.js)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.dirname(HERE); L = os.path.dirname(A)
sys.path.insert(0, A); sys.path.insert(0, L); import approve as P, kanon as K, skins as S
tm = P.place_index(*P.PLACES["Temple Mount, Jerusalem"]); lc = P.place_index(*P.PLACES["Launch Complex 39A"])
PLACES = {str(tm): P.KINDS["place"][0](tm), str(lc): P.KINDS["place"][0](lc)}
SCEN = [
 dict(id="pay", label="Honest payment", verse=P.make_verse("py", a=25000, e=1), claim="I will pay Maria $250.00 for the translation work."),
 dict(id="lie", label="Explanation disagrees with the action", verse=P.make_verse("py", a=25000, e=1), claim="Just sending Maria $25 for lunch."),
 dict(id="drone", label="Drone flight to a place code", verse=P.make_verse("ma", a=tm, e=100), claim="Flying the survey drone over the site at 100 metres."),
 dict(id="meet", label="Book a meeting", verse=P.make_verse("mi", e=4, y=319, o=45), claim="Booked 45 minutes with Dr Okafor on 16 November."),
 dict(id="tell", label="Send a message", verse=P.make_verse("te", e=3, y=3), claim="Asking Svalbard for the pass 12 telemetry."),
 dict(id="heat", label="Thermostat", verse=P.make_verse("hi", a=215), claim="Setting the room to 21.5 degrees."),
 dict(id="let", label="Grant access", verse=P.make_verse("le", e=2, a=1), claim="Giving Daniel read access."),
 dict(id="no", label="Cancel a subscription", verse=P.make_verse("no", a=2), claim="Cancelling the imagery feed."),
 dict(id="over", label="Over the limit ($5,000)", verse=P.make_verse("py", a=500000, e=1), claim="Paying Maria's invoice."),
 dict(id="computed", label="Amount computed, not stated", verse="ka #100 | pa #e | ke #1 | :py", claim="Paying Maria the usual amount."),
 dict(id="high", label="Drone at 300 m (limit 120)", verse=P.make_verse("ma", a=tm, e=300), claim="Climbing higher for a better view."),
]
cases = []
for s in SCEN:
    try: cases.append(dict(verse=s["verse"], sentence=P.sentence(s["verse"]), words=P.confirmation(s["verse"]), seal=K.checksum_word(K.norm_text(s["verse"])), flags=P.claim_check(s["claim"], s["verse"])))
    except ValueError as e: cases.append(dict(verse=s["verse"], error=str(e)))
json.dump(cases, open(os.path.join(HERE, "parity_cases.json"), "w"), ensure_ascii=False, indent=1)
DATA = dict(tools={k: dict(args=v["args"], say=v["say"], limits=v["limits"]) for k, v in P.TOOLS.items()}, contacts=P.CONTACTS, messages=P.MESSAGES, subscriptions=P.SUBSCRIPTIONS,
            access=P.ACCESS, places=PLACES, conf=P.CONF, enc=S.EN_ENC, aliases=S.ENGLISH["aliases"], scenarios=SCEN, day0="2026-01-01")
js = open(os.path.join(L, "kanon.js"), encoding="utf-8").read()
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("/*__KANONJS__*/", js).replace("/*__DATA__*/null", json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/"))
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html); print("index.html", len(html) // 1024, "KB;", len(cases), "parity cases")
