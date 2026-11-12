"""Minimal Text-Fabric .tf node-feature reader (stdlib only)."""
def read_feature(path):
    vals = {}
    n = 0
    body = False
    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if not body:
                if line == '':
                    body = True
                continue
            if '\t' in line:
                key, v = line.split('\t', 1)
                if '-' in key and ',' not in key:
                    a, b = key.split('-'); a, b = int(a), int(b)
                    for k in range(a, b + 1):
                        vals[k] = v
                    n = b
                    continue
                if ',' in key:
                    for part in key.split(','):
                        if '-' in part:
                            a, b = map(int, part.split('-'))
                            for k in range(a, b + 1): vals[k] = v
                            n = b
                        else:
                            n = int(part); vals[n] = v
                    continue
                n = int(key)
            else:
                v = line
                n += 1
            vals[n] = v
    return vals


def read_oslots(path, max_slot):
    """Return dict node -> (first_slot, last_slot)."""
    out = {}
    n = max_slot
    body = False
    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if not body:
                if line == '':
                    body = True
                continue
            if '\t' in line:
                key, v = line.split('\t', 1); n = int(key)
            else:
                v = line; n += 1
            nums = []
            for part in v.split(','):
                if '-' in part:
                    a, b = part.split('-'); nums += [int(a), int(b)]
                else:
                    nums.append(int(part))
            out[n] = (min(nums), max(nums))
    return out


def dss_lines(tfdir, scroll_prefixes, max_slot=1430241,
              line_range=(1552973, 1605867), word_range=(1606869, 2107863)):
    """Return list of (scroll, fragment, line, [word glyphs]) for scrolls whose
    acronym starts with one of scroll_prefixes, in text order."""
    import bisect
    sc = read_feature(tfdir + 'scroll.tf'); fr = read_feature(tfdir + 'fragment.tf')
    ln = read_feature(tfdir + 'line.tf'); gl = read_feature(tfdir + 'glyph.tf')
    sl = read_oslots(tfdir + 'oslots.tf', max_slot)
    lines = [n for n in range(line_range[0], line_range[1] + 1)
             if sc.get(n, '').startswith(tuple(scroll_prefixes))]
    starts = sorted((sl[n][0], n) for n in lines)
    keys = [s for s, _ in starts]
    words = {n: [] for n in lines}
    for w in range(word_range[0], word_range[1] + 1):
        if w not in sl:
            continue
        a, b = sl[w]
        i = bisect.bisect_right(keys, a) - 1
        if i < 0:
            continue
        ln_node = starts[i][1]
        if sl[ln_node][0] <= a <= sl[ln_node][1]:
            words[ln_node].append(gl.get(w, ''))
    return [(sc[n], fr.get(n, ''), ln.get(n, ''), words[n]) for _, n in starts]
