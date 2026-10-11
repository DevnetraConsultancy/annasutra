"""Reporting and Recall API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.identity.authentication import IsVerifiedOrg
from .services.recall_service import open_recall, trace_recall


class RecallOpenView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request):
        result = open_recall(request.user, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class RecallTraceView(APIView):
    permission_classes = [IsVerifiedOrg]

    def get(self, request, recall_id):
        result = trace_recall(request.user, recall_id)
        return Response(result, status=status.HTTP_200_OK)
