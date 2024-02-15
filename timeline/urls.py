from django.urls import path, include
from rest_framework import routers

from timeline.views import TimelineView

app_name = "timeline"

router = routers.DefaultRouter()
router.register(r"", TimelineView)

urlpatterns = [
    path("", include(router.urls))
]
