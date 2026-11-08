#!/usr/bin/env python3
"""Is John written as performance, recording movement as well as speech?  A first, testable version of the '3D writing' idea.

Every verb of motion is a step on three axes: vertical (ascend +1 / descend -1), threshold (enter +1 / go out -1) and
approach (come, draw near +1 / go away, depart -1).  Posture (stand, sit, rise, fall, bow) and gesture (weep, breathe on,
touch, wash, lift up the eyes) are counted as body actions.
 1. DENSITY: motion and body-action verbs per 1,000 words in John, Matthew, Mark, Luke.
 2. STAGING: scenes where speech is framed by movement; the trial before Pilate as a test case (seven scenes,
    in/out alternation): is its in/out alternation more regular than the same moves shuffled?
 3. THE PATH: the cumulative 3-axis path through John (written to movement_path.json for the map); where it turns.
 4. SPEECH-ACTION INTERLEAVING: how often a speech verse is followed by an action verse and back, against shuffled order.
Usage: python3 movement.py <sblgnt dir>
"""
import collections, glob, json, os, re, sys, unicodedata
import numpy as np
SBL = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(3); out = {}
def nrm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c)); return re.sub(r"[^α-ω]", "", w.replace("ς", "σ"))
AX = {"αναβαινω": (0, 1), "καταβαινω": (0, -1), "εισερχομαι": (1, 1), "εξερχομαι": (1, -1), "εισαγω": (1, 1), "εξαγω": (1, -1),
      "ερχομαι": (2, 1), "προσερχομαι": (2, 1), "εγγιζω": (2, 1), "απερχομαι": (2, -1), "υπαγω": (2, -1), "πορευομαι": (2, -1), "αναχωρεω": (2, -1), "φευγω": (2, -1)}
BODY = {"ιστημι": "stand", "καθιζω": "sit", "καθημαι": "sit", "ανιστημι": "rise", "πιπτω": "fall", "κλινω": "bow", "κλαιω": "weep", "δακρυω": "weep",
        "εμφυσαω": "breathe on", "απτω": "touch", "νιπτω": "wash", "επαιρω": "lift up", "ενεβριμησατο": "groan", "εμβριμαομαι": "groan", "ταρασσω": "troubled",
        "κραζω": "cry out", "κραυγαζω": "cry out", "βλεπω": "look", "εμβλεπω": "look", "δεικνυμι": "show", "ενδυω": "clothe", "περιζωννυμι": "gird", "ζωννυμι": "gird"}
SPEAK = {"λεγω", "λαλεω", "αποκρινομαι", "φημι", "κραζω", "ερωταω"}
def load(code):
    V = collections.OrderedDict()
    for l in open(glob.glob(os.path.join(SBL, f"*-{code}-*"))[0], encoding="utf-8"):
        p = l.split(); V.setdefault((int(p[0][2:4]), int(p[0][4:6])), []).append((nrm(p[6]), p[1]))
    return V
print("1. DENSITY per 1,000 words")
G = {c: load(c) for c in ("Jn", "Mt", "Mk", "Lk")}
for c, V in G.items():
    lem = [l for v in V.values() for l, _ in v]; n = len(lem)
    mv = sum(l in AX for l in lem); bd = sum(l in BODY for l in lem); ax = collections.Counter(AX[l][0] for l in lem if l in AX)
    print(f"   {c}: motion {1000 * mv / n:5.1f}  (vertical {1000 * ax[0] / n:4.1f}, threshold {1000 * ax[1] / n:4.1f}, approach {1000 * ax[2] / n:4.1f})   body actions {1000 * bd / n:5.1f}")
    out.setdefault("density", {})[c] = dict(motion=1000 * mv / n, vertical=1000 * ax[0] / n, threshold=1000 * ax[1] / n, approach=1000 * ax[2] / n, body=1000 * bd / n)
print("\n2. STAGING: the trial before Pilate (18:28-19:16)")
J = G["Jn"]; seq = []
for k, v in J.items():
    if (18, 28) <= k <= (19, 16):
        for l, _ in v:
            if l in ("εισερχομαι", "εξερχομαι", "εισαγω", "εξαγω"): seq.append((f"{k[0]}:{k[1]}", "in" if AX[l][1] > 0 else "out"))
alt = sum(1 for a, b in zip(seq, seq[1:]) if a[1] != b[1]) / max(1, len(seq) - 1)
moves = [s for _, s in seq]; null = [np.mean([a != b for a, b in zip(m, m[1:])]) for m in (list(rng.permutation(moves)) for _ in range(5000))]
print(f"   in/out moves: {' '.join(f'{r} {s}' for r, s in seq)}")
print(f"   alternation {alt:.2f} (in, out, in, out …); shuffled moves {np.mean(null):.2f}; p = {np.mean(np.array(null) >= alt):.3f}")
out["trial"] = dict(moves=seq, alternation=alt)
print("\n3. THE PATH THROUGH JOHN (cumulative steps on three axes)")
pos = np.zeros(3); path = []
for k, v in J.items():
    acts = [BODY[l] for l, _ in v if l in BODY]
    for l, _ in v:
        if l in AX: a, s = AX[l]; pos[a] += s
    speech = any(l in SPEAK for l, _ in v)
    path.append(dict(v=f"{k[0]}:{k[1]}", x=int(pos[2]), y=int(pos[0]), z=int(pos[1]), body=acts, speech=speech))
ys = [p["y"] for p in path]; zs = [p["z"] for p in path]; xs = [p["x"] for p in path]
print(f"   end point: approach {xs[-1]}, vertical {ys[-1]}, threshold {zs[-1]};  vertical highest at {path[int(np.argmax(ys))]['v']} ({max(ys)}), lowest at {path[int(np.argmin(ys))]['v']} ({min(ys)})")
json.dump(path, open(os.path.join(HERE, "movement_path.json"), "w"), ensure_ascii=False)
print("\n4. SPEECH AND ACTION INTERLEAVED (verse level)")
for c, V in G.items():
    lab = []
    for v in V.values():
        s = any(l in SPEAK for l, _ in v); a = any(l in AX or l in BODY for l, _ in v)
        lab.append("S" if s and not a else "A" if a and not s else "B" if a and s else "-")
    x = [t for t in lab if t in "SA"]; sw = np.mean([a != b for a, b in zip(x, x[1:])]); nl = [np.mean([a != b for a, b in zip(y, y[1:])]) for y in (list(rng.permutation(x)) for _ in range(2000))]
    both = lab.count("B") / len(lab)
    print(f"   {c}: speech/action switches {sw:.2f} (shuffled {np.mean(nl):.2f}, p = {np.mean(np.array(nl) >= sw):.3f});  verses with speech AND action together {both:.1%}")
    out.setdefault("interleave", {})[c] = dict(switch=float(sw), shuffled=float(np.mean(nl)), both=both)
json.dump(out, open(os.path.join(HERE, "movement_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
