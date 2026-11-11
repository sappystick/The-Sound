#!/usr/bin/env python3
"""Round 39 lens: Sefer Yetzirah letter physics (A) and the priestly 364-day calendar (B).

Usage:
  python3 -I yetzirah_calendar.py <texts_dir> <out_dir>
  (texts_dir = /home/user/The-Sound/sources/texts ; out_dir = this folder)

All tests were written down here BEFORE results were inspected.

PART A. Sefer Yetzirah (SY), Sefaria: "Sefer Yetzirah" (Warsaw 1884 Hebrew, CC0 English) and
"Sefer Yetzirah Gra Version" (Hebrew; English is Kaplan, copyrighted: not used).
 A0  Extract the letter classes from the SY text itself (2.1/3.1 mothers, 2.3 five places, 4.1
     doubles, 5.1 simples) in both recensions; check that they partition the 22 letters.
 A1  Power-speech profile.  Passages: Gen 1 divine speech (the words after "and God said" in the
     ten utterances), Exod 3:14, Num 6:24-26, Deut 6:4, Ps 29, Isa 6:3; plus the pooled set; plus
     a list of divine names.  Profiles (7): share of mothers (A,M,Sh), share of each of the five
     places, and an omnibus chi-square distance of the 5-place distribution.
     Null: random contiguous windows of the same letter length from the same book (word-start
     aligned), 20000 draws.  Two-sided empirical p.  Names: random tokens of the same length from
     the whole Hebrew Bible.  Sensitivity: the pooled set with the divine names removed.
     Positive control: Psalm 119 acrostic stanzas (mem 119:97-104 -> M share; shin 119:161-168 ->
     Sh share; bet 119:9-16 -> labials) against Psalms windows.
 A2  Mothers as elements.  Water: Gen 1:2-10, Ezek 47:1-12, Zech 14:8 -> share of M.  Fire:
     Exod 3:1-6, Exod 19:16-20, 1 Kgs 18:20-40 -> share of Sh (all shin/sin; secondary: shin-dot
     only).  Same-book window null.  Control: remove the words whose lemma is mayim (H4325) or
     esh (H784) from passage AND from the null books, re-test.  Specificity: M in fire, Sh in water.
 A3  231 gates: unordered pairs of distinct adjacent letters inside words.  Gen 1:1-2:3 against
     random contiguous Torah blocks of the same number of words (5000 draws); per-gate empirical
     two-sided p, BH over 231.  Positive control: Num 7:12-83 truncated to the same word count
     (a repetitive offering list; must give many significant gates).  Negative control: one
     random Torah block (fixed seed).
PART B. 364-day calendar.
 B0  Calendar model (Jubilees 6:23-38; 1 Enoch 72-82): 4 x (30,30,31) days, 1/I = Wednesday.
     Positive controls: (i) Enoch 72 month lengths and Enoch 74:10-16 / Jubilees 6 numbers recomputed;
     (ii) every festival weekday numeral and priestly-course name in the Qumran calendrical texts
     (4Q320 4 iii-vi, 4Q319, 4Q325, 4Q326, 4Q329a; ETCBC/CACCHT dss data) predicted by the model
     (one fitted parameter: the course serving in week 0 of year 1).
 B1  Every time marker in John (SBLGNT lemmas), listed with reference; John's day-by-day timeline.
 B2  Model comparison (with explicit assumptions): John's passion markers scored as consistent /
     contradicted / undetermined under (L) official lunar calendar with astronomical new moons
     and first-crescent visibility (Meeus new-moon series; AD 26-36), (S) 364-day calendar,
     (J) Jaubert's hybrid.  Positive control: Meeus example 49.a new moon (1977 Feb 18 03:37:42 TD)
     and the AD 33 April 3 full moon (lunar eclipse, Humphreys & Waddington 1983).
 B3  John 1:19-2:11 day count.
"""
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np

SEED = 39
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tfread import dss_lines  # noqa: E402

FINALS = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
LETTERS = 'אבגדהוזחטיכלמנסעפצקרשת'
LIDX = {c: i for i, c in enumerate(LETTERS)}
SHIN_DOT, SIN_DOT = 'ׁ', 'ׂ'


def bh(pvals):
    p = np.asarray(pvals, float)
    n = len(p)
    if n == 0:
        return []
    order = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank, i in reversed(list(enumerate(order, start=1))):
        prev = min(prev, p[i] * n / rank)
        q[i] = prev
    return q.tolist()


# ----------------------------------------------------------------------------------------------
# Hebrew Bible (WLC / OSHB)
# ----------------------------------------------------------------------------------------------
W_RE = re.compile(r'<w\b([^>]*)>(.*?)</w>', re.S)
V_RE = re.compile(r'<verse osisID="([^"]+)">(.*?)</verse>', re.S)
NOTE_RE = re.compile(r'<note\b.*?</note>', re.S)


def cons(word):
    """consonants (finals normalized) and the count of shin-dot letters"""
    out = []
    shin = 0
    for i, ch in enumerate(word):
        if ch in FINALS:
            ch = FINALS[ch]
        if ch in LIDX:
            out.append(ch)
            if ch == 'ש':
                j = i + 1
                while j < len(word) and '֑' <= word[j] <= 'ׇ' and word[j] not in (SHIN_DOT, SIN_DOT):
                    j += 1
                if j < len(word) and word[j] == SHIN_DOT:
                    shin += 1
    return ''.join(out), shin


def load_book(wlc, book):
    txt = open(os.path.join(wlc, book + '.xml'), encoding='utf-8').read()
    words = []  # (ref, consonants, lemma, shin_dot_count)
    for ref, body in V_RE.findall(txt):
        body = NOTE_RE.sub('', body)
        for attrs, w in W_RE.findall(body):
            m = re.search(r'lemma="([^"]*)"', attrs)
            lem = m.group(1) if m else ''
            c, sh = cons(w)
            if c:
                words.append((ref, c, lem, sh, len(words)))
    return words


def ref_tuple(ref):
    b, c, v = ref.split('.')
    return b, int(c), int(v)


def select(words, book, c1, v1, c2, v2):
    out = []
    for w in words:
        b, c, v = ref_tuple(w[0])
        if b == book and (c, v) >= (c1, v1) and (c, v) <= (c2, v2):
            out.append(w)
    return out


def lemma_nums(lem):
    return set(re.findall(r'\d+', lem))


# ----------------------------------------------------------------------------------------------
# A0  Sefer Yetzirah classification from the text
# ----------------------------------------------------------------------------------------------
def sy_groups(line):
    toks = re.findall(r'[א-ת]+"[א-ת]', line)
    return [''.join(FINALS.get(ch, ch) for ch in t.replace('"', '')) for t in toks]


