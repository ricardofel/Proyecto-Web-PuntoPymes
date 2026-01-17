from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from auditoria.models import LogAuditoria
from auditoria.middleware import get_current_user
from auditoria.constants import AccionesLog

# Configuración de apps cuyos modelos serán auditados
APPS_DEL_PROYECTO = [
    'empleados',
    'asistencia',
    'solicitudes',
    'kpi',
    'integraciones',
    'core',
    'usuarios',
    'poa',
    'notificaciones',
]

# Carga dinámica y segura de modelos a vigilar
modelos_vigilados = []
for app_label in APPS_DEL_PROYECTO:
    try:
        app_config = apps.get_app_config(app_label)
        modelos_vigilados.extend(app_config.get_models())
    except LookupError:
        # La app no está instalada; se ignora
        pass


def obtener_detalle(instance):
    """Obtiene una representación corta del objeto para el log."""
    return str(instance)[:500]


@receiver(post_save)
def registrar_cambio(sender, instance, created, **kwargs):
    """Registra creación o edición de modelos vigilados."""
    if sender in modelos_vigilados:
        # Evita auditar el propio modelo de logs
        if sender == LogAuditoria:
            return

        usuario = get_current_user()

        LogAuditoria.objects.create(
            usuario=usuario if (usuario and usuario.is_authenticated) else None,
            accion=AccionesLog.CREAR if created else AccionesLog.EDITAR,
            modulo=sender._meta.app_label.upper(),
            modelo=sender._meta.model_name.upper(),
            objeto_id=str(instance.pk),
            detalle=obtener_detalle(instance),
        )


@receiver(post_delete)
def registrar_eliminacion(sender, instance, **kwargs):
    """Registra eliminación de modelos vigilados."""
    if sender in modelos_vigilados:
        if sender == LogAuditoria:
            return

        usuario = get_current_user()

        LogAuditoria.objects.create(
            usuario=usuario if (usuario and usuario.is_authenticated) else None,
            accion=AccionesLog.ELIMINAR,
            modulo=sender._meta.app_label.upper(),
            modelo=sender._meta.model_name.upper(),
            objeto_id=str(instance.pk),
            detalle=obtener_detalle(instance),
        )
