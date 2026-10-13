from django.urls import path
from .views import RecallOpenView, RecallTraceView

urlpatterns = [
    path("", RecallOpenView.as_view(), name="recall_open"),
    path("<uuid:recall_id>/trace", RecallTraceView.as_view(), name="recall_trace"),
]

