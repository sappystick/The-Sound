"""Ritual instruction records, Egypt -> Israel -> Mishnah -> early church -> living practice.

Each record is ONE written instruction (paraphrased in English by the compiler; no modern
translation is reproduced).  Fields:
  id, tradition, year (approx., negative = BCE; used for ordering), source, ref,
  rite, instruction, time, place, direction, repetition, posture, voice,
  tools, oils, plants, ingestants, materials, elements, threads, confidence, note
confidence:  text      = stated directly in the cited passage
             scholarly = from the standard scholarly description/edition of the source
             verify    = a detail that should be checked against an edition before citing
"""

R = []


def r(id, tradition, year, source, ref, rite, instruction, *, time="", place="", direction="", repetition="",
      posture="", voice="", tools="", oils="", plants="", ingestants="", materials="", elements="", threads="",
      confidence="text", note="", power=""):
    R.append(dict(id=id, tradition=tradition, year=year, source=source, ref=ref, rite=rite, instruction=instruction,
                  time=time, place=place, direction=direction, repetition=repetition, posture=posture, voice=voice,
                  tools=tools, oils=oils, plants=plants, ingestants=ingestants, materials=materials,
                  elements=elements, threads=threads, power=power, confidence=confidence, note=note))


EG, HB, MI, CH, LV = "Egypt", "Hebrew Bible", "Mishnah (Second Temple practice)", "Early church", "Living tradition"
ST = "Second Temple Judaism (Qumran, Philo, Josephus)"
GR = "Greco-Roman mysteries"
IS = "Islam"
# power categories (what the SOURCE says makes the rite work):
#   name, word, blood, water, breath, light, time, place, substance, purity, inner, tradition, divine_will

# ------------------------------------------------------------------ EGYPT
r("EG01", EG, -1290, "Daily Temple Ritual (Seti I chapels, Abydos; Papyrus Berlin 3055)", "episodes 1-10",
  "Daily temple ritual", "At daybreak the priest kindles fire, takes up the censer, breaks the clay seal and draws the bolt of the shrine, and 'reveals the face of the god'.",
  time="dawn", place="sanctuary (inner shrine)", tools="censer arm; seal; bolt", materials="fire; clay seal",
  elements="fire; light", threads="dawn; incense; inner_room", confidence="scholarly",
  note="Moret 1902; R. David, Religious Ritual at Abydos (1973).")
r("EG02", EG, -1290, "Daily Temple Ritual", "episodes on 'kissing the earth'",
  "Daily temple ritual", "On seeing the god the priest prostrates himself, 'smelling/kissing the earth' (sn-tA), and sings a hymn of adoration.",
  time="dawn", place="sanctuary", posture="prostration", voice="sung hymn of adoration", threads="prostration; dawn; sung_praise",
  confidence="scholarly")
r("EG03", EG, -1290, "Daily Temple Ritual", "closing episodes",
  "Daily temple ritual", "The god's image is purified with water and natron, anointed with md.t ointment, clothed in linen cloths of four colours, given eye paint, and offered food; incense throughout.",
  time="morning", place="sanctuary", tools="nemset jars; censer", oils="md.t ointment; incense (sntr)",
  materials="water; natron; linen", ingestants="food offering", elements="water; earth (natron); fire",
  threads="washing; anointing; incense; linen; bread_offering", confidence="scholarly")
r("EG04", EG, -1290, "Daily Temple Ritual", "final episode ('bringing the foot')",
  "Daily temple ritual", "The priest withdraws backwards, sweeping away his footprints with a broom, and the shrine is closed.",
  time="morning", place="sanctuary threshold", posture="walking backwards", tools="broom (hdn plant)", plants="hdn plant broom",
  threads="threshold; inner_room", confidence="scholarly")
r("EG05", EG, -430, "Herodotus, Histories", "2.37",
  "Priestly purity", "Egyptian priests wash in cold water twice each day and twice each night, shave the whole body every other day, and wear only linen and papyrus sandals.",
  time="twice by day, twice by night", repetition="2+2 daily", tools="razor", materials="cold water; linen; papyrus",
  plants="flax (linen); papyrus", elements="water", threads="washing; shaving; linen; hours", confidence="text")
r("EG06", EG, -1300, "Book of the Dead", "spell 125, rubric",
  "Judgement / declaration of innocence", "The declaration of innocence is to be said by one who is clean and pure, dressed in fresh clothes, shod in white sandals, painted with eye paint and anointed with myrrh, after offering cattle, fowl and incense.",
  posture="standing before the judges", voice="spoken declaration ('I have not ...') x42", repetition="42 denials",
  oils="myrrh ointment; incense", materials="white sandals; fresh linen; eye paint", ingestants="cattle and fowl offered",
  threads="purity_declaration; anointing; incense; linen", confidence="scholarly", note="Faulkner / Allen translations.")
r("EG07", EG, -1300, "Book of the Dead", "spell 15 ('Adoring Ra when he rises in the eastern horizon')",
  "Solar hymn", "A hymn of adoration addressed to the sun at its rising; vignettes show the worshipper with both arms raised (dwA).",
  time="sunrise", direction="east", posture="arms raised", voice="hymn", elements="light; fire", threads="dawn; facing_east; raised_hands; sung_praise",
  confidence="scholarly")
r("EG08", EG, -1300, "Book of the Dead", "spell 137A rubric",
  "Kindling the torches", "Four torches are kindled for the deceased and later quenched in four clay basins of milk; the spell is to be said by the light of the torches.",
  time="night", repetition="4 torches / 4 basins", tools="torches; clay basins", ingestants="milk (of a white cow)", materials="cloth wicks; fat; clay",
  elements="fire; light", threads="lamp_light; four_directions", confidence="verify", note="Check rubric wording in Lucarelli / Quirke editions.")
r("EG09", EG, -2350, "Pyramid Texts and ritual papyri", "rubric formula Dd mdw ... zp 4",
  "Recitation formula", "Spells open with 'Words to be spoken' and many end 'four times', one recitation toward each cardinal direction.",
  repetition="4 times", voice="spoken formula", direction="four cardinal directions", threads="repetition; four_directions; rubric",
  confidence="scholarly")
r("EG10", EG, -1300, "Opening of the Mouth ritual (tombs of Rekhmire, Seti I)", "scenes 1-75",
  "Opening of the Mouth", "The sem-priest in a leopard skin touches the mouth and eyes of the statue or mummy with the adze (and other blades) so it can breathe, see and eat; it is purified with water from four nemset jars and natron, censed, and offered the foreleg of a bull.",
  repetition="4 jars (4 directions)", tools="adze (ntrty); pesesh-kef blade; nemset jars; censer", materials="water; natron; leopard skin",
  ingestants="bull's foreleg; offerings", elements="water; fire; flesh; breath", threads="opening_senses; washing; incense; four_directions",
  confidence="scholarly", note="E. Otto, Das aegyptische Mundoeffnungsritual (1960).")
