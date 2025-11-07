"""Utility helpers for the backend application."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def get_tiger_cli_path() -> str:
    """Return the absolute path to the Tiger CLI within the current venv."""

    python_path = Path(sys.executable)
    bin_dir = python_path.parent

    candidates = [
        bin_dir / "tiger",
        bin_dir / "tiger.exe",
        Path("/root/bin/tiger"),
        Path("/root/bin/tiger.exe"),
        Path("/usr/local/bin/tiger"),
        Path("/usr/bin/tiger"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)

    resolved = shutil.which("tiger", path=str(bin_dir)) or shutil.which("tiger")
    if resolved:
        return resolved

    raise FileNotFoundError(
        "Tiger CLI executable not found. Ensure Tiger CLI is installed and accessible via PATH."
    )

