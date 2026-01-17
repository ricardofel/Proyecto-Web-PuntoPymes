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
from notificaciones.api.views import NotificacionViewSet

# 1. Importamos POA
from poa.api.views import ObjetivoViewSet, MetaTacticoViewSet, ActividadViewSet

router = routers.DefaultRouter()

# --- REGISTRO DE RUTAS ---
# Core RRHH
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet)

# Auditoría y Seguridad
router.register(r'auditoria', LogAuditoriaViewSet)

# Integraciones
router.register(r'integraciones/erp', IntegracionErpViewSet)
router.register(r'integraciones/webhooks', WebhookViewSet)
router.register(r'integraciones/logs', LogIntegracionViewSet)

# Desempeño
router.register(r'kpis/definiciones', KPIViewSet)
router.register(r'kpis/resultados', KPIResultadoViewSet)

# Notificaciones
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

# 2. Registramos POA (Plan Operativo Anual)
router.register(r'poa/objetivos', ObjetivoViewSet)
router.register(r'poa/metas', MetaTacticoViewSet)
router.register(r'poa/actividades', ActividadViewSet)

urlpatterns = router.urls