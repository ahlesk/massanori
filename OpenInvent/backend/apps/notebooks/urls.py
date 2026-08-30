from django.urls import path

from apps.notebooks.views import (
    NotebookCheckoutView,
    NotebookDetailView,
    NotebookHistoryView,
    NotebookListCreateView,
    NotebookReturnView,
    NotebookSummaryView,
)

urlpatterns = [
    path("", NotebookListCreateView.as_view(), name="notebook-list-create"),
    # "summary/" precisa vir antes de "<str:asset>/": senão o Django tentaria
    # casar essa rota fixa como se "summary" fosse um asset.
    path("summary/", NotebookSummaryView.as_view(), name="notebook-summary"),
    path("<str:asset>/", NotebookDetailView.as_view(), name="notebook-detail"),
    path("<str:asset>/checkout/", NotebookCheckoutView.as_view(), name="notebook-checkout"),
    path("<str:asset>/return/", NotebookReturnView.as_view(), name="notebook-return"),
    path("<str:asset>/history/", NotebookHistoryView.as_view(), name="notebook-history"),
]
