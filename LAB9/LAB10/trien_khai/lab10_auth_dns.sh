#!/bin/bash
# =====================================================================
# LAB10 - AUTH-DNS / RACE RELAY (172.16.6.20) - chay bang sudo tren may auth-dns
# Chay:  sudo bash lab10_auth_dns.sh
# Kiem AUTH-DNS hop le (UDP/53) + race harness (UDP/5300) + web hop le 172.16.6.10
# =====================================================================
set -e
LABIF=ens37
HOME_DIR=$(eval echo ~${SUDO_USER:-$USER})

echo "[1] Cau hinh netplan ens37 = 172.16.6.20/24 (+ alias 172.16.6.10 web hop le), on-link toi 10.9.0.0/24"
rm -f /etc/netplan/99-dnslab.yaml
cat > /etc/netplan/99-lab10.yaml <<'EOF'
network:
  version: 2
  ethernets:
    ens37:
      dhcp4: no
      addresses: [172.16.6.20/24, 172.16.6.10/24]
      routes:
        - to: 10.9.0.0/24       # resolver 10.9.0.10 cung L2 segment -> on-link
          scope: link
EOF
chmod 600 /etc/netplan/99-lab10.yaml
netplan apply
sleep 1

echo "[2] Tat BIND cu (neu co) de giai phong 172.16.6.20:53 cho script auth_dns_relay"
systemctl stop named 2>/dev/null || true
systemctl disable named 2>/dev/null || true
systemctl stop bind9 2>/dev/null || true

echo "[3] Web hop le 172.16.6.10:80 (de baseline mo duoc trang that)"
LEGIT='<!doctype html><meta charset=utf-8><title>LAB10 LEGIT WEB</title><h1>LAB10 - Trang web HOP LE (172.16.6.10)</h1><p>Day la DMZ-WEB that truoc khi bi poison.</p>'
pkill -f 'http.server' 2>/dev/null || true
if command -v apache2 >/dev/null 2>&1; then
  echo "$LEGIT" > /var/www/html/index.html
  systemctl restart apache2 2>/dev/null || true
  echo "    dung apache2 phuc vu :80 (moi interface, gom 172.16.6.10)"
else
  mkdir -p /opt/legitweb; echo "$LEGIT" > /opt/legitweb/index.html
  setsid bash -c 'cd /opt/legitweb && exec python3 -m http.server 80 --bind 172.16.6.10' >/var/log/lab10_legitweb.log 2>&1 < /dev/null &
  echo "    dung python http.server phuc vu 172.16.6.10:80"
fi

echo "[4] Tao launcher chay AUTH-DNS + race relay"
cat > "$HOME_DIR/lab10_auth_start.sh" <<EOF
#!/bin/bash
# AUTH-DNS hop le (53) + race relay (5300). Hien log [PENDING]/[HIT]/[LEGIT]. Ctrl+C de dung.
sudo pkill -f auth_dns_relay_lab10.py 2>/dev/null; sleep 1
sudo python3 "$HOME_DIR/auth_dns_relay_lab10.py"
EOF
chmod +x "$HOME_DIR/lab10_auth_start.sh"

echo "[5] Trang thai:"
ip -br -4 addr show $LABIF
echo "[DONE] AUTH-DNS san sang. Chay dich vu: bash ~/lab10_auth_start.sh"
