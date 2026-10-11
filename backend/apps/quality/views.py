from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.identity.authentication import IsVerifiedOrg
from .services.quality_service import request_evidence_upload


class EvidenceUploadRequestView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request):
        result = request_evidence_upload(request.user, request.data)
        return Response(result, status=status.HTTP_201_CREATED)
