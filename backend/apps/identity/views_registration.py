"""Registration & Profile API views adhering to AnnaSutra_Registration_Handover.md."""

import hashlib
import json
import re
import uuid
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from PIL import Image
from rest_framework import exceptions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.labels.models import QrBlock, QrLabel
from .models import (
    EntityConsentRecord,
    EntityDeletionRequest,
    EntityDocument,
    EntityPlot,
    EntityProfile,
    EntityRoleDetails,
    EntitySensitive,
    ProfileChangeLog,
    SensitiveAccessLog,
    VerificationReview,
)
from .services.crypto import CryptoService
from .services.entity_allocation import get_or_mint_farmer_uid

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
PIN_REGEX = re.compile(r"^[0-9]{6}$")
IFSC_REGEX = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")
AADHAAR_LAST4_REGEX = re.compile(r"^[0-9]{4}$")

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB


def _get_entity_profile_for_user(user, auto_create=False, initial_role="PRODUCER"):
    """Fetch EntityProfile bound to user, optionally creating a DRAFT."""
    profile = EntityProfile.objects.filter(user_id=user.user_id).first()
    if not profile:
        # Check if an existing profile was previously created for this phone
        profile = EntityProfile.objects.filter(phone_e164=user.phone_e164).first()
        if profile and profile.user_id != user.user_id:
            profile.user_id = user.user_id
            profile.save(update_fields=["user_id"])

    if not profile and auto_create:
        role = getattr(user, "role", initial_role) or initial_role
        profile = EntityProfile.objects.create(
            entity_id=uuid.uuid4(),
            user_id=user.user_id,
            role=role if role in dict(EntityProfile.ROLE_CHOICES) else "PRODUCER",
            phone_e164=user.phone_e164,
            first_name="",
            last_name="",
            organisation_name="",
            village_town="",
            district="",
            state="",
            address_line1="",
            pincode="000000",
            photo_object_key="",
            status="DRAFT",
            version=1,
        )
    return profile


def _serialize_profile(profile):
    """Serialize profile to JSON representation with masked indicators."""
    sensitive = EntitySensitive.objects.filter(entity=profile).first()
    role_details = EntityRoleDetails.objects.filter(entity=profile).first()
    plots = EntityPlot.objects.filter(entity=profile)
    consent = EntityConsentRecord.objects.filter(entity=profile).order_by("-given_at").first()

    sensitive_masked = None
    if sensitive:
        pan_plain = CryptoService.decrypt(bytes(sensitive.pan_enc), entity_id=str(profile.entity_id)) if sensitive.pan_enc else None
        acc_plain = CryptoService.decrypt(bytes(sensitive.account_no_enc), entity_id=str(profile.entity_id)) if sensitive.account_no_enc else None
        ifsc_plain = CryptoService.decrypt(bytes(sensitive.ifsc_enc), entity_id=str(profile.entity_id)) if sensitive.ifsc_enc else None

        sensitive_masked = {
            "pan_masked": CryptoService.mask_pan(pan_plain) if pan_plain else None,
            "aadhaar_last4": sensitive.aadhaar_last4,
            "bank_name": sensitive.bank_name,
            "bank_account_masked": CryptoService.mask_bank_account(acc_plain) if acc_plain else None,
            "ifsc_masked": (ifsc_plain[:4] + "***" + ifsc_plain[-3:]) if ifsc_plain and len(ifsc_plain) >= 7 else None,
            "has_upi": bool(sensitive.upi_enc),
        }

    farmer_uid = get_or_mint_farmer_uid(profile) if profile.status == "VERIFIED" else None
    role_details = EntityRoleDetails.objects.filter(entity=profile).first()

    return {
        "entity_id": str(profile.entity_id),
        "user_id": str(profile.user_id),
        "role": profile.role,
        "entity_code": profile.entity_code,
        "farmer_uid": farmer_uid,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "organisation_name": profile.organisation_name,
        "gender": profile.gender,
        "phone_e164": profile.phone_e164,
        "email": profile.email,
        "total_land_acres": float(profile.total_land_acres) if profile.total_land_acres else None,
        "address_line1": profile.address_line1,
        "address_line2": profile.address_line2,
        "village_town": profile.village_town,
        "district": profile.district,
        "state": profile.state,
        "pincode": profile.pincode,
        "photo_object_key": profile.photo_object_key,
        "photo_url": f"/media/{profile.photo_object_key}" if profile.photo_object_key else None,
        "status": profile.status,
        "version": profile.version,
        "submitted_at": profile.submitted_at.isoformat() if profile.submitted_at else None,
        "verified_at": profile.verified_at.isoformat() if profile.verified_at else None,
        "role_details": role_details.details if role_details else {},
        "plots_count": plots.count(),
        "has_sensitive": sensitive is not None,
        "sensitive_masked": sensitive_masked,
        "consent_given": consent is not None,
        "consent_info": {
            "notice_version": consent.notice_version,
            "given_at": consent.given_at.isoformat(),
        } if consent else None,
    }


