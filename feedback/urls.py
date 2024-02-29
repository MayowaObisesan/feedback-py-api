# Django imports
from django.urls import path, include
from rest_framework import routers

from feedback.views import FeedbackView, VersionView

# restframework imports
# from rest_framework.urlpatterns import format_suffix_patterns

app_name = "feedback"

# API endpoints
# urlpatterns = format_suffix_patterns([path("")])

router = routers.DefaultRouter()
router.register(r"", FeedbackView)
# router.register(r"version", VersionView, basename="version")

urlpatterns = [
    path("", include(router.urls))
]
