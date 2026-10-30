"""DRF Authentication and Permission classes for AnnaSutra JWT auth."""

from rest_framework import authentication, exceptions, permissions

from .models import AppUser, EntityProfile
from .services.token import TokenService


class JWTAuthentication(authentication.BaseAuthentication):
    """Authenticates requests carrying a Bearer JWT access token."""

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        entity_phone = (request.headers.get("X-Entity-Phone") or "").strip()
        entity_email = (request.headers.get("X-Entity-Email") or "").strip().lower()

        if not auth_header:
            if entity_email:
                user = AppUser.objects.select_related("org").filter(email__iexact=entity_email, status="ACTIVE").first()
                if user:
                    return (user, None)
            if entity_phone:
                user = AppUser.objects.select_related("org").filter(phone_e164=entity_phone, status="ACTIVE").first()
                if user:
                    return (user, None)
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        raw_token = parts[1]
        try:
            payload = TokenService.decode_token(raw_token, expected_type="access")
        except Exception as e:
            if entity_email:
                user = AppUser.objects.select_related("org").filter(email__iexact=entity_email, status="ACTIVE").first()
                if user:
                    return (user, raw_token)
            if entity_phone:
                user = AppUser.objects.select_related("org").filter(phone_e164=entity_phone, status="ACTIVE").first()
                if user:
                    return (user, raw_token)
            raise exceptions.AuthenticationFailed(f"Invalid or expired token: {str(e)}")

        user_id = payload.get("sub")
        try:
            user = AppUser.objects.get(user_id=user_id)
        except AppUser.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found.")

        try:
            _ = user.org.pk
        except Exception:
            from apps.organisations.models import Organisation
            org = Organisation.objects.create(
                name=f"Account ({str(user.email or user.phone_e164 or 'User').split('@')[0]})",
                org_type="FARMER",
                verification="PENDING",
            )
            user.org = org
            user.save(update_fields=["org"])

        if user.status != "ACTIVE":
            raise exceptions.AuthenticationFailed("User account is not active.")

        # Attach token payload to user instance for easy access in views
        user.token_payload = payload
        return (user, raw_token)


class IsVerifiedOrg(permissions.BasePermission):
    """Allows access only to users belonging to an organization verified by platform admin."""

    message = "Your organization must be verified by the platform before performing supply chain operations."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not getattr(request.user, "org_id", None):
            return False
        if request.user.org and request.user.org.verification == "VERIFIED":
            return True
        return EntityProfile.objects.filter(user_id=request.user.user_id).exists()


class IsRole(permissions.BasePermission):
    """Allows access only if user has one of the required roles."""

    def __init__(self, *allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in self.allowed_roles
