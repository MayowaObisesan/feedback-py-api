from django.db import models


class ImageModelManager(models.Manager):
    ...

class FeedbackModelManager(models.Manager):
    # def get_by_natural_key(self, app_name):
    #     return self.get(name=app_name)
    pass


class VersionModelManager(models.Manager):
    ...
