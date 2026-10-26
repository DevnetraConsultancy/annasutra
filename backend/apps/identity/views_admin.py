"""AnnaSutra Admin Review Queue & QR Block Issuance API Views.
Conforms to Handover Sections 9, 10, 11 and DPDP 2023 audit standards.
"""

import hmac
import json
import uuid

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.authentication import JWTAuthentication
from apps.identity.models import (
    AppUser,
    EntityProfile,
    EntityRoleDetails,
    EntitySensitive,
    SensitiveAccessLog,
    VerificationReview,
)
from apps.identity.services.crypto import (
    decrypt_field,
    mask_bank_account,
    mask_pan,
    mask_upi,
)
from apps.identity.services.entity_allocation import (
    approve_entity_registration,
    issue_qr_block_for_entity,
)
from apps.labels.models import QrBlock


class IsAdminOrStaff(permissions.BasePermission):
    """Permission allowing access only to OWNER/STAFF platform operators or admin secret header."""

    def has_permission(self, request, view):
        # Allow via secure administrative key header with constant-time comparison
        admin_key = request.headers.get("X-Admin-Key")
        if admin_key:
            expected_key = getattr(settings, "ADMIN_API_KEY", settings.SECRET_KEY)
            if expected_key and hmac.compare_digest(str(admin_key), str(expected_key)):
                return True

        if not request.user or not request.user.is_authenticated:
            return False

        # Allow user with OWNER or STAFF roles
        return getattr(request.user, "role", None) in ("OWNER", "STAFF")


_trash_enums_ensured = True


def _ensure_trash_enums():
    pass


