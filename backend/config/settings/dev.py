"""Development settings for AnnaSutra."""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# In development, disable strict password checks for easy testing
AUTH_PASSWORD_VALIDATORS = []
