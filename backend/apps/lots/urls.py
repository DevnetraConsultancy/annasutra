from django.urls import path
from .views import (
    LotListCreateView,
    LotDetailView,
    LotEventsView,
    LotInspectionView,
    LotDispatchView,
    LotSplitView,
    LotMergeView,
    LotSortView,
    LotRepackView,
    LotWasteView,
    LotSaleView,
    LotLabelReissueView,
)

urlpatterns = [
    path("", LotListCreateView.as_view(), name="lot_list_create"),
    path("merge", LotMergeView.as_view(), name="lot_merge"),
    path("<str:code>", LotDetailView.as_view(), name="lot_detail"),
    path("<str:code>/events", LotEventsView.as_view(), name="lot_events"),
    path("<str:code>/inspections", LotInspectionView.as_view(), name="lot_inspection"),
    path("<str:code>/dispatch", LotDispatchView.as_view(), name="lot_dispatch"),
    path("<str:code>/split", LotSplitView.as_view(), name="lot_split"),
    path("<str:code>/sort", LotSortView.as_view(), name="lot_sort"),
    path("<str:code>/repack", LotRepackView.as_view(), name="lot_repack"),
    path("<str:code>/waste", LotWasteView.as_view(), name="lot_waste"),
    path("<str:code>/sales", LotSaleView.as_view(), name="lot_sales"),
    path("<str:code>/label-reissue", LotLabelReissueView.as_view(), name="lot_label_reissue"),
]

