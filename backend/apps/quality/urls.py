from django.urls import path
from .views import EvidenceUploadRequestView

urlpatterns = [
    path("uploads", EvidenceUploadRequestView.as_view(), name="evidence_uploads"),
]
