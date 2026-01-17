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
# importamos los nuevos viewsets de kpi
from kpi.api.views import KPIViewSet, KPIResultadoViewSet

router = routers.DefaultRouter()

# --- REGISTRO DE RUTAS ---
# Recursos Humanos
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet)

# Auditoría y Seguridad
router.register(r'auditoria', LogAuditoriaViewSet)

# Integraciones
router.register(r'integraciones/erp', IntegracionErpViewSet)
router.register(r'integraciones/webhooks', WebhookViewSet)
router.register(r'integraciones/logs', LogIntegracionViewSet)

# Gestión de Desempeño (KPIs)
router.register(r'kpis/definiciones', KPIViewSet)
router.register(r'kpis/resultados', KPIResultadoViewSet)

urlpatterns = router.urls