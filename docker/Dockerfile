FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    openvpn \
    3proxy \
    ca-certificates \
    bash \
    iproute2 \
    procps \
  && rm -rf /var/lib/apt/lists/*

COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/3proxy.cfg.template /etc/3proxy/3proxy.cfg.template

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
