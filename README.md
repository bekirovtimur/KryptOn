# KryptOn

[RU](README.md) | [EN](README.en.md)

<img src="https://raw.githubusercontent.com/bekirovtimur/KryptOn/refs/heads/main/other/media/krypton.png" alt="drawing" width="200"/>

OpenSource-система управления подписками на ключи с Telegram-ботом и API-эндпоинтом.

## Описание проекта

KryptOn — комплексное решение для управления подписками на ключи, состоящее из:
1. Telegram-бот (Python)
2. API-эндпоинт подписок (PHP)
3. База данных MySQL

## Как это работает

1. Пользователь обращается к Telegram-боту → автоматическая регистрация в БД
2. Пользователь выбирает подписку из доступных вариантов
3. Бот создаёт запись о подписке в БД и предоставляет:
   - Персональную ссылку на подписку с токеном
   - QR-код для быстрой настройки
4. Пользователь получает персональные ключи по ссылке на подписку (QR-код — для удобства)
5. Подписка автоматически деактивируется после истечения срока

## Технологии

- **Telegram-бот**: Python
- **API-эндпоинт**: PHP
- **База данных**: MySQL
- **Инфраструктура**: Docker, Nginx

## Установка

### Требования
- Сервер (AWS, Azure, Google Cloud и т.д.)
- Доменное имя (например, бесплатно на [FreeDNS](https://freedns.afraid.org/) или [GetFreeDomain](https://www.getfreedomain.name/))

### 1. Подготовка сервера
```bash
apt update && apt upgrade -y
apt install nginx certbot python3-certbot-nginx
curl -sL https://get.docker.com | bash
```
### 2. Клонирование репозитория
```bash
mkdir -p /opt/ && cd /opt/
git clone https://github.com/bekirovtimur/KryptOn.git
cd /opt/KryptOn
```
### 3. Настройка окружения
```bash
cp .env_example .env
nano .env  # Измените параметры конфигурации
```

Файлы в `keys/` — нерабочие примеры-заглушки, а не реальные ключи. Каждый региональный `.txt`-файл содержит образец-заглушку `key://` с нулевым UUID и зарезервированным доменом `.invalid`. Замените их собственными записями ключей (по одной в строке) и укажите в `SUBSCRIPTION_BASE_URL` в `.env` адрес, по которому доступны ваши региональные файлы, прежде чем использовать подписки.

### 4. Запуск проекта
```bash
docker compose up -d
```
### 5. Инициализация базы данных
```bash
docker cp init_db.sql krypton-mysql-1:/tmp/init_db.sql
docker exec krypton-mysql-1 /bin/bash -c 'MYSQL_PWD=${MYSQL_ROOT_PASSWORD} mysql -u root krypton < /tmp/init_db.sql'
docker compose restart
```
### 6. Настройка Nginx и PHP
```bash
cp /opt/KryptOn/other/nginx_config/krypton.conf /etc/nginx/sites-available/krypton.conf
ln -s /etc/nginx/sites-available/krypton.conf /etc/nginx/sites-enabled/

find /opt/KryptOn/php/app -type d -exec chmod 755 {} \;
find /opt/KryptOn/php/app -type f -exec chmod 644 {} \;

ln -s /opt/KryptOn/php/app/index.php /var/www/html/index.php
ln -s /opt/KryptOn/php/app/subscribe.php /var/www/html/subscribe.php

systemctl restart nginx
```
### 7. Получение SSL-сертификата
```bash
certbot --nginx -d your-domain.com
```

## Важные замечания
- Файлы в `keys/` содержат только примеры-заглушки; реальных ключей и учётных данных нет
- Проект предоставляется «как есть»

## Поддержка автора

Если этот скрипт и проект помогли вам, и вы хотите поддержать автора или поблагодарить его — можно воспользоваться ссылкой на ЮMoney:

[![YooMoney](https://img.shields.io/badge/ЮMoney-Поддержать-8B2BE2?style=flat&labelColor=FFB300&color=8B2BE2)](https://yoomoney.ru/to/410013756545159)

## Лицензия
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Распространяется по лицензии MIT. Подробности в файле `LICENSE`.
