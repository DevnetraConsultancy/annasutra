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
    EntityDocument,
    EntityPlot,
    EntityProfile,
    EntityRoleDetails,
    EntitySensitive,
    ProfileChangeLog,
    SensitiveAccessLog,
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

    farmer_uid = get_or_mint_farmer_uid(profile)
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
            "farmer_uid": get_or_mint_farmer_uid(profile),
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
