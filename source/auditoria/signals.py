from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from auditoria.models import LogAuditoria
from auditoria.middleware import get_current_user
from auditoria.constants import AccionesLog # <--- Importamos

# --- 1. CONFIGURACIÓN ---
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

modelos_vigilados = []
# Llenamos la lista de modelos de forma segura
for app_label in APPS_DEL_PROYECTO:
    try:
        app_config = apps.get_app_config(app_label)
        modelos_vigilados.extend(app_config.get_models())
    except LookupError:
        pass # Si la app no está instalada aún, la ignoramos

def obtener_detalle(instance):
    return str(instance)[:500]

# --- 2. SEÑAL GUARDAR (Crear/Editar) ---
@receiver(post_save)
def registrar_cambio(sender, instance, created, **kwargs):
    if sender in modelos_vigilados:
        # Evitamos auditar el propio Log para no hacer bucles infinitos
        if sender == LogAuditoria: 
            return

        usuario = get_current_user()
        
        LogAuditoria.objects.create(
            usuario=usuario if (usuario and usuario.is_authenticated) else None,
            accion=AccionesLog.CREAR if created else AccionesLog.EDITAR, # Constantes
            modulo=sender._meta.app_label.upper(),
            modelo=sender._meta.model_name.upper(),
            objeto_id=str(instance.pk),
            detalle=obtener_detalle(instance)
        )

# --- 3. SEÑAL ELIMINAR ---
@receiver(post_delete)
def registrar_eliminacion(sender, instance, **kwargs):
    if sender in modelos_vigilados:
        if sender == LogAuditoria: 
            return

        usuario = get_current_user()
        
        LogAuditoria.objects.create(
            usuario=usuario if (usuario and usuario.is_authenticated) else None,
            accion=AccionesLog.ELIMINAR, # Constantes
            modulo=sender._meta.app_label.upper(),
            modelo=sender._meta.model_name.upper(),
            objeto_id=str(instance.pk),
            detalle=obtener_detalle(instance)
        )