def run_A0(sydir):
    res = {}
    for name, pre in [('Warsaw1884 (Sefaria "Sefer Yetzirah")', 'sy'), ('Gra version (Sefaria)', 'gra')]:
        lines = {}
        for c in range(1, 7):
            with open(os.path.join(sydir, f'{pre}{c}.json'), encoding='utf-8') as fh:
                d = json.load(fh)
            heb = [v for v in d['versions'] if v['language'] == 'he'][0]
            for i, t in enumerate(heb['text']):
                lines[f'{c}.{i + 1}'] = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', t))
        main23 = lines['2.3'].split('[')[0]
        places = sy_groups(main23)
        organs = re.findall(r'"[א-ת]\s+(ב[א-ת]+)', main23)
        mothers = sy_groups(lines['3.1'])[0] if sy_groups(lines['3.1']) else sy_groups(lines['2.1'])[0]
        dbl = ''.join(sy_groups(lines['4.1'].split('(')[0])[:2])
        simp = ''.join(sy_groups(lines['5.1'])[:6])
        if not simp:  # Gra spelling: single letters with geresh, ה' ו' ז', ...
            simp = ''.join(re.findall(r"([\u05D0-\u05EA])'", lines['5.1'].split('יסודן')[0]))
        allc = mothers + dbl + simp
        r = {'mothers': mothers, 'doubles': dbl, 'simples': simp,
             'partition_ok': len(allc) == 22 and set(allc) == set(LETTERS),
             'five_places_in_order': places, 'organs_named': organs,
             'places_partition_ok': len(''.join(places)) == 22 and set(''.join(places)) == set(LETTERS)}
        # Mantua addition (bracketed note in Warsaw 2.3)
        if '[' in lines['2.3']:
            r['bracket_note_groups'] = sy_groups(lines['2.3'].split('[', 1)[1])
        # element mapping from 3.3
        r['king_letter_element'] = [(m.group(1), m.group(2)) for k in sorted(lines) if k.startswith('3.')
                                    for m in re.finditer(r'המליך אות (\S+) ב(\S+)', lines[k])]
        r['heaven_fire_earth_water'] = [k for k in sorted(lines) if 'שמים נבראו' in lines[k] or 'ארץ נבראת' in lines[k]]
        res[name] = r
    return res


PLACE_NAMES = ['gutturals', 'labials', 'palatals', 'linguals', 'dentals']


def letter_class_arrays(a0):
    r = a0['Warsaw1884 (Sefaria "Sefer Yetzirah")']
    place_of = np.zeros(22, int)
    places = r['five_places_in_order']  # Warsaw order: gutt, lab, pal, ling, dent
    for pi, g in enumerate(places):
        for ch in g:
            place_of[LIDX[ch]] = pi
    mothers = [LIDX[c] for c in r['mothers']]
    return place_of, mothers


# ----------------------------------------------------------------------------------------------
# window null machinery
# ----------------------------------------------------------------------------------------------
class BookLetters:
    def __init__(self, words, remove_lemmas=None):
        if remove_lemmas:
            words = [w for w in words if not (lemma_nums(w[2]) & remove_lemmas)]
        self.words = words
        self.kpos = {}
        pos_ = 0
        for w in words:
            self.kpos[w[4]] = pos_
            pos_ += len(w[1])
        s = ''.join(w[1] for w in words)
        self.idx = np.array([LIDX[c] for c in s], np.int16)
        lens = np.array([len(w[1]) for w in words])
        self.wstart = np.concatenate([[0], np.cumsum(lens)[:-1]])
        self.N = len(self.idx)
        onehot = np.zeros((self.N + 1, 22), np.int32)
        onehot[np.arange(1, self.N + 1), self.idx] = 1
        self.cum = np.cumsum(onehot, axis=0)
        shin = np.zeros(self.N + 1, np.int32)
        pos = 0
        for w in words:
            # place shin-dot counts at the word's first letter (approximation inside window)
            shin[pos + 1] += w[3]
            pos += len(w[1])
        self.shincum = np.cumsum(shin)

    def span(self, ws):
        """letter range [a, b) of a passage (list of words) in this book"""
        ks = [self.kpos[w[4]] for w in ws if w[4] in self.kpos]
        if not ks:
            return None
        last = max(ws, key=lambda w: w[4])
        return min(ks), self.kpos.get(last[4], max(ks)) + len(last[1])

    def windows(self, L, n, rng, excl=None):
        """n random windows of L letters starting at word starts; windows overlapping excl=[a,b) are not drawn"""
        ok = self.wstart[self.wstart + L <= self.N]
        if excl is not None:
            a, b = excl
            ok = ok[(ok >= b) | (ok + L <= a)]
        s = rng.choice(ok, size=n)
        counts = self.cum[s + L] - self.cum[s]
        shin = self.shincum[s + L] - self.shincum[s]
        return counts, shin


def counts_of(words):
    c = np.zeros(22, np.int64)
    sh = 0
    for w in words:
        for ch in w[1]:
            c[LIDX[ch]] += 1
        sh += w[3]
    return c, sh


def profiles(counts, place_of, mothers, base_place=None):
    """counts: (..., 22). returns dict name->array"""
    counts = np.asarray(counts, float)
    tot = counts.sum(-1)
    out = {'mothers': counts[..., mothers].sum(-1) / tot}
    pl = np.stack([counts[..., place_of == k].sum(-1) for k in range(5)], -1) / tot[..., None]
    for k, nm in enumerate(PLACE_NAMES):
        out[nm] = pl[..., k]
    if base_place is not None:
        out['omnibus_chi2'] = (((pl - base_place) ** 2) / base_place).sum(-1) * tot
    return out, pl


def emp_p(obs, null, two_sided=True):
    null = np.asarray(null)
    if two_sided:
        mu = null.mean()
        return float((np.sum(np.abs(null - mu) >= abs(obs - mu) - 1e-12) + 1) / (len(null) + 1))
    return float((np.sum(null >= obs - 1e-12) + 1) / (len(null) + 1))


def test_segments(segments, books, place_of, mothers, rng, n=20000, names=None):
    """segments: list of (book, words). Null = per-segment same-length windows from own book."""
    obs_c = np.zeros(22)
    null_c = np.zeros((n, 22))
    for bk, ws in segments:
        c, _ = counts_of(ws)
        obs_c += c
        cnt, _ = books[bk].windows(int(c.sum()), n, rng, books[bk].span(ws))
        null_c += cnt
    # base place distribution = mean of null
    _, pl_null = profiles(null_c, place_of, mothers)
    base = pl_null.mean(0)
    po, _ = profiles(obs_c, place_of, mothers, base)
    pn, _ = profiles(null_c, place_of, mothers, base)
    out = {'letters': int(obs_c.sum())}
    for k in po:
        out[k] = {'obs': float(po[k]), 'null_mean': float(pn[k].mean()),
                  'z': float((po[k] - pn[k].mean()) / (pn[k].std() + 1e-12)),
                  'p': emp_p(po[k], pn[k], two_sided=(k != 'omnibus_chi2'))}
    return out


