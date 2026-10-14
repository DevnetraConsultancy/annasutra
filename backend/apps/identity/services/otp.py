"""Phone OTP service with rate-limiting, privacy masking, and pluggable providers."""

from abc import ABC, abstractmethod
import hashlib
import logging
import re
import secrets
import time

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("annasutra.identity.otp")

PHONE_E164_REGEX = re.compile(r"^\+[1-9]\d{9,14}$")
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_COOLDOWN_SECONDS = 60  # 1 minute between requests
OTP_MAX_REQUESTS = 3  # Max 3 requests in window
OTP_WINDOW_SECONDS = 600  # 10 minutes window
OTP_MAX_VERIFY_ATTEMPTS = 5


def validate_e164(phone: str) -> str:
    """Validate and clean E.164 phone number string."""
    cleaned = phone.strip()
    if not PHONE_E164_REGEX.match(cleaned):
        raise ValueError("Invalid phone number. Must be valid E.164 format (e.g. +919876543210).")
    return cleaned


def mask_phone(phone: str) -> str:
    """Mask phone number for safe logging (e.g. +91*****43210)."""
    if len(phone) < 6:
        return "***"
    return phone[:3] + "*" * (len(phone) - 7) + phone[-4:]


class BaseOtpProvider(ABC):
    """Abstract SMS/OTP provider."""

    @abstractmethod
    def send_otp(self, phone: str, code: str, language: str = "en") -> bool:
        """Send OTP to recipient."""
        pass


class ConsoleOtpProvider(BaseOtpProvider):
    """Console/Dev/CI provider. Logs OTP and stores for testing."""

    def send_otp(self, phone: str, code: str, language: str = "en") -> bool:
        masked = mask_phone(phone)
        logger.info("OTP generated for %s (language: %s)", masked, language)
        return True


class InboundCarrierOtpProvider(BaseOtpProvider):
    """Carrier-based SMS verification provider."""

    def send_otp(self, phone: str, code: str, language: str = "en") -> bool:
        masked = mask_phone(phone)
        logger.info("Inbound carrier verification ready for %s", masked)
        return True


class AndroidSmsGatewayOtpProvider(BaseOtpProvider):
    """
    Open-source Android SMS Gateway provider (capcom6/android-sms-gateway).
    Supports Cloud Relay (https://api.sms-gate.app) and Local/Private server modes.
    """

    def send_otp(self, phone: str, code: str, language: str = "en") -> bool:
        import requests

        base_url = getattr(settings, "SMS_GATEWAY_URL", "https://api.sms-gate.app/3rdparty/v1/messages").strip()
        username = getattr(settings, "SMS_GATEWAY_USER", "").strip()
        password = getattr(settings, "SMS_GATEWAY_PASSWORD", "").strip()
        sim_number = getattr(settings, "SMS_GATEWAY_SIM_NUMBER", 1)

        masked = mask_phone(phone)

        # Fallback to simulated delivery if credentials not provided
        if not username or not password:
            logger.warning(
                "SMS_GATEWAY_USER or SMS_GATEWAY_PASSWORD not configured. Simulated OTP for %s logged.",
                masked,
            )
            logger.info("[SIMULATED SMS] To: %s | OTP: %s", masked, code)
            return True

        # Multilingual SMS templates
        if language == "hi":
            text = f"अन्नसूत्र (AnnaSutra) सत्यापन कोड: {code} है। यह 5 मिनट के लिए वैध है। कृपया यह ओटीपी साझा न करें।"
        elif language == "bn":
            text = f"অন্নসূত্র (AnnaSutra) যাচাইকরণ কোড হলো: {code}। এটি ৫ মিনিটের জন্য বৈধ। ওটিপি কারো সাথে শেয়ার করবেন না।"
        else:
            text = f"Your AnnaSutra verification code is: {code}. Valid for 5 minutes. Do not share this OTP."

        # Normalize endpoint URL
        endpoint = base_url
        if not (endpoint.endswith("/message") or endpoint.endswith("/messages")):
            if "3rdparty" in endpoint or "api.sms-gate.app" in endpoint:
                endpoint = f"{endpoint.rstrip('/')}/messages"
            elif endpoint.endswith(":8080") or "/message" not in endpoint:
                endpoint = f"{endpoint.rstrip('/')}/message"

        payload = {
            "phoneNumbers": [phone],
            "textMessage": {
                "text": text,
            },
        }
        if sim_number:
            try:
                payload["simNumber"] = int(sim_number)
            except (ValueError, TypeError):
                pass

        try:
            logger.info("Dispatching OTP via Android SMS Gateway to %s via %s", masked, endpoint)
            response = requests.post(
                endpoint,
                json=payload,
                auth=(username, password),
                headers={"Content-Type": "application/json"},
                timeout=12,
            )

            if response.status_code in [200, 201, 202]:
                data = response.json() if response.content else {}
                msg_id = data.get("id") or data.get("messageId") or "dispatched"
                logger.info("SMS OTP dispatched successfully to %s (Gateway ID: %s)", masked, msg_id)
                return True
            else:
                logger.error(
                    "SMS Gateway returned HTTP %d for recipient %s: %s",
                    response.status_code,
                    masked,
                    response.text[:200],
                )
                return False

        except requests.exceptions.RequestException as exc:
            logger.error("Failed to connect to Android SMS Gateway (%s): %s", endpoint, exc)
            return False


