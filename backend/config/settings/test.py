"""Test settings for AnnaSutra."""
import os
from .base import *

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Fallback to in-memory SQLite for isolated local test runs when no DATABASE_URL is set
if "DATABASE_URL" not in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# Enable problem detail responses in testing
REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json"