# ----------------------------------------------------------------------------------------------
# PART A
# ----------------------------------------------------------------------------------------------
TORAH = ['Gen', 'Exod', 'Lev', 'Num', 'Deut']


def gen1_speech(gen):
    """words following 'ויאמר (להם) אלהים' up to the end of the verse, Gen 1:3-29"""
    segs = []
    byv = defaultdict(list)
    for w in gen:
        b, c, v = ref_tuple(w[0])
        if c == 1:
            byv[v].append(w)
    for v in sorted(byv):
        ws = byv[v]
        for i, w in enumerate(ws):
            if w[1] == 'ויאמר':
                j = i + 1
                if ws[j][1] == 'להמ':
                    j += 1
                if ws[j][1] == 'אלהימ':
                    segs.append((v, ws[j + 1:]))
                    break
    return segs


def run_A(texts, a0, rng):
    wlc = os.path.join(texts, 'morphhb', 'wlc')
    allbooks = [f[:-4] for f in os.listdir(wlc) if f.endswith('.xml') and f != 'VerseMap.xml']
    words = {b: load_book(wlc, b) for b in sorted(allbooks)}
    place_of, mothers = letter_class_arrays(a0)
    need = ['Gen', 'Exod', 'Num', 'Deut', 'Ps', 'Isa', 'Ezek', 'Zech', '1Kgs']
    books = {b: BookLetters(words[b]) for b in need}
    out = {'tests': []}

    # whole-Bible letter base rates
    allc = np.zeros(22)
    for b in words:
        allc += counts_of(words[b])[0]
    pb, plb = profiles(allc, place_of, mothers)
    out['bible_base'] = {k: float(v) for k, v in pb.items()}

    # ---------- positive controls (Psalm 119) ----------
    ps = words['Ps']
    pc = {}
    for nm, (c1, v1, c2, v2), prof in [('Ps119 mem stanza 97-104', (119, 97, 119, 104), 'mem_share'),
                                         ('Ps119 shin stanza 161-168', (119, 161, 119, 168), 'shin_share'),
                                         ('Ps119 bet stanza 9-16', (119, 9, 119, 16), 'labials')]:
        seg = select(ps, 'Ps', c1, v1, c2, v2)
        c, _ = counts_of(seg)
        L = int(c.sum())
        cnt, _ = books['Ps'].windows(L, 20000, rng, books['Ps'].span(seg))
        if prof == 'mem_share':
            o, nl = c[LIDX['מ']] / L, cnt[:, LIDX['מ']] / L
        elif prof == 'shin_share':
            o, nl = c[LIDX['ש']] / L, cnt[:, LIDX['ש']] / L
        else:
            po, _ = profiles(c, place_of, mothers)
            pn, _ = profiles(cnt, place_of, mothers)
            o, nl = po['labials'], pn['labials']
        pc[nm] = {'profile': prof, 'obs': float(o), 'null_mean': float(nl.mean()),
                  'z': float((o - nl.mean()) / nl.std()), 'p_one_sided': emp_p(o, nl, False)}
    # alliteration control: Isa 28:10 ("tsav la-tsav, tsav la-tsav, qav la-qav ..."), omnibus place profile
    seg = select(words['Isa'], 'Isa', 28, 10, 28, 10)
    r_ = test_segments([('Isa', seg)], books, place_of, mothers, rng)
    pc['Isa 28:10 alliteration (omnibus)'] = {'profile': 'omnibus_chi2', 'obs': r_['omnibus_chi2']['obs'],
                                              'null_mean': r_['omnibus_chi2']['null_mean'], 'z': r_['omnibus_chi2']['z'],
                                              'p_one_sided': r_['omnibus_chi2']['p'], 'letters': r_['letters']}
    out['A1_positive_controls'] = pc
    # power: minimum detectable shift in a class share (two-sided 0.05) for window sizes used here
    mde = {}
    for L in (25, 60, 350, 545):
        cnt, _ = books['Gen'].windows(L, 20000, rng)
        po_, _ = profiles(cnt, place_of, mothers)
        mde[str(L)] = {k: float(1.96 * po_[k].std()) for k in ('mothers', 'gutturals', 'labials', 'palatals', 'linguals', 'dentals')}
    out['A1_min_detectable_shift'] = mde

    # ---------- A1 passages ----------
    gen = words['Gen']
    sp = gen1_speech(gen)
    out['A1_gen1_speech_verses'] = [v for v, _ in sp]
    passages = {
        'Gen 1 divine speech (10 utterances)': [('Gen', ws) for _, ws in sp],
        'Exod 3:14': [('Exod', select(words['Exod'], 'Exod', 3, 14, 3, 14))],
        'Num 6:24-26': [('Num', select(words['Num'], 'Num', 6, 24, 6, 26))],
        'Deut 6:4': [('Deut', select(words['Deut'], 'Deut', 6, 4, 6, 4))],
        'Ps 29': [('Ps', select(ps, 'Ps', 29, 1, 29, 11))],
        'Isa 6:3': [('Isa', select(words['Isa'], 'Isa', 6, 3, 6, 3))],
    }
    passages['POOLED power speech'] = sum(passages.values(), [])
    a1 = {}
    for nm, segs in passages.items():
        a1[nm] = test_segments(segs, books, place_of, mothers, rng)
        for k, v in a1[nm].items():
            if isinstance(v, dict):
                out['tests'].append(('A1', nm, k, v['p']))
    # names removed (sensitivity, reported separately, not in the BH family)
    NAME_LEMMAS = {'3068', '3069', '430', '410', '433', '136', '7706', '6635', '3050', '5945'}
    segs_nr = [(b, [w for w in ws if not (lemma_nums(w[2]) & NAME_LEMMAS)]) for b, ws in passages['POOLED power speech']]
    a1['POOLED, divine names removed (sensitivity)'] = test_segments(segs_nr, books, place_of, mothers, rng)
    # divine names list
    names = ['יהוה', 'אלהים', 'אל', 'אלוה', 'שדי', 'אדני', 'יה', 'צבאות', 'עליון', 'אהיה']
    toks_by_len = defaultdict(list)
    for b in words:
        for w in words[b]:
            toks_by_len[len(w[1])].append(w[1])
    nc = np.zeros(22)
    names = [cons(x)[0] for x in names]
    for nmw in names:
        for ch in nmw:
            nc[LIDX[ch]] += 1
    nn = 20000
    null_c = np.zeros((nn, 22))
    for nmw in names:
        pool = toks_by_len[len(nmw)]
        pick = rng.integers(0, len(pool), nn)
        for i, j in enumerate(pick):
            for ch in pool[j]:
                null_c[i, LIDX[ch]] += 1
    _, pln = profiles(null_c, place_of, mothers)
    base = pln.mean(0)
    po, _ = profiles(nc, place_of, mothers, base)
    pn, _ = profiles(null_c, place_of, mothers, base)
    a1['divine names (10, vs random same-length tokens)'] = {
        k: {'obs': float(po[k]), 'null_mean': float(pn[k].mean()),
            'z': float((po[k] - pn[k].mean()) / (pn[k].std() + 1e-12)),
            'p': emp_p(po[k], pn[k], k != 'omnibus_chi2')} for k in po}
    for k, v in a1['divine names (10, vs random same-length tokens)'].items():
        out['tests'].append(('A1', 'divine names', k, v['p']))
    out['A1'] = a1

    # ---------- A2 elements ----------
    REM = {'4325', '784'}
    water = [('Gen', select(gen, 'Gen', 1, 2, 1, 10)), ('Ezek', select(words['Ezek'], 'Ezek', 47, 1, 47, 12)),
             ('Zech', select(words['Zech'], 'Zech', 14, 8, 14, 8))]
    fire = [('Exod', select(words['Exod'], 'Exod', 3, 1, 3, 6)), ('Exod', select(words['Exod'], 'Exod', 19, 16, 19, 20)),
            ('1Kgs', select(words['1Kgs'], '1Kgs', 18, 20, 18, 40))]
    books_rm = {b: BookLetters(words[b], REM) for b in set(x[0] for x in water + fire)}
    a2 = {}

    def letter_share_test(segs, bks, letter, remove, shin_only=False, n=20000):
        obs = 0; L_tot = 0
        null = np.zeros(n)
        for bk, ws in segs:
            if remove:
                ws = [w for w in ws if not (lemma_nums(w[2]) & REM)]
            c, sh = counts_of(ws)
            L = int(c.sum())
            cnt, shn = bks[bk].windows(L, n, rng, bks[bk].span(ws))
            if shin_only:
                obs += sh; null += shn
            else:
                obs += c[LIDX[letter]]; null += cnt[:, LIDX[letter]]
            L_tot += L
        o, nl = obs / L_tot, null / L_tot
        removed = sum(1 for bk, ws in segs for w in ws if lemma_nums(w[2]) & REM)
        return {'letters': L_tot, 'obs_share': float(o), 'null_mean': float(nl.mean()),
                'ratio': float(o / nl.mean()), 'z': float((o - nl.mean()) / nl.std()),
                'p_one_sided': emp_p(o, nl, False), 'words_removed': removed if remove else 0}

    for setname, segs, letter in [('water', water, 'מ'), ('fire', fire, 'ש')]:
        for remove in (False, True):
            key = f'{setname}: share of {letter}' + (' (mayim/esh words removed)' if remove else '')
            a2[key] = letter_share_test(segs, books_rm if remove else books, letter, remove)
            out['tests'].append(('A2', setname, key, a2[key]['p_one_sided']))
    a2['fire: shin-dot only'] = letter_share_test(fire, books, 'ש', False, shin_only=True)
    a2['fire: shin-dot only (esh removed)'] = letter_share_test(fire, books_rm, 'ש', True, shin_only=True)
    out['tests'].append(('A2', 'fire', 'shin-dot only (esh removed)', a2['fire: shin-dot only (esh removed)']['p_one_sided']))
    a2['specificity: water: share of ש'] = letter_share_test(water, books, 'ש', False)
    a2['specificity: fire: share of מ'] = letter_share_test(fire, books, 'מ', False)
    a2['specificity: water: share of ש (removed)'] = letter_share_test(water, books_rm, 'ש', True)
    a2['specificity: fire: share of מ (removed)'] = letter_share_test(fire, books_rm, 'מ', True)
    # word-count bookkeeping
    a2['mayim_tokens_in_water'] = sum(1 for _, ws in water for w in ws if '4325' in lemma_nums(w[2]))
    a2['esh_tokens_in_fire'] = sum(1 for _, ws in fire for w in ws if '784' in lemma_nums(w[2]))
    out['A2'] = a2

    # ---------- A3 231 gates ----------
    gates = [(i, j) for i in range(22) for j in range(i + 1, 22)]
    gidx = {g: k for k, g in enumerate(gates)}
    assert len(gates) == 231
    torah = sum((words[b] for b in TORAH), [])

    def word_gates(c):
        v = []
        for a, b in zip(c, c[1:]):
            i, j = LIDX[a], LIDX[b]
            if i != j:
                v.append(gidx[(min(i, j), max(i, j))])
        return v
    M = np.zeros((len(torah) + 1, 231), np.int32)
    for k, w in enumerate(torah):
        for g in word_gates(w[1]):
            M[k + 1, g] += 1
    C = np.cumsum(M, axis=0)
    del M
    pos_of = {}
    for k, w in enumerate(torah):
        pos_of.setdefault((w[0]), k)

    def block_counts(start, nw):
        return C[start + nw] - C[start]

    def find(ref):
        return pos_of[ref]
    g1s = find('Gen.1.1'); g1e = find('Gen.2.4')
    nw = g1e - g1s
    nnull = 5000

    def rates(x):
        return x / x.sum(-1, keepdims=True)

    def make_null(start):
        """random Torah blocks of nw words that do not overlap the tested block"""
        ok = np.arange(0, len(torah) - nw)
        ok = ok[(ok >= start + nw) | (ok + nw <= start)]
        st = rng.choice(ok, nnull)
        n_r = rates((C[st + nw] - C[st]).astype(float))
        return n_r, n_r.mean(0), n_r.std(0) + 1e-12

    def chi(o_r, mu):
        return float((((o_r - mu) ** 2) / (mu + 1e-12)).sum())

    def gate_test(start):
        o_r = rates(block_counts(start, nw).astype(float))
        n_r, mu, sd = make_null(start)
        z = (o_r - mu) / sd
        p = ((np.abs(n_r - mu) >= np.abs(o_r - mu)[None, :] - 1e-15).sum(0) + 1) / (nnull + 1)
        q = np.array(bh(p))
        chi_null = ((n_r - mu) ** 2 / (mu + 1e-12)).sum(1)
        p_omni = emp_p(chi(o_r, mu), chi_null, False)
        return z, p, q, p_omni, mu
    obs = block_counts(g1s, nw).astype(float)
    z, p, q, p_omni_g1, mu = gate_test(g1s)
    gname = lambda k: LETTERS[gates[k][0]] + LETTERS[gates[k][1]]
    order = np.argsort(p)
    # which Gen 1 words drive each top gate
    g1words = torah[g1s:g1e]

    def drivers(k):
        cc = Counter()
        for w in g1words:
            n_ = word_gates(w[1]).count(k)
            if n_:
                cc[w[1]] += n_
        return cc.most_common(3)
    a3 = {'gen1_words': nw, 'gen1_pairs': int(obs.sum()), 'null_blocks': nnull,
          'n_gates_q05': int((q < 0.05).sum()), 'n_gates_p05': int((p < 0.05).sum()),
          'expected_p05_by_chance': 231 * 0.05,
          'unused_gates_gen1': [gname(k) for k in range(231) if obs[k] == 0],
          'unused_gates_torah': [gname(k) for k in range(231) if C[-1][k] == 0],
          'top': [{'gate': gname(k), 'obs': int(obs[k]), 'exp': float(mu[k] * obs.sum()), 'z': float(z[k]),
                   'p': float(p[k]), 'q': float(q[k]), 'driven_by': drivers(int(k))} for k in order[:15]]}
    # positive control: Num 7:12-83 truncated to nw words
    n7 = find('Num.7.12')
    zc, pc_, qc, po7, _ = gate_test(n7)
    a3['positive_control_Num7'] = {'n_gates_q05': int((qc < 0.05).sum()), 'n_gates_p05': int((pc_ < 0.05).sum()),
                                   'n_gates_p001': int((pc_ <= 0.001).sum()), 'omnibus_chi_p': po7,
                                   'top': [(gname(int(k)), float(zc[k])) for k in np.argsort(-np.abs(zc))[:6]]}
    s0 = int(np.random.default_rng(SEED + 7).integers(0, len(torah) - nw))
    zn, pn_, qn, pon, _ = gate_test(s0)
    a3['negative_control_random_block'] = {'start_ref': torah[s0][0], 'n_gates_q05': int((qn < 0.05).sum()),
                                           'n_gates_p05': int((pn_ < 0.05).sum()), 'n_gates_p001': int((pn_ <= 0.001).sum()),
                                           'omnibus_chi_p': pon}
    a3['gen1_n_gates_p001'] = int((p <= 0.001).sum())
    a3['omnibus_chi_p'] = p_omni_g1
    out['tests'].append(('A3', 'Gen1 gates', 'omnibus', a3['omnibus_chi_p']))
    a3['gate_level_note'] = 'per-gate BH is within the 231 family; omnibus enters the lens family'
    a3['per_gate_p'] = {gname(k): float(p[k]) for k in range(231)}
    out['A3'] = a3
    return out


