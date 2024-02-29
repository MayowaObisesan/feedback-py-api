import uuid

# from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone

from .enums import APP_STAGE, PLAYSTORE_APPS_CATEGORY
from .managers import FeedbackModelManager, ImageModelManager, VersionModelManager
from timeline.models import TimelineModel


class ImageModel(models.Model):
    """
    This model defines Nine Images
    """
    objects = ImageModelManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)
    image = models.FileField(upload_to="images", null=True, blank=True)

    def __str__(self):
        return f"{self.image.name} -> {self.image.size}"


class FeedbackModel(models.Model):
    """This Model defines Nine Apps Model."""

    objects = FeedbackModelManager()

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    screenshot = models.ManyToManyField(ImageModel)
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="app_owner", on_delete=models.CASCADE, null=True)
    owner = models.UUIDField(default=None)
    external_link = models.URLField(max_length=1024, default="", blank=True, null=True)
    title = models.CharField(max_length=256, default="", blank=True, null=True)
    description = models.TextField(max_length=200, default="")
    long_description = models.TextField(max_length=2000, default="")
    category = models.CharField(max_length=20, choices=PLAYSTORE_APPS_CATEGORY, default="")
    website = models.URLField(max_length=256, default="", blank=True, null=False)
    clicks = models.BigIntegerField(null=True)
    views = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("category", "title"),
                name="feedback_model_index",
                # opclasses=("gin_trgm_ops", "gin_trgm_ops", "gin_trgm_ops")
            )
            # GinIndex(
            #     fields=["stack", "category", "name"], name="apps_model_index",
            #     opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops']
            # )
        ]

    def __str__(self):
        return self.name

    @staticmethod
    def generate_name_id(name: str) -> str:
        name = name.replace(" ", "-").lower()
        return name

    def save(self, *args, **kwargs):
        """
        Override the save method to add custom updates to the app instance.
        """
        self.name_id = self.generate_name_id(str(self.name))
        super(FeedbackModel, self).save(*args, **kwargs)
        TimelineModel.objects.create_app_timeline(user_id=self.owner, app_id=self.id, category="LIST_APP")

    def natural_key(self):
        return self.name


class LikesUserModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    user_id = models.UUIDField(default=None)


class LikesModel(models.Model):
    """
    Spunned from iTheirs Likes Model
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    # user_liking = ArrayField(models.UUIDField(), default=list)
    # users_liking = models.CharField(
    #     max_length=1024,
    #     default="",
    #     blank=True,
    #     null=True,
    #     help_text="Merkle hash of the users liking this app",
    # )
    users_liking = models.ManyToManyField(LikesUserModel)
    app_liked = models.UUIDField()
    likes_status = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        help_text="For toggling the like of an operation.",
    )
    likes_count = models.BigIntegerField(default=0, blank=True, null=True)
    likes_datetime = models.DateTimeField(auto_now=True)

    def __str__(self) -> int:
        return int(self.likes_count)
