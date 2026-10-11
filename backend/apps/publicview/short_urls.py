from django.urls import path
from .views import public_lot_html_view

urlpatterns = [
    path("", public_lot_html_view, name="short_link_public_html"),
]
