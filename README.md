# ovpnProxy

## Turkce Rehber

Docker Compose tabanli OpenVPN -> SOCKS5 proxy manager.

Her `.ovpn` dosyasi icin ayri container acilir. Container icinde OpenVPN tüneli ve SOCKS5 proxy calisir. Boylece birden fazla VPN ayni makinede route cakismasi olmadan servis edilir.

### Ne Yapar

- `vpns/` klasorundeki `.ovpn` dosyalarini otomatik bulur.
- Her VPN icin ayri Docker Compose service uretir.
- Her VPN icin ayri SOCKS5 portu acar.
- Username/password ile SOCKS5 auth kullanir.
- Baslangic portu doluysa sonraki bos portu secer.
- VPN connect/drop eventlerini `logs/events.log` dosyasina yazar.
- Atanan portlari `state/ports.json` icinde saklar.

### Gereksinimler

- Linux host
- Docker
- Docker Compose plugin
- Python 3
- `/dev/net/tun` destegi
- Container icin `NET_ADMIN` yetkisi

Docker daemon calisir durumda olmali:

```bash
docker info
```

### Proje Yapisi

```text
ovpnProxy/
  app/
    main.py
    settings.py
    ports.py
    compose.py
    logger.py
  config/
    settings.yml
  docker/
    Dockerfile
    entrypoint.sh
    3proxy.cfg.template
  logs/
    events.log
  state/
    ports.json
  vpns/
    account1.ovpn
    account2.ovpn
  README.md
```

### VPN Dosyalari

`.ovpn` dosyalarini `vpns/` klasorune koy:

```text
vpns/account1.ovpn
vpns/account2.ovpn
vpns/account3.ovpn
```

Repo `.ovpn` dosyalarini paylasmaz. `.gitignore` icinde `*.ovpn` vardir.

### Ayarlar

`config/settings.yml` dosyasi:

```yaml
auth:
  username: proxyuser
  password: proxypass

ports:
  start: 1040

vpn:
  directory: vpns

logging:
  events: logs/events.log
  state: state/ports.json
```

Alanlar:

- `auth.username`: SOCKS5 kullanici adi
- `auth.password`: SOCKS5 sifre
- `ports.start`: ilk denenecek host portu
- `vpn.directory`: `.ovpn` dosyalarinin oldugu klasor
- `logging.events`: event log dosyasi
- `logging.state`: port state dosyasi

### Port Mantigi

Ornek config:

```yaml
ports:
  start: 1040
```

Port atama mantigi:

```text
account1.ovpn -> 1040 uygunsa 1040
account2.ovpn -> 1041 doluysa 1042 dene
account2.ovpn -> 1042 doluysa 1043 kullan
account3.ovpn -> sonraki bos port
```

Atanan portlar `state/ports.json` icinde saklanir. Sonraki calistirmada ayni port bossa ayni port korunur.

### Ilk Calistirma

Proje klasorune gir:

```bash
cd /config/Desktop/projects/ovpnProxy
```

Docker baslatmadan compose dosyasi uret ve portlari goster:

```bash
python3 -m app.main render
```

Containerlari baslat:

```bash
python3 -m app.main up
```

Durum kontrol et:

```bash
python3 -m app.main status
```

Log oku:

```bash
python3 -m app.main logs
```

Tum containerlari durdur:

```bash
python3 -m app.main down
```

### Komutlar

```bash
python3 -m app.main render
python3 -m app.main up
python3 -m app.main status
python3 -m app.main logs
python3 -m app.main down
```

Komut aciklamalari:

- `render`: Docker baslatmadan port atar ve `docker-compose.yml` uretir.
- `up`: `docker compose up -d --build` calistirir.
- `status`: portlari ve container durumunu gosterir.
- `logs`: `logs/events.log` dosyasini yazar.
- `down`: `docker compose down` calistirir.

### SOCKS5 Erisim

SOCKS5 URL formati:

```text
socks5://USERNAME:PASSWORD@SERVER_IP:PORT
```

Ornek:

```text
socks5://proxyuser:proxypass@127.0.0.1:1040
```

Uzaktaki sunucudan erisim ornegi:

```text
socks5://proxyuser:proxypass@SERVER_PUBLIC_IP:1040
```

SOCKS5 protokolunde path kullanilmaz. Bu yuzden `account1.ovpn/1040` gibi path tabanli erisim yoktur. Hangi VPN'e gidilecegi port ile belirlenir.

### Test

Ilk proxy icin IP testi:

