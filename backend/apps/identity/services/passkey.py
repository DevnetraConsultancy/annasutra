"""WebAuthn FIDO2 Passkey registration and login service."""

import base64
import json
import logging

from django.conf import settings
from django.core.cache import cache
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

logger = logging.getLogger("annasutra.identity.passkey")


class PasskeyService:
    """Manages WebAuthn challenges, registration, and authentication."""

    @classmethod
    def _rp_id(cls) -> str:
        return getattr(settings, "WEBAUTHN_RP_ID", "localhost")

    @classmethod
    def _rp_name(cls) -> str:
        return getattr(settings, "WEBAUTHN_RP_NAME", "AnnaSutra")

    @classmethod
    def _origin(cls) -> str:
        return getattr(settings, "WEBAUTHN_ORIGIN", "http://localhost:8000")

    @classmethod
    def create_registration_options(cls, user) -> dict:
        """Create WebAuthn registration options for user."""
        options = generate_registration_options(
            rp_id=cls._rp_id(),
            rp_name=cls._rp_name(),
            user_id=user.user_id.bytes,
            user_name=user.phone_e164,
            user_display_name=f"AnnaSutra User {user.phone_e164[-4:]}",
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
        )
        # Store challenge in cache for 5 minutes
        cache_key = f"webauthn:reg_challenge:{user.user_id}"
        cache.set(cache_key, options.challenge, timeout=300)

        return json.loads(options_to_json(options))

    @classmethod
    def verify_registration(cls, user, credential_json: dict) -> object:
        """Verify WebAuthn registration response and save credential."""
        cache_key = f"webauthn:reg_challenge:{user.user_id}"
        expected_challenge = cache.get(cache_key)
        if not expected_challenge:
            raise ValueError("Registration challenge expired or not found.")

        verification = verify_registration_response(
            credential=credential_json,
            expected_challenge=expected_challenge,
            expected_origin=cls._origin(),
            expected_rp_id=cls._rp_id(),
            require_user_verification=False,
        )
        cache.delete(cache_key)

        from apps.identity.models import PasskeyCredential

        credential = PasskeyCredential.objects.create(
            credential_id=verification.credential_id,
            user=user,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
        )
        return credential

    @classmethod
    def create_authentication_options(cls, user=None) -> dict:
        """Create WebAuthn authentication options."""
        allow_credentials = []
        cache_key = "webauthn:auth_challenge:global"

        if user:
            from apps.identity.models import PasskeyCredential

            user_creds = PasskeyCredential.objects.filter(user=user, revoked_at__isnull=True)
            allow_credentials = [
                PublicKeyCredentialDescriptor(id=c.credential_id) for c in user_creds
            ]
            cache_key = f"webauthn:auth_challenge:{user.user_id}"

        options = generate_authentication_options(
            rp_id=cls._rp_id(),
            allow_credentials=allow_credentials if allow_credentials else None,
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        cache.set(cache_key, options.challenge, timeout=300)

        return json.loads(options_to_json(options))

    @classmethod
    def verify_authentication(cls, credential_json: dict, user=None) -> object:
        """Verify WebAuthn authentication response."""
        from apps.identity.models import PasskeyCredential

        raw_id_b64 = credential_json.get("rawId") or credential_json.get("id")
        if not raw_id_b64:
            raise ValueError("Credential id is missing.")

        # Decode credential id (url-safe b64 with padding)
        padding = "=" * ((4 - len(raw_id_b64) % 4) % 4)
        cred_id_bytes = base64.urlsafe_b64decode(raw_id_b64 + padding)

        try:
            stored_cred = PasskeyCredential.objects.select_related("user").get(
                credential_id=cred_id_bytes,
                revoked_at__isnull=True,
            )
        except PasskeyCredential.DoesNotExist:
            raise ValueError("Passkey credential not recognized.")

        target_user = user or stored_cred.user
        cache_key = f"webauthn:auth_challenge:{target_user.user_id}"
        expected_challenge = cache.get(cache_key) or cache.get("webauthn:auth_challenge:global")
        if not expected_challenge:
            raise ValueError("Authentication challenge expired or not found.")

        verification = verify_authentication_response(
            credential=credential_json,
            expected_challenge=expected_challenge,
            expected_origin=cls._origin(),
            expected_rp_id=cls._rp_id(),
            credential_public_key=bytes(stored_cred.public_key),
            credential_current_sign_count=stored_cred.sign_count,
            require_user_verification=False,
        )

        cache.delete(cache_key)
        stored_cred.sign_count = verification.new_sign_count
        stored_cred.save(update_fields=["sign_count"])

        return stored_cred.user
