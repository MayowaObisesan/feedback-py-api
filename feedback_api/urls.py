"""feedback_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# from feedback.views import AppsView
from user.views import MyTokenObtainPairView, Logout

app_name = "feedback"

# router = routers.DefaultRouter()
# router.register(r"user", views.UserView, basename="user")
# router.register(r"app", AppsView, basename="feedback")

urlpatterns = [
    path("api/v1/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/logout/", Logout.as_view(), name="logout"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/doc/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/v1/feedback/", include("feedback.urls")),
    path("api/v1/user/", include("user.urls")),
    path("api/v1/timeline/", include("timeline.urls")),
    # path('', include(router.urls))
]