r("EG11", EG, -330, "Lamentations of Isis and Nephthys (Papyrus Berlin 3008); Songs of Isis and Nephthys (Papyrus Bremner-Rhind)", "opening rubrics",
  "Khoiak mourning songs", "Two women, pure in body, hair removed, with tambourines and the names Isis and Nephthys written on their arms, sing the stanzas for Osiris in the temple during the festival of the fourth month of Inundation (Khoiak).",
  time="Khoiak (4th month of Akhet), late in the month", place="temple of Osiris", voice="sung by two women, alternating",
  tools="tambourines", materials="names written on the arms", threads="sung_praise; antiphony; khoiak; seed_burial; instruments",
  confidence="verify", note="Faulkner 1934/1936; confirm days given in the Bremner-Rhind rubric (22-26 Khoiak).")
r("EG12", EG, -50, "Dendera, Osiris chapels on the temple roof (Khoiak texts)", "Cauville, Dendara: Les chapelles osiriennes",
  "Khoiak 'corn-Osiris'", "Figures of Osiris are moulded from earth (or sand) mixed with barley, set in moulds, watered daily until they sprout, then buried at the end of the month; the djed pillar is raised on the last day of Khoiak.",
  time="Khoiak, mid-month to day 30", place="roof chapels; necropolis", tools="gold mould; basins", plants="barley; (wheat)",
  materials="earth; sand; water", elements="earth; water; seed", threads="seed_burial; khoiak; water", confidence="scholarly")
r("EG13", EG, -237, "Edfu temple foundation texts", "'stretching of the cord' (pD-SS)",
  "Temple foundation", "The king with the goddess Seshat stretches a cord to fix the temple axis, sighting the Great Bear (msxtyw) and Orion, then digs the trench, moulds the first brick and lays foundation deposits.",
  time="foundation (night sighting)", place="temple site", direction="axis set by stars", tools="cord; stakes; brick mould; hoe",
  materials="earth; brick; sand", elements="earth; stars", threads="orientation; stars", confidence="scholarly")
r("EG14", EG, -50, "Dendera, New Year rites (roof kiosk and stairways)", "Cauville / Daumas",
  "New Year: union with the sun disk", "At the New Year the image of Hathor is carried in procession up the east stair to the roof kiosk to be 'united with the disk' at sunrise, then down the west stair.",
  time="New Year (Wpt-rnpt), sunrise", place="roof kiosk; east and west stairways", direction="up the east stair, down the west",
  posture="procession", elements="light; fire", threads="dawn; procession_steps; facing_east; new_year", confidence="scholarly")
r("EG15", EG, 100, "Plutarch, On Isis and Osiris", "79-80",
  "Incense of the hours", "The Egyptians burn resin (frankincense) at sunrise, myrrh at midday, and kyphi, a compound of sixteen ingredients, at evening.",
  time="sunrise / midday / evening", repetition="3 daily", oils="frankincense resin; myrrh; kyphi (16 ingredients: honey, wine, raisins, resins, juniper ...)",
  plants="resins; juniper; cyperus; mastic", ingestants="honey and wine (in the compound)", elements="fire; smoke",
  threads="incense; hours", confidence="text")
r("EG16", EG, -100, "Edfu temple, purity inscriptions on doorways", "Edfu V-VI",
  "Entry purity", "Inscriptions at the doors warn that whoever enters must be pure; priests list impurities they have avoided.",
  place="temple doorway (threshold)", voice="declaration of purity", threads="purity_declaration; threshold", confidence="scholarly")
r("EG17", EG, -1350, "Hymn to the Aten (tomb of Ay, Amarna)", "lines on sunrise",
  "Solar hymn", "At the Aten's rising all people wash, dress and raise their arms in adoration; the hymn was performed in open-air temples facing the sunrise.",
  time="sunrise", place="open-air sun temple", direction="east", posture="arms raised", voice="hymn",
  elements="light; water", threads="dawn; facing_east; raised_hands; washing; sung_praise", confidence="scholarly",
  note="Parallel to Psalm 104 (see doc).")

# ------------------------------------------------------------------ HEBREW BIBLE
r("HB01", HB, -550, "Exodus", "30:7-8", "Incense", "Aaron burns fragrant incense each morning when he tends the lamps, and at twilight when he lights them: a perpetual incense.",
  time="morning; twilight", repetition="2 daily", place="altar of incense before the veil", tools="incense altar; lamps", oils="sweet incense",
  elements="fire; light", threads="incense; lamp_light; dawn; hours", confidence="text")
r("HB02", HB, -550, "Exodus", "30:17-21", "Washing", "A bronze basin stands between tent and altar; the priests wash hands and feet before entering or approaching the altar, 'so that they do not die'.",
  place="between tent and altar", tools="bronze basin", materials="water; bronze", elements="water", threads="washing; threshold", confidence="text")
r("HB03", HB, -550, "Exodus", "30:22-33", "Anointing oil", "Holy anointing oil: 500 shekels liquid myrrh, 250 sweet cinnamon, 250 aromatic cane, 500 cassia, and a hin of olive oil; it anoints the tent, ark, table, lampstand, altars, basin and priests, and is not for ordinary bodies.",
  oils="myrrh; cinnamon; aromatic cane; cassia; olive oil", plants="olive; cinnamon; cane; cassia", threads="anointing", confidence="text")
r("HB04", HB, -550, "Exodus", "30:34-38", "Incense recipe", "Sacred incense of stacte, onycha, galbanum and pure frankincense in equal parts, salted, pure and holy; some beaten fine and set before the testimony.",
  oils="stacte; onycha; galbanum; frankincense", materials="salt", plants="resins", elements="fire; smoke", threads="incense", confidence="text")
r("HB05", HB, -550, "Exodus", "27:20-21", "Lamp", "Pure beaten olive oil for the light; the lamp burns from evening to morning before the LORD, a perpetual statute.",
  time="evening to morning", place="outside the veil", oils="beaten olive oil", plants="olive", elements="fire; light", threads="lamp_light", confidence="text")
r("HB06", HB, -550, "Exodus", "28:39-43", "Priestly garments", "Priests wear a linen tunic, turban, sash and linen undergarments when they serve.",
  materials="linen", plants="flax", threads="linen", confidence="text")
