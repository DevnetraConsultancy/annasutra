from django.urls import path
from .views import PublicLotDetailView

urlpatterns = [
    path("lots/<str:code>", PublicLotDetailView.as_view(), name="public_lot_detail"),
]
