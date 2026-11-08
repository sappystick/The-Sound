"""Key ritual words: literal sense, broader meanings, ritual use, and cross-language links.
status: established = standard lexicons agree
        debated     = proposed by scholars, not agreed
        sound-link  = similar sound only; NOT an etymological relation (kept because traditions used it)
"""
W = []


def w(id, lang, term, translit, literal, broader, ritual_use, links, refs, status="established"):
    W.append(dict(id=id, language=lang, term=term, translit=translit, literal=literal, broader=broader,
                  ritual_use=ritual_use, links=links, refs=refs, status=status))


EGY, HEB, GRK, ARM = "Egyptian", "Hebrew", "Greek", "Aramaic"
w("W01", EGY, "Dd mdw", "djed medu", "speaking words", "'words to be spoken': marks what is said aloud vs. done", "Opens spells and rubrics; the boundary between voice and action", "rubrics (red ink) -> Christian rubrics", "Pyramid Texts; ritual papyri")
w("W02", EGY, "wab", "wab", "pure; to wash", "the ordinary priest is 'the pure one'; purity by washing", "Priests named by their washing", "Heb. tahor; Gk. katharos; baptism", "Herodotus 2.37; priestly titles")
w("W03", EGY, "sntr", "senetjer", "incense (causative of ntr 'god')", "often glossed 'that which makes divine'", "Censing the god at dawn", "Heb. qetoret; Gk. thymiama; Plutarch's three daily incenses", "Daily ritual", "debated")
w("W04", EGY, "mAa-xrw", "maa-kheru", "true of voice", "vindicated, justified; title of the righteous dead", "Said of one who passes the judgement of BD 125", "John 18:37 'everyone of the truth hears my voice' (parallel only)", "Book of the Dead 125")
w("W05", EGY, "Htp", "hotep", "offering table; to be content, at peace", "offering and peace are one word, written with a loaf on a mat", "Offering formula 'an offering which the king gives' (Htp-di-nsw)", "Heb. shalom / shelamim (peace-offerings); minchah", "Offering formula")
w("W06", EGY, "dwA", "dua", "to adore (written with a star)", "the same star sign writes dwAw 'morning' and dwAt 'the netherworld': adoration, dawn and the night journey share a sign", "Arms-raised posture of adoration at sunrise", "raised hands (Ps 141:2; Origen); dawn prayer", "Gardiner sign N14")
w("W07", EGY, "sbA / sbAyt", "seba / sebayt", "star; door; to teach / instruction", "'teaching' and 'instruction' (the wisdom genre, e.g. Amenemope) are written with the star sign", "Wisdom instruction texts", "Heb. torah 'instruction'; Proverbs 22-24", "Gardiner N14; wisdom texts", "debated")
w("W08", EGY, "Axt", "akhet", "horizon (place of the sun's rising)", "also the name of the Great Pyramid (Akhet Khufu) and of the season of inundation (Akhet)", "Temple pylons as the horizon; sunrise rites", "Temple gate toward the east; Jachin and Boaz", "Pyramid name; calendar")
w("W09", EGY, "anx", "ankh", "life", "also 'sandal strap', 'mirror', 'oath'; the sign became the Coptic looped cross", "Held to the nose of the king: the breath of life", "crux ansata; Gen 2:7 breath of life", "Socrates Scholasticus 5.17")
w("W10", EGY, "pr-anx", "per-ankh", "house of life", "the temple scriptorium where ritual books were written and kept", "Copying and guarding the rituals", "Christian scriptoria; the transmission chain itself", "Gardiner, 'The House of Life' (1938)")
w("W11", HEB, "dabar", "davar", "word", "also 'thing, matter, event': a word is a deed", "The ten 'words' (Exod 34:28)", "Gk. logos; Aram. memra; Ge'ez qal", "Lexicons (BDB, HALOT)")
w("W12", HEB, "qol", "qol", "voice", "sound, noise, thunder", "Ps 29: the qol of the LORD seven times over the waters", "Gk. phone; Ge'ez qal 'word/voice'", "Ps 29; Exod 19:16-19")
w("W13", HEB, "ruach", "ruach", "wind, breath", "spirit; the same word for weather, breathing and God's presence", "Breath over the waters (Gen 1:2)", "Gk. pneuma; John 3:8; 20:22", "Lexicons")
w("W14", HEB, "nefesh", "nefesh", "throat, neck", "breath, appetite, life, self", "Ps 42:1-2: the nefesh thirsts", "voice and life located in the throat", "Lexicons")
w("W15", HEB, "kavod", "kavod", "weight, heaviness", "glory, honour, presence", "The cloud of kavod fills the house (1 Kgs 8:11)", "Gk. doxa (which first meant 'opinion'); John 1:14", "Lexicons; LXX usage")
w("W16", HEB, "mishkan / shakhan", "mishkan", "dwelling (from 'to settle, dwell')", "the tabernacle; later shekhinah, God's dwelling presence", "The portable sanctuary", "Gk. skene / eskenosen (shared s-k-n sound)", "Exod 25:8-9; John 1:14", "established")
w("W17", HEB, "kipper", "kipper", "to cover / to wipe off", "to atone, ransom; kapporet = the 'mercy seat' lid", "Blood and incense at the kapporet on Yom Kippur", "Gk. hilasterion (Rom 3:25; Heb 9:5)", "Lev 16", "debated")
w("W18", HEB, "qorban", "qorban", "that which is brought near", "offering; nearness to God", "Every offering", "Mark 7:11 (korban)", "Lev 1:2")
w("W19", HEB, "mashiach", "mashiach", "smeared, anointed (with oil)", "the anointed king or priest; Messiah", "Anointing with the horn of oil", "Gk. christos, chrisma; Christian chrism", "1 Sam 16:13; John 1:41")
w("W20", HEB, "shemen", "shemen", "oil, fat", "richness, fertility, gladness ('oil of gladness', Ps 45:7)", "Anointing; lamp fuel", "olive; Exod 30 recipe", "Exod 27:20; 30:22-33")
w("W21", HEB, "qetoret", "qetoret", "smoke, what rises in smoke", "incense; prayer rising (Ps 141:2)", "Morning and twilight incense", "Egy. sntr; Rev 5:8 (bowls of incense = prayers)", "Exod 30:7-8, 34-38")
w("W22", HEB, "torah", "torah", "instruction (from yarah 'to throw, shoot, point out')", "teaching, direction, law", "Read aloud and taught", "Egy. sebayt 'instruction'", "Lexicons", "established")
w("W23", HEB, "tamid", "tamid", "continual", "the perpetual daily offering, lamp and incense", "Morning and evening offering", "Christian hours; 'pray without ceasing' (1 Thess 5:17)", "Exod 29:42; Mishnah Tamid")
w("W24", HEB, "hoshia na", "hosha-na", "save, please", "a cry that became a shout of praise", "Circling the altar with willows (Sukkah 4:5)", "Gk. hosanna (John 12:13)", "Ps 118:25")
w("W25", HEB, "selah", "selah", "unknown (perhaps 'lift up' or 'pause')", "a performance mark", "71 times in 39 psalms", "rubric; Byzantine pauses", "Psalms", "debated")
w("W26", ARM, "ephphatha", "ephphatha", "be opened", "opening of the senses", "Mark 7:34; the baptismal rite (Ambrose)", "Egyptian Opening of the Mouth (parallel only)", "Mark 7:34; Ambrose")
w("W27", GRK, "logos", "logos", "word, account", "reason; also 'ratio, proportion' in mathematics (Euclid)", "John 1:1", "Heb. davar; Aram. memra; the chat's ratio tests read logos in its mathematical sense", "LSJ; Euclid Elements V")
w("W28", GRK, "doxa", "doxa", "opinion, expectation", "in the Septuagint, 'glory' (for kavod)", "'We beheld his glory' (John 1:14)", "Heb. kavod", "LSJ; LXX")
w("W29", GRK, "photismos", "photismos", "illumination", "baptism (Justin, 1 Apol 61)", "Baptism at the Easter dawn", "light rites; John 1:9", "Justin; Heb 6:4")
w("W30", GRK, "anamnesis", "anamnesis", "remembrance, recalling", "making a past event present in the rite", "'Do this in remembrance of me' (Luke 22:19)", "Heb. zikkaron (Exod 12:14 Passover 'memorial')", "Luke 22:19; 1 Cor 11:24-25")
w("W31", GRK, "leitourgia", "leitourgia", "public work (laos + ergon)", "service of priests (LXX), then Christian worship: liturgy", "Temple service in the Septuagint; Heb 8:6", "Heb. avodah 'service/work'", "LXX; Heb 8:6")
w("W32", GRK, "psalmos", "psalmos", "a plucking (of strings)", "song to a stringed instrument, then 'psalm'", "Psalm singing", "Heb. mizmor (song with accompaniment)", "LSJ")
w("W33", GRK, "eleos / elaion", "eleos / elaion", "mercy / olive oil", "similar sound used by Greek preachers to link 'Lord have mercy' with anointing", "Kyrie eleison", "anointing oil; the Good Samaritan's oil (Luke 10:34)", "Patristic homilies", "sound-link")
w("W34", GRK, "mysterion", "mysterion", "secret rite", "the sacraments (Latin sacramentum)", "Baptism and Eucharist", "Basil's 'unwritten tradition'", "Basil, On the Holy Spirit 27")
