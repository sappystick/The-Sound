#!/usr/bin/env bash
# Fetch every open source text used by the-sound into ./texts (not committed: each keeps its own licence).
set -e
mkdir -p texts && cd texts
clone() { [ -d "$2" ] || git clone -q --depth 1 "$1" "$2"; }
sparse() { [ -d "$2" ] || git clone -q --depth 1 --filter=blob:none --sparse "$1" "$2"; (cd "$2" && git sparse-checkout add "${@:3}"); }
clone https://github.com/morphgnt/sblgnt.git sblgnt                    # Greek NT, CC BY 4.0
clone https://github.com/nathans/lxx-swete.git lxx-swete               # Septuagint (Swete), CC BY-SA 4.0
clone https://github.com/openscriptures/morphhb.git morphhb            # Hebrew Bible (WLC/OSHB), CC BY 4.0
clone https://github.com/Center-for-New-Testament-Restoration/transcriptions.git cntr   # papyri & codices, CC BY-SA 4.0
# Greek authors (First1KGreek, CC BY-SA): Philo, Corpus Hermeticum, Orphica, Eusebius, Irenaeus
sparse https://github.com/OpenGreekAndLatin/First1KGreek.git f1k data/tlg0018 data/tlg1286 data/tlg0579 data/tlg2018 data/tlg1447
# Perseus Greek (CC BY-SA): Josephus, Homeric Hymns, Plato (Timaeus), Euclid, Hippocrates, Aristotle
sparse https://github.com/PerseusDL/canonical-greekLit.git perseus data/tlg0526 data/tlg0013 data/tlg0059/tlg031 data/tlg1799 data/tlg0627 data/tlg0086
# Perseus Latin: Vitruvius (architecture), Pliny (Natural History: stones, water, medicine)
sparse https://github.com/PerseusDL/canonical-latinLit.git latin data/phi1056 data/phi0978
# Mishnah Sukkah (Hebrew, public domain) from the Sefaria export
mkdir -p sefaria && curl -sS -o sefaria/sukkah.json "https://storage.googleapis.com/sefaria-export/json/Mishnah/Seder%20Moed/Mishnah%20Sukkah/Hebrew/merged.json"
echo "done: $(du -sh . | cut -f1)"
# ---- added: further witnesses and the era's other voices ----
clone https://github.com/ETCBC/dss.git dss                            # Dead Sea Scrolls (Abegg data, Text-Fabric), CC BY-NC
clone https://github.com/scrollmapper/bible_databases.git versions    # Vulgate, Peshitta, Coptic Sahidic and others
sparse https://github.com/OpenGreekAndLatin/First1KGreek.git f1k data/tlg1443 data/tlg1139 data/tlg0555   # Ignatius, Hermas, Clement of Alexandria
mkdir -p heron && curl -sL -o heron/heron_vol1_schmidt1899.txt "https://archive.org/download/heronisalexandri01hero/heronisalexandri01hero_djvu.txt"   # Heron, Pneumatica (Schmidt 1899), public domain
mkdir -p oxyrhynchus && curl -sL -o oxyrhynchus/poxy15.txt "https://archive.org/download/oxyrhynchuspapyr0015gren/oxyrhynchuspapyr0015gren_djvu.txt"   # P.Oxy. XV (1922), incl. 1786 Christian hymn with notes
curl -sS -o sefaria/berakhot_3b.json "https://www.sefaria.org/api/v3/texts/Berakhot.3b?version=english&version=hebrew"   # David's wind-played lyre
mkdir -p odes_solomon && curl -sL -o odes_solomon/harris1909.txt "https://archive.org/download/bwb_KU-773-127/bwb_KU-773-127_djvu.txt" && curl -sL -o odes_solomon/harris1916.txt "https://archive.org/download/odespsalmsofsolo01harruoft/odespsalmsofsolo01harruoft_djvu.txt"
mkdir -p amherst && curl -sL -o amherst/pamh1.txt "https://archive.org/download/amherstpapyribei01grenuoft/amherstpapyribei01grenuoft_djvu.txt"   # Amherst Papyri I (1900), P.Amh. 2 Christian acrostic hymn
mkdir -p sefaria/r47 && for ref in Mishnah_Arakhin.2 Mishnah_Tamid.3 Mishnah_Tamid.5 Mishnah_Tamid.7 Mishnah_Sukkah.5 Mishnah_Middot.2 Mishnah_Rosh_Hashanah.4 Berakhot.62a Arakhin.10b Arakhin.11a; do curl -s -o "sefaria/r47/$ref.json" "https://www.sefaria.org/api/v3/texts/$ref?version=english&version=hebrew"; done
for t in Berakhot Shabbat Taanit Sanhedrin; do for c in 1 2 3 4 5; do curl -s -o "sefaria/r47/Y_${t}_$c.json" "https://www.sefaria.org/api/v3/texts/Jerusalem_Talmud_${t}.$c?version=hebrew"; done; done   # Galilean Aramaic sample
mkdir -p petrie && curl -sL -o petrie/petrie1883.txt "https://archive.org/download/cu31924012038927/cu31924012038927_djvu.txt"   # Petrie, Pyramids and Temples of Gizeh (1883)
