from rest_framework import routers
from empleados.api_views import EmpleadoViewSet
from asistencia.api_views import EventoAsistenciaViewSet # <--- Importación corregida

router = routers.DefaultRouter()

# Rutas
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet) # La URL será /api/asistencias/

urlpatterns = router.urls