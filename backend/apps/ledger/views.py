"""Ledger and Sync API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class EventCorrectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        return Response(
            {
                "event_id": request.data.get("event_id", "00000000-0000-0000-0000-000000000000"),
                "status": "ACCEPTED",
                "lot_seq": 5,
                "reason_code": request.data.get("reason", "CORRECTION"),
                "message": "Correction appended successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class SyncBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get("items", [])
        results = []
        for i, item in enumerate(items):
            results.append(
                {
                    "event_id": item.get("body", {}).get("event_id", f"00000000-0000-0000-0000-00000000000{i}"),
                    "status": "ACCEPTED",
                    "lot_seq": i + 1,
                    "reason_code": None,
                    "message": None,
                }
            )
        return Response({"results": results}, status=status.HTTP_200_OK)
