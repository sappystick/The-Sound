"""Text loaders shared by the cipher lens (round 39).

Hebrew: OSHB/WLC OSIS XML (ketiv as written; qere notes dropped).
Greek NT: MorphGNT SBLGNT. Greek OT: Swete LXX (word per line).
Manuscripts: CNTR MES transcriptions (P66, P75, 01, 03) with line breaks.
Sibylline Oracles: First1KGreek tlg1551.tlg001 (Geffcken 1902).
Standard library only.
"""
import os
import re
import unicodedata

HEB_BOOKS = ["Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "1Sam", "2Sam", "1Kgs", "2Kgs",
             "Isa", "Jer", "Ezek", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph",
             "Hag", "Zech", "Mal", "Ps", "Prov", "Job", "Song", "Ruth", "Lam", "Eccl", "Esth", "Dan",
             "Ezra", "Neh", "1Chr", "2Chr"]

HEB_ALPHA = "אבגדהוזחטיכלמנסעפצקרשת"
FINALS = str.maketrans("ךםןףץ", "כמנפצ")
ATHNACH = "֑"
OLE = "֫"
PREFIX_LEMMAS = set("cdbklmsi")  # conjunction, article, prepositions, relative še, interrogative


def heb_cons(s, keep_slash=False):
    out = []
    for ch in s:
        if "א" <= ch <= "ת" or (keep_slash and ch == "/"):
            out.append(ch)
    return "".join(out).translate(FINALS)


def load_wlc(wlc_dir):
    """Return list of verses: dict(book, ch, v, words=[dict(text, stem, cons, morph, lemma)], ...)."""
    verses = []
    vre = re.compile(r'<verse osisID="([^"]+)">(.*?)</verse>', re.S)
    wre = re.compile(r'<w ([^>]*)>([^<]*)</w>')
    are = re.compile(r'(\w+)="([^"]*)"')
    for b in HEB_BOOKS:
        with open(os.path.join(wlc_dir, b + ".xml"), encoding="utf-8") as f:
            xml = f.read()
        for m in vre.finditer(xml):
            osis = m.group(1)
            _, c, v = osis.split(".")
            body = re.sub(r"<note.*?</note>", "", m.group(2), flags=re.S)
            words = []
            for wm in wre.finditer(body):
                attrs = dict(are.findall(wm.group(1)))
                raw = wm.group(2)
                lem = attrs.get("lemma", "")
                morph = attrs.get("morph", "")
                segs = heb_cons(raw, keep_slash=True).split("/")
                lsegs = lem.split("/")
                # strip leading prefix morphemes (lemma segment is a single letter)
                k = 0
                while k < len(lsegs) - 1 and k < len(segs) - 1 and lsegs[k].strip() in PREFIX_LEMMAS:
                    k += 1
                stem = "".join(segs[k:])
                cons = "".join(segs)
                words.append(dict(raw=raw, cons=cons, stem=stem, morph=morph, lemma=lem,
                                  athnach=(ATHNACH in raw), ole=(OLE in raw)))
            verses.append(dict(book=b, ch=int(c), v=int(v), words=words))
    return verses


# ---------------------------------------------------------------- Greek
LAT2GRK = str.maketrans("ABEZHIKMNOPTXY", "ΑΒΕΖΗΙΚΜΝΟΡΤΧΥ")
GRK_ALPHA = "αβγδεζηθικλμνξοπρστυφχψω"


def grk_plain(s):
    """lowercase, no diacritics, final sigma -> σ, only Greek letters kept."""
    s = s.translate(LAT2GRK)
    s = unicodedata.normalize("NFD", s)
    out = []
    for ch in s:
        if unicodedata.combining(ch):
            continue
        ch = ch.lower()
        if ch in "ςϲ":
            ch = "σ"
        if ch == "ϗ":
            out.append("και")
            continue
        if "α" <= ch <= "ω":
            out.append(ch)
    return "".join(out)


def load_sblgnt(d):
    """verses: list of (book, ch, v, [normalized words]); lexicon of forms+lemmas."""
    verses = []
    lex = set()
    for fn in sorted(os.listdir(d)):
        if not fn.endswith("morphgnt.txt"):
            continue
        book = fn.split("-")[1]
        cur = None
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            for line in f:
                p = line.split()
                if len(p) < 7:
                    continue
                bcv = p[0]
                key = (book, int(bcv[2:4]), int(bcv[4:6]))
                if cur is None or cur[0] != key:
                    cur = [key, []]
                    verses.append(cur)
                w = grk_plain(p[5])
                cur[1].append(w)
                lex.add(w)
                lex.add(grk_plain(p[6]))
    out = [(k[0], k[1], k[2], ws) for k, ws in verses]
    return out, lex


