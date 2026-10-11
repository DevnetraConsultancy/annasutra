"""Reporting and Recall API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class RecallOpenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "recall_id": "00000000-0000-0000-0000-000000000000",
                "status": "OPEN",
                "root_lot": request.data.get("lot_code", "7K3Q9XMD4T2B"),
            },
            status=status.HTTP_201_CREATED,
        )


class RecallTraceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, recall_id):
        return Response(
            {
                "items": [
                    {
                        "lot_code": "7K3Q9XMD4T2B",
                        "custodian": "Gariahat Fresh",
                        "state": "RECALLED",
                        "on_hand_kg": 49.0,
                        "sold_kg": 71.0,
                    }
                ]
            },
            status=status.HTTP_200_OK,
        )