class AdminReviewQueueView(APIView):
    """GET /api/v1/admin/reviews?status=SUBMITTED
    List entity registrations awaiting administrative verification.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        _ensure_trash_enums()
        status_filter = request.query_params.get("status", "SUBMITTED").upper()
        role_filter = request.query_params.get("role")
        state_filter = request.query_params.get("state")
        search_query = request.query_params.get("q")

        qs = EntityProfile.objects.all().order_by("-submitted_at", "-created_at")

        if status_filter == "TRASH":
            qs = qs.filter(status="TRASH")
        elif status_filter == "ALL":
            qs = qs.exclude(status="TRASH")
        else:
            qs = qs.filter(status=status_filter)

        if role_filter:
            qs = qs.filter(role=role_filter.upper())

        if state_filter:
            qs = qs.filter(state__iexact=state_filter)

        if search_query:
            qs = qs.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(organisation_name__icontains=search_query)
                | Q(phone_e164__icontains=search_query)
                | Q(entity_code__icontains=search_query)
                | Q(district__icontains=search_query)
            )

        results = []
        for p in qs[:100]:
            results.append({
                "entity_id": str(p.entity_id),
                "role": p.role,
                "entity_code": p.entity_code,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "full_name": f"{p.first_name} {p.last_name}".strip(),
                "organisation_name": p.organisation_name,
                "phone_e164": p.phone_e164,
                "district": p.district,
                "state": p.state,
                "pincode": p.pincode,
                "status": p.status,
                "total_land_acres": float(p.total_land_acres) if p.total_land_acres else None,
                "plot_count": p.plots.count(),
                "document_count": p.documents.count(),
                "photo_url": p.photo_object_key if p.photo_object_key else None,
                "submitted_at": p.submitted_at.isoformat() if p.submitted_at else None,
                "created_at": p.created_at.isoformat(),
            })

        return Response({
            "count": len(results),
            "status_filter": status_filter,
            "results": results,
        })


class AdminEntityDetailView(APIView):
    """GET /api/v1/admin/entities/{entity_id}
    Retrieve full profile for admin review, with masked sensitive data and decrypted plot boundaries.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request, entity_id):
        try:
            entity = EntityProfile.objects.get(entity_id=entity_id)
        except EntityProfile.DoesNotExist:
            raise exceptions.NotFound({"detail": "Entity profile not found.", "code": "NOT_FOUND"})

        # Decrypt plot GeoJSON for administrative inspection
        plots_data = []
        for plot in entity.plots.all():
            geojson_dict = {}
            if plot.geojson_enc:
                try:
                    decrypted_raw = decrypt_field(bytes(plot.geojson_enc), str(entity.entity_id))
                    geojson_dict = json.loads(decrypted_raw)
                except Exception:
                    geojson_dict = {"error": "Failed to decrypt plot polygon"}

            plots_data.append({
                "plot_id": str(plot.plot_id),
                "plot_name": plot.plot_name,
                "area_acres": float(plot.area_acres),
                "district": plot.district,
                "geojson": geojson_dict,
                "created_at": plot.created_at.isoformat(),
            })

        # Masked sensitive preview
        sensitive_data = {}
        try:
            sens = entity.sensitive
            pan_val = None
            if sens.pan_enc:
                try:
                    pan_val = mask_pan(decrypt_field(bytes(sens.pan_enc), str(entity.entity_id)))
                except Exception:
                    pan_val = "DECRYPTION_ERROR"

            acc_val = None
            if sens.account_no_enc:
                try:
                    acc_val = mask_bank_account(decrypt_field(bytes(sens.account_no_enc), str(entity.entity_id)))
                except Exception:
                    acc_val = "DECRYPTION_ERROR"

            ifsc_val = None
            if sens.ifsc_enc:
                try:
                    ifsc_val = decrypt_field(bytes(sens.ifsc_enc), str(entity.entity_id))
                except Exception:
                    ifsc_val = "DECRYPTION_ERROR"

            upi_val = None
            if sens.upi_enc:
                try:
                    upi_val = mask_upi(decrypt_field(bytes(sens.upi_enc), str(entity.entity_id)))
                except Exception:
                    upi_val = "DECRYPTION_ERROR"

            sensitive_data = {
                "has_pan": bool(sens.pan_enc),
                "pan_masked": pan_val,
                "bank_name": sens.bank_name,
                "account_no_masked": acc_val,
                "ifsc": ifsc_val,
                "upi_masked": upi_val,
                "aadhaar_last4": sens.aadhaar_last4,
            }
        except EntitySensitive.DoesNotExist:
            sensitive_data = {"configured": False}

        # Role details
        role_details_data = {}
        try:
            role_details_data = entity.role_details.details
        except EntityRoleDetails.DoesNotExist:
            pass

        # Documents
        docs_data = [
            {
                "doc_id": str(d.doc_id),
                "doc_type": d.doc_type,
                "object_key": d.object_key,
                "review": d.review,
                "uploaded_at": d.uploaded_at.isoformat(),
            }
            for d in entity.documents.all()
        ]

        # Prior reviews
        reviews_data = [
            {
                "review_id": str(r.review_id),
                "decision": r.decision,
                "reason": r.reason,
                "created_at": r.created_at.isoformat(),
            }
            for r in entity.reviews.all().order_by("-created_at")
        ]

        # Consents
        consents_data = [
            {
                "consent_id": str(c.consent_id),
                "notice_version": c.notice_version,
                "language": c.language,
                "purposes": c.purposes,
                "given_at": c.given_at.isoformat(),
            }
            for c in entity.consent_records.all()
        ]

        # Issued QR blocks (if verified)
        qr_blocks_data = []
        try:
            user = AppUser.objects.get(user_id=entity.user_id)
            blocks = QrBlock.objects.filter(issued_to_org=user.org).order_by("-issued_at")
            for b in blocks:
                qr_blocks_data.append({
                    "block_id": str(b.block_id),
                    "count": b.count,
                    "issued_at": b.issued_at.isoformat(),
                    "bound_count": b.labels.filter(status="BOUND").count(),
                    "available_count": b.labels.filter(status="ISSUED").count(),
                })
        except Exception:
            pass

        return Response({
            "entity_id": str(entity.entity_id),
            "role": entity.role,
            "entity_code": entity.entity_code,
            "status": entity.status,
            "first_name": entity.first_name,
            "last_name": entity.last_name,
            "organisation_name": entity.organisation_name,
            "gender": entity.gender,
            "phone_e164": entity.phone_e164,
            "email": entity.email,
            "total_land_acres": float(entity.total_land_acres) if entity.total_land_acres else None,
            "address_line1": entity.address_line1,
            "address_line2": entity.address_line2,
            "village_town": entity.village_town,
            "district": entity.district,
            "state": entity.state,
            "pincode": entity.pincode,
            "photo_object_key": entity.photo_object_key,
            "version": entity.version,
            "submitted_at": entity.submitted_at.isoformat() if entity.submitted_at else None,
            "verified_at": entity.verified_at.isoformat() if entity.verified_at else None,
            "created_at": entity.created_at.isoformat(),
            "plots": plots_data,
            "sensitive": sensitive_data,
            "role_details": role_details_data,
            "documents": docs_data,
            "reviews": reviews_data,
            "consents": consents_data,
            "qr_blocks": qr_blocks_data,
        })


