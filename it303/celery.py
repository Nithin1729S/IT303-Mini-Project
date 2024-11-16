from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it303.settings')

app = Celery('it303')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# Namespace 'CELERY' means all celery-related configs in settings should have this prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in your Django apps automatically.
app.autodiscover_tasks()
