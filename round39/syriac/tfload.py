"""Minimal Text-Fabric (.tf) reader: standard library only (text-fabric is not installed).
Node features: lines 'n<TAB>value' or 'a-b<TAB>value' set the node explicitly; a bare value means previous node + 1.
Edge feature oslots: 'node<TAB>ranges' or bare 'ranges' (comma-separated a-b), node = previous + 1."""
import os


def _body(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = 0
    while i < len(lines) and lines[i].startswith("@"):
        i += 1
    while i < len(lines) and lines[i] == "":
        i += 1
        break
    return lines[i:]


def node_feature(folder, name):
    out = {}
    n = 0
    for line in _body(os.path.join(folder, name + ".tf")):
        if line == "":
            n += 1  # an empty line is an empty value for the next node
            continue
        if "\t" in line:
            spec, val = line.split("\t", 1)
            if "-" in spec:
                a, b = map(int, spec.split("-"))
                for k in range(a, b + 1):
                    out[k] = val
                n = b
                continue
            n = int(spec)
        else:
            n += 1
            val = line
        out[n] = val
    return out


def oslots(folder):
    out = {}
    n = 0
    for line in _body(os.path.join(folder, "oslots.tf")):
        if line == "":
            continue
        if "\t" in line:
            spec, val = line.split("\t", 1)
            n = int(spec)
        else:
            n += 1
            val = line
        slots = []
        for part in val.split(","):
            if "-" in part:
                a, b = map(int, part.split("-"))
                slots.extend(range(a, b + 1))
            else:
                slots.append(int(part))
        out[n] = slots
    return out


def otypes(folder):
    """returns list of (first, last, type)"""
    res = []
    for line in _body(os.path.join(folder, "otype.tf")):
        if "\t" in line:
            spec, t = line.split("\t")
            if "-" in spec:
                a, b = map(int, spec.split("-"))
            else:
                a = b = int(spec)
            res.append((a, b, t))
    return res