# ----------------------------------------------------------------------------------------------
# PART B
# ----------------------------------------------------------------------------------------------
WEEKDAY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
COURSES = ['יהויריב', 'ידעיה', 'חרים', 'שעורים', 'מלכיה', 'מימין', 'הקוץ', 'אביה', 'ישוע', 'שכניה', 'אלישיב',
           'יקים', 'חפה', 'ישבאב', 'בלגה', 'אמר', 'חזיר', 'הפצץ', 'פתחיה', 'יחזקאל', 'יכין', 'גמול', 'דליה', 'מעזיה']
COURSE_ALIAS = {'ייריב': 'יהויריב', 'יויריב': 'יהויריב', 'מימן': 'מימין', 'קוץ': 'הקוץ', 'חפא': 'חפה', 'חופה': 'חפה',
                'חופא': 'חפה', 'פצצ': 'הפצץ', 'פצץ': 'הפצץ', 'מעוזיה': 'מעזיה', 'מועזיה': 'מעזיה', 'בלגא': 'בלגה'}
MONTH_LEN = [30, 30, 31] * 4


def doy364(m, d):
    return sum(MONTH_LEN[:m - 1]) + d - 1


def wd364(m, d):
    """weekday index 0=Sun of day d of month m; 1/I = Wednesday"""
    return (3 + doy364(m, d)) % 7


