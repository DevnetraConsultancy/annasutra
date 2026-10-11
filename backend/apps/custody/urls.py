from django.urls import path
from .views import HandoverReceiveView, HandoverDisputeView, HandoverResolveView

urlpatterns = [
    path("<uuid:handover_id>/receive", HandoverReceiveView.as_view(), name="handover_receive"),
    path("<uuid:handover_id>/dispute", HandoverDisputeView.as_view(), name="handover_dispute"),
    path("<uuid:handover_id>/resolve", HandoverResolveView.as_view(), name="handover_resolve"),
]
