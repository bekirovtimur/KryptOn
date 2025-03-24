FROM php:8.3.19-fpm-alpine
RUN docker-php-ext-install mysqli
# COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
WORKDIR /var/www/html
