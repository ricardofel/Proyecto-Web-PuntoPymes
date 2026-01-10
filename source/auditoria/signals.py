import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps

# --- 1. CONFIGURAR LOGGER ---
logger = logging.getLogger('auditoria_app')

def obtener_detalle(instance):
    """Extrae un resumen legible del objeto"""
    return str(instance)

# --- 2. DEFINIR QUÉ APPS VIGILAR ---
# Listamos las apps de TU proyecto + 'auth' (Usuarios).
# No ponemos 'admin', 'sessions', etc. para no llenar el log de basura técnica.
APPS_DEL_PROYECTO = [
    'core',
    'empleados',
    'asistencia',
    'solicitudes',
    'poa',
    'kpi',
    'integraciones', # Si tienes modelos aquí
    'auth',          # Usuarios y Grupos (Django)
]

# --- 3. OBTENER TODOS LOS MODELOS DINÁMICAMENTE ---
modelos_vigilados = []

for app_label in APPS_DEL_PROYECTO:
    try:
        # Obtenemos la configuración de la app
        app_config = apps.get_app_config(app_label)
        # Extraemos TODOS sus modelos y los sumamos a la lista
        modelos_vigilados.extend(app_config.get_models())
    except LookupError:
        # Si una app no está instalada (ej: integraciones vacía), no pasa nada
        pass

# --- 4. SEÑALES UNIVERSALES ---

@receiver(post_save)
def registrar_cambio_universal(sender, instance, created, **kwargs):
    """Detecta CREACIÓN o EDICIÓN en cualquier modelo de la lista"""
    if sender in modelos_vigilados:
        accion = 'CREADO' if created else 'EDITADO'
        app = sender._meta.app_label.upper()     # Ej: EMPLEADOS
        tabla = sender._meta.model_name.upper()  # Ej: CONTRATO
        detalle = obtener_detalle(instance)
        
        # Mejora visual para Usuarios
        if hasattr(instance, 'username'):
             detalle = f"Usuario: {instance.username} | Email: {getattr(instance, 'email', '-')}"

        # Formato Columnar para el Log
        mensaje = f"APP: {app:<12} | ACCION: {accion:<8} | TABLA: {tabla:<18} | ID: {str(instance.pk):<5} | DETALLE: {detalle}"
        logger.info(mensaje)

@receiver(post_delete)
def registrar_eliminacion_universal(sender, instance, **kwargs):
    """Detecta ELIMINACIÓN en cualquier modelo de la lista"""
    if sender in modelos_vigilados:
        app = sender._meta.app_label.upper()
        tabla = sender._meta.model_name.upper()
        detalle = obtener_detalle(instance)
        
        mensaje = f"APP: {app:<12} | ACCION: ELIMINADO | TABLA: {tabla:<18} | ID: {str(instance.pk):<5} | DETALLE: {detalle}"
        logger.info(mensaje)