"""URL routing for /me and /me/profile endpoints."""

from django.urls import path
from .views_registration import (
    MyProfileView,
    SubmitProfileView,
    MySensitiveView,
    MyPlotsView,
    UploadPhotoView,
    UploadDocumentView,
    RecordConsentView,
    MyQrBlocksView,
    MyQrBlockSheetPdfView,
    MyRoleStatsView,
)

urlpatterns = [
    path("", MyProfileView.as_view(), name="me_root"),
    path("profile", MyProfileView.as_view(), name="me_profile"),
    path("profile/", MyProfileView.as_view(), name="me_profile_slash"),
    path("profile/submit", SubmitProfileView.as_view(), name="me_profile_submit"),
    path("profile/submit/", SubmitProfileView.as_view(), name="me_profile_submit_slash"),
    path("sensitive", MySensitiveView.as_view(), name="me_sensitive"),
    path("sensitive/", MySensitiveView.as_view(), name="me_sensitive_slash"),
    path("plots", MyPlotsView.as_view(), name="me_plots"),
    path("plots/", MyPlotsView.as_view(), name="me_plots_slash"),
    path("photo", UploadPhotoView.as_view(), name="me_photo"),
    path("photo/", UploadPhotoView.as_view(), name="me_photo_slash"),
    path("documents", UploadDocumentView.as_view(), name="me_documents"),
    path("documents/", UploadDocumentView.as_view(), name="me_documents_slash"),
    path("consent", RecordConsentView.as_view(), name="me_consent"),
    path("consent/", RecordConsentView.as_view(), name="me_consent_slash"),
    path("qr-blocks", MyQrBlocksView.as_view(), name="me_qr_blocks"),
    path("qr-blocks/", MyQrBlocksView.as_view(), name="me_qr_blocks_slash"),
    path("qr-blocks/<uuid:block_id>/sheet.pdf", MyQrBlockSheetPdfView.as_view(), name="me_qr_block_sheet_pdf"),
    path("stats", MyRoleStatsView.as_view(), name="me_stats"),
    path("stats/", MyRoleStatsView.as_view(), name="me_stats_slash"),
]
