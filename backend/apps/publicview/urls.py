from django.urls import path
from .views import PublicLotDetailView, public_lot_html_view

urlpatterns = [
    path("lots/<str:code>", PublicLotDetailView.as_view(), name="public_lot_detail"),
    path("view/<str:code>", public_lot_html_view, name="public_lot_html"),
]
