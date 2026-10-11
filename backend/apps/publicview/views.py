"""Public View API and HTML views conforming to api/openapi.yaml."""
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.permissions import AllowAny

from apps.publicview.models import PublicView
from apps.alerts.models import ScanLog


class PublicLotDetailView(APIView):
    """Consumer-visible JSON summary selecting exclusively from the public_view table."""

    permission_classes = [AllowAny]

    def get(self, request, code):
        public_view = PublicView.objects.filter(public_code=code).first()
        result_str = "FOUND" if public_view else "NOT_FOUND"

        # Log public scan
        ScanLog.objects.create(
            serial=code,
            result=result_str,
        )

        if not public_view:
            raise exceptions.NotFound(
                {"detail": "Lot record not found.", "code": "NOT_FOUND"}
            )

        # Update scan_count in response payload dynamically
        payload = dict(public_view.payload)
        payload["scan_count"] = ScanLog.objects.filter(serial=code).count()

        return Response(payload, status=status.HTTP_200_OK)


def public_lot_html_view(request, code: str):
    """Server-rendered consumer public page with zero JavaScript framework."""
    public_view = PublicView.objects.filter(public_code=code).first()
    result_str = "FOUND" if public_view else "NOT_FOUND"

    ScanLog.objects.create(
        serial=code,
        result=result_str,
    )

    if not public_view:
        return render(request, "publicview/lot_not_found.html", {"code": code}, status=404)

    payload = dict(public_view.payload)
    payload["scan_count"] = ScanLog.objects.filter(serial=code).count()

    return render(request, "publicview/lot_summary.html", {"lot": payload})
