#!/usr/bin/env python3
"""Create a floppy-style turbo boot directory for FS-UAE/real-disk staging.

If `xdftool` is available, an ADF is also emitted. Without it, the directory is
still directly mountable as a filesystem hard drive in FS-UAE and can be copied
to a real Amiga disk with normal tools.
"""
from pathlib import Path
import shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
exe = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build/aga_hyperdrive_engine")
if not exe.exists():
    sys.exit(f"missing executable: {exe}")

out = ROOT / "build/floppy_turbo"
if out.exists():
    shutil.rmtree(out)
(out / "S").mkdir(parents=True)
(out / "C").mkdir()
(out / "DEVS").mkdir()
(out / "LIBS").mkdir()
shutil.copy2(exe, out / "aga_hyperdrive_engine")
(out / "S/Startup-Sequence").write_text(
    "; AGA Hyperdrive Engine turbo boot\n"
    "aga_hyperdrive_engine\n"
)
(out / "README.TXT").write_text(
    "AGA Hyperdrive Engine turbo floppy staging directory.\n"
    "Boot or mount on an AGA Amiga/FS-UAE A1200 profile. Left mouse exits.\n"
)

adf = ROOT / "build/aga_hyperdrive_turbo.adf"
xdftool = shutil.which("xdftool")
if xdftool:
    if adf.exists():
        adf.unlink()
    subprocess.check_call([xdftool, str(adf), "format", "AGAHD"])
    subprocess.check_call([xdftool, str(adf), "boot", "install"])
    for p in sorted(out.rglob("*")):
        if p.is_file():
            subprocess.check_call([xdftool, str(adf), "write", str(p), p.relative_to(out).as_posix()])
    print(f"floppy turbo directory: {out}")
    print(f"floppy turbo ADF: {adf}")
else:
    print(f"floppy turbo directory: {out}")
    print("xdftool not found; skipped optional ADF image")
