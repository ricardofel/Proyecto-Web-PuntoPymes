from rest_framework import routers

# --- IMPORTACIONES CORREGIDAS ---
# 1. Sin 'source.' al inicio
# 2. Apuntando a la carpeta .api.views (donde movimos los archivos)

from empleados.api.views import EmpleadoViewSet
from asistencia.api.views import EventoAsistenciaViewSet
from auditoria.api.views import LogAuditoriaViewSet
from integraciones.api.views import (
    IntegracionErpViewSet, 
    WebhookViewSet, 
    LogIntegracionViewSet
)

router = routers.DefaultRouter()

# --- REGISTRO DE RUTAS ---
router.register(r'empleados', EmpleadoViewSet)
router.register(r'asistencias', EventoAsistenciaViewSet)
router.register(r'auditoria', LogAuditoriaViewSet)

# Rutas de Integraciones
router.register(r'integraciones/erp', IntegracionErpViewSet)
router.register(r'integraciones/webhooks', WebhookViewSet)
router.register(r'integraciones/logs', LogIntegracionViewSet)

urlpatterns = router.urls