FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    openvpn \
    ca-certificates \
    bash \
    iproute2 \
    procps \
    build-essential \
    git \
  && git clone --depth 1 https://github.com/3proxy/3proxy.git /tmp/3proxy \
  && make -C /tmp/3proxy -f Makefile.Linux \
  && install -m 755 /tmp/3proxy/bin/3proxy /usr/local/bin/3proxy \
  && apt-get purge -y --auto-remove build-essential git \
  && rm -rf /tmp/3proxy \
  && rm -rf /var/lib/apt/lists/*

COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/3proxy.cfg.template /etc/3proxy/3proxy.cfg.template

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
