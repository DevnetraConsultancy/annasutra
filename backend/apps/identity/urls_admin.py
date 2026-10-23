"""URL routing for administrative review queue and verification endpoints."""

from django.urls import path
from .views_admin import (
    AdminReviewQueueView,
    AdminEntityDetailView,
    AdminRevealFieldView,
    AdminEntityDecisionView,
    AdminIssueQrBlockView,
    AdminEntityRestoreView,
    AdminEntityPurgeView,
)

urlpatterns = [
    path("reviews", AdminReviewQueueView.as_view(), name="admin_reviews"),
    path("reviews/", AdminReviewQueueView.as_view(), name="admin_reviews_slash"),
    path("entities/<uuid:entity_id>", AdminEntityDetailView.as_view(), name="admin_entity_detail"),
    path("entities/<uuid:entity_id>/", AdminEntityDetailView.as_view(), name="admin_entity_detail_slash"),
    path("entities/<uuid:entity_id>/reveal", AdminRevealFieldView.as_view(), name="admin_reveal_field"),
    path("entities/<uuid:entity_id>/reveal/", AdminRevealFieldView.as_view(), name="admin_reveal_field_slash"),
    path("entities/<uuid:entity_id>/decision", AdminEntityDecisionView.as_view(), name="admin_entity_decision"),
    path("entities/<uuid:entity_id>/decision/", AdminEntityDecisionView.as_view(), name="admin_entity_decision_slash"),
    path("entities/<uuid:entity_id>/qr-blocks", AdminIssueQrBlockView.as_view(), name="admin_issue_qr_block"),
    path("entities/<uuid:entity_id>/qr-blocks/", AdminIssueQrBlockView.as_view(), name="admin_issue_qr_block_slash"),
    path("entities/<uuid:entity_id>/restore", AdminEntityRestoreView.as_view(), name="admin_entity_restore"),
    path("entities/<uuid:entity_id>/restore/", AdminEntityRestoreView.as_view(), name="admin_entity_restore_slash"),
    path("entities/<uuid:entity_id>/purge", AdminEntityPurgeView.as_view(), name="admin_entity_purge"),
    path("entities/<uuid:entity_id>/purge/", AdminEntityPurgeView.as_view(), name="admin_entity_purge_slash"),
]
