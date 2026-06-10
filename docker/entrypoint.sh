#!/usr/bin/env bash
set -euo pipefail

VPN_FILE="${VPN_FILE:?VPN_FILE not set}"
PROXY_PORT="${PROXY_PORT:-1080}"
SOCKS_USER="${SOCKS_USER:-proxyuser}"
SOCKS_PASS="${SOCKS_PASS:-proxypass}"

mkdir -p /logs

# Create OpenVPN auth file for automated login
echo -e "${SOCKS_USER}\n${SOCKS_PASS}" > /tmp/vpn_auth.txt
chmod 600 /tmp/vpn_auth.txt

cat > /etc/3proxy/3proxy.cfg <<EOF
auth strong
users ${SOCKS_USER}:CL:${SOCKS_PASS}
allow ${SOCKS_USER}
socks -p${PROXY_PORT}
EOF

3proxy /etc/3proxy/3proxy.cfg >/logs/3proxy.log 2>&1 &
PROXY_PID=$!

trap 'kill ${PROXY_PID} >/dev/null 2>&1 || true' INT TERM EXIT

echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] VPN_START file=${VPN_FILE} port=${PROXY_PORT}" >> /logs/events.log

set +e
openvpn --config "${VPN_FILE}" --auth-user-pass /tmp/vpn_auth.txt --verb 3 2>&1 | while IFS= read -r line; do
  echo "$line" >> /logs/openvpn.log
  case "$line" in
    *"Initialization Sequence Completed"*)
      echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] VPN_CONNECTED file=${VPN_FILE} port=${PROXY_PORT}" >> /logs/events.log
      ;;
    *"AUTH_FAILED"*|*"Exiting due to fatal error"*|*"SIGTERM"*|*"SIGINT"*)
      echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] VPN_DROPPED file=${VPN_FILE} port=${PROXY_PORT} line=${line}" >> /logs/events.log
      ;;
  esac
done
OPENVPN_EXIT=${PIPESTATUS[0]}
set -e

echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] VPN_PROCESS_EXIT file=${VPN_FILE} port=${PROXY_PORT} code=${OPENVPN_EXIT}" >> /logs/events.log

exit ${OPENVPN_EXIT}
