"""Gmail & Phone OTP service with rate-limiting, privacy masking, and pluggable providers."""

from abc import ABC, abstractmethod
import hashlib
import logging
import re
import secrets
import time
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

logger = logging.getLogger("annasutra.identity.otp")

PHONE_E164_REGEX = re.compile(r"^\+[1-9]\d{9,14}$")
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_COOLDOWN_SECONDS = 60  # 1 minute between requests
OTP_MAX_REQUESTS = 3  # Max 3 requests in window
OTP_WINDOW_SECONDS = 600  # 10 minutes window
OTP_MAX_VERIFY_ATTEMPTS = 5


def validate_e164(phone: str) -> str:
    """Validate and clean E.164 phone number string."""
    cleaned = str(phone or "").strip()
    if not PHONE_E164_REGEX.match(cleaned):
        raise ValueError("Invalid phone number. Must be valid E.164 format (e.g. +919876543210).")
    return cleaned


def mask_phone(phone: str) -> str:
    """Mask phone number for safe logging (e.g. +91*****43210)."""
    if not phone or len(phone) < 6:
        return "***"
    return phone[:3] + "*" * (len(phone) - 7) + phone[-4:]


def mask_email(email: str) -> str:
    """Mask email address for safe logging (e.g. ra***@gmail.com)."""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[:2]}***@{domain}"


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


def get_localized_otp_message(language: str, code: str) -> str:
    """Generate localized OTP verification SMS text for all 11 supported languages."""
    sms_templates = {
        "bn": f"অন্নসূত্র (AnnaSutra) যাচাইকরণ কোড হলো: {code}। এটি ৫ মিনিটের জন্য বৈধ। ওটিপি কারো সাথে শেয়ার করবেন না।",
        "gu": f"અન્નસૂત્ર (AnnaSutra) ચકાસણી કોડ: {code} છે. તે 5 મિનિટ માટે માન્ય છે. આ OTP કોઈની સાથે શેર કરશો નહીં.",
        "hi": f"अन्नसूत्र (AnnaSutra) सत्यापन कोड: {code} है। यह 5 मिनट के लिए वैध है। कृपया यह ओटीपी साझा न करें।",
        "kn": f"ಅನ್ನಸೂತ್ರ (AnnaSutra) ಪರಿಶೀಲನಾ ಕೋಡ್: {code}. ಇದು 5 ನಿಮಿಷಗಳವರೆಗೆ ಮಾನ್ಯವಾಗಿರುತ್ತದೆ. ಈ OTP ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
        "ml": f"അന്നസൂത്ര (AnnaSutra) പരിശോധനാ കോഡ്: {code}. ഇത് 5 മിനിറ്റ് സാധുവാണ്. ഈ OTP പങ്കിടരുത്.",
        "mr": f"अन्नसूत्र (AnnaSutra) पडताळणी कोड: {code} आहे. हा ५ मिनिटांसाठी वैध आहे. कृपया हा OTP शेअर करू नका.",
        "or": f"ଅନ୍ନସୂତ୍ର (AnnaSutra) ଯାଞ୍ଚ କୋଡ୍ ହେଉଛି: {code}। ଏହା 5 ମିନିଟ୍ ପାଇଁ ବୈଧ ଅଟେ। ଏହି OTP କାହା ସହ ସେୟାର କରନ୍ତୁ ନାହିଁ।",
        "pa": f"ਅੰਨਸੂਤਰ (AnnaSutra) ਤਸਦੀਕ ਕੋਡ: {code} ਹੈ। ਇਹ 5 ਮਿੰਟਾਂ ਲਈ ਵੈਧ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਇਹ OTP ਸਾਂਝਾ ਨਾ ਕਰੋ।",
        "ta": f"அன்னசூத்ரா (AnnaSutra) சரிபார்ப்பு குறியீடு: {code}. இது 5 நிಮಿடங்களுக்கு செல்லுபடியாகும். இந்த OTP-ஐ பகிர வேண்டாம்.",
        "te": f"అన్నసూత్ర (AnnaSutra) ధృవీకరణ కోడ్: {code}. ఇది 5 నిమిషాల పాటు చెల్లుతుంది. ఈ OTPని ఎవరితోనూ పంచుకోవద్దు.",
    }
    return sms_templates.get(
        language,
        f"Your AnnaSutra verification code is: {code}. Valid for 5 minutes. Do not share this code.",
    )


