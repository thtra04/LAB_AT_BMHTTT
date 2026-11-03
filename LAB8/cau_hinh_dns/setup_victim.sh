#!/bin/bash
# VICTIM 10.9.0.100 + DMZ roles 172.16.6.10 (legit web) / 172.16.6.20 (auth-dns)
NATIF=$(ip -br -4 addr | awk '/192\.168\.226\./{print $1; exit}')
LABIF=$(ip -br link | awk '$1 ~ /^(en|eth)/{print $1}' | grep -v "^$NATIF$" | head -1)
echo "NATIF=$NATIF LABIF=$LABIF"
ip addr flush dev "$LABIF" 2>/dev/null
ip addr add 10.9.0.100/24 dev "$LABIF"
ip addr add 172.16.6.10/24 dev "$LABIF"
ip addr add 172.16.6.20/24 dev "$LABIF"
ip link set "$LABIF" up
hostnamectl set-hostname victim 2>/dev/null
# Force DNS to resolver 10.9.0.10
systemctl stop systemd-resolved 2>/dev/null; systemctl disable systemd-resolved 2>/dev/null
rm -f /etc/resolv.conf; echo "nameserver 10.9.0.10" > /etc/resolv.conf
# Legit DMZ web on 172.16.6.10:80
mkdir -p /opt/legitweb; echo '<!doctype html><h1>LAB9 LEGIT DMZ-WEB</h1><p>172.16.6.10 - trang that</p>' > /opt/legitweb/index.html
pkill -f 'http.server 80' 2>/dev/null; sleep 1
setsid bash -c 'cd /opt/legitweb && exec python3 -m http.server 80 --bind 172.16.6.10' >/var/log/legitweb.log 2>&1 < /dev/null &
# Authoritative sim on 172.16.6.20:53
pkill -f auth_dns_delayed 2>/dev/null; sleep 1
setsid bash -c 'exec python3 /opt/auth_dns_delayed.py --bind 172.16.6.20 --delay 1.5' >/var/log/authdns.log 2>&1 < /dev/null &
sleep 2
echo "=== resolv.conf ==="; cat /etc/resolv.conf
echo "=== listeners ==="; ss -tulnp 2>/dev/null | grep -E '172.16.6.(10|20)'
