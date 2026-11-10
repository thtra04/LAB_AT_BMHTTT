#!/bin/bash
# =====================================================================
# LAB10 - KALI / ATTACKER (10.10.0.200 tren ATTACKNET) - chay bang sudo
# Chay:  sudo bash lab10_kali.sh
# NIC lab: eth1 (ATTACKNET). eth0 giu NAT lam default (SSH/Internet).
# =====================================================================
set -e
LABIF=eth1
HOME_DIR=$(eval echo ~${SUDO_USER:-$USER})

echo "[1] Cau hinh eth1 = 10.10.0.200/24, route 10.9.0.0/24 & 172.16.6.0/24 qua pfSense 10.10.0.1"
nmcli con delete lab10-attacknet 2>/dev/null || true
nmcli con add type ethernet ifname eth1 con-name lab10-attacknet ip4 10.10.0.200/24
nmcli con mod lab10-attacknet +ipv4.routes "10.9.0.0/24 10.10.0.1"
nmcli con mod lab10-attacknet +ipv4.routes "172.16.6.0/24 10.10.0.1"
nmcli con mod lab10-attacknet ipv4.never-default yes ipv4.method manual
nmcli con up lab10-attacknet
# dam bao KHONG promiscuous (tinh "remote": khong sniff)
ip link set eth1 promisc off 2>/dev/null || true

echo "[2] Chuan bi fake web"
mkdir -p "$HOME_DIR/fakeweb"
cp -f "$HOME_DIR/fake_index.html" "$HOME_DIR/fakeweb/index.html"

echo "[3] Tao 3 launcher (3 terminal khi demo)"
cat > "$HOME_DIR/lab10_evil_dns.sh" <<EOF
#!/bin/bash
# TERMINAL 1: malicious authoritative DNS mo phong tren 10.10.0.200:53
sudo pkill -f evil_dns_lab10.py 2>/dev/null; sleep 1
sudo python3 "$HOME_DIR/evil_dns_lab10.py"
EOF
cat > "$HOME_DIR/lab10_fakeweb.sh" <<EOF
#!/bin/bash
# TERMINAL 2: fake web tren 10.10.0.200:80
sudo pkill -f 'http.server 80' 2>/dev/null; sleep 1
sudo python3 -m http.server 80 --bind 10.10.0.200 --directory "$HOME_DIR/fakeweb"
EOF
cat > "$HOME_DIR/lab10_kaminsky.sh" <<EOF
#!/bin/bash
# TERMINAL 3: remote TXID guessing + verify
python3 "$HOME_DIR/kaminsky_remote_lab10.py"
EOF
chmod +x "$HOME_DIR/lab10_evil_dns.sh" "$HOME_DIR/lab10_fakeweb.sh" "$HOME_DIR/lab10_kaminsky.sh"

echo "[4] Trang thai:"
ip -br -4 addr show $LABIF
ip route | grep -E '10.9.0.0|172.16.6.0' || true
echo "[DONE] KALI san sang. Demo: T1 ~/lab10_evil_dns.sh | T2 ~/lab10_fakeweb.sh | T3 ~/lab10_kaminsky.sh"
