# KryptOn

<img src="https://raw.githubusercontent.com/bekirovtimur/KryptOn/refs/heads/main/other/media/krypton-model.jpg" alt="drawing" width="200"/>

An OpenSource subscription management system with Telegram bot and API endpoint.

## Project Description

KryptOn is a comprehensive proxy subscription management solution consisting of:
1. Telegram bot (Python)
2. Subscription API endpoint (PHP)
3. MySQL database

## How It Works

1. User contacts Telegram bot → automatic registration in DB
2. User selects a subscription from available options
3. Bot creates subscription record in DB and provides:
   - Personal subscription URL with token
   - QR code for quick setup
4. User adds subscription to client software (e.g. Hiddify)
5. Subscription automatically deactivates after expiration

## Technologies

- **Telegram Bot**: Python
- **API Endpoint**: PHP
- **Database**: MySQL
- **Infrastructure**: Docker, Nginx

## Demo

Try the Telegram bot: [@KryptOnAssistBot](https://t.me/KryptOnAssistBot)

## Installation Guide

### Prerequisites
- Server (AWS, Azure, Google Cloud etc.)
- Domain name (For example, you can get it for free on [FreeDNS](https://freedns.afraid.org/) or [GetFreeDomain](https://www.getfreedomain.name/))

### 1. Server Preparation
```bash
apt update && apt upgrade -y
apt install nginx certbot python3-certbot-nginx
curl -sL https://get.docker.com | bash
```
### 2. Clone Repository
```bash
mkdir -p /opt/ && cd /opt/
git clone https://github.com/bekirovtimur/KryptOn.git
cd /opt/KryptOn
```
### 3. Configure Environment
```bash
cp .env_example .env
nano .env  # Edit configuration parameters
```
### 4. Launch Project
```bash
docker compose up -d
```
### 5. Initialize Database
```bash
docker cp init_db.sql krypton-mysql-1:/tmp/init_db.sql
docker exec krypton-mysql-1 /bin/bash -c 'MYSQL_PWD=${MYSQL_ROOT_PASSWORD} mysql -u root krypton < /tmp/init_db.sql'
docker compose restart
```
### 6. Configure Nginx and PHP
```bash
cp /opt/KryptOn/other/nginx_config/krypton.conf /etc/nginx/sites-available/krypton.conf
ln -s /etc/nginx/sites-available/krypton.conf /etc/nginx/sites-enabled/

find /opt/KryptOn/php/app -type d -exec chmod 755 {} \;
find /opt/KryptOn/php/app -type f -exec chmod 644 {} \;

ln -s /opt/KryptOn/php/app/index.php /var/www/html/index.php
ln -s /opt/KryptOn/php/app/subscribe.php /var/www/html/subscribe.php

systemctl restart nginx
```
### 7. Obtain SSL Certificate
```bash
certbot --nginx -d your-domain.com
```
## Important Notes
- Proxy servers (VMess, VLess, Hysteria, Shadowsocks) used in this project are obtained from public sources and provided as examples only
- Project is provided "as is"

## License
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Distributed under the MIT License. See `LICENSE` file for more information.

## Contacts
- **Author**: [Bekirov Timur](https://github.com/bekirovtimur)
- **Telegram**: [@bekirovtimur](https://t.me/bekirovtimur)
- **Issues**: https://github.com/bekirovtimur/KryptOn/issues