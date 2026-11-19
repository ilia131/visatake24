from django.urls import path
from apps.accounts.api.views.csrf import CSRFTokenAPIView

from apps.accounts.api.views.authentication import (
    OTPRequestAPIView,
    OTPVerifyAPIView,
    TokenRefreshAPIView,
    MeAPIView,
    LogoutAPIView,
)

urlpatterns = [
    path(
        "auth/otp/request/",
        OTPRequestAPIView.as_view(),
        name="otp-request",
    ),
        path("auth/csrf/", CSRFTokenAPIView.as_view(), name="csrf-token"),


    path(
        "auth/otp/verify/",
        OTPVerifyAPIView.as_view(),
        name="otp-verify",
    ),

    path(
        "auth/token/refresh/",
        TokenRefreshAPIView.as_view(),
        name="token-refresh",
    ),

    path(
        "auth/me/",
        MeAPIView.as_view(),
        name="current-user",
    ),

    path(
        "auth/logout/",
        LogoutAPIView.as_view(),
        name="logout",
    ),
]