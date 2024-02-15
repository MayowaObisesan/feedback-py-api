# Django imports
from django.urls import path, include
from rest_framework import routers

from apps.views import AppsView, VersionView

# restframework imports
# from rest_framework.urlpatterns import format_suffix_patterns

app_name = "app"

# API endpoints
# urlpatterns = format_suffix_patterns([path("")])

router = routers.DefaultRouter()
router.register(r"", AppsView)
router.register(r"version", VersionView, basename="version")

urlpatterns = [
    path("", include(router.urls))
]