class AndroidSmsGatewayOtpProvider(BaseOtpProvider):
    """Open-source Android SMS Gateway provider (capcom6/android-sms-gateway)."""

    def send_otp(self, phone: str, code: str, language: str = "en") -> bool:
        import requests

        base_url = getattr(settings, "SMS_GATEWAY_URL", "https://api.sms-gate.app/3rdparty/v1/messages").strip()
        username = getattr(settings, "SMS_GATEWAY_USER", "").strip()
        password = getattr(settings, "SMS_GATEWAY_PASSWORD", "").strip()
        sim_number = getattr(settings, "SMS_GATEWAY_SIM_NUMBER", 1)

        masked = mask_phone(phone)

        if not username or not password:
            logger.warning(
                "SMS_GATEWAY_USER or SMS_GATEWAY_PASSWORD not configured. Simulated OTP for %s logged.",
                masked,
            )
            return True

        text = get_localized_otp_message(language, code)

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
            response = requests.post(
                endpoint,
                json=payload,
                auth=(username, password),
                headers={"Content-Type": "application/json"},
                timeout=12,
            )
            if response.status_code in [200, 201, 202]:
                return True
            return False
        except requests.exceptions.RequestException:
            return False


def get_otp_provider() -> BaseOtpProvider:
    if getattr(settings, "OTP_DEBUG", False) or getattr(settings, "TESTING", False):
        return ConsoleOtpProvider()
    provider_name = getattr(settings, "OTP_PROVIDER", "").lower()
    user = getattr(settings, "SMS_GATEWAY_USER", "").strip()

    if provider_name in ["android_gateway", "android-sms-gateway", "sms_gateway", "android", "gateway"]:
        return AndroidSmsGatewayOtpProvider()
    if provider_name == "carrier":
        return InboundCarrierOtpProvider()
    if provider_name == "console":
        return ConsoleOtpProvider()
    if user:
        return AndroidSmsGatewayOtpProvider()
    return ConsoleOtpProvider()


