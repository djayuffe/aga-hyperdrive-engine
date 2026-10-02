#!/usr/bin/env python3
"""Generate deterministic assets for AGA Hyperdrive Engine."""
from pathlib import Path
import hashlib, math, struct, zlib
import gen_tables

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

W, H = 320, 80
SCREEN_H = 256
PAL = [
    0x001, 0x013, 0x025, 0x047, 0x06A, 0x09D, 0x4DF, 0xCFF,
    0x112, 0x302, 0x714, 0xB25, 0xF47, 0xFC6, 0xFFF, 0xF7D,
]
GLYPHS = {
    " ": ["00000"] * 7,
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["11110","00001","00001","01110","10000","10000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["10001","10001","10001","11111","00001","00001","00001"],
    "5": ["11111","10000","10000","11110","00001","00001","11110"],
    "6": ["01110","10000","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","01110"],
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "G": ["01111","10000","10000","10111","10001","10001","01111"],
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "I": ["01110","00100","00100","00100","00100","00100","01110"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
}

def put_text(img, text, x, y, scale, fg, shadow=8):
    h = len(img)
    w = len(img[0]) if h else 0
    for i, ch in enumerate(text):
        g = GLYPHS[ch]
        ox = x + i * 6 * scale
        for gy, row in enumerate(g):
            for gx, bit in enumerate(row):
                if bit != "1":
                    continue
                for yy in range(scale):
                    for xx in range(scale):
                        px, py = ox + gx * scale + xx, y + gy * scale + yy
                        if 0 <= px + 2 < w and 0 <= py + 2 < h:
                            img[py + 2][px + 2] = shadow
                        if 0 <= px < w and 0 <= py < h:
                            edge = gx in (0, 4) or gy in (0, 6)
                            img[py][px] = min(15, fg + (2 if edge else 0))

def logo():
    img = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            t = y / (H - 1)
            if (x + y * 3) % 37 == 0:
                img[y][x] = 7
            elif y < 12:
                img[y][x] = 1
            else:
                img[y][x] = 1 + int(4 * t)
    put_text(img, "HYPERDRIVE", 13, 8, 5, 11)
    put_text(img, "AGA ENGINE", 83, 55, 2, 5)
    for x in range(8, W - 8):
        img[2][x] = 15 if x % 13 == 0 else 12
        img[H - 3][x] = 6 if x % 11 else 15
    return img

def full_screen():
    img = [[0] * W for _ in range(SCREEN_H)]
    lg = logo()
    for y, row in enumerate(lg):
        img[y][:] = row[:]
    # Aurora/plasma band.
    for y in range(86, 190):
        for x in range(W):
            t = (math.sin((x * 0.045) + (y * 0.13)) + math.sin((x + y) * 0.031) + 2) / 4
            img[y][x] = 2 + int(t * 5)
            if (x * 7 + y * 13) % 211 == 0:
                img[y][x] = 14
    # Wire tunnel perspective ribs.
    cx, cy = 160, 138
    for ring in range(7):
        rz = 28 + ring * 15
        w = 34 + ring * 17
        h = 8 + ring * 8
        col = 12 if ring % 2 else 6
        for x in range(cx - w, cx + w + 1):
            for yy in (cy - h, cy + h):
                if 0 <= x < W and 86 <= yy < SCREEN_H:
                    img[yy][x] = col
        for y in range(cy - h, cy + h + 1):
            for xx in (cx - w, cx + w):
                if 0 <= xx < W and 86 <= y < SCREEN_H:
                    img[y][xx] = col
    for a in range(0, 360, 30):
        rad = math.radians(a)
        x2, y2 = int(cx + math.cos(rad) * 135), int(cy + math.sin(rad) * 54)
        steps = max(abs(x2 - cx), abs(y2 - cy), 1)
        for i in range(steps):
            x = int(cx + (x2 - cx) * i / steps)
            y = int(cy + (y2 - cy) * i / steps)
            if 0 <= x < W and 86 <= y < 190:
                img[y][x] = 15 if i % 9 == 0 else 5
    # Sprite/orb-like software art in the static layer.
    for ox, oy, col in [(72, 114, 15), (238, 112, 7), (97, 171, 6), (221, 170, 13)]:
        for dy in range(-10, 11):
            for dx in range(-10, 11):
                d = dx * dx + dy * dy
                if d <= 100:
                    shade = col if d < 40 else max(1, col - 2)
                    img[oy + dy][ox + dx] = shade
    # Scroller/status panel.
    for y in range(198, 226):
        for x in range(W):
            img[y][x] = 1 if y in (198, 225) else 2
    put_text(img, "HYPERDRIVE AGA ENGINE", 22, 203, 2, 5)
    # Floor bars.
    for y in range(232, 256):
        for x in range(W):
            band = (y - 232) // 4
            img[y][x] = [1, 3, 6, 15, 13, 11][band % 6]
    return img

def planes(img, n=4):
    out = bytearray()
    for p in range(n):
        for row in img:
            for xb in range(0, W, 8):
                b = 0
                for bit in range(8):
                    b |= ((row[xb + bit] >> p) & 1) << (7 - bit)
                out.append(b)
    return bytes(out)

def png_rgb(img, scale=3):
    h = len(img)
    w = len(img[0]) if h else 0
    raw_rows = []
    for row in img:
        rb = bytearray()
        for idx in row:
            c = PAL[idx]
            rgb = bytes([((c >> 8) & 15) * 17, ((c >> 4) & 15) * 17, (c & 15) * 17])
            rb += rgb * scale
        raw_rows += [bytes(rb)] * scale
    width, height = w * scale, h * scale
    raw = b"".join(b"\0" + r for r in raw_rows)
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")

def sample_wave(freq, seconds, rate=8287, amp=64, waveform="sine"):
    n = int(seconds * rate)
    data = bytearray()
    for i in range(n):
        ph = (i * freq / rate) % 1.0
        if waveform == "tri":
            v = 4 * abs(ph - 0.5) - 1
        elif waveform == "saw":
            v = 2 * ph - 1
        elif waveform == "noise":
            h = hashlib.sha256(f"{i}:{freq}".encode()).digest()[0]
            v = (h / 127.5) - 1
        else:
            v = math.sin(2 * math.pi * ph)
        data.append(int(max(-127, min(127, round(v * amp)))) & 0xff)
    if len(data) % 2:
        data.append(0)
    return bytes(data)

def audio_loop(rate=8287, seconds=2.0):
    n = int(rate * seconds)
    out = bytearray()
    scale = [55, 65.41, 73.42, 82.41, 98.0, 110.0, 130.81, 146.83]
    for i in range(n):
        step = (i // (rate // 8)) % len(scale)
        bass = math.sin(math.tau * scale[step] * i / rate) * 44
        lead = math.sin(math.tau * scale[(step + 2) % len(scale)] * 2 * i / rate) * 18
        hat = 0
        if (i % (rate // 8)) < 120:
            hat = ((hashlib.sha256(f"hat:{i}".encode()).digest()[0] / 127.5) - 1) * 20
        kick = 0
        if (i % (rate // 2)) < 700:
            k = i % (rate // 2)
            kick = math.sin(math.tau * (90 - k * 0.06) * i / rate) * (1 - k / 700) * 50
        out.append(int(max(-127, min(127, bass + lead + hat + kick))) & 0xff)
    if len(out) % 2:
        out.append(0)
    return bytes(out)

def mod():
    samples = [
        ("SUBBASS", sample_wave(55, 0.25, amp=72, waveform="tri"), 56, True),
        ("HYPERSAW", sample_wave(220, 0.20, amp=50, waveform="saw"), 44, True),
        ("GLASS", sample_wave(880, 0.12, amp=38), 40, True),
        ("KICK", sample_wave(70, 0.08, amp=90, waveform="tri"), 64, False),
        ("SNARE", sample_wave(170, 0.06, amp=55, waveform="noise"), 52, False),
        ("HAT", sample_wave(900, 0.035, amp=28, waveform="noise"), 32, False),
    ]
    while len(samples) < 31:
        samples.append(("", b"", 0, False))
    buf = bytearray(b"HYPERDRIVE AGA".ljust(20, b" ")[:20])
    body = bytearray()
    for name, data, vol, looped in samples:
        if len(data) % 2:
            data += b"\0"
        length = len(data) // 2
        loop_len = length if looped and length > 2 else 1
        buf += name.encode("ascii").ljust(22, b"\0")[:22]
        buf += length.to_bytes(2, "big")
        buf += bytes([0, vol])
        buf += (0).to_bytes(2, "big")
        buf += loop_len.to_bytes(2, "big")
        body += data
    song_len = 8
    buf += bytes([song_len, 0])
    buf += bytes(range(song_len)) + bytes(128 - song_len)
    buf += b"M.K."
    periods = [428, 381, 339, 320, 285, 254, 226, 214]
    for pat in range(song_len):
        for row in range(64):
            for ch in range(4):
                smp = 0
                per = 0
                eff = 0
                if ch == 0 and row % 4 == 0:
                    smp, per = 1, periods[(row // 4 + pat) % len(periods)]
                elif ch == 1 and row % 8 == 2:
                    smp, per = 2, periods[(row // 8 + pat + 2) % len(periods)]
                elif ch == 2 and row % 16 == 0:
                    smp, per = 4, 214
                elif ch == 2 and row % 16 == 8:
                    smp, per = 5, 254
                elif ch == 3 and row % 4 in (1, 3):
                    smp, per = 6, 428
                b0 = (smp & 0xF0) | ((per >> 8) & 0x0F)
                b1 = per & 0xFF
                b2 = ((smp & 0x0F) << 4) | ((eff >> 8) & 0x0F)
                b3 = eff & 0xFF
                buf += bytes([b0, b1, b2, b3])
    buf += body
    return bytes(buf)

def main():
    img = logo()
    (ASSETS / "logo.raw").write_bytes(planes(img))
    (ASSETS / "logo_preview.png").write_bytes(png_rgb(img))
    screen = full_screen()
    (ASSETS / "screen.raw").write_bytes(planes(screen))
    (ASSETS / "screen_preview.png").write_bytes(png_rgb(screen, scale=2))
    (ASSETS / "hyperdrive.mod").write_bytes(mod())
    (ASSETS / "audio_loop.raw").write_bytes(audio_loop())
    for name, vals in {
        "plasma_palette.bin": gen_tables.plasma_palette(),
        "copper_gradient.bin": gen_tables.copper_gradient(),
        "tunnel.bin": gen_tables.tunnel_table(),
    }.items():
        b = bytearray()
        for v in vals:
            if name.endswith("tunnel.bin"):
                b += struct.pack(">H", v & 0xffff)
            else:
                b += struct.pack(">I", v & 0xffffffff)
        (ASSETS / name).write_bytes(bytes(b))
    digest = hashlib.sha256((ASSETS / "logo.raw").read_bytes()).hexdigest()[:16]
    print(f"generated logo={W}x{H} mod={len((ASSETS / 'hyperdrive.mod').read_bytes())} logo_sha={digest}")

if __name__ == "__main__":
    main()
