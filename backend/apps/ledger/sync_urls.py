from django.urls import path
from .views import SyncBatchView

urlpatterns = [
    path("events", SyncBatchView.as_view(), name="sync_events"),
]
