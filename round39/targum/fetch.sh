#!/usr/bin/env bash
# Round 39 / targum lens: download the Aramaic Targums from the Sefaria API (v3), whole books, primary version.
# Licences (per Sefaria metadata): Onkelos (Metsudah 2009) CC-BY-NC; Neofiti (Vatican MS Neofiti 1) "unknown";
# Pseudo-Jonathan, Fragment Targum, Targum Jonathan (Mikraot Gedolot), Writings Targums: Public Domain.
# Counts and short quotations only in the write-up.
set -euo pipefail
OUT="${1:-sources/texts/targum}"; mkdir -p "$OUT"
API="https://www.sefaria.org/api/v3/texts"
get() { [ -s "$OUT/$1.json" ] || { curl -sS --retry 3 "$API/$1" -o "$OUT/$1.json"; sleep 0.3; }; }
get "Targum_Neofiti"               # Sefaria stub: Neofiti Gen 1:1-8 only (Aramaic)
for b in Genesis Exodus Leviticus Numbers Deuteronomy; do
  get "Onkelos_$b"                 # Targum Onkelos
  get "Targum_Jonathan_on_$b"      # Targum Pseudo-Jonathan
  get "Targum_Jerusalem,_$b"       # Fragment Targum (Jerusalem)
done
for b in Joshua Judges I_Samuel II_Samuel I_Kings II_Kings Isaiah Jeremiah Ezekiel Hosea Joel Amos Obadiah Jonah Micah Nahum Habakkuk Zephaniah Haggai Zechariah Malachi; do
  get "Targum_Jonathan_on_$b"      # Targum Jonathan on the Prophets
done
for b in Psalms Proverbs Job Song_of_Songs Ruth Lamentations Ecclesiastes Esther I_Chronicles II_Chronicles; do
  get "Aramaic_Targum_to_$b"       # Targums of the Writings
done
# Sefaria's "Targum Neofiti" holds only Genesis 1:1-8 (index lengths [1, 8]); the per-chapter requests above all
# return that stub.  Fallback: the English translation (McNamara & Maher) printed in Diez Macho's editio princeps
# (Neophyti 1, Madrid 1968-79), OCR text on archive.org.  Copyrighted: counts and short quotations only.
NIA="${OUT%/targum}/neofiti_ia"; mkdir -p "$NIA"
IA="https://archive.org/download"
[ -s "$NIA/Genesis_en.txt" ]     || curl -sSL "$IA/neofiti1genesis/Neofiti%201%20-%20G%C3%A9nesis%20-%20Translation-English_djvu.txt" -o "$NIA/Genesis_en.txt"
[ -s "$NIA/Exodus_en.txt" ]      || curl -sSL "$IA/neofiti1exodo/Neofiti%201%20-%20Exodo%20-%20Translation%20-%20English_djvu.txt" -o "$NIA/Exodus_en.txt"
[ -s "$NIA/Leviticus_en.txt" ]   || curl -sSL "$IA/neofiti1levitico/Neofiti%201%20-%20Levitico%20-%20Translation-English_djvu.txt" -o "$NIA/Leviticus_en.txt"
[ -s "$NIA/Numbers_en.txt" ]     || curl -sSL "$IA/neofiti1numeros/Neofiti%201%20-%20Numeros%20-%20Translation-English_djvu.txt" -o "$NIA/Numbers_en.txt"
[ -s "$NIA/Deuteronomy_en.txt" ] || curl -sSL "$IA/neofiti1deuteronomio/Neofiti%201%20-%20Deuteronomio%20-%20Translation-English_djvu.txt" -o "$NIA/Deuteronomy_en.txt"
