"""Base Django settings for AnnaSutra modular monolith."""
import os
from pathlib import Path
import environ

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "insecure-default-key-for-building-must-override-in-prod"),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost", ".vercel.app"]),
)

# Read .env or .env.local if present
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
environ.Env.read_env(os.path.join(BASE_DIR, "..", ".env.local"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:8000", "http://127.0.0.1:8000", "https://*.vercel.app"],
)
SILENCED_SYSTEM_CHECKS = ["fields.W342"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    # Domain apps (modular monolith)
    "apps.identity",
    "apps.organisations",
    "apps.labels",
    "apps.lots",
    "apps.custody",
    "apps.quality",
    "apps.inventory",
    "apps.ledger",
    "apps.publicview",
    "apps.alerts",
    "apps.reporting",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
except ImportError:
    pass

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database defaults: SQLite for seamless local zero-config runs, or MySQL/PostgreSQL if DATABASE_URL is set
DEFAULT_SQLITE_URL = f"sqlite:///{BASE_DIR / 'annasutra.sqlite3'}"
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=DEFAULT_SQLITE_URL,
    )
}

if DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    options = DATABASES["default"].setdefault("OPTIONS", {})
    if "ssl-mode" in options or "ssl_mode" in options:
        ssl_val = options.pop("ssl-mode", None) or options.pop("ssl_mode", None) or ""
        if ssl_val and "ssl" not in options:
            options["ssl"] = {"check_hostname": False}
    options.setdefault("charset", "utf8mb4")
    options.setdefault("init_command", "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'")
elif DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    db_name = DATABASES["default"].get("NAME")
    if db_name and not os.path.isabs(str(db_name)) and str(db_name) != ":memory:":
        DATABASES["default"]["NAME"] = str(BASE_DIR / db_name)


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR.parent / "static",
]
MEDIA_URL = "/media/"
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    MEDIA_ROOT = Path("/tmp") / "media"
else:
    MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

try:
    import whitenoise  # noqa: F401
    STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedStaticFilesStorage"
except ImportError:
    pass

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache configuration for OTP rate limiting and challenge storage
CACHES = {
    "default": {
        "default_timeout": 300,
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "annasutra-local-cache",
    }
}

# OTP & SMS Gateway configuration (capcom6/android-sms-gateway)
OTP_PROVIDER = env("OTP_PROVIDER", default="android_gateway" if env("SMS_GATEWAY_USER", default="") else "console")
SMS_GATEWAY_URL = env("SMS_GATEWAY_URL", default="https://api.sms-gate.app/3rdparty/v1/messages")
SMS_GATEWAY_USER = env("SMS_GATEWAY_USER", default="")
SMS_GATEWAY_PASSWORD = env("SMS_GATEWAY_PASSWORD", default="")
SMS_GATEWAY_SIM_NUMBER = env.int("SMS_GATEWAY_SIM_NUMBER", default=1)
OTP_DEBUG = env.bool("OTP_DEBUG", default=False)


# WebAuthn relying party configuration
WEBAUTHN_RP_ID = env("WEBAUTHN_RP_ID", default="localhost")
WEBAUTHN_RP_NAME = env("WEBAUTHN_RP_NAME", default="AnnaSutra")
WEBAUTHN_ORIGIN = env("WEBAUTHN_ORIGIN", default="http://localhost:8000")

# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default="")
GOOGLE_REDIRECT_URI = env("GOOGLE_REDIRECT_URI", default="")

# JWT configuration
JWT_SECRET_KEY = env("JWT_SECRET_KEY", default=SECRET_KEY)
JWT_ACCESS_EXPIRY_SECONDS = env.int("JWT_ACCESS_EXPIRY_SECONDS", default=86400)  # 24 hours for agricultural field pilots
JWT_REFRESH_EXPIRY_SECONDS = 2592000  # 30 days

# Django REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.identity.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/minute",
        "user": "600/minute",
        "otp": "5/day",
        "public_scan": "60/minute",
    },
    "EXCEPTION_HANDLER": "config.exceptions.problem_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

# Base security defaults
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

# CERT-In direction: 180-day ICT logging retention configuration
if os.environ.get("VERCEL"):
    LOGS_DIR = Path("/tmp") / "logs"
else:
    LOGS_DIR = BASE_DIR / "logs"

try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    audit_file_handler = {
        "class": "logging.FileHandler",
        "filename": str(LOGS_DIR / "audit.log"),
        "formatter": "audit",
    }
    audit_handlers = ["console", "audit_file"]
except OSError:
    audit_file_handler = {
        "class": "logging.StreamHandler",
        "formatter": "audit",
    }
    audit_handlers = ["console"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "audit": {
            "format": "%(asctime)s [%(levelname)s] [CERT-IN-AUDIT] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "audit_file": audit_file_handler,
    },
    "loggers": {
        "annasutra.audit": {
            "handlers": audit_handlers,
            "level": "INFO",
            "propagate": False,
        },
        "annasutra.security": {
            "handlers": audit_handlers,
            "level": "INFO",
            "propagate": False,
        },
    },
}