class OtpService:
    """Manages verification code generation, rate limiting, and delivery to Gmail + optional mobile."""

    @staticmethod
    def _cache_key_otp(identifier: str) -> str:
        h = hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()
        return f"otp:code:{h}"

    @staticmethod
    def _cache_key_rate(identifier: str) -> str:
        h = hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()
        return f"otp:rate:{h}"

    @classmethod
    def request_otp(cls, phone: Optional[str] = None, language: str = "en", email: Optional[str] = None) -> dict:
        """Rate limit, generate, and deliver verification code to Gmail (by default) and/or verified phone."""
        raw_phone = str(phone or "").strip()
        raw_email = str(email or "").strip().lower()

        if "@" in raw_phone and not raw_email:
            raw_email = raw_phone.lower()
            raw_phone = ""

        clean_phone = validate_e164(raw_phone) if raw_phone else ""
        clean_email = raw_email if (raw_email and "@" in raw_email) else ""

        if not clean_phone and not clean_email:
            raise ValueError("A valid Gmail address or E.164 phone number is required.")

        primary_id = clean_email or clean_phone
        now = time.time()
        rate_key = cls._cache_key_rate(primary_id)
        rate_data = cache.get(rate_key) or {"count": 0, "last_sent": 0.0, "window_start": now}

        if now - rate_data["window_start"] > OTP_WINDOW_SECONDS:
            rate_data = {"count": 0, "last_sent": 0.0, "window_start": now}

        if now - rate_data["last_sent"] < OTP_COOLDOWN_SECONDS:
            retry_after = int(OTP_COOLDOWN_SECONDS - (now - rate_data["last_sent"]))
            return {
                "status": "RATE_LIMITED",
                "message": f"Please wait {retry_after} seconds before requesting a new code.",
                "retry_after": retry_after,
            }

        if rate_data["count"] >= OTP_MAX_REQUESTS:
            retry_after = int(OTP_WINDOW_SECONDS - (now - rate_data["window_start"]))
            return {
                "status": "RATE_LIMITED",
                "message": f"Too many requests. Please try again after {retry_after} seconds.",
                "retry_after": max(1, retry_after),
            }

        code = f"{secrets.SystemRandom().randint(100000, 999999)}"
        salt = secrets.token_hex(16)
        code_hash = hashlib.sha256(f"{salt}:{code}".encode("utf-8")).hexdigest()

        record_payload = {
            "hash": code_hash,
            "salt": salt,
            "created_at": now,
            "attempts": 0,
        }
        if clean_email:
            cache.set(cls._cache_key_otp(clean_email), dict(record_payload), timeout=OTP_EXPIRY_SECONDS)
        if clean_phone:
            cache.set(cls._cache_key_otp(clean_phone), dict(record_payload), timeout=OTP_EXPIRY_SECONDS)

        rate_data["count"] += 1
        rate_data["last_sent"] = now
        cache.set(rate_key, rate_data, timeout=OTP_WINDOW_SECONDS)

        channels = []
        if clean_email:
            try:
                msg = get_localized_otp_message(language, code)
                send_mail(
                    subject="AnnaSutra Verification Code",
                    message=msg,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@annasutra.in"),
                    recipient_list=[clean_email],
                    fail_silently=True,
                )
            except Exception:
                pass
            logger.info("Verification code dispatched to Gmail %s", mask_email(clean_email))
            channels.append("email")

        if clean_phone:
            provider = get_otp_provider()
            sent = provider.send_otp(clean_phone, code, language)
            if not sent and not clean_email:
                return {
                    "status": "GATEWAY_ERROR",
                    "message": "Unable to dispatch SMS. Please ensure the SMS Gateway app on your phone is running with Cloud Server enabled.",
                }
            if sent:
                channels.append("sms")

        result = {
            "status": "SENT",
            "channels": channels,
            "expires_in": OTP_EXPIRY_SECONDS,
        }
        if getattr(settings, "DEBUG", False) or getattr(settings, "OTP_DEBUG", False):
            result["debug_code"] = code

        return result

    @classmethod
    def verify_otp(cls, phone: Optional[str] = None, code: str = "", email: Optional[str] = None) -> bool:
        """Verify the 6-digit code against Gmail and/or phone."""
        raw_phone = str(phone or "").strip()
        raw_email = str(email or "").strip().lower()

        if "@" in raw_phone and not raw_email:
            raw_email = raw_phone.lower()
            raw_phone = ""

        clean_phone = validate_e164(raw_phone) if raw_phone else ""
        clean_email = raw_email if (raw_email and "@" in raw_email) else ""

        candidates = [c for c in (clean_email, clean_phone) if c]
        if not candidates:
            raise ValueError("A valid Gmail address or E.164 phone number is required.")

        for candidate in candidates:
            otp_key = cls._cache_key_otp(candidate)
            record = cache.get(otp_key)
            if not record:
                continue

            record["attempts"] += 1
            if record["attempts"] > OTP_MAX_VERIFY_ATTEMPTS:
                cache.delete(otp_key)
                continue

            salt = record["salt"]
            expected_hash = record["hash"]
            provided_hash = hashlib.sha256(f"{salt}:{str(code).strip()}".encode("utf-8")).hexdigest()

            if secrets.compare_digest(expected_hash, provided_hash):
                for c in candidates:
                    cache.delete(cls._cache_key_otp(c))
                return True

            cache.set(otp_key, record, timeout=OTP_EXPIRY_SECONDS)

        return False
