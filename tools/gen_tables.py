#!/usr/bin/env python3
"""Generate AGA Hyperdrive Engine tables."""
import math, sys

def rgb12_to_rgb24(c):
    return (((c >> 8) & 15) * 17, ((c >> 4) & 15) * 17, (c & 15) * 17)

def rgb24_to_aga_long(rgb):
    r, g, b = rgb
    hi = ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
    lo = ((r & 15) << 8) | ((g & 15) << 4) | (b & 15)
    return (hi << 16) | lo

def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))

def ramp(stops, t):
    if t <= stops[0][0]:
        return rgb12_to_rgb24(stops[0][1])
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if t <= b:
            local = (t - a) / (b - a)
            local = local * local * (3 - 2 * local)
            return mix(rgb12_to_rgb24(ca), rgb12_to_rgb24(cb), local)
    return rgb12_to_rgb24(stops[-1][1])

def longs(vals, per=4):
    out = []
    for i in range(0, len(vals), per):
        out.append("        dc.l " + ",".join(f"${v:08X}" for v in vals[i:i+per]))
    return "\n".join(out)

def words(vals, per=8):
    out = []
    for i in range(0, len(vals), per):
        out.append("        dc.w " + ",".join(f"${v & 0xffff:04X}" for v in vals[i:i+per]))
    return "\n".join(out)

def plasma_palette():
    stops = [
        (0.00, 0x001), (0.10, 0x014), (0.23, 0x037), (0.38, 0x07C),
        (0.54, 0x5FF), (0.70, 0xB5F), (0.84, 0xF4B), (1.00, 0xFFE),
    ]
    return [rgb24_to_aga_long(ramp(stops, i / 255)) for i in range(256)]

def copper_gradient():
    vals = []
    for y in range(256):
        t = y / 255
        wave = 0.5 + 0.5 * math.sin(t * math.tau * 3.0 + math.sin(t * math.tau) * 0.7)
        rgb = ramp([(0,0x001),(0.35,0x035),(0.65,0x09F),(1,0xF7D)], (t * 0.65 + wave * 0.35))
        vals.append(rgb24_to_aga_long(rgb))
    return vals

def sine_table(scale=127):
    return [round(math.sin(i * math.tau / 256) * scale) for i in range(256)]

def tunnel_table():
    vals = []
    for i in range(192):
        z = 32 + i * 3
        vals.append(round(256 * 192 / z))
    return vals

def palette_words():
    return [0x001,0x013,0x025,0x047,0x06A,0x09D,0x4DF,0xCFF,
            0x112,0x302,0x714,0xB25,0xF47,0xFC6,0xFFF,0xF7D]

MAP = {
    "plasma_palette": lambda: longs(plasma_palette()),
    "copper_gradient": lambda: longs(copper_gradient()),
    "sine": lambda: words(sine_table()),
    "tunnel": lambda: words(tunnel_table()),
    "palette": lambda: words(palette_words()),
}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in MAP:
        sys.exit("usage: gen_tables.py " + "|".join(MAP))
    print(MAP[sys.argv[1]]())
