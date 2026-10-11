"""Test settings for AnnaSutra."""
from .base import *

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Enable problem detail responses in testing
REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json"
