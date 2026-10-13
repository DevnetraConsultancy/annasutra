import base64
import os
import re
import mimetypes
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.permissions import AllowAny

from apps.publicview.models import PublicView
from apps.alerts.models import ScanLog
from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle


def serve_static_asset(request, path: str):
    """Serve static assets with HTTP 206 byte-range streaming for background & promo videos."""
    clean_path = Path(path).as_posix().lstrip("/")
    if ".." in clean_path:
        raise Http404("Invalid path")

    candidates = [
        settings.BASE_DIR.parent / "static" / clean_path,
        settings.BASE_DIR / "staticfiles" / clean_path,
        settings.BASE_DIR / "apps" / "publicview" / "static" / clean_path,
    ]
    file_path = None
    for c in candidates:
        if c.exists() and c.is_file():
            file_path = c
            break

    if not file_path:
        raise Http404(f"Asset not found: {clean_path}")

    file_size = file_path.stat().st_size
    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or "application/octet-stream"

    range_header = request.headers.get("Range", "")
    range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)

    if range_match:
        first_byte = int(range_match.group(1))
        last_byte = int(range_match.group(2)) if range_match.group(2) else file_size - 1
        if first_byte >= file_size:
            return HttpResponse(status=416)
        last_byte = min(last_byte, file_size - 1)
        length = last_byte - first_byte + 1

        def range_iterator(start, length, chunk_size=65536):
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    read_len = min(chunk_size, remaining)
                    data = f.read(read_len)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        resp = StreamingHttpResponse(
            range_iterator(first_byte, length),
            status=206,
            content_type=content_type,
        )
        resp["Content-Range"] = f"bytes {first_byte}-{last_byte}/{file_size}"
        resp["Accept-Ranges"] = "bytes"
        resp["Content-Length"] = str(length)
        resp["Cache-Control"] = "public, max-age=86400"
        return resp

    def file_iterator(chunk_size=65536):
        with open(file_path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data

    resp = StreamingHttpResponse(
        file_iterator(),
        status=200,
        content_type=content_type,
    )
    resp["Accept-Ranges"] = "bytes"
    resp["Content-Length"] = str(file_size)
    resp["Cache-Control"] = "public, max-age=86400"
    return resp


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
        "hero_video_url": "/static/publicview/videos/hero_bg.mp4",
        "promo_video_url": "/static/publicview/videos/annasutra_promo.mp4",
    })


