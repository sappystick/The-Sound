#!/usr/bin/env python3
"""KANON units: physical dimensions as chords of the seven planes.

There are exactly seven SI base units, and KANON has exactly seven vowels. Each base unit gets a vowel:
  s  -> i  (the Sun keeps time)                 m  -> a  (moon and measure share one Indo-European root, *me-)
  kg -> o                                       A  -> e  (Mercury, the messenger: current)
  K  -> u                                       mol -> y          cd -> w
A dimension is a vector of seven integer exponents, so every quantity has a spoken DIMENSION WORD: for each base unit
with a non-zero exponent, one syllable per power, p (project) for a positive power and n (negate) for a negative one.
  speed m/s     -> pani          acceleration m/s^2 -> panini          force kg m/s^2 -> popanini
Equal words mean equal dimensions, so a listener can check units by ear. The arithmetic below refuses to add unlike
dimensions, to take the logarithm of a dimensioned quantity, and so on: the classic unit errors become impossible.
Usage: python3 units.py   (runs the checks)"""
import math, re
BASE = ["s", "m", "kg", "A", "K", "mol", "cd"]; VOWEL = dict(zip(BASE, "iaoeuyw"))
ORDER = ["kg", "m", "s", "A", "K", "mol", "cd"]          # spoken order: mass, length, time, then the rest
def _d(**kw): return tuple(kw.get(b, 0) for b in BASE)
UNITS = {  # name: (scale to SI, dimension)
 "s": (1, _d(s=1)), "m": (1, _d(m=1)), "kg": (1, _d(kg=1)), "A": (1, _d(A=1)), "K": (1, _d(K=1)), "mol": (1, _d(mol=1)), "cd": (1, _d(cd=1)),
 "g": (1e-3, _d(kg=1)), "km": (1e3, _d(m=1)), "min": (60, _d(s=1)), "h": (3600, _d(s=1)), "day": (86400, _d(s=1)),
 "N": (1, _d(kg=1, m=1, s=-2)), "J": (1, _d(kg=1, m=2, s=-2)), "W": (1, _d(kg=1, m=2, s=-3)), "Pa": (1, _d(kg=1, m=-1, s=-2)),
 "Hz": (1, _d(s=-1)), "C": (1, _d(A=1, s=1)), "V": (1, _d(kg=1, m=2, s=-3, A=-1)), "ohm": (1, _d(kg=1, m=2, s=-3, A=-2)),
 "T": (1, _d(kg=1, s=-2, A=-1)), "eV": (1.602176634e-19, _d(kg=1, m=2, s=-2)), "au": (1.495978707e11, _d(m=1)),
 "lbf": (4.4482216152605, _d(kg=1, m=1, s=-2)), "lb": (0.45359237, _d(kg=1)), "ft": (0.3048, _d(m=1)), "cubit": (0.5236, _d(m=1)), "bit": (1, _d()), "rad": (1, _d()), "1": (1, _d()),
}
def parse_unit(u):
    """'kg m/s^2' or 'm s^-2' -> (scale, dimension)."""
    scale, dim = 1.0, [0] * 7
    num, _, den = u.replace("·", " ").replace("*", " ").partition("/")
    for part, sign in ((num, 1), (den, -1)):
        for tok in part.split():
            if tok == "1": continue
            m = re.fullmatch(r"([A-Za-z]+)(?:\^?(-?\d+))?", tok)
            if not m or m.group(1) not in UNITS: raise ValueError(f"unknown unit {tok!r}")
            p = sign * int(m.group(2) or 1); sc, dd = UNITS[m.group(1)]; scale *= sc ** p
            for k in range(7): dim[k] += p * dd[k]
    return scale, tuple(dim)
def dim_word(dim):
    w = "".join(("p" if dim[BASE.index(b)] > 0 else "n") + VOWEL[b] for b in ORDER for _ in range(abs(dim[BASE.index(b)])))
    return w or "ki"            # dimensionless: ki
def dim_name(dim):
    for n, (sc, d) in UNITS.items():
        if d == dim and sc == 1 and n not in ("rad", "bit", "1"): return n
    parts = [f"{b}^{dim[BASE.index(b)]}" if dim[BASE.index(b)] != 1 else b for b in ORDER if dim[BASE.index(b)]]
    return " ".join(parts) or "1"
