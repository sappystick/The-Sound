#!/usr/bin/env bash
# Round 39, lens "coptic": sources fetched (run from the repo root).
set -euo pipefail
cd sources/texts

# 1. Coptic SCRIPTORIUM corpora (https://github.com/CopticScriptorium/corpora). Large repo (>1 GB of blobs):
#    blobless sparse clone, then only the CoNLL-U folders + the two Bible TreeTagger zips.
#    Commit used: see `git -C sources/texts/coptic_scriptorium rev-parse HEAD` (recorded in results.json).
#    Licences vary per corpus (mostly CC-BY 4.0; Sahidica NT text (c) J. Warren Wells, academic use only).
git clone --depth 1 --filter=blob:none --sparse https://github.com/CopticScriptorium/corpora.git coptic_scriptorium
git -C coptic_scriptorium sparse-checkout set --no-cone '/*/*_CONLLU/' '/*/*.md' '/LICENSE*' '/README*'
git -C coptic_scriptorium sparse-checkout add '/sahidica.nt/sahidica.nt_TT.zip' '/sahidic.ot/sahidic.ot_TT.zip'
# NB: in this repo sahidica.nt_CONLLU holds 2-byte placeholders for most books; the TT zip is the full NT.

# 2. Unpack the TreeTagger SGML files (Sahidic NT 259 chapters, Sahidic OT 911 chapters) into their own folder.
mkdir -p coptic_scriptorium_tt
python3 -I -c "
import zipfile
for z in ['coptic_scriptorium/sahidica.nt/sahidica.nt_TT.zip','coptic_scriptorium/sahidic.ot/sahidic.ot_TT.zip']:
    zf=zipfile.ZipFile(z)
    assert all(not m.startswith('/') and '..' not in m for m in zf.namelist())
    zf.extractall('coptic_scriptorium_tt')
"

# 3. Looked for, not fetched: Nag Hammadi Gospel of Truth (NHC I,3) and Apocryphon of John (NHC II,1) are NOT in
#    Coptic SCRIPTORIUM. archive.org has only in-copyright editions (e.g. apocryphonjohann0000unse, Giversen 1963,
#    lending scan) - no open lemmatised text, so they are not used.
#    archive.org advancedsearch queries used:
#      curl "https://archive.org/advancedsearch.php?q=apocryphon%20of%20john%20coptic&fl[]=identifier&rows=8&output=json"
#      curl "https://archive.org/advancedsearch.php?q=gospel%20of%20truth%20coptic&fl[]=identifier&rows=8&output=json"
