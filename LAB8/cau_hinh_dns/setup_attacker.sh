#!/bin/bash
# ATTACKER 10.9.0.200 : scapy spoof + fake web
NATIF=$(ip -br -4 addr | awk '/192\.168\.226\./{print $1; exit}')
LABIF=$(ip -br link | awk '$1 ~ /^(en|eth)/{print $1}' | grep -v "^$NATIF$" | head -1)
echo "NATIF=$NATIF LABIF=$LABIF"
ip addr flush dev "$LABIF" 2>/dev/null
ip addr add 10.9.0.200/24 dev "$LABIF"
ip link set "$LABIF" up
ip link set "$LABIF" promisc on
hostnamectl set-hostname attacker 2>/dev/null
# fake web on 10.9.0.200:80
mkdir -p /opt/fakeweb; cp /tmp/fake_index.html /opt/fakeweb/index.html 2>/dev/null
pkill -f 'http.server 80' 2>/dev/null; sleep 1
setsid bash -c 'cd /opt/fakeweb && exec python3 -m http.server 80 --bind 10.9.0.200' >/var/log/fakeweb.log 2>&1 < /dev/null &
echo "LABIF=$LABIF" > /tmp/labif.txt
echo "=== promisc ==="; ip -d link show "$LABIF" | grep -o promiscuity.* | head -1
echo "=== scapy ==="; python3 -c 'import scapy; print("scapy", scapy.__version__)' 2>&1