r("HB07", HB, -550, "Exodus", "12:1-28; 13:14", "Passover", "On the 14th of the first month at evening, a lamb is slaughtered, its blood put on the doorposts with hyssop; it is eaten at night, roasted, with unleavened bread and bitter herbs, loins girded, sandals on, staff in hand, in haste; when a child asks 'what does this mean?' the story is told.",
  time="14th of first month, evening; full moon", place="household; doorway", posture="standing ready, girded", voice="child's question and retelling",
  plants="hyssop; bitter herbs", ingestants="roast lamb; unleavened bread; bitter herbs", materials="blood", elements="blood; fire",
  threads="full_moon_festival; question_answer; threshold; bread_offering", confidence="text")
r("HB08", HB, -600, "Deuteronomy", "6:4-9", "Shema", "Speak these words when you sit at home, walk on the road, lie down and rise; bind them on your hand and between your eyes; write them on doorposts and gates.",
  time="lying down and rising (evening, morning)", place="home; road; doorposts; gates", repetition="twice daily (by later practice)", voice="spoken",
  materials="written words", threads="hours; threshold; sacred_name", confidence="text")
r("HB09", HB, -550, "Leviticus", "16:4, 12-14, 24", "Day of Atonement", "The high priest bathes, puts on linen; brings a censer of coals and two handfuls of incense behind the veil so the cloud covers the mercy seat; sprinkles blood with his finger seven times; bathes again afterwards.",
  time="10th day of 7th month", place="Holy of Holies", repetition="7 sprinklings", tools="censer; coals", oils="incense", materials="linen; blood; water",
  elements="fire; smoke; blood; water", threads="washing; incense; linen; inner_room; repetition", confidence="text")
r("HB10", HB, -550, "Leviticus", "23:40-42", "Tabernacles", "On the first day take the fruit of splendid trees, palm fronds, boughs of leafy trees and willows of the brook, and rejoice seven days; live in booths.",
  time="15th of 7th month (full moon near autumn equinox), 7 days", place="booths", repetition="7 days",
  plants="palm; willow; leafy tree (myrtle); 'splendid fruit' (citron, by later tradition)", threads="full_moon_festival; plants; procession", confidence="text")
r("HB11", HB, -550, "Leviticus", "24:5-9", "Bread of the Presence", "Twelve loaves of fine flour in two rows of six on the pure table, with pure frankincense on each row, renewed every Sabbath.",
  time="every Sabbath", place="table in the holy place", repetition="12 loaves", ingestants="bread (eaten by priests)", oils="frankincense",
  threads="bread_offering; incense; weekly", confidence="text")
r("HB12", HB, -550, "Leviticus", "10:9", "Abstinence", "Priests drink no wine or strong drink when they enter the tent of meeting.",
  ingestants="no wine", threads="fasting_abstinence", confidence="text")
r("HB13", HB, -550, "Exodus", "29:38-42", "Daily offering", "Two lambs daily, one in the morning and one at twilight, each with flour mixed with beaten oil and a libation of a quarter-hin of wine.",
  time="morning; twilight", repetition="2 daily", ingestants="lamb; flour; wine (poured)", oils="olive oil", threads="dawn; hours; wine_libation", confidence="text")
r("HB14", HB, -550, "Numbers", "8:7", "Levites' purification", "Sprinkle the Levites with water of purification, have them shave their whole body and wash their clothes.",
  tools="razor", materials="water", elements="water", threads="washing; shaving", confidence="text")
r("HB15", HB, -550, "Numbers", "19:1-19", "Red heifer", "A red heifer is burned outside the camp with cedar wood, hyssop and scarlet yarn; its ash in water purifies, sprinkled on the third and seventh days.",
  time="3rd and 7th day", place="outside the camp, toward the sanctuary", repetition="2 sprinklings; blood 7 times toward the tent", plants="cedar; hyssop",
  materials="ash; water; scarlet yarn", elements="fire; water; blood", threads="washing; repetition; plants", confidence="text")
r("HB16", HB, -550, "Numbers", "10:1-10", "Silver trumpets", "Two hammered silver trumpets: to assemble, to sound alarm, and on feast days and new moons over the offerings, as a remembrance before God.",
  time="feasts; new moons", tools="two silver trumpets", voice="trumpet blasts (long; alarm)", threads="instruments; new_moon", confidence="text")
r("HB17", HB, -550, "Numbers", "6:22-27", "Priestly blessing", "Aaron and his sons bless Israel with the threefold blessing ('The LORD bless you ...'), 'so they shall put my name on the people'.",
  repetition="3 lines, divine name 3 times", voice="spoken blessing", posture="(raised hands, by later practice)", threads="sacred_name; raised_hands; repetition", confidence="text")
r("HB18", HB, -600, "Joshua", "6:3-20", "Circuit of Jericho", "March around the city once a day for six days with seven priests carrying seven ram's horns before the ark; on the seventh day circle seven times, then a long blast and a great shout.",
  time="7 days", place="around the city wall", repetition="6 x 1 circuit, then 7 circuits", tools="7 ram's horns", voice="silence, then shout",
  threads="circling; repetition; instruments", confidence="text")
r("HB19", HB, -600, "1 Kings", "8:22, 54", "Dedication prayer", "Solomon stands before the altar and spreads out his hands toward heaven; at the end he rises from kneeling with hands spread.",
  place="before the altar", posture="standing, then kneeling, hands spread", threads="raised_hands; prostration", confidence="text")
r("HB20", HB, -400, "Psalms", "134:2; 141:2", "Night and evening prayer", "Lift up your hands in the sanctuary by night; let my prayer rise as incense, the lifting of my hands as the evening offering.",
  time="night; evening", posture="hands raised", oils="incense", threads="raised_hands; incense; hours", confidence="text")
r("HB21", HB, -400, "Psalms", "55:17", "Times of prayer", "Evening, morning and noon I cry out.", time="evening, morning, noon", repetition="3 daily", threads="hours", confidence="text")
r("HB22", HB, -165, "Daniel", "6:10", "Daily prayer", "Daniel kneels three times a day in his upper room, windows open toward Jerusalem, praying and giving thanks.",
  time="3 times daily", place="upper room", direction="toward Jerusalem", repetition="3 daily", posture="kneeling",
  threads="hours; orientation; prostration", confidence="text")
r("HB23", HB, -350, "1 Chronicles", "25:1-31", "Temple music", "David sets apart musicians to prophesy with lyres, harps and cymbals: 288 in 24 courses of 12.",
  repetition="24 courses x 12", tools="lyres; harps; cymbals", voice="prophesying in song", threads="instruments; sung_praise", confidence="text")
