from django.urls import path

from apps.movements.views import MovementListView

urlpatterns = [
    path("", MovementListView.as_view(), name="movement-list"),
]
