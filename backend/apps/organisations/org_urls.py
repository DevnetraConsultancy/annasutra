from django.urls import path
from .views import OrgRegisterView

urlpatterns = [
    path("", OrgRegisterView.as_view(), name="org_register"),
]
