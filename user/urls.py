from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from Library import settings

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from user.views import UserViewSet


router = DefaultRouter()
router.register("user", UserViewSet, basename="user")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("manage/", include(router.urls), name="user"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "user"
