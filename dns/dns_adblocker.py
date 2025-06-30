from scapy.all import DNS, DNSQR, DNSRR
import socket
import csv
from datetime import datetime

BLOCKLIST_FILE = "blocklist.txt"  # Fisierul cu domenii blocate
UPSTREAM_DNS = "8.8.8.8"          # DNS-ul la care se face forward daca nu e blocat
DNS_PORT = 53                     # Portul DNS
CSV_LOG = "blocked_ads_log.csv"   # Fisierul de log pentru domenii blocate

def load_blocklist(filename):
    # Incarca blocklist-ul intr-un set pentru cautare rapida
    with open(filename) as f:
        return set(line.strip().lower() for line in f if line.strip() and not line.startswith("#"))

def is_blocked(domain, blocklist):
    domain = domain.lower().rstrip('.')
    # Blocheaza daca domeniul sau oricare dintre domeniile parinte sunt in blocklist
    parts = domain.split('.')
    for i in range(len(parts)):
        check = '.'.join(parts[i:])
        if check in blocklist:
            return True
    return False

def log_blocked(domain, client_ip):
    # Logheaza intr-un fisier CSV domeniul blocat si IP-ul clientului
    with open(CSV_LOG, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now().isoformat(), domain, client_ip])

def main():
    blocklist = load_blocklist(BLOCKLIST_FILE)  # Incarca blocklist-ul la pornire
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creeaza socket UDP pentru DNS
    sock.bind(("0.0.0.0", DNS_PORT))
    print("DNS ad blocker server running on port 53...")

    while True:
        data, addr = sock.recvfrom(512)  # Primeste pachet DNS de la client
        try:
            dns_req = DNS(data)  # Parzeaza pachetul DNS
            if dns_req.qr == 0 and dns_req.opcode == 0 and dns_req.qdcount > 0:
                qname = dns_req.qd.qname.decode().rstrip('.')  # Extrage numele domeniului cerut
                print(f"Received query for: {qname} from {addr[0]}")
                if is_blocked(qname, blocklist):  # Verifica daca domeniul e blocat
                    print(f"Blocked: {qname}")
                    log_blocked(qname, addr[0])  # Logheaza blocarea
                    # Construieste raspuns DNS cu IP 0.0.0.0 (blocare)
                    dns_resp = DNS(
                        id=dns_req.id,
                        qr=1, aa=1, qd=dns_req.qd, ra=1,
                        ancount=1,
                        an=DNSRR(rrname=dns_req.qd.qname, type='A', ttl=60, rdata="127.0.0.1")
                    )
                    sock.sendto(bytes(dns_resp), addr)  # Trimite raspunsul catre client
                else:
                    # Forward request to upstream DNS daca nu e blocat
                    upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    upstream_sock.settimeout(2)
                    upstream_sock.sendto(data, (UPSTREAM_DNS, DNS_PORT))
                    try:
                        upstream_data, _ = upstream_sock.recvfrom(512)  # Primeste raspunsul de la upstream
                        sock.sendto(upstream_data, addr)  # Trimite raspunsul catre client
                    except socket.timeout:
                        print("Upstream DNS timeout")  # Timeout la upstream
                    upstream_sock.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()