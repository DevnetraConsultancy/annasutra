"""Custody and Handover API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.identity.authentication import IsVerifiedOrg
from apps.custody.services.handover_service import (
    receive_handover,
    dispute_handover,
    resolve_handover,
)


def handover_response(handover) -> dict:
    return {
        "handover_id": str(handover.handover_id),
        "lot_code": handover.lot.public_code,
        "state": handover.state,
        "declared_qty_kg": float(handover.declared_qty_kg),
        "received_qty_kg": float(handover.received_qty_kg) if handover.received_qty_kg is not None else None,
        "expires_at": handover.expires_at.isoformat(),
    }


class HandoverReceiveView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, handover_id):
        handover = receive_handover(request.user, handover_id, request.data)
        return Response(handover_response(handover), status=status.HTTP_200_OK)


class HandoverDisputeView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, handover_id):
        handover = dispute_handover(request.user, handover_id, request.data)
        return Response(handover_response(handover), status=status.HTTP_200_OK)


class HandoverResolveView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, handover_id):
        handover = resolve_handover(request.user, handover_id, request.data)
        return Response(handover_response(handover), status=status.HTTP_200_OK)
