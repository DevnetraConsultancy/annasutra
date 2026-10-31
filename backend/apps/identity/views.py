"""Identity & Authentication API views conforming to api/openapi.yaml."""

import base64
import re
import uuid

from django.db import IntegrityError, transaction
from django.utils import timezone
import jwt
from rest_framework import exceptions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organisations.models import Organisation
from .models import AppUser, Device, EntityProfile
from .services.entity_allocation import get_or_mint_farmer_uid
from .services.otp import OtpService
from .services.passkey import PasskeyService
from .services.token import TokenService

SINGLE_ADMIN_EMAIL = "devnetraconsultancy@gmail.com"
ALL_ENTITY_ROLES = ["PRODUCER", "AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"]


def build_portal_registrations_for_user(user) -> dict:
    """Return all 6 role registrations and approved roles for a given AppUser."""
    profiles = list(EntityProfile.objects.filter(user_id=user.user_id).order_by("created_at"))
    by_role = {p.role: p for p in profiles}

    role_labels = {
        "PRODUCER": "Producer / Farmer",
        "AGGREGATOR": "Aggregator / FPO",
        "PROCESSOR": "Processor / Packhouse",
        "WHOLESALER": "Wholesaler",
        "DISTRIBUTOR": "Distributor",
        "RETAILER": "Retailer",
    }

    registrations = []
    approved_roles = []
    for role_code in ALL_ENTITY_ROLES:
        prof = by_role.get(role_code)
        if not prof:
            registrations.append({
                "role": role_code,
                "role_label": role_labels[role_code],
                "registered": False,
                "status": "NOT_REGISTERED",
                "entity_id": None,
                "application_ref": None,
                "role_uid": None,
                "farmer_uid": None,
                "organisation_name": None,
                "admin_remark": None,
                "action": "REGISTER",
            })
            continue

        uid = get_or_mint_farmer_uid(prof) if prof.status == "VERIFIED" else None
        latest_review = prof.reviews.order_by("-created_at").first()
        admin_remark = latest_review.reason if latest_review and latest_review.reason else None
        app_ref = f"APP-{str(prof.entity_id)[:8].upper()}"

        if prof.status == "VERIFIED":
            approved_roles.append(role_code)
            action = "OPEN_CONSOLE"
        elif prof.status in ("NEEDS_CHANGES", "CHANGES_REQUESTED", "DRAFT"):
            action = "FIX_AND_RESUBMIT" if prof.status != "DRAFT" else "CONTINUE_DRAFT"
        elif prof.status == "REJECTED":
            action = "VIEW_REMARK"
        else:
            action = "VIEW_STATUS"

        registrations.append({
            "role": role_code,
            "role_label": role_labels.get(role_code, role_code),
            "registered": True,
            "status": "APPROVED" if prof.status == "VERIFIED" else prof.status,
            "raw_status": prof.status,
            "entity_id": str(prof.entity_id),
            "entity_code": prof.entity_code,
            "application_ref": app_ref,
            "role_uid": uid,
            "farmer_uid": uid,
            "organisation_name": prof.organisation_name or f"{prof.first_name} {prof.last_name}".strip(),
            "admin_remark": admin_remark,
            "submitted_at": prof.submitted_at.isoformat() if prof.submitted_at else None,
            "verified_at": prof.verified_at.isoformat() if prof.verified_at else None,
            "action": action,
        })

    if str(getattr(user, "email", None) or "").strip().lower() == SINGLE_ADMIN_EMAIL:
        if "ADMIN" not in approved_roles:
            approved_roles.append("ADMIN")
    return {
        "registrations": registrations,
        "approved_roles": approved_roles,
    }


