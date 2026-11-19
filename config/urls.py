from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("api/v1/appointments/", include("apps.appointments.api.urls")),
    path("admin/", admin.site.urls),

    path(
        "api/v1/",
        include("apps.common.api.urls")
    ),

    path(
        "api/v1/",
        include("apps.accounts.api.urls")
    ),
    path("api/v1/visas/", include("apps.visas.api.urls")),


    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema"
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui"
    ),
    path(
    "api/v1/consultants/",
    include("apps.consultants.api.urls"),
),
        path("api/v1/dashboard/", include("apps.dashboard.api.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
