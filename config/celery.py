import os

from celery import Celery
from django.conf import settings
from kombu import Exchange, Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object(settings, namespace="CELERY", force=True)
app.autodiscover_tasks()

app.conf.task_queues = [
    Queue(settings.CELERY_TASK_DEFAULT_QUEUE, Exchange("tasks"), queue_arguments={"x-max-priority": 10})
]
app.conf.task_default_priority = settings.CELERY_PRIORITY_DEFAULT
