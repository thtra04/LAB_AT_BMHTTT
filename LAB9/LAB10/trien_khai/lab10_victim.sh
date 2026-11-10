#!/bin/bash
# =====================================================================
# LAB10 - VICTIM (10.9.0.100) - chay bang sudo tren may victim
# Chay:  sudo bash lab10_victim.sh
# =====================================================================
set -e
LABIF=ens37
HOME_DIR=$(eval echo ~${SUDO_USER:-$USER})

echo "[1] Cau hinh netplan ens37 = 10.9.0.100/24, gateway lab = pfSense 10.9.0.1"
cat > /etc/netplan/99-lab10.yaml <<'EOF'
network:
  version: 2
  ethernets:
    ens37:
      dhcp4: no
      addresses: [10.9.0.100/24]
      routes:
        - to: 10.10.0.0/24      # de mo fake web 10.10.0.200 sau khi poison
          via: 10.9.0.1
EOF
chmod 600 /etc/netplan/99-lab10.yaml
netplan apply
sleep 1

echo "[2] Ep DNS cua victim ve resolver 10.9.0.10"
systemctl stop systemd-resolved 2>/dev/null || true
systemctl disable systemd-resolved 2>/dev/null || true
rm -f /etc/resolv.conf
echo "nameserver 10.9.0.10" > /etc/resolv.conf

echo "[3] Tao launcher kiem tra"
cat > "$HOME_DIR/lab10_victim_check.sh" <<'EOF'
#!/bin/bash
echo "=== resolv.conf ==="; cat /etc/resolv.conf
echo "=== dig www.example.lab10.test ==="; dig +short www.example.lab10.test
echo "=== HTTP ==="; curl -s --max-time 4 http://www.example.lab10.test/ | head -5
EOF
chmod +x "$HOME_DIR/lab10_victim_check.sh"

echo "[4] Trang thai:"
ip -br -4 addr show $LABIF
echo "[DONE] VICTIM san sang. Baseline/poison kiem tra bang: bash ~/lab10_victim_check.sh"