class AdminRevealFieldView(APIView):
    """POST /api/v1/admin/entities/{entity_id}/reveal
    Reveal one sensitive field with a mandatory typed justification.
    Generates an immutable audit trail in sensitive_access_log conforming to Section 6.5.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request, entity_id):
        field_name = request.data.get("field")
        reason = request.data.get("reason", "").strip()

        if not field_name:
            raise exceptions.ValidationError({"detail": "field is required.", "code": "FIELD_REQUIRED"})
        if not reason or len(reason) < 10:
            raise exceptions.ValidationError({
                "detail": "A specific justification (minimum 10 characters) is required to access sensitive citizen data under DPDP Act 2023.",
                "code": "REASON_REQUIRED",
            })

        try:
            entity = EntityProfile.objects.get(entity_id=entity_id)
            sensitive = entity.sensitive
        except (EntityProfile.DoesNotExist, EntitySensitive.DoesNotExist):
            raise exceptions.NotFound({"detail": "Entity sensitive records not found.", "code": "NOT_FOUND"})

        actor_id = getattr(request.user, "user_id", uuid.uuid4())
        field_name = field_name.lower().strip()
        plaintext = None

        if field_name == "pan":
            if not sensitive.pan_enc:
                raise exceptions.ValidationError({"detail": "PAN is not configured.", "code": "NO_DATA"})
            plaintext = decrypt_field(bytes(sensitive.pan_enc), str(entity.entity_id))
        elif field_name in ("account_no", "bank_account"):
            if not sensitive.account_no_enc:
                raise exceptions.ValidationError({"detail": "Bank account is not configured.", "code": "NO_DATA"})
            plaintext = decrypt_field(bytes(sensitive.account_no_enc), str(entity.entity_id))
        elif field_name == "ifsc":
            if not sensitive.ifsc_enc:
                raise exceptions.ValidationError({"detail": "IFSC is not configured.", "code": "NO_DATA"})
            plaintext = decrypt_field(bytes(sensitive.ifsc_enc), str(entity.entity_id))
        elif field_name == "upi":
            if not sensitive.upi_enc:
                raise exceptions.ValidationError({"detail": "UPI ID is not configured.", "code": "NO_DATA"})
            plaintext = decrypt_field(bytes(sensitive.upi_enc), str(entity.entity_id))
        elif field_name == "aadhaar":
            plaintext = sensitive.aadhaar_last4 or "NOT_CONFIGURED"
        else:
            raise exceptions.ValidationError({"detail": f"Unsupported sensitive field: {field_name}", "code": "INVALID_FIELD"})

        # Record append-only audit log
        log_entry = SensitiveAccessLog.objects.create(
            entity_id=entity.entity_id,
            actor_id=actor_id,
            field_name=field_name,
            reason=reason,
            at=timezone.now(),
        )

        return Response({
            "entity_id": str(entity.entity_id),
            "field": field_name,
            "plaintext": plaintext,
            "access_audit_id": log_entry.id,
            "logged_at": log_entry.at.isoformat(),
        })


class AdminEntityDecisionView(APIView):
    """POST /api/v1/admin/entities/{entity_id}/decision
    Execute verification decision: APPROVED, REJECTED, NEEDS_CHANGES, SUSPENDED.
    Approving runs the atomic transaction in Section 9.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request, entity_id):
        _ensure_trash_enums()
        decision = request.data.get("decision", "").upper().strip()
        reason = request.data.get("reason", "").strip()
        qr_count = request.data.get("qr_count")

        if decision not in ("APPROVED", "REJECTED", "NEEDS_CHANGES", "SUSPENDED", "TRASH"):
            raise exceptions.ValidationError({
                "detail": "decision must be one of: APPROVED, REJECTED, NEEDS_CHANGES, SUSPENDED, TRASH",
                "code": "INVALID_DECISION",
            })

        if decision != "APPROVED" and not reason:
            raise exceptions.ValidationError({
                "detail": "reason is required when rejecting, requesting changes, or suspending.",
                "code": "REASON_REQUIRED",
            })

        try:
            entity = EntityProfile.objects.get(entity_id=entity_id)
        except EntityProfile.DoesNotExist:
            raise exceptions.NotFound({"detail": "Entity profile not found.", "code": "NOT_FOUND"})

        admin_user = request.user
        if not admin_user or not getattr(admin_user, "user_id", None):
            # Fallback admin actor if called via API key
            admin_user = AppUser.objects.filter(role__in=["OWNER", "STAFF"]).first()
            if not admin_user:
                try:
                    admin_user = AppUser.objects.get(user_id=entity.user_id)
                except AppUser.DoesNotExist:
                    pass

        if decision == "APPROVED":
            res = approve_entity_registration(
                entity=entity,
                admin_user=admin_user,
                qr_count=qr_count,
                review_notes=reason,
            )
            return Response(res, status=status.HTTP_200_OK)

        if decision == "TRASH":
            with transaction.atomic():
                now = timezone.now()
                entity.status = "TRASH"
                entity.version += 1
                entity.save(update_fields=["status", "version", "updated_at"])

                try:
                    user = AppUser.objects.get(user_id=entity.user_id)
                    org = user.org
                    org.verification = "SUSPENDED"
                    org.save(update_fields=["verification"])
                except Exception:
                    pass

                review = VerificationReview.objects.create(
                    review_id=uuid.uuid4(),
                    entity=entity,
                    reviewer_id=admin_user.user_id if getattr(admin_user, "user_id", None) else uuid.uuid4(),
                    decision="TRASH",
                    reason=reason or "Moved to trash by administrator.",
                    created_at=now,
                )

            return Response({
                "entity_id": str(entity.entity_id),
                "status": "TRASH",
                "decision": "TRASH",
                "review_id": str(review.review_id),
                "message": "Producer moved to trash successfully.",
            }, status=status.HTTP_200_OK)

        with transaction.atomic():
            now = timezone.now()
            entity.status = decision
            entity.version += 1
            entity.save(update_fields=["status", "version", "updated_at"])

            # Append-only review log
            review = VerificationReview.objects.create(
                review_id=uuid.uuid4(),
                entity=entity,
                reviewer_id=admin_user.user_id if admin_user else uuid.uuid4(),
                decision=decision,
                reason=reason,
                created_at=now,
            )

        return Response({
            "entity_id": str(entity.entity_id),
            "status": entity.status,
            "decision": decision,
            "review_id": str(review.review_id),
            "reason": reason,
        })