def get_otp_provider() -> BaseOtpProvider:
    provider_name = getattr(settings, "OTP_PROVIDER", "").lower()
    user = getattr(settings, "SMS_GATEWAY_USER", "").strip()

    if provider_name in ["android_gateway", "android-sms-gateway", "sms_gateway", "android", "gateway"]:
        return AndroidSmsGatewayOtpProvider()
    if provider_name == "carrier":
        return InboundCarrierOtpProvider()
    if provider_name == "console":
        return ConsoleOtpProvider()
    # If not explicitly forced to console/carrier, use gateway if credentials exist
    if user:
        return AndroidSmsGatewayOtpProvider()
    return ConsoleOtpProvider()




class OtpService:
    """Manages OTP generation, rate limiting, and verification."""

    @staticmethod
    def _cache_key_otp(phone: str) -> str:
        h = hashlib.sha256(phone.encode("utf-8")).hexdigest()
        return f"otp:code:{h}"

    @staticmethod
    def _cache_key_rate(phone: str) -> str:
        h = hashlib.sha256(phone.encode("utf-8")).hexdigest()
        return f"otp:rate:{h}"

    @classmethod
    def request_otp(cls, phone: str, language: str = "en") -> dict:
        """Rate limit, generate, and deliver OTP to phone."""
        phone = validate_e164(phone)
        now = time.time()
        rate_key = cls._cache_key_rate(phone)
        rate_data = cache.get(rate_key) or {"count": 0, "last_sent": 0.0, "window_start": now}

        # Check window reset
        if now - rate_data["window_start"] > OTP_WINDOW_SECONDS:
            rate_data = {"count": 0, "last_sent": 0.0, "window_start": now}

        # Cooldown check
        if now - rate_data["last_sent"] < OTP_COOLDOWN_SECONDS:
            retry_after = int(OTP_COOLDOWN_SECONDS - (now - rate_data["last_sent"]))
            return {
                "status": "RATE_LIMITED",
                "message": f"Please wait {retry_after} seconds before requesting a new code.",
                "retry_after": retry_after,
            }

        # Max requests check
        if rate_data["count"] >= OTP_MAX_REQUESTS:
            retry_after = int(OTP_WINDOW_SECONDS - (now - rate_data["window_start"]))
            return {
                "status": "RATE_LIMITED",
                "message": f"Too many requests. Please try again after {retry_after} seconds.",
                "retry_after": max(1, retry_after),
            }

        # Generate 6-digit numeric code
        code = f"{secrets.SystemRandom().randint(100000, 999999)}"
        salt = secrets.token_hex(16)
        code_hash = hashlib.sha256(f"{salt}:{code}".encode("utf-8")).hexdigest()

        # Save to cache
        otp_key = cls._cache_key_otp(phone)
        cache.set(
            otp_key,
            {
                "hash": code_hash,
                "salt": salt,
                "created_at": now,
                "attempts": 0,
            },
            timeout=OTP_EXPIRY_SECONDS,
        )

        # Update rate limit data
        rate_data["count"] += 1
        rate_data["last_sent"] = now
        cache.set(rate_key, rate_data, timeout=OTP_WINDOW_SECONDS)

        # Send via provider
        provider = get_otp_provider()
        provider.send_otp(phone, code, language)

        result = {
            "status": "SENT",
            "expires_in": OTP_EXPIRY_SECONDS,
        }
        # Include debug_code only in debug or test mode
        if getattr(settings, "DEBUG", False) or getattr(settings, "OTP_DEBUG", False):
            result["debug_code"] = code

        return result

    @classmethod
    def verify_otp(cls, phone: str, code: str) -> bool:
        """Verify the 6-digit code for phone."""
        phone = validate_e164(phone)
        otp_key = cls._cache_key_otp(phone)
        record = cache.get(otp_key)
        if not record:
            return False

        record["attempts"] += 1
        if record["attempts"] > OTP_MAX_VERIFY_ATTEMPTS:
            cache.delete(otp_key)
            return False

        salt = record["salt"]
        expected_hash = record["hash"]
        provided_hash = hashlib.sha256(f"{salt}:{code.strip()}".encode("utf-8")).hexdigest()

        if secrets.compare_digest(expected_hash, provided_hash):
            cache.delete(otp_key)
            return True

        cache.set(otp_key, record, timeout=OTP_EXPIRY_SECONDS)
        return False
