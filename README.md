# ovpnProxy

Docker Compose tabanli OpenVPN -> SOCKS5 proxy manager.

Her `.ovpn` dosyasi icin ayri container acilir. Container icinde OpenVPN tüneli ve SOCKS5 proxy calisir. Boylece birden fazla VPN ayni makinede route cakismasi olmadan servis edilir.

## Ne Yapar

- `vpns/` klasorundeki `.ovpn` dosyalarini otomatik bulur.
- Her VPN icin ayri Docker Compose service uretir.
- Her VPN icin ayri SOCKS5 portu acar.
- Username/password ile SOCKS5 auth kullanir.
- Baslangic portu doluysa sonraki bos portu secer.
- VPN connect/drop eventlerini `logs/events.log` dosyasina yazar.
- Atanan portlari `state/ports.json` icinde saklar.

## Gereksinimler

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

## Proje Yapisi

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

## VPN Dosyalari

`.ovpn` dosyalarini `vpns/` klasorune koy:

```text
vpns/account1.ovpn
vpns/account2.ovpn
vpns/account3.ovpn
```

Repo `.ovpn` dosyalarini paylasmaz. `.gitignore` icinde `*.ovpn` vardir.

## Ayarlar

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

## Port Mantigi

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

## Ilk Calistirma

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

## Komutlar

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

## SOCKS5 Erisim

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

## Test

Ilk proxy icin IP testi:

```bash
curl --socks5 proxyuser:proxypass@127.0.0.1:1040 https://ifconfig.me
```

Ikinci proxy icin IP testi:

```bash
curl --socks5 proxyuser:proxypass@127.0.0.1:1041 https://ifconfig.me
```

Her port farkli VPN cikis IP'si donmelidir.

## Loglar

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

## Docker Compose

`docker-compose.yml` otomatik uretilir. Manuel duzenleme onerilmez. Degisiklik icin `config/settings.yml` veya `vpns/` klasoru kullan.

Uretilen service her VPN icin su ayarlari kullanir:

```yaml
cap_add:
  - NET_ADMIN
devices:
  - /dev/net/tun:/dev/net/tun
restart: unless-stopped
```

## Guvenlik

- `.ovpn` dosyalari repo disinda tutulur.
- `logs/` repo disinda tutulur.
- `state/` repo disinda tutulur.
- `.env` repo disinda tutulur.
- Public sunucuda guclu username/password kullan.
- Gerek yoksa proxy portlarini internete acma.
- Firewall ile sadece kendi IP adresine izin vermek daha guvenlidir.

## Sorun Giderme

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

## Notlar

Bu proje Docker ile tasarlandi. Docker olmadan coklu OpenVPN tünelini duzgun izole etmek icin Linux network namespace, iptables ve root seviyesinde ek kurulum gerekir.