FESTIVALS_364 = {'Passover (14/I)': (1, 14), 'Unleavened Bread (15/I)': (1, 15), 'Omer waving (26/I)': (1, 26),
                 'Second Passover (14/II)': (2, 14), 'Weeks (15/III)': (3, 15), 'New Wine (3/V)': (5, 3),
                 'New Oil (22/VI)': (6, 22), 'Remembrance (1/VII)': (7, 1), 'Atonement (10/VII)': (7, 10),
                 'Tabernacles (15/VII)': (7, 15), 'Eighth day (22/VII)': (7, 22), 'Dedication (25/IX, not in 364 texts)': (9, 25)}

DSS_FEST = {'הפסחהשני': 'Second Passover (14/II)', 'הפסח': 'Passover (14/I)', 'הנףהעמר': 'Omer waving (26/I)',
            'הנףהעומר': 'Omer waving (26/I)', 'חגהשבועים': 'Weeks (15/III)', 'יוםהזכרון': 'Remembrance (1/VII)',
            'יוםהכפורים': 'Atonement (10/VII)', 'חגהסכות': 'Tabernacles (15/VII)', 'חגהמצות': 'Unleavened Bread (15/I)'}
NUMR = {'א֜': 1, 'אׄ': 1, 'אׅ': 1, 'אֽ': 1, 'י֜': 10, 'ך֜': 20, 'ק֜': 100}
ORD = {'ראשון': 1, 'שני': 2, 'שלישי': 3, 'רביעי': 4, 'חמישי': 5, 'ששי': 6, 'שביעי': 7}


def numeral_value(tok):
    v = 0
    i = 0
    ok = False
    while i < len(tok):
        two = tok[i:i + 2]
        if two in NUMR:
            v += NUMR[two]; i += 2; ok = True
        else:
            return None
    return v if ok else None


def year_doy(y, m, d):
    """absolute day index from 1/I of year 1 (years of 364 days)"""
    return (y - 1) * 364 + doy364(m, d)


def course_of(absday, offset, start_on_sunday=True):
    """course serving on absday; week 0 = the week containing 1/I of year 1 (1/I is Wednesday, abs day 0).
    Weeks run Sun-Sat (start_on_sunday) or Sat-Fri."""
    first_week_start = -3 if start_on_sunday else -4
    wk = (absday - first_week_start) // 7
    return COURSES[(offset + wk) % 24]


