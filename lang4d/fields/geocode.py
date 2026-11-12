#!/usr/bin/env python3
"""KLIMATA: every place on Earth as a short KANON word that can be spoken, heard, repaired and drawn.

Each syllable refines the cell: one consonant (12 choices) and one vowel (7 choices) split the current cell into
12 x 7 = 84. The two roles alternate, so the cells stay roughly square:
  odd syllables:  consonant = longitude slice (12, like the hours and months)  vowel = latitude slice (7, like Ptolemy's
                  seven klimata, the bands of latitude of ancient geography)
  even syllables: consonant = latitude slice                                  vowel = longitude slice
Precision: 3 syllables ~ city district, 5 ~ street block, 7 ~ 5 m square, 8 ~ 0.7 m.
Nearby places share their first syllables (unlike random three-word addresses), so a code says where it is coarsely
before it says where it is exactly. Five Reed-Solomon words repair any two misheard syllables.
Usage: python3 geocode.py"""
import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); import kanon as K, skins as S
def encode(lat, lon, n=7):
    la0, la1, lo0, lo1 = -90.0, 90.0, -180.0, 180.0; syl = []
    for k in range(n):
        if k % 2 == 0:   # consonant: longitude in 12; vowel: latitude in 7
            c = min(11, int((lon - lo0) / (lo1 - lo0) * 12)); lo0, lo1 = lo0 + c * (lo1 - lo0) / 12, lo0 + (c + 1) * (lo1 - lo0) / 12
            v = min(6, int((lat - la0) / (la1 - la0) * 7)); la0, la1 = la0 + v * (la1 - la0) / 7, la0 + (v + 1) * (la1 - la0) / 7
        else:            # consonant: latitude in 12; vowel: longitude in 7
            c = min(11, int((lat - la0) / (la1 - la0) * 12)); la0, la1 = la0 + c * (la1 - la0) / 12, la0 + (c + 1) * (la1 - la0) / 12
            v = min(6, int((lon - lo0) / (lo1 - lo0) * 7)); lo0, lo1 = lo0 + v * (lo1 - lo0) / 7, lo0 + (v + 1) * (lo1 - lo0) / 7
        syl.append(c * 7 + v)
    return syl
def decode(syl):
    la0, la1, lo0, lo1 = -90.0, 90.0, -180.0, 180.0
    for k, s in enumerate(syl):
        c, v = divmod(s, 7)
        if k % 2 == 0: lo0, lo1 = lo0 + c * (lo1 - lo0) / 12, lo0 + (c + 1) * (lo1 - lo0) / 12; la0, la1 = la0 + v * (la1 - la0) / 7, la0 + (v + 1) * (la1 - la0) / 7
        else: la0, la1 = la0 + c * (la1 - la0) / 12, la0 + (c + 1) * (la1 - la0) / 12; lo0, lo1 = lo0 + v * (lo1 - lo0) / 7, lo0 + (v + 1) * (lo1 - lo0) / 7
    return (la0 + la1) / 2, (lo0 + lo1) / 2, (la1 - la0), (lo1 - lo0)
def text(syl, parity=True):
    w = "".join(K.CONS[s // 7] + K.VOWELS[s % 7] for s in syl)
    return w + (" =" + "-".join(K._pword(p) for p in K.rs_parity(syl)) if parity else "")
def english(syl): return " ".join(S.EN_ENC[K.CONS[s // 7] + K.VOWELS[s % 7]] for s in syl) + " check " + " ".join("-".join(S._word(K._pword(p), S.EN_ENC)) for p in K.rs_parity(syl))
def metres(dlat, dlon, lat): return dlat * 111320, dlon * 111320 * math.cos(math.radians(lat))
def hear(syl_heard, parity):
    fixed, n = K.rs_correct(parity, syl_heard); return fixed, n
if __name__ == "__main__":
    places = {"Jerusalem, Temple Mount": (31.7781, 35.2354), "Great Pyramid of Giza": (29.9792, 31.1342), "Ephesus (John's tradition)": (37.9395, 27.3417),
              "Patmos": (37.3088, 26.5464), "Kennedy Space Center LC-39A": (28.6083, -80.6041), "Null Island": (0.0, 0.0)}
    for n in (3, 5, 7, 8):
        la, lo, dla, dlo = decode(encode(31.7781, 35.2354, n)); my, mx = metres(dla, dlo, 31.78); print(f"   {n} syllables: cell about {my:,.1f} m x {mx:,.1f} m")
    for name, (la, lo) in places.items():
        s = encode(la, lo); print(f"{name:30s} {text(s):40s} {english(s)}")
    # nearby places share prefixes
    a, b = encode(31.7781, 35.2354), encode(31.7767, 35.2345)   # Temple Mount and the Western Wall plaza, ~200 m apart
    print("   Temple Mount", text(a, False), "| Western Wall", text(b, False), "| shared prefix:", sum(1 for _ in __import__('itertools').takewhile(lambda p: p[0] == p[1], zip(a, b))), "syllables")
    # accuracy and repair on random places
    R = random.Random(1); worst = 0; rep = 0
    for _ in range(5000):
        la, lo = math.degrees(math.asin(R.uniform(-1, 1))), R.uniform(-180, 180); s = encode(la, lo); dla, dlo = decode(s)[:2]
        worst = max(worst, max(*metres(abs(dla - la), abs(dlo - lo), la)))
        par = K.rs_parity(s); h = list(s)
        for i in R.sample(range(7), 2): h[i] = (h[i] + R.randrange(1, 84)) % 84
        rep += hear(h, par)[0] == s
    print(f"   5,000 random places: worst position error {worst:.2f} m (half a 7-syllable cell); two misheard syllables repaired in {rep}/5000")
