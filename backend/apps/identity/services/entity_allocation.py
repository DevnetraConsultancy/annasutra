"""AnnaSutra Entity Allocation & Verification Services.
Handles atomic entity code generation, 26-digit Unique Role ID minting with
10-digit Identity Segment (verified mobile or system serial), Crockford Base32
13-char QR generation, approval transaction, and block issuance.
"""

import re
import secrets
import uuid
from typing import Optional, Tuple

from django.db import transaction
from django.utils import timezone

from apps.identity.models import (
    AppUser,
    EntityProfile,
    EntityRoleDetails,
    VerificationReview,
)
from apps.labels.models import QrBlock, QrLabel
from apps.organisations.models import Organisation

# Crockford Base32 alphabet (omits I, L, O, U to prevent visual confusion and accidental profanity)
CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

ROLE_PREFIX_MAP = {
    "PRODUCER": "PR",
    "AGGREGATOR": "AG",
    "PROCESSOR": "PC",
    "WHOLESALER": "WH",
    "DISTRIBUTOR": "DI",
    "RETAILER": "RE",
}

# Standard 2-letter state abbreviations for Indian states and union territories
STATE_CODE_MAP = {
    "ANDAMAN AND NICOBAR": "AN",
    "ANDHRA PRADESH": "AP",
    "ARUNACHAL PRADESH": "AR",
    "ASSAM": "AS",
    "BIHAR": "BR",
    "CHANDIGARH": "CH",
    "CHHATTISGARH": "CG",
    "DADRA AND NAGAR HAVELI": "DH",
    "DAMAN AND DIU": "DD",
    "DELHI": "DL",
    "GOA": "GA",
    "GUJARAT": "GJ",
    "HARYANA": "HR",
    "HIMACHAL PRADESH": "HP",
    "JAMMU AND KASHMIR": "JK",
    "JHARKHAND": "JH",
    "KARNATAKA": "KA",
    "KERALA": "KL",
    "LADAKH": "LA",
    "LAKSHADWEEP": "LD",
    "MADHYA PRADESH": "MP",
    "MAHARASHTRA": "MH",
    "MANIPUR": "MN",
    "MEGHALAYA": "ML",
    "MIZORAM": "MZ",
    "NAGALAND": "NL",
    "ODISHA": "OD",
    "PUDUCHERRY": "PY",
    "PUNJAB": "PB",
    "RAJASTHAN": "RJ",
    "SIKKIM": "SK",
    "TAMIL NADU": "TN",
    "TELANGANA": "TS",
    "TRIPURA": "TR",
    "UTTAR PRADESH": "UP",
    "UTTARAKHAND": "UK",
    "WEST BENGAL": "WB",
}

# Default initial QR block label counts per role
DEFAULT_QR_BLOCK_SIZES = {
    "PRODUCER": 50,
    "AGGREGATOR": 20,
    "PROCESSOR": 20,
    "WHOLESALER": 20,
    "DISTRIBUTOR": 20,
    "RETAILER": 20,
}


def normalize_state_code(state_str: str) -> str:
    """Normalize a state string to its standard 2-letter uppercase code."""
    if not state_str:
        return "IN"
    cleaned = state_str.strip().upper()
    if len(cleaned) == 2 and cleaned.isalpha():
        return cleaned
    if cleaned in STATE_CODE_MAP:
        return STATE_CODE_MAP[cleaned]
    for name, code in STATE_CODE_MAP.items():
        if name in cleaned or cleaned in name:
            return code
    alpha = "".join(c for c in cleaned if c.isalpha())
    return (alpha[:2] if len(alpha) >= 2 else "IN").upper()


def compute_crockford_checksum(raw12: str) -> str:
    """Compute weighted modulo-32 check character for Crockford Base32 chars."""
    weights = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    total = sum(CROCKFORD_ALPHABET.index(c) * weights[i % len(weights)] for i, c in enumerate(raw12))
    return CROCKFORD_ALPHABET[total % 32]


def verify_crockford_13(serial: str) -> bool:
    """Verify that a serial is a valid 13-char Crockford Base32 string with correct checksum."""
    if not serial or len(serial) != 13:
        return False
    clean = serial.upper()
    if any(c not in CROCKFORD_ALPHABET for c in clean):
        return False
    raw12 = clean[:12]
    expected_check = compute_crockford_checksum(raw12)
    return clean[12] == expected_check


