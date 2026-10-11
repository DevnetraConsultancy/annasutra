"""Identity & Authentication API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


class OtpRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({"status": "accepted"}, status=status.HTTP_202_ACCEPTED)


class OtpVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {
                "access_token": "stub_access_token",
                "refresh_token": "stub_refresh_token",
                "expires_in": 900,
                "org_verification": "PENDING",
            },
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {
                "access_token": "stub_new_access_token",
                "refresh_token": "stub_new_refresh_token",
                "expires_in": 900,
                "org_verification": "VERIFIED",
            },
            status=status.HTTP_200_OK,
        )


class PasskeyRegisterOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"options": {}}, status=status.HTTP_200_OK)


class PasskeyRegisterVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasskeyLoginOptionsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({"options": {}}, status=status.HTTP_200_OK)


class PasskeyLoginVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {
                "access_token": "stub_access_token",
                "refresh_token": "stub_refresh_token",
                "expires_in": 900,
                "org_verification": "VERIFIED",
            },
            status=status.HTTP_200_OK,
        )


class DeviceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([], status=status.HTTP_200_OK)

    def post(self, request):
        return Response(
            {
                "device_id": "00000000-0000-0000-0000-000000000000",
                "label": request.data.get("label", "primary"),
                "created_at": "2026-10-11T00:00:00Z",
                "revoked_at": None,
            },
            status=status.HTTP_201_CREATED,
        )


class DeviceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, device_id):
        return Response(status=status.HTTP_204_NO_CONTENT)
