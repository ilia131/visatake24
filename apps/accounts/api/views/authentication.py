from django.conf import settings
from django.contrib.auth import authenticate
from django.middleware.csrf import rotate_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.serializers.authentication import LoginSerializer, RegisterSerializer
from apps.accounts.api.serializers.schema import MeResponseSerializer, SuccessSerializer, UserResponseSerializer
from apps.accounts.services.authentication import client_ip, limit_auth_attempt
from apps.accounts.services.registration import register_user


def set_token_cookies(response, access, refresh):
    for cookie, token, lifetime in (
        (settings.JWT_ACCESS_COOKIE, access, api_settings.ACCESS_TOKEN_LIFETIME),
        (settings.JWT_REFRESH_COOKIE, refresh, api_settings.REFRESH_TOKEN_LIFETIME),
    ):
        if token:
            response.set_cookie(
                cookie, token, max_age=int(lifetime.total_seconds()),
                httponly=True, secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE, path=settings.JWT_COOKIE_PATH,
            )
    return response


def user_response(user, status_code=status.HTTP_200_OK):
    return Response({"success": True, "user": UserResponseSerializer(user).data}, status=status_code)


def start_session(request, user, status_code=status.HTTP_200_OK):
    rotate_token(request)
    refresh = RefreshToken.for_user(user)
    return set_token_cookies(user_response(user, status_code), str(refresh.access_token), str(refresh))


@method_decorator(csrf_protect, name="dispatch")
class CookieSessionAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]


class RegisterAPIView(CookieSessionAPIView):
    @extend_schema(request=RegisterSerializer, responses={201: MeResponseSerializer})
    def post(self, request):
        limit_auth_attempt("register-ip", client_ip(request), 20)
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)
        return start_session(request, user, status.HTTP_201_CREATED)


class LoginAPIView(CookieSessionAPIView):
    @extend_schema(request=LoginSerializer, responses={200: MeResponseSerializer})
    def post(self, request):
        limit_auth_attempt("login-ip", client_ip(request), 100)
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        limit_auth_attempt("login-phone", serializer.validated_data["phone_number"], 8)
        user = authenticate(request=request, **serializer.validated_data)
        if user is None:
            return Response(
                {"detail": "شماره تلفن یا رمز عبور نادرست است."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return start_session(request, user)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=MeResponseSerializer)
    def get(self, request):
        return user_response(request.user)


class LogoutAPIView(CookieSessionAPIView):
    @extend_schema(request=None, responses=SuccessSerializer)
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass
        rotate_token(request)
        response = Response({"success": True})
        for cookie in (settings.JWT_ACCESS_COOKIE, settings.JWT_REFRESH_COOKIE):
            response.delete_cookie(cookie, path=settings.JWT_COOKIE_PATH, samesite=settings.JWT_COOKIE_SAMESITE)
        return response


class TokenRefreshAPIView(CookieSessionAPIView):
    @extend_schema(request=None, responses=SuccessSerializer)
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token or ""})
        try:
            if not refresh_token:
                raise TokenError()
            serializer.is_valid(raise_exception=True)
        except (TokenError, AuthenticationFailed):
            return Response({"detail": "نشست معتبر نیست."}, status=status.HTTP_401_UNAUTHORIZED)
        data = serializer.validated_data
        return set_token_cookies(Response({"success": True}), data["access"], data.get("refresh"))