r("HB24", HB, -350, "2 Chronicles", "5:12-14", "Temple dedication", "Levitical singers in fine linen with cymbals, harps and lyres stand east of the altar with 120 trumpeting priests; trumpeters and singers sound as one voice, and the cloud fills the house.",
  place="east of the altar", direction="east side", repetition="120 trumpets", tools="cymbals; harps; lyres; trumpets", materials="fine linen",
  voice="one voice", elements="cloud", threads="instruments; sung_praise; linen; one_voice", confidence="text")
r("HB25", HB, -400, "Nehemiah", "12:31-40", "Wall dedication", "Two great thanksgiving choirs walk on the city wall in opposite directions and meet at the house of God.",
  place="city wall to temple", direction="one to the right, one to the left", posture="procession", voice="two choirs",
  threads="circling; procession_steps; antiphony", confidence="text")
r("HB26", HB, -300, "Psalms", "136", "Refrain psalm", "Every one of 26 verses ends with the response 'for his steadfast love endures forever'.",
  repetition="26 refrains", voice="call and response", threads="antiphony; repetition", confidence="text")
r("HB27", HB, -580, "Ezekiel", "8:16", "Forbidden orientation", "About 25 men at the temple entrance, backs to the sanctuary, faces east, bow to the sun: condemned as an abomination.",
  place="between porch and altar", direction="east (condemned)", posture="bowing", elements="sun", threads="orientation; facing_east", confidence="text")
r("HB28", HB, -580, "Ezekiel", "44:1-2", "East gate", "The outer east gate is shut and stays shut, because the LORD God of Israel entered by it.",
  place="outer east gate", direction="east", threads="orientation; threshold", confidence="text")
r("HB29", HB, -600, "1 Samuel", "16:13", "Anointing a king", "Samuel takes the horn of oil and anoints David among his brothers, and the Spirit comes on him from that day.",
  tools="horn of oil", oils="olive oil", elements="breath (spirit)", threads="anointing", confidence="text")
r("HB30", HB, -400, "Psalms", "headings, e.g. 4, 6, 22, 92; 'Selah' x71", "Psalm performance notes", "Headings name the choirmaster, stringed instruments, flutes, the tune ('The Doe of the Dawn', Ps 22), the day ('for the Sabbath', Ps 92); 'Selah' marks a pause or interlude 71 times.",
  time="Sabbath (Ps 92)", tools="strings; flutes", voice="tune names; pauses", threads="rubric; instruments; weekly", confidence="text")

# ------------------------------------------------------------------ MISHNAH (redacted c. 200 CE; describes Temple before 70)
r("MI01", MI, 200, "Mishnah", "Tamid 1:2", "Clearing the altar", "Whoever wishes to clear the altar of ashes rises early and immerses before the officer arrives.",
  time="before dawn", materials="water (immersion)", elements="water; ash", threads="washing; dawn", confidence="text")
r("MI02", MI, 200, "Mishnah", "Tamid 3:2", "Waiting for light", "The officer sends a watcher to see if it is time for the morning offering; he calls out when the eastern sky is lit 'as far as Hebron'.",
  time="first light", place="temple roof/high place", direction="looking east-south (toward Hebron)", voice="call: 'it is bright'", elements="light",
  threads="dawn; orientation", confidence="text")
r("MI03", MI, 200, "Mishnah", "Tamid 5:1", "Morning recitation", "In the Chamber of Hewn Stone the priests recite a blessing, the Ten Commandments, the Shema passages, and further blessings, and bless the people.",
  time="morning", place="Chamber of Hewn Stone", voice="recitation; blessing", threads="sacred_name; hours", confidence="text")
r("MI04", MI, 200, "Mishnah", "Tamid 7:3", "Levitical song", "At the libation the cymbal is clashed, the Levites sing; at each break in the psalm the priests blow trumpets and the people prostrate.",
  place="temple court; Levites on the platform", posture="prostration at each break", tools="cymbal; trumpets", voice="Levitical song in sections",
  ingestants="wine libation", threads="instruments; prostration; sung_praise; wine_libation", confidence="text")
r("MI05", MI, 200, "Mishnah", "Tamid 7:4", "Psalm of the day", "Psalm for each day: Sunday 24, Monday 48, Tuesday 82, Wednesday 94, Thursday 81, Friday 93, Sabbath 92.",
  time="each weekday", repetition="weekly cycle of 7", voice="sung by Levites", threads="weekly; sung_praise", confidence="text")
r("MI06", MI, 200, "Mishnah", "Middot 2:5; Sukkah 5:4", "Fifteen steps", "Fifteen semicircular steps lead from the Court of Women to the Court of Israel, matching the fifteen Songs of Ascents; the Levites stood on them to sing.",
  place="15 steps between the courts", repetition="15", voice="Songs of Ascents (Ps 120-134)", threads="procession_steps; sung_praise", confidence="text")
r("MI07", MI, 200, "Mishnah", "Sukkah 4:9", "Water libation", "Each morning of Tabernacles a golden flask of three logs is filled at Siloam, brought through the Water Gate to trumpet blasts, and poured into a silver bowl on the altar beside the wine.",
  time="each morning of Tabernacles", place="Siloam -> Water Gate -> altar", repetition="7 days; 3 blasts", tools="golden flask; silver bowls; trumpets",
  materials="water; gold; silver", ingestants="wine (beside)", elements="water", threads="water_libation; procession_steps; instruments; full_moon_festival", confidence="text")
r("MI08", MI, 200, "Mishnah", "Sukkah 5:2-4", "Joy of the water-drawing", "Golden lamps 50 cubits high with wicks of old priestly garments light every courtyard in Jerusalem; pious men dance with torches; Levites play on the 15 steps; at cockcrow two priests blow, go to the east gate, turn west, and renounce sun worship.",
  time="nights of Tabernacles; cockcrow", place="Court of Women; 15 steps; east gate", direction="turn from east to west", posture="dance; turning",
  tools="golden lamps; ladders; torches; harps; lyres; cymbals; trumpets", oils="olive oil (120 log jars)", materials="old linen garments as wicks",
  voice="formula: 'our eyes are to the LORD'", elements="fire; light", threads="lamp_light; orientation; instruments; procession_steps; full_moon_festival", confidence="text")
r("MI09", MI, 200, "Mishnah", "Sukkah 4:5", "Willows and circuits", "Willow branches are set up beside the altar; each day they circle the altar once saying 'Please, LORD, save us' (Ps 118:25); on the seventh day seven times.",
  time="7 days of Tabernacles", place="around the altar", repetition="1 daily; 7 on day seven", plants="willow", voice="Hosanna cry",
  threads="circling; repetition; plants", confidence="text")
r("MI10", MI, 200, "Mishnah", "Yoma 3:3", "High priest's washings", "On the Day of Atonement the high priest immerses five times and washes hands and feet ten times.",
  repetition="5 immersions; 10 washings", materials="water", threads="washing; repetition", confidence="text")
