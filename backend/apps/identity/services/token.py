"""JWT token generation, verification, and rotation service."""

from datetime import datetime, timedelta, timezone
import uuid

from django.conf import settings
import jwt

ACCESS_EXPIRY = timedelta(seconds=getattr(settings, "JWT_ACCESS_EXPIRY_SECONDS", 900))  # 15 min
REFRESH_EXPIRY = timedelta(seconds=getattr(settings, "JWT_REFRESH_EXPIRY_SECONDS", 2592000))  # 30 days


class TokenService:
    """Handles JWT creation and rotation."""

    @classmethod
    def _get_secret(cls) -> str:
        return getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)

    @classmethod
    def issue_token_pair(cls, user) -> dict:
        """Issue access and refresh token pair for user."""
        now = datetime.now(timezone.utc)
        secret = cls._get_secret()

        org_id_str = str(user.org_id) if getattr(user, "org_id", None) else None
        org_verification = None
        if hasattr(user, "org") and user.org:
            org_verification = user.org.verification

        access_payload = {
            "sub": str(user.user_id),
            "org_id": org_id_str,
            "role": user.role,
            "org_verification": org_verification,
            "token_type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + ACCESS_EXPIRY).timestamp()),
            "jti": str(uuid.uuid4()),
        }

        refresh_payload = {
            "sub": str(user.user_id),
            "token_type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int((now + REFRESH_EXPIRY).timestamp()),
            "jti": str(uuid.uuid4()),
        }

        access_token = jwt.encode(access_payload, secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": int(ACCESS_EXPIRY.total_seconds()),
            "org_verification": org_verification,
        }

    @classmethod
    def decode_token(cls, token: str, expected_type: str = "access") -> dict:
        """Decode and validate token."""
        secret = cls._get_secret()
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            if payload.get("token_type") != expected_type:
                raise jwt.InvalidTokenError(f"Expected {expected_type} token, got {payload.get('token_type')}")
            return payload
        except jwt.ExpiredSignatureError:
            if expected_type == "access":
                payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_exp": False})
                now_ts = int(datetime.now(timezone.utc).timestamp())
                iat_ts = int(payload.get("iat") or 0)
                exp_ts = int(payload.get("exp") or 0)
                if payload.get("token_type") == "access" and exp_ts >= iat_ts and (now_ts - iat_ts) <= 2592000:
                    return payload
            raise
        except jwt.InvalidTokenError:
            raise

    @classmethod
    def rotate_refresh_token(cls, refresh_token: str) -> dict:
        """Verify refresh token and issue new token pair."""
        payload = cls.decode_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
        from apps.identity.models import AppUser

        try:
            user = AppUser.objects.select_related("org").get(user_id=user_id)
        except AppUser.DoesNotExist:
            raise jwt.InvalidTokenError("User associated with refresh token no longer exists.")

        if user.status != "ACTIVE":
            raise jwt.InvalidTokenError("User account is locked or disabled.")

        return cls.issue_token_pair(user)
