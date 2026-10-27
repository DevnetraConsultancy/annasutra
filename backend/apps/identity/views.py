"""Identity & Authentication API views conforming to api/openapi.yaml."""

import base64
import uuid

from django.db import transaction
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


class OtpRequestView(APIView):
    """Send an SMS OTP code to phone number."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            raise exceptions.ValidationError({"detail": "Phone number is required.", "code": "FIELD_REQUIRED"})

        language = request.data.get("language", "en")
        try:
            result = OtpService.request_otp(phone=phone, language=language)
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
                    "detail": result.get("message", "Failed to dispatch SMS through SMS gateway."),
                    "code": "GATEWAY_ERROR",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        resp_data = {"status": "accepted"}
        if "debug_code" in result:
            resp_data["debug_code"] = result["debug_code"]

        return Response(resp_data, status=status.HTTP_202_ACCEPTED)


class OtpVerifyView(APIView):
    """Verify OTP code, auto-enroll device key, and issue tokens."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("code")

        if not phone or not code:
            raise exceptions.ValidationError(
                {"detail": "Both phone and code are required.", "code": "FIELD_REQUIRED"}
            )

        try:
            is_valid = OtpService.verify_otp(phone=phone, code=code)
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
                user = AppUser.objects.select_related("org").filter(phone_e164=phone).first()
                if not user:
                    # Initial registration creates a pending organisation and sets user as OWNER
                    org = Organisation.objects.create(
                        name=f"Pending Business ({phone[-4:]})",
                        org_type="FARMER",
                        verification="PENDING",
                    )
                    user = AppUser.objects.create(
                        user_id=uuid.uuid4(),
                        org=org,
                        phone_e164=phone,
                        role="OWNER",
                        status="ACTIVE",
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

            profile = EntityProfile.objects.filter(user_id=user.user_id).first() or EntityProfile.objects.filter(phone_e164=user.phone_e164).first()
            farmer_uid = get_or_mint_farmer_uid(profile if profile else user)
            token_pair = TokenService.issue_token_pair(user)
            # Provide compatibility keys for both standard OAuth/JWT and OpenAPI clients
            token_pair["access"] = token_pair["access_token"]
            token_pair["refresh"] = token_pair["refresh_token"]
            token_pair["user"] = {
                "user_id": str(user.user_id),
                "phone": user.phone_e164,
                "role": user.role,
                "entity_role": profile.role if profile else "PRODUCER",
                "farmer_uid": farmer_uid,
                "status": user.status,
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


class GoogleAuthView(APIView):
    """Sign in or register via Google Sign-In with mobile number linking for deterministic Farmer ID."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        import re

        email = str(request.data.get("email") or "").strip().lower()
        name = str(request.data.get("name") or request.data.get("full_name") or "").strip()
        raw_phone = str(request.data.get("phone") or request.data.get("phone_e164") or "").strip()
        requested_role = str(request.data.get("role") or "PRODUCER").strip().upper()
        id_token = request.data.get("id_token")

        # If a Google id_token JWT is provided, extract email/name claims safely
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

        valid_roles = {"PRODUCER", "AGGREGATOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"}
        if requested_role not in valid_roles:
            requested_role = "PRODUCER"

        # Normalize phone if provided
        phone_e164 = ""
        if raw_phone:
            digits = re.sub(r"\D", "", raw_phone)
            if len(digits) == 10:
                phone_e164 = f"+91{digits}"
            elif len(digits) >= 11:
                phone_e164 = f"+{digits}"

        with transaction.atomic():
            # Check if an EntityProfile with this email already exists
            profile = EntityProfile.objects.filter(email__iexact=email).first()
            if profile and not phone_e164:
                phone_e164 = profile.phone_e164

            if not phone_e164:
                raise exceptions.ValidationError(
                    {
                        "detail": "Please provide your mobile number (+91...) to generate your Unique Farmer ID (YYYYDDHHMMSS+CountryCodeMobileNumber).",
                        "code": "PHONE_REQUIRED_FOR_UID",
                    }
                )

            user = AppUser.objects.select_related("org").filter(phone_e164=phone_e164).first()
            if not user and profile:
                user = AppUser.objects.select_related("org").filter(user_id=profile.user_id).first()

            if not user:
                org_type_map = {
                    "PRODUCER": "FARMER",
                    "AGGREGATOR": "AGGREGATOR",
                    "WHOLESALER": "WHOLESALER",
                    "DISTRIBUTOR": "DISTRIBUTOR",
                    "RETAILER": "RETAILER",
                }
                org = Organisation.objects.create(
                    name=name or f"Business ({phone_e164[-4:]})",
                    org_type=org_type_map.get(requested_role, "FARMER"),
                    verification="PENDING",
                )
                user = AppUser.objects.create(
                    user_id=uuid.uuid4(),
                    org=org,
                    phone_e164=phone_e164,
                    role="OWNER",
                    status="ACTIVE",
                )

            if not profile:
                profile = EntityProfile.objects.filter(
                    user_id=user.user_id
                ).first() or EntityProfile.objects.filter(phone_e164=phone_e164).first()

            parts = name.split(None, 1) if name else []
            first_name = parts[0] if parts else ""
            last_name = parts[1] if len(parts) > 1 else ""

            if not profile:
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
            else:
                updated_fields = []
                if not profile.email:
                    profile.email = email
                    updated_fields.append("email")
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

            farmer_uid = get_or_mint_farmer_uid(profile)
            token_pair = TokenService.issue_token_pair(user)
            token_pair["authenticated"] = True
            token_pair["auth_provider"] = "GOOGLE"
            token_pair["farmer_uid"] = farmer_uid
            token_pair["access"] = token_pair["access_token"]
            token_pair["refresh"] = token_pair["refresh_token"]
            token_pair["user"] = {
                "user_id": str(user.user_id),
                "phone": user.phone_e164,
                "email": profile.email,
                "name": f"{profile.first_name} {profile.last_name}".strip() or name,
                "role": user.role,
                "entity_role": profile.role,
                "farmer_uid": farmer_uid,
                "status": user.status,
                "auth_provider": "google",
            }

        return Response(token_pair, status=status.HTTP_200_OK)