def run_B0(texts):
    out = {}
    # (i) texts
    en = open(os.path.join(texts, 'enoch_jubilees_charles', 'enoch_charles1917_djvu.txt'), encoding='utf-8').read()
    a = en.find('CHAPTER LXXIl.')
    b = en.find('CHAPTER LXXIII')
    ch72 = en[a:b] if a > 0 and b > a else ''
    ml = [31 if m.startswith('one') else 30 for m in re.findall(r'(one-and-thirty|thirty) mornings', ch72)]
    out['enoch72_month_lengths_found'] = ml
    out['enoch72_sum_first12'] = sum(ml[:12])
    m = re.search(r'In 3 years there\s+are (\d+) days, and in 5 years (\d+) days, so that in 8 years there are (\d+) days', en)
    lun = re.search(r'amount in 3 years to (\d+) days', en)
    lun8 = re.search(r'8 years amount to (\d+) days', en)
    out['enoch74_solar'] = [int(x) for x in m.groups()] if m else None
    out['enoch74_solar_check'] = bool(m) and [int(x) for x in m.groups()] == [3 * 364, 5 * 364, 8 * 364]
    out['enoch74_lunar'] = [int(lun.group(1)) if lun else None, int(lun8.group(1)) if lun8 else None]
    out['enoch74_lunar_check_354'] = bool(lun and lun8) and int(lun.group(1)) == 3 * 354 and int(lun8.group(1)) == 8 * 354
    jb = open(os.path.join(texts, 'enoch_jubilees_charles', 'jubilees_charles1917_djvu.txt'), encoding='utf-8').read()
    jbs = re.sub(r'\s+', ' ', jb)
    out['jubilees6_markers'] = {k: (k in jbs) for k in ['thirteen weeks', 'two and fifty weeks', 'three hundred and sixty-four days',
                                                         'ten days too soon', 'observations of the moon']}
    out['model'] = {'month_lengths': MONTH_LEN, 'year_days': sum(MONTH_LEN), 'weeks': sum(MONTH_LEN) / 7, '1/I': 'Wed'}
    out['festival_weekdays_364'] = {k: WEEKDAY[wd364(*v)] for k, v in FESTIVALS_364.items()}

    # (ii) DSS calendrical texts
    L = dss_lines(os.path.join(texts, 'dss', 'tf', '1.9') + '/', ['4Q319', '4Q32', '4Q330'])
    out['dss_lines'] = len(L)
    out['dss_scrolls'] = dict(Counter(s for s, _, _, _ in L))
    entries = []
    year = 0
    for s, f, ln, ws in L:
        joined = ''.join(ws)
        if s == '4Q320' and f.startswith('f4') and 'מועדי' in joined:
            year += 1
            continue
        if s == '4Q320' and f.startswith('f4') and year > 0 and len(ws) >= 3 and ws[0] == 'ב':
            wd = numeral_value(ws[1])
            # course name follows 'ב' (and optional 'שבת בני')
            rest = ws[2:]
            if rest[:3] == ['ב', 'שבת', 'בני']:
                rest = rest[3:]
            elif rest[:1] == ['ב']:
                rest = rest[1:]
            course = rest[0] if rest else ''
            fest = ''.join(rest[1:])
            fest_name = DSS_FEST.get(fest)
            if wd and fest_name:
                entries.append({'scroll': s, 'frag': f, 'line': ln, 'year': year, 'weekday_num': wd,
                                'course': COURSE_ALIAS.get(course, course), 'festival': fest_name})
    # 4Q326 / 4Q325 "יום שלישי" style
    for s, f, ln, ws in L:
        j = ' '.join(ws)
        for mm in re.finditer(r'(ה פסח|חג ה מצות) יום (\S+)', j):
            fest = 'Passover (14/I)' if mm.group(1) == 'ה פסח' else 'Unleavened Bread (15/I)'
            o = ORD.get(mm.group(2))
            if o:
                entries.append({'scroll': s, 'frag': f, 'line': ln, 'year': None, 'weekday_num': o, 'course': None,
                                'festival': fest})
    # predicted weekday check
    ok_wd = 0
    for e in entries:
        mth, d = FESTIVALS_364[e['festival']]
        pred = wd364(mth, d) + 1  # Sun = 1
        e['pred_weekday_num'] = pred
        e['weekday_ok'] = (pred == e['weekday_num'])
        ok_wd += e['weekday_ok']
    out['dss_weekday_entries'] = len(entries)
    out['dss_weekday_matches'] = ok_wd
    # courses: fit one offset and week convention using the FIRST entry only, predict the rest
    ce = [e for e in entries if e['course']]
    best = None
    for conv in (True, False):
        for off in range(24):
            e0 = ce[0]
            mth, d = FESTIVALS_364[e0['festival']]
            if course_of(year_doy(e0['year'], mth, d), off, conv) == e0['course']:
                hits = sum(course_of(year_doy(e['year'], *FESTIVALS_364[e['festival']]), off, conv) == e['course'] for e in ce)
                if best is None or hits > best[0]:
                    best = (hits, off, conv)
    out['dss_course_entries'] = len(ce)
    out['dss_course_fit'] = {'hits': best[0], 'of': len(ce), 'offset_course_week0': COURSES[best[1]],
                             'weeks_start_sunday': best[2], 'fitted_from_entry': 1}
    # chance level: a random course name matches with p = 1/24
    k, n = best[0] - 1, len(ce) - 1
    p_bin = sum(math.comb(n, i) * (1 / 24) ** i * (23 / 24) ** (n - i) for i in range(k, n + 1))
    out['dss_course_p_binomial'] = p_bin
    misses = []
    for e in ce:
        pc = course_of(year_doy(e['year'], *FESTIVALS_364[e['festival']]), best[1], best[2])
        if pc != e['course']:
            misses.append({'ref': f"{e['scroll']} {e['frag']} {e['line']}", 'text_course': e['course'], 'model': pc})
    out['dss_course_misses'] = misses
    out['dss_entries'] = entries
    # does the calendrical corpus mention Hanukkah / Purim?
    alltxt = ' '.join(' '.join(ws) for _, _, _, ws in L)
    out['dss_mentions'] = {w: alltxt.count(w) for w in ['חנוכה', 'פורים', 'ה פסח', 'סכות', 'שבועים', 'כפורים']}
    out['six_year_cycle_days'] = 6 * 364
    out['six_year_cycle_weeks_over_24'] = 6 * 364 / 7 / 24
    return out


# ---------------- John ----------------
TIME_LEMMAS = {'ἐπαύριον', 'ἡμέρα', 'ὥρα', 'πάσχα', 'ἑορτή', 'σκηνοπηγία', 'ἐγκαίνια', 'σάββατον', 'παρασκευή',
               'ὀψία', 'πρωΐ', 'πρωΐα', 'νύξ', 'χειμών', 'ἔτος', 'τετράμηνος', 'σήμερον', 'αὔριον', 'ἄρτι'}


def load_john(texts):
    rows = []
    for ln in open(os.path.join(texts, 'sblgnt', '64-Jn-morphgnt.txt'), encoding='utf-8'):
        p = ln.split()
        ref = p[0]
        rows.append((int(ref[2:4]), int(ref[4:6]), p[3], p[5], p[6]))
    return rows


