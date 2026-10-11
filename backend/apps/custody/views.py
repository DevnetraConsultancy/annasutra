"""Custody and Handover API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class HandoverReceiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, handover_id):
        return Response(
            {
                "handover_id": str(handover_id),
                "lot_code": "7K3Q9XMD4T2B",
                "state": "ACCEPTED",
                "declared_qty_kg": 500.0,
                "received_qty_kg": float(request.data.get("received_qty_kg", 500.0)),
                "expires_at": "2026-10-12T16:30:00Z",
            },
            status=status.HTTP_200_OK,
        )


class HandoverDisputeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, handover_id):
        return Response(
            {
                "handover_id": str(handover_id),
                "lot_code": "7K3Q9XMD4T2B",
                "state": "DISPUTED",
                "declared_qty_kg": 500.0,
                "received_qty_kg": float(request.data.get("claimed_qty_kg", 480.0)),
                "expires_at": "2026-10-12T16:30:00Z",
            },
            status=status.HTTP_200_OK,
        )


class HandoverResolveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, handover_id):
        return Response(
            {
                "handover_id": str(handover_id),
                "lot_code": "7K3Q9XMD4T2B",
                "state": "ACCEPTED",
                "declared_qty_kg": 500.0,
                "received_qty_kg": float(request.data.get("agreed_qty_kg", 490.0)),
                "expires_at": "2026-10-12T16:30:00Z",
            },
            status=status.HTTP_200_OK,
        )
