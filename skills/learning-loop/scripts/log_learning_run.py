#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CORE = SCRIPT_DIR / "log_learning_run_core.py"
NORMALIZE = SCRIPT_DIR / "normalize_learning_layout.py"


def main() -> int:
    core = subprocess.run([sys.executable, str(CORE), *sys.argv[1:]])
    normalize = subprocess.run([sys.executable, str(NORMALIZE)])
    if core.returncode != 0:
        return core.returncode
    return normalize.returncode


if __name__ == "__main__":
    raise SystemExit(main())
