from django.conf import settings

from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        raw_token = request.COOKIES.get(
            settings.JWT_ACCESS_COOKIE
        )

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)

        except Exception:
            raise AuthenticationFailed(
                "توکن معتبر نیست یا منقضی شده است."
            )

        # CSRF protection for unsafe methods
        if request.method not in (
            "GET",
            "HEAD",
            "OPTIONS",
            "TRACE",
        ):
            SessionAuthentication().enforce_csrf(request)

        return user, validated_token