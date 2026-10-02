#!/usr/bin/env python3
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
skip_dirs = {".git", "build", "__pycache__", "tools/vendor", "tools/bin"}
skip_names = {"MANIFEST.sha256", ".DS_Store"}
files = []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT).as_posix()
    if p.name in skip_names or p.name.startswith("."):
        continue
    if any(rel == d or rel.startswith(d + "/") for d in skip_dirs):
        continue
    if p.suffix in {".pyc", ".o", ".tmp"}:
        continue
    files.append(p)
with (ROOT / "MANIFEST.sha256").open("w") as f:
    for p in files:
        f.write(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.relative_to(ROOT).as_posix() + "\n")
print("manifest:", len(files), "files")
