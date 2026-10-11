from django.urls import path
from .views import LabelBlockView

urlpatterns = [
    path("blocks", LabelBlockView.as_view(), name="label_blocks"),
]
