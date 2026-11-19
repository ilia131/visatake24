
from django.conf import settings
from django.middleware.csrf import get_token
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.accounts.services.otp import (
    request_otp,
    OTPError,
)

from drf_spectacular.utils import extend_schema

from apps.accounts.api.serializers.schema import (
    OTPRequestResponseSerializer,
    OTPVerifyResponseSerializer,
    MeResponseSerializer,
    LogoutResponseSerializer,
    SuccessSerializer,
)

from apps.accounts.services.authentication import verify_otp
from apps.accounts.api.serializers.authentication import (
    OTPRequestSerializer,
    OTPVerifySerializer,
)

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from django.conf import settings

class OTPRequestThrottle(AnonRateThrottle):
    scope = "otp"

@extend_schema(
    request=OTPRequestSerializer,
    responses={
        200: OTPRequestResponseSerializer,
        429: SuccessSerializer,
    },
)
class OTPRequestAPIView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [OTPRequestThrottle]

    def post(self, request):

        serializer = OTPRequestSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            request_otp(
                phone_number=serializer.validated_data[
                    "phone_number"
                ]
            )

        except OTPError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response(
            {
                "success": True,
                "message": "Verification code sent.",
            },
            status=status.HTTP_200_OK,
        )

@extend_schema(
    request=OTPVerifySerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "is_new_user": {"type": "boolean"},
            },
        }
    },
)

@extend_schema(
    request=OTPVerifySerializer,
    responses={
        200: OTPVerifyResponseSerializer,
    },
)
class OTPVerifyAPIView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = OTPVerifySerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            user, created = verify_otp(
                **serializer.validated_data
            )

        except OTPError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return Response(
                {
                    "success": False,
                    "message": "Invalid verification request.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "success": True,
                "is_new_user": created,
                "user": {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "is_phone_verified": user.is_phone_verified,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key=settings.JWT_ACCESS_COOKIE,
            value=str(refresh.access_token),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path=settings.JWT_COOKIE_PATH,
        )

        response.set_cookie(
            key=settings.JWT_REFRESH_COOKIE,
            value=str(refresh),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path=settings.JWT_COOKIE_PATH,
        )

        get_token(request)

        return response

@extend_schema(
    responses={200: MeResponseSerializer}
)
class MeAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response({
            "success": True,
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_phone_verified": user.is_phone_verified,
            }
        })

@extend_schema(
    request=None,
    responses={200: LogoutResponseSerializer}
)
class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.COOKIES.get(
            settings.JWT_REFRESH_COOKIE
        )

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        response = Response({
            "success": True,
            "message": "Logged out successfully.",
        })

        response.delete_cookie(
            settings.JWT_ACCESS_COOKIE,
            path=settings.JWT_COOKIE_PATH,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        response.delete_cookie(
            settings.JWT_REFRESH_COOKIE,
            path=settings.JWT_COOKIE_PATH,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        return response
    
    

@extend_schema(
    request=None,
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
            },
        }
    },
)
@extend_schema(
    request=None,
    responses={200: SuccessSerializer}
)
class TokenRefreshAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.JWT_REFRESH_COOKIE
        )

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(
            data={"refresh": refresh_token}
        )

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        response = Response({
            "success": True,
        })

        response.set_cookie(
            key=settings.JWT_ACCESS_COOKIE,
            value=data["access"],
            max_age=15 * 60,
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path=settings.JWT_COOKIE_PATH,
        )

        if "refresh" in data:
            response.set_cookie(
                key=settings.JWT_REFRESH_COOKIE,
                value=data["refresh"],
                max_age=7 * 24 * 60 * 60,
                httponly=True,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                path=settings.JWT_COOKIE_PATH,
            )

        return response

