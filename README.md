# ovpnProxy

Docker Compose tabanli OpenVPN -> SOCKS5 proxy manager.

## Kullanim

1. `vpns/` altina `.ovpn` dosyalari koy.
2. `config/settings.yml` icinde username, password ve baslangic port ayarla.
3. Calistir:

```bash
python3 -m app.main up
```

## Komutlar

```bash
python3 -m app.main up
python3 -m app.main down
python3 -m app.main status
python3 -m app.main logs
python3 -m app.main render
```

`render` Docker baslatmadan port atar ve `docker-compose.yml` uretir.

## Erisim

Her `.ovpn` icin otomatik port atanir. Bos port bulup atanir.

Ornek:

```text
socks5://proxyuser:proxypass@SERVER_IP:1040
```

Test:

```bash
curl --socks5 proxyuser:proxypass@127.0.0.1:1040 https://ifconfig.me
```

## Log

Event log:

```text
logs/events.log
```

VPN connected/dropped eventleri buraya yazilir.