r("MI11", MI, 200, "Mishnah", "Yoma 6:2", "The Name spoken", "When priests and people in the court heard the high priest pronounce the Name, they knelt, prostrated, fell on their faces and said 'Blessed be the name of his glorious kingdom for ever'.",
  time="Day of Atonement", place="temple court", posture="kneel, prostrate, face down", voice="the Name pronounced; congregational response",
  threads="sacred_name; prostration; antiphony", confidence="text")
r("MI12", MI, 200, "Mishnah", "Yoma 5:1", "Short prayer", "Leaving the Holy of Holies, the high priest prays a short prayer in the outer house, not prolonging it so as not to alarm Israel.",
  place="outer house (Holy Place)", voice="short prayer", threads="inner_room; silence", confidence="text")
r("MI13", MI, 200, "Mishnah", "Pesachim 10:1-8", "Passover meal", "Not eaten until dark; even the poorest reclines and drinks four cups of wine; the son asks why this night differs; the story is told from shame to praise; the Hallel is sung.",
  time="Passover night", posture="reclining", repetition="4 cups", ingestants="wine; unleavened bread; bitter herbs; haroset", voice="question and answer; Hallel",
  threads="question_answer; full_moon_festival; wine; sung_praise", confidence="text")
r("MI14", MI, 200, "Mishnah", "Berakhot 1:2", "Time of the morning Shema", "The morning Shema may be said from when one can tell blue (tekhelet) from white.",
  time="first light (colour discrimination)", elements="light", threads="dawn; hours", confidence="text")
r("MI15", MI, 200, "Mishnah", "Berakhot 4:5", "Direction of prayer", "If riding or unable to dismount, turn your face; if you cannot, direct your heart toward the Holy of Holies.",
  direction="toward the Holy of Holies", threads="orientation", confidence="text")
r("MI16", MI, 200, "Mishnah", "Middot 2:4", "Line of sight", "All the walls were high except the eastern one, so that the priest burning the red heifer on the Mount of Olives could see the sanctuary entrance while sprinkling the blood.",
  place="Mount of Olives facing the sanctuary", direction="looking west into the temple", elements="blood; fire", threads="orientation; line_of_sight", confidence="text")
r("MI17", MI, 200, "Mishnah", "Rosh Hashanah 3:3; 4:9", "Shofar", "At the New Year the shofar is of ibex horn, straight, mouth overlaid with gold, with two trumpets beside it; the blasts come in sets of three: long, broken, long.",
  time="New Year (1st of 7th month, new moon)", tools="shofar; trumpets", voice="tekiah-teruah-tekiah", repetition="3 sets of 3", threads="instruments; new_year; new_moon", confidence="text")

r("MI18", MI, 200, "Mishnah", "Tamid 5:4-6:3", "Incense offering", "A priest chosen by lot carries the incense inside and offers it on the golden altar in the Holy Place while the people outside withdraw and prostrate; he leaves before the others bless.",
  time="morning (and afternoon)", place="golden incense altar, Holy Place", posture="people prostrate outside", tools="censer; ladle; golden altar",
  oils="incense", elements="fire; smoke", threads="incense; prostration; inner_room; hours", confidence="text")

# ------------------------------------------------------------------ EARLY CHURCH
r("CH22", CH, 85, "Luke", "1:8-10", "Incense hour", "Zechariah, chosen by lot, enters the sanctuary to burn incense while the whole people pray outside at the hour of incense.",
  time="hour of incense", place="sanctuary; court outside", tools="lot", oils="incense", voice="people praying outside",
  threads="incense; hours; inner_room", confidence="text", note="An early Christian text preserving the Temple incense hour.")
r("CH23", CH, 95, "Revelation", "5:8; 8:3-4", "Heavenly incense", "Elders hold golden bowls of incense, 'which are the prayers of the saints'; an angel offers incense at the golden altar and its smoke rises with the prayers.",
  place="heavenly temple; golden altar", tools="golden bowls; golden censer", oils="incense", voice="new song (5:9)", elements="fire; smoke",
  threads="incense; sung_praise", confidence="text")
r("CH01", CH, 100, "Didache", "7", "Baptism", "Baptize in running water in the name of Father, Son and Holy Spirit; if not, other water, cold or warm; if neither, pour water on the head three times; baptizer and candidate fast beforehand.",
  repetition="3 pourings", materials="running water", ingestants="fast 1-2 days before", elements="water", threads="washing; repetition; fasting_abstinence; sacred_name", confidence="text")
r("CH02", CH, 100, "Didache", "8", "Fasts and prayer", "Fast on Wednesday and Friday; pray the Lord's Prayer three times a day.",
  time="Wednesday, Friday; 3 times daily", repetition="3 daily", threads="hours; fasting_abstinence; weekly", confidence="text")
r("CH03", CH, 100, "Didache", "9-10, 14", "Thanksgiving meal", "Give thanks first over the cup, then the broken bread ('as this bread was scattered on the mountains and gathered into one'); on the Lord's day gather, break bread and give thanks after confessing.",
  time="Lord's day", ingestants="bread; wine", plants="grain; vine", voice="set prayers; Amen", threads="bread_offering; wine; weekly", confidence="text")
r("CH04", CH, 112, "Pliny the Younger, Letters", "10.96", "Dawn hymn", "On a fixed day they meet before dawn and sing a song (carmen) to Christ as to a god, alternately among themselves; later they reassemble for an ordinary meal.",
  time="before dawn; fixed day", voice="sung alternately (antiphonal)", ingestants="ordinary food", threads="dawn; antiphony; sung_praise; weekly", confidence="text")
r("CH05", CH, 155, "Justin Martyr, First Apology", "61", "Baptism as illumination", "Candidates pray and fast; they are brought to water and washed in the name of the Father, Jesus Christ and the Holy Spirit; the washing is called illumination (photismos).",
  materials="water", ingestants="fasting", elements="water; light", threads="washing; fasting_abstinence; illumination", confidence="text")
r("CH06", CH, 155, "Justin Martyr, First Apology", "65-67", "Sunday assembly", "On Sunday the memoirs of the apostles or the prophets are read as long as time permits; the president exhorts; all stand and pray; bread and wine mixed with water are brought, thanks given, the people say Amen; deacons take portions to the absent. Sunday, because God made light from darkness on that day and Christ rose.",
  time="Sunday", posture="standing for prayer", voice="reading; exhortation; Amen", ingestants="bread; wine mixed with water", elements="light",
  threads="weekly; bread_offering; wine; reading_aloud", confidence="text")
r("CH07", CH, 197, "Tertullian, Apology", "16", "Facing east", "Outsiders think Christians worship the sun because they pray toward the east and keep Sunday.",
  direction="east", threads="facing_east; weekly", confidence="text")
