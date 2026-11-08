#!/usr/bin/env python3
"""Resonant modes (standing waves) of ancient sacred rooms, from their recorded dimensions."""
import itertools, json, math, sys
C = 343.0  # m/s at 20 C (speed of sound depends on temperature, not gravity)
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def note(f):
    m = 69 + 12 * math.log2(f / 440); n = round(m); return f"{NOTES[n % 12]}{n // 12 - 1}{'+' if m - n > 0 else '-'}{abs(m - n) * 100:.0f}c"
ROOMS = {  # name: (dims m, description, absorption range)
    "Holy of Holies, 20x20x20 cubits @0.445 m": ((8.9, 8.9, 8.9), (0.04, 0.12)),
    "Holy of Holies, 20x20x20 cubits @0.525 m": ((10.5, 10.5, 10.5), (0.04, 0.12)),
    "Holy Place, 40x20x30 cubits @0.445 m": ((17.8, 8.9, 13.35), (0.04, 0.10)),
    "King's Chamber (granite), 10.47x5.24x5.84 m": ((10.47, 5.24, 5.84), (0.02, 0.04)),
}
out = {}
for name, ((x, y, z), (a1, a2)) in ROOMS.items():
    modes = {}
    for nx, ny, nz in itertools.product(range(0, 12), repeat=3):
        if nx == ny == nz == 0: continue
        f = C / 2 * math.sqrt((nx / x) ** 2 + (ny / y) ** 2 + (nz / z) ** 2)
        if f <= 200: modes.setdefault(round(f, 1), []).append((nx, ny, nz))
    V = x * y * z; S = 2 * (x * y + x * z + y * z)
    rt = [round(0.161 * V / (a * S), 1) for a in (a2, a1)]
    fs = sorted(modes)
    strong = [(f, len(modes[f])) for f in fs if len(modes[f]) >= 3]
    voice = [(f, len(modes[f]), note(f)) for f in fs if 85 <= f <= 160]
    out[name] = dict(volume_m3=round(V), rt60_s=rt, n_modes_below_200=sum(len(v) for v in modes.values()),
                     distinct_freqs_below_200=len(fs), lowest=[(f, note(f)) for f in fs[:4]],
                     strong_degenerate=strong[:8], voice_range_85_160=voice)
    print(f"\n{name}: V={V:.0f} m3, RT60 {rt[0]}-{rt[1]} s, {sum(len(v) for v in modes.values())} modes in {len(fs)} distinct freqs <200 Hz")
    print("  lowest:", [(f, note(f)) for f in fs[:4]])
    print("  degenerate (>=3 modes on one pitch):", [(f, n, note(f)) for f, n in strong[:8]])
    print("  in male chant range 85-160 Hz:", [(f, n, note(f)) for f, n, _ in voice][:12])
json.dump(out, open("room_modes_results.json", "w"), indent=1)
