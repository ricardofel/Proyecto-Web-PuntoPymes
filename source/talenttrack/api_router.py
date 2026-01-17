from rest_framework import routers
from empleados.api_views import EmpleadoViewSet
from asistencia.api_views import EventoAsistenciaViewSet
# 1. importar la vista de auditoria
from auditoria.api_views import LogAuditoriaViewSet

router = routers.DefaultRouter()

# rutas existentes
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet)
router.register(r'auditoria', LogAuditoriaViewSet)

urlpatterns = router.urls