from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def write_event(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} {message}\n")
