#!/usr/bin/env bash
# Sources for the round-39 scribal lens. Run from the repo root.
set -e
cd sources/texts
# already present (sources/fetch_sources.sh): MorphGNT SBLGNT (sblgnt/), CNTR transcriptions (cntr/, commit 4e743a4 per AUDIT.md)
# NEW: SBLGNT with its editorial paragraphing (XML <p> elements), CC BY 4.0, commit d7f35adca9ec410e1d1499c63b4dd989d76c8d4d
[ -d sblgnt-logos ] || git clone --depth 1 https://github.com/LogosBible/SBLGNT sblgnt-logos
