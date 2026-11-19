from ipaddress import ip_address
from secrets import randbelow

from django.conf import settings
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import salted_hmac
from rest_framework.exceptions import Throttled

from apps.accounts.models import AuthAttempt


WINDOW_SECONDS = 15 * 60


def client_ip(request):
    hops = settings.AUTH_PROXY_HOPS
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")
    if hops and len(forwarded) >= hops:
        try:
            return str(ip_address(forwarded[-hops].strip()))
        except ValueError:
            pass
    return request.META.get("REMOTE_ADDR", "")


def limit_auth_attempt(scope, identifier, limit):
    now = int(timezone.now().timestamp())
    window, elapsed = divmod(now, WINDOW_SECONDS)
    key = salted_hmac("accounts.auth_attempt", f"{scope}:{identifier}", algorithm="sha256").hexdigest()
    if randbelow(128) == 0:
        AuthAttempt.objects.filter(window__lt=window - 1).delete()
    AuthAttempt.objects.get_or_create(key=key, defaults={"window": window})
    AuthAttempt.objects.filter(key=key, window__lt=window).update(window=window, count=0)
    updated = AuthAttempt.objects.filter(key=key, window=window, count__lt=limit).update(count=F("count") + 1)
    if not updated:
        raise Throttled(wait=WINDOW_SECONDS - elapsed)
