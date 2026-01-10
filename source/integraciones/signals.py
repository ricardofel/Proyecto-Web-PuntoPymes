import requests
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder

# Modelos
from solicitudes.models import SolicitudAusencia
from asistencia.models import EventoAsistencia
from .models import Webhook, LogIntegracion

# --- WEBHOOK 1: NUEVO PERMISO (SOLICITUD) ---
@receiver(post_save, sender=SolicitudAusencia)
def webhook_nuevo_permiso(sender, instance, created, **kwargs):
    if created: # Solo al crear
        # Buscamos webhooks suscritos a 'solicitud_creada' (o similar)
        # Nota: Asegúrate de que en tus choices de Webhook.EVENTOS tengas 'solicitud_aprobada' o crea uno nuevo
        hooks = Webhook.objects.filter(evento='solicitud_aprobada', activo=True) 
        
        payload = {
            "evento": "NUEVA_SOLICITUD_PERMISO",
            "empleado": f"{instance.empleado.nombres} {instance.empleado.apellidos}",
            "tipo": instance.ausencia.nombre,
            "fechas": f"{instance.fecha_inicio} al {instance.fecha_fin}",
            "motivo": instance.motivo
        }
        _enviar_webhooks(hooks, payload)

# --- WEBHOOK 2: CHECK-IN (ASISTENCIA) ---
@receiver(post_save, sender=EventoAsistencia)
def webhook_check_in(sender, instance, created, **kwargs):
    if created and instance.tipo == 'check_in': # Solo Entradas
        # Buscamos webhooks genéricos o específicos (usaremos 'empleado_creado' como placeholder si no tienes 'checkin')
        # Ojo: Lo ideal es agregar 'asistencia_checkin' a los choices de tu modelo Webhook.
        hooks = Webhook.objects.filter(nombre__icontains="asistencia", activo=True)
        
        payload = {
            "evento": "CHECK_IN_DETECTADO",
            "empleado_id": instance.empleado.id,
            "nombre": instance.empleado.nombres,
            "hora": str(instance.registrado_el),
            "gps": f"{instance.latitud}, {instance.longitud}"
        }
        _enviar_webhooks(hooks, payload)

# --- FUNCIÓN AUXILIAR DE ENVÍO ---
def _enviar_webhooks(hooks, payload):
    for hook in hooks:
        try:
            print(f"🚀 [Webhook] Enviando a {hook.nombre}...")
            response = requests.post(
                hook.url_destino,
                data=json.dumps(payload, cls=DjangoJSONEncoder),
                headers={'Content-Type': 'application/json'},
                timeout=3
            )
            # Log de éxito
            LogIntegracion.objects.create(
                webhook=hook,
                endpoint=hook.url_destino,
                codigo_respuesta=response.status_code,
                mensaje_respuesta="Enviado correctamente"
            )
        except Exception as e:
            print(f"❌ [Webhook] Error: {e}")
            # Log de error
            LogIntegracion.objects.create(
                webhook=hook,
                endpoint=hook.url_destino,
                codigo_respuesta=500,
                mensaje_respuesta=str(e)
            )