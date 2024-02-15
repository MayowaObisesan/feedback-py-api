import uuid

from django.db import models
from django.utils import timezone

from timeline.enums import TIMELINE_ENTITY, TIMELINE_CATEGORY
from timeline.managers import TimelineModelManager


class TimelineModel(models.Model):
    """ App and User Timeline """

    objects = TimelineModelManager()

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.UUIDField()
    app = models.UUIDField(null=True)
    entity = models.CharField(
        max_length=4,
        choices=TIMELINE_ENTITY,
        default="",
        help_text="Either the User or App Entity owns this timeline"
    )
    category = models.CharField(max_length=20, choices=TIMELINE_CATEGORY, default="")

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("user", "app", "entity", "category"),
                name="timeline_model_index",
            )
        ]

    def __str__(self):
        return f"{self.entity} {self.category} timeline"