def run_B1(texts):
    rows = load_john(texts)
    byv = defaultdict(list)
    for c, v, t, nw, lem in rows:
        byv[(c, v)].append((t, nw, lem))
    markers = []
    for (c, v), ws in sorted(byv.items()):
        lems = [w[2] for w in ws]
        hit = [l for l in lems if l in TIME_LEMMAS and l not in ('ἄρτι', 'σήμερον')]
        if not hit:
            continue
        txt = ' '.join(w[0] for w in ws)
        kinds = []
        if 'ἐπαύριον' in lems: kinds.append('next day')
        if 'ἡμέρα' in lems:
            if 'τρίτος' in lems: kinds.append('third day')
            if 'δύο' in lems: kinds.append('two days')
            if 'ἕξ' in lems: kinds.append('six days')
            if 'τέσσαρες' in lems: kinds.append('four days')
            if 'ὀκτώ' in lems: kinds.append('eight days')
            if 'τρεῖς' in lems: kinds.append('three days')
            if 'ἔσχατος' in lems: kinds.append('last day')
            if 'πολύς' in lems: kinds.append('not many days')
        if 'ὥρα' in lems:
            for o in ('δέκατος', 'ἕκτος', 'ἕβδομος', 'τρίτος'):
                if o in lems: kinds.append(f'hour: {o}')
        for l, k in [('πάσχα', 'Passover'), ('σκηνοπηγία', 'Tabernacles'), ('ἐγκαίνια', 'Dedication'),
                     ('ἑορτή', 'feast'), ('σάββατον', 'sabbath/week'), ('παρασκευή', 'Preparation'),
                     ('ὀψία', 'evening'), ('πρωΐ', 'early morning'), ('πρωΐα', 'early morning'), ('νύξ', 'night'),
                     ('χειμών', 'winter'), ('ἔτος', 'years'), ('τετράμηνος', 'four months')]:
            if l in lems: kinds.append(k)
        if 'ὥρα' in lems and not any(k.startswith('hour:') for k in kinds):
            kinds.append('hour (non-clock)')
        markers.append({'ref': f'{c}:{v}', 'kinds': kinds, 'greek': txt})
    counts = Counter(k for m in markers for k in m['kinds'])
    # the inaugural week (B3)
    week = []
    for ref in ['1:19', '1:29', '1:35', '1:39', '1:43', '2:1']:
        c, v = map(int, ref.split(':'))
        week.append({'ref': ref, 'greek': ' '.join(w[0] for w in byv[(c, v)])[:90]})
    # epaurion frequency across Gospels/Acts
    freq = {}
    for fn, nm in [('61-Mt', 'Matt'), ('62-Mk', 'Mark'), ('63-Lk', 'Luke'), ('64-Jn', 'John'), ('65-Ac', 'Acts')]:
        lem = [ln.split()[6] for ln in open(os.path.join(texts, 'sblgnt', fn + '-morphgnt.txt'), encoding='utf-8')]
        freq[nm] = {'epaurion': lem.count('ἐπαύριον'), 'words': len(lem), 'per_1000': 1000 * lem.count('ἐπαύριον') / len(lem),
                    'pascha': lem.count('πάσχα'), 'heorte': lem.count('ἑορτή')}
    return {'markers': markers, 'kind_counts': dict(counts), 'n_marker_verses': len(markers),
            'inaugural_week_verses': week, 'cross_gospel': freq}


# ---------------- astronomy ----------------
def jd_from_julian(y, m, d):
    if m <= 2:
        y -= 1; m += 12
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d - 1524.5


def julian_from_jd(jd):
    jd = jd + 0.5
    Z = int(math.floor(jd)); F = jd - Z
    A = Z
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E) + F
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715
    return year, month, day


def weekday_of_jd(jd):
    return int(math.floor(jd + 1.5)) % 7  # 0 = Sunday


def moon_phase_jde(k, full=False):
    T = k / 1236.85
    jde = 2451550.09766 + 29.530588861 * k + 0.00015437 * T ** 2 - 0.000000150 * T ** 3 + 0.00000000073 * T ** 4
    E = 1 - 0.002516 * T - 0.0000074 * T ** 2
    rad = math.radians
    M = rad(2.5534 + 29.10535670 * k - 0.0000014 * T ** 2 - 0.00000011 * T ** 3)
    Mp = rad(201.5643 + 385.81693528 * k + 0.0107582 * T ** 2 + 0.00001238 * T ** 3 - 0.000000058 * T ** 4)
    F = rad(160.7108 + 390.67050284 * k - 0.0016118 * T ** 2 - 0.00000227 * T ** 3 + 0.000000011 * T ** 4)
    Om = rad(124.7746 - 1.56375588 * k + 0.0020672 * T ** 2 + 0.00000215 * T ** 3)
    s = math.sin
    if not full:
        c = [-0.40720 * s(Mp), 0.17241 * E * s(M), 0.01608 * s(2 * Mp), 0.01039 * s(2 * F), 0.00739 * E * s(Mp - M),
             -0.00514 * E * s(Mp + M), 0.00208 * E * E * s(2 * M), -0.00111 * s(Mp - 2 * F), -0.00057 * s(Mp + 2 * F),
             0.00056 * E * s(2 * Mp + M), -0.00042 * s(3 * Mp), 0.00042 * E * s(M + 2 * F), 0.00038 * E * s(M - 2 * F),
             -0.00024 * E * s(2 * Mp - M), -0.00017 * s(Om)]
    else:
        c = [-0.40614 * s(Mp), 0.17302 * E * s(M), 0.01614 * s(2 * Mp), 0.01043 * s(2 * F), 0.00734 * E * s(Mp - M),
             -0.00515 * E * s(Mp + M), 0.00209 * E * E * s(2 * M), -0.00111 * s(Mp - 2 * F), -0.00057 * s(Mp + 2 * F),
             0.00056 * E * s(2 * Mp + M), -0.00042 * s(3 * Mp), 0.00042 * E * s(M + 2 * F), 0.00038 * E * s(M - 2 * F),
             -0.00024 * E * s(2 * Mp - M), -0.00017 * s(Om)]
    return jde + sum(c)


def delta_t_days(year):
    u = (year - 1820) / 100
    return (-20 + 32 * u * u) / 86400


def equinox_jd(year):
    Y = year / 1000
    return 1721139.29189 + 365242.13740 * Y + 0.06134 * Y ** 2 + 0.00111 * Y ** 3 - 0.00071 * Y ** 4


SUNSET_UT = 15.67 / 24  # Jerusalem sunset late March / April, about 18:00 local mean time


def nisan_for_year(year, vis_hours, rule='14_after_equinox'):
    """Return dict for Nisan of a given AD year (astronomical year == AD year for AD)."""
    eq = equinox_jd(year) - delta_t_days(year)
    k0 = math.floor((year - 2000) * 12.3685) - 4
    cands = []
    for k in range(k0, k0 + 20):
        conj = moon_phase_jde(k) - delta_t_days(year)  # UT
        # evening of first visibility: first sunset with age >= vis_hours
        day0 = math.floor(conj + 0.5) - 0.5  # 0h UT of the conjunction date
        ev = day0 + SUNSET_UT
        while (ev - conj) * 24 < vis_hours:
            ev += 1
        nisan1_civil = ev + 0.5  # daylight day after the visibility evening (noon UT)
        n14 = nisan1_civil + 13
        cands.append((k, conj, ev, nisan1_civil, n14))
    if rule == '14_after_equinox':
        sel = [c for c in cands if c[4] >= eq][0]
    else:  # 15 Nisan on/after equinox
        sel = [c for c in cands if c[4] + 1 >= eq][0]
    k, conj, ev, n1, n14 = sel
    y, m, d = julian_from_jd(n14)
    return {'conj_ut': julian_from_jd(conj), 'nisan14': f'{y}-{m:02d}-{int(d):02d}', 'weekday14': WEEKDAY[weekday_of_jd(n14)],
            'weekday15': WEEKDAY[(weekday_of_jd(n14) + 1) % 7]}


