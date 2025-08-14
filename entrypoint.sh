#!/bin/sh
set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! mysqladmin ping -h"$DB_HOST" --silent; do
    sleep 1
done

echo "Database is ready!"

# Create database tables if they don't exist
echo "Creating database tables..."
mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < /var/www/html/migrations/001_create_tables.sql

# Create superuser if it doesn't exist
echo "Creating default admin user if it doesn't exist..."
mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" << EOF
INSERT IGNORE INTO users (username, email, password, first_name, last_name, is_superuser, is_staff, is_active) 
VALUES ('leticiajackson', 'precioustwaya1@gmail.com', '\$2y\$10\$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Leticia', 'Jackson', 1, 1, 1);
INSERT IGNORE INTO parents (user_id, phone_number) 
SELECT id, '1234567890' FROM users WHERE username = 'leticiajackson' AND NOT EXISTS (SELECT 1 FROM parents WHERE user_id = users.id);
EOF

echo "Starting Apache..."
exec "$@"
