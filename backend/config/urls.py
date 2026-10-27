"""AnnaSutra URL Configuration."""
from django.contrib import admin
from django.urls import path, re_path, include
from django.http import JsonResponse
from django.db import connection
from apps.publicview.views import landing_page_view, public_lot_html_view, serve_static_asset, download_apk_view


def health_check(request):
    """Liveness and readiness health check probe."""
    db_ok = True
    err_msg = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_ok = False
        err_msg = str(e)

    status_code = 200 if db_ok else 503
    res_payload = {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
    }
    if err_msg:
        res_payload["error"] = err_msg

    return JsonResponse(res_payload, status=status_code)


urlpatterns = [
    path("favicon.ico", serve_static_asset, {"path": "publicview/images/favicon.ico"}, name="favicon"),
    path("", landing_page_view, name="landing_page"),
    path("admin/", admin.site.urls),
    path("health", health_check, name="health_root"),
    path("health/", health_check, name="health_slash"),
    path("api/health", health_check, name="api_health_root"),
    path("api/health/", health_check, name="api_health_slash"),
    path("v1/health", health_check, name="v1_health_root"),
    path("v1/health/", health_check, name="v1_health_slash"),
    path("api/v1/health", health_check, name="api_v1_health_root"),
    path("api/v1/health/", health_check, name="api_v1_health_slash"),
    path("public/lot/<str:code>/", public_lot_html_view, name="public_lot_html_canonical"),
    path("public/lot/<str:code>", public_lot_html_view, name="public_lot_html_canonical_noslash"),
    path("q/<str:code>", public_lot_html_view, name="qr_short_link"),
    path("q/<str:code>/", public_lot_html_view, name="qr_short_link_slash"),
    path("l/<str:code>", public_lot_html_view, name="lot_short_link"),
    path("l/<str:code>/", public_lot_html_view, name="lot_short_link_slash"),
    path("download/apk", download_apk_view, name="download_apk"),
    path("download/apk/", download_apk_view, name="download_apk_slash"),
    path("download/android", download_apk_view, name="download_android"),
    path("download/android/", download_apk_view, name="download_android_slash"),

    # API v1 routes conforming to api/openapi.yaml (supports both /api/v1/ and /v1/)
    path("api/v1/auth/", include("apps.identity.urls")),
    path("api/v1/auth", include("apps.identity.urls")),
    path("v1/auth/", include("apps.identity.urls")),
    path("v1/auth", include("apps.identity.urls")),
    path("api/v1/me/", include("apps.identity.urls_me")),
    path("api/v1/me", include("apps.identity.urls_me")),
    path("v1/me/", include("apps.identity.urls_me")),
    path("v1/me", include("apps.identity.urls_me")),
    path("api/v1/admin/", include("apps.identity.urls_admin")),
    path("api/v1/admin", include("apps.identity.urls_admin")),
    path("v1/admin/", include("apps.identity.urls_admin")),
    path("v1/admin", include("apps.identity.urls_admin")),
    path("api/v1/organisations/", include("apps.organisations.org_urls")),
    path("api/v1/organisations", include("apps.organisations.org_urls")),
    path("v1/organisations/", include("apps.organisations.org_urls")),
    path("v1/organisations", include("apps.organisations.org_urls")),
    path("api/v1/partners/", include("apps.organisations.partner_urls")),
    path("api/v1/partners", include("apps.organisations.partner_urls")),
    path("v1/partners/", include("apps.organisations.partner_urls")),
    path("v1/partners", include("apps.organisations.partner_urls")),
    path("api/v1/labels/", include("apps.labels.urls")),
    path("api/v1/labels", include("apps.labels.urls")),
    path("v1/labels/", include("apps.labels.urls")),
    path("v1/labels", include("apps.labels.urls")),
    path("api/v1/lots/", include("apps.lots.urls")),
    path("api/v1/lots", include("apps.lots.urls")),
    path("v1/lots/", include("apps.lots.urls")),
    path("v1/lots", include("apps.lots.urls")),
    path("api/v1/handovers/", include("apps.custody.urls")),
    path("api/v1/handovers", include("apps.custody.urls")),
    path("v1/handovers/", include("apps.custody.urls")),
    path("v1/handovers", include("apps.custody.urls")),
    path("api/v1/evidence/", include("apps.quality.urls")),
    path("api/v1/evidence", include("apps.quality.urls")),
    path("v1/evidence/", include("apps.quality.urls")),
    path("v1/evidence", include("apps.quality.urls")),
    path("api/v1/events/", include("apps.ledger.event_urls")),
    path("api/v1/events", include("apps.ledger.event_urls")),
    path("v1/events/", include("apps.ledger.event_urls")),
    path("v1/events", include("apps.ledger.event_urls")),
    path("api/v1/sync/", include("apps.ledger.sync_urls")),
    path("api/v1/sync", include("apps.ledger.sync_urls")),
    path("v1/sync/", include("apps.ledger.sync_urls")),
    path("v1/sync", include("apps.ledger.sync_urls")),
    path("api/v1/recalls/", include("apps.reporting.urls")),
    path("api/v1/recalls", include("apps.reporting.urls")),
    path("v1/recalls/", include("apps.reporting.urls")),
    path("v1/recalls", include("apps.reporting.urls")),

    path("api/v1/public/", include("apps.publicview.urls")),
    path("api/v1/public", include("apps.publicview.urls")),
    path("v1/public/", include("apps.publicview.urls")),
    path("v1/public", include("apps.publicview.urls")),
    path("L/<str:code>", include("apps.publicview.short_urls")),
    re_path(r"^static/(?P<path>.*)$", serve_static_asset, name="static_asset"),
    re_path(r"^media/(?P<path>.*)$", serve_static_asset, name="media_asset"),
]

