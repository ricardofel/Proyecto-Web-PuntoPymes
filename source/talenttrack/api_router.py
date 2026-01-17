from rest_framework import routers

# --- IMPORTACIONES ---
from empleados.api.views import EmpleadoViewSet
from asistencia.api.views import EventoAsistenciaViewSet
from auditoria.api.views import LogAuditoriaViewSet
from integraciones.api.views import (
    IntegracionErpViewSet, 
    WebhookViewSet, 
    LogIntegracionViewSet
)
from kpi.api.views import KPIViewSet, KPIResultadoViewSet

# 1. Importamos Notificaciones
from notificaciones.api.views import NotificacionViewSet

router = routers.DefaultRouter()

# --- REGISTRO DE RUTAS ---
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet)
router.register(r'auditoria', LogAuditoriaViewSet)

router.register(r'integraciones/erp', IntegracionErpViewSet)
router.register(r'integraciones/webhooks', WebhookViewSet)
router.register(r'integraciones/logs', LogIntegracionViewSet)

router.register(r'kpis/definiciones', KPIViewSet)
router.register(r'kpis/resultados', KPIResultadoViewSet)

# 2. Registramos la ruta (Simple y directa)
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = router.urls