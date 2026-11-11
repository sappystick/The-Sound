"""Parse the OCR of the English translation of Codex Neofiti 1 (Diez Macho, Neophyti 1, Anexo; tr. McNamara & Maher)
into verses, keeping the main text and dropping the critical notes (marginal readings 'M:', interlinear 'I:').
In this translation Memra is rendered 'Word' (capital W), Yeqara 'Glory', Shekinah 'Shekinah'."""
import re
ROM = {"I": 1, "V": 5, "X": 10, "L": 50}
def roman(s):
    s = s.replace(" ", "").replace("l", "I").replace("1", "I"); t = 0
    for i, ch in enumerate(s):
        v = ROM.get(ch, 0); t += -v if i + 1 < len(s) and ROM.get(s[i + 1], 0) > v else v
    return t
def parse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    out, ch, vs, buf, note = {}, 0, 0, [], False
    def flush():
        if ch and vs and buf: out[(ch, vs)] = re.sub(r"\s+", " ", " ".join(buf)).strip()
    for raw in lines:
        l = raw.strip()
        if re.match(r"^CHAPTER\s*[A-Za-z0-9 ]{0,8}$", l):  # headings are OCR-noisy; every book has the full count
            flush(); buf = []; ch, vs, note = ch + 1, 0, False
            continue
        if not l: continue
        if re.match(r"^(\(\s*.{0,4}\s*\)|O|C\))\s*(M|I|V|P|Nu|R|Ms|Cf|cf|The|This|In|Or|Lit|See|Read|Text|Correction|Probably|Ms\.)\b", l) or re.match(r"^\(\s*\S{0,3}\s*\)\s", l):
            note = True; continue
        if re.match(r"^(Gen|Ex|Exod|Lev|Num|Nu|Deut|Dt)\.?\s+\d+\s*,", l) or re.match(r"^NEOFITI", l) or re.match(r"^\d{1,4}$", l):
            note = False  # a page header / page number starts a new page of main text
            continue
        m = re.match(r"^(\d[\d ]{0,4}?)\s+(?=[A-Z«(\[‘“'\"])", l)
        if m:
            n = int(m.group(1).replace(" ", ""))
            if vs < n <= vs + 3:
                flush(); buf = [l[m.end():]]; vs = n; note = False; continue
        if not note and ch and vs: buf.append(l)
    flush()
    return out
def clean(t):
    t = re.split(r"\S{0,3}\)\s*(?:M|I|V|P)\s*[:;]", t)[0]  # a leaked critical note: cut from its siglum on
    return re.sub(r"\(\s*[^()]{0,4}\s*\)", " ", t)  # drop inline note markers like ( 3 )
def en_terms(t):
    t = clean(t)
    return dict(memra=len(re.findall(r"\bWord\b", t)), shekinah=len(re.findall(r"\bShekin", t)),
                yeqara_all=len(re.findall(r"\bGlory\b", t)), anahu_all=len(re.findall(r"\bam he\b", t)))