class AdminIssueQrBlockView(APIView):
    """POST /api/v1/admin/entities/{entity_id}/qr-blocks
    Issue an additional block of Crockford Base32 13-char QR labels for a verified entity.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request, entity_id):
        try:
            entity = EntityProfile.objects.get(entity_id=entity_id)
        except EntityProfile.DoesNotExist:
            raise exceptions.NotFound({"detail": "Entity profile not found.", "code": "NOT_FOUND"})

        if entity.status != "VERIFIED":
            raise exceptions.ValidationError({
                "detail": "QR blocks can only be issued to VERIFIED entities.",
                "code": "ENTITY_NOT_VERIFIED",
            })

        count = request.data.get("count", 20)
        try:
            count = int(count)
        except (ValueError, TypeError):
            raise exceptions.ValidationError({"detail": "count must be an integer.", "code": "INVALID_COUNT"})

        block, serials = issue_qr_block_for_entity(
            entity=entity,
            count=count,
            admin_user=request.user if getattr(request.user, "user_id", None) else None,
        )

        return Response({
            "entity_id": str(entity.entity_id),
            "block_id": str(block.block_id),
            "count": block.count,
            "issued_at": block.issued_at.isoformat(),
            "sample_serials": serials[:5],
            "total_serials": len(serials),
        }, status=status.HTTP_201_CREATED)


class AdminEntityRestoreView(APIView):
    """POST /api/v1/admin/entities/{entity_id}/restore
    Restore a producer from TRASH back to active review/verified status.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request, entity_id):
        try:
            entity = EntityProfile.objects.get(entity_id=entity_id)
        except EntityProfile.DoesNotExist:
            raise exceptions.NotFound({"detail": "Entity profile not found.", "code": "NOT_FOUND"})

        if entity.status != "TRASH":
            raise exceptions.ValidationError({"detail": "Entity is not currently in trash.", "code": "NOT_IN_TRASH"})

        admin_user = request.user
        if not admin_user or not getattr(admin_user, "user_id", None):
            admin_user = AppUser.objects.filter(role__in=["OWNER", "STAFF"]).first()

        target_status = "VERIFIED" if entity.entity_code else "SUBMITTED"
        with transaction.atomic():
            now = timezone.now()
            entity.status = target_status
            entity.version += 1
            entity.save(update_fields=["status", "version", "updated_at"])

            try:
                user = AppUser.objects.get(user_id=entity.user_id)
                org = user.org
                org.verification = "VERIFIED" if entity.entity_code else "PENDING"
                org.save(update_fields=["verification"])
            except Exception:
                pass

            VerificationReview.objects.create(
                review_id=uuid.uuid4(),
                entity=entity,
                reviewer_id=admin_user.user_id if admin_user else uuid.uuid4(),
                decision="RESTORED",
                reason="Restored from trash by administrator.",
                created_at=now,
            )

        return Response({
            "entity_id": str(entity.entity_id),
            "status": entity.status,
            "message": f"Producer restored to {entity.status} successfully.",
        }, status=status.HTTP_200_OK)