def generate_crockford_13() -> str:
    """Generate a single 13-character Crockford Base32 serial code (12 random + 1 check)."""
    raw12 = "".join(secrets.choice(CROCKFORD_ALPHABET) for _ in range(12))
    check = compute_crockford_checksum(raw12)
    return raw12 + check


def format_serial_display(serial: str) -> str:
    """Format 13-char serial for human printing, e.g. 'XXXX-XXXX-XXXX-X'."""
    clean = serial.upper().replace("-", "")
    if len(clean) == 13:
        return f"{clean[0:4]}-{clean[4:8]}-{clean[8:12]}-{clean[12]}"
    elif len(clean) == 12:
        return f"{clean[0:4]}-{clean[4:8]}-{clean[8:12]}"
    return serial


def generate_entity_code(role: str, state: str) -> str:
    """Generate the next sequential unique entity code: {ROLE}-{STATE}-{SEQ6}.
    Example: PR-WB-000101.
    Must be called inside an atomic transaction.
    """
    role_prefix = ROLE_PREFIX_MAP.get(role.upper(), "PR")
    state_code = normalize_state_code(state)
    prefix = f"{role_prefix}-{state_code}-"

    existing_codes = EntityProfile.objects.filter(
        entity_code__startswith=prefix
    ).values_list("entity_code", flat=True)

    max_seq = 100
    seq_pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    for code in existing_codes:
        if code:
            m = seq_pattern.match(code)
            if m:
                try:
                    val = int(m.group(1))
                    if val > max_seq:
                        max_seq = val
                except ValueError:
                    pass

    next_seq = max_seq + 1
    return f"{prefix}{next_seq:06d}"


def extract_10_digit_mobile(phone_raw: Optional[str]) -> Optional[str]:
    """Extract a valid 10-digit mobile number from phone_e164 if present."""
    if not phone_raw:
        return None
    digits = re.sub(r"\D", "", str(phone_raw))
    if not digits or set(digits) == {"0"} or digits == "910000000000":
        return None
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) > 10:
        digits = digits[-10:]
    if len(digits) == 10 and digits != "0000000000":
        return digits
    return None


def mint_system_identity_segment(seed_uuid=None) -> str:
    """Issue a unique 10-digit system serial (000000xxxx) when no mobile is present at approval.
    Starts with 000000 so it never collides with a 10-digit mobile number.
    """
    used_segments = set()
    for rd in EntityRoleDetails.objects.all():
        if isinstance(rd.details, dict):
            seg = rd.details.get("identity_segment")
            if seg:
                used_segments.add(str(seg))
            uid = rd.details.get("farmer_uid") or rd.details.get("role_uid")
            if uid and len(str(uid)) >= 10:
                used_segments.add(str(uid)[-10:])

    # Deterministic candidate from seed_uuid or sequential fallback starting at 0000001001
    if seed_uuid:
        num = (int(uuid.UUID(str(seed_uuid)).int) % 8999) + 1001
        candidate = f"000000{num:04d}"
        if candidate not in used_segments:
            return candidate

    seq = 1001
    while True:
        candidate = f"000000{seq:04d}"
        if candidate not in used_segments:
            return candidate
        seq += 1


def resolve_identity_segment(profile_or_user) -> str:
    """Resolve the frozen 10-digit Identity Segment for a profile or user (Decision 29)."""
    if profile_or_user is None:
        return "0000001001"

    profile = None
    user = None
    if isinstance(profile_or_user, EntityProfile):
        profile = profile_or_user
    elif isinstance(profile_or_user, AppUser):
        user = profile_or_user
        profile = EntityProfile.objects.filter(user_id=user.user_id).order_by("-verified_at", "-created_at").first()

    if profile:
        role_det = EntityRoleDetails.objects.filter(entity=profile).first()
        if role_det and isinstance(role_det.details, dict):
            existing_seg = role_det.details.get("identity_segment")
            if existing_seg and re.match(r"^\d{10}$", str(existing_seg)):
                return str(existing_seg)
            existing_uid = role_det.details.get("farmer_uid") or role_det.details.get("role_uid")
            if existing_uid and re.match(r"^\d{24,26}$", str(existing_uid)):
                return str(existing_uid)[-10:]

        mob = extract_10_digit_mobile(profile.phone_e164)
        if not mob:
            u = user or AppUser.objects.filter(user_id=profile.user_id).first()
            if u:
                mob = extract_10_digit_mobile(u.phone_e164)
        if mob:
            return mob
        return mint_system_identity_segment(seed_uuid=profile.entity_id)

    if user:
        mob = extract_10_digit_mobile(user.phone_e164)
        if mob:
            return mob
        return mint_system_identity_segment(seed_uuid=user.user_id)

    return "0000001001"


