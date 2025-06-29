FROM python:3.11-slim

WORKDIR /app

COPY dns_adblocker.py .
COPY blocklist.txt .

RUN pip install scapy

CMD ["python", "dns_adblocker.py"]