def run_B2():
    out = {}
    # positive controls
    jde = moon_phase_jde(-283)
    out['meeus_49a'] = {'computed_jde': jde, 'reference_jde': 2443192.65118, 'diff_minutes': (jde - 2443192.65118) * 1440}
    k = math.floor((33 - 2000) * 12.3685)
    fm = None
    for kk in range(k - 3, k + 6):
        j = moon_phase_jde(kk + 0.5, full=True) - delta_t_days(33)
        y, m, d = julian_from_jd(j)
        if y == 33 and m in (3, 4):
            if fm is None or abs(m * 31 + d - (4 * 31 + 3)) < abs(fm[1] * 31 + fm[2] - (4 * 31 + 3)):
                fm = (y, m, d)
    out['AD33_full_moon'] = {'computed': f'{fm[0]}-{fm[1]:02d}-{fm[2]:.2f} UT', 'reference': '33-04-03 (lunar eclipse, Humphreys & Waddington 1983)'}
    out['equinox_AD30'] = julian_from_jd(equinox_jd(30))
    # lunar table
    tab = {}
    for vis in (18, 24, 30):
        for rule in ('14_after_equinox', '15_after_equinox'):
            for y in range(26, 37):
                tab.setdefault(str(y), {})[f'vis{vis}h_{rule}'] = nisan_for_year(y, vis, rule)
    out['nisan_table'] = tab
    fri = defaultdict(list)
    for y, d in tab.items():
        for key, v in d.items():
            if v['weekday14'] == 'Fri':
                fri[y].append(key)
    out['years_with_14Nisan_Friday'] = {y: len(v) for y, v in fri.items()}
    out['n_variants_per_year'] = 6
    # model scoring
    # markers: True=consistent, False=contradiction, None=undetermined
    out['markers'] = {
        '19:31,42 + 20:1 crucifixion day = Preparation (Friday), next day Sabbath': 'fixes weekday Friday',
        '18:28 Passover meal not yet eaten on crucifixion morning': '',
        '19:14 crucifixion day = Preparation of the Passover (14th)': '',
        '19:31 that Sabbath was a great day (Sabbath = 15th)': '',
        '13:1-2 supper before the feast of Passover': '',
        '13:30-18:28 supper, arrest, trial, cross form one continuous night and day': '',
        '12:1 six days before the Passover (arrival at Bethany)': '',
        '5:1,9 an unnamed feast whose day was a Sabbath': '',
        '10:22 feast of Dedication observed in Jerusalem': '',
    }
    S = {}  # 364-day calendar: 14/I Tue, 15/I Wed
    S['19:31,42 + 20:1 crucifixion day = Preparation (Friday), next day Sabbath'] = None
    S['18:28 Passover meal not yet eaten on crucifixion morning'] = False  # meal Tue night, three days earlier
    S['19:14 crucifixion day = Preparation of the Passover (14th)'] = False  # Friday = 17/I
    S['19:31 that Sabbath was a great day (Sabbath = 15th)'] = False  # Sabbath = 18/I (a festival-week sabbath; weak)
    S['13:1-2 supper before the feast of Passover'] = True
    S['13:30-18:28 supper, arrest, trial, cross form one continuous night and day'] = True
    S['12:1 six days before the Passover (arrival at Bethany)'] = None
    S['5:1,9 an unnamed feast whose day was a Sabbath'] = None  # only inside the festival weeks
    S['10:22 feast of Dedication observed in Jerusalem'] = False  # not in the 364-day festival lists
    L = {k: True for k in S}
    L['19:31,42 + 20:1 crucifixion day = Preparation (Friday), next day Sabbath'] = None
    L['12:1 six days before the Passover (arrival at Bethany)'] = None
    L['5:1,9 an unnamed feast whose day was a Sabbath'] = None
    J = dict(L)  # Jaubert: supper Tuesday night (364 Passover), crucifixion Friday 14 Nisan (official)
    J['13:30-18:28 supper, arrest, trial, cross form one continuous night and day'] = False
    J['18:28 Passover meal not yet eaten on crucifixion morning'] = True  # official Passover still ahead
    scores = {}
    for nm, mdl in [('L official lunar, crucifixion Fri 14 Nisan', L), ('S 364-day calendar', S),
                    ('J Jaubert hybrid (supper Tue by 364, cross Fri by lunar)', J)]:
        scores[nm] = {'consistent': sum(v is True for v in mdl.values()), 'contradicted': sum(v is False for v in mdl.values()),
                      'undetermined': sum(v is None for v in mdl.values()),
                      'detail': {k: v for k, v in mdl.items()}}
    out['model_scores'] = scores
    out['assumptions'] = [
        'John\'s "Preparation" in 19:31,42 means Friday (day before the weekly Sabbath), as in Mark 15:42.',
        '"Eat the Passover" in 18:28 means the Passover meal of the evening that begins 15 Nisan.',
        'Lunar calendar: month begins at the evening of first crescent visibility in Jerusalem; age thresholds 18/24/30 h; '
        'Nisan chosen so that 14 (or 15) Nisan falls on/after the vernal equinox; no allowance for cloud or for a '
        'barley-based intercalation, so each year carries +/-1 day and +/-1 month uncertainty.',
        '364-day calendar: 1/I Wednesday (Jaubert 1953, confirmed here by 4Q320/4Q326); no intercalation assumed (weekdays '
        'are fixed whatever the intercalation).',
    ]
    return out


def main():
    texts = sys.argv[1] if len(sys.argv) > 1 else '/home/user/The-Sound/sources/texts'
    outdir = sys.argv[2] if len(sys.argv) > 2 else HERE
    rng = np.random.default_rng(SEED)
    res = {}
    res['A0'] = run_A0(os.path.join(texts, 'sefer_yetzirah'))
    res['A'] = run_A(texts, res['A0'], rng)
    res['B0'] = run_B0(texts)
    res['B1'] = run_B1(texts)
    res['B2'] = run_B2()
    tests = res['A'].pop('tests')
    tests.append(('B0', 'DSS courses', 'course rotation vs chance', res['B0']['dss_course_p_binomial']))
    q = bh([t[3] for t in tests])
    res['bh_family'] = [{'part': t[0], 'set': t[1], 'profile': t[2], 'p': t[3], 'q': qq} for t, qq in zip(tests, q)]
    res['n_tests'] = len(tests)
    res['n_q05'] = int(sum(qq < 0.05 for qq in q))
    with open(os.path.join(outdir, 'results.json'), 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    print('tests', len(tests), 'q<0.05:', res['n_q05'])


if __name__ == '__main__':
    main()
