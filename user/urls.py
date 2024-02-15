# Django imports
from django.urls import path, include
from rest_framework import routers

from user.views import UserView

app_name = "user"

router = routers.DefaultRouter()
router.register(r"", UserView, basename="user")

urlpatterns = [
    path("", include(router.urls))
]
