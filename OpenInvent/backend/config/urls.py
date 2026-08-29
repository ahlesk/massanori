from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.auth_urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/notebooks/", include("apps.notebooks.urls")),
    path("api/movements/", include("apps.movements.urls")),
]