class DimensionError(TypeError): pass
class Q:
    """A quantity: a value in SI with a dimension."""
    __slots__ = ("v", "d")
    def __init__(self, v, unit="1"):
        if isinstance(unit, tuple): self.v, self.d = float(v), unit
        else: sc, d = parse_unit(unit); self.v, self.d = float(v) * sc, d
    def _same(self, o, op):
        o = o if isinstance(o, Q) else Q(o)
        if o.d != self.d: raise DimensionError(f"cannot {op} {dim_name(self.d)} ({dim_word(self.d)}) and {dim_name(o.d)} ({dim_word(o.d)})")
        return o
    def __add__(self, o): o = self._same(o, "add"); return Q(self.v + o.v, self.d)
    def __sub__(self, o): o = self._same(o, "subtract"); return Q(self.v - o.v, self.d)
    def __mul__(self, o): o = o if isinstance(o, Q) else Q(o); return Q(self.v * o.v, tuple(a + b for a, b in zip(self.d, o.d)))
    __rmul__ = __mul__
    def __truediv__(self, o): o = o if isinstance(o, Q) else Q(o); return Q(self.v / o.v, tuple(a - b for a, b in zip(self.d, o.d)))
    def __rtruediv__(self, o): return Q(o) / self
    def __pow__(self, p):
        if any((a * p) % 1 for a in self.d): raise DimensionError(f"{dim_name(self.d)} to the power {p} has no whole dimension")
        return Q(self.v ** p, tuple(int(a * p) for a in self.d))
    def __lt__(self, o): o = self._same(o, "compare"); return self.v < o.v
    def __gt__(self, o): o = self._same(o, "compare"); return self.v > o.v
    def to(self, unit):
        sc, d = parse_unit(unit)
        if d != self.d: raise DimensionError(f"cannot express {dim_name(self.d)} in {unit}")
        return self.v / sc
    def __repr__(self): return f"{self.v:.6g} {dim_name(self.d)} [{dim_word(self.d)}]"
def _dimless(q, f):
    q = q if isinstance(q, Q) else Q(q)
    if any(q.d): raise DimensionError(f"{f} needs a dimensionless argument, got {dim_name(q.d)} ({dim_word(q.d)})")
    return q.v
def ln(q): return Q(math.log(_dimless(q, "ln")))
def exp(q): return Q(math.exp(_dimless(q, "exp")))
def sqrt(q): return q ** 0.5
G = Q(6.67430e-11, "m^3 kg^-1 s^-2"); g0 = Q(9.80665, "m/s^2"); c = Q(299792458, "m/s"); M_EARTH = Q(5.9722e24, "kg"); R_EARTH = Q(6371, "km")
def checks():
    out = []
    def ok(name, f):
        try: r = f(); out.append((name, "ok", repr(r)))
        except DimensionError as e: out.append((name, "refused", str(e)))
    # rocket equation: dv = Isp g0 ln(m0/mf)
    ok("rocket equation, Isp 311 s, 549 t -> 25.6 t", lambda: Q(311, "s") * g0 * ln(Q(549, "kg") * 1000 / (Q(25.6, "kg") * 1000)))
    ok("circular orbit speed at 400 km", lambda: sqrt(G * M_EARTH / (R_EARTH + Q(400, "km"))))
    ok("kinetic energy of 1 kg at 7.67 km/s", lambda: Q(0.5) * Q(1, "kg") * Q(7.67, "km/s") ** 2)
    ok("photon energy of 500 nm light in eV", lambda: (Q(6.62607015e-34, "J s") * c / Q(500e-9, "m")))
    ok("ERROR: adding a mass to a time", lambda: Q(1, "kg") + Q(1, "s"))
    ok("ERROR: log of a mass ratio left in kg", lambda: ln(Q(549, "kg") - Q(25.6, "kg")))
    ok("ERROR: thrust compared with an energy", lambda: Q(7.6e6, "N") > Q(1, "J"))
    # Mars Climate Orbiter (1999): impulse delivered in lbf s was read as N s. Same DIMENSION (popani), different SCALE,
    # so a dimension check alone cannot catch it; declaring the unit at the interface converts it instead.
    ok("Mars Climate Orbiter: 1 lbf s declared at the interface, expressed in N s", lambda: Q(Q(1, "lbf s").to("N s"), "N s"))
    return out
if __name__ == "__main__":
    for d in [_d(m=1, s=-1), _d(m=1, s=-2), UNITS["N"][1], UNITS["J"][1], UNITS["V"][1], _d()]: print(f"   {dim_name(d):12s} spoken {dim_word(d)}")
    for name, st, r in checks(): print(f"{st:8s} {name}\n         {r}")
