"""AnnaSutra Entity Allocation & Verification Services.
Handles atomic entity code generation, Crockford Base32 13-char QR generation,
approval transaction, and block issuance conforming to Handover Sections 9 & 11.
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
    VerificationReview,
)
from apps.labels.models import QrBlock, QrLabel
from apps.organisations.models import Organisation

# Crockford Base32 alphabet (omits I, L, O, U to prevent visual confusion and accidental profanity)
CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

ROLE_PREFIX_MAP = {
    "PRODUCER": "PR",
    "AGGREGATOR": "AG",
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
    # Check for substring match
    for name, code in STATE_CODE_MAP.items():
        if name in cleaned or cleaned in name:
            return code
    # Fallback to first two alphabetic characters
    alpha = "".join(c for c in cleaned if c.isalpha())
    return (alpha[:2] if len(alpha) >= 2 else "IN").upper()


def compute_crockford_checksum(raw12: str) -> str:
    """Compute weighted modulo-32 check character for 12 Crockford Base32 chars."""
    weights = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    total = sum(CROCKFORD_ALPHABET.index(c) * w for c, w in zip(raw12, weights))
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
    """Format 13-char serial for human printing, e.g. 'XXXX-XXXX-XXXX-X' or 'XXXX-XXXX-XXXX'."""
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

    # Query highest existing sequence with this prefix
    existing_codes = EntityProfile.objects.filter(
        entity_code__startswith=prefix
    ).values_list("entity_code", flat=True)

    max_seq = 100  # Start sequence at 101 per Handover examples
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


def generate_farmer_uid(phone_e164: str, dt=None) -> str:
    """Generate deterministic Farmer ID per mentor specification:
    YYYYDDHHMMSS + CountryCodeMobileNumber (e.g., 202627223015919876543210).
    """
    ts_dt = dt or timezone.now()
    ts_part = ts_dt.strftime("%Y%d%H%M%S")
    digits = re.sub(r"\D", "", str(phone_e164 or "910000000000"))
    if len(digits) == 10:
        digits = "91" + digits
    elif not digits:
        digits = "910000000000"
    return f"{ts_part}{digits}"


def get_or_mint_farmer_uid(profile_or_user, dt=None) -> str:
    """Return existing or newly minted YYYYDDHHMMSS+CountryCodeMobileNumber Farmer ID."""
    from apps.identity.models import EntityRoleDetails

    phone = getattr(profile_or_user, "phone_e164", "") or "910000000000"
    created_at = getattr(profile_or_user, "created_at", None) or dt or timezone.now()

    if isinstance(profile_or_user, EntityProfile):
        role_det = EntityRoleDetails.objects.filter(entity=profile_or_user).first()
        if role_det and isinstance(role_det.details, dict):
            existing = role_det.details.get("farmer_uid")
            if existing and re.match(r"^\d{20,30}$", str(existing)):
                return str(existing)
        uid = generate_farmer_uid(phone, created_at)
        try:
            role_det, _ = EntityRoleDetails.objects.get_or_create(entity=profile_or_user, defaults={"details": {}})
            details = dict(role_det.details or {})
            details["farmer_uid"] = uid
            role_det.details = details
            role_det.save(update_fields=["details"])
        except Exception:
            pass
        return uid

    return generate_farmer_uid(phone, created_at)



def issue_qr_block_for_entity(
    entity: EntityProfile,
    count: Optional[int] = None,
    admin_user: Optional[AppUser] = None,
) -> Tuple[QrBlock, list]:
    """Issue a new block of Crockford Base32 13-char QR labels for the entity."""
    if count is None:
        count = DEFAULT_QR_BLOCK_SIZES.get(entity.role, 20)
    count = max(1, min(count, 500))

    # Resolve issuing organisation and user
    try:
        user = AppUser.objects.get(user_id=entity.user_id)
        org = user.org
    except AppUser.DoesNotExist:
        # Fallback: check if an organisation with entity_id exists
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
        # Find any admin or fallback user
        admin_user = AppUser.objects.filter(role__in=["OWNER", "STAFF"]).first()
        if admin_user is None:
            if user:
                admin_user = user
            else:
                admin_user = AppUser.objects.create(
                    user_id=uuid.uuid4(),
                    org=org,
                    phone_e164=entity.phone_e164,
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
    2. Transition entity status to VERIFIED
    3. Transition linked organisation to VERIFIED
    4. Record immutable VerificationReview log
    5. Issue first QR block (default 50 for Producer, 20 for others)
    """
    if entity.status == "VERIFIED":
        return {
            "entity_id": str(entity.entity_id),
            "entity_code": entity.entity_code,
            "status": "VERIFIED",
            "already_verified": True,
        }

    with transaction.atomic():
        now = timezone.now()
        # 1. Generate unique code
        code = generate_entity_code(entity.role, entity.state)

        # 2. Update entity profile
        entity.entity_code = code
        entity.status = "VERIFIED"
        entity.verified_at = now
        entity.verified_by = admin_user.user_id
        entity.version += 1
        entity.save(update_fields=[
            "entity_code", "status", "verified_at", "verified_by", "version", "updated_at"
        ])

        # 3. Update Organisation
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

        # 4. Record append-only verification review
        VerificationReview.objects.create(
            review_id=uuid.uuid4(),
            entity=entity,
            reviewer_id=admin_user.user_id,
            decision="APPROVED",
            reason=review_notes or "Identity, plots, and DPDP consent verified by administration.",
            created_at=now,
        )

        # 5. Issue initial QR block
        block, serials = issue_qr_block_for_entity(
            entity=entity,
            count=qr_count,
            admin_user=admin_user,
        )

    return {
        "entity_id": str(entity.entity_id),
        "entity_code": entity.entity_code,
        "status": "VERIFIED",
        "verified_at": entity.verified_at.isoformat(),
        "block_id": str(block.block_id),
        "qr_count": block.count,
        "sample_serials": serials[:5],
    }
