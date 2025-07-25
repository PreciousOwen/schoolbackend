# smartrestaurant/celery.py

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartrestaurant.settings')

app = Celery('smartrestaurant')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks (simplified for now)
app.conf.beat_schedule = {
    # We'll add scheduled tasks later once everything is working
}

# Celery routing
app.conf.task_routes = {
    'notifications.*': {'queue': 'notifications'},
    'analytics.*': {'queue': 'analytics'},
    'reservations.*': {'queue': 'reservations'},
    'payments.*': {'queue': 'payments'},
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
