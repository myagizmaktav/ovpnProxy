from __future__ import annotations

from pathlib import Path


def build_compose(root: Path, entries: list[dict[str, str | int]]) -> str:
    lines: list[str] = ["services:"]

    for entry in entries:
        name = str(entry["name"])
        port = int(entry["port"])
        ovpn_file = str(entry["ovpn_file"])
        service_name = f"vpn_{name}"
        lines.extend(
            [
                f"  {service_name}:",
                f"    build:",
                f"      context: .",
                f"      dockerfile: docker/Dockerfile",
                f"    container_name: ovpnproxy-{name}",
                f"    restart: unless-stopped",
                f"    cap_add:",
                f"      - NET_ADMIN",
                f"    devices:",
                f"      - /dev/net/tun:/dev/net/tun",
                f"    ports:",
                f"      - \"{port}:1080\"",
                f"    environment:",
                f"      VPN_FILE: /vpns/{ovpn_file}",
                f"      PROXY_PORT: 1080",
                f"      SOCKS_USER: ${{SOCKS_USER:-proxyuser}}",
                f"      SOCKS_PASS: ${{SOCKS_PASS:-proxypass}}",
                f"    volumes:",
                f"      - ./vpns:/vpns:ro",
                f"      - ./logs:/logs",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def write_compose(root: Path, content: str) -> None:
    (root / "docker-compose.yml").write_text(content, encoding="utf-8")
