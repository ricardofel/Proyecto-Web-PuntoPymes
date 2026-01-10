from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from auditoria.models import LogAuditoria        # <--- Conectamos con la BD
from auditoria.middleware import get_current_user # <--- Conectamos con el Middleware

# --- 1. CONFIGURACIÓN ---
# Evitamos bucles infinitos excluyendo auditoria y sesiones
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
for app_label in APPS_DEL_PROYECTO:
    try:
        app_config = apps.get_app_config(app_label)
        modelos_vigilados.extend(app_config.get_models())
    except LookupError:
        pass

def obtener_detalle(instance):
    return str(instance)[:500] # Cortamos para no saturar la BD

# --- 2. SEÑAL GUARDAR (Crear/Editar) ---
@receiver(post_save)
def registrar_cambio(sender, instance, created, **kwargs):
    if sender in modelos_vigilados:
        usuario = get_current_user() # ¡Atrapamos al culpable!
        
        LogAuditoria.objects.create(
            usuario=usuario if (usuario and usuario.is_authenticated) else None,
            accion='CREAR' if created else 'EDITAR',
            modulo=sender._meta.app_label.upper(),
            modelo=sender._meta.model_name.upper(),
            objeto_id=str(instance.pk),
            detalle=obtener_detalle(instance)
        )

# --- 3. SEÑAL ELIMINAR ---
@receiver(post_delete)
def registrar_eliminacion(sender, instance, **kwargs):
    if sender in modelos_vigilados:
        usuario = get_current_user()
        
        LogAuditoria.objects.create(
            usuario=usuario if (usuario and usuario.is_authenticated) else None,
            accion='ELIMINAR',
            modulo=sender._meta.app_label.upper(),
            modelo=sender._meta.model_name.upper(),
            objeto_id=str(instance.pk),
            detalle=obtener_detalle(instance)
        )