from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

from app.compose import build_compose, write_compose
from app.logger import write_event
from app.ports import allocate_ports, load_port_state, save_port_state
from app.settings import load_settings


def discover_vpns(vpn_dir: Path) -> list[Path]:
    return sorted([p for p in vpn_dir.glob("*.ovpn") if p.is_file()])


def ensure_support_files(root: Path) -> None:
    (root / "logs").mkdir(parents=True, exist_ok=True)
    (root / "state").mkdir(parents=True, exist_ok=True)


def sanitize_name(path: Path) -> str:
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", path.stem).strip("_")
    return name or "vpn"


def prepare(root: Path) -> list[dict[str, str | int]]:
    settings = load_settings(root)
    ensure_support_files(root)
    vpn_files = discover_vpns(settings.vpn_dir)

    if not vpn_files:
        raise RuntimeError("no ovpn files found")

    existing = load_port_state(settings.state_file)
    names = [p.name for p in vpn_files]
    allocated = allocate_ports(names, settings.start_port, existing)
    save_port_state(settings.state_file, allocated)

    entries = [
        {"name": sanitize_name(p), "port": allocated[p.name], "ovpn_file": p.name}
        for p in vpn_files
    ]

    compose = build_compose(root, entries)
    write_compose(root, compose)

    write_event(settings.events_log, f"CONFIG_READY vpns={len(entries)} start_port={settings.start_port}")
    return entries


def cmd_up(root: Path) -> int:
    settings = load_settings(root)
    try:
        entries = prepare(root)
    except RuntimeError as exc:
        print(str(exc))
        return 1

    env = os.environ.copy()
    env["SOCKS_USER"] = settings.username
    env["SOCKS_PASS"] = settings.password
    subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=root, check=True, env=env)
    write_event(settings.events_log, "DOCKER_COMPOSE_STARTED")
    print(f"started {len(entries)} proxies")
    for entry in entries:
        print(f"{entry['name']} -> port {entry['port']}")
    return 0


def cmd_render(root: Path) -> int:
    try:
        entries = prepare(root)
    except RuntimeError as exc:
        print(str(exc))
        return 1
    print(f"rendered {len(entries)} proxies")
    for entry in entries:
        print(f"{entry['name']} -> port {entry['port']}")
    return 0


def cmd_down(root: Path) -> int:
    settings = load_settings(root)
    subprocess.run(["docker", "compose", "down"], cwd=root, check=True)
    write_event(settings.events_log, "DOCKER_COMPOSE_STOPPED")
    print("stopped")
    return 0


def cmd_status(root: Path) -> int:
    settings = load_settings(root)
    state = load_port_state(settings.state_file)
    if not state:
        print("no state")
        return 0
    for name, port in sorted(state.items(), key=lambda item: item[1]):
        container = f"ovpnproxy-{sanitize_name(Path(name))}"
        status = "unknown"
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Status}}", container],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                status = result.stdout.strip() or "unknown"
            elif "docker.sock" in result.stderr or "Cannot connect" in result.stderr:
                status = "docker-unavailable"
            else:
                status = "not-created"
        except FileNotFoundError:
            status = "docker-not-installed"
        print(f"{name} port={port} status={status}")
    return 0


def cmd_logs(root: Path) -> int:
    settings = load_settings(root)
    if not settings.events_log.exists():
        print("no logs")
        return 0
    print(settings.events_log.read_text(encoding="utf-8"), end="")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["up", "down", "status", "logs", "render"])
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]

    if args.command == "up":
        return cmd_up(root)
    if args.command == "render":
        return cmd_render(root)
    if args.command == "down":
        return cmd_down(root)
    if args.command == "status":
        return cmd_status(root)
    if args.command == "logs":
        return cmd_logs(root)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
