from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# No es necesario importar settings y static dos veces,
# las he dejado comentadas para limpiar, pero si tu archivo las tenía así,
# asegúrate de que solo estén una vez.
# from django.conf import settings
# from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("empleados/", include("empleados.urls")),
    path("", include("core.urls")),
    path("api/", include("talenttrack.api_router")),
    path('solicitudes/', include('solicitudes.urls', namespace='solicitudes')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
