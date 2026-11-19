import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
PRODUCTION = {
    "DJANGO_DEBUG": "False",
    "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
    "DJANGO_ALLOWED_HOSTS": "api.example.test",
    "POSTGRES_DB": "test_db",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test-password",
    "POSTGRES_HOST": "db",
}


def load_settings(values, assertions=""):
    # Keep the subprocess isolated from deployment variables and the developer's .env.
    program = (
        "from unittest.mock import patch\n"
        "with patch('environ.Env.read_env'):\n"
        "    from config import settings\n"
        + assertions
    )
    return subprocess.run(
        [sys.executable, "-c", program],
        cwd=ROOT,
        env={"PATH": os.defpath, **values},
        capture_output=True,
        text=True,
    )


def test_development_sqlite():
    result = load_settings(
        {"DJANGO_DEBUG": "True", "DJANGO_USE_SQLITE": "True", "POSTGRES_DB": "unused"},
        'assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"\n',
    )
    assert result.returncode == 0, result.stderr


def test_production_postgres_and_secure_cookies():
    result = load_settings(
        {
            **PRODUCTION,
            "POSTGRES_PORT": "5433",
            "DJANGO_COOKIE_SAMESITE": "None",
            "DJANGO_CORS_ALLOWED_ORIGINS": "https://app.example.test",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "https://app.example.test",
        },
        'assert not settings.DEBUG\n'
        'assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"\n'
        'assert settings.DATABASES["default"]["PORT"] == "5433"\n'
        'assert settings.SECURE_SSL_REDIRECT\n'
        'assert settings.JWT_COOKIE_SECURE and settings.CSRF_COOKIE_SECURE and settings.SESSION_COOKIE_SECURE\n'
        'assert settings.JWT_COOKIE_SAMESITE == settings.CSRF_COOKIE_SAMESITE == "None"\n',
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(("changes", "error"), [
    ({"DJANGO_USE_SQLITE": "True"}, "Production requires PostgreSQL"),
    ({"DJANGO_SECRET_KEY": "weak"}, "Set DJANGO_SECRET_KEY"),
    ({"DJANGO_ALLOWED_HOSTS": "*"}, "Set DJANGO_ALLOWED_HOSTS"),
    ({"POSTGRES_PASSWORD": ""}, "Set POSTGRES_PASSWORD"),
    ({"DJANGO_CORS_ALLOWED_ORIGINS": "http://app.example.test"}, "DJANGO_CORS_ALLOWED_ORIGINS requires"),
    ({"DJANGO_CSRF_TRUSTED_ORIGINS": "https://*.example.test"}, "DJANGO_CSRF_TRUSTED_ORIGINS requires"),
    ({"DJANGO_DEBUG": "True", "DJANGO_COOKIE_SAMESITE": "None"}, "Cross-site cookies require HTTPS"),
])
def test_invalid_settings_fail_at_startup(changes, error):
    result = load_settings({**PRODUCTION, **changes})
    assert result.returncode != 0
    assert error in result.stderr
