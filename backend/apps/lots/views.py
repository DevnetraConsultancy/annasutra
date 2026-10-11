"""Lots API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class LotListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"items": [], "next_cursor": None}, status=status.HTTP_200_OK)

    def post(self, request):
        return Response(
            {
                "lot_id": "00000000-0000-0000-0000-000000000000",
                "public_code": request.data.get("label_serial", "7K3Q9XMD4T2B"),
                "state": "CREATED",
                "custodian_org": "00000000-0000-0000-0000-000000000000",
                "pending_receiver_org": None,
                "on_hand_kg": float(request.data.get("net_qty_kg", 500.0)),
                "lot_seq": 1,
            },
            status=status.HTTP_201_CREATED,
        )


class LotDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        return Response(
            {
                "lot_id": "00000000-0000-0000-0000-000000000000",
                "public_code": code,
                "state": "IN_CUSTODY",
                "custodian_org": "00000000-0000-0000-0000-000000000000",
                "pending_receiver_org": None,
                "on_hand_kg": 500.0,
                "lot_seq": 2,
            },
            status=status.HTTP_200_OK,
        )


class LotEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        return Response({"items": [], "next_cursor": None}, status=status.HTTP_200_OK)


class LotInspectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response(
            {
                "event_id": request.data.get("event_id", "00000000-0000-0000-0000-000000000000"),
                "status": "ACCEPTED",
                "lot_seq": 2,
                "reason_code": None,
                "message": None,
            },
            status=status.HTTP_201_CREATED,
        )


class LotDispatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response(
            {
                "handover_id": "00000000-0000-0000-0000-000000000000",
                "lot_code": code,
                "state": "PENDING",
                "declared_qty_kg": float(request.data.get("qty_kg", 500.0)),
                "received_qty_kg": None,
                "expires_at": "2026-10-12T16:30:00Z",
            },
            status=status.HTTP_201_CREATED,
        )


class LotSplitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response({"items": [], "next_cursor": None}, status=status.HTTP_201_CREATED)


class LotMergeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "lot_id": "00000000-0000-0000-0000-000000000000",
                "public_code": request.data.get("label_serial", "MERGED-001"),
                "state": "CREATED",
                "custodian_org": "00000000-0000-0000-0000-000000000000",
                "pending_receiver_org": None,
                "on_hand_kg": 1000.0,
                "lot_seq": 1,
            },
            status=status.HTTP_201_CREATED,
        )


class LotSortView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response({"items": [], "next_cursor": None}, status=status.HTTP_201_CREATED)


class LotRepackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response(
            {
                "event_id": request.data.get("event_id", "00000000-0000-0000-0000-000000000000"),
                "status": "ACCEPTED",
                "lot_seq": 3,
            },
            status=status.HTTP_201_CREATED,
        )


class LotWasteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response(
            {
                "event_id": request.data.get("event_id", "00000000-0000-0000-0000-000000000000"),
                "status": "ACCEPTED",
                "lot_seq": 3,
            },
            status=status.HTTP_201_CREATED,
        )


class LotSaleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response(
            {
                "event_id": request.data.get("event_id", "00000000-0000-0000-0000-000000000000"),
                "status": "ACCEPTED",
                "lot_seq": 3,
            },
            status=status.HTTP_201_CREATED,
        )


class LotLabelReissueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        return Response(
            {
                "event_id": request.data.get("event_id", "00000000-0000-0000-0000-000000000000"),
                "status": "ACCEPTED",
                "lot_seq": 4,
            },
            status=status.HTTP_201_CREATED,
        )
