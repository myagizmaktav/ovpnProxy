from __future__ import annotations

import json
import socket
from pathlib import Path


def load_port_state(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    try:
        return {str(k): int(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}
    except Exception:
        return {}


def save_port_state(path: Path, state: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", port))
        except OSError:
            return False
    return True


def allocate_ports(names: list[str], start_port: int, existing: dict[str, int]) -> dict[str, int]:
    taken = set(existing.values())
    allocated: dict[str, int] = {}
    next_port = start_port

    for name in names:
        if name in existing and is_port_free(existing[name]):
            port = existing[name]
            allocated[name] = port
            taken.add(port)
            continue

        while next_port in taken or not is_port_free(next_port):
            next_port += 1

        allocated[name] = next_port
        taken.add(next_port)
        next_port += 1

    return allocated
