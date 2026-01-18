from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("empleados/", include("empleados.urls")),
    path("", include("core.urls")),
    path("api/", include("talenttrack.api_router")),
    path("solicitudes/", include("solicitudes.urls", namespace="solicitudes")),
]

# Rutas para servir archivos multimedia en entorno de desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
