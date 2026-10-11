"""Public View API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class PublicLotDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code):
        return Response(
            {
                "code": code,
                "product": "Tomato (hybrid)",
                "harvest_date": "2026-10-06",
                "region": "Purba Bardhaman, West Bengal",
                "stages_confirmed": 5,
                "quality_checks": 3,
                "certificates": [],
                "scan_count": 12,
                "gaps_flagged": False,
                "disclaimer": (
                    "This record is based on information entered by supply-chain participants. "
                    "It does not prove the contents of this package."
                ),
            },
            status=status.HTTP_200_OK,
        )
