from django.urls import path
from .views import PublicLotDetailView, public_lot_html_view, PublicScanPingView

urlpatterns = [
    path("lots/<str:code>", PublicLotDetailView.as_view(), name="public_lot_detail"),
    path("lots/<str:code>/", PublicLotDetailView.as_view(), name="public_lot_detail_slash"),
    path("lots/<str:code>/scan-ping", PublicScanPingView.as_view(), name="public_lot_scan_ping"),
    path("lots/<str:code>/scan-ping/", PublicScanPingView.as_view(), name="public_lot_scan_ping_slash"),
    path("view/<str:code>", public_lot_html_view, name="public_lot_html"),
    path("view/<str:code>/", public_lot_html_view, name="public_lot_html_slash"),
]
