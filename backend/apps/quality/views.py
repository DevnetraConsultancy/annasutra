"""Quality and Evidence API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class EvidenceUploadRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "evidence_id": "00000000-0000-0000-0000-000000000000",
                "upload_url": "https://storage.example.in/upload-signed-url-stub",
                "expires_at": "2026-10-11T23:59:59Z",
            },
            status=status.HTTP_201_CREATED,
        )
