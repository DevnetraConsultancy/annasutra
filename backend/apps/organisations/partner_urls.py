from django.urls import path
from .views import PartnerListView, PartnerInviteView, PartnerAcceptView

urlpatterns = [
    path("", PartnerListView.as_view(), name="partner_list"),
    path("/invitations", PartnerInviteView.as_view(), name="partner_invite"),
    path("/invitations/<uuid:org_id>/accept", PartnerAcceptView.as_view(), name="partner_accept"),
]
