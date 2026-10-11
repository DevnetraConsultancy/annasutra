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
from .models import AppUser, Device
from .services.otp import OtpService
from .services.passkey import PasskeyService
from .services.token import TokenService


class OtpRequestView(APIView):
    """Send an SMS OTP code to phone number."""

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

        resp_data = {"status": "accepted"}
        if "debug_code" in result:
            resp_data["debug_code"] = result["debug_code"]

        return Response(resp_data, status=status.HTTP_202_ACCEPTED)


class OtpVerifyView(APIView):
    """Verify OTP code, auto-enroll device key, and issue tokens."""

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

        token_pair = TokenService.issue_token_pair(user)
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
