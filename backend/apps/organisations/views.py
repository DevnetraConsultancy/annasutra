"""Organisations and Partners API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class OrgRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "org_id": "00000000-0000-0000-0000-000000000000",
                "name": request.data.get("name", "Org Name"),
                "org_type": request.data.get("org_type", "FARMER"),
                "verification": "PENDING",
            },
            status=status.HTTP_201_CREATED,
        )


class PartnerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([], status=status.HTTP_200_OK)


class PartnerInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "org_id": request.data.get("to_org_id", "00000000-0000-0000-0000-000000000000"),
                "name": "Invited Partner",
                "status": "INVITED",
            },
            status=status.HTTP_201_CREATED,
        )


class PartnerAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        return Response(
            {
                "org_id": str(org_id),
                "name": "Accepted Partner",
                "status": "ACCEPTED",
            },
            status=status.HTTP_200_OK,
        )
