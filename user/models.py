import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone

from user.enums import SOCIAL_ACCOUNT_CHOICES
from user.managers import NineUserManager


class User(AbstractBaseUser):
    """
    Nine User Model
    :Date: March, 26, 2023.
    """

    class Meta:
        ordering = ("pk",)
        indexes = [
            # GinIndex(
            #     fields=["social_account_dict", "lastname", "firstname"], name="user_model_index",
            #     opclasses=["jsonb_path_ops", "gin_trgm_ops", "gin_trgm_ops"]
            # )
            # GinIndex(fields=["social_account_di.ct"], name="user_model_index", opclasses=["jsonb_path_ops"])
            models.Index(
                fields=["lastname", "firstname"],
                name="user_model_index",
                # opclasses=["gin_trgm_ops", "gin_trgm_ops"]
            )
        ]

    objects = NineUserManager()

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False
    )
    eid = models.CharField(max_length=44, null=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    password = models.CharField(max_length=255)
    dp = models.ImageField(upload_to="dp/", null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)
    phone_no = models.CharField(max_length=17, null=True)
    firstname = models.CharField(max_length=128)
    lastname = models.CharField(max_length=128)
    address = models.TextField(null=True)
    country = models.CharField(max_length=255, null=True)
    country_code = models.CharField(max_length=3, null=True)
    # date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_brand = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    social_account_dict = models.JSONField(default=dict, null=True)
    last_resend_code_datetime = models.DateTimeField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [""]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def save_last_login(self):
        self.last_login = timezone.now()
        self.save()

    def update_last_resend_datetime(self):
        self.last_resend_code_datetime = timezone.now()
        self.save()


class AccountCodeModel(models.Model):
    """
    Model to Manage Nine Account Code
    i.e., the registration codes, the reset code etc.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    reg_code = models.CharField(max_length=8, null=True, blank=True)
    reset_code = models.CharField(max_length=8, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.firstname