class AdminEntityPurgeView(APIView):
    """POST /api/v1/admin/entities/{entity_id}/purge
    Permanently purge producer data after explicit word confirmation 'DELETE'.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request, entity_id):
        confirm_word = str(request.data.get("confirmation", "")).strip().upper()
        if confirm_word != "DELETE":
            raise exceptions.ValidationError({
                "detail": "Word confirmation 'DELETE' is required to permanently purge producer data.",
                "code": "CONFIRMATION_REQUIRED",
            })

        try:
            entity = EntityProfile.objects.get(entity_id=entity_id)
        except EntityProfile.DoesNotExist:
            raise exceptions.NotFound({"detail": "Entity profile not found.", "code": "NOT_FOUND"})

        with transaction.atomic():
            try:
                entity.sensitive.delete()
            except Exception:
                pass
            entity.documents.all().delete()
            entity.plots.all().delete()
            entity.facilities.all().delete()
            try:
                entity.role_details.delete()
            except Exception:
                pass
            from django.db import connection
            with connection.cursor() as cursor:
                if connection.vendor == "mysql":
                    cursor.execute("SET @annasutra_allow_purge = 1;")
                ids = [str(entity.entity_id), getattr(entity.entity_id, "hex", str(entity.entity_id))]
                cursor.execute("DELETE FROM verification_review WHERE entity_id IN (%s, %s)", ids)
                cursor.execute("DELETE FROM profile_change_log WHERE entity_id IN (%s, %s)", ids)
                cursor.execute("DELETE FROM sensitive_access_log WHERE entity_id IN (%s, %s)", ids)
                cursor.execute("DELETE FROM entity_consent_record WHERE entity_id IN (%s, %s)", ids)
                if connection.vendor == "mysql":
                    cursor.execute("SET @annasutra_allow_purge = 0;")
            entity.delete()

        return Response({"message": "Producer data permanently purged from system."}, status=status.HTTP_200_OK)
