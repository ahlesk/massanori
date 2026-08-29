from django.urls import path

from apps.notebooks.views import NotebookDetailView, NotebookListCreateView

# checkout/, return/ e history/ entram na Fase 2.
urlpatterns = [
    path("", NotebookListCreateView.as_view(), name="notebook-list-create"),
    path("<str:asset>/", NotebookDetailView.as_view(), name="notebook-detail"),
]