def generate_farmer_uid(phone_e164: Optional[str] = None, dt=None, identity_segment: Optional[str] = None) -> str:
    """Generate deterministic 26-digit Unique Role / Farmer ID (Decisions 2 & 29):
    YYYYMMDDHHMMSS (14 digits) + 91 (2 digits) + IdentitySegment (10 digits) = 26 digits.
    Example: 20261028155226919876543210 or 20261028155226910000004817
    """
    ts_dt = dt or timezone.now()
    ts_part = ts_dt.strftime("%Y%m%d%H%M%S")
    seg = identity_segment or extract_10_digit_mobile(phone_e164) or mint_system_identity_segment()
    return f"{ts_part}91{seg}"


def get_or_mint_farmer_uid(profile_or_user, dt=None) -> str:
    """Return existing or newly minted 26-digit Unique Role ID (YYYYMMDDHHMMSS+91+IdentitySegment).
    CRITICAL POLICY (Rule 1, C4, Decision 29):
    Unapproved registrations (status != 'VERIFIED') MUST NOT receive a Unique Role/Farmer ID.
    Once minted at Admin approval, the 26-digit ID and its 10-digit Identity Segment are frozen forever.
    """
    if profile_or_user is None:
        return ""

    profile = None
    if isinstance(profile_or_user, EntityProfile):
        profile = profile_or_user
    elif isinstance(profile_or_user, AppUser):
        profile = EntityProfile.objects.filter(user_id=profile_or_user.user_id, status="VERIFIED").first()
        if not profile:
            profile = EntityProfile.objects.filter(user_id=profile_or_user.user_id).first()
        if not profile and profile_or_user.phone_e164:
            profile = EntityProfile.objects.filter(phone_e164=profile_or_user.phone_e164).first()

    if profile:
        if profile.status != "VERIFIED":
            return ""

        role_det = EntityRoleDetails.objects.filter(entity=profile).first()
        if role_det and isinstance(role_det.details, dict):
            existing = role_det.details.get("farmer_uid") or role_det.details.get("role_uid")
            if existing and re.match(r"^\d{26}$", str(existing)):
                return str(existing)

        seg = resolve_identity_segment(profile)
        created_at = getattr(profile, "verified_at", None) or getattr(profile, "created_at", None) or dt or timezone.now()
        uid = generate_farmer_uid(dt=created_at, identity_segment=seg)
        try:
            role_det, _ = EntityRoleDetails.objects.get_or_create(entity=profile, defaults={"details": {}})
            details = dict(role_det.details or {})
            details["farmer_uid"] = uid
            details["role_uid"] = uid
            details["identity_segment"] = seg
            role_det.details = details
            role_det.save(update_fields=["details"])
        except Exception:
            pass
        return uid

    if isinstance(profile_or_user, AppUser):
        user_org = getattr(profile_or_user, "org", None)
        if user_org and user_org.verification == "VERIFIED":
            seg = resolve_identity_segment(profile_or_user)
            created_at = getattr(profile_or_user, "created_at", None) or dt or timezone.now()
            return generate_farmer_uid(dt=created_at, identity_segment=seg)

    return ""