r("CH08", CH, 211, "Tertullian, On the Crown", "3", "Customs from tradition", "Before baptism renounce the devil; immerse three times; taste milk and honey; no kneeling on the Lord's day or from Easter to Pentecost; trace the sign of the cross on the forehead at every going out and coming in.",
  posture="standing on Sundays; no kneeling", repetition="3 immersions", ingestants="milk and honey", materials="water", threads="washing; repetition; threshold; tradition", confidence="text")
r("CH09", CH, 233, "Origen, On Prayer", "31-32", "Posture and direction", "Pray standing, hands stretched out and eyes lifted; and toward the east, the direction of the rising light.",
  direction="east", posture="standing, hands outstretched, eyes raised", elements="light", threads="facing_east; raised_hands", confidence="text")
r("CH10", CH, 220, "Apostolic Tradition (attributed to Hippolytus)", "21", "Baptism at cockcrow", "At cockcrow, prayer over the water, which should be flowing; children first, then men, then women with hair loosened and jewellery removed; renunciation; oil of exorcism; three immersions with three questions; oil of thanksgiving; then cups of water, milk-and-honey and wine at the first Eucharist.",
  time="cockcrow (Easter vigil)", repetition="3 immersions / 3 questions", oils="oil of exorcism; oil of thanksgiving", materials="flowing water",
  ingestants="water; milk and honey; wine; bread", elements="water", threads="washing; anointing; dawn; repetition", confidence="verify",
  note="Date and origin of the Apostolic Tradition are debated (3rd-4th c., composite).")
r("CH11", CH, 220, "Apostolic Tradition", "25; 41", "Lamps and hours", "At evening a deacon brings in the lamp and the bishop gives thanks for the light; pray on rising, at the 3rd, 6th and 9th hours, at bedtime, at midnight and at cockcrow, each hour tied to an event of the Passion.",
  time="evening; 3rd, 6th, 9th hours; midnight; cockcrow", repetition="7 times daily", tools="lamp", elements="fire; light",
  threads="lamp_light; hours", confidence="verify")
r("CH12", CH, 350, "Cyril (or John) of Jerusalem, Mystagogical Catecheses", "1.2-9; 2.3-4; 3.4", "Turning from west to east", "In the outer hall the candidate faces west, stretches out a hand and renounces Satan, then turns east to confess the faith; is stripped, anointed with exorcised oil from head to foot, immersed three times; then chrism on forehead, ears, nostrils and breast.",
  time="Easter vigil", place="baptistery vestibule -> font", direction="west (renounce) -> east (confess)", posture="hand stretched out; turning",
  repetition="3 immersions", oils="exorcised olive oil; chrism (myron)", materials="water", elements="water", threads="facing_east; anointing; washing; opening_senses", confidence="text")
r("CH13", CH, 390, "Ambrose, On the Sacraments", "1.2-3", "Ephphatha", "The bishop touches the candidate's ears and nostrils saying 'Ephphatha, be opened', so they may perceive the sweet fragrance of eternal life.",
  voice="Aramaic word 'Ephphatha'", elements="breath; scent", threads="opening_senses; sacred_name", confidence="text")
r("CH14", CH, 383, "Egeria, Travels", "24.1-7", "Jerusalem daily office", "Before cockcrow the doors of the Anastasis open and hymns, psalms and antiphons are sung with responses until dawn; at the tenth hour (lucernare) all lamps are lit from the lamp that burns day and night inside the tomb cave, never from outside.",
  time="before cockcrow; tenth hour (evening)", place="Anastasis (tomb church)", voice="hymns; antiphons with responses", tools="lamps; candles",
  elements="fire; light", threads="dawn; lamp_light; antiphony; inner_room", confidence="text")
r("CH15", CH, 383, "Egeria, Travels", "24.9-10", "Sunday Gospel at dawn", "On Sunday at cockcrow the bishop reads the resurrection Gospel inside the tomb grotto; censers are brought in so the basilica fills with fragrance; the people groan and weep.",
  time="Sunday cockcrow", place="inside the tomb", tools="censers", oils="incense", voice="Gospel read aloud; groaning", threads="dawn; incense; reading_aloud; inner_room; weekly", confidence="text")
r("CH16", CH, 383, "Egeria, Travels", "37.1-3", "Veneration of the wood", "On Good Friday each person bows, touches the wood of the cross with forehead and eyes, and kisses it; deacons guard it because someone once bit off a piece.",
  time="Good Friday", posture="bowing; touching forehead and eyes", materials="wood", threads="prostration; tree_wood", confidence="text")
r("CH17", CH, 380, "Apostolic Constitutions", "2.57", "Church building and assembly", "The building is oblong like a ship, turned toward the east; the reader stands on a raised place to read Moses and the prophets; another sings David's hymns and the people respond with the closing lines.",
  place="raised reading place", direction="building toward east", voice="reading; psalm with response", threads="facing_east; antiphony; reading_aloud; orientation", confidence="text")
r("CH18", CH, 375, "Basil of Caesarea, On the Holy Spirit", "27.66", "Unwritten traditions", "Practices received from unwritten tradition: the sign of the cross, turning east to pray, the words of invocation at the Eucharist, blessing the baptismal water and the oil of anointing, triple immersion, renouncing Satan.",
  direction="east", repetition="3 immersions", oils="oil of anointing", materials="water", threads="tradition; facing_east; anointing; washing", confidence="text",
  note="Explicit ancient statement that ritual practice was passed down orally, outside the written texts.")
r("CH19", CH, 375, "Basil, On the Holy Spirit (citing the evening hymn)", "29.73", "Phos Hilaron", "At the lighting of the lamps the people sing the ancient thanksgiving 'Joyful light ...', whose author Basil no longer knew.",
  time="lamp-lighting (sunset)", voice="hymn", elements="light; fire", threads="lamp_light; sung_praise", confidence="text")
r("CH20", CH, 420, "John Cassian, Institutes", "2.4-7", "Egyptian monastic office", "Egyptian monks say twelve psalms at the evening and night offices, a number given by an angel; after each psalm they rise, stand in silent prayer, briefly prostrate, and rise again.",
  time="evening; night", repetition="12 psalms", posture="standing; brief prostration", voice="one chanter, others silent", threads="hours; prostration; silence", confidence="text")
r("CH21", CH, 650, "John Climacus, The Ladder", "27", "Prayer with the breath", "Let the remembrance of Jesus be joined to your breath, and you will know the value of stillness (hesychia).",
  voice="name of Jesus with breath", elements="breath", threads="breath; sacred_name; silence", confidence="text")

