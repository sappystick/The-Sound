#!/usr/bin/env python3
"""Dawn (heliacal) risings of the stars named in scripture, over Jerusalem in 30 CE.

Star positions: J2000 catalogue values, moved back by proper motion and precessed to the
epoch with the IAU 1976 (Lieske) angles.  Sun: low-precision solar theory (Meeus ch. 25).
Heliacal rising = first morning, after the star's conjunction with the Sun, on which the star
stands >= 1 deg above the horizon at the moment the Sun is still `arcus visionis` degrees below
it (brighter stars need less darkness).  Expect +/- 3 days from these simplifications.
Dates are given in the Julian calendar, the calendar of the Roman world at the time.
"""
import json, math
LAT, LON = 31.778, 35.235            # Jerusalem, Temple Mount
YEAR = 30
STARS = {  # name: (RA deg, Dec deg, V mag, pmRA* mas/yr, pmDec mas/yr, scripture)
    "Pleiades (Alcyone) - Kimah": (56.871, 24.105, 2.9, 19.3, -43.7, "Job 9:9; 38:31; Amos 5:8"),
    "Orion's Belt (Alnilam) - Kesil": (84.053, -1.202, 1.7, 1.5, -1.1, "Job 9:9; 38:31; Amos 5:8"),
    "Betelgeuse (Orion)": (88.793, 7.407, 0.5, 27.5, 11.3, ""),
    "Sirius": (101.287, -16.716, -1.46, -546.0, -1223.1, "Egyptian Sopdet, herald of the Nile flood"),
    "Arcturus": (213.915, 19.182, -0.05, -1093.4, -1999.4, "often read as 'Ash/Ayish' in older translations"),
    "Spica (Virgo)": (201.298, -11.161, 0.98, -42.4, -30.7, "the Virgin's ear of grain"),
}
AV = lambda m: 10.0 + 1.2 * m if m > 0 else 10.0 + 1.6 * m   # arcus visionis (deg) by magnitude


def jd_julian(y, m, d):  # Julian-calendar date -> JD
    if m <= 2: y -= 1; m += 12
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d - 1524.5


def julian_date(jd):
    z = int(jd + 0.5); a = z; b = a + 1524; c = int((b - 122.1) / 365.25); d = int(365.25 * c)
    e = int((b - d) / 30.6001); day = b - d - int(30.6001 * e); m = e - 1 if e < 14 else e - 13
    return m, day


MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
T = (jd_julian(YEAR, 7, 1) - 2451545.0) / 36525
zeta = math.radians((2306.2181 * T + 0.30188 * T * T + 0.017998 * T ** 3) / 3600)
z = math.radians((2306.2181 * T + 1.09468 * T * T + 0.018203 * T ** 3) / 3600)
th = math.radians((2004.3109 * T - 0.42665 * T * T - 0.041833 * T ** 3) / 3600)
eps = math.radians(23.439291 - 0.0130042 * T)
yrs = YEAR - 2000


def star_of_date(ra, dec, pmra, pmdec):
    dec0 = dec + pmdec * yrs / 3.6e6
    ra0 = ra + pmra * yrs / 3.6e6 / math.cos(math.radians(dec))
    a, d = math.radians(ra0), math.radians(dec0)
    A = math.cos(d) * math.sin(a + zeta)
    B = math.cos(th) * math.cos(d) * math.cos(a + zeta) - math.sin(th) * math.sin(d)
    C = math.sin(th) * math.cos(d) * math.cos(a + zeta) + math.cos(th) * math.sin(d)
    return (math.atan2(A, B) + z) % (2 * math.pi), math.asin(C)


def sun(jd):
    n = jd - 2451545.0
    L = math.radians((280.460 + 0.9856474 * n) % 360); g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2 * g)
    return math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam)) % (2 * math.pi), math.asin(math.sin(eps) * math.sin(lam)), lam


def alt(ra, dec, jd):
    gmst = math.radians((280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360)
    H = gmst + math.radians(LON) - ra; p = math.radians(LAT)
    return math.degrees(math.asin(math.sin(p) * math.sin(dec) + math.cos(p) * math.cos(dec) * math.cos(H)))


def sun_alt(jd):
    r, d, _ = sun(jd); return alt(r, d, jd)


def morning_moment(jd0, target):  # UT jd on this date when the Sun climbs through `target` altitude
    t = jd0 - 0.5 + (3 - LON / 15) / 24 - 0.25   # search from local ~midnight
    prev = sun_alt(t)
    for k in range(1, 400):
        tt = t + k * (2 / 1440); a = sun_alt(tt)
        if prev < target <= a: return tt
        prev = a
    return None


out = {}
# solar markers of the year
lam_prev = None; marks = {}
for d in range(0, 366):
    jd = jd_julian(YEAR, 1, 1) + d + 0.5
    lam = math.degrees(sun(jd)[2]) % 360
    if lam_prev is not None:
        for name, L0 in (("spring equinox", 0), ("summer solstice", 90), ("autumn equinox", 180), ("winter solstice", 270)):
            if (lam_prev - L0) % 360 > 300 and (lam - L0) % 360 < 60: marks[name] = "%s %d" % (MON[julian_date(jd)[0] - 1], julian_date(jd)[1])
    lam_prev = lam
out["solar"] = marks
print("Solar year", YEAR, "CE (Julian calendar):", marks)
for name, (ra, dec, mag, pmra, pmdec, ref) in STARS.items():
    r, dd = star_of_date(ra, dec, pmra, pmdec)
    av = AV(mag)
    # conjunction: day the Sun's RA passes the star's RA
    start = None
    for d in range(0, 366):
        jd = jd_julian(YEAR, 1, 1) + d + 0.5
        if abs(((sun(jd)[0] - r + math.pi) % (2 * math.pi)) - math.pi) < math.radians(1.0): start = d; break
    rise = None
    for d in range(start, start + 120):
        jd0 = jd_julian(YEAR, 1, 1) + d
        mm = morning_moment(jd0 + 0.5, -av)
        if mm and alt(r, dd, mm) >= 1.0: rise = julian_date(jd0 + 0.5); break
    circ = math.degrees(dd) > 90 - LAT
    out[name] = dict(dawn_rising="%s %d" % (MON[rise[0] - 1], rise[1]) if rise else None, dec_of_date=round(math.degrees(dd), 2),
                     arcus_visionis=round(av, 1), scripture=ref)
    print(f"{name:34s} dec {math.degrees(dd):+6.2f}  first dawn rising: {MON[rise[0] - 1]} {rise[1]:2d}  ({ref})")
# the Bear: circumpolar?
for nm, dec in (("Dubhe (Great Bear)", 61.75), ("Alkaid (Great Bear tail)", 49.31), ("Polaris", 89.26)):
    r, dd = star_of_date(0, dec, 0, 0) if False else (None, math.radians(dec))
for nm, (ra, dec) in {"Dubhe (Great Bear)": (165.932, 61.751), "Alkaid (Great Bear tail)": (206.885, 49.313),
                      "Polaris": (37.955, 89.264), "Kochab (pole star region in antiquity)": (222.676, 74.156)}.items():
    r, dd = star_of_date(ra, dec, 0, 0)
    print(f"{nm:34s} dec {math.degrees(dd):+6.2f}  never sets at Jerusalem: {math.degrees(dd) > 90 - LAT}")
    out[nm] = dict(dec_of_date=round(math.degrees(dd), 2), circumpolar=math.degrees(dd) > 90 - LAT)
json.dump(out, open("star_risings_results.json", "w"), indent=1, ensure_ascii=False)
