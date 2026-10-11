"""Organisations and Partners API views conforming to api/openapi.yaml."""

import uuid

from django.db import models, transaction
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import ConsentRecord
from .models import Facility, FarmerProfile, Organisation, PartnerLink


class OrgRegisterView(APIView):
    """Register or complete business/farmer profile."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        name = data.get("name")
        org_type = data.get("org_type")
        consent_notice_version = data.get("consent_notice_version")

        if not name or not org_type or not consent_notice_version:
            raise exceptions.ValidationError(
                {
                    "detail": "name, org_type, and consent_notice_version are required.",
                    "code": "FIELD_REQUIRED",
                }
            )

        valid_types = {"FARMER", "AGGREGATOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER", "LAB", "OPERATOR"}
        if org_type not in valid_types:
            raise exceptions.ValidationError(
                {"detail": f"org_type must be one of {sorted(valid_types)}", "code": "INVALID_ORG_TYPE"}
            )

        with transaction.atomic():
            user = request.user
            org = getattr(user, "org", None)
            if org:
                org.name = name
                org.org_type = org_type
                org.fssai_no = data.get("fssai_no")
                org.save(update_fields=["name", "org_type", "fssai_no"])
            else:
                org = Organisation.objects.create(
                    org_id=uuid.uuid4(),
                    name=name,
                    org_type=org_type,
                    fssai_no=data.get("fssai_no"),
                    verification="PENDING",
                )
                user.org = org
                user.role = "OWNER"
                user.save(update_fields=["org", "role"])

            # Ensure default facility exists
            facility_type = "FARM" if org_type == "FARMER" else "WAREHOUSE"
            Facility.objects.get_or_create(
                org=org,
                name=f"{name} Primary Site",
                defaults={"facility_type": facility_type},
            )

            # Ensure farmer profile if type is FARMER
            if org_type == "FARMER":
                FarmerProfile.objects.get_or_create(
                    farmer_org=org,
                    defaults={"registered_by_user": user},
                )

            # Record user consent
            ConsentRecord.objects.create(
                consent_id=uuid.uuid4(),
                user=user,
                notice_version=consent_notice_version,
                language=data.get("consent_language", "en"),
                method="SELF",
            )

        return Response(
            {
                "org_id": str(org.org_id),
                "name": org.name,
                "org_type": org.org_type,
                "verification": org.verification,
            },
            status=status.HTTP_201_CREATED,
        )


class PartnerListView(APIView):
    """List counterparty partner organisations."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_org = request.user.org
        if not user_org:
            return Response([], status=status.HTTP_200_OK)

        links = PartnerLink.objects.filter(
            models.Q(org_a=user_org) | models.Q(org_b=user_org)
        ).select_related("org_a", "org_b")

        results = []
        for link in links:
            partner = link.org_b if link.org_a_id == user_org.org_id else link.org_a
            results.append(
                {
                    "org_id": str(partner.org_id),
                    "name": partner.name,
                    "status": link.status,
                }
            )

        return Response(results, status=status.HTTP_200_OK)


class PartnerInviteView(APIView):
    """Invite a partner organisation to link supply chains."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_org_id = request.data.get("to_org_id")
        if not to_org_id:
            raise exceptions.ValidationError(
                {"detail": "to_org_id is required.", "code": "FIELD_REQUIRED"}
            )

        user_org = request.user.org
        if str(user_org.org_id) == str(to_org_id):
            raise exceptions.ValidationError(
                {"detail": "Cannot invite your own organisation.", "code": "CANNOT_INVITE_SELF"}
            )

        try:
            target_org = Organisation.objects.get(org_id=to_org_id)
        except Organisation.DoesNotExist:
            raise exceptions.NotFound(
                {"detail": "Target organisation not found.", "code": "ORG_NOT_FOUND"}
            )

        # Canonical ordering to avoid duplicate reversed composite keys
        id_a, id_b = sorted([user_org.org_id, target_org.org_id])
        org_a = user_org if id_a == user_org.org_id else target_org
        org_b = target_org if id_b == target_org.org_id else user_org

        link, _ = PartnerLink.objects.update_or_create(
            org_a=org_a,
            org_b=org_b,
            defaults={
                "status": "INVITED",
                "invited_by": request.user,
            },
        )

        return Response(
            {
                "org_id": str(target_org.org_id),
                "name": target_org.name,
                "status": link.status,
            },
            status=status.HTTP_201_CREATED,
        )


class PartnerAcceptView(APIView):
    """Accept a pending counterparty partner invitation."""

    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        user_org = request.user.org

        try:
            partner_org = Organisation.objects.get(org_id=org_id)
        except Organisation.DoesNotExist:
            raise exceptions.NotFound(
                {"detail": "Organisation not found.", "code": "ORG_NOT_FOUND"}
            )

        id_a, id_b = sorted([user_org.org_id, partner_org.org_id])
        link = PartnerLink.objects.filter(org_a_id=id_a, org_b_id=id_b).first()

        if not link:
            raise exceptions.NotFound(
                {"detail": "No partnership invitation found.", "code": "INVITATION_NOT_FOUND"}
            )

        if link.status != "INVITED":
            raise exceptions.ValidationError(
                {"detail": f"Partnership is already {link.status}.", "code": "ALREADY_PROCESSED"}
            )

        # Ensure the caller was the recipient (not the one who invited)
        if link.invited_by_id and link.invited_by_id == request.user.user_id:
            raise exceptions.ValidationError(
                {"detail": "Cannot accept an invitation you sent.", "code": "CANNOT_ACCEPT_OWN_INVITE"}
            )

        link.status = "ACCEPTED"
        link.save(update_fields=["status"])

        return Response(
            {
                "org_id": str(partner_org.org_id),
                "name": partner_org.name,
                "status": link.status,
            },
            status=status.HTTP_200_OK,
        )
