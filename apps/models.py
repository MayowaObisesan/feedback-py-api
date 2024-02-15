import uuid

from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone

from .enums import APP_STAGE
from .managers import AppsModelManager, ImageModelManager, VersionModelManager
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


class AppsModel(models.Model):
    """This Model defines Nine Apps Model."""

    objects = AppsModelManager()

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    logo = models.FileField(upload_to="apps/", null=True, blank=True)
    screenshot = models.ManyToManyField(ImageModel)
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="app_owner", on_delete=models.CASCADE, null=True)
    owner = models.UUIDField(default=None)
    name = models.CharField(max_length=32, default="")
    name_id = models.CharField(max_length=32, unique=True, default="")
    playstore_link = models.URLField(max_length=1024, default="", blank=True, null=True)
    appstore_link = models.URLField(max_length=1024, default="", blank=True, null=True)
    galaxystore_link = models.URLField(max_length=1024, default="", blank=True, null=True)
    ahastore_link = models.URLField(max_length=1024, default="", blank=True, null=True)
    external_link = models.URLField(max_length=1024, default="", blank=True, null=True)
    description = models.TextField(max_length=200, default="")
    long_description = models.TextField(max_length=2000, default="")
    # category = ArrayField(models.CharField(max_length=32, blank=True), size=4, default=list)
    category = models.CharField(max_length=256, default="", blank=True, null=True)
    stack = models.CharField(max_length=256, default="", blank=True, null=True)
    development_stage = models.CharField(max_length=256, default="", blank=True, null=True, choices=APP_STAGE)
    # app_version = models.DecimalField(max_digits=16, decimal_places=6)
    version = models.CharField(max_length=16, default="", blank=True, null=True)
    website = models.URLField(max_length=256, default="", blank=True, null=False)
    details = models.JSONField(default=dict, blank=True, null=True)
    bio = models.CharField(max_length=1024, default="", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    download_count = models.CharField(max_length=255, null=True)
    clicks = models.BigIntegerField(null=True)
    views = models.BigIntegerField(null=True)
    target_age = models.IntegerField(null=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("name", "category", "name"),
                name="apps_model_index",
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
        super(AppsModel, self).save(*args, **kwargs)
        TimelineModel.objects.create_app_timeline(user_id=self.owner, app_id=self.id, category="LIST_APP")
        VersionModel.objects.create(app=self.id, version=self.version, latest_feature=self.long_description)

    def natural_key(self):
        return self.name


# class Likes(models.Model):
#     """ This model defines Likes Model """
#     id = models.UUIDField(
#         primary_key=True, default=uuid.uuid4, editable=False, null=False
#     )
#     count = models.BigIntegerField(null=True)

#     def __str__(self):
#         return self.count


class LikesModel(models.Model):
    """
    Spunned from iTheirs Likes Model
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    # user_liking = ArrayField(models.UUIDField(), default=list)
    users_liking = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        null=True,
        help_text="Merkle hash of the users liking this app",
    )
    app_liked = models.UUIDField()
    # liked_star = models.PositiveIntegerField(default=0, blank=False, null=False)
    # liked_app = models.ForeignKey(
    #     "AppsModel",
    #     related_name="liked_app",
    #     on_delete=models.CASCADE,
    #     default=None,
    #     blank=False,
    #     null=True,
    # )
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


class VersionModel(models.Model):
    """ App Versions Model """
    objects = VersionModelManager()

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    app = models.UUIDField()
    version = models.CharField(max_length=16, default="", blank=True, null=True)
    latest_feature = models.TextField(max_length=2000)
    release_date = models.DateTimeField(default=timezone.now)
    release_type = models.CharField(max_length=18, choices=APP_STAGE, default="IN_DEVELOPMENT")
    is_upgrade = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("app",),
                name="apps_version_model_index",
            )
        ]

    def __str__(self):
        return self.app