# ------------------------------------------------------------------ LIVING TRADITION
r("LV01", LV, 2000, "Coptic Orthodox practice", "month of Kiahk", "Kiahk praises", "Through the month of Kiahk (named for the ancient Khoiak) nightly vigils of special praises (Tasbeha) lead to Christmas on 29 Kiahk.",
  time="Kiahk (Dec-Jan)", voice="sung praises, long melismas", threads="khoiak; sung_praise; hours", confidence="scholarly")
r("LV02", LV, 2000, "Jewish practice", "Hoshanot (Sukkot)", "Willow circuits", "On each day of Sukkot the congregation circles the reading desk with the four species crying 'Hosha-na'; on Hoshana Rabba seven circuits, then the willows are beaten on the ground.",
  repetition="1 daily; 7 on the last day", plants="palm; willow; myrtle; citron", threads="circling; plants; repetition", confidence="scholarly")
r("LV03", LV, 2000, "Orthodox and Coptic practice", "orientation", "Facing east", "Churches are oriented with the altar to the east; prayer is said facing east.",
  direction="east", threads="facing_east; orientation", confidence="scholarly")
r("LV04", LV, 2000, "Ethiopian Orthodox practice", "zema", "Sistrum and drum", "Debtera singers chant with the sistrum (tsenatsel), drum (kebero) and prayer staff, with liturgical dance.",
  tools="sistrum; drum; prayer staff", posture="liturgical dance", threads="instruments; sung_praise", confidence="scholarly")
r("LV05", LV, 2000, "Jewish practice", "Shema and tefillin", "Shema", "The Shema is said morning and evening; tefillin are bound on arm and head; mezuzot on doorposts.",
  time="morning; evening", repetition="2 daily", threads="hours; sacred_name; threshold", confidence="scholarly")
r("LV06", LV, 2000, "Eastern Orthodox practice", "Holy Saturday, Jerusalem", "Holy Fire", "The flame is brought out from the tomb of the Holy Sepulchre and passed hand to hand.",
  place="tomb", elements="fire; light", threads="lamp_light; inner_room", confidence="scholarly")


# ------------------------------------------------------------------ POWER attributions on existing records
POWER = {
    "EG06": ("purity; word", "The pure speaker's declaration makes him 'true of voice' before the judges."),
    "EG09": ("word", "Efficacy lies in the spoken words themselves ('words to be spoken')."),
    "EG10": ("substance; word", "The adze and the spoken formulae restore breath, sight and speech."),
    "HB02": ("water; purity", "Washing hands and feet 'so that they do not die' (Exod 30:21)."),
    "HB07": ("blood", "'When I see the blood I will pass over you' (Exod 12:13)."),
    "HB09": ("blood; place; time", "Blood at the kapporet on the one day, in the one room, atones."),
    "HB17": ("name", "'So they shall put my name upon the people of Israel, and I will bless them' (Num 6:27)."),
    "HB29": ("substance; breath", "The oil is poured and the Spirit comes on David."),
    "MI11": ("name; place; time", "The Name, spoken by the high priest in the court on Yom Kippur."),
    "CH01": ("name; water", "Baptism 'in the name' of Father, Son and Holy Spirit, in living water."),
    "CH05": ("light; water; name", "The washing is 'illumination'."),
    "CH18": ("tradition", "Basil: these practices have authority from unwritten tradition."),
    "CH21": ("name; breath", "The name of Jesus joined to the breath."),
}
for d in R:
    if d["id"] in POWER: d["power"], d["note"] = POWER[d["id"]][0], (d["note"] + " " + POWER[d["id"]][1]).strip()

# ------------------------------------------------------------------ MORE HEBREW BIBLE / NT statements about where power lies
r("HB31", HB, -550, "Leviticus", "17:11", "Blood", "The life of the flesh is in the blood; it is given on the altar to make atonement, because the blood is the life.",
  materials="blood", elements="blood", threads="blood_rite", power="blood", confidence="text")
r("HB32", HB, -450, "Psalms", "51:16-17", "Inner offering", "God does not delight in sacrifice or burnt offering; the sacrifice God accepts is a broken spirit and a contrite heart.",
  threads="inner", power="inner", confidence="text")
r("HB33", HB, -700, "Micah", "6:6-8", "What is required", "Not thousands of rams or rivers of oil, but to do justice, love kindness and walk humbly with God.",
  oils="(rivers of oil rejected)", threads="inner", power="inner", confidence="text")
r("CH24", CH, 95, "John", "4:21-24", "Neither this mountain nor Jerusalem", "The hour is coming when worship will be neither on this mountain nor in Jerusalem; true worshippers will worship the Father in spirit and truth.",
  place="(no required place)", direction="(no required direction)", threads="orientation; inner", power="breath; inner", confidence="text",
  note="The text itself relocates the source of worship from place and direction to spirit (pneuma = breath) and truth.")
r("CH25", CH, 95, "John", "20:22", "Breathing", "Jesus breathes on the disciples and says 'Receive the Holy Spirit' (the verb of Genesis 2:7 LXX).",
  elements="breath", threads="breath", power="breath", confidence="text")
r("CH26", CH, 248, "Origen, Against Celsus", "1.24-25; 5.45", "Names of power", "Names such as Sabaoth and Adonai, and 'the God of Abraham, Isaac and Jacob', are effective spoken in their own language and powerless when translated.",
  voice="names in the original language", threads="sacred_name", power="name; word", confidence="text")
r("CH27", CH, 60, "Acts", "7:48-50", "No house made by hands", "The Most High does not dwell in houses made by hands: heaven is my throne and the earth my footstool (Isa 66:1).",
  threads="inner_room; orientation", power="divine_will", confidence="text")

# ------------------------------------------------------------------ SECOND TEMPLE JUDAISM BEYOND THE MISHNAH
r("ST01", ST, -100, "Dead Sea Scrolls, Community Rule (1QS)", "10:1-3", "Times of blessing", "The member blesses God at the times ordained: when the dominion of light begins, at its turning, and when it withdraws; when the watches of darkness begin; and at the starts of months, feasts and years.",
  time="sunrise; midday; sunset; nightfall; new moons; feasts", elements="light; darkness", threads="hours; dawn; new_moon", power="time", confidence="scholarly")
r("ST02", ST, -100, "Dead Sea Scrolls, Community Rule (1QS)", "3:4-9", "Water and spirit", "No one is cleansed by waters of purification while refusing God's ways; by the holy spirit and by humble submission his flesh is cleansed when sprinkled with water.",
  materials="water", elements="water; breath", threads="washing; inner", power="breath; inner; water", confidence="scholarly")