```bash
curl --socks5 proxyuser:proxypass@127.0.0.1:1040 https://ifconfig.me
```

Ikinci proxy icin IP testi:

```bash
curl --socks5 proxyuser:proxypass@127.0.0.1:1041 https://ifconfig.me
```

Her port farkli VPN cikis IP'si donmelidir.

### Loglar

Event log dosyasi:

```text
logs/events.log
```

Ornek eventler:

```text
2026-06-09 14:47:13 UTC CONFIG_READY vpns=2 start_port=1040
2026-06-09 14:48:20 UTC VPN_START file=/vpns/account1.ovpn port=1080
2026-06-09 14:48:28 UTC VPN_CONNECTED file=/vpns/account1.ovpn port=1080
2026-06-09 14:51:05 UTC VPN_DROPPED file=/vpns/account1.ovpn port=1080 line=AUTH_FAILED
2026-06-09 14:51:06 UTC VPN_PROCESS_EXIT file=/vpns/account1.ovpn port=1080 code=1
```

OpenVPN raw log:

```text
logs/openvpn.log
```

3proxy raw log:

```text
logs/3proxy.log
```

### Docker Compose

`docker-compose.yml` otomatik uretilir. Manuel duzenleme onerilmez. Degisiklik icin `config/settings.yml` veya `vpns/` klasoru kullan.

Uretilen service her VPN icin su ayarlari kullanir:

```yaml
cap_add:
  - NET_ADMIN
devices:
  - /dev/net/tun:/dev/net/tun
restart: unless-stopped
```

### Guvenlik

- `.ovpn` dosyalari repo disinda tutulur.
- `logs/` repo disinda tutulur.
- `state/` repo disinda tutulur.
- `.env` repo disinda tutulur.
- Public sunucuda guclu username/password kullan.
- Gerek yoksa proxy portlarini internete acma.
- Firewall ile sadece kendi IP adresine izin vermek daha guvenlidir.

### Sorun Giderme

Docker daemon yoksa:

```text
failed to connect to the docker API at unix:///var/run/docker.sock
```

Docker servisini baslat:

```bash
sudo systemctl start docker
```

TUN device yoksa:

```text
Cannot open TUN/TAP dev /dev/net/tun
```

Hostta TUN destegini kontrol et:

```bash
ls -la /dev/net/tun
```

Auth hatasi varsa `.ovpn` dosyasinda provider'in istedigi auth ayarlarini kontrol et. Bazi VPN providerlari ek username/password dosyasi ister.

Port erisilmiyorsa:

```bash
python3 -m app.main status
docker compose ps
```

Container loglarini incele:

```bash
docker compose logs
```

### Notlar

Bu proje Docker ile tasarlandi. Docker olmadan coklu OpenVPN tünelini duzgun izole etmek icin Linux network namespace, iptables ve root seviyesinde ek kurulum gerekir.

## English Guide

Docker Compose based OpenVPN -> SOCKS5 proxy manager.

Each `.ovpn` file runs in its own container. OpenVPN and SOCKS5 proxy run inside same container. This allows multiple VPN connections on same host without route conflicts.

### What It Does

- Automatically discovers `.ovpn` files in `vpns/`.
- Generates one Docker Compose service per VPN.
- Opens one SOCKS5 port per VPN.
- Uses username/password SOCKS5 authentication.
- Uses next free port when configured start port is busy.
- Writes VPN connect/drop events to `logs/events.log`.
- Stores assigned ports in `state/ports.json`.

### Requirements

- Linux host
- Docker
- Docker Compose plugin
- Python 3
- `/dev/net/tun` support
- `NET_ADMIN` capability for containers

Docker daemon must be running:

```bash
docker info
```

### Project Structure

```text
ovpnProxy/
  app/
    main.py
    settings.py
    ports.py
    compose.py
    logger.py
  config/
    settings.yml
  docker/
    Dockerfile
    entrypoint.sh
    3proxy.cfg.template
  logs/
    events.log
  state/
    ports.json
  vpns/
    account1.ovpn
    account2.ovpn
  README.md
```

### VPN Files

Put `.ovpn` files into `vpns/`:

```text
vpns/account1.ovpn
vpns/account2.ovpn
vpns/account3.ovpn
```

Repository does not publish `.ovpn` files. `.gitignore` includes `*.ovpn`.

### Settings

`config/settings.yml` file:

```yaml
auth:
  username: proxyuser
  password: proxypass

ports:
  start: 1040

vpn:
  directory: vpns

logging:
  events: logs/events.log
  state: state/ports.json
```

