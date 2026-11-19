from django.urls import path

from apps.accounts.api.views.authentication import (
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    RegisterAPIView,
    TokenRefreshAPIView,
)
from apps.accounts.api.views.csrf import CSRFTokenAPIView


urlpatterns = [
    path("auth/csrf/", CSRFTokenAPIView.as_view(), name="csrf-token"),
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("auth/me/", MeAPIView.as_view(), name="current-user"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
]
