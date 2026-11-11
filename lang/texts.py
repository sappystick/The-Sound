#!/usr/bin/env python3
"""Sala texts, written in the authoring notation (English keys + grammar words) and rendered by sala.render().
Each entry: (notation, intended English). Running this file renders, parses and checks every sentence, measures
length against English and Greek, and writes lang/texts.json."""
import json, os, re
import sala as S
HERE = os.path.dirname(os.path.abspath(__file__))
JOHN = [  # John 1:1-5 and 1:14
 ("word sa ta exist na begin .", "In the beginning was the Word,"),
 ("ye word sa ta exist wi god .", "and the Word was with God,"),
 ("ye word sa ta god .", "and the Word was God."),
 ("si sa ta exist wi god na begin .", "He was in the beginning with God."),
 ("thing all sa ta become ho si .", "All things came to be through him,"),
 ("ye thing sa ta mo become wi mo si .", "and without him nothing came to be."),
 ("life sa ta exist na si .", "In him was life,"),
 ("ye life sa ta light le person lu .", "and the life was the light of people."),
 ("ye light sa light na dark .", "The light shines in the darkness,"),
 ("ye dark sa ta mo win ke si .", "and the darkness did not overcome it."),
 ("ye word sa ta become flesh .", "And the Word became flesh"),
 ("ye si sa ta stay wi mi lu .", "and dwelt among us,"),
 ("ye mi lu sa ta see ke light big le si .", "and we saw his glory."),
]
DIALOGUE = [
 ("peace . name le yu sa what ka", "A: Peace. What is your name?"),
 ("peace . name le mi sa ha Mira . ye yu ka", "B: Peace. My name is Mira. And you?"),
 ("mi sa ha Tomas . yu sa come ho place what ka", "A: I am Tomas. Where do you come from?"),
 ("mi sa come ho ha Kenya . sa give ke water pe mi pu", "B: I come from Kenya. Please give me water."),
 ("yes . water sa exist na place this hi", "A: Yes. There is water here! (gladly)"),
 ("thanks . mi sa mo know ke way pe house le friend le mi he", "B: Thanks. I do not know the way to my friend's house. (sadly)"),
 ("mi sa so help ke yu . sa come wi mi pu", "A: I can help you. Please come with me."),
 ("good . mi lu sa go now hi", "B: Good. We go now! (gladly)"),
]
MACHINE = [
 ("sa open ke door pu", "Please open the door."),
 ("water sa exist na house ka", "Is there water in the house?"),
 ("ku fire sa exist na house te sa send ke word pe mi wa", "If there is fire in the house, send word to me! (warning)"),
 ("sa show ke book #3 pe mi pu", "Please show me book 3."),
 ("sa find ke person ti si sa know ke way tu pu", "Please find a person who knows the way."),
 ("sa make ke light small na night pu", "Please make the light small at night."),
]
STARTER = [  # short sentences for the course; they repeat the core words in new combinations
 ("mi sa person .", "I am a person."), ("yu sa person .", "You are a person."), ("mi sa see ke yu .", "I see you."), ("yu sa see ke mi .", "You see me."),
 ("mi sa see ke water .", "I see water."), ("si sa see ke house .", "He or she sees the house."), ("house sa big .", "The house is big."), ("house sa mo big .", "The house is not big."),
 ("water sa good .", "Water is good."), ("mi sa want ke water .", "I want water."), ("yu sa want ke what ka", "What do you want?"), ("mi sa want ke food .", "I want food."),
 ("mi sa eat ke bread .", "I eat bread."), ("si sa eat ke fish .", "He or she eats fish."), ("mi sa ta eat ke bread .", "I ate bread."), ("mi sa ya eat ke fish .", "I will eat fish."),
 ("mi sa go pe house .", "I go to the house."), ("yu sa go pe house ka", "Do you go to the house?"), ("si sa ta go pe house .", "He or she went to the house."), ("mi lu sa go pe house big .", "We go to the big house."),
 ("mi sa come ho house .", "I come from the house."), ("friend le mi sa come .", "My friend comes."), ("friend le mi sa good .", "My friend is good."), ("friend le yu sa see ke mi .", "Your friend sees me."),
 ("mi sa know ke yu .", "I know you."), ("mi sa mo know ke si .", "I do not know him or her."), ("yu sa know ke way ka", "Do you know the way?"), ("mi sa know ke way pe house .", "I know the way to the house."),
 ("mi sa give ke water pe yu .", "I give you water."), ("sa give ke bread pe mi pu", "Please give me bread."), ("si sa ta give ke book pe mi .", "He or she gave me a book."), ("mi sa have ke book .", "I have a book."),
 ("mi sa read ke book .", "I read the book."), ("book sa good hi", "The book is good! (gladly)"), ("mi sa love ke yu hi", "I love you! (gladly)"), ("mother le mi sa love ke mi .", "My mother loves me."),
 ("father le mi sa work na house .", "My father works at the house."), ("child sa sleep na night .", "The child sleeps at night."), ("sun sa light na day .", "The sun shines in the day."), ("moon sa light na night .", "The moon shines at night."),
 ("mi sa so see ke star lu na night .", "I can see the stars at night."), ("mi sa mu go now .", "I must go now."), ("yu sa mu eat .", "You must eat."), ("mi sa so help ke yu .", "I can help you."),
 ("sa help ke mi pu", "Please help me."), ("sa come pu", "Please come."), ("sa wait pu", "Please wait."), ("sa open ke door pu", "Please open the door."),
 ("door sa open .", "The door is open."), ("sa close ke door pu", "Please close the door."), ("fire sa hot .", "Fire is hot."), ("water sa cold .", "The water is cold."),
 ("mi sa feel ke joy .", "I feel joy."), ("mi sa feel ke fear he", "I feel fear. (sadly)"), ("yu sa good ka", "Are you well?"), ("mi sa good . ye yu ka", "I am well. And you?"),
 ("this sa what ka", "What is this?"), ("this sa bread .", "This is bread."), ("that sa house le mi .", "That is my house."), ("word this sa true .", "This word is true."),
 ("mi sa say ke truth .", "I say the truth."), ("mi sa hear ke voice le yu .", "I hear your voice."), ("mi sa believe ke yu .", "I believe you."), ("mi sa learn ke word new .", "I learn a new word."),
 ("word sa life .", "The word is life."), ("life sa good hi", "Life is good! (gladly)"), ("peace sa exist na world ka", "Is there peace in the world?"), ("person all sa want ke peace .", "All people want peace."),
 ("ku yu sa come te mi sa give ke food pe yu .", "If you come, I give you food."), ("mi sa want ke water pa water sa mo exist .", "I want water, but there is no water."), ("mi sa eat ye yu sa drink .", "I eat and you drink."), ("thanks . peace .", "Thanks. Peace."),
]
SETS = dict(john=JOHN, dialogue=DIALOGUE, machine=MACHINE, starter=STARTER)
if __name__ == "__main__":
    out = {}; nsyl = lambda t: sum(len(w) // 2 if S.is_cv(w.lower()) else max(1, len(re.findall(r"[aeiouy]+", w.lower()))) for w in re.findall(r"[A-Za-z]+", t))
    en_syl = lambda t: sum(max(1, len(re.findall(r"[aeiouy]+", re.sub(r"e\b", "", w.lower())))) for w in re.findall(r"[A-Za-z]+", t))
    for name, items in SETS.items():
        rows = []
        for notation, eng in items:
            text = S.render(notation); p = S.parse(text); b = S.to_bytes(text); assert S.from_bytes(b).replace(".", "").split() == re.sub(r"[.?!;]", "", text).split(), (text, S.from_bytes(b))
            rows.append(dict(sala=text, english=eng, literal=" ".join(S.english(s) for s in p), call=[S.to_call(s) for s in p], bytes=len(b), hex=b.hex(), syllables=nsyl(text), en_syllables=en_syl(re.sub(r"^[AB]: |\(.*?\)", "", eng))))
        out[name] = rows; ws = sum(len(r["sala"].split()) for r in rows)
        print(f"{name}: {len(rows)} items, {ws} words; Sala {sum(r['syllables'] for r in rows)} syllables vs English {sum(r['en_syllables'] for r in rows)}; {sum(r['bytes'] for r in rows)} bytes packed vs {sum(len(r['sala'].encode()) for r in rows)} as text")
    used = {t for items in SETS.values() for n, _ in items for t in n.split() if t in S.MEAN}; print(len(used), "of", len(S.MEAN), "roots used in these texts;", len({t for items in SETS.values() for n, _ in items for t in n.split() if t in S.PARTICLES}), "grammar words used")
    for r in out["john"][:5] + out["dialogue"][:3] + out["machine"][:3]: print("  ", r["sala"], "|", r["literal"], "|", r["call"][0])
    json.dump(out, open(os.path.join(HERE, "texts.json"), "w"), ensure_ascii=False, indent=1)
