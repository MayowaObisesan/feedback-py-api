import os

from django.apps import apps, AppConfig
from django.conf import settings

from celery import Celery

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # pragma: no cover

APP = Celery("feedback_api")


class CeleryConfig(AppConfig):
    name = "feedback_api"
    verbose_name = "Celery Config"

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        APP.config_from_object("django.conf:settings", namespace="CELERY")
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        APP.autodiscover_tasks(installed_apps, force=True)

    # def tearDown(self):
    #     get_redis_connection("default").flushall()
