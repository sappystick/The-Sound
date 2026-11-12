#!/usr/bin/env bash
# Round 39, lens yetzirah_calendar: every download used (run from the repo root).
set -euo pipefail
T=sources/texts

# Sefer Yetzirah, Sefaria API v3. Hebrew: "Sefer Yetzirah, Warsaw 1884" (public domain); English: Sefaria Community
# Translation (CC0). The "Gra Version" index carries a different Hebrew recension (also labelled Warsaw 1884 on
# Sefaria) and Kaplan's English (copyrighted; not used beyond counts).
mkdir -p $T/sefer_yetzirah
for c in 1 2 3 4 5 6; do
  curl -sS "https://www.sefaria.org/api/v3/texts/Sefer_Yetzirah.$c?version=hebrew&version=english" -o $T/sefer_yetzirah/sy$c.json
  curl -sS "https://www.sefaria.org/api/v3/texts/Sefer%20Yetzirah%20Gra%20Version.$c?version=hebrew&version=english" -o $T/sefer_yetzirah/gra$c.json
done

# R. H. Charles, public domain, archive.org full-text OCR (_djvu.txt)
mkdir -p $T/enoch_jubilees_charles
curl -sSL -o $T/enoch_jubilees_charles/enoch_charles1912_djvu.txt https://archive.org/download/bookofenochor1en00char/bookofenochor1en00char_djvu.txt
curl -sSL -o $T/enoch_jubilees_charles/enoch_charles1917_djvu.txt https://archive.org/download/book-of-enoch_1917/BookOfEnoch_1917_djvu.txt
curl -sSL -o $T/enoch_jubilees_charles/jubilees_charles1902_djvu.txt https://archive.org/download/bookofjubileesor00char/bookofjubileesor00char_djvu.txt
curl -sSL -o $T/enoch_jubilees_charles/jubilees_charles1917_djvu.txt https://archive.org/download/bookofjubileesor01char/bookofjubileesor01char_djvu.txt

# Already present (not re-fetched): morphhb/wlc (OSHB WLC 4.18), sblgnt (MorphGNT), cntr (CNTR transcriptions),
# dss (ETCBC/CACCHT Dead Sea Scrolls, Text-Fabric v1.9 under dss/tf/1.9; CC BY-NC 4.0).

# run
python3 -I round39/yetzirah_calendar/yetzirah_calendar.py $T round39/yetzirah_calendar
