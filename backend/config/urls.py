"""AnnaSutra URL Configuration."""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """Liveness and readiness health check probe."""
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse(
        {
            "status": "healthy" if db_ok else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
        },
        status=status_code,
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health_check, name="health_root"),
    path("health/", health_check, name="health_slash"),
    # API v1 routes conforming to api/openapi.yaml
    path("v1/auth/", include("apps.identity.urls")),
    path("v1/organisations", include("apps.organisations.org_urls")),
    path("v1/partners", include("apps.organisations.partner_urls")),
    path("v1/labels/", include("apps.labels.urls")),
    path("v1/lots", include("apps.lots.urls")),
    path("v1/handovers/", include("apps.custody.urls")),
    path("v1/evidence/", include("apps.quality.urls")),
    path("v1/events/", include("apps.ledger.event_urls")),
    path("v1/sync/", include("apps.ledger.sync_urls")),
    path("v1/recalls", include("apps.reporting.urls")),
    path("v1/public/", include("apps.publicview.urls")),
]
