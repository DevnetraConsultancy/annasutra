import base64
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.permissions import AllowAny

from apps.publicview.models import PublicView
from apps.alerts.models import ScanLog
from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle


def _get_logo_data_uri(relative_path: str) -> str:
    """Resolve static logo file to an infallible inline Base64 data URI."""
    candidates = [
        settings.BASE_DIR.parent / "static" / relative_path,
        settings.BASE_DIR / "apps" / "publicview" / "static" / relative_path,
        settings.BASE_DIR / "staticfiles" / relative_path,
    ]
    for p in candidates:
        if p.exists():
            try:
                data = base64.b64encode(p.read_bytes()).decode("ascii")
                return f"data:image/png;base64,{data}"
            except Exception:
                pass
    return f"/static/{relative_path}"


ANNASUTRA_LOGO_URI = _get_logo_data_uri("publicview/images/annasutra_logo.png")
CDAC_LOGO_URI = _get_logo_data_uri("publicview/images/cdac_logo.png")


class PublicLotDetailView(APIView):
    """Consumer-visible JSON summary selecting exclusively from the public_view table."""

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, ScopedRateThrottle]
    throttle_scope = "public_scan"

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

    user_lang = request.COOKIES.get("annasutra_lang", "en")
    if user_lang not in ["en", "hi", "bn"]:
        user_lang = "en"

    base_context = {
        "user_lang": user_lang,
        "brand_logo": ANNASUTRA_LOGO_URI,
        "cdac_logo": CDAC_LOGO_URI,
    }

    if not public_view:
        context = {**base_context, "code": code}
        return render(request, "publicview/lot_not_found.html", context, status=404)

    payload = dict(public_view.payload)
    payload["scan_count"] = ScanLog.objects.filter(serial=code).count()

    context = {**base_context, "lot": payload}
    return render(request, "publicview/lot_summary.html", context)


def landing_page_view(request):
    """AnnaSutra public portal landing page."""
    query_code = request.GET.get("code", "").strip()
    if query_code:
        from django.shortcuts import redirect
        return redirect("public_lot_html_canonical", code=query_code)
    user_lang = request.COOKIES.get("annasutra_lang", "en")
    if user_lang not in ["en", "hi", "bn"]:
        user_lang = "en"
    return render(request, "publicview/landing.html", {
        "user_lang": user_lang,
        "brand_logo": ANNASUTRA_LOGO_URI,
        "cdac_logo": CDAC_LOGO_URI,
    })

