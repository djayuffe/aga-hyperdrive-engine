#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "assets").glob("*") if p.is_file()}
subprocess.check_call([sys.executable, str(ROOT / "tools/generate_assets.py")], cwd=ROOT)
after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "assets").glob("*") if p.is_file()}
if before != after:
    print("REPRODUCIBILITY FAILED")
    for p in sorted(set(before) | set(after)):
        if before.get(p) != after.get(p):
            print(p.relative_to(ROOT), before.get(p), after.get(p))
    sys.exit(1)
print("REPRODUCIBILITY OK")
