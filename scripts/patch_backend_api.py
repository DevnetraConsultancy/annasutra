"""Script to update backend lots views and admin views for rich harvest lot management and trash features."""

import os
import re

# 1. Update backend/apps/identity/views_admin.py
with open("backend/apps/identity/views_admin.py", "r", encoding="utf-8") as f:
    admin_views = f.read()

# Update get() in AdminReviewQueueView to handle TRASH
old_queue_get = """        if status_filter != "ALL":
            qs = qs.filter(status=status_filter)"""

new_queue_get = """        if status_filter == "TRASH":
            qs = qs.filter(status="TRASH")
        elif status_filter == "ALL":
            qs = qs.exclude(status="TRASH")
        else:
            qs = qs.filter(status=status_filter)"""

if old_queue_get in admin_views:
    admin_views = admin_views.replace(old_queue_get, new_queue_get)

# Update AdminEntityDecisionView to accept TRASH
old_decision_check = """        if decision not in ("APPROVED", "REJECTED", "NEEDS_CHANGES", "SUSPENDED"):
            raise exceptions.ValidationError({
                "detail": "decision must be one of: APPROVED, REJECTED, NEEDS_CHANGES, SUSPENDED",
                "code": "INVALID_DECISION",
            })"""

new_decision_check = """        if decision not in ("APPROVED", "REJECTED", "NEEDS_CHANGES", "SUSPENDED", "TRASH"):
            raise exceptions.ValidationError({
                "detail": "decision must be one of: APPROVED, REJECTED, NEEDS_CHANGES, SUSPENDED, TRASH",
                "code": "INVALID_DECISION",
            })"""

if old_decision_check in admin_views:
    admin_views = admin_views.replace(old_decision_check, new_decision_check)

# Add TRASH branch in AdminEntityDecisionView
old_approved_branch = """        if decision == "APPROVED":
            res = approve_entity_registration(
                entity=entity,
                admin_user=admin_user,
                qr_count=qr_count,
                review_notes=reason,
            )
            return Response(res, status=status.HTTP_200_OK)"""

new_approved_branch = """        if decision == "APPROVED":
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
            }, status=status.HTTP_200_OK)"""

if old_approved_branch in admin_views:
    admin_views = admin_views.replace(old_approved_branch, new_approved_branch)

# Add AdminEntityRestoreView and AdminEntityPurgeView at the end of views_admin.py
extra_admin_views = """

class AdminEntityRestoreView(APIView):
    \"\"\"POST /api/v1/admin/entities/{entity_id}/restore
    Restore a producer from TRASH back to active review/verified status.
    \"\"\"

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
    \"\"\"POST /api/v1/admin/entities/{entity_id}/purge
    Permanently purge producer data after explicit word confirmation 'DELETE'.
    \"\"\"

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
            try:
                entity.role_details.delete()
            except Exception:
                pass
            entity.delete()

        return Response({"message": "Producer data permanently purged from system."}, status=status.HTTP_200_OK)
"""

if "class AdminEntityRestoreView" not in admin_views:
    admin_views += extra_admin_views

with open("backend/apps/identity/views_admin.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(admin_views)

print("Updated views_admin.py")

# 2. Update backend/apps/identity/urls_admin.py
with open("backend/apps/identity/urls_admin.py", "r", encoding="utf-8") as f:
    admin_urls = f.read()

if "AdminEntityRestoreView" not in admin_urls:
    admin_urls = admin_urls.replace(
        "    AdminIssueQrBlockView,\n)",
        "    AdminIssueQrBlockView,\n    AdminEntityRestoreView,\n    AdminEntityPurgeView,\n)"
    )
    admin_urls = admin_urls.replace(
        "    path(\"entities/<uuid:entity_id>/qr-blocks/\", AdminIssueQrBlockView.as_view(), name=\"admin_issue_qr_block_slash\"),",
        "    path(\"entities/<uuid:entity_id>/qr-blocks/\", AdminIssueQrBlockView.as_view(), name=\"admin_issue_qr_block_slash\"),\n"
        "    path(\"entities/<uuid:entity_id>/restore\", AdminEntityRestoreView.as_view(), name=\"admin_entity_restore\"),\n"
        "    path(\"entities/<uuid:entity_id>/restore/\", AdminEntityRestoreView.as_view(), name=\"admin_entity_restore_slash\"),\n"
        "    path(\"entities/<uuid:entity_id>/purge\", AdminEntityPurgeView.as_view(), name=\"admin_entity_purge\"),\n"
        "    path(\"entities/<uuid:entity_id>/purge/\", AdminEntityPurgeView.as_view(), name=\"admin_entity_purge_slash\"),"
    )

with open("backend/apps/identity/urls_admin.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(admin_urls)

print("Updated urls_admin.py")
