#!/usr/bin/env bash
# Reproduce the audited results.  Run from the repository root after sources/fetch_sources.sh.
set -euo pipefail
SRC=${SRC:-sources/data}             # where fetch_sources.sh cloned the texts
SBL=$SRC/sblgnt; WLC=$SRC/morphhb/wlc; LXX=$SRC/lxx-swete/data; CNTR="$SRC/cntr/class 1"
python3 robustness/robustness.py "$SBL" "$WLC" "$LXX" "$CNTR" | tee robustness/robustness_log.txt   # C24 C25 C3 C11 G G2
python3 robustness/highres.py "$SBL"                                                               # C24 with 1,000,000 random cut sets
python3 code/analysis/round30.py "$SBL"; python3 code/analysis/round31.py "$SBL"                    # section finder, four Gospels
python3 code/analysis/round28.py "$CNTR" "$SBL"; python3 code/analysis/round29.py "$CNTR" "$SBL"    # clause edges in unspaced papyri
python3 model/build_john_model.py "$SBL"                                                           # sound model with section pauses
python3 video/render_john_video.py "$SBL" "$SRC/versions/KJV.csv" /tmp/john_video                   # full spoken reconstruction (about 1 hour)
