#!/bin/bash
# DNS-SERVER 10.9.0.10 : BIND9 recursive/cache + authoritative lab9.test
NATIF=$(ip -br -4 addr | awk '/192\.168\.226\./{print $1; exit}')
LABIF=$(ip -br link | awk '$1 ~ /^(en|eth)/{print $1}' | grep -v "^$NATIF$" | head -1)
echo "NATIF=$NATIF LABIF=$LABIF"
ip addr flush dev "$LABIF" 2>/dev/null
ip addr add 10.9.0.10/24 dev "$LABIF"
ip link set "$LABIF" up
ip route replace 172.16.6.0/24 dev "$LABIF"
hostnamectl set-hostname dns-server 2>/dev/null
systemctl restart named 2>/dev/null || systemctl restart bind9 2>/dev/null
sleep 2
echo "=== :53 listen ==="; ss -ulnp 2>/dev/null | grep ':53'
echo "=== dig @self www.lab9.test (expect 172.16.6.10) ==="; dig +short @10.9.0.10 www.lab9.test
