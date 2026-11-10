#!/bin/bash
# =====================================================================
# LAB10 - DNS-SERVER (10.9.0.10) - script setup chay bang sudo tren may dns-server
# Chay:  sudo bash lab10_dns_server.sh
# Vai tro: BIND9 baseline (pha restore) + resolver mo phong (pha tan cong)
# =====================================================================
set -e
LABIF=ens37
HOME_DIR=$(eval echo ~${SUDO_USER:-$USER})
echo "[*] Home chua file goc: $HOME_DIR  | NIC lab: $LABIF"

echo "[1] Cau hinh netplan ens37 = 10.9.0.10/24 (gateway lab = pfSense 10.9.0.1)"
rm -f /etc/netplan/99-lab10-dns.yaml /etc/netplan/99-dnslab.yaml
cat > /etc/netplan/99-lab10.yaml <<'EOF'
network:
  version: 2
  ethernets:
    ens37:
      dhcp4: no
      addresses: [10.9.0.10/24]
      routes:
        - to: 10.10.0.0/24      # ATTACKNET -> qua pfSense (poison: resolver->evil DNS)
          via: 10.9.0.1
        - to: 172.16.6.0/24     # DMZ/AUTH-DNS cung L2 segment -> on-link
          scope: link
EOF
chmod 600 /etc/netplan/99-lab10.yaml
netplan apply
sleep 1

echo "[2] Cai BIND9 baseline (forward example.lab10.test -> 172.16.6.20, DNSSEC auto + validate-except)"
cp -n /etc/bind/named.conf.options /etc/bind/named.conf.options.pre_lab10 2>/dev/null || true
cp -n /etc/bind/named.conf.local   /etc/bind/named.conf.local.pre_lab10   2>/dev/null || true
cp "$HOME_DIR/named.conf.options.baseline" /etc/bind/named.conf.options
cp "$HOME_DIR/named.conf.local.baseline"   /etc/bind/named.conf.local
named-checkconf && echo "    named.conf OK"
systemctl restart named 2>/dev/null || systemctl restart bind9

echo "[3] Tao launcher pha tan cong / pha khoi phuc"
cat > "$HOME_DIR/lab10_dns_attack.sh" <<EOF
#!/bin/bash
# PHA TAN CONG: dung BIND, chay resolver mo phong co chu dich (source port 33333)
sudo systemctl stop named 2>/dev/null
echo "[*] BIND da dung. Chay vulnerable resolver (Ctrl+C de dung)..."
sudo python3 "$HOME_DIR/vuln_resolver_lab10.py"
EOF
cat > "$HOME_DIR/lab10_dns_restore.sh" <<EOF
#!/bin/bash
# PHA KHOI PHUC: khoi dong lai BIND9 hien dai + kiem tra source-port randomization
sudo pkill -f vuln_resolver_lab10.py 2>/dev/null; sleep 1
sudo systemctl restart named
sleep 2
echo "=== dig baseline (expect 172.16.6.10) ==="
dig +short @10.9.0.10 www.example.lab10.test
echo "=== source port cua BIND (KHONG con co dinh 33333) ==="
echo "Chay song song: sudo tcpdump -ni $LABIF 'udp and port 53' ; roi dig nhieu lan"
EOF
chmod +x "$HOME_DIR/lab10_dns_attack.sh" "$HOME_DIR/lab10_dns_restore.sh"

echo "[4] Trang thai:"
ip -br -4 addr show $LABIF
ip route | grep -E '10.10.0.0|172.16.6.0' || true
echo "[DONE] DNS-SERVER san sang. Pha tan cong: bash ~/lab10_dns_attack.sh | Khoi phuc: bash ~/lab10_dns_restore.sh"