r("ST03", ST, -100, "Dead Sea Scrolls, Community Rule (1QS)", "6:4-5", "Communal meal", "When the table is set, the priest stretches out his hand first to bless the bread and the new wine.",
  posture="hand stretched out", ingestants="bread; new wine", threads="bread_offering; wine", confidence="scholarly")
r("ST04", ST, -75, "Dead Sea Scrolls, Songs of the Sabbath Sacrifice (4Q400-407)", "Songs 1-13", "Angelic liturgy", "Thirteen songs for the first thirteen Sabbaths of the year describe angelic priests praising in the heavenly temple; the seventh song stands at the center.",
  time="13 Sabbaths (one quarter-year)", repetition="13; center at 7", place="heavenly temple", voice="angelic praise", threads="sung_praise; weekly; inner_room", confidence="scholarly")
r("ST05", ST, -50, "Dead Sea Scrolls, Daily Prayers (4Q503)", "fragments", "Morning and evening blessings", "For each day of a month, blessings at sunrise and at evening, counting the day by the lights of the sky.",
  time="sunrise; evening; daily through the month", elements="light", threads="dawn; hours", power="time; light", confidence="scholarly")
r("ST06", ST, 30, "Philo, On the Contemplative Life", "27; 89", "Therapeutae: dawn prayer", "The Therapeutae, a Jewish community by Lake Mareotis near Alexandria, pray at dawn and evening; after their all-night vigil they stand facing east, and when the sun rises they stretch their hands to heaven and pray for a bright day and for truth.",
  time="dawn; evening; after an all-night vigil", place="near Alexandria, Egypt", direction="east", posture="standing; hands raised to heaven",
  elements="light", threads="dawn; facing_east; raised_hands; hours", power="light; inner", confidence="text",
  note="An Egyptian-Jewish community facing the sunrise, contrasting with Sukkah 5:4.")
r("ST07", ST, 30, "Philo, On the Contemplative Life", "83-88", "Therapeutae: two choirs", "At the all-night vigil men and women form two choirs, each with a leader, singing hymns alternately; then they merge into one choir in imitation of Israel's choir at the Red Sea (Exodus 15).",
  time="all night (50th-day feast)", voice="two choirs, antiphonal, then one", posture="dance", threads="antiphony; sung_praise; one_voice", confidence="text")
r("ST08", ST, 75, "Josephus, Jewish War", "2.128-131", "Essenes at sunrise", "Before sunrise the Essenes speak no ordinary word but offer ancestral prayers toward the sun as if begging it to rise; at the fifth hour they bathe in cold water, put on linen and eat together in silence.",
  time="before sunrise; fifth hour", direction="toward the rising sun", voice="silence; ancestral prayers", materials="cold water; linen",
  ingestants="bread; one dish", elements="light; water", threads="dawn; facing_east; washing; linen; silence; hours", power="light; time", confidence="text")
r("ST09", ST, 324, "Eusebius, Church History", "2.17", "Therapeutae read as Christians", "Eusebius claims Philo's Therapeutae were the first Christians of Egypt, citing their vigils, hymns and fasting.",
  place="Egypt", threads="tradition", confidence="text", note="A 4th-century reader linking Egyptian-Jewish practice to Christian monasticism.")

# ------------------------------------------------------------------ GRECO-ROMAN MYSTERIES (side branch)
r("GR01", GR, -600, "Homeric Hymn to Demeter", "47-50", "Torches and fasting", "Demeter wanders nine days with blazing torches, taking no ambrosia or nectar and not bathing.",
  time="9 days", repetition="9", tools="torches", ingestants="fasting", elements="fire; light", threads="lamp_light; fasting_abstinence", confidence="text")
r("GR02", GR, -600, "Homeric Hymn to Demeter", "208-211", "The kykeon", "Demeter refuses wine and asks for a drink of barley meal, water and mint: the kykeon drunk by initiates at Eleusis.",
  ingestants="kykeon (barley, water, mint)", plants="barley; mint", threads="seed_burial; ingestant_rite", confidence="text")
r("GR03", GR, 170, "Apuleius, Metamorphoses", "11.10", "Isis procession", "Initiates in white linen, priests with shaven heads, the clatter of bronze and silver sistra, lamps, torches and candles carried in procession.",
  posture="procession", tools="sistra; lamps; torches", materials="linen", threads="linen; shaving; instruments; lamp_light", confidence="text")
r("GR04", GR, 170, "Apuleius, Metamorphoses", "11.20", "Isis morning rite", "At dawn the temple is opened, white curtains drawn back; the priest lights the altar fire and pours water from the inner sanctuary, and the first hour is greeted with song.",
  time="dawn; first hour", place="inner sanctuary", materials="water", elements="fire; water", threads="dawn; inner_room; sung_praise; washing", confidence="text")
r("GR05", GR, 170, "Apuleius, Metamorphoses", "11.23", "Isis initiation", "The candidate abstains from meat and wine for ten days, is bathed and sprinkled; at midnight he sees the sun shining with a brilliant light.",
  time="midnight", repetition="10 days", ingestants="no meat; no wine", materials="water", elements="light; darkness",
  threads="fasting_abstinence; washing; illumination", power="light; divine_will", confidence="text",
  note="Light in darkness as the climax of initiation; compare John 1:5 and baptism as 'illumination'.")

# ------------------------------------------------------------------ ISLAM AND LIVING DESCENDANTS
r("IS01", IS, 624, "Qur'an", "2:142-144", "Change of prayer direction", "The direction of prayer is turned from Jerusalem to the Sacred Mosque at Mecca: 'turn your face toward it wherever you are'.",
  direction="from Jerusalem to Mecca", threads="orientation", power="place; divine_will", confidence="text",
  note="A documented handover in which direction is kept as a practice but its target changes.")
r("IS02", IS, 630, "Qur'an", "5:6", "Ablution", "Before prayer wash the face, the hands to the elbows, wipe the head, and wash the feet to the ankles; if no water, use clean earth.",
  materials="water; clean earth (if no water)", elements="water; earth", threads="washing", power="purity", confidence="text")
r("LV07", LV, 2000, "Coptic Orthodox practice", "Agpeya", "Book of hours", "Seven daily hours of prayer (with a midnight office), each with psalms and a Gospel reading.",
  repetition="7 daily", threads="hours; reading_aloud", confidence="scholarly")
r("LV08", LV, 2000, "Ethiopian Orthodox practice", "Timkat (Epiphany)", "Ark to the water", "Each church's tabot (a tablet representing the Ark) is carried in procession to water; after a night vigil the water is blessed at dawn and sprinkled on the people.",
  time="Epiphany eve to dawn", place="river or pool", posture="procession", tools="tabot", materials="water", elements="water",
  threads="procession_steps; washing; dawn; inner_room", confidence="scholarly")
