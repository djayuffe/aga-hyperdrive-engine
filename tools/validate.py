#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
errors = []

def check(cond, msg):
    if not cond:
        errors.append(msg)

logo = ROOT / "assets/logo.raw"
preview = ROOT / "assets/logo_preview.png"
screen_preview = ROOT / "assets/screen_preview.png"
mod = ROOT / "assets/hyperdrive.mod"
screen = ROOT / "assets/screen.raw"
audio = ROOT / "assets/audio_loop.raw"
sprite_orbs = ROOT / "assets/sprite_orbs.bin"
sprite_path = ROOT / "assets/sprite_path.bin"
main = ROOT / "src/main.s"

check(logo.exists(), "assets/logo.raw missing")
check(preview.exists(), "assets/logo_preview.png missing")
check(screen_preview.exists(), "assets/screen_preview.png missing")
check(mod.exists(), "assets/hyperdrive.mod missing")
check(screen.exists(), "assets/screen.raw missing")
check(audio.exists(), "assets/audio_loop.raw missing")
check(sprite_orbs.exists(), "assets/sprite_orbs.bin missing")
check(sprite_path.exists(), "assets/sprite_path.bin missing")
if logo.exists():
    check(logo.stat().st_size == 4 * 320 * 80 // 8, f"logo.raw size {logo.stat().st_size} != 12800")
if preview.exists():
    check(preview.read_bytes().startswith(b"\x89PNG"), "logo_preview.png is not a PNG")
if screen_preview.exists():
    check(screen_preview.read_bytes().startswith(b"\x89PNG"), "screen_preview.png is not a PNG")
if mod.exists():
    data = mod.read_bytes()
    check(data[1080:1084] == b"M.K.", "MOD signature missing")
    check(data[:20].rstrip() == b"HYPERDRIVE AGA", "MOD title mismatch")
if screen.exists():
    check(screen.stat().st_size == 4 * 320 * 256 // 8, f"screen.raw size {screen.stat().st_size} != 40960")
if audio.exists():
    check(audio.stat().st_size >= 16000 and audio.stat().st_size % 2 == 0, "audio_loop.raw must be even and at least ~2 seconds")
if sprite_orbs.exists():
    check(sprite_orbs.stat().st_size == 8 * (2 + 16 * 2 + 2) * 2, "sprite_orbs.bin must contain eight 16-line hardware sprites")
if sprite_path.exists():
    check(sprite_path.stat().st_size == 256 * 4, "sprite_path.bin must contain 256 x/y pairs")

if main.exists():
    s = main.read_text()
    for required in (
        "Effect_Init", "Effect_Frame", "Copper_Build", "Music_Tick", "DENISEID",
        "Screen_Init", "copper_bplptrs", "logo_data", "Effect_CopperLattice",
        "Effect_TunnelLayer", "Effect_SpriteOrbLayer", "Scene_Update",
        "Music_EventBus", "Sprite_Build", "cop_sprptrs", "sprite_orbs",
        "audio_loop", "AUD0LCH", "DMAF_AUD0",
        "DENISEID", "Blitter_ClearVectorPlane", "BLTSIZE", "Effect_BitplaneWarp",
        "sprite_path", "sprite_orbs.bin", "SPRITE_BYTES",
    ):
        check(required in s, f"missing source symbol/comment {required}")
    check("move.w  d0,2(a1)" in s and "move.w  d0,6(a1)" in s, "Copper_Build must patch bitplane pointer high/low words")
    check('incbin "assets/screen.raw"' in s, "full-screen art must be displayed from screen.raw")
    check("btst    #6,CIAAPRA" in s, "main loop must stay running until left mouse is pressed")
    for forbidden in ("TODO", "stub", "placeholder", "scaffold"):
        check(forbidden.lower() not in s.lower(), f"source contains {forbidden}")

readme = (ROOT / "README.md").read_text() if (ROOT / "README.md").exists() else ""
check("state-of-the-art" in readme.lower(), "README should describe state-of-the-art ambition")
check("docs/screenshots/" in readme, "README should include screenshots")
docs = "\n".join(
    p.read_text()
    for p in (ROOT / "docs").glob("*.md")
)
for forbidden in (
    "Remaining expansion work",
    "foundation/smoke-test",
    "placeholder sprite",
    "placeholder",
    "reserve the music control surface",
    "next milestones",
    "scaffold",
):
    check(forbidden not in readme + docs, f"stale scaffold wording remains: {forbidden}")

if errors:
    print("VALIDATION FAILED")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("VALIDATION OK")
if logo.exists():
    print(" logo_sha256", hashlib.sha256(logo.read_bytes()).hexdigest())