class OtpRequestView(APIView):
    """Send an OTP code to Gmail and/or phone number."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        email = request.data.get("email")
        if not phone and not email:
            raise exceptions.ValidationError({"detail": "Phone number or Gmail is required.", "code": "FIELD_REQUIRED"})

        language = request.data.get("language", "en")
        try:
            result = OtpService.request_otp(phone=phone, language=language, email=email)
        except ValueError as e:
            raise exceptions.ValidationError({"detail": str(e), "code": "INVALID_PHONE"})

        if result.get("status") == "RATE_LIMITED":
            return Response(
                {
                    "type": "urn:problem:rate-limited",
                    "title": "Too Many Requests",
                    "status": 429,
                    "detail": result.get("message"),
                    "code": "RATE_LIMITED",
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if result.get("status") == "GATEWAY_ERROR":
            return Response(
                {
                    "type": "urn:problem:gateway-error",
                    "title": "Gateway Error",
                    "status": 502,
                    "detail": result.get("message", "Failed to dispatch verification code."),
                    "code": "GATEWAY_ERROR",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        resp_data = {"status": "accepted", "channel": result.get("channel", "SMS")}
        if "debug_code" in result:
            resp_data["debug_code"] = result["debug_code"]

        return Response(resp_data, status=status.HTTP_202_ACCEPTED)


class OtpVerifyView(APIView):
    """Verify OTP code, auto-enroll device key, and issue tokens.
    Decision 30: First sign-in must be Google Sign-In (Gmail).
    Mobile OTP login works ONLY if that mobile is already verified and linked to an existing account.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        email = request.data.get("email")
        code = request.data.get("code")

        if (not phone and not email) or not code:
            raise exceptions.ValidationError(
                {"detail": "Phone (or email) and code are required.", "code": "FIELD_REQUIRED"}
            )

        try:
            is_valid = OtpService.verify_otp(phone=phone, code=code, email=email)
        except ValueError as e:
            raise exceptions.ValidationError({"detail": str(e), "code": "INVALID_PHONE"})

        if not is_valid:
            return Response(
                {
                    "type": "urn:problem:invalid-otp",
                    "title": "Invalid Code",
                    "status": 400,
                    "detail": "Verification code is invalid, expired, or max attempts exceeded.",
                    "code": "INVALID_OTP",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                user = None
                if phone:
                    user = AppUser.objects.select_related("org").filter(phone_e164=phone).first()
                    if not user:
                        linked_profile = EntityProfile.objects.filter(phone_e164=phone).first()
                        if linked_profile:
                            user = AppUser.objects.select_related("org").filter(user_id=linked_profile.user_id).first()
                if not user and email:
                    user = AppUser.objects.select_related("org").filter(email__iexact=str(email).strip().lower()).first()

                # Decision 30: Mobile OTP login works ONLY if that mobile is already verified and linked
                if not user:
                    return Response(
                        {
                            "type": "urn:problem:gmail-required-first",
                            "title": "Google Sign-In Required First",
                            "status": 400,
                            "detail": "First sign-in must use Google Sign-In (Gmail). Mobile OTP login works only if that mobile is already verified and linked to an existing Gmail account.",
                            "code": "GMAIL_REQUIRED_FIRST",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Register device key if provided in verify request
                device_pub_key = request.data.get("device_public_key")
                if device_pub_key:
                    try:
                        pk_bytes = base64.b64decode(device_pub_key)
                    except Exception:
                        pk_bytes = device_pub_key.encode("utf-8")

                    Device.objects.create(
                        device_id=uuid.uuid4(),
                        user=user,
                        public_key=pk_bytes,
                        key_alg=request.data.get("key_alg", "ES256"),
                        label=request.data.get("device_label", "Primary Device"),
                    )

            profile = (
                EntityProfile.objects.filter(user_id=user.user_id).order_by("-verified_at", "-updated_at").first()
                or (EntityProfile.objects.filter(phone_e164=user.phone_e164).first() if user.phone_e164 else None)
            )
            farmer_uid = get_or_mint_farmer_uid(profile if profile else user)
            email_val = (user.email or (profile.email if profile else "") or "").strip().lower()
            portal_info = build_portal_registrations_for_user(user)
            token_pair = TokenService.issue_token_pair(user)
            token_pair["access"] = token_pair["access_token"]
            token_pair["refresh"] = token_pair["refresh_token"]
            token_pair["is_admin"] = email_val == SINGLE_ADMIN_EMAIL
            token_pair["registrations"] = portal_info["registrations"]
            token_pair["approved_roles"] = portal_info["approved_roles"]
            token_pair["user"] = {
                "user_id": str(user.user_id),
                "phone": user.phone_e164,
                "email": email_val or None,
                "role": user.role,
                "entity_role": profile.role if profile else "PRODUCER",
                "farmer_uid": farmer_uid,
                "status": user.status,
                "is_admin": email_val == SINGLE_ADMIN_EMAIL,
            }
        except Exception as exc:
            import logging
            logging.getLogger("annasutra.identity").error("Authentication database session error: %s", exc, exc_info=True)
            return Response(
                {
                    "type": "urn:problem:database-unavailable",
                    "title": "Service Unavailable",
                    "status": 503,
                    "detail": "Authentication service is currently unable to reach the database. Please try again shortly.",
                    "code": "DATABASE_ERROR",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(token_pair, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """Rotate and refresh token pair."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            raise exceptions.ValidationError(
                {"detail": "refresh_token is required.", "code": "FIELD_REQUIRED"}
            )

        try:
            tokens = TokenService.rotate_refresh_token(refresh_token)
            return Response(tokens, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response(
                {
                    "type": "urn:problem:token-expired",
                    "title": "Token Expired",
                    "status": 401,
                    "detail": "The refresh token has expired. Please log in again.",
                    "code": "TOKEN_EXPIRED",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError as e:
            return Response(
                {
                    "type": "urn:problem:invalid-token",
                    "title": "Invalid Token",
                    "status": 401,
                    "detail": str(e),
                    "code": "INVALID_TOKEN",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class PasskeyRegisterOptionsView(APIView):
    """Generate WebAuthn registration options for authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        options = PasskeyService.create_registration_options(request.user)
        return Response({"options": options}, status=status.HTTP_200_OK)


class PasskeyRegisterVerifyView(APIView):
    """Verify WebAuthn credential registration."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        credential = request.data.get("credential")
        if not credential:
            raise exceptions.ValidationError(
                {"detail": "credential payload is required.", "code": "FIELD_REQUIRED"}
            )

        try:
            PasskeyService.verify_registration(request.user, credential)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise exceptions.ValidationError({"detail": str(e), "code": "PASSKEY_VERIFY_FAILED"})


class PasskeyLoginOptionsView(APIView):
    """Generate WebAuthn authentication options for passkey login."""

    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        target_user = None
        if phone:
            target_user = AppUser.objects.filter(phone_e164=phone, status="ACTIVE").first()

        options = PasskeyService.create_authentication_options(user=target_user)
        return Response({"options": options}, status=status.HTTP_200_OK)


class PasskeyLoginVerifyView(APIView):
    """Verify WebAuthn authentication response and issue tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get("credential")
        if not credential:
            raise exceptions.ValidationError(
                {"detail": "credential payload is required.", "code": "FIELD_REQUIRED"}
            )

        try:
            user = PasskeyService.verify_authentication(credential)
            tokens = TokenService.issue_token_pair(user)
            return Response(tokens, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "type": "urn:problem:passkey-auth-failed",
                    "title": "Authentication Failed",
                    "status": 401,
                    "detail": str(e),
                    "code": "PASSKEY_AUTH_FAILED",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class DeviceListCreateView(APIView):
    """List or enroll hardware devices."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = Device.objects.filter(user=request.user).order_by("-created_at")
        results = [
            {
                "device_id": str(d.device_id),
                "label": d.label or "Unnamed Device",
                "created_at": d.created_at.isoformat(),
                "revoked_at": d.revoked_at.isoformat() if d.revoked_at else None,
            }
            for d in devices
        ]
        return Response(results, status=status.HTTP_200_OK)

    def post(self, request):
        pub_key_str = request.data.get("public_key")
        if not pub_key_str:
            raise exceptions.ValidationError(
                {"detail": "public_key is required.", "code": "FIELD_REQUIRED"}
            )

        try:
            pk_bytes = base64.b64decode(pub_key_str)
        except Exception:
            pk_bytes = pub_key_str.encode("utf-8")

        device = Device.objects.create(
            device_id=uuid.uuid4(),
            user=request.user,
            public_key=pk_bytes,
            key_alg=request.data.get("key_alg", "ES256"),
            label=request.data.get("label", "Mobile Device"),
        )
        return Response(
            {
                "device_id": str(device.device_id),
                "label": device.label,
                "created_at": device.created_at.isoformat(),
                "revoked_at": None,
            },
            status=status.HTTP_201_CREATED,
        )


class DeviceDetailView(APIView):
    """Revoke an enrolled device."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, device_id):
        device = Device.objects.filter(device_id=device_id, user=request.user).first()
        if not device:
            raise exceptions.NotFound({"detail": "Device not found.", "code": "NOT_FOUND"})

        device.revoked_at = timezone.now()
        device.save(update_fields=["revoked_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


def _ensure_identity_mysql_schema():
    """Idempotently add any missing columns in MySQL to match Decision 30."""
    from django.db import connection
    try:
        if connection.vendor == "mysql":
            with connection.cursor() as cursor:
                try:
                    cursor.execute("ALTER TABLE app_user ADD COLUMN email VARCHAR(190) NULL UNIQUE;")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE app_user MODIFY COLUMN phone_e164 VARCHAR(32) NULL;")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE entity_profile MODIFY COLUMN phone_e164 VARCHAR(20) NULL;")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE entity_profile MODIFY COLUMN entity_code VARCHAR(32) NULL;")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE entity_profile ADD UNIQUE KEY uq_user_role (user_id, role);")
                except Exception:
                    pass
    except Exception as e:
        import logging
        logging.getLogger("annasutra.identity").warning("Schema check notice: %s", e)


def _complete_google_user_session(email: str, name: str, raw_phone: str = "", requested_role: str = "PRODUCER", create_draft: bool = True):
    """Create or link AppUser + EntityProfile for a verified Google account and issue JWT pair.
    Decisions 29, 30, 31, 32, 35:
    - Gmail (`email`) is the mandatory, unique, lowercase, immutable primary key.
    - Mobile (`phone_e164`) is optional.
    - One Gmail can register across multiple roles (`unique(user_id, role)`).
    """
    email = str(email or "").strip().lower()
    if not email or "@" not in email:
        raise exceptions.ValidationError(
            {"detail": "A valid Google email address is required.", "code": "INVALID_EMAIL"}
        )

    valid_roles = {"PRODUCER", "AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER", "ADMIN"}
    is_single_admin = email == SINGLE_ADMIN_EMAIL
    if is_single_admin:
        requested_role = "ADMIN"
    elif requested_role not in valid_roles:
        requested_role = "PRODUCER"

    phone_e164 = None
    if raw_phone:
        digits = re.sub(r"\D", "", str(raw_phone))
        if len(digits) == 10:
            phone_e164 = f"+91{digits}"
        elif len(digits) >= 11:
            phone_e164 = f"+{digits}"

    _ensure_identity_mysql_schema()

    org_type_map = {
        "PRODUCER": "FARMER",
        "AGGREGATOR": "AGGREGATOR",
        "PROCESSOR": "PROCESSOR",
        "WHOLESALER": "WHOLESALER",
        "DISTRIBUTOR": "DISTRIBUTOR",
        "RETAILER": "RETAILER",
        "ADMIN": "OPERATOR",
    }

    with transaction.atomic():
        try:
            user = AppUser.objects.filter(email__iexact=email).first()
        except Exception as e:
            if "Unknown column 'app_user.email'" in str(e) or "1054" in str(e):
                _ensure_identity_mysql_schema()
                user = AppUser.objects.filter(email__iexact=email).first()
            else:
                raise

        existing_profile_by_email = EntityProfile.objects.filter(email__iexact=email).first()

        if not user and existing_profile_by_email:
            user = AppUser.objects.filter(user_id=existing_profile_by_email.user_id).first()

        if not user and phone_e164:
            user = AppUser.objects.filter(phone_e164=phone_e164).first()

        if existing_profile_by_email and not phone_e164 and existing_profile_by_email.phone_e164:
            phone_e164 = existing_profile_by_email.phone_e164

        if not user:
            org = Organisation.objects.create(
                name=name or f"Account ({email.split('@')[0]})",
                org_type="OPERATOR" if is_single_admin else org_type_map.get(requested_role, "FARMER"),
                verification="VERIFIED" if is_single_admin else "PENDING",
            )
            try:
                user = AppUser.objects.create(
                    user_id=uuid.uuid4(),
                    org=org,
                    email=email,
                    phone_e164=phone_e164,
                    role="OWNER",
                    status="ACTIVE",
                )
            except IntegrityError:
                user = AppUser.objects.filter(email__iexact=email).first()
                if not user and phone_e164:
                    user = AppUser.objects.filter(phone_e164=phone_e164).first()
                if user:
                    user.org = org
                    if not user.email:
                        user.email = email
                    user.save(update_fields=["org", "email"])
        else:
            # Repair orphaned organisation pointer if previous purge deleted the org row
            try:
                _ = user.org.pk
            except Exception:
                org = Organisation.objects.create(
                    name=name or f"Account ({email.split('@')[0]})",
                    org_type="OPERATOR" if is_single_admin else org_type_map.get(requested_role, "FARMER"),
                    verification="VERIFIED" if is_single_admin else "PENDING",
                )
                user.org = org
                user.save(update_fields=["org"])

            user_updates = []
            if not user.email:
                user.email = email
                user_updates.append("email")
            if phone_e164 and not user.phone_e164:
                if not AppUser.objects.filter(phone_e164=phone_e164).exclude(user_id=user.user_id).exists():
                    user.phone_e164 = phone_e164
                    user_updates.append("phone_e164")
            if user_updates:
                user.save(update_fields=user_updates)

        if is_single_admin:
            # Sovereign Admin is the regulatory reviewer, not an applicant.
            EntityProfile.objects.filter(email__iexact=email).delete()
            profile = None
            active_profile = None
        else:
            # Look up the profile for the requested role under this Gmail user
            profile = EntityProfile.objects.filter(user_id=user.user_id, role=requested_role).first()
            if not profile and phone_e164:
                profile = EntityProfile.objects.filter(phone_e164=phone_e164, role=requested_role).first()
            if not profile and email:
                profile = EntityProfile.objects.filter(email__iexact=email, role=requested_role).first()

            parts = name.split(None, 1) if name else []
            first_name = parts[0] if parts else ""
            last_name = parts[1] if len(parts) > 1 else ""

            if not profile and create_draft:
                try:
                    profile = EntityProfile.objects.create(
                        entity_id=uuid.uuid4(),
                        user_id=user.user_id,
                        role=requested_role,
                        phone_e164=phone_e164,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        organisation_name=name or "",
                        village_town="",
                        district="",
                        state="",
                        address_line1="",
                        pincode="000000",
                        photo_object_key="",
                        status="DRAFT",
                        version=1,
                    )
                except IntegrityError:
                    profile = EntityProfile.objects.filter(user_id=user.user_id, role=requested_role).first()
            elif profile:
                updated_fields = []
                if profile.email != email:
                    profile.email = email
                    updated_fields.append("email")
                if phone_e164 and not profile.phone_e164:
                    profile.phone_e164 = phone_e164
                    updated_fields.append("phone_e164")
                if first_name and not profile.first_name:
                    profile.first_name = first_name
                    updated_fields.append("first_name")
                if last_name and not profile.last_name:
                    profile.last_name = last_name
                    updated_fields.append("last_name")
                if profile.user_id != user.user_id:
                    profile.user_id = user.user_id
                    updated_fields.append("user_id")
                if updated_fields:
                    profile.save(update_fields=updated_fields)

            active_profile = profile or EntityProfile.objects.filter(user_id=user.user_id).order_by("-verified_at", "-updated_at").first()

        farmer_uid = get_or_mint_farmer_uid(active_profile) if active_profile else ("ADMIN-AUTHORITY" if is_single_admin else None)
        portal_info = build_portal_registrations_for_user(user)
        is_admin = email == SINGLE_ADMIN_EMAIL

        token_pair = TokenService.issue_token_pair(user)
        token_pair["authenticated"] = True
        token_pair["auth_provider"] = "GOOGLE"
        token_pair["farmer_uid"] = farmer_uid
        token_pair["is_admin"] = is_admin
        token_pair["registrations"] = portal_info["registrations"]
        token_pair["approved_roles"] = ["ADMIN"] if is_single_admin else portal_info["approved_roles"]
        token_pair["access"] = token_pair["access_token"]
        token_pair["refresh"] = token_pair["refresh_token"]
        token_pair["user"] = {
            "user_id": str(user.user_id),
            "phone": user.phone_e164 or (active_profile.phone_e164 if active_profile else None),
            "email": email,
            "name": "AnnaSutra Sovereign Secretariat" if is_single_admin else (((f"{active_profile.first_name} {active_profile.last_name}".strip() if active_profile else "") or name or email)),
            "role": "ADMIN" if is_single_admin else user.role,
            "entity_role": "ADMIN" if is_single_admin else (active_profile.role if active_profile else requested_role),
            "farmer_uid": farmer_uid,
            "status": user.status,
            "auth_provider": "google",
            "is_admin": is_admin,
        }
        return token_pair


def _resolve_google_redirect_uri(request) -> str:
    """Resolve the canonical Google OAuth 2.0 callback URI."""
    from django.conf import settings

    configured = getattr(settings, "GOOGLE_REDIRECT_URI", "").strip()
    if configured:
        return configured
    host = request.get_host()
    proto = request.headers.get("X-Forwarded-Proto", "")
    scheme = "https" if (request.is_secure() or proto == "https" or "vercel.app" in host) else "http"
    return f"{scheme}://{host}/api/v1/auth/google/callback"


class GoogleOAuthStartView(APIView):
    """Initiate standard Google OAuth 2.0 Authorization Code flow."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        import time
        import urllib.parse
        from django.conf import settings
        from django.http import HttpResponse, HttpResponseRedirect

        role = str(request.GET.get("role") or "PRODUCER").strip().upper()
        phone = str(request.GET.get("phone") or "").strip()
        portal_only = str(request.GET.get("portal") or "").strip() == "1"
        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "").strip()
        redirect_uri = _resolve_google_redirect_uri(request)

        if not client_id:
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Google OAuth 2.0 Configuration Required — AnnaSutra</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #07271d; color: #f8fafc; margin: 0; padding: 24px; display: flex; align-items: center; justify-content: center; min-height: 90vh; }}
    .card {{ background: #ffffff; color: #0f172a; max-width: 520px; width: 100%; border-radius: 16px; padding: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.4); }}
    h2 {{ margin: 0 0 8px; color: #0b3d2e; font-size: 19px; }}
    p {{ font-size: 13.5px; color: #475569; line-height: 1.5; margin: 0 0 12px; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #0f172a; word-break: break-all; display: block; margin: 6px 0 12px; padding: 8px 10px; border: 1px solid #cbd5e1; }}
    .btn {{ background: #0b3d2e; color: #fff; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; width: 100%; margin-top: 8px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>Google OAuth 2.0 Credentials Needed</h2>
    <p>To enable Google OAuth Consent Sign-In, add your Google OAuth 2.0 Client ID and Secret in your environment variables (Vercel Project Settings &rarr; Environment Variables or <code>backend/.env</code>):</p>
    <code>GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com<br/>GOOGLE_CLIENT_SECRET=your-client-secret</code>
    <p>In <strong>Google Cloud Console &rarr; APIs &amp; Services &rarr; Credentials</strong>, set this exact Authorized Redirect URI:</p>
    <code>{redirect_uri}</code>
    <button class="btn" onclick="window.close()">Close Window</button>
  </div>
</body>
</html>"""
            return HttpResponse(html, status=200)

        state_token = jwt.encode(
            {
                "role": role,
                "phone": phone,
                "portal": portal_only,
                "exp": int(time.time()) + 600,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
            "state": state_token,
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        return HttpResponseRedirect(auth_url)


class GoogleOAuthCallbackView(APIView):
    """Handle Google OAuth 2.0 Authorization Code callback.
    Decisions 29 & 30: Gmail is the primary identity and mobile is optional.
    Completes sign-in immediately without forcing a mobile number gate.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        import json
        import urllib.parse
        import urllib.request
        from django.conf import settings
        from django.http import HttpResponse

        error = request.GET.get("error")
        if error:
            return HttpResponse(
                "<script>if(window.opener){window.close();}else{window.location.href='/';}</script>",
                content_type="text/html",
            )

        code = str(request.GET.get("code") or "").strip()
        state_token = str(request.GET.get("state") or "").strip()
        if not code:
            return HttpResponse("Missing authorization code.", status=400)

        role = "PRODUCER"
        phone = ""
        portal_only = False
        if state_token:
            try:
                state_data = jwt.decode(state_token, settings.SECRET_KEY, algorithms=["HS256"])
                role = str(state_data.get("role") or "PRODUCER").strip().upper()
                phone = str(state_data.get("phone") or "").strip()
                portal_only = bool(state_data.get("portal"))
            except Exception:
                pass

        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "").strip()
        client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "").strip()
        redirect_uri = _resolve_google_redirect_uri(request)

        try:
            token_payload = urllib.parse.urlencode(
                {
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            ).encode("utf-8")
            token_req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=token_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(token_req, timeout=10) as resp:
                token_resp = json.loads(resp.read().decode("utf-8"))

            google_access_token = token_resp.get("access_token")
            userinfo_req = urllib.request.Request(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {google_access_token}"},
                method="GET",
            )
            with urllib.request.urlopen(userinfo_req, timeout=10) as uresp:
                userinfo = json.loads(uresp.read().decode("utf-8"))

            email = str(userinfo.get("email") or "").strip().lower()
            name = str(userinfo.get("name") or "").strip()
        except Exception as exc:
            return HttpResponse(f"Google OAuth verification failed: {exc}", status=400)

        try:
            existing_profile = EntityProfile.objects.filter(email__iexact=email).first()
            resolved_phone = phone or (existing_profile.phone_e164 if existing_profile else "")

            token_pair = _complete_google_user_session(
                email=email,
                name=name,
                raw_phone=resolved_phone,
                requested_role=role,
                create_draft=(not portal_only),
            )
        except Exception as auth_exc:
            _ensure_identity_mysql_schema()
            try:
                existing_profile = EntityProfile.objects.filter(email__iexact=email).first()
                resolved_phone = phone or (existing_profile.phone_e164 if existing_profile else "")
                token_pair = _complete_google_user_session(
                    email=email,
                    name=name,
                    raw_phone=resolved_phone,
                    requested_role=role,
                    create_draft=(not portal_only),
                )
            except Exception as final_exc:
                return HttpResponse(
                    f"<!DOCTYPE html><html><body style='background:#062419;color:#fff;font-family:system-ui,sans-serif;padding:32px;text-align:center;'>"
                    f"<div style='background:#0c3527;border:1.5px solid #ef4444;border-radius:18px;padding:28px 24px;max-width:380px;margin:40px auto;'>"
                    f"<h3 style='color:#f87171;margin-top:0;'>Authentication Processing Error</h3>"
                    f"<p style='color:#fca5a5;font-size:13px;'>{final_exc}</p>"
                    f"<a href='/' style='display:inline-block;margin-top:16px;background:#10b981;color:#041c14;padding:10px 20px;border-radius:8px;font-weight:700;text-decoration:none;'>Return to AnnaSutra</a>"
                    f"</div></body></html>",
                    status=500,
                    content_type="text/html",
                )
        payload_json = json.dumps(token_pair)
        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Signed In — AnnaSutra</title>
  <style>
    body {{ background: #062419; color: #fff; font-family: system-ui, -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 24px; box-sizing: border-box; }}
    .card {{ background: #0c3527; border: 1.5px solid #10b981; border-radius: 18px; padding: 28px 24px; text-align: center; max-width: 360px; width: 100%; box-shadow: 0 20px 45px rgba(0,0,0,0.5); }}
    .check-icon {{ width: 52px; height: 52px; border-radius: 50%; background: #10b981; color: #041c14; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-size: 26px; font-weight: 900; }}
    h2 {{ margin: 0 0 8px; font-size: 19px; font-weight: 800; color: #ecfdf5; }}
    p {{ margin: 0 0 20px; font-size: 13px; color: #a7f3d0; line-height: 1.5; }}
    button {{ background: #10b981; color: #041c14; border: none; padding: 12px 20px; border-radius: 8px; font-weight: 800; font-size: 13.5px; cursor: pointer; width: 100%; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="check-icon">&#10003;</div>
    <h2>Signed In Successfully</h2>
    <p>{email}</p>
    <button onclick="closeNow()">Continue to AnnaSutra</button>
  </div>
  <script>
    const data = {payload_json};
    const token = data.access_token || data.access;
    if (token) localStorage.setItem('annasutra_access_token', token);
    if (data.user && data.user.email) localStorage.setItem('annasutra_email', data.user.email);
    if (data.user && data.user.phone) localStorage.setItem('annasutra_phone', data.user.phone);
    if (data.user && data.user.farmer_uid) localStorage.setItem('annasutra_farmer_uid', data.user.farmer_uid);
    localStorage.setItem('annasutra_role', '{role}');
    localStorage.setItem('annasutra_google_oauth_event', JSON.stringify({{ ts: Date.now(), data: data, role: '{role}' }}));

    function notifyOpener() {{
      if (window.opener && !window.opener.closed) {{
        try {{
          window.opener.postMessage({{ type: 'ANNASUTRA_GOOGLE_AUTH_SUCCESS', data: data, role: '{role}' }}, window.location.origin);
        }} catch(e) {{}}
      }}
    }}

    function closeNow() {{
      notifyOpener();
      try {{ window.close(); }} catch(e) {{}}
      setTimeout(() => {{
        if (!window.opener && window.name !== 'AnnaSutraGoogleOAuth') {{
          window.location.href = '/?google_auth=1';
        }}
      }}, 300);
    }}

    notifyOpener();
    try {{ window.close(); }} catch(e) {{}}
    setTimeout(closeNow, 300);
  </script>
</body>
</html>"""
        return HttpResponse(html, content_type="text/html")


class GoogleAuthView(APIView):
    """Sign in or register via Google OAuth 2.0 token or verified identity payload."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        from django.conf import settings

        email = str(request.data.get("email") or "").strip().lower()
        name = str(request.data.get("name") or request.data.get("full_name") or "").strip()
        raw_phone = str(request.data.get("phone") or request.data.get("phone_e164") or "").strip()
        requested_role = str(request.data.get("role") or "PRODUCER").strip().upper()
        create_draft = request.data.get("create_draft", True)
        id_token = request.data.get("id_token") or request.data.get("credential")
        google_oauth_token = request.data.get("google_oauth_token")

        if google_oauth_token:
            try:
                verified = jwt.decode(google_oauth_token, settings.SECRET_KEY, algorithms=["HS256"])
                email = str(verified.get("email") or "").strip().lower()
                name = str(verified.get("name") or name).strip()
                requested_role = str(verified.get("role") or requested_role).strip().upper()
            except Exception as exc:
                raise exceptions.AuthenticationFailed(
                    {"detail": "Expired or invalid Google OAuth session.", "code": "INVALID_OAUTH_TOKEN"}
                ) from exc

        if id_token and not email:
            try:
                claims = jwt.decode(id_token, options={"verify_signature": False})
                email = str(claims.get("email") or "").strip().lower()
                if not name:
                    name = str(claims.get("name") or "").strip()
            except Exception:
                pass

        if not email or "@" not in email:
            raise exceptions.ValidationError(
                {"detail": "A valid Google email address is required.", "code": "INVALID_EMAIL"}
            )

        token_pair = _complete_google_user_session(
            email=email,
            name=name,
            raw_phone=raw_phone,
            requested_role=requested_role,
            create_draft=bool(create_draft),
        )
        return Response(token_pair, status=status.HTTP_200_OK)