Fields:

- `auth.username`: SOCKS5 username
- `auth.password`: SOCKS5 password
- `ports.start`: first host port to try
- `vpn.directory`: folder containing `.ovpn` files
- `logging.events`: event log file
- `logging.state`: port state file

### Port Allocation

Example config:

```yaml
ports:
  start: 1040
```

Port allocation logic:

```text
account1.ovpn -> 1040 if available
account2.ovpn -> try 1042 if 1041 is busy
account2.ovpn -> use 1043 if 1042 is also busy
account3.ovpn -> next free port
```

Assigned ports are stored in `state/ports.json`. On next run, same port is kept when still available.

### First Run

Enter project directory:

```bash
cd /config/Desktop/projects/ovpnProxy
```

Generate compose file and show ports without starting Docker:

```bash
python3 -m app.main render
```

Start containers:

```bash
python3 -m app.main up
```

Check status:

```bash
python3 -m app.main status
```

Read event log:

```bash
python3 -m app.main logs
```

Stop all containers:

```bash
python3 -m app.main down
```

### Commands

```bash
python3 -m app.main render
python3 -m app.main up
python3 -m app.main status
python3 -m app.main logs
python3 -m app.main down
```

Command descriptions:

- `render`: assigns ports and generates `docker-compose.yml` without starting Docker.
- `up`: runs `docker compose up -d --build`.
- `status`: shows ports and container status.
- `logs`: prints `logs/events.log`.
- `down`: runs `docker compose down`.

### SOCKS5 Access

SOCKS5 URL format:

```text
socks5://USERNAME:PASSWORD@SERVER_IP:PORT
```

Example:

```text
socks5://proxyuser:proxypass@127.0.0.1:1040
```

Remote server example:

```text
socks5://proxyuser:proxypass@SERVER_PUBLIC_IP:1040
```

SOCKS5 protocol does not use URL paths. This means path-based access like `account1.ovpn/1040` is not supported. VPN selection is done by port.

### Test

IP test for first proxy:

```bash
curl --socks5 proxyuser:proxypass@127.0.0.1:1040 https://ifconfig.me
```

IP test for second proxy:

```bash
curl --socks5 proxyuser:proxypass@127.0.0.1:1041 https://ifconfig.me
```

Each port should return a different VPN exit IP.

### Logs

Event log file:

```text
logs/events.log
```

Example events:

```text
2026-06-09 14:47:13 UTC CONFIG_READY vpns=2 start_port=1040
2026-06-09 14:48:20 UTC VPN_START file=/vpns/account1.ovpn port=1080
2026-06-09 14:48:28 UTC VPN_CONNECTED file=/vpns/account1.ovpn port=1080
2026-06-09 14:51:05 UTC VPN_DROPPED file=/vpns/account1.ovpn port=1080 line=AUTH_FAILED
2026-06-09 14:51:06 UTC VPN_PROCESS_EXIT file=/vpns/account1.ovpn port=1080 code=1
```

OpenVPN raw log:

```text
logs/openvpn.log
```

3proxy raw log:

```text
logs/3proxy.log
```

### Docker Compose

`docker-compose.yml` is generated automatically. Manual edits are not recommended. Use `config/settings.yml` or `vpns/` folder for changes.

Generated services use these settings for each VPN:

```yaml
cap_add:
  - NET_ADMIN
devices:
  - /dev/net/tun:/dev/net/tun
restart: unless-stopped
```

### Security

- `.ovpn` files are kept out of repository.
- `logs/` is kept out of repository.
- `state/` is kept out of repository.
- `.env` is kept out of repository.
- Use strong username/password on public servers.
- Do not expose proxy ports to public internet unless needed.
- Restrict access to your own IP with firewall when possible.

### Troubleshooting

Docker daemon unavailable:

```text
failed to connect to the docker API at unix:///var/run/docker.sock
```

Start Docker service:

```bash
sudo systemctl start docker
```

TUN device missing:

```text
Cannot open TUN/TAP dev /dev/net/tun
```

Check TUN support on host:

```bash
ls -la /dev/net/tun
```

If authentication fails, check provider-required auth settings inside `.ovpn`. Some VPN providers require separate username/password auth file.

If port is not reachable:

```bash
python3 -m app.main status
docker compose ps
```

Inspect container logs:

```bash
docker compose logs
```

### Notes

This project is designed for Docker. Without Docker, proper multi-OpenVPN isolation requires Linux network namespaces, iptables, and additional root-level setup.
