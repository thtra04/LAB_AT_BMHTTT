#!/usr/bin/env bash
# LAB7 - cau hinh WEB-PROXY (E2Guardian :8080 -> Squid 127.0.0.1:3128 + ClamAV)
# Hoang Thanh Tra - 1150080120. Ap dung theo 03_WEB_PROXY/*.txt cua bo tai nguyen LAB7.
set -euo pipefail
E2=/etc/e2guardian
L=$E2/lists
TS=$(date +%Y%m%d-%H%M%S)

echo "[1] Sao luu cau hinh goc (*.bak-$TS)"
cp /etc/squid/squid.conf /etc/squid/squid.conf.bak-$TS
cp $E2/e2guardian.conf $E2/e2guardian.conf.bak-$TS
cp $E2/e2guardianf1.conf $E2/e2guardianf1.conf.bak-$TS
for f in bannedsitelist exceptionsitelist domainsnobypass; do cp $L/$f $L/$f.bak-$TS; done

echo "[2] Squid: chi nghe localhost:3128 + gioi han file > 100 MB (reply_body_max_size)"
sed -i 's/^http_port 3128$/http_port 127.0.0.1:3128/' /etc/squid/squid.conf
grep -q '^reply_body_max_size' /etc/squid/squid.conf || \
  sed -i '/^http_port 127.0.0.1:3128/i # LAB7: chan doi tuong tai ve lon hon 100 MB\nreply_body_max_size 104857600 bytes' /etc/squid/squid.conf

grep -q '^cache deny all' /etc/squid/squid.conf || sed -i '/^http_port 127.0.0.1:3128/a # LAB7: khong cache de moi request deu qua firewall/policy
cache deny all' /etc/squid/squid.conf

echo "[3] e2guardian.conf: filterip/port, upstream Squid, ClamAV scanner"
sed -i 's/^filterip =.*/filterip = 10.6.0.30/' $E2/e2guardian.conf
sed -i 's/^#proxyip = 127.0.0.1/proxyip = 127.0.0.1/; s/^#proxyport = 3128/proxyport = 3128/' $E2/e2guardian.conf
sed -i "s|^#contentscanner = '/etc/e2guardian/contentscanners/clamdscan.conf'|contentscanner = '/etc/e2guardian/contentscanners/clamdscan.conf'|" $E2/e2guardian.conf
sed -i 's/^loglevel = .*/loglevel = 2/' $E2/e2guardian.conf
sed -i 's/^enablessl = .*/enablessl = off/' $E2/e2guardian.conf

echo "[4] e2guardianf1.conf: bypass 300 s, reportinglevel 3, quet ca exception site, trang block LAB7"
sed -i 's/^bypass = .*/bypass = 300/' $E2/e2guardianf1.conf
sed -i 's/^reportinglevel = .*/reportinglevel = 3/' $E2/e2guardianf1.conf
sed -i 's/^contentscanexceptions = .*/contentscanexceptions = off/' $E2/e2guardianf1.conf
sed -i "s/^#htmltemplate = .*/htmltemplate = 'lab7_block.html'/" $E2/e2guardianf1.conf

echo "[4b] site.story: bat lai checknobypasslists + checknoscanlists/types (bypass va AV dang dung)"
cp $E2/site.story $E2/site.story.bak-$TS
sed -i 's/^function(checknobypasslists)/#function(checknobypasslists)/; s/^function(checknoscanlists)/#function(checknoscanlists)/; s/^function(checknoscantypes)/#function(checknoscantypes)/' $E2/site.story

echo "[5] Danh sach chinh sach"
{ echo; echo '# LAB7 hard block (Geo-Sim, Job Search, game cu the)'; echo china.lab7.test; echo mideast.lab7.test; echo jobs.lab7.test; echo blockedgame.lab7.test;
  echo '# LAB7 warning / temporary bypass'; echo weapons.lab7.test; echo politics.lab7.test; echo religion.lab7.test; echo streaming.lab7.test; } >> $L/bannedsitelist
{ echo; echo '# LAB7 hard block: KHONG cho bypass'; echo china.lab7.test; echo mideast.lab7.test; echo jobs.lab7.test; echo blockedgame.lab7.test; } >> $L/domainsnobypass
{ echo; echo '# LAB7 exception / whitelist'; echo normal.lab7.test; echo education.lab7.test;
  echo '# download.lab7.test KHONG dua vao exception: E2Guardian 5.3.5 bo qua quet AV voi exception site';
  echo '# LAB7 entertainment/games: E2Guardian cho qua, pfSense gioi han theo Schedule 60 phut'; echo entertainment.lab7.test; echo games.lab7.test; } >> $L/exceptionsitelist

echo "[5b] ClamAV doc duoc file tam cua E2Guardian (lab) + cho phep file .bin kiem thu kich thuoc"
sed -i 's/^User clamav/User root/' /etc/clamav/clamd.conf
sed -i 's/^\.bin /#.bin /' $L/bannedextensionlist

echo "[6] Trang block tuy bien (dua tren custom_block_template.html)"
install -m 644 /home/hoangthanhtra/lab7_block.html /usr/share/e2guardian/languages/ukenglish/lab7_block.html

echo "[7] Kiem tra va khoi dong lai dich vu"
squid -k parse 2>&1 | grep -E 'http_port|reply_body|ERROR' || true
systemctl restart squid clamav-daemon
sleep 3
systemctl enable e2guardian >/dev/null 2>&1 || true
systemctl restart e2guardian
sleep 2
systemctl --no-pager is-active squid clamav-daemon e2guardian
ss -lntp | grep -E ':8080|:3128'
