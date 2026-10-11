"""Labels API views conforming to api/openapi.yaml."""

import secrets
import uuid

from django.db import transaction
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.authentication import IsVerifiedOrg
from .models import QrBlock, QrLabel

# Crockford Base32 alphabet (omits I, L, O, U to prevent visual confusion and offensive words)
CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def generate_crockford_serial(length: int = 12) -> str:
    """Generate unguessable 12-character Crockford Base32 serial code."""
    return "".join(secrets.choice(CROCKFORD_ALPHABET) for _ in range(length))


class LabelBlockView(APIView):
    """Allocate a block of unguessable physical QR label serials."""

    permission_classes = [IsVerifiedOrg]

    def post(self, request):
        count = request.data.get("count")
        if count is None:
            raise exceptions.ValidationError({"detail": "count is required.", "code": "FIELD_REQUIRED"})

        try:
            count = int(count)
        except (ValueError, TypeError):
            raise exceptions.ValidationError({"detail": "count must be an integer.", "code": "INVALID_COUNT"})

        if count < 1 or count > 500:
            raise exceptions.ValidationError(
                {"detail": "count must be between 1 and 500.", "code": "COUNT_OUT_OF_RANGE"}
            )

        user_org = request.user.org
        serials = set()
        # Generate unguessable collision-free serials
        while len(serials) < count:
            s = generate_crockford_serial(12)
            if not QrLabel.objects.filter(serial=s).exists():
                serials.add(s)

        serial_list = list(serials)

        with transaction.atomic():
            block = QrBlock.objects.create(
                block_id=uuid.uuid4(),
                issued_to_org=user_org,
                issued_by=request.user,
                count=count,
            )
            labels_to_create = [
                QrLabel(
                    serial=s,
                    block=block,
                    issued_to_org=user_org,
                    status="ISSUED",
                )
                for s in serial_list
            ]
            QrLabel.objects.bulk_create(labels_to_create)

        return Response(
            {
                "block_id": str(block.block_id),
                "serials": serial_list,
            },
            status=status.HTTP_201_CREATED,
        )
