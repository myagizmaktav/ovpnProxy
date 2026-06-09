from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(0, data)]

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        while stack and stack[-1][0] >= indent + 1:
            stack.pop()

        current = stack[-1][1]
        if not value:
            current[key] = {}
            stack.append((indent + 1, current[key]))
            continue

        if value.isdigit():
            current[key] = int(value)
        else:
            current[key] = value

    return data


@dataclass(frozen=True)
class Settings:
    username: str
    password: str
    start_port: int
    vpn_dir: Path
    events_log: Path
    state_file: Path


def load_settings(root: Path) -> Settings:
    config_path = root / "config" / "settings.yml"
    data = _load_simple_yaml(config_path)

    auth = data.get("auth", {}) or {}
    ports = data.get("ports", {}) or {}
    vpn = data.get("vpn", {}) or {}
    logging = data.get("logging", {}) or {}

    return Settings(
        username=str(auth.get("username", "proxyuser")),
        password=str(auth.get("password", "proxypass")),
        start_port=int(ports.get("start", 1040)),
        vpn_dir=root / str(vpn.get("directory", "vpns")),
        events_log=root / str(logging.get("events", "logs/events.log")),
        state_file=root / str(logging.get("state", "state/ports.json")),
    )
