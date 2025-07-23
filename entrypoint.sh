#!/bin/sh
set -e

python manage.py collectstatic --noinput
python manage.py migrate --noinput
# Create superuser if it doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='leticiajackson').exists():
    User.objects.create_superuser('leticiajackson', 'precioustwaya1@gmail.com', '12345678')
END
exec "$@"
