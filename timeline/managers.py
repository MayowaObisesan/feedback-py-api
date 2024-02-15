from django.db import models


class TimelineModelManager(models.Manager):

    def create_user_timeline(self, user_id, category):
        timeline = self.model(user=user_id, entity="USER", category=category)
        timeline.save()
        return timeline

    def create_app_timeline(self, user_id, app_id, category):
        timeline = self.model(user=user_id, app=app_id, entity="APP", category=category)
        timeline.save()
        return timeline