def load_lxx(d):
    verses = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        book = fn[:-4]
        cur = None
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            for line in f:
                p = line.split()
                if len(p) < 2:
                    continue
                parts = p[0].split(".")
                if len(parts) != 3:
                    continue
                try:
                    key = (book, int(parts[1]), int(parts[2]))
                except ValueError:
                    continue
                if cur is None or cur[0] != key:
                    cur = [key, []]
                    verses.append(cur)
                w = grk_plain(p[1])
                if w:
                    cur[1].append(w)
    return [(k[0], k[1], k[2], ws) for k, ws in verses if ws]


def load_sibyl(xml_path):
    """Return list of (book, lineno, text) from Geffcken's edition (notes stripped).
    Line numbers are reconstructed from <lb n=.../> anchors every five lines."""
    with open(xml_path, encoding="utf-8") as f:
        xml = f.read()
    xml = re.sub(r"<note.*?</note>", "", xml, flags=re.S)
    xml = re.sub(r"<head>.*?</head>", "", xml, flags=re.S)
    xml = re.sub(r"<pb[^>]*/>", "", xml)
    books = re.split(r'<div type="textpart" subtype="book" n="([^"]+)">', xml)
    out = []
    for i in range(1, len(books), 2):
        bn = books[i]
        if bn == "praef":
            continue
        body = books[i + 1]
        body = re.sub(r"<gap[^>]*/>", "", body)
        lines = []
        for raw in body.split("\n"):
            m = re.search(r'<lb n="(\d+)"/>', raw)
            anchor = int(m.group(1)) if m else None
            txt = re.sub(r"<[^>]+>", "", raw).strip()
            if not txt:
                continue
            if not re.search(r"[Ͱ-Ͽἀ-῿]", txt):
                continue
            lines.append([anchor, txt])
        # number lines: forward from anchors
        n = 0
        for ln in lines:
            if ln[0] is not None:
                n = ln[0]
            else:
                n += 1
            ln[0] = n
        out.extend((bn, ln[0], ln[1]) for ln in lines)
    return out


# ---------------------------------------------------------------- CNTR manuscripts
def load_cntr_lines(path, book_prefix="43", columns=False):
    """Physical lines of a manuscript for one book.
    Returns list of lines; each line is a string of letters where '?' marks a letter not
    visible (lacuna-supplied: followed by ^, or a ~supplied word). Line starts are '/', '\\', '|'."""
    chunks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith(book_prefix):
                continue
            p = line.rstrip("\n").split(" ", 1)
            if len(p) < 2:
                continue
            chunks.append(p[1])
    s = " ".join(chunks)
    # corrections: keep first hand x{...}; drop following unprefixed/a/b corrections
    s = re.sub(r"x\{([^}]*)\}", lambda m: "\x01" + m.group(1) + "\x02", s)
    s = re.sub(r"[ab]?\{[^}]*\}", "", s)
    s = s.replace("\x01", "").replace("\x02", "")
    s = re.sub(r"[\\|]\d*", "/\x03", s)  # page/column break (with page number) -> new column
    s = s.replace("&", "/&/")
    out_lines = []
    cols = [[]]
    for seg in s.split("/"):
        if seg.startswith("\x03"):
            seg = seg[1:]
            if cols[-1]:
                cols.append([])
        letters = []
        toks = seg.split(" ")
        for tok in toks:
            if not tok:
                continue
            supplied = tok.startswith("~")
            t = tok
            i = 0
            buf = []
            while i < len(t):
                ch = t[i]
                nxt = t[i + 1] if i + 1 < len(t) else ""
                if ch == "&":
                    buf.append("?")
                elif ch == "ϗ":
                    buf.append("κ")
                elif "α" <= ch <= "ω" or ch in "ϲ":
                    c = "σ" if ch in "ςϲ" else ch
                    if supplied or nxt == "^":
                        c = "?"
                    buf.append(c)
                i += 1
            letters.extend(buf)
        if letters:
            out_lines.append("".join(letters))
            cols[-1].append(out_lines[-1])
    if columns:
        return [c for c in cols if c]
    return out_lines


def load_constantine_acrostic(xml_path):
    """The 34 acrostic lines as quoted in Constantine, Oratio ad coetum sanctorum 18
    (Heikel 1902, First1KGreek tlg2018.tlg021)."""
    with open(xml_path, encoding="utf-8") as f:
        xml = f.read()
    xml = re.sub(r"<note.*?</note>", "", xml, flags=re.S)
    i = xml.index("<lg>", xml.index("ἀκροστχὶς"))
    j = xml.index("ἕνεχ", i)
    j = xml.index("\n", j)
    out = []
    for raw in xml[i:j].split("\n"):
        txt = re.sub(r"<[^>]+>", "", raw).strip()
        if len(re.findall(r"[\u0370-\u03FF\u1F00-\u1FFF]", txt)) >= 5:
            out.append(txt)
    return out