def issue_qr_block_for_entity(
    entity: EntityProfile,
    count: Optional[int] = None,
    admin_user: Optional[AppUser] = None,
) -> Tuple[QrBlock, list]:
    """Issue a new block of Crockford Base32 13-char QR labels for the entity."""
    if count is None:
        count = DEFAULT_QR_BLOCK_SIZES.get(entity.role, 20)
    count = max(1, min(count, 500))

    try:
        user = AppUser.objects.get(user_id=entity.user_id)
        org = user.org
    except AppUser.DoesNotExist:
        org, _ = Organisation.objects.get_or_create(
            org_id=entity.entity_id,
            defaults={
                "name": entity.organisation_name or f"{entity.first_name} {entity.last_name}",
                "org_type": "FARMER" if entity.role == "PRODUCER" else entity.role,
                "verification": "VERIFIED",
            },
        )
        user = None

    if admin_user is None:
        admin_user = AppUser.objects.filter(email="devnetraconsultancy@gmail.com").first() or AppUser.objects.filter(role__in=["OWNER", "STAFF"]).first()
        if admin_user is None:
            if user:
                admin_user = user
            else:
                admin_user = AppUser.objects.create(
                    user_id=uuid.uuid4(),
                    org=org,
                    email=entity.email or f"entity_{str(entity.entity_id)[:8]}@annasutra.local",
                    phone_e164=entity.phone_e164 or None,
                    role="OWNER",
                    status="ACTIVE",
                )

    serials = set()
    while len(serials) < count:
        s = generate_crockford_13()
        if not QrLabel.objects.filter(serial=s).exists():
            serials.add(s)

    serial_list = sorted(list(serials))

    with transaction.atomic():
        block = QrBlock.objects.create(
            block_id=uuid.uuid4(),
            issued_to_org=org,
            issued_by=admin_user,
            count=count,
        )
        labels_to_create = [
            QrLabel(
                serial=s,
                block=block,
                issued_to_org=org,
                status="ISSUED",
            )
            for s in serial_list
        ]
        QrLabel.objects.bulk_create(labels_to_create)

    return block, serial_list


def approve_entity_registration(
    entity: EntityProfile,
    admin_user: AppUser,
    qr_count: Optional[int] = None,
    review_notes: Optional[str] = None,
) -> dict:
    """Execute Section 9 atomic approval transaction:
    1. Assign unique sequential entity code {ROLE}-{STATE}-{SEQ6}
    2. Mint and freeze 26-digit Unique Role ID (YYYYMMDDHHMMSS + 91 + IdentitySegment(10))
    3. Transition entity status to VERIFIED
    4. Transition linked organisation to VERIFIED
    5. Record immutable VerificationReview log
    6. Issue first QR block (default 50 for Producer, 20 for others)
    """
    if entity.status == "VERIFIED":
        uid = get_or_mint_farmer_uid(entity)
        return {
            "entity_id": str(entity.entity_id),
            "entity_code": entity.entity_code,
            "farmer_uid": uid,
            "role_uid": uid,
            "status": "VERIFIED",
            "already_verified": True,
        }

    with transaction.atomic():
        now = timezone.now()
        code = generate_entity_code(entity.role, entity.state)

        entity.entity_code = code
        entity.status = "VERIFIED"
        entity.verified_at = now
        entity.verified_by = admin_user.user_id
        entity.version += 1
        entity.save(update_fields=[
            "entity_code", "status", "verified_at", "verified_by", "version", "updated_at"
        ])

        try:
            user = AppUser.objects.get(user_id=entity.user_id)
            org = user.org
            if entity.organisation_name and entity.organisation_name.strip():
                org.name = entity.organisation_name.strip()
            org.verification = "VERIFIED"
            org.verified_at = now
            org.verified_by = str(admin_user.user_id)
            org.save(update_fields=["name", "verification", "verified_at", "verified_by"])
        except AppUser.DoesNotExist:
            pass

        VerificationReview.objects.create(
            review_id=uuid.uuid4(),
            entity=entity,
            reviewer_id=admin_user.user_id,
            decision="APPROVED",
            reason=review_notes or "Identity, plots, and DPDP consent verified by administration.",
            created_at=now,
        )

        block, serials = issue_qr_block_for_entity(
            entity=entity,
            count=qr_count,
            admin_user=admin_user,
        )

        role_uid_val = get_or_mint_farmer_uid(entity, dt=now)

    return {
        "entity_id": str(entity.entity_id),
        "entity_code": entity.entity_code,
        "farmer_uid": role_uid_val,
        "role_uid": role_uid_val,
        "status": "VERIFIED",
        "verified_at": entity.verified_at.isoformat(),
        "block_id": str(block.block_id),
        "qr_count": block.count,
        "sample_serials": serials[:5],
    }
