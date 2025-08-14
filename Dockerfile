# Use official PHP image
FROM php:8.1-apache

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY . /var/www/html/

# Install PHP dependencies (if composer.json exists)
# RUN composer install --no-dev --optimize-autoloader

# Set permissions
RUN chown -R www-data:www-data /var/www/html/
RUN a2enmod rewrite

# Expose port
EXPOSE 8081

# Start Apache
CMD ["apache2-foreground"]
