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
mod = ROOT / "assets/hyperdrive.mod"
main = ROOT / "src/main.s"

check(logo.exists(), "assets/logo.raw missing")
check(preview.exists(), "assets/logo_preview.png missing")
check(mod.exists(), "assets/hyperdrive.mod missing")
if logo.exists():
    check(logo.stat().st_size == 4 * 320 * 80 // 8, f"logo.raw size {logo.stat().st_size} != 12800")
if preview.exists():
    check(preview.read_bytes().startswith(b"\x89PNG"), "logo_preview.png is not a PNG")
if mod.exists():
    data = mod.read_bytes()
    check(data[1080:1084] == b"M.K.", "MOD signature missing")
    check(data[:20].rstrip() == b"HYPERDRIVE AGA", "MOD title mismatch")

if main.exists():
    s = main.read_text()
    for required in ("Effect_Init", "Effect_Frame", "Copper_Build", "Music_Tick", "AGA_REQUIRE"):
        check(required in s, f"missing source symbol/comment {required}")
    check("TODO" not in s, "source contains TODO")

readme = (ROOT / "README.md").read_text() if (ROOT / "README.md").exists() else ""
check("state-of-the-art" in readme.lower(), "README should describe state-of-the-art ambition")
check("docs/screenshots/" in readme, "README should include screenshots")

if errors:
    print("VALIDATION FAILED")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("VALIDATION OK")
if logo.exists():
    print(" logo_sha256", hashlib.sha256(logo.read_bytes()).hexdigest())
