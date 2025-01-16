import os
import platform
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Windows-specific settings
if platform.system().lower() == "windows":
    # Use the solo pool on Windows to avoid multiprocessing issues
    app.conf.update(
        broker_connection_retry_on_startup=True,  # Address deprecation warning
        worker_pool="solo",  # Use solo pool instead of prefork
        broker_connection_max_retries=None,  # Retry broker connection indefinitely
    )

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
