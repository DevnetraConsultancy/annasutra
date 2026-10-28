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


def _complete_google_user_session(email: str, name: str, raw_phone: str, requested_role: str):
    """Create or link AppUser + EntityProfile for a verified Google account and issue JWT pair."""
    import re

    valid_roles = {"PRODUCER", "AGGREGATOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"}
    if requested_role not in valid_roles:
        requested_role = "PRODUCER"

    phone_e164 = ""
    if raw_phone:
        digits = re.sub(r"\D", "", raw_phone)
        if len(digits) == 10:
            phone_e164 = f"+91{digits}"
        elif len(digits) >= 11:
            phone_e164 = f"+{digits}"

    with transaction.atomic():
        profile = EntityProfile.objects.filter(email__iexact=email).first()
        if profile and not phone_e164:
            phone_e164 = profile.phone_e164

        if not phone_e164:
            raise exceptions.ValidationError(
                {
                    "detail": "Please provide your mobile number (+91...) to link your account.",
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
    """Handle Google OAuth 2.0 Authorization Code callback."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        import json
        import time
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
        if state_token:
            try:
                state_data = jwt.decode(state_token, settings.SECRET_KEY, algorithms=["HS256"])
                role = str(state_data.get("role") or "PRODUCER").strip().upper()
                phone = str(state_data.get("phone") or "").strip()
            except Exception:
                pass

        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "").strip()
        client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "").strip()
        redirect_uri = _resolve_google_redirect_uri(request)

        try:
            token_Payload = urllib.parse.urlencode(
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
                data=token_Payload,
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

        existing_profile = EntityProfile.objects.filter(email__iexact=email).first()
        resolved_phone = phone or (existing_profile.phone_e164 if existing_profile else "")

        if resolved_phone:
            token_pair = _complete_google_user_session(email, name, resolved_phone, role)
            payload_json = json.dumps(token_pair)
            html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Signed In — AnnaSutra</title></head>
<body style="background:#07271d;color:#fff;font-family:system-ui;display:flex;align-items:center;justify-content:center;height:90vh;">
<script>
  const data = {payload_json};
  const token = data.access_token || data.access;
  if (token) localStorage.setItem('annasutra_access_token', token);
  if (data.user && data.user.phone) localStorage.setItem('annasutra_phone', data.user.phone);
  if (data.user && data.user.farmer_uid) localStorage.setItem('annasutra_farmer_uid', data.user.farmer_uid);
  localStorage.setItem('annasutra_role', '{role}');
  localStorage.setItem('annasutra_google_oauth_event', JSON.stringify({{ ts: Date.now(), data: data, role: '{role}' }}));
  if (window.opener && !window.opener.closed) {{
    try {{ window.opener.postMessage({{ type: 'ANNASUTRA_GOOGLE_AUTH_SUCCESS', data: data, role: '{role}' }}, window.location.origin); }} catch(e) {{}}
    window.close();
  }} else {{
    window.location.href = '/?google_auth=1';
  }}
</script>
<p>Completing Google Sign-In...</p>
</body></html>"""
            return HttpResponse(html, content_type="text/html")

        # First-time Google user: ask once for mobile number to link their account
        signed_google_token = jwt.encode(
            {
                "email": email,
                "name": name,
                "role": role,
                "exp": int(time.time()) + 600,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Link Mobile Number — AnnaSutra</title>
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #07271d; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; min-height: 92vh; }}
    .card {{ background: #fff; max-width: 420px; width: 100%; border-radius: 18px; padding: 26px; box-shadow: 0 20px 50px rgba(0,0,0,0.45); }}
    .badge {{ background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; padding: 8px 12px; border-radius: 10px; font-size: 12.5px; font-weight: 700; margin-bottom: 16px; }}
    h3 {{ margin: 0 0 6px; color: #0b3d2e; font-size: 19px; }}
    p {{ margin: 0 0 16px; color: #475569; font-size: 13px; line-height: 1.45; }}
    label {{ display: block; font-size: 11.5px; font-weight: 800; color: #334155; margin-bottom: 6px; text-transform: uppercase; }}
    input {{ width: 100%; box-sizing: border-box; padding: 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 15px; font-weight: 600; margin-bottom: 14px; }}
    button {{ width: 100%; background: #0b3d2e; color: #fff; border: none; padding: 13px; border-radius: 8px; font-weight: 800; font-size: 14px; cursor: pointer; }}
    .err {{ color: #dc2626; font-size: 12.5px; margin-bottom: 10px; display: none; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">&#10003; Verified by Google: {email}</div>
    <h3>Link Your Mobile Number</h3>
    <p>Welcome, <strong>{name or email}</strong>. Please enter your 10-digit mobile number once to complete your AnnaSutra registration.</p>
    <div id="errBox" class="err"></div>
    <label>Mobile Number *</label>
    <input type="tel" id="phoneInput" placeholder="+91 9876543210" maxlength="15" autofocus />
    <button id="submitBtn" onclick="finishSignup()">Complete Registration &amp; Enter Console</button>
  </div>
  <script>
    async function finishSignup() {{
      const phone = document.getElementById('phoneInput').value.trim();
      const errBox = document.getElementById('errBox');
      const btn = document.getElementById('submitBtn');
      if (phone.replace(/\\D/g, '').length < 10) {{
        errBox.style.display = 'block';
        errBox.textContent = 'Please enter a valid 10-digit mobile number.';
        return;
      }}
      btn.disabled = true;
      btn.textContent = 'Completing Sign-In...';
      try {{
        const res = await fetch('/api/v1/auth/google', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            google_oauth_token: '{signed_google_token}',
            phone: phone,
            role: '{role}'
          }})
        }});
        const data = await res.json();
        if (!res.ok) {{
          errBox.style.display = 'block';
          errBox.textContent = data.detail || 'Could not complete registration.';
          btn.disabled = false;
          btn.textContent = 'Complete Registration & Enter Console';
          return;
        }}
        const token = data.access_token || data.access;
        if (token) localStorage.setItem('annasutra_access_token', token);
        if (data.user && data.user.phone) localStorage.setItem('annasutra_phone', data.user.phone);
        if (data.user && data.user.farmer_uid) localStorage.setItem('annasutra_farmer_uid', data.user.farmer_uid);
        localStorage.setItem('annasutra_role', '{role}');
        localStorage.setItem('annasutra_google_oauth_event', JSON.stringify({{ ts: Date.now(), data: data, role: '{role}' }}));
        if (window.opener && !window.opener.closed) {{
          try {{ window.opener.postMessage({{ type: 'ANNASUTRA_GOOGLE_AUTH_SUCCESS', data: data, role: '{role}' }}, window.location.origin); }} catch(e) {{}}
          window.close();
        }} else {{
          window.location.href = '/?google_auth=1';
        }}
      }} catch (e) {{
        errBox.style.display = 'block';
        errBox.textContent = 'Network error. Please try again.';
        btn.disabled = false;
        btn.textContent = 'Complete Registration & Enter Console';
      }}
    }}
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

        token_pair = _complete_google_user_session(email, name, raw_phone, requested_role)
        return Response(token_pair, status=status.HTTP_200_OK)