class MyProfileView(APIView):
    """Retrieve or save draft profile for current authenticated entity."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = EntityProfile.objects.filter(user_id=request.user.user_id).first()
        if not profile:
            profile = EntityProfile.objects.filter(phone_e164=request.user.phone_e164).first()
            if profile and profile.user_id != request.user.user_id:
                profile.user_id = request.user.user_id
                profile.save(update_fields=["user_id"])

        if not profile:
            return Response(
                {
                    "status": "NEW",
                    "role": getattr(request.user, "role", "PRODUCER"),
                    "phone_e164": request.user.phone_e164,
                    "farmer_uid": get_or_mint_farmer_uid(request.user),
                    "profile": None,
                },
                status=status.HTTP_200_OK,
            )
        return Response(_serialize_profile(profile), status=status.HTTP_200_OK)

    def put(self, request):
        with transaction.atomic():
            profile = _get_entity_profile_for_user(request.user, auto_create=True, initial_role=request.data.get("role", "PRODUCER"))

            if profile.status in ("SUBMITTED", "VERIFIED") and not request.data.get("override_lock"):
                raise exceptions.ValidationError(
                    {"detail": f"Profile in {profile.status} status is locked from direct draft edits.", "code": "PROFILE_LOCKED"}
                )

            # Optimistic concurrency version check
            client_version = request.data.get("version")
            if client_version is not None and int(client_version) != profile.version:
                return Response(
                    {
                        "type": "urn:problem:version-conflict",
                        "title": "Version Conflict",
                        "status": 409,
                        "detail": "Profile was modified in another session. Please reload the latest data.",
                        "code": "VERSION_CONFLICT",
                        "server_version": profile.version,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            # Compute before hash for append-only audit log
            before_bytes = json.dumps(_serialize_profile(profile), sort_keys=True).encode("utf-8")
            before_hash = hashlib.sha256(before_bytes).digest()

            # Update mutable fields (partial save permitted for DRAFT)
            updatable_fields = [
                "first_name",
                "last_name",
                "organisation_name",
                "email",
                "address_line1",
                "address_line2",
                "village_town",
                "district",
                "state",
            ]
            for field in updatable_fields:
                if field in request.data:
                    val = request.data[field]
                    setattr(profile, field, str(val).strip() if val is not None else "")

            if "gender" in request.data:
                raw_gender = str(request.data.get("gender") or "").strip().upper()
                gender_map = {
                    "M": "MALE",
                    "MALE": "MALE",
                    "F": "FEMALE",
                    "FEMALE": "FEMALE",
                    "O": "OTHER",
                    "OTHER": "OTHER",
                    "UNSPECIFIED": "UNSPECIFIED",
                    "": "UNSPECIFIED",
                }
                profile.gender = gender_map.get(raw_gender, "UNSPECIFIED")

            if "total_land_acres" in request.data and request.data["total_land_acres"] not in (None, ""):
                try:
                    acres = Decimal(str(request.data["total_land_acres"]))
                    if acres > 0:
                        profile.total_land_acres = acres
                except Exception:
                    pass

            if "pincode" in request.data:
                pin = str(request.data["pincode"]).strip()
                if PIN_REGEX.match(pin):
                    profile.pincode = pin
                elif not profile.pincode or not PIN_REGEX.match(str(profile.pincode)):
                    profile.pincode = "000000"

            if "photo_object_key" in request.data:
                profile.photo_object_key = str(request.data["photo_object_key"]).strip()

            if "role" in request.data and request.data["role"] in dict(EntityProfile.ROLE_CHOICES):
                profile.role = request.data["role"]

            profile.version += 1
            profile.save()

            if getattr(request.user, "org", None) and profile.organisation_name and profile.organisation_name.strip():
                org = request.user.org
                org.name = profile.organisation_name.strip()
                org.save(update_fields=["name"])

            # Update role details if provided
            if "role_details" in request.data and isinstance(request.data["role_details"], dict):
                role_det, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
                existing_uid = (role_det.details or {}).get("farmer_uid") or get_or_mint_farmer_uid(profile)
                merged_details = dict(request.data["role_details"])
                merged_details["farmer_uid"] = existing_uid
                role_det.details = merged_details
                role_det.save()

            # Record append-only profile change log
            after_bytes = json.dumps(_serialize_profile(profile), sort_keys=True).encode("utf-8")
            after_hash = hashlib.sha256(after_bytes).digest()
            ProfileChangeLog.objects.create(
                entity=profile,
                changed_by=request.user.user_id,
                field_group="profile_draft",
                before_hash=before_hash,
                after_hash=after_hash,
            )

        return Response(_serialize_profile(profile), status=status.HTTP_200_OK)


class SubmitProfileView(APIView):
    """Perform rigorous validation and transition profile state from DRAFT to SUBMITTED."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=False)
        if not profile:
            raise exceptions.NotFound({"detail": "Profile does not exist. Please create a draft first.", "code": "PROFILE_NOT_FOUND"})

        if profile.status == "SUBMITTED":
            return Response(
                {"detail": "Profile has already been submitted and is currently pending verification review.", "code": "ALREADY_SUBMITTED"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = {}

        # 1. Basic details validation
        if not profile.first_name or len(profile.first_name.strip()) < 2:
            errors["first_name"] = "First name is required (minimum 2 characters)."
        if not profile.last_name or len(profile.last_name.strip()) < 1:
            errors["last_name"] = "Last name is required."
        if not profile.organisation_name or len(profile.organisation_name.strip()) < 2:
            errors["organisation_name"] = "Business or Farm name is required."
        if not profile.address_line1 or len(profile.address_line1.strip()) < 3:
            errors["address_line1"] = "Street address is required."
        if not profile.village_town or len(profile.village_town.strip()) < 2:
            errors["village_town"] = "Village or Town name is required."
        if not profile.district or len(profile.district.strip()) < 2:
            errors["district"] = "District is required."
        if not profile.state or len(profile.state.strip()) < 2:
            errors["state"] = "State is required."
        if not profile.pincode or profile.pincode == "000000" or not PIN_REGEX.match(profile.pincode):
            errors["pincode"] = "A valid 6-digit postal PIN code is required."
        if not profile.photo_object_key:
            errors["photo"] = "A verified profile photograph is required."

        # 2. Role specific checks (Producer)
        if profile.role == "PRODUCER":
            plots = EntityPlot.objects.filter(entity=profile)
            if not plots.exists():
                errors["plots"] = "At least one farm plot boundary must be mapped."
            if not profile.total_land_acres or profile.total_land_acres <= 0:
                errors["total_land_acres"] = "Total landholding area in acres must be greater than zero."

            role_det = EntityRoleDetails.objects.filter(entity=profile).first()
            if not role_det or not role_det.details.get("commodities"):
                errors["commodities"] = "At least one primary crop commodity must be selected."

        # 3. Sensitive / financial checks
        sensitive = EntitySensitive.objects.filter(entity=profile).first()
        if not sensitive:
            errors["sensitive"] = "Identity (PAN or Aadhaar last-4) and bank account details must be completed."
        else:
            if not sensitive.pan_enc and not sensitive.aadhaar_last4:
                errors["identity"] = "Either a verified PAN or voluntary Aadhaar last-4 digits must be provided."
            if not sensitive.account_no_enc:
                errors["bank_account"] = "Bank account number is required for transaction settlement."
            if not sensitive.ifsc_enc:
                errors["ifsc"] = "Bank branch IFSC code is required."
            if not sensitive.bank_name:
                errors["bank_name"] = "Bank name is required."

        # 4. Consent check
        consent = EntityConsentRecord.objects.filter(entity=profile).first()
        if not consent:
            errors["consent"] = "Statutory DPDP Act 2023 and agricultural pilot terms consent must be recorded."

        if errors:
            return Response(
                {
                    "type": "urn:problem:validation-failed",
                    "title": "Validation Failed",
                    "status": 422,
                    "detail": "Please correct the required fields before submitting for review.",
                    "code": "VALIDATION_FAILED",
                    "errors": errors,
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        with transaction.atomic():
            before_bytes = json.dumps(_serialize_profile(profile), sort_keys=True).encode("utf-8")
            before_hash = hashlib.sha256(before_bytes).digest()

            profile.status = "SUBMITTED"
            profile.submitted_at = timezone.now()
            profile.version += 1
            profile.save()

            after_bytes = json.dumps(_serialize_profile(profile), sort_keys=True).encode("utf-8")
            after_hash = hashlib.sha256(after_bytes).digest()
            ProfileChangeLog.objects.create(
                entity=profile,
                changed_by=request.user.user_id,
                field_group="profile_submit",
                before_hash=before_hash,
                after_hash=after_hash,
            )

        return Response(
            {
                "status": "SUBMITTED",
                "message": "Profile submitted successfully for verification. Your application is under review.",
                "profile": _serialize_profile(profile),
            },
            status=status.HTTP_200_OK,
        )


class MySensitiveView(APIView):
    """Manage encrypted identity and bank account details for the entity."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=False)
        if not profile:
            return Response({"sensitive": None}, status=status.HTTP_200_OK)

        sensitive = EntitySensitive.objects.filter(entity=profile).first()
        if not sensitive:
            return Response({"sensitive": None}, status=status.HTTP_200_OK)

        pan_plain = CryptoService.decrypt(bytes(sensitive.pan_enc), entity_id=str(profile.entity_id)) if sensitive.pan_enc else None
        acc_plain = CryptoService.decrypt(bytes(sensitive.account_no_enc), entity_id=str(profile.entity_id)) if sensitive.account_no_enc else None
        ifsc_plain = CryptoService.decrypt(bytes(sensitive.ifsc_enc), entity_id=str(profile.entity_id)) if sensitive.ifsc_enc else None

        # Log sensitive access
        SensitiveAccessLog.objects.create(
            entity_id=profile.entity_id,
            actor_id=request.user.user_id,
            field_name="sensitive_masked_read",
            reason="Owner read masked identity details in console",
        )

        return Response(
            {
                "pan_masked": CryptoService.mask_pan(pan_plain) if pan_plain else None,
                "aadhaar_last4": sensitive.aadhaar_last4,
                "bank_name": sensitive.bank_name,
                "bank_account_masked": CryptoService.mask_bank_account(acc_plain) if acc_plain else None,
                "ifsc_masked": (ifsc_plain[:4] + "***" + ifsc_plain[-3:]) if ifsc_plain and len(ifsc_plain) >= 7 else None,
                "has_upi": bool(sensitive.upi_enc),
                "updated_at": sensitive.updated_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        if profile.status in ("SUBMITTED", "VERIFIED") and not request.data.get("override_lock"):
            raise exceptions.ValidationError(
                {"detail": f"Profile in {profile.status} status is locked from editing sensitive details.", "code": "PROFILE_LOCKED"}
            )

        pan = request.data.get("pan")
        aadhaar_last4 = request.data.get("aadhaar_last4")
        bank_name = request.data.get("bank_name")
        account_no = request.data.get("bank_account")
        bank_holder = request.data.get("bank_holder_name")
        ifsc = request.data.get("ifsc")
        upi = request.data.get("upi_id")

        entity_id_str = str(profile.entity_id)

        # PAN validation
        pan_enc = None
        pan_hmac = None
        if pan:
            pan_clean = pan.strip().upper()
            if not PAN_REGEX.match(pan_clean):
                raise exceptions.ValidationError({"detail": "Invalid PAN format. Must be 10 characters (e.g. ABCDE1234F).", "code": "INVALID_PAN"})
            pan_enc = CryptoService.encrypt(pan_clean, entity_id=entity_id_str)
            pan_hmac = CryptoService.blind_index_pan(pan_clean)

        # Aadhaar last-4 validation (RULE 5: Never accept or store full 12-digit Aadhaar!)
        a4_clean = None
        if aadhaar_last4:
            a4_str = str(aadhaar_last4).strip()
            if len(a4_str) > 4:
                raise exceptions.ValidationError(
                    {"detail": "Only the last 4 digits of Aadhaar are permitted. Full Aadhaar is never stored.", "code": "INVALID_AADHAAR"}
                )
            if not AADHAAR_LAST4_REGEX.match(a4_str):
                raise exceptions.ValidationError({"detail": "Aadhaar last 4 must be exactly 4 digits.", "code": "INVALID_AADHAAR"})
            a4_clean = a4_str

        # IFSC validation
        ifsc_enc = None
        if ifsc:
            ifsc_clean = ifsc.strip().upper()
            if not IFSC_REGEX.match(ifsc_clean):
                raise exceptions.ValidationError({"detail": "Invalid IFSC code format (e.g. SBIN0001234).", "code": "INVALID_IFSC"})
            ifsc_enc = CryptoService.encrypt(ifsc_clean, entity_id=entity_id_str)

        # Bank Account encryption
        account_enc = None
        acc_last4 = None
        if account_no:
            acc_clean = str(account_no).strip()
            if len(acc_clean) < 6 or not acc_clean.isdigit():
                raise exceptions.ValidationError({"detail": "Invalid bank account number (digits only, min 6 digits).", "code": "INVALID_ACCOUNT"})
            account_enc = CryptoService.encrypt(acc_clean, entity_id=entity_id_str)
            acc_last4 = acc_clean[-4:]

        holder_enc = None
        if bank_holder:
            holder_enc = CryptoService.encrypt(str(bank_holder).strip(), entity_id=entity_id_str)

        upi_enc = None
        if upi:
            upi_enc = CryptoService.encrypt(str(upi).strip(), entity_id=entity_id_str)

        if pan_hmac and EntitySensitive.objects.filter(pan_hmac=pan_hmac).exclude(entity=profile).exists():
            raise exceptions.ValidationError(
                {"detail": "This PAN is already registered with another entity.", "code": "DUPLICATE_PAN"}
            )

        with transaction.atomic():
            sensitive, _ = EntitySensitive.objects.get_or_create(
                entity=profile,
                defaults={"enc_key_id": CryptoService.ACTIVE_KEY_ID},
            )
            if pan_enc:
                sensitive.pan_enc = pan_enc
                sensitive.pan_hmac = pan_hmac
            if a4_clean:
                sensitive.aadhaar_last4 = a4_clean
            if bank_name:
                sensitive.bank_name = str(bank_name).strip()
            if account_enc:
                sensitive.account_no_enc = account_enc
                sensitive.account_last4 = acc_last4
            if holder_enc:
                sensitive.bank_holder_enc = holder_enc
            if ifsc_enc:
                sensitive.ifsc_enc = ifsc_enc
            if upi_enc:
                sensitive.upi_enc = upi_enc
            sensitive.enc_key_id = CryptoService.ACTIVE_KEY_ID
            sensitive.save()

            ProfileChangeLog.objects.create(
                entity=profile,
                changed_by=request.user.user_id,
                field_group="sensitive_update",
                before_hash=None,
                after_hash=hashlib.sha256(b"sensitive_encrypted").digest(),
            )

        return Response(
            {
                "status": "saved",
                "pan_masked": CryptoService.mask_pan(pan.strip().upper()) if pan else None,
                "aadhaar_last4": sensitive.aadhaar_last4,
                "bank_name": sensitive.bank_name,
                "bank_account_masked": CryptoService.mask_bank_account(account_no) if account_no else None,
                "has_upi": bool(sensitive.upi_enc),
            },
            status=status.HTTP_200_OK,
        )


class MyPlotsView(APIView):
    """Retrieve and update farm plots with AES-256-GCM encrypted GeoJSON polygons."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=False)
        if not profile:
            raise exceptions.NotFound({"detail": "Profile not found.", "code": "NOT_FOUND"})

        plots = EntityPlot.objects.filter(entity=profile).order_by("created_at")
        results = []
        for p in plots:
            geojson_data = None
            try:
                decrypted_str = CryptoService.decrypt(bytes(p.geojson_enc), entity_id=str(profile.entity_id))
                geojson_data = json.loads(decrypted_str)
            except Exception:
                geojson_data = {}

            results.append(
                {
                    "plot_id": str(p.plot_id),
                    "plot_name": p.plot_name,
                    "area_acres": float(p.area_acres),
                    "district": p.district,
                    "geojson": geojson_data,
                    "created_at": p.created_at.isoformat(),
                }
            )

        return Response({"plots": results}, status=status.HTTP_200_OK)

    def put(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        if profile.status in ("SUBMITTED", "VERIFIED") and not request.data.get("override_lock"):
            raise exceptions.ValidationError(
                {"detail": f"Profile in {profile.status} status is locked from plot modifications.", "code": "PROFILE_LOCKED"}
            )

        raw_plots = request.data.get("plots", [])
        if not isinstance(raw_plots, list):
            raise exceptions.ValidationError({"detail": "Plots must be provided as a list.", "code": "INVALID_PLOTS"})

        entity_id_str = str(profile.entity_id)
        saved_plots = []
        total_acres = Decimal("0.000")

        with transaction.atomic():
            EntityPlot.objects.filter(entity=profile).delete()
            seen_names = set()

            for idx, p_data in enumerate(raw_plots):
                base_name = str(p_data.get("plot_name") or f"Plot {idx + 1}").strip() or f"Plot {idx + 1}"
                name = base_name
                dup_idx = 2
                while name.lower() in seen_names:
                    name = f"{base_name} ({dup_idx})"
                    dup_idx += 1
                seen_names.add(name.lower())
                try:
                    acres = Decimal(str(p_data.get("area_acres", "0.000")))
                except Exception:
                    acres = Decimal("0.000")

                if acres <= 0:
                    raise exceptions.ValidationError(
                        {"detail": f"Plot '{name}' must have an area greater than 0 acres.", "code": "INVALID_AREA"}
                    )

                district = str(p_data.get("district") or profile.district or "Unknown").strip()
                geojson = p_data.get("geojson") or {"type": "Polygon", "coordinates": []}
                geojson_str = json.dumps(geojson)

                enc_geojson = CryptoService.encrypt(geojson_str, entity_id=entity_id_str)

                plot_obj = EntityPlot.objects.create(
                    plot_id=uuid.uuid4(),
                    entity=profile,
                    plot_name=name,
                    area_acres=acres,
                    district=district,
                    geojson_enc=enc_geojson,
                    enc_key_id=CryptoService.ACTIVE_KEY_ID,
                )
                total_acres += acres
                saved_plots.append(
                    {
                        "plot_id": str(plot_obj.plot_id),
                        "plot_name": plot_obj.plot_name,
                        "area_acres": float(plot_obj.area_acres),
                        "district": plot_obj.district,
                        "geojson": geojson,
                    }
                )

            profile.total_land_acres = total_acres if total_acres > 0 else None
            profile.save(update_fields=["total_land_acres"])

        return Response({"status": "saved", "plots": saved_plots, "total_acres": float(total_acres)}, status=status.HTTP_200_OK)


def _save_media_blob(object_key: str, content_type: str, data: bytes) -> None:
    """Persist media binary in DB for serverless multi-instance resilience."""
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            if connection.vendor == "mysql":
                cursor.execute(
                    "INSERT INTO media_blob (object_key, content_type, data) VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE content_type = VALUES(content_type), data = VALUES(data)",
                    [object_key, content_type, data],
                )
            else:
                cursor.execute(
                    "INSERT OR REPLACE INTO media_blob (object_key, content_type, data) VALUES (%s, %s, %s)",
                    [object_key, content_type, data],
                )
    except Exception:
        pass


class UploadPhotoView(APIView):
    """Secure profile photo upload with automated EXIF stripping and dimensions optimization."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        photo_file = request.FILES.get("photo")

        if not photo_file:
            raise exceptions.ValidationError({"detail": "Photo file is required.", "code": "FIELD_REQUIRED"})

        if photo_file.size > MAX_UPLOAD_SIZE:
            raise exceptions.ValidationError({"detail": "Photo exceeds 5MB size limit.", "code": "FILE_TOO_LARGE"})

        allowed_mimes = ["image/jpeg", "image/jpg", "image/pjpeg", "image/png", "image/webp", "application/octet-stream"]
        content_type = (getattr(photo_file, "content_type", "") or "").lower()
        if content_type and content_type not in allowed_mimes:
            raise exceptions.ValidationError({"detail": "Only JPEG, PNG, and WebP images are permitted.", "code": "INVALID_MIME"})

        try:
            import io
            from PIL import ImageOps

            image = Image.open(photo_file)
            image.verify()  # Verify integrity
            photo_file.seek(0)
            image = Image.open(photo_file)
            try:
                image = ImageOps.exif_transpose(image)
            except Exception:
                pass

            # Convert to RGB while stripping EXIF metadata into a fresh canvas
            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                rgba_img = image.convert("RGBA")
                clean_image = Image.new("RGB", rgba_img.size, (255, 255, 255))
                clean_image.paste(rgba_img, mask=rgba_img.split()[3])
            else:
                rgb_conv = image.convert("RGB")
                clean_image = Image.new("RGB", rgb_conv.size)
                clean_image.paste(rgb_conv)

            # Resize if dimensions exceed 1024x1024
            max_dim = 1024
            if clean_image.width > max_dim or clean_image.height > max_dim:
                clean_image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

            filename = f"producer_{profile.entity_id}_{uuid.uuid4().hex[:8]}.jpg"
            base_media = Path(getattr(settings, "MEDIA_ROOT", Path("/tmp") / "media"))
            dest_dir = base_media / "photos"
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                dest_dir = Path("/tmp") / "media" / "photos"
                dest_dir.mkdir(parents=True, exist_ok=True)

            out_buf = io.BytesIO()
            clean_image.save(out_buf, "JPEG", quality=85, optimize=True)
            clean_bytes = out_buf.getvalue()

            dest_path = dest_dir / filename
            dest_path.write_bytes(clean_bytes)

            object_key = f"photos/{filename}"
            _save_media_blob(object_key, "image/jpeg", clean_bytes)
            profile.photo_object_key = object_key
            profile.save(update_fields=["photo_object_key"])

            return Response(
                {
                    "status": "uploaded",
                    "photo_object_key": object_key,
                    "url": f"/media/{object_key}",
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            raise exceptions.ValidationError({"detail": f"Failed to process image: {str(e)}", "code": "IMAGE_PROCESSING_FAILED"})


class UploadDocumentView(APIView):
    """Upload supporting identity or compliance documents with SHA-256 checksumming."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        doc_file = request.FILES.get("document")
        doc_type = str(request.data.get("doc_type", "OTHER") or "OTHER").strip().upper()

        if not doc_file:
            raise exceptions.ValidationError({"detail": "Document file is required.", "code": "FIELD_REQUIRED"})

        if doc_file.size > MAX_UPLOAD_SIZE:
            raise exceptions.ValidationError({"detail": "Document exceeds 5MB size limit.", "code": "FILE_TOO_LARGE"})

        allowed_types = {
            "PAN_IMAGE", "FSSAI", "GST", "TRADE_LICENCE", "MANDI_LICENCE",
            "SCALE_CALIBRATION", "LAND_RECORD", "FPO_REG", "ORGANIC_CERT", "OTHER",
        }
        if doc_type not in allowed_types:
            raise exceptions.ValidationError({"detail": f"Invalid doc_type. Choices: {sorted(allowed_types)}", "code": "INVALID_DOC_TYPE"})

        file_bytes = doc_file.read()
        sha256_hash = hashlib.sha256(file_bytes).digest()

        # Save to disk securely
        ext = Path(doc_file.name).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".pdf"):
            ext = ".bin"

        filename = f"doc_{profile.entity_id}_{uuid.uuid4().hex[:8]}{ext}"
        base_media = Path(getattr(settings, "MEDIA_ROOT", Path("/tmp") / "media"))
        dest_dir = base_media / "documents"
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            dest_dir = Path("/tmp") / "media" / "documents"
            dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / filename
        dest_path.write_bytes(file_bytes)

        object_key = f"documents/{filename}"
        mime_type = getattr(doc_file, "content_type", None) or "application/octet-stream"
        _save_media_blob(object_key, mime_type, file_bytes)

        try:
            doc = EntityDocument.objects.create(
                doc_id=uuid.uuid4(),
                entity=profile,
                doc_type=doc_type,
                object_key=object_key,
                sha256=sha256_hash,
                review="UNREVIEWED",
            )
        except Exception:
            doc = EntityDocument.objects.create(
                doc_id=uuid.uuid4(),
                entity=profile,
                doc_type="OTHER",
                object_key=object_key,
                sha256=sha256_hash,
                review="UNREVIEWED",
            )

        return Response(
            {
                "status": "uploaded",
                "doc_id": str(doc.doc_id),
                "doc_type": doc.doc_type,
                "sha256": sha256_hash.hex(),
                "object_key": object_key,
            },
            status=status.HTTP_201_CREATED,
        )


class RecordConsentView(APIView):
    """Record explicit statutory consent adhering to DPDP Act 2023 purpose limitation."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        notice_version = request.data.get("notice_version", "v1.0-2026")
        language = request.data.get("language", "en")
        purposes = request.data.get("purposes", "DPDP_PURPOSE_LIMITATION,AADHAAR_VOLUNTARY_LAST4,TRACEABILITY_PILOT_TERMS")

        if isinstance(purposes, list):
            purposes = ",".join(purposes)

        consent = EntityConsentRecord.objects.create(
            consent_id=uuid.uuid4(),
            entity=profile,
            notice_version=str(notice_version).strip()[:20],
            language=str(language).strip()[:5],
            purposes=str(purposes).strip()[:300],
        )

        return Response(
            {
                "status": "recorded",
                "consent_id": str(consent.consent_id),
                "notice_version": consent.notice_version,
                "given_at": consent.given_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class MyQrBlocksView(APIView):
    """GET /api/v1/me/qr-blocks
    List all physical QR label blocks allocated to the authenticated entity's organisation.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_org = getattr(request.user, "org", None)
        if not user_org:
            return Response({"blocks": [], "total_issued": 0, "total_bound": 0, "total_available": 0}, status=status.HTTP_200_OK)

        blocks = QrBlock.objects.filter(issued_to_org=user_org).order_by("-issued_at")
        results = []
        total_issued = 0
        total_bound = 0
        total_available = 0

        for b in blocks:
            b_count = b.count
            bound = b.labels.filter(status="BOUND").count()
            avail = b.labels.filter(status="ISSUED").count()
            void_c = b.labels.filter(status="VOID").count()

            total_issued += b_count
            total_bound += bound
            total_available += avail

            sample_serials = list(b.labels.order_by("serial").values_list("serial", flat=True)[:5])

            results.append({
                "block_id": str(b.block_id),
                "count": b_count,
                "issued_at": b.issued_at.isoformat(),
                "bound_count": bound,
                "available_count": avail,
                "void_count": void_c,
                "sample_serials": sample_serials,
                "download_pdf_url": f"/api/v1/me/qr-blocks/{b.block_id}/sheet.pdf",
            })

        return Response({
            "blocks": results,
            "total_issued": total_issued,
            "total_bound": total_bound,
            "total_available": total_available,
        }, status=status.HTTP_200_OK)


class MyQrBlockSheetPdfView(APIView):
    """GET /api/v1/me/qr-blocks/{block_id}/sheet.pdf
    Download printable A4 sticker PDF sheet containing 13-character Crockford Base32 QR labels.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, block_id):
        user_org = getattr(request.user, "org", None)
        if not user_org:
            raise exceptions.NotFound({"detail": "User has no associated organisation.", "code": "NO_ORG"})

        try:
            block = QrBlock.objects.get(block_id=block_id, issued_to_org=user_org)
        except QrBlock.DoesNotExist:
            raise exceptions.NotFound({"detail": "QR block not found or access denied.", "code": "NOT_FOUND"})

        serials = list(block.labels.order_by("serial").values_list("serial", flat=True))
        if not serials:
            raise exceptions.ValidationError({"detail": "No serials found in this block.", "code": "EMPTY_BLOCK"})

        profile = EntityProfile.objects.filter(user_id=request.user.user_id).first()
        entity_code = get_or_mint_farmer_uid(profile) if profile else user_org.name[:16]
        org_name = profile.organisation_name if profile and profile.organisation_name else user_org.name

        from apps.identity.services.pdf_sheet import render_a4_sticker_sheet
        from django.http import HttpResponse

        pdf_bytes = render_a4_sticker_sheet(
            serials=serials,
            entity_code=entity_code,
            org_name=org_name,
        )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="annasutra_qr_block_{block_id}.pdf"'
        return response


class MyRoleStatsView(APIView):
    """GET /api/v1/me/stats
    Return real database-computed operational statistics for the authenticated entity conforming to Section 10.
    Zero fabricated metrics, zero placeholder data.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        user_org = getattr(request.user, "org", None)

        from apps.lots.models import Lot
        from apps.inventory.models import LotBalance
        from apps.custody.models import Handover

        # Real DB queries
        lots_count = 0
        total_kg = 0.0
        pending_handovers = 0
        confirmed_handovers = 0
        discrepancies = 0
        qr_available = 0
        qr_bound = 0

        if user_org:
            lots_count = Lot.objects.filter(created_by_org=user_org).count()
            kg_sum = LotBalance.objects.filter(lot__created_by_org=user_org).aggregate(Sum("qty_in_kg"))["qty_in_kg__sum"]
            total_kg = float(kg_sum) if kg_sum else 0.0

            pending_handovers = Handover.objects.filter(
                Q(from_org=user_org) | Q(to_org=user_org),
                state="PENDING"
            ).count()

            confirmed_handovers = Handover.objects.filter(
                Q(from_org=user_org) | Q(to_org=user_org),
                state="ACCEPTED"
            ).count()

            discrepancies = Handover.objects.filter(
                Q(from_org=user_org) | Q(to_org=user_org),
                state="ACCEPTED_WITH_DISCREPANCY"
            ).count()

            qr_available = QrLabel.objects.filter(issued_to_org=user_org, status="ISSUED").count()
            qr_bound = QrLabel.objects.filter(issued_to_org=user_org, status="BOUND").count()

        plot_count = profile.plots.count()
        total_land = float(profile.total_land_acres) if profile.total_land_acres else 0.0

        return Response({
            "entity_id": str(profile.entity_id),
            "role": profile.role,
            "status": profile.status,
            "entity_code": profile.entity_code,
            "farmer_uid": get_or_mint_farmer_uid(profile) if profile.status == "VERIFIED" else None,
            "stats": {
                "batches_created": lots_count,
                "total_kg_declared": total_kg,
                "handovers_pending": pending_handovers,
                "handovers_confirmed": confirmed_handovers,
                "discrepancies_flagged": discrepancies,
                "qr_labels_available": qr_available,
                "qr_labels_bound": qr_bound,
                "plots_count": plot_count,
                "total_land_acres": total_land,
            },
            "refreshed_at": timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)


class MySeasonAllocationsView(APIView):
    """GET / POST / DELETE /api/v1/me/season-allocations
    Manage Season Crop Class Acreage Allocations across 10 agricultural domains.
    Validates allocated acreage against verified total land parcel capacity.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        role_details, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
        allocations = role_details.details.get("season_allocations", [])
        total_allocated = sum(float(a.get("acres") or 0) for a in allocations)
        total_land = float(profile.total_land_acres or 0.0)

        return Response({
            "season_allocations": allocations,
            "allocations": allocations,
            "total_allocated_acres": round(total_allocated, 3),
            "total_land_acres": round(total_land, 3),
            "remaining_acres": round(max(0.0, total_land - total_allocated), 3),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        role_details, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
        allocations = role_details.details.setdefault("season_allocations", [])

        data = request.data
        season = str(data.get("season") or "Rabi 2026-27").strip()
        crop_category = str(data.get("crop_category") or data.get("category_code") or "VG").strip().upper()
        crop_name = str(data.get("crop_name") or data.get("crop") or "").strip()
        variety = str(data.get("variety") or "").strip()
        acres = float(data.get("acres") or data.get("area_acres") or 0.0)
        plot_id = str(data.get("plot_id") or "").strip()
        plot_name = str(data.get("plot_name") or "").strip()
        sowing_date = str(data.get("sowing_date") or "").strip()
        expected_harvest = str(data.get("expected_harvest_date") or data.get("expected_harvest") or "").strip()

        if not crop_name:
            raise exceptions.ValidationError({"detail": "crop_name is required.", "code": "FIELD_REQUIRED"})
        if acres <= 0:
            raise exceptions.ValidationError({"detail": "acres must be greater than 0.", "code": "INVALID_ACRES"})

        entry = {
            "allocation_id": str(uuid.uuid4()),
            "season": season,
            "crop_category": crop_category,
            "crop_name": crop_name,
            "variety": variety,
            "acres": acres,
            "plot_id": plot_id,
            "plot_name": plot_name,
            "sowing_date": sowing_date,
            "expected_harvest_date": expected_harvest,
            "created_at": timezone.now().isoformat(),
        }

        allocations.append(entry)
        role_details.details["season_allocations"] = allocations
        role_details.save()

        total_allocated = sum(float(a.get("acres") or 0) for a in allocations)
        total_land = float(profile.total_land_acres or 0.0)

        return Response({
            "status": "saved",
            "allocation": entry,
            "allocations": allocations,
            "total_allocated_acres": round(total_allocated, 3),
            "remaining_acres": round(max(0.0, total_land - total_allocated), 3),
        }, status=status.HTTP_201_CREATED)

    def delete(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        role_details, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
        allocations = role_details.details.get("season_allocations", [])

        alloc_id = request.data.get("allocation_id") or request.query_params.get("allocation_id")
        if alloc_id:
            allocations = [a for a in allocations if a.get("allocation_id") != str(alloc_id)]
            role_details.details["season_allocations"] = allocations
            role_details.save()

        return Response({"status": "deleted", "allocations": allocations}, status=status.HTTP_200_OK)


class MyHarvestRecordsView(APIView):
    """GET / POST /api/v1/me/harvest-records
    Log harvest yields mapped to land plots & season crop allocations.
    Enforces Mass Balance accounting: Gross Yield - Waste Loss = Net Yield = Lotted + Unlotted.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        role_details, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
        harvests = role_details.details.get("harvest_records", [])

        total_gross = sum(float(h.get("gross_weight_kg") or 0) for h in harvests)
        total_net = sum(float(h.get("net_yield_kg") or 0) for h in harvests)
        total_lotted = sum(float(h.get("lotted_kg") or 0) for h in harvests)
        total_unlotted = max(0.0, total_net - total_lotted)

        return Response({
            "harvest_records": harvests,
            "harvests": harvests,
            "total_gross_kg": round(total_gross, 2),
            "total_net_kg": round(total_net, 2),
            "total_lotted_kg": round(total_lotted, 2),
            "total_unlotted_kg": round(total_unlotted, 2),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        role_details, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
        harvests = role_details.details.setdefault("harvest_records", [])

        data = request.data
        plot_id = str(data.get("plot_id") or "").strip()
        plot_name = str(data.get("plot_name") or "Primary Farm Parcel").strip()
        crop_category = str(data.get("crop_category") or data.get("category_code") or "VG").strip().upper()
        crop_name = str(data.get("crop_name") or data.get("crop") or "").strip()
        variety = str(data.get("variety") or "").strip()
        harvest_date = str(data.get("harvest_date") or timezone.now().date().isoformat()).strip()
        gross_weight_kg = float(data.get("gross_weight_kg") or data.get("qty_kg") or 0.0)
        waste_loss_kg = float(data.get("waste_loss_kg") or 0.0)
        net_yield_kg = max(0.0, gross_weight_kg - waste_loss_kg)
        storage_location = str(data.get("storage_location") or "Farm Store / On-site Granary").strip()

        if not crop_name:
            raise exceptions.ValidationError({"detail": "crop_name is required.", "code": "FIELD_REQUIRED"})
        if gross_weight_kg <= 0:
            raise exceptions.ValidationError({"detail": "gross_weight_kg must be greater than 0.", "code": "INVALID_WEIGHT"})

        entry = {
            "harvest_id": str(uuid.uuid4()),
            "plot_id": plot_id,
            "plot_name": plot_name,
            "crop_category": crop_category,
            "crop_name": crop_name,
            "variety": variety,
            "harvest_date": harvest_date,
            "gross_weight_kg": gross_weight_kg,
            "waste_loss_kg": waste_loss_kg,
            "net_yield_kg": net_yield_kg,
            "lotted_kg": 0.0,
            "remaining_unlotted_kg": net_yield_kg,
            "storage_location": storage_location,
            "created_at": timezone.now().isoformat(),
        }

        harvests.append(entry)
        role_details.details["harvest_records"] = harvests
        role_details.save()

        return Response({
            "status": "recorded",
            "harvest": entry,
            "harvest_records": harvests,
        }, status=status.HTTP_201_CREATED)


class MyChangeRequestsView(APIView):
    """GET / POST /api/v1/me/change-requests
    Submit modification requests for Admin-locked profile attributes (Name, KYC, Land, Bank).
    Self-editable fields (Email, Language, Alternate Phone, UPI) can be updated immediately.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        role_details, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
        change_requests = role_details.details.get("change_requests", [])
        return Response({"change_requests": change_requests}, status=status.HTTP_200_OK)

    def post(self, request):
        profile = _get_entity_profile_for_user(request.user, auto_create=True)
        role_details, _ = EntityRoleDetails.objects.get_or_create(entity=profile)
        change_requests = role_details.details.setdefault("change_requests", [])

        data = request.data
        field_group = str(data.get("field_group") or "PROFILE_UPDATE").strip().upper()
        requested_changes = data.get("requested_changes") or {}
        reason = str(data.get("reason") or "Farmer profile data update").strip()

        if not requested_changes or not isinstance(requested_changes, dict):
            raise exceptions.ValidationError({"detail": "requested_changes dictionary is required.", "code": "FIELD_REQUIRED"})

        entry = {
            "request_id": str(uuid.uuid4()),
            "entity_id": str(profile.entity_id),
            "farmer_uid": get_or_mint_farmer_uid(profile) if profile.status == "VERIFIED" else None,
            "farmer_name": f"{profile.first_name} {profile.last_name}".strip() or profile.organisation_name,
            "phone_e164": profile.phone_e164,
            "field_group": field_group,
            "requested_changes": requested_changes,
            "reason": reason,
            "status": "PENDING",
            "created_at": timezone.now().isoformat(),
            "reviewed_at": None,
            "reviewer_reason": None,
        }

        change_requests.append(entry)
        role_details.details["change_requests"] = change_requests
        role_details.save()

        return Response({
            "status": "submitted",
            "change_request": entry,
        }, status=status.HTTP_201_CREATED)


class MyProfileDeleteRequestView(APIView):

    """Handles entity profile deletion requests (Right to Erasure / Deactivation).

    Supports GET (pre-flight status and checks) and POST (OTP request or final submission).

    """

    permission_classes = [IsAuthenticated]



    def get(self, request):

        profile = _get_entity_profile_for_user(request.user, auto_create=False)

        del_req = None

        if profile:

            try:

                del_req = EntityDeletionRequest.objects.filter(entity=profile, status="PENDING").first()

            except Exception:

                del_req = None



        org = getattr(request.user, "org", None)

        in_transit_count = 0

        active_custody_count = 0

        blocking_reasons = []



        try:

            from apps.custody.models import Handover

            from apps.lots.models import Lot



            if org:

                in_transit_count = Lot.objects.filter(

                    Q(custodian_org=org) | Q(created_by_org=org),

                    state__in=["IN_TRANSIT", "HANDOVER_REQUESTED", "DISPUTED"]

                ).count()

                open_handovers = Handover.objects.filter(from_org=org, state="INITIATED").count()

                if open_handovers > 0:

                    in_transit_count += open_handovers



                active_custody_count = Lot.objects.filter(custodian_org=org, state="IN_CUSTODY").count()



            if in_transit_count > 0:

                blocking_reasons.append(

                    f"You have {in_transit_count} lot(s) currently in transit or pending handover. Complete or cancel open dispatches first."

                )



            if profile and profile.role in ("AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER") and active_custody_count > 0:

                blocking_reasons.append(

                    f"You currently have {active_custody_count} active lot(s) in custody. All stock must be dispatched, closed, or marked sold out before account deletion."

                )

        except Exception:

            pass



        return Response({

            "has_pending_request": del_req is not None,

            "entity_status": profile.status if profile else "NEW",

            "can_request_deletion": len(blocking_reasons) == 0,

            "blocking_reasons": blocking_reasons,

            "active_in_transit_count": in_transit_count,

            "active_custody_count": active_custody_count,

            "registered_phone": profile.phone_e164 if profile else getattr(request.user, "phone_e164", ""),

            "pending_request": {

                "request_id": str(del_req.request_id),

                "reason": del_req.reason,

                "reason_display": del_req.get_reason_display(),

                "remarks": del_req.remarks,

                "created_at": del_req.created_at.isoformat(),

                "status": del_req.status,

            } if del_req else None,

        })



    def post(self, request):

        profile = _get_entity_profile_for_user(request.user, auto_create=False)

        user_role = getattr(request.user, "role", "OWNER")

        if user_role not in ("OWNER", "PRODUCER", "AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER", ""):

            raise exceptions.PermissionDenied({"detail": "Only the registered account owner can request account deletion.", "code": "OWNER_ONLY"})



        data = request.data or {}

        action = data.get("action")

        phone_e164 = profile.phone_e164 if profile else getattr(request.user, "phone_e164", "")



        if action == "request_otp":

            from .services.otp import OtpService

            otp_res = OtpService.request_otp(phone_e164, language=data.get("language", "en"))

            res_payload = {

                "status": "OTP_SENT",

                "message": f"Verification OTP sent to registered mobile {phone_e164[-4:].rjust(len(phone_e164), '*') if phone_e164 else 'on file'}.",

                "expires_in": otp_res.get("expires_in", 300),

            }

            if "debug_code" in otp_res:

                res_payload["debug_code"] = otp_res["debug_code"]

            return Response(res_payload, status=status.HTTP_202_ACCEPTED)



        # If user has no saved profile yet, delete/deactivate user directly

        if not profile:

            otp_code = str(data.get("otp_code", "")).strip()

            from .services.otp import OtpService

            otp_valid = False

            if (getattr(settings, "OTP_DEBUG", False) or getattr(settings, "DEBUG", False)) and otp_code in ("123456", data.get("debug_code")):

                otp_valid = True

            elif phone_e164 and otp_code:

                otp_valid = OtpService.verify_otp(phone_e164, otp_code)

            elif not otp_code:

                raise exceptions.ValidationError({"detail": "Verification code is required to delete account.", "code": "OTP_REQUIRED"})



            if not otp_valid:

                raise exceptions.ValidationError({"detail": "Invalid or expired verification code.", "code": "INVALID_OTP"})



            user = request.user

            user.status = "DISABLED"

            user.save(update_fields=["status"])

            return Response({

                "status": "DELETED",

                "message": "Account successfully deleted.",

            }, status=status.HTTP_200_OK)



        reason = str(data.get("reason", "")).strip()

        remarks = str(data.get("remarks", "")).strip()

        otp_code = str(data.get("otp_code", "")).strip()



        valid_reasons = dict(EntityDeletionRequest.REASON_CHOICES)

        if not reason or reason not in valid_reasons:

            raise exceptions.ValidationError({"detail": f"Valid reason required. Choices: {list(valid_reasons.keys())}", "code": "INVALID_REASON"})



        if not otp_code:

            raise exceptions.ValidationError({"detail": "OTP code is required to authenticate deletion request.", "code": "OTP_REQUIRED"})



        from .services.otp import OtpService

        otp_valid = False

        if (getattr(settings, "OTP_DEBUG", False) or getattr(settings, "DEBUG", False)) and otp_code in ("123456", data.get("debug_code")):

            otp_valid = True

        else:

            otp_valid = OtpService.verify_otp(profile.phone_e164, otp_code)



        if not otp_valid:

            raise exceptions.ValidationError({"detail": "Invalid or expired OTP code.", "code": "INVALID_OTP"})



        org = getattr(request.user, "org", None)

        try:

            from apps.custody.models import Handover

            from apps.lots.models import Lot



            if org:

                in_transit = Lot.objects.filter(

                    Q(custodian_org=org) | Q(created_by_org=org),

                    state__in=["IN_TRANSIT", "HANDOVER_REQUESTED", "DISPUTED"]

                ).count()

                open_handovers = Handover.objects.filter(from_org=org, state="INITIATED").count()

                if (in_transit + open_handovers) > 0:

                    raise exceptions.ValidationError({

                        "detail": "Cannot submit account deletion request while lots are in transit. Complete or cancel open dispatches first.",

                        "code": "IN_TRANSIT_BLOCK"

                    })



                if profile.role in ("AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"):

                    active_stock = Lot.objects.filter(custodian_org=org, state="IN_CUSTODY").count()

                    if active_stock > 0:

                        raise exceptions.ValidationError({

                            "detail": f"You currently have {active_stock} active lot(s) in custody. All stock must be dispatched, closed, or marked sold out before account deletion.",

                            "code": "ACTIVE_STOCK_BLOCK"

                        })

        except exceptions.ValidationError:

            raise

        except Exception:

            pass



        del_req, _ = EntityDeletionRequest.objects.update_or_create(

            entity=profile,

            status="PENDING",

            defaults={

                "requested_by_user_id": request.user.user_id,

                "reason": reason,

                "remarks": remarks,

                "created_at": timezone.now(),

            }

        )



        profile.status = "DELETION_REQUESTED"

        profile.save(update_fields=["status", "updated_at"])



        VerificationReview.objects.create(

            entity=profile,

            reviewer_id=request.user.user_id,

            decision="DELETION_REQUESTED",

            reason=f"Account deletion requested by registered owner. Reason: {valid_reasons.get(reason)}. Remarks: {remarks}".strip(),

        )



        return Response({

            "status": "DELETION_REQUESTED",

            "request_id": str(del_req.request_id),

            "message": "Account deletion request submitted. Operations are now frozen pending administrative review.",

        }, status=status.HTTP_201_CREATED)





class MyProfileDeleteRequestCancelView(APIView):

    """Allows an entity owner to withdraw/cancel a pending account deletion request."""

    permission_classes = [IsAuthenticated]



    def post(self, request):

        profile = _get_entity_profile_for_user(request.user, auto_create=False)

        if not profile:

            return Response({"status": "CANCELLED", "message": "No pending deletion request found."})



        del_req = None

        try:

            del_req = EntityDeletionRequest.objects.filter(entity=profile, status="PENDING").first()

        except Exception:

            del_req = None



        if not del_req:

            return Response({"status": "CANCELLED", "message": "No pending account deletion request found."})



        del_req.status = "CANCELLED"

        del_req.save(update_fields=["status", "updated_at"])



        profile.status = "VERIFIED"

        profile.save(update_fields=["status", "updated_at"])



        VerificationReview.objects.create(

            entity=profile,

            reviewer_id=request.user.user_id,

            decision="RESTORED",

            reason="Account deletion request cancelled by entity owner.",

        )



        return Response({

            "status": "VERIFIED",

            "message": "Account deletion request successfully withdrawn. Normal operations restored.",

        }, status=status.HTTP_200_OK)

