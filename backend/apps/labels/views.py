"""Labels API views conforming to api/openapi.yaml."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class LabelBlockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = request.data.get("count", 10)
        serials = [f"STUB-{i:04d}" for i in range(count)]
        return Response(
            {
                "block_id": "00000000-0000-0000-0000-000000000000",
                "serials": serials,
            },
            status=status.HTTP_201_CREATED,
        )
