# Production deployment guide

This document is intended for **release engineers and DevOps** responsible for
deploying Tech Support to a production environment.

---

## Table of contents

1. [Hardware requirements](#1-hardware-requirements)
2. [Required software](#2-required-software)
3. [Network configuration](#3-network-configuration)
4. [Server configuration](#4-server-configuration)
5. [Database setup](#5-database-setup)
6. [Deploying the code](#6-deploying-the-code)
7. [Health checks](#7-health-checks)

---

## 1. Hardware requirements

| Parameter | Minimum | Recommended |
|-----------|---------|-------------|
| Architecture | x86-64 (amd64) | x86-64 or ARM64 |
| vCPU | 1 | 2 |
| RAM | 512 MB | 1 GB |
| Disk | 2 GB | 10 GB |
| Network | 10 Mbit/s | 100 Mbit/s |

> The application is stateless and CPU-light at current scale.
> Scale up RAM and CPU if the number of concurrent users exceeds ~100.

---

## 2. Required software

Install on the production server (Ubuntu 22.04 LTS recommended):

### Runtime

```bash
# Python 3.10 or 3.11
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# Node.js 20 LTS (needed only if serving the frontend from the same host)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Nginx (reverse proxy)
sudo apt install -y nginx

# (Optional) Certbot for TLS
sudo apt install -y certbot python3-certbot-nginx
```

### Build tools (needed once, during deploy)

```bash
# Poetry
pip install poetry

# Yarn
npm install -g yarn
```

---

## 3. Network configuration

### Required open ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 80 | TCP | HTTP (redirect to HTTPS) |
| 443 | TCP | HTTPS |
| 22 | TCP | SSH (restrict to your IP range) |

All other inbound ports should be blocked by the firewall.
The backend (port 8000) must **not** be exposed externally - Nginx proxies it internally.

### UFW example

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 4. Server configuration

### Nginx

Create `/etc/nginx/sites-available/tech-support`:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com www.example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Frontend - serve static build
    root /var/www/tech-support/front/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass         http://127.0.0.1:8000/;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/tech-support /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### TLS certificate (Let's Encrypt)

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

Certbot configures auto-renewal automatically.

### Systemd service for the backend

Create `/etc/systemd/system/tech-support-api.service`:

```ini
[Unit]
Description=Tech Support FastAPI backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/tech-support/back
Environment="PATH=/var/www/tech-support/back/.venv/bin"
ExecStart=/var/www/tech-support/back/.venv/bin/uvicorn src.back.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable tech-support-api
sudo systemctl start tech-support-api
```

---

## 5. Database setup

The current version of the application does not use a database.

When a database is introduced, this section will describe:
- installing and configuring the DBMS (e.g. PostgreSQL)
- creating the database user and schema
- running migrations
- connection string configuration via environment variables

---

## 6. Deploying the code

### First deploy

```bash
# 1. Create the deployment directory
sudo mkdir -p /var/www/tech-support
sudo chown $USER:$USER /var/www/tech-support

# 2. Clone the repository
git clone https://github.com/burjuazniy/tech-support.git /var/www/tech-support
cd /var/www/tech-support

# 3. Build backend
cd back
poetry install --without dev
poetry run python -c "from src.back.main import app; print('OK')"  # smoke test
cd ..

# 4. Build frontend
cd front
yarn install --frozen-lockfile
yarn build
cd ..

# 5. Start services
sudo systemctl start tech-support-api
sudo systemctl reload nginx
```

### Updating to a new version

```bash
cd /var/www/tech-support

# 1. Pull latest code
git pull origin main

# 2. Rebuild backend dependencies (if changed)
cd back && poetry install --without dev && cd ..

# 3. Rebuild frontend
cd front && yarn install --frozen-lockfile && yarn build && cd ..

# 4. Restart the API
sudo systemctl restart tech-support-api
```

### Environment variables

Place production secrets in `/var/www/tech-support/back/.env` (not committed to git).

```bash
# Example .env (adapt to your setup)
DEBUG=false
ALLOWED_ORIGINS=https://example.com
```

The `.env` file must be owned by `www-data` and readable only by that user:

```bash
sudo chown www-data:www-data /var/www/tech-support/back/.env
sudo chmod 600 /var/www/tech-support/back/.env
```

---

## 7. Health checks

### Backend API

```bash
curl -s http://127.0.0.1:8000/ | python3 -m json.tool
# Expected: {"message": "Hello World"}
```

### Systemd service status

```bash
sudo systemctl status tech-support-api
# Expected: Active: active (running)

# Live logs
sudo journalctl -u tech-support-api -f
```

### Nginx

```bash
sudo nginx -t          # config syntax check
sudo systemctl status nginx
curl -I https://example.com   # must return HTTP/2 200
```

### Quick checklist after deploy

- [ ] `curl http://127.0.0.1:8000/` returns `{"message":"Hello World"}`
- [ ] `https://example.com` loads the frontend without certificate warnings
- [ ] `https://example.com/api/` proxies to the backend correctly
- [ ] `sudo systemctl status tech-support-api` shows `active (running)`
- [ ] No `ERROR` lines in `journalctl -u tech-support-api -n 50`
