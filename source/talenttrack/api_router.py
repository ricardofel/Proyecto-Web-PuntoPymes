from rest_framework import routers

# 1. Core
from core.api.views import EmpresaViewSet, UnidadOrganizacionalViewSet

# 2. RRHH
from empleados.api.views import EmpleadoViewSet
from asistencia.api.views import EventoAsistenciaViewSet

# 3. Solicitudes
from solicitudes.api.views import (
    TipoAusenciaViewSet, SolicitudAusenciaViewSet, RegistroVacacionesViewSet
)

# 4. Seguridad y Auditoría
from auditoria.api.views import LogAuditoriaViewSet
from usuarios.api.views import UsuarioViewSet, RolViewSet

# 5. Integraciones
from integraciones.api.views import (
    IntegracionErpViewSet, WebhookViewSet, LogIntegracionViewSet
)

# 6. Desempeño y Estrategia
from kpi.api.views import KPIViewSet, KPIResultadoViewSet
from poa.api.views import ObjetivoViewSet, MetaTacticoViewSet, ActividadViewSet

# 7. Notificaciones
from notificaciones.api.views import NotificacionViewSet


# --- CONFIGURACIÓN DEL ROUTER ---
router = routers.DefaultRouter()

# === REGISTRO DE RUTAS ===

# Core
router.register(r'core/empresas', EmpresaViewSet)
router.register(r'core/unidades', UnidadOrganizacionalViewSet)

# RRHH
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet)

# Solicitudes
router.register(r'solicitudes/tipos', TipoAusenciaViewSet)
router.register(r'solicitudes/gestion', SolicitudAusenciaViewSet, basename='solicitud')
router.register(r'solicitudes/saldos', RegistroVacacionesViewSet, basename='saldo_vacaciones')

# Usuarios y Seguridad
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'roles', RolViewSet)
router.register(r'auditoria', LogAuditoriaViewSet)

# Integraciones
router.register(r'integraciones/erp', IntegracionErpViewSet)
router.register(r'integraciones/webhooks', WebhookViewSet)
router.register(r'integraciones/logs', LogIntegracionViewSet)

# KPIs y POA
router.register(r'kpis/definiciones', KPIViewSet)
router.register(r'kpis/resultados', KPIResultadoViewSet)
router.register(r'poa/objetivos', ObjetivoViewSet)
router.register(r'poa/metas', MetaTacticoViewSet)
router.register(r'poa/actividades', ActividadViewSet)

# Notificaciones
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = router.urls