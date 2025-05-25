# Frizerie Deployment Guide

This guide provides instructions for deploying the Frizerie application to a production environment.

## Prerequisites

- A server with:
  - Ubuntu 20.04 or later
  - Python 3.9+
  - Node.js 16+
  - Nginx
  - PostgreSQL (optional, can use SQLite for small deployments)

## Backend Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/frizerie.git
cd frizerie
```

### 2. Set Up Python Virtual Environment

```bash
cd frizerie-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Production Settings

Create a `.env` file with production settings:

```bash
# .env file
SECRET_KEY=your_very_secure_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=postgresql://user:password@localhost/frizerie
# For SQLite: DATABASE_URL=sqlite:///./frizerie.db
```

### 4. Set Up the Database

If using PostgreSQL:

```bash
# Create the database
sudo -u postgres createdb frizerie
sudo -u postgres createuser -P frizerie_user

# Grant privileges
sudo -u postgres psql
postgres=# GRANT ALL PRIVILEGES ON DATABASE frizerie TO frizerie_user;
postgres=# \q
```

### 5. Create Systemd Service

Create a systemd service file for the backend:

```bash
sudo nano /etc/systemd/system/frizerie-backend.service
```

Add the following content:

```
[Unit]
Description=Frizerie Backend
After=network.target

[Service]
User=your_username
Group=your_username
WorkingDirectory=/path/to/frizerie/frizerie-backend
Environment="PATH=/path/to/frizerie/frizerie-backend/venv/bin"
ExecStart=/path/to/frizerie/frizerie-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable frizerie-backend
sudo systemctl start frizerie-backend
```

## Frontend Deployment

### 1. Configure Production API URL

Edit the `.env` file in the frontend directory:

```bash
cd frizerie-frontend
nano .env
```

Set the production API URL:

```
VITE_API_URL=https://api.yourdomain.com
```

### 2. Build the Frontend

```bash
npm install
npm run build
```

This will generate a `dist` folder with the production build.

### 3. Configure Nginx

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/frizerie
```

Add the following configuration:

```nginx
# API Server
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend Server
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /path/to/frizerie/frizerie-frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/frizerie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

## Database Backups

Set up a cron job to backup the database daily:

```bash
sudo crontab -e
```

Add the following line for PostgreSQL:

```
0 2 * * * pg_dump -U frizerie_user frizerie > /path/to/backups/frizerie_$(date +\%Y\%m\%d).sql
```

Or for SQLite:

```
0 2 * * * cp /path/to/frizerie/frizerie-backend/frizerie.db /path/to/backups/frizerie_$(date +\%Y\%m\%d).db
```

## Monitoring and Logging

### Set Up Application Logging

Edit the backend settings to enable logging:

```python
# In frizerie-backend/config/settings.py
import logging

# Add logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/frizerie/app.log"),
        logging.StreamHandler()
    ]
)
```

### Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/frizerie
```

Add the following configuration:

```
/var/log/frizerie/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 your_username your_username
}
```

## Maintenance

### Updating the Application

```bash
# Pull latest changes
cd /path/to/frizerie
git pull

# Update backend
cd frizerie-backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart frizerie-backend

# Update frontend
cd ../frizerie-frontend
npm install
npm run build
```

### Monitoring Server Health

Install monitoring tools:

```bash
sudo apt install htop
```

## Troubleshooting

### Check Backend Status

```bash
sudo systemctl status frizerie-backend
```

### View Backend Logs

```bash
sudo journalctl -u frizerie-backend
```

### Check Nginx Logs

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Test API Connectivity

```bash
curl -I https://api.yourdomain.com/health
``` 