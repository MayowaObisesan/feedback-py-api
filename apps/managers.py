from django.contrib.auth.models import UserManager
from django.db import models


class ImageModelManager(models.Manager):
    ...

class AppsModelManager(models.Manager):
    def get_by_natural_key(self, app_name):
        return self.get(name=app_name)


class VersionModelManager(models.Manager):
    ...
