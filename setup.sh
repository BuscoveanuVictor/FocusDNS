#!/bin/bash

# Setări
NGINX_CONF="/etc/nginx/sites-available/default"
BACKUP_CONF="/etc/nginx/sites-available/default.bak"
SERVER_NAME="
BACKEND_URL="http://localhost:5000"

# Asigură-te că rulezi ca root
if [ "$EUID" -ne 0 ]; then
  echo "Te rog rulează scriptul cu sudo."
  exit 1
fi

# Backup
echo "Se face backup la fișierul original..."
cp "$NGINX_CONF" "$BACKUP_CONF"

# Suprascrie fișierul cu noua configurație
cat > "$NGINX_CONF" <<EOF
server {
    listen 80 default_server;

    location / {
        proxy_pass $BACKEND_URL;
    }
}
EOF

# Verificare sintaxă Nginx
echo "Se verifică configurația..."
nginx -t

if [ $? -eq 0 ]; then
  echo "Configurația este validă. Se repornește Nginx..."
  systemctl reload nginx
  echo "Gata! Reverse proxy-ul este activ pentru $SERVER_NAME -> $BACKEND_URL"
else
  echo "Eroare în configurația Nginx. Restaurăm fișierul original."
  mv "$BACKUP_CONF" "$NGINX_CONF"
  exit 1
fi
