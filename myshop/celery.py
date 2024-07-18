import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myshop.settings")

# Create a Celery instance.
app = Celery("myshop")

# Set the broker URL to connect to RabbitMQ.
# app.conf.broker_url = "amqp://me6:8811920734272@localhost//"

# Load configuration from Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Enable eager mode (disable the need for a broker).
app.conf.CELERY_ALWAYS_EAGER = True

# Automatically discover tasks.
app.autodiscover_tasks()
