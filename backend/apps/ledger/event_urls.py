from django.urls import path
from .views import EventCorrectionView

urlpatterns = [
    path("<uuid:event_id>/corrections", EventCorrectionView.as_view(), name="event_corrections"),
]
