from rest_framework import routers

# --- IMPORTACIONES ---
from empleados.api.views import EmpleadoViewSet
from asistencia.api.views import EventoAsistenciaViewSet
from auditoria.api.views import LogAuditoriaViewSet
from integraciones.api.views import (
    IntegracionErpViewSet, WebhookViewSet, LogIntegracionViewSet
)
from kpi.api.views import KPIViewSet, KPIResultadoViewSet
from notificaciones.api.views import NotificacionViewSet
from poa.api.views import ObjetivoViewSet, MetaTacticoViewSet, ActividadViewSet

# 1. Importamos Solicitudes
from solicitudes.api.views import (
    TipoAusenciaViewSet, 
    SolicitudAusenciaViewSet, 
    RegistroVacacionesViewSet
)

router = routers.DefaultRouter()

# RRHH Core
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet)

# Solicitudes y Ausencias (NUEVO)
router.register(r'solicitudes/tipos', TipoAusenciaViewSet)
router.register(r'solicitudes/gestion', SolicitudAusenciaViewSet, basename='solicitud')
router.register(r'solicitudes/saldos', RegistroVacacionesViewSet, basename='saldo_vacaciones')

# Auditoría y Seguridad
router.register(r'auditoria', LogAuditoriaViewSet)

# Integraciones
router.register(r'integraciones/erp', IntegracionErpViewSet)
router.register(r'integraciones/webhooks', WebhookViewSet)
router.register(r'integraciones/logs', LogIntegracionViewSet)

# Desempeño y Estrategia
router.register(r'kpis/definiciones', KPIViewSet)
router.register(r'kpis/resultados', KPIResultadoViewSet)
router.register(r'poa/objetivos', ObjetivoViewSet)
router.register(r'poa/metas', MetaTacticoViewSet)
router.register(r'poa/actividades', ActividadViewSet)

# Notificaciones
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = router.urls